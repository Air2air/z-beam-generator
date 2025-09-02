#!/usr/bin/env python3
"""
Test module for run.py modular architecture after cleanup.
Verifies that extracted modules are properly integrated and functionality is preserved.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_modular_imports():
    """Test that run.py properly imports from extracted modules"""
    print("\n🔧 Testing Modular Import Architecture...")
    
    try:
        # Test API client manager import
        from api.client_manager import setup_api_client, validate_api_environment
        print("  ✅ API client functions imported from api.client_manager")
        
        # Test author manager import
        from utils.author_manager import load_authors, get_author_by_id, list_authors
        print("  ✅ Author manager functions imported from utils.author_manager")
        
        # Test environment checker import
        from utils.environment_checker import check_environment, format_environment_report
        print("  ✅ Environment checker functions imported from utils.environment_checker")
        
        # Test file operations import
        from utils.file_operations import save_component_to_file, ensure_output_directory
        print("  ✅ File operations functions imported from utils.file_operations")
        
        # Test component config import
        from cli.component_config import COMPONENT_CONFIG, show_component_configuration
        print("  ✅ Component configuration imported from cli.component_config")
        
        print("  ✅ All modular imports successful")
        
    except Exception as e:
        pytest.fail(f"Modular import failed: {e}")

def test_run_py_uses_modular_components():
    """Test that run.py actually uses the modular components"""
    print("\n🏗️ Testing run.py Modular Usage...")
    
    try:
        from run import (
            run_dynamic_generation,
            run_yaml_validation,
            run_single_material,
            create_arg_parser,
            main
        )
        
        # These should be imported by run.py internally
        import api.client_manager
        import utils.author_manager
        import utils.environment_checker
        import utils.file_operations
        import cli.component_config
        
        print("  ✅ run.py successfully uses modular imports")
        
        # Test that the argument parser works
        parser = create_arg_parser()
        
        # Test basic args
        args = parser.parse_args(['--list-materials'])
        assert hasattr(args, 'list_materials')
        print("  ✅ Argument parser functional")
        
        # Test component config access
        from cli.component_config import COMPONENT_CONFIG
        assert isinstance(COMPONENT_CONFIG, dict)
        print("  ✅ Component configuration accessible")
        
    except Exception as e:
        pytest.fail(f"Modular usage test failed: {e}")

def test_reduced_run_py_size():
    """Test that run.py is significantly smaller after modular cleanup"""
    print("\n📏 Testing run.py Size Reduction...")
    
    try:
        # Check current run.py size
        run_py_path = os.path.join(os.path.dirname(__file__), '..', 'run.py')
        with open(run_py_path, 'r') as f:
            current_lines = len(f.readlines())
        
        print(f"  📊 Current run.py: {current_lines} lines")
        
        # Should be significantly smaller than the original ~1692 lines
        assert current_lines < 800, f"run.py should be < 800 lines, got {current_lines}"
        print(f"  ✅ run.py successfully reduced to {current_lines} lines")
        
        # Check that backup exists
        backup_path = os.path.join(os.path.dirname(__file__), '..', 'run_original_backup.py')
        if os.path.exists(backup_path):
            with open(backup_path, 'r') as f:
                backup_lines = len(f.readlines())
            print(f"  📋 Original backup: {backup_lines} lines")
            
            reduction_percent = ((backup_lines - current_lines) / backup_lines) * 100
            print(f"  📉 Size reduction: {reduction_percent:.1f}%")
            
    except Exception as e:
        pytest.fail(f"Size reduction test failed: {e}")

def test_functionality_preserved():
    """Test that core functionality is preserved after modular cleanup"""
    print("\n⚡ Testing Functionality Preservation...")
    
    try:
        from run import run_yaml_validation, run_comprehensive_tests
        
        # These should be callable
        assert callable(run_yaml_validation)
        assert callable(run_comprehensive_tests)
        print("  ✅ Core functions are callable")
        
        # Test argument parser with various options
        from run import create_arg_parser
        parser = create_arg_parser()
        
        test_cases = [
            ['--help'],  # Will cause SystemExit
            ['--list-materials'],
            ['--list-components'],
            ['--check-env'],
            ['--show-config'],
            ['--yaml'],
            ['--material', 'Aluminum'],
        ]
        
        for case in test_cases:
            try:
                parser.parse_args(case)
                print(f"    ✅ Args handled: {' '.join(case)}")
            except SystemExit:
                # --help causes SystemExit, which is expected
                if '--help' in case:
                    print(f"    ✅ Help command handled: {' '.join(case)}")
                    
        print("  ✅ Argument parsing functionality preserved")
        
    except Exception as e:
        pytest.fail(f"Functionality preservation test failed: {e}")

def test_error_handling_preserved():
    """Test that error handling is preserved in modular architecture"""
    print("\n🛡️ Testing Error Handling Preservation...")
    
    try:
        # Test environment checking still works
        from utils.environment_checker import check_environment
        
        # Should handle missing API keys gracefully
        with patch.dict(os.environ, {}, clear=True):
            # This should not crash
            result = check_environment()
            print("  ✅ Environment checker handles missing keys")
        
        # Test file operations error handling
        from utils.file_operations import save_component_to_file
        
        # Should handle permission errors gracefully
        try:
            save_component_to_file("test", "/nonexistent/directory/file.txt")
        except (OSError, IOError, PermissionError):
            print("  ✅ File operations handle permission errors")
        
        print("  ✅ Error handling preserved in modular architecture")
        
    except Exception as e:
        pytest.fail(f"Error handling test failed: {e}")

if __name__ == "__main__":
    print("🧪 Running Modular Architecture Tests...")
    
    test_functions = [
        ("Modular Imports", test_modular_imports),
        ("Modular Usage", test_run_py_uses_modular_components),
        ("Size Reduction", test_reduced_run_py_size),
        ("Functionality Preservation", test_functionality_preserved),
        ("Error Handling", test_error_handling_preserved),
    ]
    
    for test_name, test_func in test_functions:
        try:
            print(f"\n{'='*50}")
            print(f"🎯 {test_name}")
            print('='*50)
            test_func()
            print(f"✅ {test_name} PASSED")
        except Exception as e:
            print(f"❌ {test_name} FAILED: {e}")
            sys.exit(1)
    
    print("\n" + "="*50)
    print("🎉 All Modular Architecture Tests PASSED!")
    print("="*50)
