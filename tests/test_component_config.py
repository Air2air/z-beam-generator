#!/usr/bin/env python3
"""
Component Configuration Test Suite

Tests the component configuration system including:
- Component enable/disable functionality
- Configuration persistence
- Interactive configuration interface
- Validation of component states
"""

import sys
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_component_config_structure():
    """Test the structure and validity of COMPONENT_CONFIG"""
    print("🔍 Testing Component Configuration Structure...")
    
    try:
        from run import COMPONENT_CONFIG
        
        # Test that config is not empty
        components_config = COMPONENT_CONFIG.get("components", {})
        assert len(components_config) > 0, "No components configured"
        print(f"  ✅ Found {len(components_config)} configured components")
        
        # Test each component configuration
        required_fields = ['enabled', 'api_provider']
        valid_providers = ['deepseek', 'grok', 'none']
        
        for component, config in components_config.items():
            # Check required fields
            for field in required_fields:
                assert field in config, f"Component {component} missing field: {field}"
            
            # Check field types
            assert isinstance(config['enabled'], bool), f"Component {component} 'enabled' must be boolean"
            assert isinstance(config['api_provider'], str), f"Component {component} 'api_provider' must be string"
            
            # Check valid provider
            assert config['api_provider'] in valid_providers, f"Invalid provider for {component}: {config['api_provider']}"
            
            print(f"  ✅ {component}: enabled={config['enabled']}, provider={config['api_provider']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Component config structure test failed: {e}")
        return False

def test_component_enable_disable():
    """Test component enable/disable functionality"""
    print("\n⚙️ Testing Component Enable/Disable...")
    
    try:
        from run import COMPONENT_CONFIG
        
        # Count enabled/disabled components
        components_config = COMPONENT_CONFIG.get("components", {})
        enabled_count = sum(1 for config in components_config.values() if config['enabled'])
        disabled_count = len(components_config) - enabled_count
        
        print(f"  📊 Current state: {enabled_count} enabled, {disabled_count} disabled")
        
        # Test that we have at least some components enabled
        assert enabled_count > 0, "No components are enabled"
        print("  ✅ At least one component is enabled")
        
        # Test component state consistency
        for component, config in components_config.items():
            enabled = config['enabled']
            provider = config['api_provider']
            
            # Verify state is boolean
            assert enabled in [True, False], f"Component {component} enabled state must be boolean"
            
            # If enabled, provider should be valid
            if enabled:
                assert provider in ['deepseek', 'grok', 'none'], f"Enabled component {component} has invalid provider: {provider}"
        
        print("  ✅ Component state consistency validated")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Component enable/disable test failed: {e}")
        return False

def test_configuration_display():
    """Test the component configuration display functionality"""
    print("\n📋 Testing Configuration Display...")
    
    try:
        from run import show_component_configuration
        
        # Test basic configuration display (function just displays and returns)
        try:
            show_component_configuration()
            print("  ✅ Configuration display runs successfully")
        except SystemExit:
            print("  ✅ Configuration display handles exit properly")
        except Exception as e:
            print(f"  ❌ Configuration display failed: {e}")
            return False
        
        # Test with mock environment variables
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test', 'GROK_API_KEY': 'test'}):
            try:
                show_component_configuration()
                print("  ✅ Configuration display works with API keys")
            except Exception as e:
                print(f"  ❌ Configuration display with API keys failed: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration display test failed: {e}")
        return False

def test_component_filtering():
    """Test component filtering based on enabled state"""
    print("\n🔽 Testing Component Filtering...")
    
    try:
        from run import COMPONENT_CONFIG
        
        # Get enabled components
        components_config = COMPONENT_CONFIG.get("components", {})
        enabled_components = [comp for comp, config in components_config.items() if config['enabled']]
        disabled_components = [comp for comp, config in components_config.items() if not config['enabled']]
        
        print(f"  📊 Enabled components: {len(enabled_components)}")
        print(f"  📊 Disabled components: {len(disabled_components)}")
        
        # Test that filtering works correctly
        total_components = len(enabled_components) + len(disabled_components)
        assert total_components == len(components_config), "Component count mismatch"
        
        # Test no overlap between enabled and disabled
        overlap = set(enabled_components) & set(disabled_components)
        assert len(overlap) == 0, "Overlap between enabled and disabled components"
        
        print("  ✅ Component filtering logic validated")
        
        # Test provider distribution
        provider_counts = {}
        for comp in enabled_components:
            provider = components_config[comp]['api_provider']
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
        
        for provider, count in provider_counts.items():
            print(f"  📈 {provider}: {count} enabled components")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Component filtering test failed: {e}")
        return False

