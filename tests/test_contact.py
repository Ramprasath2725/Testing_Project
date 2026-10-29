"""Contact Us form (site test case 6)."""
import pytest

from pages.contact_page import ContactPage
from utils.data_loader import load_data


@pytest.mark.regression
@pytest.mark.contact
def test_contact_us_form_submission_shows_success(driver, tmp_path):
    """TC23 - Form with attachment is submitted, the dialog accepted, success shown."""
    data = load_data()["contact"]
    attachment = tmp_path / "attachment.txt"
    attachment.write_text("Attachment created by the automated test suite.")

    contact = ContactPage(driver).load()
    assert contact.is_loaded()
    contact.submit_form("QA Tester", "qa_contact@example.com",
                        data["subject"], data["message"], attachment)
    assert "details have been submitted successfully" in contact.get_success_message().lower()
