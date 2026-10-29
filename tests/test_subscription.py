"""Footer subscription test - exercises scrolling + a dynamic success banner."""
import pytest

from pages.home_page import HomePage


@pytest.mark.regression
@pytest.mark.contact
def test_footer_subscription_success(driver):
    """TC24 - Subscribing from the footer shows the success banner."""
    home = HomePage(driver).load()
    home.subscribe("qa_subscriber@example.com")
    assert "successfully subscribed" in home.get_subscription_message().lower()
