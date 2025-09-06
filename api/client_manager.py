#!/usr/bin/env python3
"""
API Client Manager

Centralized API client management and configuration.
Extracted from run.py to reduce bloat and improve testability.
"""

import os

# Import configurations from run.py where they are now centralized
import sys
import time
from pathlib import Path
from typing import Optional

from .client import APIClient
from .env_loader import EnvLoader

# Add the project root to path to ensure run.py can be imported
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import configurations from api.config and cli.component_config to avoid circular imports
from .config import API_PROVIDERS


def setup_api_client(provider: str = "deepseek") -> APIClient:
    """Setup API client with fail-fast behavior - no fallbacks"""
    return create_api_client(provider)


def create_api_client(provider: str) -> APIClient:
    """
    Create API client for specified provider with strict fail-fast behavior.

    Args:
        provider: Provider ID (deepseek, grok, etc.)

    Returns:
        APIClient instance

    Raises:
        ValueError: If provider is invalid
        RuntimeError: If API key is missing
    """
    # Load environment/configuration first
    EnvLoader.load_env()

    if provider not in API_PROVIDERS:
        raise ValueError(
            f"Invalid provider: {provider}. Available: {list(API_PROVIDERS.keys())}"
        )

    provider_config = API_PROVIDERS[provider]
    api_key = os.getenv(provider_config["env_var"])

    if not api_key:
        raise RuntimeError(
            f"API key missing for {provider}. Set {provider_config['env_var']} environment variable."
        )

    # Create client with provider configuration
    client = APIClient(
        base_url=provider_config["base_url"],
        api_key=api_key,
        model=provider_config["model"],
    )

    return client


def get_api_client_for_component(component_type: str) -> APIClient:
    """
    Get appropriate API client for a specific component type.

    Args:
        component_type: Component type (frontmatter, content, etc.)

    Returns:
        APIClient instance configured for the component

    Raises:
        ValueError: If component type is invalid
        RuntimeError: If provider configuration is missing
    """
    # Import here to avoid circular import
    from cli.component_config import COMPONENT_CONFIG
    components_config = COMPONENT_CONFIG.get("components", {})

    if component_type not in components_config:
        raise ValueError(f"Unknown component type: {component_type}")

    component_config = components_config[component_type]

    # Handle hybrid and API data providers - use api_provider field
    data_provider = component_config.get("data_provider", "API")
    api_provider = component_config.get("api_provider", "deepseek")

    if data_provider in ["hybrid", "API"]:
        return create_api_client(api_provider)
    else:
        # For static components, still return default client for consistency
        return create_api_client("deepseek")


def validate_api_environment() -> dict:
    """
    Validate API environment configuration.

    Returns:
        Dict with validation results for each provider
    """
    EnvLoader.load_env()
    results = {}

    for provider_id, config in API_PROVIDERS.items():
        api_key = os.getenv(config["env_var"])
        results[provider_id] = {
            "provider": config["name"],
            "env_var": config["env_var"],
            "configured": bool(api_key),
            "base_url": config["base_url"],
            "model": config.get("model", config.get("default_model", "unknown")),
        }

    return results


def test_api_connectivity(provider: str = None) -> dict:
    """
    Test API connectivity for providers.

    Args:
        provider: Specific provider to test, or None for all

    Returns:
        Dict with connectivity test results
    """
    results = {}
    providers_to_test = [provider] if provider else list(API_PROVIDERS.keys())

    for provider_id in providers_to_test:
        try:
            client = create_api_client(provider_id)

            # Test with simple prompt
            test_prompt = "Test connectivity - respond with 'OK'"
            start_time = time.time()
            response = client.generate_simple(test_prompt)
            response_time = time.time() - start_time

            results[provider_id] = {
                "success": response.success,
                "response_time": response_time,
                "token_count": getattr(response, "token_count", 0),
                "error": getattr(response, "error_message", None)
                if not response.success
                else None,
            }

        except Exception as e:
            results[provider_id] = {
                "success": False,
                "error": str(e),
                "response_time": None,
                "token_count": 0,
            }

    return results
