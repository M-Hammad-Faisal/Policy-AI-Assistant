"""Centralized logging configuration for the Policy Assistant."""
import logging
from typing import Any, Final

APP_NAME: Final[str] = "policy-assistant"


def setup_logging(level: Any = logging.INFO) -> logging.Logger:
    """Set up the global logging configuration for the application."""
    # Use standard format suitable for Cloud Logging
    logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    return logging.getLogger(APP_NAME)


logger = logging.getLogger(APP_NAME)
setup_logging()
