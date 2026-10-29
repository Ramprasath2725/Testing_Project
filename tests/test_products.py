"""Product browsing + search, including a data-driven (parametrized) search."""
import pytest

from pages.products_page import ProductsPage
from utils.data_loader import load_data

SEARCH = load_data()["search_terms"]


@pytest.mark.smoke
@pytest.mark.products
def test_all_products_page_loads(driver):
    """TC10 - The listing renders with products."""
    products = ProductsPage(driver).load()
    assert products.is_loaded()
    assert products.product_count() > 0, "No products rendered on the listing page"


@pytest.mark.regression
@pytest.mark.products
@pytest.mark.parametrize("search_term", SEARCH["valid"])
def test_search_returns_results(driver, search_term):
    """TC11 - Searching known terms returns matching products."""
    products = ProductsPage(driver).load()
    products.search(search_term)
    assert products.searched_products_visible(), (
        f"'Searched Products' header not shown for term '{search_term}'"
    )
    assert products.product_count() > 0, f"No results for '{search_term}'"


@pytest.mark.regression
@pytest.mark.products
def test_search_with_no_match_returns_no_products(driver):
    """TC12 - Negative: a term that matches nothing shows the header but no products."""
    products = ProductsPage(driver).load()
    products.search(SEARCH["no_match"])
    assert products.searched_products_visible()
    assert products.result_count_now() == 0
