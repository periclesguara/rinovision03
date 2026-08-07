import logging
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler


def setup_logger(name="RinoVision", log_dir="logs"):
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_path = Path(log_dir) / "runtime.log"
    handler = TimedRotatingFileHandler(log_path, when="midnight", backupCount=7)

    formatter = logging.Formatter(
        "%(asctime)s — %(name)s — %(levelname)s — %(message)s"
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        logger.addHandler(handler)
    else:
        handler.close()
    return logger
