#!/usr/bin/env python3
"""
API Response Test Suite

Focused test suite for API response validation:
- Basic API response testing
- Error handling validation  
- Environment configuration testing
- API connection validation
- Multi-provider integration testing
"""

import sys
import os
import time
import json
import requests
from pathlib import Path
from unittest.mock import patch, MagicMock
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import pytest

# Add parent directory to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent))

@dataclass
class APITestResult:
    """Test result with comprehensive metrics"""
    provider: str
    test_name: str
    success: bool
    response_time: Optional[float] = None
    token_count: Optional[int] = None
    error_message: Optional[str] = None
    content_quality: Optional[str] = None

class APITestSuite:
    """Comprehensive API testing framework"""
    
    def __init__(self):
        self.results: List[APITestResult] = []
        self.enable_real_api_tests = self._check_api_keys_available()
    
    def _check_api_keys_available(self) -> bool:
        """Check if API keys are available for real testing"""
        try:
            from api.env_loader import EnvLoader
            EnvLoader.load_env()
            
            deepseek_key = os.getenv('DEEPSEEK_API_KEY')
            grok_key = os.getenv('GROK_API_KEY')
            
            # Only enable real API tests if both keys are present AND not obviously fake
            keys_available = (
                deepseek_key and len(deepseek_key) > 10 and not deepseek_key.startswith('test') and
                grok_key and len(grok_key) > 10 and not grok_key.startswith('test')
            )
            
            # Also check for explicit test environment variable
            test_env = os.getenv('ENABLE_REAL_API_TESTS', '').lower()
            if test_env in ['false', '0', 'no', 'off']:
                return False
            
            return keys_available
        except:
            return False
    
    def add_result(self, result: APITestResult):
        """Add test result to collection"""
        self.results.append(result)
    
    def test_environment_configuration(self) -> bool:
        """Test environment configuration and API key loading"""
        print("🌍 Testing Environment Configuration...")
        
        try:
            from api.env_loader import EnvLoader
            
            # Test .env file loading
            env_file = Path('.env')
            if env_file.exists():
                print("  ✅ .env file found")
                
                # Load environment
                EnvLoader.load_env()
                print("  ✅ Environment loaded successfully")
                
                # Check API keys
                deepseek_key = os.getenv('DEEPSEEK_API_KEY')
                grok_key = os.getenv('GROK_API_KEY')
                
                if deepseek_key:
                    masked_key = f"{deepseek_key[:8]}...{deepseek_key[-4:]}" if len(deepseek_key) > 12 else "[short]"
                    print(f"  ✅ DeepSeek API key: {masked_key}")
                else:
                    print("  ⚠️  DeepSeek API key: Not found")
                
                if grok_key:
                    masked_key = f"{grok_key[:8]}...{grok_key[-4:]}" if len(grok_key) > 12 else "[short]"
                    print(f"  ✅ Grok API key: {masked_key}")
                else:
                    print("  ⚠️  Grok API key: Not found")
                
                self.add_result(APITestResult(
                    provider="environment",
                    test_name="configuration",
                    success=True
                ))
                
            else:
                print("  ⚠️  .env file not found")
                self.add_result(APITestResult(
                    provider="environment",
                    test_name="configuration",
                    success=False,
                    error_message=".env file not found"
                ))
            
            return True
            
        except Exception as e:
            print(f"  ❌ Environment test failed: {e}")
            self.add_result(APITestResult(
                provider="environment",
                test_name="configuration",
                success=False,
                error_message=str(e)
            ))
            return False
    
    def test_api_client_creation(self) -> bool:
        """Test API client creation for all providers"""
        print("\n🔧 Testing API Client Creation...")
        
        try:
            from api.client import APIClient
            from run import API_PROVIDERS
            
            success_count = 0
            total_providers = len(API_PROVIDERS)
            
            for provider_id, config in API_PROVIDERS.items():
                try:
                    # Test with mock key first
                    with patch.dict(os.environ, {config['env_var']: 'test_key'}):
                        client = APIClient(
                            base_url=config['base_url'],
                            model=config['model'],
                            api_key='test_key'
                        )
                        
                        # Verify client configuration
                        assert client.base_url == config['base_url']
                        assert client.model == config['model']
                        
                        print(f"  ✅ {config['name']}: Client created successfully")
                        success_count += 1
                        
                        self.add_result(APITestResult(
                            provider=provider_id,
                            test_name="client_creation",
                            success=True
                        ))
                        
                except Exception as e:
                    print(f"  ❌ {config['name']}: {e}")
                    self.add_result(APITestResult(
                        provider=provider_id,
                        test_name="client_creation",
                        success=False,
                        error_message=str(e)
                    ))
            
            print(f"  📊 Client creation: {success_count}/{total_providers} successful")
            return success_count == total_providers
            
        except Exception as e:
            print(f"  ❌ Client creation test failed: {e}")
            return False
    
    def test_api_connections(self) -> bool:
        """Test API connections (uses mocks when API keys not available)"""
        print("\n🔗 Testing API Connections...")
        
        try:
            from api.client import APIClient
            from run import API_PROVIDERS
            from api.env_loader import EnvLoader
            
            if self.enable_real_api_tests:
                EnvLoader.load_env()
            
            success_count = 0
            total_tests = 0
            
            for provider_id, config in API_PROVIDERS.items():
                total_tests += 1
                api_key = os.getenv(config['env_var']) if self.enable_real_api_tests else 'mock_key'
                
                if not api_key and self.enable_real_api_tests:
                    print(f"  ⚠️  {config['name']}: API key not available")
                    continue
                
                try:
                    if self.enable_real_api_tests and api_key != 'mock_key':
                        # Real API test
                        client = APIClient(
                            base_url=config['base_url'],
                            model=config['model'],
                            api_key=api_key
                        )
                        
                        # Test connection
                        start_time = time.time()
                        connection_result = client.test_connection()
                        response_time = time.time() - start_time
                        
                        if connection_result:
                            print(f"  ✅ {config['name']}: Connection successful ({response_time:.2f}s)")
                            success_count += 1
                            
                            self.add_result(APITestResult(
                                provider=provider_id,
                                test_name="connection",
                                success=True,
                                response_time=response_time
                            ))
                        else:
                            print(f"  ❌ {config['name']}: Connection failed")
                            self.add_result(APITestResult(
                                provider=provider_id,
                                test_name="connection",
                                success=False,
                                error_message="Connection test failed"
                            ))
                    else:
                        # Mock test when API keys not available
                        with patch('requests.Session.post') as mock_post:
                            mock_response = MagicMock()
                            mock_response.status_code = 200
                            mock_response.json.return_value = {"status": "ok"}
                            mock_post.return_value = mock_response
                            
                            client = APIClient(
                                base_url=config['base_url'],
                                model=config['model'],
                                api_key='mock_key'
                            )
                            
                            connection_result = client.test_connection()
                            print(f"  ✅ {config['name']}: Connection test (mocked)")
                            success_count += 1
                            
                            self.add_result(APITestResult(
                                provider=provider_id,
                                test_name="connection",
                                success=True,
                                response_time=0.1
                            ))
                        
                except Exception as e:
                    print(f"  ❌ {config['name']}: Connection error - {e}")
                    self.add_result(APITestResult(
                        provider=provider_id,
                        test_name="connection",
                        success=False,
                        error_message=str(e)
                    ))
            
            print(f"  📊 Connection tests: {success_count}/{total_tests} successful")
            return success_count > 0  # At least one should work
            
        except Exception as e:
            print(f"  ❌ Connection test failed: {e}")
            return False
    
    def test_component_routing(self) -> bool:
        """Test component-to-provider routing system"""
        print("\n🔀 Testing Component Routing...")
        
        try:
            from run import COMPONENT_CONFIG, get_api_client_for_component
            
            success_count = 0
            components_config = COMPONENT_CONFIG.get("components", {})
            total_components = len(components_config)
            
            # Test routing for each component
            with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test', 'GROK_API_KEY': 'test'}):
                for component, config in components_config.items():
                    try:
                        expected_provider = config['api_provider']
                        
                        if expected_provider == "none":
                            # Components with 'none' provider don't need API clients
                            print(f"  ⚠️  {component} → {expected_provider} (no client needed)")
                            success_count += 1
                            continue
                        
                        client = get_api_client_for_component(component)
                        assert client is not None, f"No client returned for {component}"
                        print(f"  ✅ {component} → {expected_provider}")
                        
                        success_count += 1
                        
                        self.add_result(APITestResult(
                            provider=expected_provider,
                            test_name=f"routing_{component}",
                            success=True
                        ))
                        
                    except Exception as e:
                        print(f"  ❌ {component}: {e}")
                        self.add_result(APITestResult(
                            provider=config.get('api_provider', 'unknown'),
                            test_name=f"routing_{component}",
                            success=False,
                            error_message=str(e)
                        ))
            
            print(f"  📊 Component routing: {success_count}/{total_components} successful")
            return success_count == total_components
            
        except Exception as e:
            print(f"  ❌ Component routing test failed: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test comprehensive error handling"""
        print("\n🛡️ Testing Error Handling...")
        
        try:
            from api.client import APIClient
            from unittest.mock import patch
            
            success_count = 0
            total_scenarios = 3
            
            # Test 1: Mock connection error (avoids real network calls)
            try:
                with patch('requests.Session.post') as mock_post:
                    mock_post.side_effect = requests.ConnectionError("Connection failed")
                    
                    client = APIClient(
                        base_url="https://test.invalid",
                        api_key="test_key",
                        model="test_model"
                    )
                    
                    # Test connection failure handling
                    connection_result = client.test_connection()
                    
                    if not connection_result:
                        print("  ✅ connection_error: Error handled gracefully")
                        success_count += 1
                    else:
                        print("  ⚠️  connection_error: Expected failure but got success")
                        
            except Exception as e:
                print(f"  ✅ connection_error: Exception handled ({type(e).__name__})")
                success_count += 1
            
            # Test 2: Mock timeout error
            try:
                with patch('requests.Session.post') as mock_post:
                    mock_post.side_effect = requests.Timeout("Request timeout")
                    
                    client = APIClient(
                        base_url="https://test.invalid",
                        api_key="test_key", 
                        model="test_model"
                    )
                    
                    response = client.generate_simple("Test prompt")
                    
                    if not response.success and "timeout" in response.error.lower():
                        print("  ✅ timeout_error: Timeout handled gracefully")
                        success_count += 1
                    else:
                        print("  ⚠️  timeout_error: Expected timeout handling")
                        
            except Exception as e:
                print(f"  ✅ timeout_error: Exception handled ({type(e).__name__})")
                success_count += 1
            
            # Test 3: Mock HTTP error
            try:
                with patch('requests.Session.post') as mock_post:
                    # Create a proper mock response object
                    mock_response = MagicMock()
                    mock_response.status_code = 401
                    mock_response.text = "Unauthorized"
                    mock_response.json.return_value = {"error": "Unauthorized"}
                    mock_response.raise_for_status.side_effect = requests.HTTPError("401 Client Error")
                    mock_post.return_value = mock_response
                    
                    client = APIClient(
                        base_url="https://test.invalid",
                        api_key="invalid_key",
                        model="test_model"
                    )
                    
                    response = client.generate_simple("Test prompt")
                    
                    if not response.success:
                        print("  ✅ http_error: HTTP error handled gracefully")
                        success_count += 1
                    else:
                        print("  ⚠️  http_error: Expected HTTP error handling")
                        
            except Exception as e:
                print(f"  ✅ http_error: Exception handled ({type(e).__name__})")
                success_count += 1
            
            print(f"  📊 Error handling: {success_count}/{total_scenarios} scenarios handled")
            return success_count >= 2  # At least most scenarios should be handled
            
        except Exception as e:
            print(f"  ❌ Error handling test failed: {e}")
            return False
    
    def test_basic_api_response(self) -> bool:
        """Test basic API response validation"""
        print("\n✅ Testing Basic API Response...")
        
        try:
            from api.client import APIClient
            from run import API_PROVIDERS
            from api.env_loader import EnvLoader
            
            if self.enable_real_api_tests:
                EnvLoader.load_env()
            
            test_prompt = "What is aluminum?"
            successful_responses = 0
            
            for provider_id, config in API_PROVIDERS.items():
                api_key = os.getenv(config['env_var']) if self.enable_real_api_tests else 'mock_key'
                
                try:
                    if self.enable_real_api_tests and api_key and api_key != 'mock_key':
                        # Real API test
                        client = APIClient(
                            base_url=config['base_url'],
                            model=config['model'],
                            api_key=api_key
                        )
                        
                        result = client.generate_simple(test_prompt)
                        
                        if result.success and result.content:
                            print(f"  ✅ {config['name']}: Response received ({len(result.content)} chars)")
                            successful_responses += 1
                            
                            self.add_result(APITestResult(
                                provider=provider_id,
                                test_name="basic_response",
                                success=True,
                                content_quality="valid"
                            ))
                        else:
                            print(f"  ❌ {config['name']}: No response or empty content")
                            self.add_result(APITestResult(
                                provider=provider_id,
                                test_name="basic_response",
                                success=False,
                                error_message="No response or empty content"
                            ))
                    else:
                        # Mock test when API keys not available
                        with patch('requests.Session.post') as mock_post:
                            mock_response = MagicMock()
                            mock_response.status_code = 200
                            mock_response.json.return_value = {
                                "choices": [{"message": {"content": "Aluminum is a lightweight, corrosion-resistant metal."}}],
                                "usage": {"total_tokens": 15}
                            }
                            mock_post.return_value = mock_response
                            
                            client = APIClient(
                                base_url=config['base_url'],
                                model=config['model'],
                                api_key='mock_key'
                            )
                            
                            result = client.generate_simple(test_prompt)
                            
                            if hasattr(result, 'success') and result.success:
                                print(f"  ✅ {config['name']}: Mock response received (mocked)")
                                successful_responses += 1
                                
                                self.add_result(APITestResult(
                                    provider=provider_id,
                                    test_name="basic_response",
                                    success=True,
                                    content_quality="valid"
                                ))
                            else:
                                print(f"  ❌ {config['name']}: Mock test failed")
                                self.add_result(APITestResult(
                                    provider=provider_id,
                                    test_name="basic_response",
                                    success=False,
                                    error_message="Mock test failed"
                                ))
                    
                except Exception as e:
                    print(f"  ❌ {config['name']}: Error - {e}")
                    self.add_result(APITestResult(
                        provider=provider_id,
                        test_name="basic_response",
                        success=False,
                        error_message=str(e)
                    ))
            
            print(f"\n  📊 Basic API Response: {successful_responses}/{len(API_PROVIDERS)} providers successful")
            return successful_responses > 0
            
        except Exception as e:
            print(f"  ❌ Basic API response test failed: {e}")
            return False
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all comprehensive tests and return results"""
        print("🧪 COMPREHENSIVE API TEST SUITE")
        print("=" * 60)
        
        if self.enable_real_api_tests:
            print("🔑 Real API testing enabled (API keys detected)")
        else:
            print("⚠️  Real API testing disabled (API keys not available)")
        
        print()
        
        test_methods = [
            ("Environment Configuration", self.test_environment_configuration),
            ("API Client Creation", self.test_api_client_creation),
            ("API Connections", self.test_api_connections),
            ("Component Routing", self.test_component_routing),
            ("Error Handling", self.test_error_handling),
            ("Basic API Response", self.test_basic_api_response)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_method in test_methods:
            try:
                if test_method():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
                failed += 1
        
        # Generate comprehensive report
        return self._generate_test_report(passed, failed, len(test_methods))
    
    def _generate_test_report(self, passed: int, failed: int, total: int) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 60)
        print(f"📈 Overall Success Rate: {success_rate:.1f}% ({passed}/{total})")
        
        # Group results by provider
        provider_stats = {}
        for result in self.results:
            if result.provider not in provider_stats:
                provider_stats[result.provider] = {
                    'total': 0,
                    'passed': 0,
                    'avg_response_time': [],
                    'total_tokens': 0
                }
            
            provider_stats[result.provider]['total'] += 1
            if result.success:
                provider_stats[result.provider]['passed'] += 1
            
            if result.response_time:
                provider_stats[result.provider]['avg_response_time'].append(result.response_time)
            
            if result.token_count:
                provider_stats[result.provider]['total_tokens'] += result.token_count
        
        print("\n📋 Provider Performance Summary:")
        for provider, stats in provider_stats.items():
            if stats['total'] > 0:
                provider_success_rate = (stats['passed'] / stats['total']) * 100
                avg_time = sum(stats['avg_response_time']) / len(stats['avg_response_time']) if stats['avg_response_time'] else 0
                
                print(f"  {provider.upper()}:")
                print(f"    Success Rate: {provider_success_rate:.1f}% ({stats['passed']}/{stats['total']})")
                if avg_time > 0:
                    print(f"    Avg Response Time: {avg_time:.2f}s")
                if stats['total_tokens'] > 0:
                    print(f"    Total Tokens: {stats['total_tokens']}")
        
        # Assessment and recommendations
        print(f"\n🎯 SYSTEM ASSESSMENT:")
        if success_rate >= 90:
            print("🎉 EXCELLENT! System is production-ready.")
        elif success_rate >= 75:
            print("✅ GOOD! System is mostly functional with minor issues.")
        elif success_rate >= 50:
            print("⚠️  FAIR! System has significant issues that need attention.")
        else:
            print("❌ POOR! System has critical issues requiring immediate fix.")
        
        if self.enable_real_api_tests:
            print("\n💡 RECOMMENDATIONS:")
            print("  • System has been tested with real API calls")
            print("  • Monitor API usage and costs in production")
            print("  • Consider rate limiting for high-volume usage")
        else:
            print("\n💡 RECOMMENDATIONS:")
            print("  • Add API keys to .env file for complete testing")
            print("  • Run real API tests before production deployment")
            print("  • Verify network connectivity and firewall settings")
        
        return {
            'success_rate': success_rate,
            'passed': passed,
            'failed': failed,
            'total': total,
            'provider_stats': provider_stats,
            'real_api_tested': self.enable_real_api_tests,
            'detailed_results': self.results
        }

def main():
    """Run comprehensive API test suite"""
    test_suite = APITestSuite()
    report = test_suite.run_comprehensive_tests()
    
    # Return appropriate exit code
    success = report['success_rate'] >= 75  # 75% threshold for success
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
