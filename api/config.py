# filepath: /Users/todddunning/Desktop/Z-Beam/z-beam-generator/api/config.py
"""
Configuration for API clients.
"""

import os
import logging
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Default provider configurations
PROVIDER_CONFIGS = {
    "deepseek": {
        "endpoint": "https://api.deepseek.com/v1/chat/completions",
        "model": "deepseek-chat",
        "max_tokens_limit": 4000,
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0,
        "presence_penalty": 0
    },
    "openai": {
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "model": "gpt-4",
        "max_tokens_limit": 8000,
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
}

def get_provider_config(provider: str) -> Dict[str, Any]:
    """Get configuration for the specified provider."""
    provider_name = provider.lower()
    if provider_name in PROVIDER_CONFIGS:
        return PROVIDER_CONFIGS[provider_name]
    return PROVIDER_CONFIGS.get("deepseek", {})

# Add this alias to handle the naming mismatch
load_provider_config = get_provider_config  # Alias for backward compatibility