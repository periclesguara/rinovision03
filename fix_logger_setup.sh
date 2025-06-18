#!/bin/bash

echo "[1/4] Criando utils/logger.py..."
mkdir -p utils
cat <<EOF > utils/logger.py
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

def setup_logger(name="RinoVision", log_dir="logs"):
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "runtime.log")
    handler = TimedRotatingFileHandler(log_path, when="midnight", backupCount=7)

    formatter = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger
EOF

echo "[2/4] Injetando logger em main.py..."
sed -i '/sys.path.append/a from utils.logger import setup_logger\nlogger = setup_logger()\nlogger.info("🚀 RinoVision iniciado com sucesso!")' main.py

echo "[3/4] Rodando black..."
black .

echo "[4/4] Tudo pronto, logs integrados com sucesso!"
