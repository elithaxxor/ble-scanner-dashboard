import logging
from logging.handlers import RotatingFileHandler
from config import LOG_FILE, LOG_LEVEL


def setup_logging() -> None:
    """Configure logging with rotation."""
    handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[handler],
    )
