#!/usr/bin/env python3
"""
Comprehensive test runner for enhanced Z-Beam system.
Runs integration tests for the complete system functionality.
"""

import unittest
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import available test modules for the Z-Beam system
from tests.test_component_config import *
from tests.test_dynamic_system import *
from tests.test_static_components import *


def create_enhanced_test_suite():
    """Create a comprehensive test suite for the enhanced Z-Beam system."""
    
    suite = unittest.TestSuite()
    
    # Load all available test cases
    test_modules = [
        'tests.test_component_config',
        'tests.test_dynamic_system', 
        'tests.test_static_components',
        'tests.test_yaml_validation',
        'tests.test_api_comprehensive'
    ]
    
    for module_name in test_modules:
        try:
            loader = unittest.TestLoader()
            # Load tests from module
            module_suite = loader.loadTestsFromName(module_name)
            suite.addTest(module_suite)
        except (ImportError, AttributeError) as e:
            print(f"Warning: Could not load tests from {module_name}: {e}")
            continue
    
    return suite


def run_enhanced_tests():
    """Run all enhanced Z-Beam system tests with detailed reporting."""
    
    print("🚀 ENHANCED Z-BEAM SYSTEM TEST SUITE")
    print("=" * 60)
    print("Testing Complete System Functionality:")
    print("• Component Configuration (data_provider/api_provider)")
    print("• Dynamic Content Generation System")
    print("• Static Component Architecture")
    print("• YAML Schema Validation")
    print("• API Integration (Grok/DeepSeek)")
    print("• Content Validation (Human Writing/Country Style)")
    print("=" * 60)
    
    # Create test suite
    suite = create_enhanced_test_suite()
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    successful = total_tests - failures - errors - skipped
    
    print(f"Total Tests Run: {total_tests}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failures: {failures}")
    print(f"💥 Errors: {errors}")
    print(f"⏭️  Skipped: {skipped}")
    
    if failures > 0:
        print(f"\n❌ FAILURES ({failures}):")
        for test, traceback in result.failures:
            print(f"  • {test}")
    
    if errors > 0:
        print(f"\n💥 ERRORS ({errors}):")
        for test, traceback in result.errors:
            print(f"  • {test}")
    
    success_rate = (successful / total_tests * 100) if total_tests > 0 else 0
    print(f"\n📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 95:
        print("🎉 EXCELLENT: Z-Beam system is highly reliable!")
    elif success_rate >= 90:
        print("✅ GOOD: Z-Beam system is working well!")
    elif success_rate >= 80:
        print("⚠️  FAIR: Z-Beam system needs some attention.")
    else:
        print("❌ POOR: Z-Beam system needs significant work.")
    
    print("=" * 60)
    
    # Return success status
    return failures == 0 and errors == 0


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run enhanced Z-Beam system tests')
    parser.add_argument('--category', '-c', 
                       choices=['config', 'dynamic', 'static', 'yaml', 'api', 'all'],
                       default='all',
                       help='Test category to run (default: all)')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Run tests quietly with minimal output')
    
    args = parser.parse_args()
    
    if args.quiet:
        # Redirect stdout to suppress verbose output
        import io
        original_stdout = sys.stdout
        sys.stdout = io.StringIO()
    
    try:
        if args.category == 'all':
            success = run_enhanced_tests()
        else:
            success = run_specific_test_category(args.category)
        
        if args.quiet:
            # Restore stdout and print final result only
            sys.stdout = original_stdout
            if success:
                print("✅ All tests passed!")
            else:
                print("❌ Some tests failed!")
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        if args.quiet:
            sys.stdout = original_stdout
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        if args.quiet:
            sys.stdout = original_stdout
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)


def run_specific_test_category(category):
    """Run tests for a specific category."""
    
    test_categories = {
        'config': 'tests.test_component_config',
        'dynamic': 'tests.test_dynamic_system', 
        'static': 'tests.test_static_components',
        'yaml': 'tests.test_yaml_validation',
        'api': 'tests.test_api_comprehensive'
    }
    
    if category.lower() not in test_categories:
        print(f"❌ Unknown test category: {category}")
        print(f"Available categories: {', '.join(test_categories.keys())}")
        return False
    
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    try:
        module_suite = loader.loadTestsFromName(test_categories[category.lower()])
        suite.addTest(module_suite)
    except (ImportError, AttributeError) as e:
        print(f"❌ Error loading {category} tests: {e}")
        return False
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return len(result.failures) == 0 and len(result.errors) == 0
    result = runner.run(suite)
    
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run enhanced percentile system tests')
    parser.add_argument('--category', '-c', 
                       choices=['calculator', 'enhancer', 'ranges', 'all'],
                       default='all',
                       help='Test category to run (default: all)')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Run tests quietly with minimal output')
    
    args = parser.parse_args()
    
    if args.quiet:
        # Redirect stdout to suppress verbose output
        import io
        original_stdout = sys.stdout
        sys.stdout = io.StringIO()
    
    try:
        if args.category == 'all':
            success = run_enhanced_tests()
        else:
            success = run_specific_test_category(args.category)
        
        if args.quiet:
            # Restore stdout and print final result only
            sys.stdout = original_stdout
            if success:
                print("✅ All tests passed!")
            else:
                print("❌ Some tests failed!")
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        if args.quiet:
            sys.stdout = original_stdout
        print(f"💥 Test runner error: {e}")
        sys.exit(1)
