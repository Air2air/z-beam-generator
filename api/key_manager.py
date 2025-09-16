#!/usr/bin/env python3
"""
Standardized API Key Management for Z-Beam Generator

Provides a consistent, fail-fast approach to API key loading across all providers.
Eliminates hardcoded environment variable names and ensures uniform behavior.
"""

import os
from typing import Dict, Optional, Any


def get_api_providers():
    """Get API provider configurations from centralized location"""
    try:
        from run import API_PROVIDERS
        return API_PROVIDERS
    except ImportError:
        raise RuntimeError(
            "CONFIGURATION ERROR: run.py not found or API_PROVIDERS not defined. "
            "All API configurations must be defined in run.py with no fallbacks."
        )


class APIKeyManager:
    """Centralized API key management with standardized loading"""
    
    @staticmethod
    def get_api_key(provider: str, config: Optional[Dict[str, Any]] = None) -> str:
        """
        Get API key for a provider using standardized approach.
        
        Args:
            provider: Provider name (e.g., 'deepseek', 'grok', 'winston')
            config: Optional provider config override
            
        Returns:
            API key string
            
        Raises:
            ValueError: If API key is not found or provider is not configured
        """
        # Get provider configuration
        if config is None:
            API_PROVIDERS = get_api_providers()
            if provider not in API_PROVIDERS:
                raise ValueError(f"Unknown provider: {provider}")
            config = API_PROVIDERS[provider]
        
        # Get environment variable name from config
        env_var = config.get("env_var")
        if not env_var:
            raise ValueError(f"No env_var specified for provider: {provider}")
        
        # Load API key from environment
        api_key = os.getenv(env_var)
        if not api_key:
            provider_name = config.get("name", provider)
            raise ValueError(
                f"{provider_name} API key not found. "
                f"Please set the {env_var} environment variable."
            )
        
        return api_key
    
    @staticmethod
    def validate_api_keys() -> Dict[str, bool]:
        """
        Validate that all configured providers have API keys available.
        
        Returns:
            Dict mapping provider names to boolean availability status
        """
        results = {}
        API_PROVIDERS = get_api_providers()
        
        for provider, config in API_PROVIDERS.items():
            try:
                APIKeyManager.get_api_key(provider, config)
                results[provider] = True
            except ValueError:
                results[provider] = False
        
        return results
    
    @staticmethod
    def get_masked_key(provider: str, config: Optional[Dict[str, Any]] = None) -> str:
        """
        Get a masked version of the API key for logging/debugging.
        
        Args:
            provider: Provider name
            config: Optional provider config override
            
        Returns:
            Masked API key string (e.g., "sk-****1234")
        """
        try:
            api_key = APIKeyManager.get_api_key(provider, config)
            if len(api_key) <= 8:
                return "****"
            return f"{api_key[:4]}****{api_key[-4:]}"
        except ValueError:
            return "NOT_SET"
    
    @staticmethod
    def check_provider_availability(provider: str) -> bool:
        """
        Check if a specific provider is available (has API key configured).
        
        Args:
            provider: Provider name to check
            
        Returns:
            True if provider is available, False otherwise
        """
        try:
            APIKeyManager.get_api_key(provider)
            return True
        except ValueError:
            return False


# Convenience functions for backward compatibility and easy access
def get_api_key(provider: str, config: Optional[Dict[str, Any]] = None) -> str:
    """Get API key for a provider (convenience function)"""
    return APIKeyManager.get_api_key(provider, config)


def validate_all_api_keys() -> Dict[str, bool]:
    """Validate all API keys (convenience function)"""
    return APIKeyManager.validate_api_keys()


def get_masked_api_key(provider: str, config: Optional[Dict[str, Any]] = None) -> str:
    """Get masked API key for logging (convenience function)"""
    return APIKeyManager.get_masked_key(provider, config)


def is_provider_available(provider: str) -> bool:
    """Check if provider is available (convenience function)"""
    return APIKeyManager.check_provider_availability(provider)
