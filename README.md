# Selenium + PyTest UI Automation Framework

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-4.x-43B02A?logo=selenium&logoColor=white)
![PyTest](https://img.shields.io/badge/PyTest-8%2B-0A9EDC?logo=pytest&logoColor=white)
![Design](https://img.shields.io/badge/Pattern-Page%20Object%20Model-orange)

End-to-end UI test automation for [automationexercise.com](https://automationexercise.com), an
e-commerce demo site. Built with **Selenium WebDriver + Python + PyTest** using the
**Page Object Model**. 25 UI test functions (32 executed test items) plus 24 browser-free
framework unit tests.

> **Status:** see [Verification status](#verification-status) for exactly what has and has not been executed.

---

## Setup

```bash
git clone https://github.com/Ramprasath2725/Testing_Project.git
cd Testing_Project
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
Requires Python 3.10+ and Google Chrome (or Firefox). Selenium Manager downloads the matching driver automatically.

## Running tests

```bash
pytest                              # everything (UI tests need a browser + internet)
pytest -m unit                      # framework unit tests only - no browser, no network
pytest -m "not unit"                # UI tests only
pytest -m smoke                     # critical-path checks
pytest -m "cart or checkout"        # any marker expression (see pytest.ini)
pytest tests/test_cart.py           # one module
pytest --headless false             # watch the browser
pytest --browser firefox            # Firefox instead of Chrome
pytest -n 4                         # parallel (pytest-xdist); tests are isolated
pytest --base-url https://staging.example.com
pytest --healing off                # disable locator recovery (strict mode)
```
Environment variables `BASE_URL`, `BROWSER`, `HEADLESS`, `HEALING_ENABLED` work too (CLI > env > `config/config.ini`).

## Reporting

Every run writes (git-ignored) to `reports/`:
- `report.html` - self-contained pytest-html report; **failure screenshots and the failing URL are embedded**
- `junit.xml` - for CI dashboards

Also: `screenshots/` (PNG per failure), `logs/test_run_<date>.log`, and a terminal section listing any
locator that had to be recovered. Allure is optional (`pip install allure-pytest`; screenshots attach automatically).

---

## Architecture

```
config/
  config.ini            URL, browser, headless, timeouts, healing switch, negative-login data
  test_data.json        products, categories, brands, search terms, test card, contact text
pages/                  Page Object layer - locators + actions, no assertions
  base_page.py          waits, safe click/type, ad clean-up, header/footer/cart-modal helpers
  home_page.py  login_page.py  signup_page.py  products_page.py
  product_details_page.py  cart_page.py  checkout_page.py  contact_page.py
tests/                  25 UI test functions grouped by feature
  unit/                 24 browser-free tests of the framework itself
utils/
  config_reader.py      config.ini + env + CLI overrides
  driver_factory.py     Chrome/Firefox, headless, eager load, ad-host blocking (Chrome)
  healing_agent.py      deterministic locator recovery (see below)
  api_client.py         create/delete users through the site's REST API (set-up/tear-down only)
  data_factory.py       unique throw-away users, random passwords generated per run
  data_loader.py        reads test_data.json
  logger.py             file logging (console output via pytest live logging)
conftest.py             fixtures, CLI options, screenshot + healing-event reporting
.github/workflows/ci.yml
```

**Key design decisions**
- **POM:** locators and page actions live in `pages/`; tests contain only flow and assertions.
- **Explicit waits only** - no `time.sleep`. Interactions wait for *clickable*/*visible*, retry on stale elements,
  and fall back to a JS click if an ad overlay intercepts the click.
- **Isolation:** one fresh browser per test; every test creates its own unique user, so tests can run in parallel.
- **Fast, reliable set-up:** users needed as a precondition are created/deleted through the site's REST API
  (`registered_user` fixture). The behaviour *under test* is always driven through the UI.
- **No secrets in the repo:** emails use `example.com`, passwords are random per run; the card number in
  `test_data.json` is a public dummy number for this demo site.
- **Ads:** the site shows Google ads that intercept clicks. Chrome blocks ad hosts via DevTools and
  `BasePage.dismiss_ads()` removes leftover overlays.

### Locator recovery (`utils/healing_agent.py`)

This is **rule-based, not AI**. When a locator times out, the agent tries, in fixed order:
1. fallbacks declared by the page object (`find(..., fallbacks=[...])`)
2. derived fallbacks, e.g. `id -> name`, `id -> data-qa`, CSS `[attr='x'] -> [attr*='x']`,
   XPath `@href='x' -> contains(@href,'x')`, `contains(text(),..)` -> normalised / case-insensitive text.

Safety rules: a candidate is accepted **only if it matches exactly one element**; ambiguous matches are skipped;
negative checks (`is_visible`, `is_present`) never use recovery. Every recovery is logged as a `WARNING`, recorded
per test, and printed in the terminal summary so the page object gets fixed. `--healing off` disables it.

---

## The 25 UI test cases

"Site TC" refers to the numbered cases on [automationexercise.com/test_cases](https://automationexercise.com/test_cases).

| ID | Module | Test | What it verifies | Site TC |
|----|--------|------|------------------|---------|
| TC01 | test_home | `test_home_page_loads` | Title and banner displayed | - |
| TC02 | test_home | `test_header_navigation_links_open_correct_page` (x5) | Products, Cart, Login, Contact, Test Cases links | - |
| TC03 | test_login | `test_new_user_signup_navigates_to_account_info` | New name+email reaches account form | 1 |
| TC04 | test_registration | `test_register_new_user_and_delete_account` | Full registration, auto-login, delete account | 1 |
| TC05 | test_registration | `test_register_with_existing_email_shows_error` | Duplicate email rejected | 5 |
| TC06 | test_login | `test_login_with_valid_credentials` | "Logged in as <name>" | 2 |
| TC07 | test_login | `test_login_with_invalid_credentials_shows_error` | Unknown user -> error | 3 |
| TC08 | test_login | `test_login_with_wrong_password_for_registered_user` | Wrong password -> error, stays logged out | 3 |
| TC09 | test_login | `test_logout_returns_to_login_page` | Logout ends session | 4 |
| TC10 | test_products | `test_all_products_page_loads` | Listing renders products | 8 |
| TC11 | test_products | `test_search_returns_results` (x3) | Search "top", "dress", "tshirt" | 9 |
| TC12 | test_products | `test_search_with_no_match_returns_no_products` | Negative search -> empty grid | - |
| TC13 | test_product_details | `test_product_details_shown_after_view_product` | Name, category, price, stock, condition, brand | 8 |
| TC14 | test_product_details | `test_submit_product_review_shows_thank_you` | Review submission | 21 |
| TC15 | test_categories | `test_category_filter_lists_matching_products` (x2) | Women-Dress, Men-Jeans | 18 |
| TC16 | test_categories | `test_brand_filter_lists_matching_products` | Brand "Polo" | 19 |
| TC17 | test_cart | `test_add_single_product_to_cart` | Name, price, qty 1, total | 12 |
| TC18 | test_cart | `test_add_multiple_products_shows_correct_line_totals` | Two lines, price x qty | 12 |
| TC19 | test_cart | `test_quantity_chosen_on_product_page_is_kept_in_cart` | Qty 4 -> total 4 x price | 13 |
| TC20 | test_cart | `test_remove_product_from_cart_empties_cart` | "Cart is empty!" | 17 |
| TC21 | test_checkout | `test_checkout_as_guest_prompts_register_or_login` | Guest checkout blocked (negative) | 14 |
| TC22 | test_checkout | `test_logged_in_user_can_place_order` | Cart -> checkout -> pay -> confirmed | 16 |
| TC23 | test_contact | `test_contact_us_form_submission_shows_success` | Form + file upload + dialog | 6 |
| TC24 | test_subscription | `test_footer_subscription_success` | Footer subscription banner | 10 |
| TC25 | test_e2e | `test_new_customer_registers_searches_buys_and_deletes_account` | Register -> search -> cart -> pay -> delete | 15 |

Totals: **25 test functions -> 32 test items** (TC02 x5, TC11 x3, TC15 x2 add 7).
Product/category data (IDs, names, prices) comes from the live site's rendered pages and lives in `config/test_data.json`.

---

## Verification status

Be aware of what has been proven:

| Area | Status |
|------|--------|
| 24 framework unit tests (`pytest -m unit`) | **Executed: 24 passed** (also under `-n 2`) |
| Original `is_visible` bug (raised `NoSuchElementException`) | **Reproduced on the original code and confirmed fixed** |
| Collection of all UI tests | **Executed:** 32 items collected, no import/syntax errors |
| 25 UI tests against the live site | **NOT executed.** The environment used to author this had no browser and no network route to automationexercise.com |

Consequences for the UI tests: locators for the data-qa based forms (login, signup, payment, contact) and the
cart/checkout tables were written from knowledge of the site's markup; only the rendered page content
(category IDs, product names/prices, product detail fields) was checked against the live site. **Expect to
adjust a few locators on the first real run.** The terminal "Locator recovery events" section and
`reports/report.html` will point at them. Assertions most worth verifying first: category/brand page titles
(TC15/16), delivery-address text (TC22), and the order-confirmation text (TC22/TC25).

## Continuous integration

`.github/workflows/ci.yml` runs on pushes/PRs to `main` and manually:
1. **unit** job - framework unit tests (no browser).
2. **ui** job (needs unit) - Chrome headless, `-n 2`, one rerun for network flakiness (reruns show in the report).
Reports go up as artifacts; screenshots and logs upload on failure.

## Roadmap
- [ ] API test suite against `/api/*` endpoints
- [ ] Allure trend history
- [ ] Playwright comparison branch
