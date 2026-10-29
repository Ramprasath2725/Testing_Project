"""Thin client for the site's documented REST API (see /api_list).

Used ONLY for fast, reliable test-data set-up/tear-down (create/delete a
user). The behaviour under test is always exercised through the UI.
Note: the site returns HTTP 200 and puts the real status in `responseCode`.
"""
import requests

from utils.config_reader import ConfigReader
from utils.logger import get_logger

logger = get_logger(__name__)
TIMEOUT = 30


def _base():
    return ConfigReader.get("general", "base_url").rstrip("/")


def _response_code(response):
    try:
        return response.json().get("responseCode")
    except ValueError:
        logger.error("API returned non-JSON body (HTTP %s)", response.status_code)
        return None


def create_account(user):
    payload = {
        "name": user["name"], "email": user["email"], "password": user["password"],
        "title": user["title"], "birth_date": user["birth_day"],
        "birth_month": user["birth_month"], "birth_year": user["birth_year"],
        "firstname": user["first_name"], "lastname": user["last_name"],
        "company": user["company"], "address1": user["address1"],
        "address2": user["address2"], "country": user["country"],
        "zipcode": user["zipcode"], "state": user["state"], "city": user["city"],
        "mobile_number": user["mobile_number"],
    }
    try:
        response = requests.post(f"{_base()}/api/createAccount", data=payload, timeout=TIMEOUT)
    except requests.RequestException as exc:
        logger.error("createAccount request failed: %s", exc)
        return False
    code = _response_code(response)
    logger.info("API createAccount(%s) -> responseCode=%s", user["email"], code)
    return code == 201


def delete_account(email, password):
    """Best-effort clean-up; never raises."""
    try:
        response = requests.delete(
            f"{_base()}/api/deleteAccount",
            data={"email": email, "password": password}, timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        logger.warning("deleteAccount request failed: %s", exc)
        return False
    code = _response_code(response)
    logger.info("API deleteAccount(%s) -> responseCode=%s", email, code)
    return code == 200
