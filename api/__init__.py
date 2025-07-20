"""
API module for accessing AI providers.
"""

import os
import logging

logger = logging.getLogger(__name__)

def get_client(provider: str):
    """Get API client for the specified provider."""
    try:
        from .client import APIClient
        
        # Get API key from environment
        env_key = f"{provider.upper()}_API_KEY"
        api_key = os.environ.get(env_key)
        
        # Create client
        return APIClient(provider, api_key)
        
    except Exception as e:
        logger.error(f"Error creating API client: {e}")
        # Return a client that provides error messages
        from .client import APIClient
        return APIClient("error")