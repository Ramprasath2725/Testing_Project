"""Checkout and order placement (site test cases 14-16)."""
import pytest

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.home_page import HomePage
from pages.products_page import ProductsPage
from utils.data_loader import load_data


@pytest.mark.regression
@pytest.mark.checkout
def test_checkout_as_guest_prompts_register_or_login(driver):
    """TC21 - Negative: a guest who clicks Proceed To Checkout gets the Register/Login prompt."""
    products = ProductsPage(driver).load()
    products.add_product_to_cart(1)
    products.view_cart_from_modal()

    cart = CartPage(driver)
    cart.proceed_to_checkout()
    assert cart.is_checkout_modal_visible(), "Register / Login prompt was not shown"
    cart.click_register_login_in_modal()
    assert cart.url_contains("/login")


@pytest.mark.smoke
@pytest.mark.checkout
def test_logged_in_user_can_place_order(driver, logged_in_user):
    """TC22 - Logged-in user: cart -> checkout -> payment -> order confirmed."""
    user = logged_in_user
    HomePage(driver).load().go_to("/products")
    products = ProductsPage(driver)
    products.add_product_to_cart(1)
    products.view_cart_from_modal()
    CartPage(driver).proceed_to_checkout()

    checkout = CheckoutPage(driver)
    assert checkout.is_loaded(), "Checkout page did not load"
    assert checkout.get_order_product_ids() == ["1"]
    address = checkout.get_delivery_address()
    assert user["address1"] in address and user["city"] in address

    checkout.add_comment("Automated order - please ignore")
    checkout.place_order()
    checkout.pay(load_data()["payment"])
    assert checkout.is_order_placed(), "'Order Placed!' not displayed after payment"
    assert "order has been confirmed" in checkout.get_confirmation_message().lower()
