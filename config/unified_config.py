#!/usr/bin/env python3
"""
Unified Configuration Manager

Centralized configuration management for the entire Z-Beam system.
Consolidates API, component, and environment configurations.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

# Import existing configurations
def get_api_providers():
    """Get API provider configurations from centralized location"""
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
            }
        }


class UnifiedConfigManager:
    """
    Unified configuration manager for the entire Z-Beam system.

    Provides centralized access to all configuration with validation
    and environment-aware defaults.
    """

    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self._config = self._load_configuration()

    def _load_configuration(self) -> Dict[str, Any]:
        """Load and merge all configuration sources"""
        config = {
            "api": self._load_api_config(),
            "components": self._load_component_config(),
            "environment": self._load_environment_config(),
            "testing": self._load_testing_config(),
        }

        # Validate configuration
        self._validate_configuration(config)

        return config

    def _load_api_config(self) -> Dict[str, Any]:
        """Load API provider configuration"""
        api_providers = get_api_providers()
        api_config = {
            "providers": api_providers,
            "default_provider": "deepseek",
            "timeout_connect": int(os.getenv("API_TIMEOUT_CONNECT", "10")),
            "timeout_read": int(os.getenv("API_TIMEOUT_READ", "45")),
            "max_retries": int(os.getenv("API_MAX_RETRIES", "3")),
            "retry_delay": float(os.getenv("API_RETRY_DELAY", "1.0")),
        }

        # Validate API keys
        for provider_id, config in api_providers.items():
            api_key = os.getenv(config["env_var"])
            api_config["providers"][provider_id]["configured"] = bool(api_key)

        return api_config

    def _load_component_config(self) -> Dict[str, Any]:
        """Load component configuration"""
        try:
            from run import COMPONENT_CONFIG
            return {
                "components": COMPONENT_CONFIG,
                "default_priority": 5,
                "max_components_per_batch": 10,
            }
        except ImportError:
            return {
                "components": {},
                "default_priority": 5,
                "max_components_per_batch": 10,
            }

    def _load_environment_config(self) -> Dict[str, Any]:
        """Load environment-specific configuration"""
        return {
            "is_test_mode": self.is_test_mode(),
            "is_production": not self.is_test_mode(),
            "project_root": str(Path(__file__).parent.parent),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "debug_mode": os.getenv("DEBUG", "false").lower() == "true",
        }

    def _load_testing_config(self) -> Dict[str, Any]:
        """Load testing-specific configuration"""
        return {
            "use_mocks": os.getenv("TEST_USE_MOCKS", "true").lower() == "true",
            "mock_delay": float(os.getenv("TEST_MOCK_DELAY", "0.01")),
            "disable_network": os.getenv("TEST_DISABLE_NETWORK", "true").lower() == "true",
            "timeout_seconds": int(os.getenv("TEST_TIMEOUT", "30")),
            "parallel_tests": os.getenv("TEST_PARALLEL", "false").lower() == "true",
        }

    def _validate_configuration(self, config: Dict[str, Any]) -> None:
        """Validate the loaded configuration"""
        # Validate API configuration
        if not config["api"]["providers"]:
            raise ValueError("No API providers configured")

        # Ensure at least one provider is configured
        configured_providers = [
            pid for pid, pconfig in config["api"]["providers"].items()
            if pconfig.get("configured", False)
        ]

        if not configured_providers and not config["environment"]["is_test_mode"]:
            raise ValueError("No API providers configured and not in test mode")

    def is_test_mode(self) -> bool:
        """Determine if we're in test mode"""
        return os.getenv('TEST_MODE', 'false').lower() == 'true' or \
               os.getenv('PYTEST_CURRENT_TEST') is not None

    def get_api_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """Get API configuration for a specific provider or all providers"""
        if provider:
            if provider not in self._config["api"]["providers"]:
                raise ValueError(f"Unknown API provider: {provider}")
            return self._config["api"]["providers"][provider]
        return self._config["api"]

    def get_component_config(self, component: Optional[str] = None) -> Dict[str, Any]:
        """Get component configuration"""
        if component:
            components = self._config["components"]["components"]
            if component not in components:
                raise ValueError(f"Unknown component: {component}")
            return components[component]
        return self._config["components"]

    def get_environment_config(self) -> Dict[str, Any]:
        """Get environment configuration"""
        return self._config["environment"]

    def get_testing_config(self) -> Dict[str, Any]:
        """Get testing configuration"""
        return self._config["testing"]

    def get_provider_for_component(self, component_type: str) -> str:
        """Get the API provider for a component type"""
        try:
            component_config = self.get_component_config(component_type)
            return component_config.get("api_provider", "deepseek")
        except (ValueError, KeyError):
            return "deepseek"

    def validate_api_keys(self) -> Dict[str, bool]:
        """Validate that all required API keys are present"""
        results = {}
        for provider_id, config in self._config["api"]["providers"].items():
            api_key = os.getenv(config["env_var"])
            results[provider_id] = bool(api_key)
        return results

    def get_all_config(self) -> Dict[str, Any]:
        """Get the complete configuration"""
        return self._config.copy()

    def reload_config(self) -> None:
        """Reload configuration from sources"""
        self._config = self._load_configuration()


# Global instance
config_manager = UnifiedConfigManager()


# Convenience functions
def get_api_provider_config(provider: str) -> Dict[str, Any]:
    """Get configuration for a specific API provider"""
    return config_manager.get_api_config(provider)


def get_component_provider(component_type: str) -> str:
    """Get the API provider for a component type"""
    return config_manager.get_provider_for_component(component_type)


def is_test_environment() -> bool:
    """Check if we're in a test environment"""
    return config_manager.is_test_mode()


def validate_system_config() -> Dict[str, Any]:
    """Validate the entire system configuration"""
    return {
        "api_keys_valid": config_manager.validate_api_keys(),
        "environment": config_manager.get_environment_config(),
        "testing": config_manager.get_testing_config(),
    }
