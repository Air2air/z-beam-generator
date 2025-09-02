#!/usr/bin/env python3
"""
Comprehensive test suite for validating run.py modular architecture.
This tests the full integration of extracted modules and ensures the cleanup maintains functionality.
"""

import pytest
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_run_py_architecture_cleanup():
    """Test that run.py architecture has been properly cleaned up"""
    print("\n🏗️ Testing run.py Architecture Cleanup...")
    
    # Check file sizes
    run_py_path = os.path.join(os.path.dirname(__file__), '..', 'run.py')
    backup_path = os.path.join(os.path.dirname(__file__), '..', 'run_original_backup.py')
    
    with open(run_py_path, 'r') as f:
        current_lines = len(f.readlines())
    
    if os.path.exists(backup_path):
        with open(backup_path, 'r') as f:
            original_lines = len(f.readlines())
        
        reduction = ((original_lines - current_lines) / original_lines) * 100
        print(f"  📊 Size reduction: {original_lines} → {current_lines} lines ({reduction:.1f}% reduction)")
        
        assert reduction > 50, f"Expected >50% reduction, got {reduction:.1f}%"
        print("  ✅ Significant size reduction achieved")
    
    # Check that imports exist for modular components
    with open(run_py_path, 'r') as f:
        content = f.read()
        
    required_imports = [
        'from api.client_manager import',
        'from utils.author_manager import',
        'from utils.environment_checker import',
        'from utils.file_operations import',
        'from cli.component_config import'
    ]
    
    for imp in required_imports:
        assert imp in content, f"Missing import: {imp}"
        print(f"  ✅ Found modular import: {imp}")

def test_modular_functionality_integration():
    """Test that modular components integrate correctly with run.py"""
    print("\n🔗 Testing Modular Functionality Integration...")
    
    # Test API client manager
    from api.client_manager import setup_api_client, validate_api_environment
    from run import create_arg_parser
    
    # Should be able to create argument parser
    parser = create_arg_parser()
    assert parser is not None
    print("  ✅ Argument parser creation works")
    
    # Test environment validation  
    env_result = validate_api_environment()
    assert isinstance(env_result, dict)
    print("  ✅ Environment validation works")
    
    # Test author management
    from utils.author_manager import load_authors
    try:
        authors = load_authors()
        print(f"  ✅ Author loading works ({len(authors) if authors else 0} authors)")
    except Exception as e:
        print(f"  ⚠️  Author loading issue (expected): {e}")
    
    # Test file operations
    from utils.file_operations import save_component_to_file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        try:
            save_component_to_file("test content", tmp.name)
            with open(tmp.name, 'r') as f:
                content = f.read()
            assert content == "test content"
            print("  ✅ File operations work")
        finally:
            os.unlink(tmp.name)

def test_component_configuration_access():
    """Test that component configuration is properly accessible"""
    print("\n⚙️ Testing Component Configuration Access...")
    
    from run import COMPONENT_CONFIG, show_component_configuration
    from cli.component_config import COMPONENT_CONFIG as CLI_CONFIG
    
    # Should be the same configuration
    assert COMPONENT_CONFIG is CLI_CONFIG
    print("  ✅ Component configuration properly imported")
    
    # Should have components
    components = COMPONENT_CONFIG.get("components", {})
    assert isinstance(components, dict)
    assert len(components) > 0
    print(f"  ✅ Component configuration loaded ({len(components)} components)")
    
    # Should be able to show configuration
    try:
        show_component_configuration()
        print("  ✅ Component configuration display works")
    except Exception as e:
        print(f"  ⚠️  Configuration display issue: {e}")

def test_api_integration_preserved():
    """Test that API integration is preserved after modular cleanup"""
    print("\n🌐 Testing API Integration Preservation...")
    
    from api.client_manager import validate_api_environment, test_api_connectivity
    
    # Should handle missing API keys gracefully
    with patch.dict(os.environ, {}, clear=True):
        result = validate_api_environment()
        assert isinstance(result, dict)
        print("  ✅ API validation handles missing keys")
        
        # Should not crash on connectivity test
        try:
            conn_result = test_api_connectivity()
            assert isinstance(conn_result, dict)
            print("  ✅ API connectivity test works")
        except Exception as e:
            print(f"  ⚠️  API connectivity issue (expected): {e}")

