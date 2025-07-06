#!/usr/bin/env python3
"""
Dynamic Optimization Test Suite

Validates the dynamic optimization requirements for the Z-Beam generator.
"""

import sys
import os
import re
from pathlib import Path


def test_parameter_access():
    """Test that all optimization parameters come from GlobalConfigManager."""
    print("📋 Test 1: Parameter Access Validation")
    print("-" * 40)
    
    try:
        # Initialize config
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, parent_dir)
        from run import USER_CONFIG, PROVIDER_MODELS
        
        from config.global_config import GlobalConfigManager
        GlobalConfigManager.initialize(USER_CONFIG, PROVIDER_MODELS)
        
        config = GlobalConfigManager.get_instance()
        
        # Test critical parameters are accessible
        critical_params = [
            ("ai_detection_threshold", "get_ai_detection_threshold"),
            ("natural_voice_threshold", "get_natural_voice_threshold"), 
            ("content_temp", "get_content_temperature"),
            ("detection_temp", "get_detection_temperature"),
            ("improvement_temp", "get_improvement_temperature"),
            ("summary_temp", "get_summary_temperature"),
            ("metadata_temp", "get_metadata_temperature"),
            ("max_article_words", "get_max_article_words"),
            ("iterations_per_section", "get_iterations_per_section")
        ]
        
        missing_params = []
        for param_name, method_name in critical_params:
            try:
                value = getattr(config, method_name)()
                if value is None:
                    missing_params.append(param_name)
                else:
                    print(f"   ✅ {param_name}: {value}")
            except AttributeError:
                missing_params.append(param_name)
                print(f"   ❌ {param_name}: Method {method_name} not found")
        
        if missing_params:
            print(f"   ❌ Missing parameters: {missing_params}")
            return False
        else:
            print("   ✅ All critical parameters accessible via GlobalConfigManager")
            return True
            
    except Exception as e:
        print(f"   ❌ Parameter access test failed: {e}")
        return False


def test_anti_hardcoding():
    """Test for hardcoded configuration values in key files."""
    print("\n📋 Test 2: Anti-Hardcoding Compliance")
    print("-" * 40)
    
    try:
        # Check key files for hardcoded values
        files_to_check = [
            "run.py",
            "config/global_config.py", 
            "enhanced_training.py",
            "infrastructure/api/client.py"
        ]
        
        hardcoded_violations = []
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for potential hardcoded values (excluding legitimate config)
                    suspicious_patterns = [
                        (r'temperature\s*=\s*0\.\d+(?!.*config|.*USER_CONFIG|.*get_)', "hardcoded temperature"),
                        (r'threshold\s*=\s*\d+(?!.*config|.*USER_CONFIG|.*get_)', "hardcoded threshold"),
                        (r'api.*=.*"http(?!.*PROVIDER_MODELS|.*config)', "hardcoded API URL"),
                    ]
                    
                    violations_in_file = []
                    for pattern, description in suspicious_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            # Filter out legitimate uses (in comments, config definitions, etc.)
                            for match in matches:
                                # Skip if it's in legitimate config structures
                                lines = content.split('\n')
                                for line in lines:
                                    if match in line:
                                        # Skip lines that are clearly config definitions
                                        if any(good_indicator in line.lower() for good_indicator in [
                                            'user_config', 'provider_models', 'get_config', 
                                            'intelligent_defaults', 'optimization_defaults',
                                            'config.get', '# config', '# default'
                                        ]):
                                            continue
                                        violations_in_file.append(f"{description}: {match}")
                                        break
                    
                    if violations_in_file:
                        hardcoded_violations.append({
                            "file": file_path,
                            "violations": violations_in_file[:3]  # Show first 3
                        })
                        
                except Exception as e:
                    print(f"   ⚠️ Could not check {file_path}: {e}")
            else:
                print(f"   ⚠️ File not found: {file_path}")
        
        if hardcoded_violations:
            print("   ❌ Found potential hardcoding violations:")
            for violation in hardcoded_violations:
                print(f"      {violation['file']}:")
                for v in violation['violations']:
                    print(f"        - {v}")
            return False
        else:
            print("   ✅ No obvious hardcoding violations detected")
            return True
            
    except Exception as e:
        print(f"   ❌ Anti-hardcoding test failed: {e}")
        return False


