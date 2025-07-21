"""
Standardized logging configuration.
"""

import os
import logging
import sys
from datetime import datetime

def configure_logging(log_level=logging.INFO):
    """Configure standardized logging for the entire application."""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/z-beam_{timestamp}.log"
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set standard log levels for various modules
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    # Log startup information
    logging.info("Z-Beam Generator started")
    logging.info(f"Log file: {log_file}")