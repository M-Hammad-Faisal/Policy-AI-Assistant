import logging
from typing import Final

# Define the application name for the logger instance
APP_NAME: Final[str] = "policy-assistant"

def setup_logging(level=logging.INFO) -> logging.Logger:
    """
    Sets up the global logging configuration for the application.
    """
    # Use standard format suitable for Cloud Logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(APP_NAME)

# Get the logger instance that will be imported across all modules
logger = logging.getLogger(APP_NAME)
setup_logging()