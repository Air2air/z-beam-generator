#!/usr/bin/env python3
"""
API Key Testing Utility
Fixes the recurring problem of losing API keys in tests by ensuring proper .env loading.
"""

import sys
from pathlib import Path

def ensure_api_keys():
    """
    Ensure API keys are loaded from .env file for testing.
    This fixes the recurring issue of API-dependent test failures.
    """
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Load environment variables
    from api.env_loader import EnvLoader
    EnvLoader.load_env()
    
    # Check available API keys
    available_keys = EnvLoader.list_available_keys()
    
    print("🔑 API KEYS STATUS:")
    print("=" * 40)
    
    required_keys = ['GROK_API_KEY', 'DEEPSEEK_API_KEY', 'OPENAI_API_KEY']
    missing_keys = []
    
    for key in required_keys:
        if available_keys.get(key, False):
            print(f"✅ {key}: Available")
        else:
            print(f"❌ {key}: Missing")
            missing_keys.append(key)
    
    if missing_keys:
        print(f"\n⚠️  Missing {len(missing_keys)} required API keys!")
        print("🔧 Check .env file in project root")
        return False
    else:
        print(f"\n✅ All {len(required_keys)} required API keys available")
        print("🎯 API-dependent tests can proceed")
        return True

def get_test_api_client():
    """Get a working API client for testing"""
    ensure_api_keys()
    
    try:
        from api.client_manager import create_api_client
        
        # Try providers in order of preference
        providers = ['grok', 'deepseek', 'openai']
        
        for provider in providers:
            try:
                client = create_api_client(provider)
                if client:
                    print(f"✅ Created {provider} client for testing")
                    return client
            except Exception as e:
                print(f"⚠️  {provider} client failed: {e}")
                continue
        
        print("❌ No working API client available")
        return None
        
    except Exception as e:
        print(f"❌ API client creation failed: {e}")
        return None

def skip_if_no_api_keys():
    """Decorator to skip tests if API keys are not available"""
    import pytest
    
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
