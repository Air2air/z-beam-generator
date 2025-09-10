#!/usr/bin/env python3
"""
API Configuration for Z-Beam Generator

Standardized configuration management for API integration.
Configuration is centralized in run.py to avoid circular imports.
"""

import os
from dataclasses import dataclass
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    # Load .env from the project root
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    # If python-dotenv is not available, continue without it
    pass


def get_api_providers():
    """
    Get API provider configurations from centralized location.
    
    Returns:
        dict: API provider configurations from run.py
    """
    try:
        from run import API_PROVIDERS
        return API_PROVIDERS
    except ImportError:
        # Fallback minimal configuration if run.py not available
        return {
            "deepseek": {
                "name": "DeepSeek",
                "env_var": "DEEPSEEK_API_KEY",
                "base_url": "https://api.deepseek.com",
                "model": "deepseek-chat",
                "max_tokens": 800,
                "temperature": 0.7,
                "timeout_connect": 10,
                "timeout_read": 45,
                "max_retries": 3,
                "retry_delay": 1.0,
            }
        }


@dataclass
class APIConfig:
    """Configuration for API client"""

    api_key: str
    base_url: str
    model: str
    max_tokens: int
    temperature: float
    timeout_connect: int
    timeout_read: int
    max_retries: int
    retry_delay: float


class ConfigManager:
    """Manages API configuration with environment variable support"""

    @staticmethod
    def load_config() -> APIConfig:
        """Load configuration from environment variables using standardized key manager"""

        # Use standardized API key loading
        from api.key_manager import get_api_key

        api_key = get_api_key("deepseek")

        # For other config values, use standardized environment variable names
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        max_tokens = int(os.getenv("DEEPSEEK_MAX_TOKENS", "2000"))
        temperature = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.9"))
        timeout_connect = int(os.getenv("DEEPSEEK_TIMEOUT_CONNECT", "10"))
        timeout_read = int(os.getenv("DEEPSEEK_TIMEOUT_READ", "45"))
        max_retries = int(os.getenv("DEEPSEEK_MAX_RETRIES", "3"))
        retry_delay = float(os.getenv("DEEPSEEK_RETRY_DELAY", "1.0"))

def get_default_config():
    """Get default configuration for DeepSeek API client"""
    api_providers = get_api_providers()
    return api_providers["deepseek"]

    @staticmethod
    def validate_config(config: APIConfig) -> bool:
        """Validate API configuration"""

        if not config.api_key:
            return False

        if not config.base_url:
            return False

        if config.max_tokens <= 0:
            return False

        if not (0.0 <= config.temperature <= 2.0):
            return False

        if config.timeout_connect <= 0 or config.timeout_read <= 0:
            return False

        return True
