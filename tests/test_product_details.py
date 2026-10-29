"""Product details page and reviews (site test cases 8 and 21)."""
import pytest

from pages.product_details_page import ProductDetailsPage
from pages.products_page import ProductsPage
from utils.data_loader import get_product, load_data

PRODUCT_ID = 1


@pytest.mark.smoke
@pytest.mark.products
def test_product_details_shown_after_view_product(driver):
    """TC13 - 'View Product' opens details with name, category, price, stock, condition, brand."""
    expected = get_product(PRODUCT_ID)
    ProductsPage(driver).load().open_product(PRODUCT_ID)

    details = ProductDetailsPage(driver)
    assert details.url_contains(f"/product_details/{PRODUCT_ID}")
    assert details.get_name() == expected["name"]
    assert details.get_detail("Category") == expected["category"]
    assert str(expected["price"]) in details.get_price_text()
    assert details.get_detail("Availability") == expected["availability"]
    assert details.get_detail("Condition") == expected["condition"]
    assert details.get_detail("Brand") == expected["brand"]


@pytest.mark.regression
@pytest.mark.products
def test_submit_product_review_shows_thank_you(driver):
    """TC14 - A review with name, email and text is accepted."""
    review = load_data()["review"]
    details = ProductDetailsPage(driver).load(PRODUCT_ID)
    details.submit_review(review["name"], review["email"], review["text"])
    assert "thank you for your review" in details.get_review_message().lower()
