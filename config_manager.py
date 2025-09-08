#!/usr/bin/env python3
"""
Configuration Manager for Z-Beam Generator
Handles loading test vs production configurations
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class ConfigManager:
    """Manages configuration loading for test and production environments"""

    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            # Look in config/ subdirectory relative to the project root
            self.config_dir = Path(__file__).parent / "config"
        else:
            self.config_dir = Path(config_dir)
        self._config_cache: Optional[Dict[str, Any]] = None

    def load_config(self, test_mode: Optional[bool] = None) -> Dict[str, Any]:
        """
        Load configuration based on test mode

        Args:
            test_mode: Override test mode detection. If None, uses environment variable

        Returns:
            Configuration dictionary
        """
        if test_mode is None:
            test_mode = self._detect_test_mode()

        config_file = "test_config.yaml" if test_mode else "prod_config.yaml"
        config_path = self.config_dir / config_file

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # Cache the loaded config
        self._config_cache = config
        return config

    def _detect_test_mode(self) -> bool:
        """Detect if we're in test mode from environment variables"""
        # Check multiple indicators for test mode
        test_indicators = [
            os.getenv("TEST_MODE", "").lower() in ("true", "1", "yes"),
            os.getenv("PYTEST_CURRENT_TEST", "") != "",
            os.getenv("CI", "").lower() in ("true", "1", "yes"),
            "pytest" in os.getenv("_", "").lower(),
        ]
        return any(test_indicators)

    def get_config_value(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation

        Args:
            key_path: Path to config value (e.g., 'AI_DETECTION.TARGET_SCORE')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        if self._config_cache is None:
            self.load_config()

        keys = key_path.split(".")
        value = self._config_cache

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def is_test_mode(self) -> bool:
        """Check if currently in test mode"""
        return self.get_config_value("TEST_MODE", False)

    def get_timeout(self, operation: str) -> int:
        """Get timeout for a specific operation"""
        timeout_key = f"TIMEOUTS.{operation.upper()}"
        return self.get_config_value(timeout_key, 30)  # Default 30 seconds


# Global configuration manager instance
config_manager = ConfigManager()


def get_config(test_mode: Optional[bool] = None) -> Dict[str, Any]:
    """Convenience function to get configuration"""
    return config_manager.load_config(test_mode)


def is_test_mode() -> bool:
    """Convenience function to check test mode"""
    return config_manager.is_test_mode()


def get_timeout(operation: str) -> int:
    """Convenience function to get operation timeout"""
    return config_manager.get_timeout(operation)


if __name__ == "__main__":
    # Example usage
    config = get_config()
    print(f"Test Mode: {is_test_mode()}")
    print(
        f"AI Detection Target Score: {config_manager.get_config_value('AI_DETECTION.TARGET_SCORE')}"
    )
    print(f"API Timeout: {get_timeout('API_CALL')}")
