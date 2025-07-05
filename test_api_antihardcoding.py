#!/usr/bin/env python3
"""
Test API Client Anti-Hardcoding Compliance

This test verifies that the API client has NO hardcoded values and properly
uses the configuration system for all API-related settings.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_api_antihardcoding():
    """Test that API client follows anti-hardcoding rules."""
    print("🔍 Testing API Client Anti-Hardcoding Compliance...")
    
    # Test 1: Configuration system works
    try:
        from config.global_config import GlobalConfigManager
        
        # Mock provider models for testing
        PROVIDER_MODELS = {
            "DEEPSEEK": {
                "model": "deepseek-chat",
                "url_template": "https://api.deepseek.com/v1/chat/completions",
            },
            "XAI": {
                "model": "grok-3-mini-beta", 
                "url_template": "https://api.x.ai/v1/chat/completions",
            },
            "GEMINI": {
                "model": "gemini-2.5-flash",
                "url_template": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
            },
        }
        
        # Mock user config for testing
        USER_CONFIG = {
            "api_timeout": 45,
            "max_article_words": 800,
            "generator_provider": "DEEPSEEK",
            "detection_provider": "DEEPSEEK",
        }
        
        # Initialize configuration manager
        config_manager = GlobalConfigManager.initialize(USER_CONFIG, PROVIDER_MODELS)
        print("✅ Configuration manager initialized successfully")
        
        # Test config access methods
        timeout = config_manager.get_api_timeout()
        max_tokens = config_manager.get_max_api_tokens()
        temp = config_manager.get_content_temperature()
        deepseek_url = config_manager.get_provider_url("DEEPSEEK")
        xai_url = config_manager.get_provider_url("XAI")
        
        print(f"✅ API Timeout from config: {timeout}")
        print(f"✅ Max API tokens from config: {max_tokens}")
        print(f"✅ Content temperature from config: {temp}")
        print(f"✅ DeepSeek URL from config: {deepseek_url}")
        print(f"✅ xAI URL from config: {xai_url}")
        
    except Exception as e:
        print(f"❌ Configuration system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: API Client uses configuration (not hardcoded values)
    try:
        from infrastructure.api.client import APIClient
        
        # Create API client
        client = APIClient('DEEPSEEK', 'test-key')
        print(f"✅ API Client created for provider: {client.get_provider_name()}")
        
        # Verify the client internally uses provider config (not hardcoded URLs)
        # Check that _provider_config contains the URL from our config
        expected_url = config_manager.get_provider_url("DEEPSEEK")
        if hasattr(client, '_provider_config') and client._provider_config.get('url_template') == expected_url:
            print(f"✅ API Client properly uses configured URL: {expected_url}")
        else:
            print("❌ API Client not using configured URL properly")
            return False
            
    except Exception as e:
        print(f"❌ API Client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Check that no hardcoded values remain in API client code
    print("\n🔍 Scanning API client code for hardcoded violations...")
    
    try:
        with open('infrastructure/api/client.py', 'r') as f:
            api_client_code = f.read()
        
        # Check for common hardcoding violations
        violations = []
        
        # Check for hardcoded URLs
        if 'https://api.x.ai' in api_client_code:
            violations.append("Hardcoded xAI URL found")
        if 'https://api.deepseek.com' in api_client_code:
            violations.append("Hardcoded DeepSeek URL found")
        if 'https://generativelanguage.googleapis.com' in api_client_code:
            violations.append("Hardcoded Gemini URL found")
        
        # Check for hardcoded timeouts, max_tokens, temperatures
        import re
        if re.search(r'timeout\s*=\s*\d+', api_client_code):
            violations.append("Hardcoded timeout found")
        if re.search(r'max_tokens\s*=\s*\d+', api_client_code):
            violations.append("Hardcoded max_tokens default found")
        if re.search(r'temperature\s*=\s*[\d.]+', api_client_code):
            violations.append("Hardcoded temperature found")
        
        if violations:
            print("❌ Anti-hardcoding violations found:")
            for violation in violations:
                print(f"  - {violation}")
            return False
        else:
            print("✅ No hardcoding violations found in API client")
            
    except Exception as e:
        print(f"❌ Code scanning failed: {e}")
        return False
    
    print("\n🎉 ALL ANTI-HARDCODING TESTS PASSED!")
    print("✅ API client properly uses configuration system")
    print("✅ No hardcoded URLs, timeouts, tokens, or temperatures")
    print("✅ All values sourced from GlobalConfigManager")
    return True

if __name__ == "__main__":
    success = test_api_antihardcoding()
    sys.exit(0 if success else 1)
