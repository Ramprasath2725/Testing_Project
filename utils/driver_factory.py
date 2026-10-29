"""Creates WebDriver instances.

Uses Selenium Manager (built into Selenium 4.6+) to resolve the driver binary,
so there is no webdriver-manager dependency or manual driver setup.
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from utils.config_reader import ConfigReader
from utils.logger import get_logger

logger = get_logger(__name__)

# Ad / tracker hosts that inject overlays and intercept clicks on the demo site.
AD_URL_PATTERNS = [
    "*googlesyndication.com*", "*doubleclick.net*", "*googleadservices.com*",
    "*adservice.google.*", "*google-analytics.com*", "*googletagmanager.com*",
]


class DriverFactory:
    @staticmethod
    def get_driver(browser: str = "chrome", headless: bool = True):
        browser = (browser or "chrome").lower().strip()
        logger.info("Launching '%s' driver (headless=%s)", browser, headless)

        if browser == "chrome":
            options = ChromeOptions()
            if headless:
                options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")              # CI / containers
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            # 'eager': don't wait for ads/images - explicit waits handle the rest
            options.page_load_strategy = "eager"
            options.add_experimental_option(
                "prefs", {"profile.default_content_setting_values.notifications": 2}
            )
            driver = webdriver.Chrome(options=options)
            DriverFactory._block_ads(driver)

        elif browser == "firefox":
            options = FirefoxOptions()
            if headless:
                options.add_argument("--headless")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            options.page_load_strategy = "eager"
            driver = webdriver.Firefox(options=options)

        else:
            raise ValueError(f"Unsupported browser '{browser}'. Use 'chrome' or 'firefox'.")

        driver.set_page_load_timeout(ConfigReader.get_int("general", "page_load_timeout", 45))
        try:
            driver.maximize_window()
        except Exception:  # some headless setups cannot maximise; size flag already set
            pass
        return driver

    @staticmethod
    def _block_ads(driver):
        """Chrome only: block ad hosts via DevTools. Best-effort."""
        try:
            driver.execute_cdp_cmd("Network.enable", {})
            driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": AD_URL_PATTERNS})
        except Exception as exc:
            logger.warning("Could not enable ad blocking: %s", exc)
