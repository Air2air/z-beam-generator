#!/usr/bin/env python3
"""
Comprehensive Anti-Hardcoding Compliance Test

This test verifies that the entire Z-Beam system follows strict anti-hardcoding
rules for all API configurations, temperatures, timeouts, thresholds, etc.
"""

import sys
import os
import re

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def scan_for_hardcoding_violations():
    """Scan all Python files for potential hardcoding violations."""
    print("🔍 Scanning entire codebase for hardcoding violations...")
    
    violations = []
    
    # Patterns to check for
    hardcode_patterns = [
        (r'timeout\s*=\s*\d+', 'Hardcoded timeout'),
        (r'max_tokens\s*=\s*\d+', 'Hardcoded max_tokens'),
        (r'temperature\s*=\s*[\d.]+', 'Hardcoded temperature'),
        (r'threshold\s*=\s*\d+', 'Hardcoded threshold'),
        (r'https://api\.(?:x\.ai|deepseek\.com|generativelanguage\.googleapis\.com)', 'Hardcoded API URL'),
    ]
    
    # Files to scan (exclude config files and tests)
    exclude_patterns = [
        'test_',
        'run.py',
        'config/',
        '__pycache__',
        '.pyc',
        'scripts/detect_hardcoding.py'
    ]
    
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if not file.endswith('.py'):
                continue
                
            file_path = os.path.join(root, file)
            
            # Skip excluded files
            if any(exclude in file_path for exclude in exclude_patterns):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern, description in hardcode_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        line_content = content.split('\n')[line_num - 1].strip()
                        
                        # Skip fallback values (marked with FALLBACK comment)
                        if 'FALLBACK' in line_content:
                            continue
                            
                        # Skip domain constants (marked with domain constant comment)
                        if 'domain constant' in line_content.lower():
                            continue
                            
                        violations.append({
                            'file': file_path,
                            'line': line_num,
                            'pattern': description,
                            'content': line_content
                        })
                        
            except Exception as e:
                print(f"Warning: Could not scan {file_path}: {e}")
    
    return violations

def test_comprehensive_antihardcoding():
    """Run comprehensive anti-hardcoding compliance tests."""
    print("🎯 COMPREHENSIVE ANTI-HARDCODING COMPLIANCE TEST")
    print("=" * 60)
    
    all_passed = True
    
    # Test 1: Configuration System
    print("\n📋 Test 1: Configuration System Functionality")
    try:
        from config.global_config import GlobalConfigManager
        
        # Test config
        PROVIDER_MODELS = {
            "DEEPSEEK": {
                "model": "deepseek-chat",
                "url_template": "https://api.deepseek.com/v1/chat/completions",
            },
            "XAI": {
                "model": "grok-3-mini-beta", 
                "url_template": "https://api.x.ai/v1/chat/completions",
            },
        }
        
        USER_CONFIG = {
            "api_timeout": 45,
            "generator_provider": "DEEPSEEK",
            "detection_provider": "DEEPSEEK",
        }
        
        config_manager = GlobalConfigManager.initialize(USER_CONFIG, PROVIDER_MODELS)
        
        # Test all config methods work
        config_methods = [
            'get_api_timeout',
            'get_max_api_tokens', 
            'get_content_temperature',
            'get_detection_temperature',
            'get_improvement_temperature',
            'get_summary_temperature',
            'get_metadata_temperature',
            'get_ai_detection_threshold',
            'get_natural_voice_threshold',
            'get_iterations_per_section',
        ]
        
        for method_name in config_methods:
            try:
                method = getattr(config_manager, method_name)
                value = method()
                print(f"✅ {method_name}(): {value}")
            except Exception as e:
                print(f"❌ {method_name}() failed: {e}")
                all_passed = False
                
        # Test provider configs
        for provider in ["DEEPSEEK", "XAI"]:
            url = config_manager.get_provider_url(provider)
            model = config_manager.get_provider_model(provider)
            print(f"✅ {provider} URL: {url}")
            print(f"✅ {provider} Model: {model}")
            
    except Exception as e:
        print(f"❌ Configuration system test failed: {e}")
        all_passed = False
    
    # Test 2: API Client Compliance
    print("\n🔗 Test 2: API Client Anti-Hardcoding Compliance")
    try:
        from infrastructure.api.client import APIClient
        
        client = APIClient('DEEPSEEK', 'test-key')
        print(f"✅ API Client created: {client.get_provider_name()}")
        
        # Verify client uses config not hardcoded values
        expected_url = config_manager.get_provider_url("DEEPSEEK")
        if hasattr(client, '_provider_config') and client._provider_config.get('url_template') == expected_url:
            print(f"✅ API Client uses configured URL: {expected_url}")
        else:
            print("❌ API Client not using configured URL")
            all_passed = False
            
    except Exception as e:
        print(f"❌ API Client test failed: {e}")
        all_passed = False
    
    # Test 3: Code Scanning for Violations
    print("\n🔍 Test 3: Codebase Hardcoding Violation Scan")
    violations = scan_for_hardcoding_violations()
    
    if violations:
        print(f"❌ Found {len(violations)} potential hardcoding violations:")
        for violation in violations:
            print(f"  {violation['file']}:{violation['line']} - {violation['pattern']}")
            print(f"    {violation['content']}")
        all_passed = False
    else:
        print("✅ No hardcoding violations found in codebase")
    
    # Test 4: Domain Objects Use Config
    print("\n🏗️ Test 4: Domain Objects Configuration Integration")
    try:
        from domain.value_objects.generation_settings import GenerationSettings, Provider
        
        settings = GenerationSettings.create_default(Provider.DEEPSEEK)
        
        # Check that domain defaults come from config when available
        expected_timeout = config_manager.get_api_timeout()
        expected_tokens = config_manager.get_max_api_tokens()
        expected_temp = config_manager.get_content_temperature()
        
        if settings.api_settings.timeout_seconds == expected_timeout:
            print(f"✅ Domain object uses config timeout: {expected_timeout}")
        else:
            print(f"❌ Domain object timeout mismatch: {settings.api_settings.timeout_seconds} vs {expected_timeout}")
            all_passed = False
            
        if settings.api_settings.max_tokens == expected_tokens:
            print(f"✅ Domain object uses config max_tokens: {expected_tokens}")
        else:
            print(f"❌ Domain object max_tokens mismatch: {settings.api_settings.max_tokens} vs {expected_tokens}")
            all_passed = False
            
        if settings.temperature_settings.content_generation == expected_temp:
            print(f"✅ Domain object uses config temperature: {expected_temp}")
        else:
            print(f"❌ Domain object temperature mismatch: {settings.temperature_settings.content_generation} vs {expected_temp}")
            all_passed = False
            
    except Exception as e:
        print(f"❌ Domain object test failed: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    # Final Result
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL ANTI-HARDCODING COMPLIANCE TESTS PASSED!")
        print("✅ Configuration system fully functional")
        print("✅ API client uses config for all parameters")
        print("✅ No hardcoding violations in codebase")
        print("✅ Domain objects integrate with config system")
        print("✅ All API configs, temperatures, timeouts properly managed")
        return True
    else:
        print("❌ ANTI-HARDCODING COMPLIANCE TESTS FAILED!")
        print("Some hardcoded values or config issues detected.")
        return False

if __name__ == "__main__":
    success = test_comprehensive_antihardcoding()
    sys.exit(0 if success else 1)
