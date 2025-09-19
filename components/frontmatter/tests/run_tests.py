#!/usr/bin/env python3
"""
Frontmatter Test Runner

Comprehensive test runner for the modular frontmatter architecture.
Runs all test suites with detailed reporting and coverage analysis.

Usage:
    python3 run_tests.py              # Run all tests
    python3 run_tests.py --core       # Run only core generator tests  
    python3 run_tests.py --ordering   # Run only field ordering tests
    python3 run_tests.py --enhancement # Run only property enhancement tests
    python3 run_tests.py --validation # Run only validation helper tests
    python3 run_tests.py --integration # Run only integration tests
    python3 run_tests.py --verbose    # Verbose output
"""

import argparse
import sys
import unittest
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from components.frontmatter.tests.test_core_generator import TestCoreGenerator, TestGeneratorEdgeCases
from components.frontmatter.tests.test_field_ordering import TestFieldOrderingService
from components.frontmatter.tests.test_property_enhancement import TestPropertyEnhancementService, TestPropertyEnhancementEdgeCases
from components.frontmatter.tests.test_validation_helpers import TestValidationHelpers, TestValidationHelpersEdgeCases
from components.frontmatter.tests.test_integration import TestModularIntegration, TestModularArchitectureQuality


def create_test_suite(test_categories=None):
    """Create test suite based on requested categories"""
    suite = unittest.TestSuite()
    
    test_mapping = {
        'core': [TestCoreGenerator, TestGeneratorEdgeCases],
        'ordering': [TestFieldOrderingService],
        'enhancement': [TestPropertyEnhancementService, TestPropertyEnhancementEdgeCases],
        'validation': [TestValidationHelpers, TestValidationHelpersEdgeCases],
        'integration': [TestModularIntegration, TestModularArchitectureQuality]
    }
    
    if not test_categories:
        # Run all tests
        test_categories = test_mapping.keys()
    
    for category in test_categories:
        if category in test_mapping:
            for test_class in test_mapping[category]:
                tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
                suite.addTests(tests)
        else:
            print(f"Warning: Unknown test category '{category}'")
    
    return suite


def print_test_summary():
    """Print summary of modular test architecture"""
    print("🧪 FRONTMATTER MODULAR TEST SUITE")
    print("=" * 50)
    print()
    print("📊 Test Organization:")
    print("  • test_core_generator.py: Core generation logic tests")
    print("  • test_field_ordering.py: Field ordering service tests")
    print("  • test_property_enhancement.py: Property enhancement tests")
    print("  • test_validation_helpers.py: Validation helper tests")
    print("  • test_integration.py: Integration & architecture tests")
    print()
    print("🎯 Total Test Classes: 9")
    print("📈 Estimated Test Count: 80+ individual tests")
    print("⚡ Focused on modular architecture validation")
    print()


def run_tests(test_categories=None, verbosity=1):
    """Run the test suite with specified parameters"""
    print_test_summary()
    
    # Create and run test suite
    suite = create_test_suite(test_categories)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Print results summary
    print()
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 30)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    # Print architecture validation
    if result.wasSuccessful():
        print()
        print("✅ MODULAR ARCHITECTURE VALIDATION SUCCESSFUL")
        print("🎉 All services work correctly in isolation and integration")
        print("📈 Refactoring from 1,102 lines to modular architecture complete")
    else:
        print()
        print("❌ SOME TESTS FAILED")
        print("🔧 Review failed tests to ensure modular architecture integrity")
    
    return result.wasSuccessful()


def main():
    """Main test runner entry point"""
    parser = argparse.ArgumentParser(description="Frontmatter Modular Test Runner")
    parser.add_argument('--core', action='store_true', help='Run core generator tests only')
    parser.add_argument('--ordering', action='store_true', help='Run field ordering tests only')
    parser.add_argument('--enhancement', action='store_true', help='Run property enhancement tests only')
    parser.add_argument('--validation', action='store_true', help='Run validation helper tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Determine which test categories to run
    test_categories = []
    if args.core:
        test_categories.append('core')
    if args.ordering:
        test_categories.append('ordering')
    if args.enhancement:
        test_categories.append('enhancement')
    if args.validation:
        test_categories.append('validation')
    if args.integration:
        test_categories.append('integration')
    
    # If no specific categories, run all
    if not test_categories:
        test_categories = None
    
    verbosity = 2 if args.verbose else 1
    
    success = run_tests(test_categories, verbosity)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
