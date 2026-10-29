"""User registration through the UI (site test cases 1 and 5)."""
import pytest

from pages.login_page import LoginPage
from pages.signup_page import SignupPage


@pytest.mark.auth
@pytest.mark.regression
def test_register_new_user_and_delete_account(driver, new_user):
    """TC04 - Full registration: create account, auto login, then delete it."""
    login = LoginPage(driver).load()
    login.start_signup(new_user["name"], new_user["email"])

    signup = SignupPage(driver)
    assert signup.is_loaded(), "Account-information form not displayed"
    signup.fill_account_information(new_user)
    assert "account created" in signup.get_account_created_message().lower()

    signup.click_continue()
    assert signup.is_logged_in(), "User is not logged in after registration"
    assert signup.get_logged_in_username() == new_user["name"]

    signup.delete_account()
    assert "account deleted" in signup.get_account_deleted_message().lower()
    signup.click_continue()


@pytest.mark.auth
@pytest.mark.regression
def test_register_with_existing_email_shows_error(driver, registered_user):
    """TC05 - Signing up with an already registered email is rejected."""
    login = LoginPage(driver).load()
    login.start_signup("Another Name", registered_user["email"])
    assert "already exist" in login.get_signup_error().lower()
