"""
DEPRECATED: Environment variable loader for API clients.

WARNING: This module is deprecated. Use api.key_manager instead for all new code.
This module is kept for backward compatibility only.

Provides legacy environment variable loading functionality.
New code should use the standardized APIKeyManager from api.key_manager.
"""

import os
import sys
import warnings
from pathlib import Path
from typing import Dict, Optional


class EnvLoader:
    """DEPRECATED: Legacy environment variable loader - use APIKeyManager instead"""

    _loaded = False

    @classmethod
    def load_env(cls) -> None:
        """DEPRECATED: Load environment variables - use APIKeyManager instead"""
        warnings.warn(
            "EnvLoader is deprecated. Use api.key_manager.APIKeyManager instead.",
            DeprecationWarning,
            stacklevel=2
        )

        if cls._loaded:
            return

        # Try to load from config/api_keys.py
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
        """DEPRECATED: Get API key - use api.key_manager.get_api_key instead"""
        warnings.warn(
            "EnvLoader.get_api_key is deprecated. Use api.key_manager.get_api_key instead.",
            DeprecationWarning,
            stacklevel=2
        )

        cls.load_env()

        api_key = os.getenv(env_key)
        if api_key:
            print(f"🔑 Found API key for {provider}")
        else:
            print(f"⚠️  No API key found for {provider} (looking for {env_key})")

        return api_key

    @classmethod
    def get_provider_config(cls, provider_config: Dict) -> Dict:
        """DEPRECATED: Get provider config - use APIKeyManager instead"""
        warnings.warn(
            "EnvLoader.get_provider_config is deprecated. Use APIKeyManager instead.",
            DeprecationWarning,
            stacklevel=2
        )

        cls.load_env()

        config = provider_config.copy()
        api_key = cls.get_api_key(config["name"], config["env_key"])

        if api_key:
            config["api_key"] = api_key

        return config

    @classmethod
    def list_available_keys(cls) -> Dict[str, bool]:
        """DEPRECATED: List available keys - use APIKeyManager.validate_api_keys instead"""
        warnings.warn(
            "EnvLoader.list_available_keys is deprecated. Use APIKeyManager.validate_api_keys instead.",
            DeprecationWarning,
            stacklevel=2
        )

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
