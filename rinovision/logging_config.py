import logging
from .config import get_log_level


def configure_logging() -> logging.Logger:
    logging.basicConfig(level=getattr(logging, get_log_level(), logging.INFO))
    return logging.getLogger("rinovision")
