"""
API Package for Z-Beam Generator

This package provides standardized, fail-fast API client management
with consistent behavior across all providers and environments.
"""

# Main API client and factory
from .client import APIClient, APIResponse, GenerationRequest
from .client_factory import APIClientFactory, create_api_client, get_api_client_for_component

# Client caching for performance
from .client_cache import (
    APIClientCache,
    get_cached_api_client,
    get_cached_client_for_component,
    api_client_cache
)

# Configuration and key management
from .config import get_default_config, get_api_providers
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

# Environment loading (DEPRECATED - use key_manager for all new code)
# from .env_loader import EnvLoader  # REMOVED - no longer supported

__all__ = [
    # Main classes
    "APIClient",
    "APIClientFactory", 
    "APIClientCache",
    "APIKeyManager",
    "DeepSeekClient",
    # "EnvLoader",  # REMOVED - deprecated

    # Response and request types
    "APIResponse",
    "GenerationRequest",

    # Factory functions
    "create_api_client",
    "create_deepseek_client",
    "get_api_client_for_component",
    "get_component_client",

    # Cache functions
    "get_cached_api_client",
    "get_cached_client_for_component",
    "api_client_cache",

    # Key management
    "get_api_key",
    "validate_all_api_keys",
    "get_masked_api_key",
    "is_provider_available",

    # Configuration
    "get_api_providers",
    "get_default_config",

    # Management functions
    "setup_api_client",
    "validate_api_environment",
    "test_api_connectivity",
]
