"""
Utility for loading environment variables from .env files.
"""

import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def load_env_variables(env_file: str = '.env') -> Dict[str, str]:
    """Load environment variables from .env file.
    
    Args:
        env_file: Path to .env file
        
    Returns:
        Dictionary of loaded environment variables
    """
    loaded_vars = {}
    
    try:
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                        
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                        
                    # Set environment variable
                    os.environ[key] = value
                    loaded_vars[key] = value
                    
            logger.info(f"Loaded {len(loaded_vars)} variables from {env_file}")
        else:
            logger.warning(f".env file not found: {env_file}")
    except Exception as e:
        logger.error(f"Error loading .env file: {e}")
    
    return loaded_vars