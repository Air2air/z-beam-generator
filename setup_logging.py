#!/usr/bin/env python3
"""
Logging setup for Z-Beam Generator
"""
import logging
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Setup logging to both terminal and file"""
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"zbeam_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Terminal output
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"📝 Logging initialized - File: {log_file}")
    return logger