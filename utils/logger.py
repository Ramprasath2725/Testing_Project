"""Project-wide logger factory.

Records go to a dated file under <project>/logs/. Console output is handled by
pytest's live logging (log_cli in pytest.ini), so nothing is printed twice.
"""
import logging
from datetime import datetime

from utils.config_reader import PROJECT_ROOT

_file_handler = None


def _get_file_handler():
    global _file_handler
    if _file_handler is None:
        log_dir = PROJECT_ROOT / "logs"
        try:
            log_dir.mkdir(exist_ok=True)
            _file_handler = logging.FileHandler(
                log_dir / f"test_run_{datetime.now():%Y%m%d}.log", encoding="utf-8"
            )
        except OSError:  # read-only file system etc. - logging must never break tests
            _file_handler = logging.NullHandler()
        _file_handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S"
        ))
    return _file_handler


def get_logger(name):
    logger = logging.getLogger(name)
    if not any(h is _get_file_handler() for h in logger.handlers):
        logger.setLevel(logging.INFO)
        logger.addHandler(_get_file_handler())
    return logger
