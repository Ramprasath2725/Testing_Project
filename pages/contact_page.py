"""Page Object for the Contact Us form (/contact_us)."""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.config_reader import ConfigReader


class ContactPage(BasePage):
    HEADER = (By.XPATH, "//h2[contains(text(),'Get In Touch')]")
    NAME = (By.CSS_SELECTOR, "input[data-qa='name']")
    EMAIL = (By.CSS_SELECTOR, "input[data-qa='email']")
    SUBJECT = (By.CSS_SELECTOR, "input[data-qa='subject']")
    MESSAGE = (By.CSS_SELECTOR, "textarea[data-qa='message']")
    FILE_INPUT = (By.CSS_SELECTOR, "input[name='upload_file']")
    SUBMIT = (By.CSS_SELECTOR, "input[data-qa='submit-button']")
    SUCCESS = (By.CSS_SELECTOR, ".status.alert-success")

    def load(self):
        base = ConfigReader.get("general", "base_url")
        self.open(f"{base}/contact_us")
        return self

    def is_loaded(self):
        return self.is_visible(self.HEADER)

    def submit_form(self, name, email, subject, message, attachment=None):
        """Fill the form, submit, and accept the browser confirmation dialog."""
        self.type(self.NAME, name)
        self.type(self.EMAIL, email)
        self.type(self.SUBJECT, subject)
        self.type(self.MESSAGE, message)
        if attachment:
            self.upload_file(self.FILE_INPUT, attachment)
        self.scroll_into_view(self.SUBMIT)
        self.click(self.SUBMIT)
        self.accept_alert()

    def get_success_message(self):
        return self.get_text(self.SUCCESS)
