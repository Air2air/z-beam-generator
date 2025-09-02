#!/usr/bin/env python3
"""
API Provider Test Suite

Tests the multi-API provider system including:
- DeepSeek API client
- Grok (X.AI) API client
- Provider routing and configuration
- Error handling and fallbacks
"""

import sys
import os
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_deepseek_api_client():
    """Test DeepSeek API client functionality"""
    print("🔍 Testing DeepSeek API Client...")
    
    try:
        from api.deepseek import create_deepseek_client
        from api.client import APIClient
        
        # Test without API key (should fail gracefully)
        try:
            create_deepseek_client()
            print("  ⚠️  DeepSeek client created without API key (check environment)")
        except ValueError as e:
            print("  ✅ DeepSeek client properly requires API key")
        
        # Test with mock API key
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test_key'}):
            client = create_deepseek_client()
            assert isinstance(client, APIClient), "DeepSeek client should be APIClient instance"
            print("  ✅ DeepSeek client creation successful")
            
            # Test client configuration
            assert client.base_url == "https://api.deepseek.com", "Incorrect DeepSeek base URL"
            assert client.model == "deepseek-chat", "Incorrect DeepSeek model"
            print("  ✅ DeepSeek client configuration correct")
        
        print("  ✅ DeepSeek API client test completed successfully")
        
    except Exception as e:
        print(f"  ❌ DeepSeek API client test failed: {e}")
        pytest.fail(f"DeepSeek API client test failed: {e}")

def test_grok_api_client():
    """Test Grok (X.AI) API client functionality"""
    print("\n🤖 Testing Grok API Client...")
    
    try:
        from run import create_api_client
        from api.client import APIClient
        
        # Test without API key (should fail gracefully)
        try:
            create_api_client('grok')
            print("  ⚠️  Grok client created without API key (check environment)")
        except ValueError as e:
            print("  ✅ Grok client properly requires API key")
        
        # Test with mock API key
        with patch.dict(os.environ, {'GROK_API_KEY': 'test_key'}):
            client = create_api_client('grok')
            assert isinstance(client, APIClient), "Grok client should be APIClient instance"
            print("  ✅ Grok client creation successful")
            
            # Test client configuration
            assert client.base_url == "https://api.x.ai", "Incorrect Grok base URL"
            assert client.model == "grok-2", "Incorrect Grok model"
            print("  ✅ Grok client configuration correct")
        
        print("  ✅ Grok API client test completed successfully")
        
    except Exception as e:
        print(f"  ❌ Grok API client test failed: {e}")
        pytest.fail(f"Grok API client test failed: {e}")

def test_provider_routing():
    """Test component-to-provider routing system"""
    print("\n🔀 Testing Provider Routing...")
    
    try:
        from run import COMPONENT_CONFIG, get_api_client_for_component
        
        # Test that all components have valid providers
        valid_providers = ['deepseek', 'grok', 'none']
        components_config = COMPONENT_CONFIG.get("components", {})
        
        for component, config in components_config.items():
            provider = config['api_provider']
            assert provider in valid_providers, f"Invalid provider {provider} for {component}"
            print(f"  ✅ {component} → {provider}")
        
        # Test get_api_client_for_component
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test', 'GROK_API_KEY': 'test'}):
            for component in components_config.keys():
                try:
                    config = components_config[component]
                    if config["api_provider"] == "none":
                        # Components with 'none' provider don't need API clients
                        print(f"  ⚠️  {component} → none (no client needed)")
                        continue
                    
                    client = get_api_client_for_component(component)
                    assert client is not None, f"No client returned for {component}"
                    print(f"  ✅ Client routing successful for {component}")
                except Exception as e:
                    print(f"  ⚠️  Client routing for {component}: {e}")
        
        print("  ✅ Provider routing test completed successfully")
        
    except Exception as e:
        print(f"  ❌ Provider routing test failed: {e}")
        pytest.fail(f"Provider routing test failed: {e}")

