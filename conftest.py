"""Pytest fixtures and hooks shared across the whole suite.

- `driver`          : fresh browser per test (isolation) with guaranteed teardown.
- `new_user`        : unique user data; account removed afterwards via API (best effort).
- `registered_user` : user pre-created through the site's REST API, removed afterwards.
- `logged_in_user`  : `registered_user` already logged in through the UI.
- CLI options       : --browser, --headless, --base-url, --healing.
- On failure        : screenshot saved to screenshots/ and embedded in the HTML report.
- Healing events    : listed in the terminal summary and attached to each test report.
"""
import json
import re
from datetime import datetime

import pytest

from utils import api_client
from utils.config_reader import PROJECT_ROOT, ConfigReader
from utils.data_factory import UserFactory
from utils.driver_factory import DriverFactory
from utils.healing_agent import HealingAgent
from utils.logger import get_logger

logger = get_logger(__name__)
SCREENSHOT_DIR = PROJECT_ROOT / "screenshots"


def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default=None,
                     help="chrome or firefox (default: config.ini)")
    parser.addoption("--headless", action="store", default=None,
                     help="true or false (default: config.ini)")
    parser.addoption("--base-url", action="store", default=None,
                     help="Override the application URL")
    parser.addoption("--healing", action="store", default=None, choices=["on", "off"],
                     help="Enable/disable locator recovery (default: config.ini)")


def pytest_configure(config):
    for option, section, key in (
        ("--browser", "general", "browser"),
        ("--headless", "general", "headless"),
        ("--base-url", "general", "base_url"),
    ):
        value = config.getoption(option)
        if value is not None:
            ConfigReader.override(section, key, value)
    healing = config.getoption("--healing")
    if healing is not None:
        ConfigReader.override("healing", "enabled", "true" if healing == "on" else "false")
    HealingAgent.configure(ConfigReader.get_bool("healing", "enabled", True))


# --------------------------------------------------------------------------- driver
@pytest.fixture
def driver():
    browser = ConfigReader.get("general", "browser", "chrome")
    headless = ConfigReader.get_bool("general", "headless", True)
    HealingAgent.reset()
    drv = DriverFactory.get_driver(browser, headless)
    yield drv
    logger.info("Tearing down driver")
    try:
        drv.quit()
    except Exception as exc:  # noqa: BLE001 - never mask the real test result
        logger.warning("driver.quit() failed: %s", exc)


# --------------------------------------------------------------------------- test data
@pytest.fixture
def new_user():
    """Unique user data. Any account created during the test is removed afterwards."""
    user = UserFactory.build()
    yield user
    api_client.delete_account(user["email"], user["password"])


@pytest.fixture
def registered_user():
    """A user that already exists on the site (created through the REST API)."""
    user = UserFactory.build()
    if not api_client.create_account(user):
        pytest.fail("Precondition failed: could not create a user via /api/createAccount",
                    pytrace=False)
    yield user
    api_client.delete_account(user["email"], user["password"])


@pytest.fixture
def logged_in_user(driver, registered_user):
    from pages.login_page import LoginPage

    login = LoginPage(driver).load()
    login.login(registered_user["email"], registered_user["password"])
    assert login.is_logged_in(), "Precondition failed: could not log in the registered user"
    return registered_user


# --------------------------------------------------------------------------- reporting
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """On failure: save + embed a screenshot. Always: attach healing events."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call":
        return

    if HealingAgent.events:
        report.user_properties.append(("healed_locators", json.dumps(HealingAgent.events)))

    if not report.failed:
        return
    drv = item.funcargs.get("driver")
    if not drv:
        return
    try:
        SCREENSHOT_DIR.mkdir(exist_ok=True)
        safe = re.sub(r"[^\w.-]+", "_", item.name)
        path = SCREENSHOT_DIR / f"{safe}_{datetime.now():%H%M%S}.png"
        drv.save_screenshot(str(path))
        logger.error("FAILED: %s | url=%s | screenshot=%s", item.nodeid, drv.current_url, path)

        try:  # embed in pytest-html
            import pytest_html
            report.extras = getattr(report, "extras", []) + [
                pytest_html.extras.png(drv.get_screenshot_as_base64()),
                pytest_html.extras.url(drv.current_url, name="Failure URL"),
            ]
        except ImportError:
            pass
        try:  # attach to Allure if installed
            import allure
            allure.attach(drv.get_screenshot_as_png(), name=item.name,
                          attachment_type=allure.attachment_type.PNG)
        except ImportError:
            pass
    except Exception as exc:  # noqa: BLE001 - best-effort capture
        logger.error("Could not capture screenshot: %s", exc)


def pytest_terminal_summary(terminalreporter):
    """List every locator that had to be recovered (works with xdist too)."""
    rows = []
    for reports in terminalreporter.stats.values():
        for rep in reports:
            for name, value in getattr(rep, "user_properties", []) or []:
                if name == "healed_locators":
                    for event in json.loads(value):
                        rows.append((rep.nodeid, event))
    if not rows:
        return
    terminalreporter.section("Locator recovery events (update these page-object locators)")
    for nodeid, e in rows:
        terminalreporter.write_line(nodeid)
        terminalreporter.write_line(f"    {e['original']}  ->  {e['healed']}  [{e['strategy']}]")
