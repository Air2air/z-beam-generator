#!/usr/bin/env python3
"""
API Client Manager

Centralized API client management and configuration.
Updated to use the unified client factory for consistency.
"""

import os
import time

# Import the unified factory
from .client_factory import create_api_client
from .config import API_PROVIDERS


def setup_api_client(provider: str = "deepseek"):
    """Setup API client with fail-fast behavior - no fallbacks"""
    return create_api_client(provider)


def validate_api_environment() -> dict:
    """
    Validate API environment configuration.

    Returns:
        Dict with validation results for each provider
    """
    from api.key_manager import is_provider_available

    results = {}

    for provider_id, config in API_PROVIDERS.items():
        results[provider_id] = {
            "provider": config["name"],
            "env_var": config["env_var"],
            "configured": is_provider_available(provider_id),
            "base_url": config["base_url"],
            "model": config.get("model", config.get("default_model", "unknown")),
        }

    return results


def get_api_client_for_component(component_type: str):
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
    from run import COMPONENT_CONFIG

    components_config = COMPONENT_CONFIG

    if component_type not in components_config:
        raise ValueError(f"Unknown component type: {component_type}")

    component_config = components_config[component_type]

    # Handle hybrid and API data providers - use api_provider field
    data_provider = component_config.get("data_provider", "API")
    api_provider = component_config.get("api_provider", "deepseek")

    if data_provider in ["hybrid", "API"]:
        return create_api_client(api_provider)
    elif api_provider == "none":
        # For truly static components that don't need any API
        return None
    else:
        # For static components, still return default client for consistency
        return create_api_client("deepseek")
def test_api_connectivity(provider: str = None) -> dict:
    """
    Test API connectivity for providers.

    Args:
        provider: Specific provider to test, or None for all

    Returns:
        Dict with connectivity test results
    """
    print("🔍 [CLIENT MANAGER] Testing API connectivity...")

    results = {}
    providers_to_test = [provider] if provider else list(API_PROVIDERS.keys())

    print(f"📋 [CLIENT MANAGER] Testing providers: {', '.join(providers_to_test)}")

    for provider_id in providers_to_test:
        print(f"🧪 [CLIENT MANAGER] Testing {provider_id}...")
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

            if response.success:
                print(f"✅ [CLIENT MANAGER] {provider_id}: Connected ({response_time:.2f}s)")
            else:
                print(f"❌ [CLIENT MANAGER] {provider_id}: Failed - {results[provider_id]['error']}")

        except Exception as e:
            results[provider_id] = {
                "success": False,
                "error": str(e),
                "response_time": None,
                "token_count": 0,
            }
            print(f"💥 [CLIENT MANAGER] {provider_id}: Error - {str(e)}")

    total_tested = len(results)
    successful = sum(1 for r in results.values() if r["success"])
    print(f"📊 [CLIENT MANAGER] Connectivity test complete: {successful}/{total_tested} providers working")

    return results
