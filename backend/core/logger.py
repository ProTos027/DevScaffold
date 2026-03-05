import logging

# Global Logging Configuration
logging.basicConfig(level=logging.INFO)

class ColoredFormatter(logging.Formatter):
    """
    INFO: Green
    WARNING: Yellow
    ERROR: Red
    """
    def format(self, record):
        color = ""
        if record.levelno == logging.INFO:
            color = "\033[92m"  # Green
        elif record.levelno == logging.WARNING:
            color = "\033[93m"  # Yellow
        elif record.levelno == logging.ERROR:
            color = "\033[91m"  # Red
        return f"{color}{super().format(record)}\033[0m"

def get_logger(name: str):
    """
    Centralized logger factory.
    Ensures color formatting is applied to the stream handler.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(ColoredFormatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
