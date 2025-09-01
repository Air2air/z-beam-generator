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


def fallback_get_api_key(provider: str) -> Optional[str]:
    """Fallback method to get API key from environment when imports fail."""
    try:
        # Try to get from environment first
                
        # Map provider names to environment variable names
        env_key_map = {
            "deepseek": "DEEPSEEK_API_KEY",
            "grok": "GROK_API_KEY"
        }
        
        env_key = env_key_map.get(provider.lower())
        if env_key:
            # Try to get from os.environ first
            api_key = os.getenv(env_key)
            if api_key:
                return api_key
        
        # Try to load from .env file directly
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key == env_key:
                            return value
        
        return None
        
    except Exception as e:
        logging.warning(f"Error in fallback API key retrieval: {e}")
        return None


def create_api_client(provider: str):
    """Create an API client for the specified provider."""

    # Handle special case for components that don't need API clients
    if provider in ["none", "frontmatter"]:
        return None

    if provider not in API_PROVIDERS:
        raise ValueError(f"Unknown API provider: {provider}")

    provider_config = API_PROVIDERS[provider]

    try:
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

    except ImportError as e:
        # Fallback when imports fail - try to get API key directly
        logging.warning(f"Import failed for API modules: {e}")
        logging.info("Attempting fallback API key retrieval...")
        
        api_key = fallback_get_api_key(provider)
        if not api_key:
            raise ValueError(
                f"Fallback failed: API key not found for {provider}. Please set {provider_config['env_key']} in your .env file."
            )
        
        try:
            # Try to create a basic APIClient with fallback method
            from api.client import APIClient
            return APIClient(
                api_key=api_key,
                base_url=provider_config["base_url"],
                model=provider_config["model"],
            )
        except ImportError:
            raise ImportError(f"Failed to import API client modules: {e}")
        
    except Exception as e:
        # Try fallback on any other error
        logging.warning(f"Error creating API client: {e}")
        logging.info("Attempting fallback API key retrieval...")
        
        api_key = fallback_get_api_key(provider)
        if not api_key:
            raise ValueError(
                f"Fallback failed: API key not found for {provider}. Please set {provider_config['env_key']} in your .env file."
            )
        
        try:
            from api.client import APIClient
            return APIClient(
                api_key=api_key,
                base_url=provider_config["base_url"],
                model=provider_config["model"],
            )
        except Exception as fallback_error:
            raise Exception(f"Both primary and fallback API client creation failed. Primary: {e}, Fallback: {fallback_error}")


def get_api_client_for_component(component_type: str, component_config: dict):
    """Get the appropriate API client for a component type."""

    components_config = component_config.get("components", {})
    if component_type in components_config:
        provider = components_config[component_type]["data_provider"]
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
