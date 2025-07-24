"""
API client factory for components.

This module provides utilities for initializing and managing API clients
for different providers.
"""

import logging
from typing import Optional, Dict, Any

from api.client import ApiClient

logger = logging.getLogger(__name__)

class ApiClientFactory:
    """Factory for creating and initializing API clients."""
    
    @staticmethod
    def create_client(provider: str, options: Dict[str, Any] = None) -> Optional[ApiClient]:
        """Create an API client for the specified provider.
        
        Args:
            provider: Provider name (deepseek, openai, etc.)
            options: Provider-specific options
            
        Returns:
            Initialized API client or None if initialization failed
        """
        try:
            return ApiClient(provider, options or {})
        except Exception as e:
            logger.error(f"Failed to initialize {provider} API client: {str(e)}")
            return None
    
    @staticmethod
    def create_client_from_context(context: Dict[str, Any], 
                                component_config: Dict[str, Any] = None) -> Optional[ApiClient]:
        """Create an API client from context and component configuration.
        
        This method intelligently determines which provider to use based on the
        following precedence:
        1. Component-specific provider from component_config
        2. Global provider from context
        3. Default provider (deepseek)
        
        Args:
            context: Application context
            component_config: Component-specific configuration
            
        Returns:
            Initialized API client or None if initialization failed
        """
        try:
            # Determine provider with precedence
            provider = None
            options = {}
            
            # 1. Try component-specific provider first
            if component_config and "provider" in component_config:
                provider = component_config.get("provider")
                options = component_config.get("options", {})
            
            # 2. Fall back to global provider
            if not provider and context:
                provider = context.get("ai_provider")
                options = context.get("options", {})
            
            # 3. Use default if still not found
            provider = provider or "deepseek"
            
            # Create client
            return ApiClientFactory.create_client(provider, options)
            
        except Exception as e:
            logger.error(f"Error creating API client from context: {str(e)}")
            return None