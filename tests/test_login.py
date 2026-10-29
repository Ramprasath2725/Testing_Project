"""Login / logout: positive-navigation and negative paths (site test cases 2-4)."""
import time

import pytest

from pages.login_page import LoginPage
from utils.config_reader import ConfigReader


@pytest.mark.regression
@pytest.mark.login
@pytest.mark.auth
def test_login_with_invalid_credentials_shows_error(driver):
    """TC07 - Unregistered credentials produce an error message."""
    login = LoginPage(driver).load()
    login.login(
        ConfigReader.get("test_data", "invalid_email"),
        ConfigReader.get("test_data", "invalid_password"),
    )
    assert "incorrect" in login.get_login_error().lower()


@pytest.mark.regression
@pytest.mark.login
@pytest.mark.auth
def test_new_user_signup_navigates_to_account_info(driver):
    """TC03 - Valid name + new email moves on to 'Enter Account Information'."""
    login = LoginPage(driver).load()
    unique_email = f"qa_auto_{int(time.time())}@example.com"
    login.start_signup("QA Tester", unique_email)
    assert login.is_account_info_displayed(), (
        "Signup did not navigate to the 'Enter Account Information' page"
    )


@pytest.mark.smoke
@pytest.mark.login
@pytest.mark.auth
def test_login_with_valid_credentials(driver, registered_user):
    """TC06 - A registered user can log in and sees 'Logged in as <name>'."""
    login = LoginPage(driver).load()
    login.login(registered_user["email"], registered_user["password"])
    assert login.is_logged_in(), "'Logged in as' not shown after valid login"
    assert login.get_logged_in_username() == registered_user["name"]


@pytest.mark.regression
@pytest.mark.login
@pytest.mark.auth
def test_login_with_wrong_password_for_registered_user(driver, registered_user):
    """TC08 - Correct email + wrong password is rejected and the user stays logged out."""
    login = LoginPage(driver).load()
    login.login(registered_user["email"], "Wrong-Password-1")
    assert "incorrect" in login.get_login_error().lower()
    assert not login.is_logged_in(timeout=2)


@pytest.mark.regression
@pytest.mark.login
@pytest.mark.auth
def test_logout_returns_to_login_page(driver, logged_in_user):
    """TC09 - Logging out lands on the login page and ends the session."""
    page = LoginPage(driver)
    page.logout()
    assert page.url_contains("/login")
    assert page.is_login_form_displayed(), "Login form not shown after logout"
    assert not page.is_logged_in(timeout=2)
