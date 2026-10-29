"""Home page: availability and header navigation."""
import pytest

from pages.home_page import HomePage


@pytest.mark.smoke
def test_home_page_loads(driver):
    """TC01 - Home page loads with the expected title and banner."""
    home = HomePage(driver).load()
    assert "Automation Exercise" in home.get_title()
    assert home.is_loaded(), "Home page banner/slider was not displayed"


@pytest.mark.smoke
@pytest.mark.parametrize("href", ["/products", "/view_cart", "/login", "/contact_us", "/test_cases"])
def test_header_navigation_links_open_correct_page(driver, href):
    """TC02 - Each header link navigates to its page."""
    home = HomePage(driver).load()
    home.go_to(href)
    assert home.url_contains(href), f"Clicking '{href}' ended on {home.current_url()}"
