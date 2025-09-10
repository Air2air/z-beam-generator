#!/usr/bin/env python3
"""
Unified API Client Factory

Standardized factory for creating API clients with consistent behavior
across testing and production environments.
"""

import os
from typing import Any, Dict, Optional

from api.client import APIClient
from api.config import API_PROVIDERS


class APIClientFactory:
    """
    Unified factory for creating API clients with standardized behavior.

    This factory ensures consistent client creation across all environments
    and provides automatic mock injection during testing.
    """

    @staticmethod
    def is_test_mode() -> bool:
        """Determine if we're in test mode"""
        return os.getenv('TEST_MODE', 'false').lower() == 'true' or \
               os.getenv('PYTEST_CURRENT_TEST') is not None

    @staticmethod
    def create_client(
        provider: str = "deepseek",
        use_mock: Optional[bool] = None,
        **kwargs
    ) -> APIClient:
        """
        Create an API client with standardized behavior.

        Args:
            provider: API provider name (deepseek, grok, winston)
            use_mock: Force mock usage (auto-detected in test mode)
            **kwargs: Additional client configuration

        Returns:
            APIClient instance (real or mock based on environment)

        Raises:
            ValueError: If provider is not supported
        """
        print(f"🏭 [CLIENT FACTORY] Creating API client for provider: {provider}")

        # Auto-detect test mode
        is_test = APIClientFactory.is_test_mode()

        # Determine if we should use mocks
        should_use_mock = use_mock if use_mock is not None else is_test

        if should_use_mock:
            print("🎭 [CLIENT FACTORY] Using mock client (test mode)")
            return APIClientFactory._create_mock_client(provider, **kwargs)
        else:
            print("🔧 [CLIENT FACTORY] Using real API client")
            return APIClientFactory._create_real_client(provider, **kwargs)

    @staticmethod
    def _create_real_client(provider: str, **kwargs) -> APIClient:
        """Create a real API client"""
        if provider not in API_PROVIDERS:
            print(f"❌ [CLIENT FACTORY] Unsupported provider: {provider}")
            raise ValueError(f"Unsupported provider: {provider}")

        provider_config = API_PROVIDERS[provider]
        print(f"✅ [CLIENT FACTORY] Provider config loaded: {provider_config['name']}")

        # Get API key using standardized key manager
        from api.key_manager import get_api_key

        try:
            api_key = get_api_key(provider)
            print(f"🔑 [CLIENT FACTORY] API key found for {provider}")
        except ValueError as e:
            print(f"❌ [CLIENT FACTORY] {e}")
            raise RuntimeError(str(e))

        # Extract basic parameters for direct constructor arguments
        client_kwargs = {
            "api_key": api_key,
            "base_url": provider_config["base_url"],
            "model": provider_config["model"],
        }

        # Create config dictionary with all operational parameters
        config_dict = {
            "max_tokens": provider_config["max_tokens"],
            "temperature": provider_config["temperature"],
            "timeout_connect": provider_config["timeout_connect"],
            "timeout_read": provider_config["timeout_read"],
            "max_retries": provider_config["max_retries"],
            "retry_delay": provider_config["retry_delay"],
        }

        # Override with any provided kwargs
        config_dict.update(kwargs)

        # Pass config as a separate parameter
        client_kwargs["config"] = config_dict

        print(f"🚀 [CLIENT FACTORY] Initializing {provider_config['name']} API client...")
        # Create real client with all required parameters
        client = APIClient(**client_kwargs)
        print("✅ [CLIENT FACTORY] API client created successfully")
        return client

    @staticmethod
    def _create_mock_client(provider: str, **kwargs) -> Any:
        """Create a mock API client"""
        try:
            from tests.fixtures.mocks.mock_api_client import MockAPIClient
            return MockAPIClient(provider, **kwargs)
        except ImportError:
            # Fallback if mock client not available
            raise RuntimeError("Mock client not available - install test dependencies")

    @staticmethod
    def create_client_for_component(
        component_type: str,
        use_mock: Optional[bool] = None,
        **kwargs
    ) -> APIClient:
        """
        Create an API client optimized for a specific component type.

        Args:
            component_type: Component type (frontmatter, text, etc.)
            use_mock: Force mock usage
            **kwargs: Additional client configuration

        Returns:
            APIClient instance configured for the component
        """
        # Import component config to get provider mapping
        try:
            from run import COMPONENT_CONFIG
            component_config = COMPONENT_CONFIG.get(component_type, {})
            provider = component_config.get("api_provider")
            if not provider:
                raise ValueError(f"API provider must be configured for component '{component_type}' - no defaults allowed in fail-fast architecture")
        except ImportError:
            raise ValueError(f"COMPONENT_CONFIG must be available for component '{component_type}' - no defaults allowed in fail-fast architecture")

        return APIClientFactory.create_client(provider, use_mock, **kwargs)

    @staticmethod
    def validate_configuration() -> Dict[str, Any]:
        """
        Validate API configuration across all providers.

        Returns:
            Dict with validation results
        """
        from api.key_manager import is_provider_available

        results = {"valid": True, "providers": {}}

        for provider_id, config in API_PROVIDERS.items():
            is_configured = is_provider_available(provider_id)

            results["providers"][provider_id] = {
                "configured": is_configured,
                "env_var": config["env_var"],
                "base_url": config["base_url"],
                "model": config.get("model", config.get("default_model", "unknown"))
            }

            if not is_configured:
                results["valid"] = False

        return results


# Convenience functions for backward compatibility
def create_api_client(provider: str = "deepseek", **kwargs) -> APIClient:
    """Create an API client (convenience function)"""
    return APIClientFactory.create_client(provider, **kwargs)


def get_api_client_for_component(component_type: str, **kwargs) -> APIClient:
    """Get API client for component (convenience function)"""
    return APIClientFactory.create_client_for_component(component_type, **kwargs)


def is_test_mode() -> bool:
    """Check if we're in test mode"""
    return APIClientFactory.is_test_mode()


# Global instance for easy access
api_client_factory = APIClientFactory()
