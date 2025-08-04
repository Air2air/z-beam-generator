"""
API module for accessing AI providers.
"""

from typing import Optional, Dict, Any
from api.client import ApiClient

def get_client(provider: str = "deepseek", **kwargs) -> ApiClient:
    """Get an API client instance.
    
    Args:
        provider: AI provider to use
        **kwargs: Additional options for the client
        
    Returns:
        API client instance
    """
    options = kwargs.get("options", {})
    article_context = kwargs.get("article_context", {})
    return ApiClient(provider=provider, options=options, article_context=article_context)