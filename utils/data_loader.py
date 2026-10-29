"""Loads static test data (products, categories, card details...) from
config/test_data.json so that test logic never hard-codes data."""
import json

from utils.config_reader import PROJECT_ROOT

_DATA_PATH = PROJECT_ROOT / "config" / "test_data.json"
_cache = None


def load_data():
    global _cache
    if _cache is None:
        with open(_DATA_PATH, encoding="utf-8") as handle:
            _cache = json.load(handle)
    return _cache


def get_product(product_id):
    return load_data()["products"][str(product_id)]
