"""
API Package for Z-Beam Generator

This package provides standardized, fail-fast API client management
with consistent behavior across all providers and environments.
"""

# Main API client and factory
from .client import APIClient, APIResponse, GenerationRequest
from .client_factory import APIClientFactory, create_api_client, get_api_client_for_component

# Configuration and key management
from .config import API_PROVIDERS, get_default_config
from .key_manager import (
    APIKeyManager,
    get_api_key,
    validate_all_api_keys,
    get_masked_api_key,
    is_provider_available
)

# Specialized clients
from .deepseek import DeepSeekClient, create_deepseek_client

# Client management
from .client_manager import (
    setup_api_client,
    validate_api_environment,
    get_api_client_for_component as get_component_client,
    test_api_connectivity
)

# Environment loading (legacy - prefer key_manager for new code)
from .env_loader import EnvLoader

__all__ = [
    # Main classes
    "APIClient",
    "APIClientFactory",
    "APIKeyManager",
    "DeepSeekClient",
    "EnvLoader",

    # Response and request types
    "APIResponse",
    "GenerationRequest",

    # Factory functions
    "create_api_client",
    "create_deepseek_client",
    "get_api_client_for_component",
    "get_component_client",

    # Key management
    "get_api_key",
    "validate_all_api_keys",
    "get_masked_api_key",
    "is_provider_available",

    # Configuration
    "API_PROVIDERS",
    "get_default_config",

    # Management functions
    "setup_api_client",
    "validate_api_environment",
    "test_api_connectivity",
]
