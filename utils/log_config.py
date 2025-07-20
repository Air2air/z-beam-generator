"""
Standardized logging configuration.
"""

import os
import logging
from typing import Optional

from utils.path_manager import PathManager

def configure_logging(log_name: str = "z-beam-generator", level: int = logging.INFO) -> logging.Logger:
    """Configure logging with standard format and handlers.
    
    Args:
        log_name: Name for the log file
        level: Logging level
        
    Returns:
        Configured logger
    """
    # Ensure logs directory exists
    os.makedirs(PathManager.LOGS_DIR, exist_ok=True)
    
    # Get log file path
    log_file = PathManager.get_log_path(log_name)
    
    # Configure logging
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Add file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger