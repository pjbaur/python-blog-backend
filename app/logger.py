import os
import logging
import logging.handlers
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default log levels mapping
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
    'TRACE': 5  # Custom TRACE level (lower than DEBUG)
}

# Add custom TRACE level
logging.addLevelName(5, "TRACE")

def trace(self, message, *args, **kws):
    """
    Log 'msg % args' with severity 'TRACE'.
    """
    if self.isEnabledFor(5):
        self._log(5, message, args, **kws)

# Add trace method to Logger class
logging.Logger.trace = trace

def setup_logging():
    """
    Set up application logging based on environment variables.
    """
    # Get logging configuration from environment variables, with defaults
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_date_format = os.getenv("LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")
    log_file = os.getenv("LOG_FILE", "app.log")
    log_max_size_mb = int(os.getenv("LOG_MAX_SIZE_MB", 10))
    log_backup_count = int(os.getenv("LOG_BACKUP_COUNT", 3))
    console_logging = os.getenv("CONSOLE_LOGGING", "true").lower() == "true"

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create a root logger
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVELS.get(log_level, logging.INFO))
    
    # Configure formatter
    formatter = logging.Formatter(log_format, log_date_format)
    
    # Configure file handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / log_file,
        maxBytes=log_max_size_mb * 1024 * 1024,  # Convert MB to bytes
        backupCount=log_backup_count
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Add console handler if enabled
    if console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Return the configured logger
    return logger

def get_logger(name):
    """
    Get a logger with the specified name.
    """
    return logging.getLogger(name)