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
    "frontmatter": {
        "generator": "frontmatter",
        "api_provider": "deepseek",
        "priority": 1,
        "required": True,
        "enabled": True,
        "data_provider": "API",
    },
    "metatags": {
        "generator": "metatags",
        "api_provider": "deepseek",
        "priority": 2,
        "required": True,
        "enabled": True,
        "data_provider": "static",
    },
    "propertiestable": {
        "generator": "propertiestable",
        "api_provider": "deepseek",
        "priority": 3,
        "required": True,
        "enabled": True,
        "data_provider": "static",
    },
    "bullets": {
        "generator": "bullets",
        "api_provider": "deepseek",
        "priority": 4,
        "required": True,
        "enabled": True,
        "data_provider": "API",
    },
    "caption": {
        "generator": "caption",
        "api_provider": "deepseek",
        "priority": 5,
        "required": True,
        "enabled": True,
        "data_provider": "API",
    },
    "text": {
        "generator": "text",
        "api_provider": "deepseek",
        "priority": 6,
        "required": True,
        "enabled": True,
        "data_provider": "API",
    },
    "table": {
        "generator": "table",
        "api_provider": "deepseek",
        "priority": 7,
        "required": True,
        "enabled": True,
        "data_provider": "API",
    },
    "tags": {
        "generator": "tags",
        "api_provider": "deepseek",
        "priority": 8,
        "required": True,
        "enabled": True,
        "data_provider": "static",
    },
    "jsonld": {
        "generator": "jsonld",
        "api_provider": "deepseek",
        "priority": 9,
        "required": True,
        "enabled": True,
        "data_provider": "static",
    },
    "author": {
        "generator": "author",
        "api_provider": "none",
        "priority": 10,
        "required": True,
        "enabled": True,
        "data_provider": "static",
    },
}


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
    for provider_id, provider_info in API_PROVIDERS.items():
        env_key = provider_info["env_key"]
        has_key = "✅" if os.getenv(env_key) else "❌"
        print(
            f"   {has_key} {provider_info['name']}: {provider_info['model']} (env: {env_key})"
        )

    print()


def get_components_sorted_by_priority():
    """Get components sorted by priority order."""
    components_config = COMPONENT_CONFIG

    # Sort by priority (ascending)
    sorted_components = sorted(
        components_config.items(),
        key=lambda x: x[1].get("priority", 999)
    )

    return [component for component, config in sorted_components if config.get("enabled", True)]


def get_enabled_components():
    """Get list of enabled components."""
    components_config = COMPONENT_CONFIG
    return [comp for comp, config in components_config.items() if config.get("enabled", True)]
