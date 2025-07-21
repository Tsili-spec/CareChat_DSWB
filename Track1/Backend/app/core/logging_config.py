
import logging
import sys
from logging.handlers import TimedRotatingFileHandler

# Define log format
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Define log file
LOG_FILE = "logs/carechat_api.log"

def setup_logging():
    """
    Sets up the application logging configuration.
    """
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Console Handler (for development and container logs)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (for persistent logs)
    # Rotates log files every day, keeps 7 days of backups
    file_handler = TimedRotatingFileHandler(
        LOG_FILE, when="midnight", interval=1, backupCount=7
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Set logger for specific libraries to a higher level to reduce noise
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("passlib").setLevel(logging.WARNING)

    logging.info("Logging configured successfully.")

def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger with the specified name.
    """
    return logging.getLogger(name) 