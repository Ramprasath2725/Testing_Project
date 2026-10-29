"""Page Object for the shopping cart (/view_cart) and its checkout modal."""
import re

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.config_reader import ConfigReader


def to_int(text):
    """'Rs. 1,500' -> 1500"""
    return int(re.sub(r"\D", "", text))


class CartPage(BasePage):
    CART_ROWS = (By.CSS_SELECTOR, "#cart_info_table tbody tr[id^='product-']")
    EMPTY_CART = (By.ID, "empty_cart")
    CHECKOUT_BUTTON = (By.CSS_SELECTOR, "a.check_out")
    CHECKOUT_MODAL = (By.ID, "checkoutModal")
    MODAL_LOGIN_LINK = (By.XPATH, "//div[@id='checkoutModal']//a[@href='/login']")

    def load(self):
        base = ConfigReader.get("general", "base_url")
        self.open(f"{base}/view_cart")
        return self

    @staticmethod
    def _row(product_id):
        return f"//tr[@id='product-{product_id}']"

    def is_empty(self):
        return self.is_visible(self.EMPTY_CART)

    def get_empty_message(self):
        return self.get_text(self.EMPTY_CART)

    def get_product_ids(self):
        self.find(self.CART_ROWS, "presence")
        return [row.get_attribute("id").replace("product-", "")
                for row in self.find_all(self.CART_ROWS)]

    def get_row(self, product_id):
        """Return {'name','price','quantity','total'} for a cart line."""
        row = self._row(product_id)
        return {
            "name": self.get_text((By.XPATH, f"{row}//td[@class='cart_description']//a")),
            "price": to_int(self.get_text((By.XPATH, f"{row}//td[@class='cart_price']/p"))),
            "quantity": to_int(self.get_text((By.XPATH, f"{row}//td[@class='cart_quantity']/button"))),
            "total": to_int(self.get_text((By.XPATH, f"{row}//td[@class='cart_total']/p"))),
        }

    def remove_product(self, product_id):
        self.click((By.CSS_SELECTOR, f"a.cart_quantity_delete[data-product-id='{product_id}']"))
        self.wait.until(lambda d: not d.find_elements(By.XPATH, self._row(product_id)))

    def proceed_to_checkout(self):
        self.click(self.CHECKOUT_BUTTON)

    def is_checkout_modal_visible(self):
        return self.is_visible(self.MODAL_LOGIN_LINK)

    def click_register_login_in_modal(self):
        self.click(self.MODAL_LOGIN_LINK)
