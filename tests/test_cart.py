"""Cart behaviour: add, multiple lines, quantity, remove (site test cases 12, 13, 17)."""
import pytest

from pages.cart_page import CartPage
from pages.product_details_page import ProductDetailsPage
from pages.products_page import ProductsPage
from utils.data_loader import get_product


@pytest.mark.smoke
@pytest.mark.cart
def test_add_single_product_to_cart(driver):
    """TC17 - One product added from the listing appears in the cart (qty 1)."""
    product = get_product(1)
    products = ProductsPage(driver).load()
    products.add_product_to_cart(1)
    products.view_cart_from_modal()

    cart = CartPage(driver)
    assert cart.get_product_ids() == ["1"]
    row = cart.get_row(1)
    assert row["name"] == product["name"]
    assert row["price"] == product["price"]
    assert row["quantity"] == 1
    assert row["total"] == product["price"]


@pytest.mark.regression
@pytest.mark.cart
def test_add_multiple_products_shows_correct_line_totals(driver):
    """TC18 - Two products give two cart lines with price x quantity totals."""
    products = ProductsPage(driver).load()
    products.add_product_to_cart(1)
    products.continue_shopping()
    products.add_product_to_cart(2)
    products.view_cart_from_modal()

    cart = CartPage(driver)
    assert sorted(cart.get_product_ids()) == ["1", "2"]
    for product_id in (1, 2):
        row = cart.get_row(product_id)
        assert row["price"] == get_product(product_id)["price"]
        assert row["total"] == row["price"] * row["quantity"]


@pytest.mark.regression
@pytest.mark.cart
def test_quantity_chosen_on_product_page_is_kept_in_cart(driver):
    """TC19 - Quantity 4 on the details page gives quantity 4 and total 4 x price."""
    quantity = 4
    price = get_product(1)["price"]
    details = ProductDetailsPage(driver).load(1)
    details.set_quantity(quantity)
    details.add_to_cart()
    details.view_cart_from_modal()

    row = CartPage(driver).get_row(1)
    assert row["quantity"] == quantity
    assert row["total"] == quantity * price


@pytest.mark.regression
@pytest.mark.cart
def test_remove_product_from_cart_empties_cart(driver):
    """TC20 - Removing the only product shows 'Cart is empty!'."""
    products = ProductsPage(driver).load()
    products.add_product_to_cart(1)
    products.view_cart_from_modal()

    cart = CartPage(driver)
    assert cart.get_product_ids() == ["1"]
    cart.remove_product(1)
    assert cart.is_empty()
    assert "cart is empty" in cart.get_empty_message().lower()