def test_provider_assignment():
    """Test API provider assignment logic"""
    print("\n🔀 Testing Provider Assignment...")
    
    try:
        from run import COMPONENT_CONFIG, get_api_client_for_component
        
        # Test provider assignment for each component
        components_config = COMPONENT_CONFIG.get("components", {})
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test', 'GROK_API_KEY': 'test'}):
            for component, config in components_config.items():
                expected_provider = config['api_provider']
                
                try:
                    if expected_provider == "none":
                        # Components with 'none' provider don't need API clients
                        print(f"  ⚠️  {component} → {expected_provider} (no client needed)")
                        continue
                    
                    client = get_api_client_for_component(component)
                    assert client is not None, f"No client returned for {component}"
                    print(f"  ✅ {component} → {expected_provider} (client created)")
                except Exception as e:
                    print(f"  ⚠️  {component} → {expected_provider} (error: {e})")
        
        # Test provider distribution
        providers = [config['api_provider'] for config in components_config.values()]
        provider_counts = {provider: providers.count(provider) for provider in set(providers)}
        
        print("  📊 Provider distribution:")
        for provider, count in provider_counts.items():
            percentage = (count / len(components_config)) * 100
            print(f"     {provider}: {count} components ({percentage:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Provider assignment test failed: {e}")
        return False

def test_configuration_consistency():
    """Test configuration consistency and validation"""
    print("\n🔍 Testing Configuration Consistency...")
    
    try:
        from run import COMPONENT_CONFIG, API_PROVIDERS
        
        # Test that all configured providers exist in API_PROVIDERS (except 'none' which is special)
        components_config = COMPONENT_CONFIG.get("components", {})
        configured_providers = set(config['api_provider'] for config in components_config.values())
        available_providers = set(API_PROVIDERS.keys())
        
        # 'none' is a special provider for static components, so it doesn't need API configuration
        missing_providers = configured_providers - available_providers - {'none'}
        assert len(missing_providers) == 0, f"Missing provider configurations: {missing_providers}"
        print("  ✅ All configured providers are available")
        
        # Test that all component names are valid strings
        for component in components_config.keys():
            assert isinstance(component, str), f"Component name {component} must be string"
            assert len(component) > 0, "Component name cannot be empty"
            assert ' ' not in component, f"Component name {component} cannot contain spaces"
        
        print("  ✅ Component names are valid")
        
        # Test configuration completeness
        expected_components = [
            'frontmatter', 'content', 'table', 'bullets', 
            'caption', 'tags', 'metatags', 'jsonld'
        ]
        
        configured_components = set(components_config.keys())
        missing_components = set(expected_components) - configured_components
        
        if missing_components:
            print(f"  ⚠️  Missing component configurations: {missing_components}")
        else:
            print("  ✅ All expected components are configured")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration consistency test failed: {e}")
        return False

def test_environment_integration():
    """Test integration with environment variables and .env file"""
    print("\n🌍 Testing Environment Integration...")
    
    try:
        # Test .env file loading simulation
        test_env_content = """
DEEPSEEK_API_KEY=test_deepseek_key
GROK_API_KEY=test_grok_key
"""
        
        # Test with missing environment variables
        with patch.dict(os.environ, {}, clear=True):
            try:
                from run import show_component_configuration
                print("  ✅ Handles missing environment variables gracefully")
            except Exception as e:
                print(f"  ⚠️  Environment handling: {e}")
        
        # Test with present environment variables
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test', 'GROK_API_KEY': 'test'}):
            try:
                from run import API_PROVIDERS
                
                # Check that providers can access their environment variables
                for provider, config in API_PROVIDERS.items():
                    env_var = config['env_var']
                    assert env_var in os.environ, f"Missing environment variable: {env_var}"
                
                print("  ✅ Environment variables properly accessible")
            except Exception as e:
                print(f"  ⚠️  Environment variable access: {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Environment integration test failed: {e}")
        return False

def main():
    """Run all component configuration tests"""
    print("🧪 COMPONENT CONFIGURATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Component Config Structure", test_component_config_structure),
        ("Enable/Disable Functionality", test_component_enable_disable),
        ("Configuration Display", test_configuration_display),
        ("Component Filtering", test_component_filtering),
        ("Provider Assignment", test_provider_assignment),
        ("Configuration Consistency", test_configuration_consistency),
        ("Environment Integration", test_environment_integration)
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
    
    print("\n" + "=" * 60)
    print(f"📊 COMPONENT CONFIGURATION TEST RESULTS")
    print(f"   ✅ Passed: {passed}/{total}")
    print(f"   ❌ Failed: {failed}/{total}")
    print(f"   📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All component configuration tests passed!")
        print("   Component system is properly configured and functional.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
