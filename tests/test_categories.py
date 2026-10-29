"""Category and brand filtering from the left sidebar (site test cases 18 and 19)."""
import pytest

from pages.products_page import ProductsPage
from utils.data_loader import load_data

DATA = load_data()


@pytest.mark.regression
@pytest.mark.products
@pytest.mark.parametrize("category", DATA["categories"], ids=lambda c: f"{c['group']}-{c['name']}")
def test_category_filter_lists_matching_products(driver, category):
    """TC15 - Choosing a sub-category shows its title and products."""
    products = ProductsPage(driver).load()
    products.select_category(category["group"], category["name"], category["id"])
    assert products.url_contains(f"/category_products/{category['id']}")
    assert products.get_page_title().lower() == category["title"]
    assert products.product_count() > 0


@pytest.mark.regression
@pytest.mark.products
@pytest.mark.parametrize("brand", DATA["brands"], ids=lambda b: b["name"])
def test_brand_filter_lists_matching_products(driver, brand):
    """TC16 - Choosing a brand shows its title and products."""
    products = ProductsPage(driver).load()
    products.select_brand(brand["name"])
    assert products.url_contains("/brand_products/")
    assert products.get_page_title().lower() == brand["title"]
    assert products.product_count() > 0
