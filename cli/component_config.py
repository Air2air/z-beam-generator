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
    return [
        comp
        for comp, config in COMPONENT_CONFIG.items()
        if config.get("enabled", False)
    ]


# CONSOLIDATION ENHANCEMENT: Adapter for unified component configuration
class ComponentConfigAdapter:
    """
    Adapter for unified component configuration access while preserving existing interfaces.
    Consolidates access to component settings and API provider information.
    """
    
    @staticmethod
    def get_component_config() -> dict:
        """Get complete component configuration"""
        return COMPONENT_CONFIG.copy()
    
    @staticmethod
    def get_enabled_components() -> list:
        """Get list of enabled components"""
        return [
            comp for comp, config in COMPONENT_CONFIG.items() 
            if config.get("enabled", False)
        ]
    
    @staticmethod
    def get_disabled_components() -> list:
        """Get list of disabled components"""
        return [
            comp for comp, config in COMPONENT_CONFIG.items() 
            if not config.get("enabled", False)
        ]
    
    @staticmethod
    def get_component_priority(component: str) -> int:
        """Get priority for a specific component"""
        return COMPONENT_CONFIG.get(component, {}).get("priority", 999)
    
    @staticmethod
    def get_components_by_provider(provider: str, include_disabled: bool = False) -> list:
        """Get components using a specific data provider"""
        components = []
        for comp, config in COMPONENT_CONFIG.items():
            if include_disabled or config.get("enabled", False):
                if config.get("data_provider") == provider:
                    components.append(comp)
        return components
    
    @staticmethod
    def validate_component_config(component: str) -> bool:
        """Validate that a component is properly configured"""
        if component not in COMPONENT_CONFIG:
            return False
        
        config = COMPONENT_CONFIG[component]
        required_fields = ["enabled", "data_provider", "priority"]
        
        return all(field in config for field in required_fields)
    
    @staticmethod
    def get_api_provider_info() -> dict:
        """Get API provider information for display"""
        providers = get_api_providers()
        info = {}
        
        for provider_id, provider_config in providers.items():
            env_key = provider_config.get("env_var", f"{provider_id.upper()}_API_KEY")
            info[provider_id] = {
                "name": provider_config.get("name", provider_id.title()),
                "env_var": env_key,
                "has_key": bool(os.getenv(env_key)),
                "base_url": provider_config.get("base_url", "unknown")
            }
        
        return info
