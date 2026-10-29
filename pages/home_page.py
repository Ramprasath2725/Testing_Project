"""Page Object for the Automation Exercise home page.

Header, footer subscription and the add-to-cart modal live in BasePage.
"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.config_reader import ConfigReader


class HomePage(BasePage):
    SLIDER = (By.ID, "slider")

    # Kept for backwards compatibility with earlier tests
    PRODUCTS_NAV = BasePage.nav_link("/products")
    LOGIN_NAV = BasePage.nav_link("/login")
    CART_NAV = BasePage.nav_link("/view_cart")

    def load(self):
        self.open(ConfigReader.get("general", "base_url"))
        return self

    def is_loaded(self):
        return self.is_visible(self.SLIDER)

    def go_to_products(self):
        self.go_to("/products")

    def go_to_login(self):
        self.go_to("/login")
