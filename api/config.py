#!/usr/bin/env python3
"""
API Configuration for Z-Beam Generator

FAIL-FAST DESIGN: All configurations must be defined in run.py
No fallbacks, no hardcoded values, no environment variable overrides.
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

    # Default to DeepSeek if available
    if "deepseek" in providers:
        config_data = providers["deepseek"]
        
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

    # Fail fast if deepseek not configured
    available = list(providers.keys())
    raise RuntimeError(
        f"CONFIGURATION ERROR: 'deepseek' provider not found in run.py. "
        f"Available providers: {available}. Configure 'deepseek' in API_PROVIDERS."
    )
