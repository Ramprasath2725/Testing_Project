"""BasePage - building blocks shared by every Page Object.

Provides explicit-wait element helpers (no time.sleep), locator recovery via
HealingAgent for *positive* lookups, ad-overlay clean-up, and the pieces of UI
that exist on every page: header navigation, login state, footer subscription
and the "added to cart" modal.
"""
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from utils.config_reader import ConfigReader
from utils.healing_agent import HealingAgent
from utils.logger import get_logger

logger = get_logger(__name__)

_CONDITIONS = {
    "presence": EC.presence_of_element_located,
    "visible": EC.visibility_of_element_located,
    "clickable": EC.element_to_be_clickable,
}

# Removes Google ad iframes / vignette overlays that can cover the page.
_AD_CLEANUP_JS = """
document.querySelectorAll(
  'ins.adsbygoogle, ins.adsbygoogle-noablate, iframe[id^="aswift"], ' +
  'iframe[id^="google_ads"], div[id^="aswift"], #ad_position_box, ' +
  '.google-auto-placed, iframe[title="Advertisement"]'
).forEach(e => e.remove());
if (document.body) { document.body.style.overflow = ''; }
"""


class BasePage:
    # --- shared UI: header ---------------------------------------------------
    LOGGED_IN_AS = (
        By.XPATH, "//ul[contains(@class,'navbar-nav')]//a[contains(.,'Logged in as')]/b"
    )
    LOGOUT_LINK = (By.XPATH, "//ul[contains(@class,'navbar-nav')]//a[@href='/logout']")
    DELETE_ACCOUNT_LINK = (
        By.XPATH, "//ul[contains(@class,'navbar-nav')]//a[@href='/delete_account']"
    )

    # --- shared UI: footer subscription ---------------------------------------
    # NOTE: the site's input id is intentionally misspelled 'susbscribe_email'.
    SUBSCRIBE_EMAIL = (By.ID, "susbscribe_email")
    SUBSCRIBE_BUTTON = (By.ID, "subscribe")
    SUBSCRIBE_SUCCESS = (By.CSS_SELECTOR, "#success-subscribe .alert-success")

    # --- shared UI: "Added!" modal after Add to cart --------------------------
    CART_MODAL_TITLE = (By.XPATH, "//div[@id='cartModal']//h4[contains(.,'Added')]")
    CART_MODAL_VIEW_CART = (By.XPATH, "//div[@id='cartModal']//a[@href='/view_cart']")
    CART_MODAL_CONTINUE = (
        By.XPATH, "//div[@id='cartModal']//button[contains(@class,'close-modal')]"
    )

    def __init__(self, driver):
        self.driver = driver
        self.timeout = ConfigReader.get_int("general", "explicit_wait", 15)
        self.wait = WebDriverWait(self.driver, self.timeout)

    # --- navigation ------------------------------------------------------------
    def open(self, url):
        logger.info("Navigating to %s", url)
        self.driver.get(url)
        self.dismiss_ads()

    def get_title(self):
        return self.driver.title

    def current_url(self):
        return self.driver.current_url

    def url_contains(self, fragment, timeout=None):
        """True if the URL contains `fragment` within the timeout (never raises)."""
        try:
            WebDriverWait(self.driver, timeout or self.timeout).until(EC.url_contains(fragment))
            return True
        except TimeoutException:
            return False

    def dismiss_ads(self):
        """Best-effort removal of ad overlays. Never fails a test."""
        try:
            self.driver.execute_script(_AD_CLEANUP_JS)
        except Exception as exc:  # noqa: BLE001
            logger.debug("Ad clean-up skipped: %s", exc)

    # --- element lookup ----------------------------------------------------------
    def find(self, locator, condition="presence", fallbacks=None, timeout=None):
        """Wait for an element; on timeout try HealingAgent, else raise TimeoutException."""
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        try:
            return wait.until(_CONDITIONS[condition](locator))
        except TimeoutException:
            element = HealingAgent.recover(self.driver, locator, fallbacks)
            if element is not None:
                return element
            raise TimeoutException(
                f"Element {locator} not {condition} within {wait._timeout}s "
                f"(url={self.driver.current_url})"
            ) from None

    def find_all(self, locator):
        return self.driver.find_elements(*locator)

    # --- element interactions ------------------------------------------------------
    def click(self, locator, fallbacks=None):
        for attempt in (1, 2):
            element = self.find(locator, "clickable", fallbacks)
            try:
                element.click()
                return
            except StaleElementReferenceException:
                if attempt == 2:
                    raise
                logger.warning("Stale element on %s - re-locating", locator)
            except (ElementClickInterceptedException, ElementNotInteractableException):
                logger.warning("Click blocked on %s - clearing ads, retrying via JS", locator)
                self.dismiss_ads()
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", element
                )
                self.driver.execute_script("arguments[0].click();", element)
                return

    def type(self, locator, text, fallbacks=None):
        element = self.find(locator, "visible", fallbacks)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator, fallbacks=None):
        return self.find(locator, "visible", fallbacks).text.strip()

    def get_attribute(self, locator, name):
        return self.find(locator).get_attribute(name)

    def select_by_value(self, locator, value):
        Select(self.find(locator, "visible")).select_by_value(str(value))

    def select_by_text(self, locator, text):
        Select(self.find(locator, "visible")).select_by_visible_text(text)

    def check(self, locator):
        element = self.find(locator, "clickable")
        if not element.is_selected():
            element.click()

    def upload_file(self, locator, path):
        self.find(locator, "presence").send_keys(str(path))

    def hover(self, locator):
        ActionChains(self.driver).move_to_element(self.find(locator, "visible")).perform()

    def scroll_into_view(self, locator):
        element = self.find(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        return element

    def accept_alert(self):
        alert = self.wait.until(EC.alert_is_present())
        text = alert.text
        alert.accept()
        return text

    # --- state checks (no healing: a missing element must read as missing) ---------
    def is_visible(self, locator, timeout=None):
        try:
            WebDriverWait(self.driver, timeout or self.timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            logger.info("Element not visible: %s", locator)
            return False

    def is_present(self, locator, timeout=None):
        try:
            WebDriverWait(self.driver, timeout or self.timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def count(self, locator):
        """Wait until at least one match exists, then return how many there are."""
        self.wait.until(lambda d: len(d.find_elements(*locator)) > 0)
        return len(self.driver.find_elements(*locator))

    def count_now(self, locator):
        return len(self.driver.find_elements(*locator))

    # --- header navigation / session --------------------------------------------------
    @staticmethod
    def nav_link(href):
        return (By.XPATH, f"//ul[contains(@class,'navbar-nav')]//a[@href='{href}']")

    def go_to(self, href):
        """Click a header link by its href, e.g. '/products', '/view_cart'."""
        self.click(self.nav_link(href))

    def is_logged_in(self, timeout=10):
        return self.is_visible(self.LOGGED_IN_AS, timeout)

    def get_logged_in_username(self):
        return self.get_text(self.LOGGED_IN_AS)

    def logout(self):
        self.click(self.LOGOUT_LINK)

    def delete_account(self):
        self.click(self.DELETE_ACCOUNT_LINK)

    # --- footer subscription -------------------------------------------------------------
    def subscribe(self, email):
        self.scroll_into_view(self.SUBSCRIBE_EMAIL)
        self.type(self.SUBSCRIBE_EMAIL, email)
        self.click(self.SUBSCRIBE_BUTTON)

    def get_subscription_message(self):
        return self.get_text(self.SUBSCRIBE_SUCCESS)

    # --- add-to-cart modal -----------------------------------------------------------------
    def add_product_to_cart(self, product_id):
        """Add a product from any listing page; waits for the 'Added!' modal."""
        self.click((
            By.CSS_SELECTOR,
            f".features_items a.add-to-cart[data-product-id='{product_id}']",
        ))
        self.find(self.CART_MODAL_TITLE, "visible")

    def continue_shopping(self):
        self.click(self.CART_MODAL_CONTINUE)
        self.wait.until(EC.invisibility_of_element_located(self.CART_MODAL_TITLE))

    def view_cart_from_modal(self):
        self.click(self.CART_MODAL_VIEW_CART)