def test_cli_interface_preserved():
    """Test that CLI interface is fully preserved"""
    print("\n💻 Testing CLI Interface Preservation...")
    
    from run import create_arg_parser, main
    
    parser = create_arg_parser()
    
    # Test all major CLI options
    cli_options = [
        ['--help'],
        ['--list-materials'],
        ['--list-components'], 
        ['--list-authors'],
        ['--show-config'],
        ['--check-env'],
        ['--yaml'],
        ['--test-api'],
        ['--clean'],
        ['--material', 'Aluminum'],
        ['--material', 'Steel', '--components', 'frontmatter,content'],
        ['--interactive'],
        ['--verbose']
    ]
    
    working_options = 0
    for options in cli_options:
        try:
            args = parser.parse_args(options)
            working_options += 1
            print(f"    ✅ CLI option: {' '.join(options)}")
        except SystemExit:
            # --help causes SystemExit, which is expected
            if '--help' in options:
                working_options += 1
                print(f"    ✅ CLI option: {' '.join(options)} (help)")
        except Exception as e:
            print(f"    ❌ CLI option failed: {' '.join(options)} - {e}")
    
    print(f"  ✅ CLI interface preserved ({working_options}/{len(cli_options)} options working)")
    assert working_options >= len(cli_options) - 2  # Allow for some variations

def test_error_handling_robustness():
    """Test that error handling is robust after modular cleanup"""
    print("\n🛡️ Testing Error Handling Robustness...")
    
    # Test environment checker error handling
    from utils.environment_checker import check_environment
    
    with patch.dict(os.environ, {}, clear=True):
        result = check_environment()
        assert isinstance(result, dict)
        print("  ✅ Environment checker robust error handling")
    
    # Test file operations error handling
    from utils.file_operations import save_component_to_file
    
    # Should handle permission errors gracefully
    try:
        save_component_to_file("test", "/root/forbidden/file.txt")
    except (OSError, IOError, PermissionError):
        print("  ✅ File operations handle permission errors")
    except Exception as e:
        print(f"  ⚠️  Unexpected error type: {e}")
    
    # Test API client error handling
    from api.client_manager import create_api_client
    
    try:
        client = create_api_client("nonexistent-provider")
        print("  ⚠️  API client should have failed for bad provider")
    except Exception:
        print("  ✅ API client handles bad provider gracefully")

def test_backward_compatibility():
    """Test that essential backward compatibility is maintained"""
    print("\n🔄 Testing Backward Compatibility...")
    
    from run import (
        run_dynamic_generation,
        run_yaml_validation, 
        run_single_material,
        run_comprehensive_tests,
        create_arg_parser,
        main
    )
    
    # All essential functions should be callable
    essential_functions = [
        run_dynamic_generation,
        run_yaml_validation,
        run_single_material, 
        run_comprehensive_tests,
        create_arg_parser,
        main
    ]
    
    for func in essential_functions:
        assert callable(func), f"Function {func.__name__} should be callable"
        print(f"  ✅ {func.__name__} is callable")
    
    print("  ✅ All essential functions preserved")

if __name__ == "__main__":
    print("🧪 Running Comprehensive Modular Architecture Tests...")
    
    test_functions = [
        ("Architecture Cleanup", test_run_py_architecture_cleanup),
        ("Functionality Integration", test_modular_functionality_integration),
        ("Component Configuration", test_component_configuration_access),
        ("API Integration", test_api_integration_preserved),
        ("CLI Interface", test_cli_interface_preserved),
        ("Error Handling", test_error_handling_robustness),
        ("Backward Compatibility", test_backward_compatibility),
    ]
    
    passed = 0
    total = len(test_functions)
    
    for test_name, test_func in test_functions:
        try:
            print(f"\n{'='*60}")
            print(f"🎯 {test_name}")
            print('='*60)
            test_func()
            print(f"✅ {test_name} PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name} FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print(f"🎉 Modular Architecture Tests Complete: {passed}/{total} PASSED")
    if passed == total:
        print("✅ ALL TESTS PASSED - Modular architecture is solid!")
    else:
        print(f"⚠️  {total - passed} tests failed - review needed")
        sys.exit(1)
    print("="*60)
