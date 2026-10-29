"""Page Object for a single product page (/product_details/<id>)."""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.config_reader import ConfigReader


class ProductDetailsPage(BasePage):
    NAME = (By.CSS_SELECTOR, ".product-information h2")
    PRICE = (By.CSS_SELECTOR, ".product-information span span")
    QUANTITY = (By.ID, "quantity")
    ADD_TO_CART = (By.CSS_SELECTOR, ".product-information button.cart")

    REVIEW_NAME = (By.ID, "name")
    REVIEW_EMAIL = (By.ID, "email")
    REVIEW_TEXT = (By.ID, "review")
    REVIEW_SUBMIT = (By.ID, "button-review")
    REVIEW_SUCCESS = (By.XPATH, "//*[contains(text(),'Thank you for your review')]")

    def load(self, product_id):
        base = ConfigReader.get("general", "base_url")
        self.open(f"{base}/product_details/{product_id}")
        return self

    def is_loaded(self):
        return self.is_visible(self.NAME)

    def get_name(self):
        return self.get_text(self.NAME)

    def get_price_text(self):
        return self.get_text(self.PRICE)

    def get_detail(self, label):
        """Value of 'Category' / 'Availability' / 'Condition' / 'Brand'."""
        text = self.get_text((By.XPATH, f"//div[@class='product-information']//p[contains(.,'{label}')]"))
        return text.split(":", 1)[1].strip()

    def set_quantity(self, quantity):
        self.type(self.QUANTITY, str(quantity))

    def add_to_cart(self):
        self.click(self.ADD_TO_CART)
        self.find(self.CART_MODAL_TITLE, "visible")

    def submit_review(self, name, email, text):
        self.scroll_into_view(self.REVIEW_NAME)
        self.type(self.REVIEW_NAME, name)
        self.type(self.REVIEW_EMAIL, email)
        self.type(self.REVIEW_TEXT, text)
        self.click(self.REVIEW_SUBMIT)

    def get_review_message(self):
        return self.get_text(self.REVIEW_SUCCESS)
