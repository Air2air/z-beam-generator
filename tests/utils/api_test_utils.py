#!/usr/bin/env python3
"""
API Key Testing Utility
Fixes the recurring problem of losing API keys in tests by ensuring proper .env loading.
"""

import sys
from pathlib import Path

import pytest

from api.client_manager import create_api_client
from api.env_loader import EnvLoader


def ensure_api_keys():
    """Ensure API keys are available for testing"""
    try:
        loader = EnvLoader()
        required_keys = ["OPENAI_API_KEY", "DEEPSEEK_API_KEY"]

        missing_keys = []
        for key in required_keys:
            if not loader.get_env_var(key):
                missing_keys.append(key)

        if missing_keys:
            print(f"❌ Missing API keys: {missing_keys}")
            return False

        print("✅ All required API keys found")
        return True

    except Exception as e:
        print(f"❌ Error checking API keys: {e}")
        return False


def get_test_api_client():
    """Get a test API client instance"""
    try:
        return create_api_client()
    except Exception as e:
        print(f"❌ Error creating API client: {e}")
        return None


def require_api_keys():
    """Decorator to skip tests if API keys are not available"""

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
            pass  # Success
        else:
            print("❌ API client creation failed")
            import pytest

            pytest.fail("Test failed")
    else:
        print("❌ API keys not available")
        import pytest

        pytest.fail("Test failed")
