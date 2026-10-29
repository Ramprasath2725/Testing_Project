"""Page Object for the account-information form and the account created/deleted screens."""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class SignupPage(BasePage):
    HEADER = (By.XPATH, "//b[contains(text(),'Enter Account Information')]")
    TITLE_RADIO = {"Mr": (By.ID, "id_gender1"), "Mrs": (By.ID, "id_gender2")}
    PASSWORD = (By.CSS_SELECTOR, "input[data-qa='password']")
    DAY = (By.CSS_SELECTOR, "select[data-qa='days']")
    MONTH = (By.CSS_SELECTOR, "select[data-qa='months']")
    YEAR = (By.CSS_SELECTOR, "select[data-qa='years']")
    NEWSLETTER = (By.ID, "newsletter")
    SPECIAL_OFFERS = (By.ID, "optin")
    FIRST_NAME = (By.CSS_SELECTOR, "input[data-qa='first_name']")
    LAST_NAME = (By.CSS_SELECTOR, "input[data-qa='last_name']")
    COMPANY = (By.CSS_SELECTOR, "input[data-qa='company']")
    ADDRESS1 = (By.CSS_SELECTOR, "input[data-qa='address']")
    ADDRESS2 = (By.CSS_SELECTOR, "input[data-qa='address2']")
    COUNTRY = (By.CSS_SELECTOR, "select[data-qa='country']")
    STATE = (By.CSS_SELECTOR, "input[data-qa='state']")
    CITY = (By.CSS_SELECTOR, "input[data-qa='city']")
    ZIPCODE = (By.CSS_SELECTOR, "input[data-qa='zipcode']")
    MOBILE = (By.CSS_SELECTOR, "input[data-qa='mobile_number']")
    CREATE_BUTTON = (By.CSS_SELECTOR, "button[data-qa='create-account']")

    ACCOUNT_CREATED = (By.CSS_SELECTOR, "h2[data-qa='account-created']")
    ACCOUNT_DELETED = (By.CSS_SELECTOR, "h2[data-qa='account-deleted']")
    CONTINUE = (By.CSS_SELECTOR, "a[data-qa='continue-button']")

    def is_loaded(self):
        return self.is_visible(self.HEADER)

    def fill_account_information(self, user):
        """Fill the whole form from a UserFactory dict and submit it."""
        self.click(self.TITLE_RADIO[user["title"]])
        self.type(self.PASSWORD, user["password"])
        self.select_by_value(self.DAY, user["birth_day"])
        self.select_by_value(self.MONTH, user["birth_month"])
        self.select_by_value(self.YEAR, user["birth_year"])
        self.check(self.NEWSLETTER)
        self.check(self.SPECIAL_OFFERS)
        self.type(self.FIRST_NAME, user["first_name"])
        self.type(self.LAST_NAME, user["last_name"])
        self.type(self.COMPANY, user["company"])
        self.type(self.ADDRESS1, user["address1"])
        self.type(self.ADDRESS2, user["address2"])
        self.select_by_text(self.COUNTRY, user["country"])
        self.type(self.STATE, user["state"])
        self.type(self.CITY, user["city"])
        self.type(self.ZIPCODE, user["zipcode"])
        self.type(self.MOBILE, user["mobile_number"])
        self.click(self.CREATE_BUTTON)

    def get_account_created_message(self):
        return self.get_text(self.ACCOUNT_CREATED)

    def get_account_deleted_message(self):
        return self.get_text(self.ACCOUNT_DELETED)

    def click_continue(self):
        self.click(self.CONTINUE)
