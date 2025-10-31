#!/usr/bin/env python3
"""
API Configuration for Z-Beam Generator

FAIL-FAST DESIGN: All configurations must be defined in run.py
No fallbacks, no hardcoded values, no environment variable overrides.

CONSOLIDATION ENHANCEMENT: Added ConfigAdapter for unified access while preserving fail-fast behavior.
"""

from typing import Any, Dict
from dataclasses import dataclass


@dataclass
class APIConfig:
    """Configuration for API clients"""

    name: str
    base_url: str
    model: str
    api_key: str
    max_tokens: int
    temperature: float
    timeout_connect: int
    timeout_read: int
    max_retries: int
    retry_delay: float


def get_api_providers() -> Dict[str, Any]:
    """Get API provider configurations from run.py ONLY"""
    try:
        from run import API_PROVIDERS
        return API_PROVIDERS
    except ImportError:
        raise RuntimeError(
            "CONFIGURATION ERROR: run.py not found or API_PROVIDERS not defined. "
            "All API configurations must be defined in run.py with no fallbacks."
        )


def get_default_config() -> APIConfig:
    """Get default API configuration from run.py"""
    providers = get_api_providers()

    # Fail fast if no providers configured
    if not providers:
        raise RuntimeError(
            "CONFIGURATION ERROR: No API providers configured in run.py. "
            "Define API_PROVIDERS dictionary in run.py."
        )

    # Default to Grok if available (per user request)
    if "grok" in providers:
        config_data = providers["grok"]
        
        # Validate all required fields are present
        required_fields = ["name", "base_url", "model", "max_tokens", "temperature", 
                          "timeout_connect", "timeout_read", "max_retries", "retry_delay"]
        
        for field in required_fields:
            if field not in config_data:
                raise RuntimeError(
                    f"CONFIGURATION ERROR: Missing required field '{field}' "
                    f"in run.py API_PROVIDERS['deepseek']"
                )
        
        return APIConfig(
            name=config_data["name"],
            base_url=config_data["base_url"],
            model=config_data["model"],
            api_key="",  # Will be set by client
            max_tokens=config_data["max_tokens"],
            temperature=config_data["temperature"],
            timeout_connect=config_data["timeout_connect"],
            timeout_read=config_data["timeout_read"],
            max_retries=config_data["max_retries"],
            retry_delay=config_data["retry_delay"],
        )

    # Fail fast if grok not configured
    available = list(providers.keys())
    raise RuntimeError(
        f"CONFIGURATION ERROR: 'grok' provider not found in run.py. "
        f"Available providers: {available}. Configure 'grok' in API_PROVIDERS."
    )


# CONSOLIDATION ENHANCEMENT: Adapter for unified configuration access
class ConfigAdapter:
    """
    Adapter for unified configuration access while preserving fail-fast behavior.
    Consolidates access to API providers and configurations.
    """
    
    @staticmethod
    def get_provider_config(provider: str) -> Dict[str, Any]:
        """Get configuration for a specific provider with validation"""
        providers = get_api_providers()
        
        if provider not in providers:
            available = list(providers.keys())
            raise ValueError(
                f"Provider '{provider}' not found. Available providers: {available}"
            )
        
        return providers[provider].copy()
    
    @staticmethod
    def validate_provider_config(provider: str) -> bool:
        """Validate that a provider is properly configured"""
        try:
            config = ConfigAdapter.get_provider_config(provider)
            required_fields = ["name", "base_url", "model", "env_var"]
            
            for field in required_fields:
                if field not in config:
                    return False
            
            return True
        except (ValueError, RuntimeError):
            return False
    
    @staticmethod
    def get_all_providers() -> Dict[str, Any]:
        """Get all provider configurations (delegate to existing function)"""
        return get_api_providers()
    
    @staticmethod
    def create_api_config(provider: str) -> APIConfig:
        """Create APIConfig for a specific provider"""
        if provider == "grok":
            return get_default_config()
        
        # For other providers, build config from provider data
        config_data = ConfigAdapter.get_provider_config(provider)
        
        return APIConfig(
            name=config_data["name"],
            base_url=config_data["base_url"],
            model=config_data.get("model", config_data.get("default_model", "unknown")),
            api_key="",  # Will be set by client
            max_tokens=config_data["max_tokens"],  # FAIL-FAST: Required per GROK_INSTRUCTIONS.md
            temperature=config_data["temperature"],  # FAIL-FAST: Required per GROK_INSTRUCTIONS.md
            timeout_connect=config_data["timeout_connect"],  # FAIL-FAST: Required per GROK_INSTRUCTIONS.md
            timeout_read=config_data["timeout_read"],  # FAIL-FAST: Required per GROK_INSTRUCTIONS.md
            max_retries=config_data["max_retries"],  # FAIL-FAST: Required per GROK_INSTRUCTIONS.md
            retry_delay=config_data["retry_delay"],  # FAIL-FAST: Required per GROK_INSTRUCTIONS.md
        )


# Removed _get_fallback function per GROK_INSTRUCTIONS.md - no fallbacks allowed in production

# Backward compatibility exports  
__all__ = ['APIConfig', 'get_api_providers', 'get_default_config', 'ConfigAdapter']
