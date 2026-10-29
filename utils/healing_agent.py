"""Rule-based locator recovery ("self-healing" in the limited, honest sense).

This is NOT AI. When the primary locator times out, the agent tries a fixed,
ordered list of deterministic fallbacks and only accepts a candidate that
matches EXACTLY ONE element (an ambiguous match is never trusted).

Order of attempts:
  1. fallbacks declared explicitly by the page object
  2. strategies derived from the failed locator (see `derive_candidates`)

Every recovery is logged at WARNING level and recorded in `HealingAgent.events`
so the test report shows which page-object locators need updating. Recovery is
never used for negative checks (is_visible/is_present), so it cannot turn a
"element must be absent" assertion into a false result.

Disable with `[healing] enabled = false`, HEALING_ENABLED=false or --healing off.
"""
import re
from datetime import datetime

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By

from utils.logger import get_logger

logger = get_logger(__name__)

_SAFE_VALUE = re.compile(r"^[\w\-:.]+$")
_CSS_ATTR = re.compile(
    r"""^(?P<tag>[a-zA-Z0-9]*)\[(?P<attr>[\w-]+)=['"]?(?P<val>[^'"\]]+)['"]?\]$"""
)
_XPATH_TEXT = re.compile(r"""contains\(text\(\),\s*'([^']*)'\)""")
_XPATH_ATTR_EQ = re.compile(r"""@([\w-]+)\s*=\s*'([^']*)'""")
_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_LOWER = "abcdefghijklmnopqrstuvwxyz"


def xpath_literal(value):
    """Return `value` as a valid XPath string literal (handles quotes)."""
    if "'" not in value:
        return f"'{value}'"
    if '"' not in value:
        return f'"{value}"'
    parts = value.split("'")
    return "concat(" + ", \"'\", ".join(f"'{p}'" for p in parts) + ")"


def derive_candidates(locator):
    """Deterministically derive fallback locators. Returns [(strategy, locator)]."""
    by, value = locator
    out = []

    if by == By.ID and _SAFE_VALUE.match(value):
        out += [
            ("id->name", (By.CSS_SELECTOR, f"[name='{value}']")),
            ("id->data-qa", (By.CSS_SELECTOR, f"[data-qa='{value}']")),
            ("id->id-contains", (By.CSS_SELECTOR, f"[id*='{value}']")),
        ]
    elif by == By.NAME and _SAFE_VALUE.match(value):
        out += [
            ("name->id", (By.CSS_SELECTOR, f"[id='{value}']")),
            ("name->data-qa", (By.CSS_SELECTOR, f"[data-qa='{value}']")),
            ("name->name-contains", (By.CSS_SELECTOR, f"[name*='{value}']")),
        ]
    elif by == By.CLASS_NAME and _SAFE_VALUE.match(value):
        out.append(("class->class-contains", (By.CSS_SELECTOR, f"[class*='{value}']")))
    elif by == By.LINK_TEXT:
        out.append(("link-text->partial", (By.PARTIAL_LINK_TEXT, value)))
        out.append(("link-text->case-insensitive", (By.XPATH,
            f"//a[contains(translate(normalize-space(.),'{_UPPER}','{_LOWER}'),"
            f"{xpath_literal(value.lower())})]")))
    elif by == By.PARTIAL_LINK_TEXT:
        out.append(("partial-link->case-insensitive", (By.XPATH,
            f"//a[contains(translate(normalize-space(.),'{_UPPER}','{_LOWER}'),"
            f"{xpath_literal(value.lower())})]")))
    elif by == By.CSS_SELECTOR:
        match = _CSS_ATTR.match(value.strip())
        if match:
            tag, attr, val = match.group("tag"), match.group("attr"), match.group("val")
            out.append(("css-attr->contains", (By.CSS_SELECTOR, f"{tag}[{attr}*='{val}']")))
            if tag:
                out.append(("css-drop-tag", (By.CSS_SELECTOR, f"[{attr}='{val}']")))
        elif re.match(r"^#[\w-]+$", value.strip()):
            ident = value.strip()[1:]
            out += [
                ("css-#id->name", (By.CSS_SELECTOR, f"[name='{ident}']")),
                ("css-#id->id-contains", (By.CSS_SELECTOR, f"[id*='{ident}']")),
            ]
        elif re.match(r"^\.[\w-]+$", value.strip()):
            out.append(("css-.class->contains", (By.CSS_SELECTOR, f"[class*='{value.strip()[1:]}']")))
    elif by == By.XPATH:
        if _XPATH_TEXT.search(value):
            out.append(("xpath-text->normalized", (By.XPATH,
                _XPATH_TEXT.sub(lambda m: f"contains(normalize-space(.),'{m.group(1)}')", value))))
            out.append(("xpath-text->case-insensitive", (By.XPATH, _XPATH_TEXT.sub(
                lambda m: f"contains(translate(normalize-space(.),'{_UPPER}','{_LOWER}'),"
                          f"'{m.group(1).lower()}')", value))))
        for m in _XPATH_ATTR_EQ.finditer(value):
            relaxed = value[:m.start()] + f"contains(@{m.group(1)},'{m.group(2)}')" + value[m.end():]
            out.append((f"xpath-@{m.group(1)}->contains", (By.XPATH, relaxed)))

    return [item for item in out if item[1] != locator]


class HealingAgent:
    enabled = True
    events = []

    @classmethod
    def configure(cls, enabled):
        cls.enabled = bool(enabled)

    @classmethod
    def reset(cls):
        cls.events.clear()

    @classmethod
    def recover(cls, driver, locator, fallbacks=None):
        """Return the recovered WebElement, or None if no safe match exists."""
        if not cls.enabled:
            logger.info("[HEALER] disabled - not recovering %s", locator)
            return None

        attempts = [("declared-fallback", fb) for fb in (fallbacks or [])]
        attempts += derive_candidates(locator)
        logger.warning("[HEALER] primary locator failed: %s (%d fallbacks to try)",
                       locator, len(attempts))

        for strategy, candidate in attempts:
            try:
                matches = driver.find_elements(*candidate)
            except WebDriverException as exc:
                logger.debug("[HEALER] %s %s errored: %s", strategy, candidate, exc)
                continue
            if len(matches) == 1:
                cls._record(driver, locator, candidate, strategy)
                return matches[0]
            if len(matches) > 1:
                logger.info("[HEALER] %s %s matched %d elements - ambiguous, skipped",
                            strategy, candidate, len(matches))

        logger.error("[HEALER] no safe recovery for %s", locator)
        return None

    @classmethod
    def _record(cls, driver, original, healed, strategy):
        try:
            url = driver.current_url
        except WebDriverException:
            url = "unknown"
        cls.events.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "original": f"{original[0]}={original[1]}",
            "healed": f"{healed[0]}={healed[1]}",
            "strategy": strategy,
            "url": url,
        })
        logger.warning("[HEALER] RECOVERED via %s: %s -> %s (url=%s). "
                       "Update the page object.", strategy, original, healed, url)
