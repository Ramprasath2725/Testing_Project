"""End-to-end customer journey (site test case 15: register before checkout)."""
import pytest

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.login_page import LoginPage
from pages.products_page import ProductsPage
from pages.signup_page import SignupPage
from utils.data_loader import get_product, load_data


@pytest.mark.e2e
@pytest.mark.regression
def test_new_customer_registers_searches_buys_and_deletes_account(driver, new_user):
    """TC25 - Register -> search -> add to cart -> checkout -> pay -> delete account."""
    product = get_product(1)

    # 1. Register through the UI
    login = LoginPage(driver).load()
    login.start_signup(new_user["name"], new_user["email"])
    signup = SignupPage(driver)
    assert signup.is_loaded()
    signup.fill_account_information(new_user)
    assert "account created" in signup.get_account_created_message().lower()
    signup.click_continue()
    assert signup.is_logged_in()

    # 2. Find the product by search and add it to the cart
    signup.go_to("/products")
    products = ProductsPage(driver)
    products.search(product["name"])
    assert products.searched_products_visible()
    products.add_product_to_cart(1)
    products.view_cart_from_modal()

    cart = CartPage(driver)
    row = cart.get_row(1)
    assert row["name"] == product["name"] and row["total"] == product["price"]

    # 3. Checkout and pay
    cart.proceed_to_checkout()
    checkout = CheckoutPage(driver)
    assert checkout.is_loaded()
    checkout.place_order()
    checkout.pay(load_data()["payment"])
    assert checkout.is_order_placed()

    # 4. Clean up through the UI
    checkout.delete_account()
    assert "account deleted" in signup.get_account_deleted_message().lower()
