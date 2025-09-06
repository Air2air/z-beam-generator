"""
Standardized environment variable loader for API clients.
Handles .env file loading and configuration file loading for consistent API key access.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional


class EnvLoader:
    """Standardized environment variable loader"""

    _loaded = False

    @classmethod
    def load_env(cls) -> None:
        """Load environment variables from config file and .env file if available"""
        if cls._loaded:
            return

        # First, try to load from config/api_keys.py
        try:
            project_root = Path(__file__).parent.parent
            config_dir = project_root / "config"

            # Add config directory to Python path
            if str(config_dir) not in sys.path:
                sys.path.insert(0, str(config_dir))

            # Import the config file
            from config.api_keys import API_KEYS

            # Set environment variables from config
            for key, value in API_KEYS.items():
                if value and not os.getenv(key):  # Don't override existing env vars
                    os.environ[key] = str(value)

            print("🔑 Loaded API keys from config/api_keys.py")

        except ImportError:
            raise Exception(
                "config/api_keys.py not found - no fallback to .env permitted in fail-fast architecture"
            )

        cls._loaded = True

    @classmethod
    def get_api_key(cls, provider: str, env_key: str) -> Optional[str]:
        """Get API key for a provider from environment"""
        cls.load_env()

        api_key = os.getenv(env_key)
        if api_key:
            print(f"🔑 Found API key for {provider}")
        else:
            print(f"⚠️  No API key found for {provider} (looking for {env_key})")

        return api_key

    @classmethod
    def get_provider_config(cls, provider_config: Dict) -> Dict:
        """Get complete configuration for a provider"""
        cls.load_env()

        config = provider_config.copy()
        api_key = cls.get_api_key(config["name"], config["env_key"])

        if api_key:
            config["api_key"] = api_key

        return config

    @classmethod
    def list_available_keys(cls) -> Dict[str, bool]:
        """List which API keys are available in environment"""
        cls.load_env()

        keys_to_check = [
            "DEEPSEEK_API_KEY",
            "GROK_API_KEY",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
        ]

        available = {}
        for key in keys_to_check:
            available[key] = bool(os.getenv(key))

        return available
