import logging
import os
from logging.handlers import RotatingFileHandler

# Ensure the logs directory exists
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Configure RotatingFileHandler
file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=10240, backupCount=10
)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(pathname)s - %(message)s")
file_handler.setFormatter(formatter)

# Configure logger
logger = logging.getLogger("affinityTradesLogger")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(logging.StreamHandler())  # Also log to console