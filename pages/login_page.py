"""Page Object for the combined Login / Signup page."""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.config_reader import ConfigReader


class LoginPage(BasePage):
    # --- Login form ---
    LOGIN_EMAIL = (By.CSS_SELECTOR, "[data-qa='login-email']")
    LOGIN_PASSWORD = (By.CSS_SELECTOR, "input[data-qa='login-password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[data-qa='login-button']")
    LOGIN_ERROR = (
        By.XPATH,
        "//form[@action='/login']//p[contains(text(),'incorrect')]",
    )

    # --- Signup form ---
    SIGNUP_NAME = (By.CSS_SELECTOR, "input[data-qa='signup-name']")
    SIGNUP_EMAIL = (By.CSS_SELECTOR, "input[data-qa='signup-email']")
    SIGNUP_BUTTON = (By.CSS_SELECTOR, "button[data-qa='signup-button']")
    ACCOUNT_INFO_TITLE = (By.XPATH, "//b[contains(text(),'Enter Account Information')]")

    def load(self):
        base = ConfigReader.get("general", "base_url")
        self.open(f"{base}/login")
        return self

    def login(self, email, password):
        self.type(self.LOGIN_EMAIL, email)
        self.type(self.LOGIN_PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    def get_login_error(self):
        return self.get_text(self.LOGIN_ERROR)

    def start_signup(self, name, email):
        self.type(self.SIGNUP_NAME, name)
        self.type(self.SIGNUP_EMAIL, email)
        self.click(self.SIGNUP_BUTTON)

    def is_account_info_displayed(self):
        return self.is_visible(self.ACCOUNT_INFO_TITLE)
