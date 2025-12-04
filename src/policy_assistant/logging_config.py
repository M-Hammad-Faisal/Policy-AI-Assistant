import logging


def setup_logging(level=logging.INFO):
    """
    Sets up the global logging configuration for the application.
    Call this once at the very start of the main script (e.g., in app.py).
    """
    # Use standard format suitable for Cloud Logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    # Return the logger for the main module (optional, but good practice)
    return logging.getLogger("policy-assistant")


# Set up logging immediately so any module importing this file benefits
logger = logging.getLogger("policy-assistant")

# Call the setup function to configure the root logger
setup_logging()