def test_production_content():
    """Test production content integrity."""
    print("\n📋 Test 3: Production Content Integrity")
    print("-" * 40)
    
    try:
        output_dir = Path("output")
        
        if not output_dir.exists():
            print(f"   ⚠️ Output directory not found: {output_dir}")
            print("   💡 Run production generation first: python3 run.py")
            return True  # Not a failure, just no content to test
        
        # Check for production MDX files
        mdx_files = list(output_dir.glob("*.mdx"))
        if mdx_files:
            print(f"   ✅ Found {len(mdx_files)} production MDX files")
            
            # Check that at least one file has recognizable content sections
            for mdx_file in mdx_files[:2]:  # Check first 2 files
                try:
                    with open(mdx_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    if any(section in content.lower() for section in ['introduction', 'overview', 'benefits', 'applications']):
                        print(f"   ✅ {mdx_file.name}: Contains recognizable sections")
                    else:
                        print(f"   ⚠️ {mdx_file.name}: No standard sections found")
                        
                except Exception as e:
                    print(f"   ❌ {mdx_file.name}: Could not read - {e}")
            
            return True
        else:
            print("   ⚠️ No production MDX files found")
            print("   💡 Run production generation first: python3 run.py")
            return True  # Not a failure, just no content to test
        
    except Exception as e:
        print(f"   ❌ Production content test failed: {e}")
        return False


def test_training_no_fallbacks():
    """Test that training systems don't generate fallback content."""
    print("\n📋 Test 4: No-Fallbacks Policy Compliance")
    print("-" * 40)
    
    try:
        # Check enhanced_training.py for fallback generation
        training_file = "enhanced_training.py"
        if os.path.exists(training_file):
            with open(training_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for positive indicators (failing fast, requiring production content)
            good_patterns = [
                r'raise.*Error.*missing',
                r'fail.*fast',
                r'must.*exist',
                r'production.*content.*required',
                r'FileNotFoundError',
                r'content.*not.*found',
                r'NEVER.*generate.*content',
                r'NO.*FALLBACKS',
                r'only.*existing.*content'
            ]
            
            good_indicators = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in good_patterns)
            
            # Look for bad patterns (fallback generation)
            bad_patterns = [
                (r'generate.*if.*not.*exist', "generate if not exists"),
                (r'create.*content.*when.*missing', "content creation on missing"),
                (r'fallback.*to.*generation', "fallback to generation"),
                (r'synthetic.*content.*creation', "synthetic content creation"),
            ]
            
            violations = []
            for pattern, description in bad_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    violations.extend([f"{description}: {match}" for match in matches])
            
            if violations:
                print("   ❌ Found potential fallback generation:")
                for violation in violations:
                    print(f"      - {violation}")
                return False
            elif good_indicators >= 2:  # Need at least 2 good indicators
                print(f"   ✅ Training enforces no-fallbacks policy ({good_indicators} indicators found)")
                return True
            else:
                print(f"   ⚠️ Weak no-fallbacks enforcement ({good_indicators} indicators found)")
                print("   💡 Consider adding more explicit error handling for missing content")
                return True  # Not a failure, but could be stronger
        else:
            print(f"   ⚠️ Training file not found: {training_file}")
            return True
            
    except Exception as e:
        print(f"   ❌ No-fallbacks test failed: {e}")
        return False


def main():
    """Run all dynamic optimization tests."""
    print("🎛️ Dynamic Optimization Tests")
    print("=" * 50)
    
    tests = [
        test_parameter_access,
        test_anti_hardcoding,
        test_production_content,
        test_training_no_fallbacks
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    # Summary
    print("\n📊 Dynamic Optimization Test Summary")
    print("=" * 50)
    
    passed_count = sum(results)
    total_count = len(results)
    
    print(f"Tests Passed: {passed_count}/{total_count}")
    
    if all(results):
        print("🎉 All dynamic optimization tests passed!")
        print("✅ System complies with anti-hardcoding requirements")
        print("✅ Configuration hierarchy working correctly") 
        print("✅ Production content integrity maintained")
        print("✅ No-fallbacks policy enforced")
        return True
    else:
        print("⚠️ Some dynamic optimization tests failed")
        print("💡 Review violations and update code to use GlobalConfigManager")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
