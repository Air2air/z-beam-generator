"""Logging setup for Z-Beam Generator."""

import logging
import os
from rich.logging import RichHandler

def setup_logging(level=logging.INFO):
    """Setup logging with Rich handler for better console output."""
    
    # Get log level from environment if set
    env_level = os.getenv("LOG_LEVEL", "INFO").upper()
    if env_level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
        level = getattr(logging, env_level)
    
    # Setup rich logging
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    
    # Set specific loggers
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging setup complete at {logging.getLevelName(level)} level")