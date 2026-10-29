"""Page Object for checkout (/checkout), payment (/payment) and order confirmation."""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    DELIVERY_ADDRESS = (By.ID, "address_delivery")
    BILLING_ADDRESS = (By.ID, "address_invoice")
    REVIEW_ROWS = (By.CSS_SELECTOR, "#cart_info tbody tr[id^='product-']")
    COMMENT = (By.CSS_SELECTOR, "textarea[name='message']")
    PLACE_ORDER = (By.CSS_SELECTOR, "a[href='/payment']")

    CARD_NAME = (By.CSS_SELECTOR, "input[data-qa='name-on-card']")
    CARD_NUMBER = (By.CSS_SELECTOR, "input[data-qa='card-number']")
    CARD_CVC = (By.CSS_SELECTOR, "input[data-qa='cvc']")
    CARD_MONTH = (By.CSS_SELECTOR, "input[data-qa='expiry-month']")
    CARD_YEAR = (By.CSS_SELECTOR, "input[data-qa='expiry-year']")
    PAY_BUTTON = (By.CSS_SELECTOR, "button[data-qa='pay-button']")

    ORDER_PLACED = (By.CSS_SELECTOR, "[data-qa='order-placed']")
    ORDER_CONFIRMATION = (By.XPATH, "//p[contains(text(),'Congratulations')]")

    def is_loaded(self):
        return self.is_visible(self.DELIVERY_ADDRESS)

    def get_delivery_address(self):
        return self.get_text(self.DELIVERY_ADDRESS)

    def get_order_product_ids(self):
        self.find(self.REVIEW_ROWS, "presence")
        return [row.get_attribute("id").replace("product-", "")
                for row in self.find_all(self.REVIEW_ROWS)]

    def add_comment(self, text):
        self.type(self.COMMENT, text)

    def place_order(self):
        self.click(self.PLACE_ORDER)

    def pay(self, card):
        self.type(self.CARD_NAME, card["name_on_card"])
        self.type(self.CARD_NUMBER, card["card_number"])
        self.type(self.CARD_CVC, card["cvc"])
        self.type(self.CARD_MONTH, card["expiry_month"])
        self.type(self.CARD_YEAR, card["expiry_year"])
        self.click(self.PAY_BUTTON)

    def is_order_placed(self):
        return self.is_visible(self.ORDER_PLACED)

    def get_confirmation_message(self):
        return self.get_text(self.ORDER_CONFIRMATION)
