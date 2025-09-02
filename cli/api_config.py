#!/usr/bin/env python3
"""
Z-Beam CLI API Configuration

Extracted API configuration and client creation from run.py for better modularity.
Handles API provider configuration, client creation, and fallback mechanisms.
"""

import os
import logging
from pathlib import Path
from typing import Optional


# API Provider Configuration
API_PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek",
        "env_key": "DEEPSEEK_API_KEY",
        "env_var": "DEEPSEEK_API_KEY",  # Add this for test compatibility
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
    },
    "grok": {
        "name": "Grok (X.AI)",
        "env_key": "GROK_API_KEY",
        "env_var": "GROK_API_KEY",  # Add this for test compatibility
        "base_url": "https://api.x.ai",  # Remove /v1 since APIClient adds it
        "model": "grok-2",  # grok-2 works reliably; grok-4 currently uses reasoning tokens without completion output
    },
}


def create_api_client(provider: str):
    """Create an API client for the specified provider."""

    # Handle special case for components that don't need API clients
    if provider in ["none", "frontmatter"]:
        return None

    if provider not in API_PROVIDERS:
        raise ValueError(f"Unknown API provider: {provider}")

    provider_config = API_PROVIDERS[provider]
    
    from api.client import APIClient
    from api.env_loader import EnvLoader

    # Get provider configuration with API key
    config = EnvLoader.get_provider_config(provider_config)

    # Check if API key was found
    if "api_key" not in config:
        raise ValueError(
            f"API key not found for {provider}. Please set {provider_config['env_key']} in your environment."
        )

    # Create API client with provider-specific configuration
    return APIClient(
        api_key=config["api_key"],
        base_url=config["base_url"],
        model=config["model"],
    )


def get_api_client_for_component(component_type: str, component_config: dict):
    """Get the appropriate API client for a component type."""

    components_config = component_config.get("components", {})
    if component_type in components_config:
        config = components_config[component_type]
        data_provider = config["data_provider"]
        
        # For hybrid and API data providers, use the api_provider field
        if data_provider in ["hybrid", "API"]:
            provider = config["api_provider"]
        else:
            provider = data_provider
    else:
        provider = "deepseek"  # Default provider

    return create_api_client(provider)


def check_environment():
    """Check environment variables and API key configuration."""

    print("🔍 ENVIRONMENT CONFIGURATION CHECK")
    print("=" * 50)

    try:
        from api.env_loader import EnvLoader
        from pathlib import Path

        # Check for .env file
        env_file = Path(".env")
        env_example = Path(".env.example")

        print("📁 Environment Files:")
        if env_file.exists():
            print(f"   ✅ .env file found: {env_file.absolute()}")
        else:
            print("   ❌ .env file not found")
            if env_example.exists():
                print(f"   💡 Example available: {env_example.absolute()}")
                print(f"      Copy {env_example.name} to .env and add your API keys")

        print()

        # Load environment and check API keys
        print("🔑 API Key Status:")
        available_keys = EnvLoader.list_available_keys()

        provider_keys_found = 0
        for provider_id, provider_info in API_PROVIDERS.items():
            env_key = provider_info["env_key"]
            has_key = bool(EnvLoader.get_api_key(provider_info["name"], env_key))
            status = "✅ Available" if has_key else "❌ Missing"
            print(f"   {status}: {provider_info['name']} ({env_key})")
            if has_key:
                provider_keys_found += 1

        print()

        # Test API client creation
        print("🧪 API Client Tests:")
        for provider_id, provider_info in API_PROVIDERS.items():
            try:
                client = create_api_client(provider_id)
                print(f"   ✅ {provider_info['name']}: Client created successfully")
            except Exception as e:
                print(f"   ❌ {provider_info['name']}: {str(e)}")

        print()

        # Summary and recommendations
        print("📋 Summary:")
        print(f"   API Keys Found: {provider_keys_found}/{len(API_PROVIDERS)}")

        if provider_keys_found == 0:
            print("   ⚠️  No API keys found - system will not work")
            print("   💡 Create .env file and add your API keys")
        elif provider_keys_found < len(API_PROVIDERS):
            print("   ⚠️  Some API keys missing - limited functionality")
            print("   💡 Add missing API keys for full provider support")
        else:
            print("   ✅ All API keys configured - system ready")

        if not env_file.exists() and env_example.exists():
            print("\n💡 Quick setup:")
            print(f"   cp {env_example.name} .env")
            print("   # Edit .env and add your API keys")

    except Exception as e:
        print(f"❌ Environment check failed: {e}")
