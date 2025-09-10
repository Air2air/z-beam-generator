#!/usr/bin/env python3
"""
Z-Beam Component Configuration Utilities

Utility functions for component configuration management.
Component configuration data is now stored in run.py for user customization.

ARCHITECTURE NOTE:
- User-settable configurations (COMPONENT_CONFIG, AI_DETECTION_CONFIG) are in run.py
- System utility functions (display, sorting, validation) remain here
- This separation allows users to easily modify settings without touching system code
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    pass  # Continue without dotenv if not available


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


# Import user-settable configuration from run.py
try:
    from run import COMPONENT_CONFIG
except ImportError:
    # Fallback if run.py is not available (e.g., during testing)
    COMPONENT_CONFIG = {}


def show_component_configuration():
    """Display current component configuration."""
    print("🔧 COMPONENT CONFIGURATION")
    print("=" * 50)

    # Get components configuration (no longer nested under "components")
    components_config = COMPONENT_CONFIG

    enabled_count = sum(1 for config in components_config.values() if config["enabled"])
    disabled_count = len(components_config) - enabled_count

    print(
        f"Total Components: {len(components_config)} ({enabled_count} enabled, {disabled_count} disabled)"
    )
    print("Global Author: Dynamic assignment per generation (no default)")
    print()

    # Group by data provider
    provider_groups = {}
    for component, config in components_config.items():
        if config["enabled"]:
            provider = config["data_provider"]
            if provider not in provider_groups:
                provider_groups[provider] = []
            provider_groups[provider].append(component)

    # Display by provider
    for provider, components in provider_groups.items():
        if provider == "static":
            provider_name = "Static Component"
        elif provider == "API":
            provider_name = "API-Driven Component"
        else:
            provider_name = f"{provider} Provider"
        print(f"🌐 {provider_name} ({len(components)} components):")
        for component in sorted(components):
            print(f"   ✅ {component}")
        print()

    # Display disabled components
    disabled = [
        comp for comp, config in components_config.items() if not config["enabled"]
    ]
    if disabled:
        print(f"❌ Disabled Components ({len(disabled)}):")
        for component in sorted(disabled):
            print(f"   ⭕ {component}")
        print()

    # Display API provider details
    print("🔑 API Provider Configuration:")
    API_PROVIDERS = get_api_providers()
    for provider_id, provider_info in API_PROVIDERS.items():
        env_key = provider_info["env_key"]
        has_key = "✅" if os.getenv(env_key) else "❌"
        print(
            f"   {has_key} {provider_info['name']}: {provider_info['model']} (env: {env_key})"
        )

    print()


def get_components_sorted_by_priority(include_disabled=False):
    """Get components sorted by priority order."""
    components_config = COMPONENT_CONFIG

    # Sort by priority (ascending)
    sorted_components = sorted(
        components_config.items(),
        key=lambda x: x[1].get("priority", 999)
    )

    if include_disabled:
        return [component for component, config in sorted_components]
    else:
        return [component for component, config in sorted_components if config.get("enabled", True)]


def get_enabled_components():
    """Get list of enabled components."""
    components_config = COMPONENT_CONFIG
    return [comp for comp, config in components_config.items() if config.get("enabled", True)]
