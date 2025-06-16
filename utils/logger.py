import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime


def setup_logger(name="RinoVision", log_dir="logs"):
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "runtime.log")
    handler = TimedRotatingFileHandler(log_path, when="midnight", backupCount=7)

    formatter = logging.Formatter(
        "%(asctime)s — %(name)s — %(levelname)s — %(message)s"
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger
