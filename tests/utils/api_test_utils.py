#!/usr/bin/env python3
"""
API Key Testing Utility
Fixes the recurring problem of losing API keys in tests by ensuring proper .env loading.
"""

import sys
from pathlib import Path

import pytest

from api.env_loader import EnvLoader
from api.client_manager import create_api_client


    def decorator(test_func):
        def wrapper(*args, **kwargs):
            if not ensure_api_keys():
                pytest.skip("API keys not available - check .env file")
            return test_func(*args, **kwargs)

        return wrapper

    return decorator


if __name__ == "__main__":
    print("🧪 TESTING API KEY AVAILABILITY")
    print("=" * 50)

    success = ensure_api_keys()

    if success:
        print("\n🎯 TESTING API CLIENT CREATION")
        print("=" * 50)
        client = get_test_api_client()

        if client:
            print("✅ API testing environment ready")
            sys.exit(0)
        else:
            print("❌ API client creation failed")
            sys.exit(1)
    else:
        print("❌ API keys not available")
        sys.exit(1)
