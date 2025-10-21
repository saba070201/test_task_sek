import logging
import os
from core.settings import get_settings

LOG_LEVEL = get_settings().LOG_LEVEL.upper()
try:
    level = getattr(logging, LOG_LEVEL)
except Exception:
    level = logging.INFO

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_DIR = os.path.join(ROOT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setFormatter(formatter)

root_logger = logging.getLogger()
if not root_logger.handlers:
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def get_logger(name: str | None = None) -> logging.Logger:
    return logging.getLogger(name)
