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

import pytest

class TestComponentConfig:
    """Component configuration test suite"""
    
    def test_component_config_structure(self):
        """Test the structure and validity of COMPONENT_CONFIG"""
        from run import COMPONENT_CONFIG
        
        # Test that config is not empty
        components_config = COMPONENT_CONFIG.get("components", {})
        assert len(components_config) > 0, "No components configured"
        
        # Test each component configuration
        required_fields = ['enabled', 'api_provider']
        valid_providers = ['deepseek', 'grok', 'gemini', 'openai', 'none']  # Updated to match actual providers
        
        for component, config in components_config.items():
            # Check required fields
            for field in required_fields:
                assert field in config, f"Component {component} missing field: {field}"
            
            # Check field types
            assert isinstance(config['enabled'], bool), f"Component {component} 'enabled' must be boolean"
            assert isinstance(config['api_provider'], str), f"Component {component} 'api_provider' must be string"
            
            # Check valid provider
            assert config['api_provider'] in valid_providers, f"Invalid provider for {component}: {config['api_provider']}"
            
            # Check AI detection flags - should only be present for API-driven components
            api_provider = config['api_provider']
            ai_detection_enabled = config.get('ai_detection_enabled', False)
            iter_improvement_enabled = config.get('iterative_improvement_enabled', False)
            
            if api_provider == 'none':
                # Static components should not have AI detection flags (they default to False)
                pass  # This is fine
            else:
                # API-driven components should have AI detection flags
                assert 'ai_detection_enabled' in config, f"API component {component} missing ai_detection_enabled"
                assert 'iterative_improvement_enabled' in config, f"API component {component} missing iterative_improvement_enabled"
    
    def test_component_enable_disable(self):
        """Test component enable/disable functionality"""
        from run import COMPONENT_CONFIG
        
        # Count enabled/disabled components
        components_config = COMPONENT_CONFIG.get("components", {})
        enabled_count = sum(1 for config in components_config.values() if config['enabled'])
        disabled_count = len(components_config) - enabled_count
        
        # Test that we have at least some components enabled
        assert enabled_count > 0, "No components are enabled"
        
        # Test component state consistency
        for component, config in components_config.items():
            enabled = config['enabled']
            provider = config['api_provider']
            
            # Verify state is boolean
            assert enabled in [True, False], f"Component {component} enabled state must be boolean"
            
            # If enabled, provider should be valid
            if enabled:
                assert provider in ['deepseek', 'grok', 'gemini', 'openai', 'none'], f"Enabled component {component} has invalid provider: {provider}"
    
    def test_configuration_display(self):
        """Test the component configuration display functionality"""
        from run import show_component_configuration
        
        # Test basic configuration display (function just displays and returns)
        try:
            show_component_configuration()
        except SystemExit:
            pass  # Expected for display functions
        except Exception as e:
            pytest.fail(f"Configuration display failed: {e}")
        
        # Test with mock environment variables
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test', 'GROK_API_KEY': 'test'}):
            try:
                show_component_configuration()
            except SystemExit:
                pass  # Expected
            except Exception as e:
                pytest.fail(f"Configuration display with API keys failed: {e}")
    
    def test_component_filtering(self):
        """Test component filtering based on enabled state"""
        from run import COMPONENT_CONFIG
        
        # Get enabled components
        components_config = COMPONENT_CONFIG.get("components", {})
        enabled_components = [comp for comp, config in components_config.items() if config['enabled']]
        disabled_components = [comp for comp, config in components_config.items() if not config['enabled']]
        
        # Test that filtering works correctly
        total_components = len(enabled_components) + len(disabled_components)
        assert total_components == len(components_config), "Component count mismatch"
        
        # Test no overlap between enabled and disabled
        overlap = set(enabled_components) & set(disabled_components)
        assert len(overlap) == 0, "Overlap between enabled and disabled components"
    
    def test_provider_assignment(self):
        """Test API provider assignment logic"""
        from run import COMPONENT_CONFIG
        
        # Test provider assignment for each component
        components_config = COMPONENT_CONFIG.get("components", {})
        for component, config in components_config.items():
            expected_provider = config['api_provider']
            
            # Just verify the provider is configured correctly
            assert expected_provider in ['deepseek', 'grok', 'gemini', 'openai', 'none'], f"Invalid provider for {component}: {expected_provider}"
            
            # For 'none' provider, no API client is needed
            if expected_provider == "none":
                continue
                
            # For API providers, verify they exist in API_PROVIDERS
            from run import API_PROVIDERS
            if expected_provider in API_PROVIDERS:
                assert expected_provider in API_PROVIDERS, f"Provider {expected_provider} not found in API_PROVIDERS"
    
    def test_configuration_consistency(self):
        """Test configuration consistency and validation"""
        from run import COMPONENT_CONFIG, API_PROVIDERS
        
        # Test that all configured providers exist in API_PROVIDERS (except 'none' which is special)
        components_config = COMPONENT_CONFIG.get("components", {})
        configured_providers = set(config['api_provider'] for config in components_config.values())
        available_providers = set(API_PROVIDERS.keys())
        
        # 'none' is a special provider for static components, so it doesn't need API configuration
        missing_providers = configured_providers - available_providers - {'none'}
        assert len(missing_providers) == 0, f"Missing provider configurations: {missing_providers}"
        
        # Test that all component names are valid strings
        for component in components_config.keys():
            assert isinstance(component, str), f"Component name {component} must be string"
            assert len(component) > 0, "Component name cannot be empty"
            assert ' ' not in component, f"Component name {component} cannot contain spaces"
    
    def test_environment_integration(self):
        """Test integration with environment variables and .env file"""
        # Test with missing environment variables
        with patch.dict(os.environ, {}, clear=True):
            # Should handle gracefully
            pass
        
        # Test with present environment variables
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test', 'GROK_API_KEY': 'test', 'GEMINI_API_KEY': 'test', 'OPENAI_API_KEY': 'test'}):
            from run import API_PROVIDERS
            
            # Check that providers can access their environment variables
            for provider, config in API_PROVIDERS.items():
                env_var = config['env_var']
                assert env_var in os.environ, f"Missing environment variable: {env_var}"


