"""
Verify environment variables and API connectivity.
"""

import os
import sys
import logging
import dotenv
from typing import Dict, List, Tuple

# Add this import
from api.connectivity import check_api_connectivity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("z-beam")

def load_env() -> bool:
    """
    Load environment variables from .env file.
    
    Returns:
        True if successful, False otherwise
    """
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        dotenv.load_dotenv(env_path)
        logger.info(f"Loaded environment variables from {env_path}")
        return True
    else:
        logger.warning(f"No .env file found at {env_path}")
        return False

def verify_required_env_vars() -> Tuple[bool, List[str]]:
    """
    Verify that required environment variables are set.
    
    Returns:
        Tuple of (success, missing_variables)
    """
    required_vars = [
        "DEEPSEEK_API_KEY",
        # Add other required variables here
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    return len(missing_vars) == 0, missing_vars

def verify_api_connectivity() -> Dict[str, bool]:
    """
    Verify connectivity to required APIs.
    
    Returns:
        Dictionary of provider connectivity results
    """
    providers = ["deepseek"]
    results = {}
    
    for provider in providers:
        success, error = check_api_connectivity(provider)
        results[provider] = success
        if not success:
            logger.warning(f"Cannot connect to {provider} API: {error}")
        else:
            logger.info(f"Successfully connected to {provider} API")
    
    return results

def main():
    """
    Verify environment setup and API connectivity.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Load environment variables
    load_env()
    
    # Verify required environment variables
    env_ok, missing_vars = verify_required_env_vars()
    if not env_ok:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return 1
    
    # Verify API connectivity
    connectivity_results = verify_api_connectivity()
    if not all(connectivity_results.values()):
        logger.error("Cannot connect to all required APIs")
        return 1
    
    logger.info("Environment verification successful")
    return 0

if __name__ == "__main__":
    sys.exit(main())