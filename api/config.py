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
    },
    "grok": {
        "name": "Grok",
        "env_var": "GROK_API_KEY",
        "env_key": "GROK_API_KEY",  # For backward compatibility
        "base_url": "https://api.x.ai/v1",
        "model": "grok-beta",
        "default_model": "grok-beta",
    },
    "winston": {
        "name": "Winston AI Detection",
        "env_var": "WINSTON_API_KEY",
        "env_key": "WINSTON_API_KEY",  # For backward compatibility
        "base_url": "https://api.gowinston.ai/v1",
        "model": "winston-ai-detector",
        "default_model": "winston-ai-detector",
    },
    "gemini": {
        "name": "Gemini",
        "env_var": "GEMINI_API_KEY",
        "env_key": "GEMINI_API_KEY",  # For backward compatibility
        "base_url": "https://generativelanguage.googleapis.com",
        "model": "gemini-1.5-pro",
        "default_model": "gemini-1.5-pro",
    },
}


@dataclass
class APIConfig:
    """Configuration for API client"""

    api_key: str
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    max_tokens: int = 2000  # FURTHER REDUCED for faster responses
    temperature: float = (
        0.9  # INCREASED for faster, more creative responses
    )
    timeout_connect: int = 10  # REDUCED for faster failure
    timeout_read: int = 45  # REDUCED for faster timeout
    max_retries: int = 1  # REDUCED to 1 retry for faster failure
    retry_delay: float = 0.3  # REDUCED for faster retries


class ConfigManager:
    """Manages API configuration with environment variable support"""

    @staticmethod
    def load_config() -> APIConfig:
        """Load configuration from environment variables"""

        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY environment variable not set. "
                "Please set your DeepSeek API key in your environment."
            )

        return APIConfig(
            api_key=api_key,
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            max_tokens=int(
                os.getenv("DEEPSEEK_MAX_TOKENS", "2000")
            ),  # OPTIMIZED: Further reduced from 3000
            temperature=float(
                os.getenv("DEEPSEEK_TEMPERATURE", "0.9")
            ),  # OPTIMIZED: Increased from 0.8
            timeout_connect=int(os.getenv("DEEPSEEK_TIMEOUT_CONNECT", "10")),
            timeout_read=int(
                os.getenv("DEEPSEEK_TIMEOUT_READ", "45")
            ),  # OPTIMIZED: Reduced from 60
            max_retries=int(
                os.getenv("DEEPSEEK_MAX_RETRIES", "1")
            ),  # OPTIMIZED: Reduced from 2
            retry_delay=float(
                os.getenv("DEEPSEEK_RETRY_DELAY", "0.3")
            ),  # OPTIMIZED: Reduced from 0.5
        )

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


# Default configuration instance
def get_default_config() -> APIConfig:
    """Get default API configuration"""
    return ConfigManager.load_config()
