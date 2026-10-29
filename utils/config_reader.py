"""Centralised reader for config/config.ini.

Lookup order (highest priority first):
  1. runtime overrides   (set from CLI options in conftest.py)
  2. environment vars    (BASE_URL, BROWSER, HEADLESS, HEALING_ENABLED)
  3. config/config.ini
"""
import configparser
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "config.ini"

_ENV_OVERRIDES = {
    ("general", "base_url"): "BASE_URL",
    ("general", "browser"): "BROWSER",
    ("general", "headless"): "HEADLESS",
    ("healing", "enabled"): "HEALING_ENABLED",
}
_TRUE = {"1", "true", "yes", "on"}


class ConfigReader:
    _config = None
    _runtime = {}

    @classmethod
    def _load(cls):
        if cls._config is None:
            cls._config = configparser.ConfigParser()
            cls._config.read(CONFIG_PATH)
        return cls._config

    @classmethod
    def override(cls, section, key, value):
        """Set a runtime override (used for CLI options)."""
        cls._runtime[(section, key)] = str(value)

    @classmethod
    def clear_overrides(cls):
        cls._runtime.clear()

    @classmethod
    def _override_value(cls, section, key):
        if (section, key) in cls._runtime:
            return cls._runtime[(section, key)]
        env_name = _ENV_OVERRIDES.get((section, key))
        if env_name and os.environ.get(env_name):
            return os.environ[env_name]
        return None

    @classmethod
    def get(cls, section, key, fallback=None):
        value = cls._override_value(section, key)
        if value is not None:
            return value
        return cls._load().get(section, key, fallback=fallback)

    @classmethod
    def get_bool(cls, section, key, fallback=False):
        value = cls._override_value(section, key)
        if value is not None:
            return value.strip().lower() in _TRUE
        return cls._load().getboolean(section, key, fallback=fallback)

    @classmethod
    def get_int(cls, section, key, fallback=0):
        value = cls._override_value(section, key)
        if value is not None:
            return int(value)
        return cls._load().getint(section, key, fallback=fallback)
