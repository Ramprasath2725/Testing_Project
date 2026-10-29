"""Page Object for the product listing, search results, category and brand pages.

Category/brand pages reuse this class: they share the same title element,
product grid and left sidebar.
"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.config_reader import ConfigReader


class ProductsPage(BasePage):
    SEARCH_INPUT = (By.ID, "search_product")
    SEARCH_BUTTON = (By.ID, "submit_search")
    ALL_PRODUCTS_TITLE = (By.XPATH, "//h2[contains(text(),'All Products')]")
    SEARCHED_PRODUCTS_TITLE = (By.XPATH, "//h2[contains(text(),'Searched Products')]")
    PAGE_TITLE = (By.CSS_SELECTOR, ".features_items h2.title")
    PRODUCT_ITEMS = (By.CSS_SELECTOR, ".features_items .product-image-wrapper")

    def load(self):
        base = ConfigReader.get("general", "base_url")
        self.open(f"{base}/products")
        return self

    def is_loaded(self):
        return self.is_visible(self.ALL_PRODUCTS_TITLE)

    # --- search ---
    def search(self, term):
        self.type(self.SEARCH_INPUT, term)
        self.click(self.SEARCH_BUTTON)

    def searched_products_visible(self):
        return self.is_visible(self.SEARCHED_PRODUCTS_TITLE)

    def product_count(self):
        """Number of product cards (waits for at least one)."""
        return self.count(self.PRODUCT_ITEMS)

    def result_count_now(self):
        """Number of product cards right now, without waiting (0 is valid)."""
        return self.count_now(self.PRODUCT_ITEMS)

    def get_page_title(self):
        return " ".join(self.get_text(self.PAGE_TITLE).split())

    # --- product navigation ---
    @staticmethod
    def view_product_link(product_id):
        return (By.CSS_SELECTOR,
                f".features_items a[href='/product_details/{product_id}']")

    def open_product(self, product_id):
        self.scroll_into_view(self.view_product_link(product_id))
        self.click(self.view_product_link(product_id))

    # --- left sidebar: categories and brands ---
    def select_category(self, group, name, category_id):
        """Expand a category group (Women/Men/Kids), then pick a sub-category."""
        self.click((By.CSS_SELECTOR, f".category-products a[href='#{group}']"))
        self.click((By.CSS_SELECTOR, f".category-products a[href='/category_products/{category_id}']"))

    def select_brand(self, brand_name):
        self.click((By.XPATH, f"//div[contains(@class,'brands_products')]//a[contains(@href,'/brand_products/') "
                              f"and contains(normalize-space(.),'{brand_name}')]"))
