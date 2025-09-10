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
        """Load configuration from environment variables"""

        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY environment variable not set. "
                "Please set your DeepSeek API key in your environment."
            )

        base_url = os.getenv("DEEPSEEK_BASE_URL")
        if not base_url:
            raise ValueError(
                "DEEPSEEK_BASE_URL environment variable not set. "
                "Please set your DeepSeek base URL in your environment."
            )

        model = os.getenv("DEEPSEEK_MODEL")
        if not model:
            raise ValueError(
                "DEEPSEEK_MODEL environment variable not set. "
                "Please set your DeepSeek model in your environment."
            )

        max_tokens_str = os.getenv("DEEPSEEK_MAX_TOKENS")
        if not max_tokens_str:
            raise ValueError(
                "DEEPSEEK_MAX_TOKENS environment variable not set. "
                "Please set your DeepSeek max tokens in your environment."
            )
        max_tokens = int(max_tokens_str)

        temperature_str = os.getenv("DEEPSEEK_TEMPERATURE")
        if not temperature_str:
            raise ValueError(
                "DEEPSEEK_TEMPERATURE environment variable not set. "
                "Please set your DeepSeek temperature in your environment."
            )
        temperature = float(temperature_str)

        timeout_connect_str = os.getenv("DEEPSEEK_TIMEOUT_CONNECT")
        if not timeout_connect_str:
            raise ValueError(
                "DEEPSEEK_TIMEOUT_CONNECT environment variable not set. "
                "Please set your DeepSeek timeout connect in your environment."
            )
        timeout_connect = int(timeout_connect_str)

        timeout_read_str = os.getenv("DEEPSEEK_TIMEOUT_READ")
        if not timeout_read_str:
            raise ValueError(
                "DEEPSEEK_TIMEOUT_READ environment variable not set. "
                "Please set your DeepSeek timeout read in your environment."
            )
        timeout_read = int(timeout_read_str)

        max_retries_str = os.getenv("DEEPSEEK_MAX_RETRIES")
        if not max_retries_str:
            raise ValueError(
                "DEEPSEEK_MAX_RETRIES environment variable not set. "
                "Please set your DeepSeek max retries in your environment."
            )
        max_retries = int(max_retries_str)

        retry_delay_str = os.getenv("DEEPSEEK_RETRY_DELAY")
        if not retry_delay_str:
            raise ValueError(
                "DEEPSEEK_RETRY_DELAY environment variable not set. "
                "Please set your DeepSeek retry delay in your environment."
            )
        retry_delay = float(retry_delay_str)

        return APIConfig(
            api_key=api_key,
            base_url=base_url,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout_connect=timeout_connect,
            timeout_read=timeout_read,
            max_retries=max_retries,
            retry_delay=retry_delay,
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
