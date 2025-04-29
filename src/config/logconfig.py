import logging
from logging.handlers import RotatingFileHandler
import os

# Ensure logs directory exists
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Log file path
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Define log format
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

# Create a logger (Log level: INFO, DEBUG, WARNING, ERROR, CRITICAL)
logger = logging.getLogger("fastapi-logger")
logger.setLevel(logging.INFO)

# Console Handler (for logs in terminal)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# File Handler (to save logs in a file)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1000, backupCount=3)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
