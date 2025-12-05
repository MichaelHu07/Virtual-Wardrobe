import logging
import sys
from app.core.config import settings

def setup_logging() -> None:
    """
    Configure the logging for the application.
    """
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(settings.LOG_LEVEL)
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    
    # Remove existing handlers to avoid duplication
    if logger.hasHandlers():
        logger.handlers.clear()
        
    logger.addHandler(handler)

    # Set specific log levels for third-party libraries if needed
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

