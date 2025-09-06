#!/usr/bin/env python3
"""
Z-Beam CLI API Configuration

Extracted API configuration and client creation from run.py for better modularity.
Handles API provider configuration, client creation, and fallback mechanisms.
"""

import logging  # noqa: F401
import os  # noqa: F401
from pathlib import Path  # noqa: F401
from typing import Optional  # noqa: F401

from api.client import APIClient
from api.config import API_PROVIDERS
from api.env_loader import EnvLoader


def check_api_configuration():
    """Check API configuration and display status."""
    try:
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
        # List keys to trigger loader output
        EnvLoader.list_available_keys()

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
                # Import here to avoid circular import
                from api.client_manager import create_api_client

                create_api_client(provider_id)
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
