"""Unit tests for HealingAgent. Use a fake driver: no browser, no network."""
import pytest
from selenium.webdriver.common.by import By

from utils.healing_agent import HealingAgent, derive_candidates, xpath_literal

pytestmark = pytest.mark.unit


class FakeDriver:
    """find_elements() answers from a {(by, value): [elements]} map."""
    current_url = "https://example.test/page"

    def __init__(self, mapping):
        self.mapping = mapping
        self.queries = []

    def find_elements(self, by, value):
        self.queries.append((by, value))
        return self.mapping.get((by, value), [])


@pytest.fixture(autouse=True)
def _clean_agent():
    HealingAgent.reset()
    HealingAgent.configure(True)
    yield
    HealingAgent.reset()
    HealingAgent.configure(True)


def test_recovers_id_locator_via_name_attribute():
    el = object()
    driver = FakeDriver({(By.CSS_SELECTOR, "[name='search']"): [el]})
    assert HealingAgent.recover(driver, (By.ID, "search")) is el
    assert HealingAgent.events[0]["strategy"] == "id->name"


def test_declared_fallback_is_tried_before_derived_ones():
    declared, derived = object(), object()
    driver = FakeDriver({
        (By.CSS_SELECTOR, "#new-id"): [declared],
        (By.CSS_SELECTOR, "[name='old']"): [derived],
    })
    found = HealingAgent.recover(driver, (By.ID, "old"), fallbacks=[(By.CSS_SELECTOR, "#new-id")])
    assert found is declared
    assert HealingAgent.events[0]["strategy"] == "declared-fallback"


def test_ambiguous_match_is_never_trusted():
    driver = FakeDriver({(By.CSS_SELECTOR, "[name='q']"): [object(), object()]})
    assert HealingAgent.recover(driver, (By.ID, "q")) is None
    assert HealingAgent.events == []


def test_returns_none_when_nothing_matches():
    assert HealingAgent.recover(FakeDriver({}), (By.ID, "ghost")) is None
    assert HealingAgent.events == []


def test_disabled_agent_does_not_query_the_page():
    HealingAgent.configure(False)
    driver = FakeDriver({(By.CSS_SELECTOR, "[name='q']"): [object()]})
    assert HealingAgent.recover(driver, (By.ID, "q")) is None
    assert driver.queries == []


def test_event_records_original_healed_strategy_and_url():
    driver = FakeDriver({(By.CSS_SELECTOR, "[data-qa='go']"): [object()]})
    HealingAgent.recover(driver, (By.ID, "go"))
    event = HealingAgent.events[0]
    assert event["original"] == "id=go"
    assert event["healed"] == "css selector=[data-qa='go']"
    assert event["url"] == "https://example.test/page"


def test_css_attribute_selector_is_relaxed_to_contains():
    cands = dict(derive_candidates((By.CSS_SELECTOR, "input[data-qa='login-email']")))
    assert cands["css-attr->contains"] == (By.CSS_SELECTOR, "input[data-qa*='login-email']")
    assert cands["css-drop-tag"] == (By.CSS_SELECTOR, "[data-qa='login-email']")


def test_xpath_text_and_attribute_are_relaxed():
    cands = dict(derive_candidates((By.XPATH, "//a[@href='/products' and contains(text(),'Products')]")))
    assert "xpath-@href->contains" in cands
    assert "contains(@href,'/products')" in cands["xpath-@href->contains"][1]
    assert "xpath-text->normalized" in cands
    assert "xpath-text->case-insensitive" in cands


def test_link_text_gets_partial_and_case_insensitive_candidates():
    names = [name for name, _ in derive_candidates((By.LINK_TEXT, "Sign Up"))]
    assert names == ["link-text->partial", "link-text->case-insensitive"]


def test_no_unsafe_candidates_for_values_with_quotes():
    assert derive_candidates((By.ID, "it's")) == []


@pytest.mark.parametrize("raw, expected", [
    ("plain", "'plain'"),
    ("it's", '"it\'s"'),
])
def test_xpath_literal_quoting(raw, expected):
    assert xpath_literal(raw) == expected


def test_xpath_literal_with_both_quote_types_uses_concat():
    assert xpath_literal("""a'b"c""").startswith("concat(")