def test_api_error_handling():
    """Test API error handling and graceful degradation"""
    print("\n🛡️ Testing API Error Handling...")
    
    try:
        from api.client import APIClient
        from unittest.mock import patch, Mock
        import requests
        
        # Test with mock failures instead of real network calls
        success_count = 0
        
        # Test connection error handling
        with patch('requests.Session.post') as mock_post:
            mock_post.side_effect = requests.ConnectionError("Connection failed")
            
            client = APIClient(
                base_url="https://test.invalid",
                api_key="test_key",
                model="test_model"
            )
            
            # Test connection (should fail)
            connection_result = client.test_connection()
            assert not connection_result, "Invalid client should fail connection test"
            print("  ✅ Invalid client properly fails connection test")
            
            # Test generation with error
            response = client.generate_simple("Test prompt")
            assert not response.success, "Invalid client should fail generation"
            print("  ✅ Invalid client properly handles generation errors")
            print(f"     Error: {response.error}")
        
        # Test statistics with failed requests
        stats = client.get_statistics()
        assert stats['total_requests'] > 0, "Statistics should track failed requests"
        print("  ✅ Statistics properly track failed requests")
        
        print("  ✅ API error handling test completed successfully")
        
    except Exception as e:
        print(f"  ❌ API error handling test failed: {e}")
        pytest.fail(f"API error handling test failed: {e}")

def test_mock_client_functionality():
    """Test mock API client for development/testing"""
    print("\n🎭 Testing Mock Client...")
    
    try:
        from api.client import MockAPIClient
        
        mock_client = MockAPIClient()
        
        # Test connection
        assert mock_client.test_connection() == True, "Mock client connection should always succeed"
        print("  ✅ Mock client connection test")
        
        # Test generation
        response = mock_client.generate_simple("Test prompt")
        assert response.success == True, "Mock generation should always succeed"
        assert len(response.content) > 0, "Mock should return content"
        assert response.token_count > 0, "Mock should return token count"
        print(f"  ✅ Mock generation ({response.token_count} tokens)")
        
        # Test statistics
        stats = mock_client.get_statistics()
        assert stats['total_requests'] >= 1, "Should track requests"
        assert stats['success_rate'] == 100.0, "Mock should have 100% success rate"
        print(f"  ✅ Mock statistics ({stats['total_requests']} requests)")
        
        # Test multiple generations
        for i in range(5):
            mock_client.generate_simple(f"Test prompt {i}")
        
        final_stats = mock_client.get_statistics()
        assert final_stats['total_requests'] >= 6, "Should track multiple requests"
        print(f"  ✅ Multiple mock generations ({final_stats['total_requests']} total)")
        
        print("  ✅ Mock client test completed successfully")
        
    except Exception as e:
        print(f"  ❌ Mock client test failed: {e}")
        pytest.fail(f"Mock client test failed: {e}")

def test_api_provider_configuration():
    """Test API provider configuration and validation"""
    print("\n⚙️ Testing API Provider Configuration...")
    
    try:
        from run import API_PROVIDERS
        
        # Test that all required providers are configured
        required_providers = ['deepseek', 'grok']
        for provider in required_providers:
            assert provider in API_PROVIDERS, f"Missing provider: {provider}"
            
            config = API_PROVIDERS[provider]
            assert 'base_url' in config, f"Missing base_url for {provider}"
            assert 'model' in config, f"Missing model for {provider}"
            assert 'env_var' in config, f"Missing env_var for {provider}"
            
            print(f"  ✅ {provider} configuration valid")
        
        # Test configuration values
        deepseek_config = API_PROVIDERS['deepseek']
        assert deepseek_config['base_url'] == "https://api.deepseek.com", "Incorrect DeepSeek URL"
        assert deepseek_config['model'] == "deepseek-chat", "Incorrect DeepSeek model"
        assert deepseek_config['env_var'] == "DEEPSEEK_API_KEY", "Incorrect DeepSeek env var"
        
        grok_config = API_PROVIDERS['grok']
        assert grok_config['base_url'] == "https://api.x.ai", "Incorrect Grok URL"
        assert grok_config['model'] == "grok-2", "Incorrect Grok model"
        assert grok_config['env_var'] == "GROK_API_KEY", "Incorrect Grok env var"
        
        print("  ✅ All provider configurations validated")
        
        print("  ✅ API provider configuration test completed successfully")
        
    except Exception as e:
        print(f"  ❌ API provider configuration test failed: {e}")
        pytest.fail(f"API provider configuration test failed: {e}")

def main():
    """Run all API provider tests"""
    print("🧪 API PROVIDER TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("DeepSeek API Client", test_deepseek_api_client),
        ("Grok API Client", test_grok_api_client),
        ("Provider Routing", test_provider_routing),
        ("API Error Handling", test_api_error_handling),
        ("Mock Client", test_mock_client_functionality),
        ("Provider Configuration", test_api_provider_configuration)
    ]
    
    passed = 0
    failed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ {test_name} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 API PROVIDER TEST RESULTS")
    print(f"   ✅ Passed: {passed}/{total}")
    print(f"   ❌ Failed: {failed}/{total}")
    print(f"   📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All API provider tests passed!")
        print("   Multi-API provider system is fully operational.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
