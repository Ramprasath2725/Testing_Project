"""Unit tests for config handling and BasePage behaviour (fake driver, no browser)."""
import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.config_reader import ConfigReader
from utils.data_factory import UserFactory
from utils.data_loader import get_product, load_data
from utils.healing_agent import HealingAgent

pytestmark = pytest.mark.unit


class MissingElementDriver:
    """Behaves like a page on which nothing can be found."""
    current_url = "https://example.test/"

    def find_element(self, *args):
        raise NoSuchElementException("not here")

    def find_elements(self, *args):
        return []

    def execute_script(self, *args):
        return None


@pytest.fixture(autouse=True)
def _reset():
    ConfigReader.clear_overrides()
    HealingAgent.reset()
    HealingAgent.configure(True)
    yield
    ConfigReader.clear_overrides()


# ---- BasePage: regression tests for the bug found in the original code ----------
def test_is_visible_returns_false_instead_of_raising_when_element_missing():
    """Original code let NoSuchElementException (from healing) escape is_visible()."""
    page = BasePage(MissingElementDriver())
    assert page.is_visible((By.ID, "ghost"), timeout=0.2) is False


def test_find_raises_timeout_with_url_when_element_and_fallbacks_missing():
    page = BasePage(MissingElementDriver())
    with pytest.raises(TimeoutException) as err:
        page.find((By.ID, "ghost"), timeout=0.2)
    assert "https://example.test/" in str(err.value)


def test_find_does_not_heal_when_healing_disabled():
    HealingAgent.configure(False)
    page = BasePage(MissingElementDriver())
    with pytest.raises(TimeoutException):
        page.find((By.ID, "ghost"), timeout=0.2)
    assert HealingAgent.events == []


# ---- ConfigReader ---------------------------------------------------------------------
def test_config_defaults_come_from_ini():
    assert ConfigReader.get("general", "base_url") == "https://automationexercise.com"
    assert ConfigReader.get_int("general", "explicit_wait") == 15


def test_runtime_override_beats_ini_and_env(monkeypatch):
    monkeypatch.setenv("BROWSER", "firefox")
    assert ConfigReader.get("general", "browser") == "firefox"       # env beats ini
    ConfigReader.override("general", "browser", "chrome")
    assert ConfigReader.get("general", "browser") == "chrome"         # CLI beats env


@pytest.mark.parametrize("raw, expected", [("true", True), ("1", True), ("False", False), ("no", False)])
def test_get_bool_parses_env_values(monkeypatch, raw, expected):
    monkeypatch.setenv("HEADLESS", raw)
    assert ConfigReader.get_bool("general", "headless") is expected


# ---- test data -----------------------------------------------------------------------
def test_user_factory_builds_unique_users_without_hardcoded_secrets():
    a, b = UserFactory.build(), UserFactory.build()
    assert a["email"] != b["email"] and a["password"] != b["password"]
    assert a["email"].endswith("@example.com")


def test_test_data_file_is_valid_and_has_expected_sections():
    data = load_data()
    for section in ("products", "categories", "brands", "search_terms", "payment", "contact"):
        assert section in data
    assert get_product(1)["price"] == 500
