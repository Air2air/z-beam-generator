#!/usr/bin/env python3
"""
API Configuration for Z-Beam Generator

Standardized configuration management for DeepSeek API integration.
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


# API Providers Configuration
# Moved here to break circular import between run.py and utils/environment_checker.py
API_PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek",
        "env_var": "DEEPSEEK_API_KEY",
        "env_key": "DEEPSEEK_API_KEY",  # For backward compatibility
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "default_model": "deepseek-chat",
        # Required operational parameters for fail-fast architecture
        "max_tokens": 2000,  # RESTORED: Correct value from working commit
        "temperature": 0.9,  # RESTORED: Correct value from working commit
        "timeout_connect": 10,  # RESTORED: Correct value from working commit
        "timeout_read": 45,  # RESTORED: Correct value from working commit
        "max_retries": 3,  # INCREASED: Better for network issues
        "retry_delay": 1.0,  # INCREASED: Give network time to recover
    },
    "grok": {
        "name": "Grok",
        "env_var": "GROK_API_KEY",
        "env_key": "GROK_API_KEY",  # For backward compatibility
        "base_url": "https://api.x.ai/v1",
        "model": "grok-beta",
        "default_model": "grok-beta",
        # Required operational parameters for fail-fast architecture
        "max_tokens": 2000,  # RESTORED: Consistent with working values
        "temperature": 0.9,  # RESTORED: Consistent with working values
        "timeout_connect": 10,  # RESTORED: Consistent with working values
        "timeout_read": 45,  # RESTORED: Consistent with working values
        "max_retries": 3,  # INCREASED: Better for network issues
        "retry_delay": 1.0,  # INCREASED: Give network time to recover
    },
    "winston": {
        "name": "Winston AI Detection",
        "env_var": "WINSTON_API_KEY",
        "env_key": "WINSTON_API_KEY",  # For backward compatibility
        "base_url": "https://api.gowinston.ai/v1",
        "model": "winston-ai-detector",
        "default_model": "winston-ai-detector",
        # Required operational parameters for fail-fast architecture
        "max_tokens": 1000,  # RESTORED: Appropriate for detection API
        "temperature": 0.1,  # RESTORED: Low temperature for consistent detection
        "timeout_connect": 10,  # RESTORED: Consistent with working values
        "timeout_read": 45,  # RESTORED: Consistent with working values
        "max_retries": 3,  # INCREASED: Better for network issues
        "retry_delay": 1.0,  # INCREASED: Give network time to recover
    },
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
    return API_PROVIDERS["deepseek"]

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
