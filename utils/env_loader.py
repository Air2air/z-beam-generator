"""Environment variable loader."""

import os
import logging
import dotenv

logger = logging.getLogger("z-beam")

def load_env_variables():
    """Load environment variables from .env file."""
    # Get the path to the .env file
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    
    # Check if the file exists
    if not os.path.exists(env_path):
        logger.warning("No .env file found")
        return False
    
    # Load the .env file
    result = dotenv.load_dotenv(env_path)
    
    if result:
        logger.info(f"Loaded environment variables from {env_path}")
    else:
        logger.warning(f"Failed to load environment variables from {env_path}")
    
    return result