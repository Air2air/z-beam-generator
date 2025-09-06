#!/usr/bin/env python3
"""
Z-Beam Component Configuration

Extracted component configuration from run.py for better modularity.
Defines component orchestration order, provider assignments, and configuration.
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    pass  # Continue without dotenv if not available

from cli.api_config import API_PROVIDERS

# Component Configuration
# Moved here to break circular import between run.py and other modules
COMPONENT_CONFIG = {
    "components": {
        "text": {
            "enabled": True,
            "data_provider": "API",
            "api_provider": "deepseek",
        },
        "frontmatter": {
            "enabled": True,
            "data_provider": "static",
            "api_provider": "deepseek",
        },
        "bullets": {
            "enabled": True,
            "data_provider": "API",
            "api_provider": "deepseek",
        },
        "caption": {
            "enabled": True,
            "data_provider": "API",
            "api_provider": "gemini",
        },
        "tags": {
            "enabled": True,
            "data_provider": "static",
            "api_provider": "deepseek",
        },
        "author": {
            "enabled": True,
            "data_provider": "static",
            "api_provider": "none",
        },
        "badgesymbol": {
            "enabled": True,
            "data_provider": "static",
            "api_provider": "none",
        },
        "propertiestable": {
            "enabled": True,
            "data_provider": "static",
            "api_provider": "none",
        },
        "metatags": {
            "enabled": True,
            "data_provider": "static",
            "api_provider": "none",
        },
        "jsonld": {
            "enabled": True,
            "data_provider": "static",
            "api_provider": "none",
        },
        "table": {
            "enabled": True,
            "data_provider": "API",
            "api_provider": "deepseek",
        },
    }
}


def show_component_configuration():
    """Display current component configuration."""
    print("🔧 COMPONENT CONFIGURATION")
    print("=" * 50)

    # Get components configuration
    components_config = COMPONENT_CONFIG.get("components", {})

    enabled_count = sum(1 for config in components_config.values() if config["enabled"])
    disabled_count = len(components_config) - enabled_count

    print(
        f"Total Components: {len(components_config)} ({enabled_count} enabled, {disabled_count} disabled)"
    )
    print("Global Author: Dynamic assignment per generation (no default)")
    print()

    # Group by API provider
    provider_groups = {}
    for component, config in components_config.items():
        if config["enabled"]:
            provider = config["data_provider"]
            if provider not in provider_groups:
                provider_groups[provider] = []
            provider_groups[provider].append(component)

    # Display by provider
    for provider, components in provider_groups.items():
        if provider == "frontmatter":
            provider_name = "Frontmatter Data"
        elif provider == "none":
            provider_name = "Static Component"
        else:
            provider_name = API_PROVIDERS.get(provider, {}).get("name", provider)
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
    for provider_id, provider_info in API_PROVIDERS.items():
        env_key = provider_info["env_key"]
        has_key = "✅" if os.getenv(env_key) else "❌"
        print(
            f"   {has_key} {provider_info['name']}: {provider_info['model']} (env: {env_key})"
        )

    print()
