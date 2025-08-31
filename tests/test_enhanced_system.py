#!/usr/bin/env python3
"""
Comprehensive test runner for enhanced percentile system.
Runs all tests for Phase 1 & 2 functionality implemented today.
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import all test modules for the enhanced system
from tests.test_percentile_calculator import TestPercentileCalculator, TestPercentileCalculatorIntegration
from tests.test_property_enhancer import TestPropertyEnhancer, TestPropertyEnhancerIntegration
from tests.test_category_ranges import TestCategoryRanges, TestCategoryRangesIntegration


def create_enhanced_test_suite():
    """Create a comprehensive test suite for the enhanced percentile system."""
    
    suite = unittest.TestSuite()
    
    # Percentile Calculator Tests
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestPercentileCalculator))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestPercentileCalculatorIntegration))
    
    # Property Enhancer Tests
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestPropertyEnhancer))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestPropertyEnhancerIntegration))
    
    # Category Ranges Tests
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestCategoryRanges))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestCategoryRangesIntegration))
    
    return suite


def run_enhanced_tests():
    """Run all enhanced percentile system tests with detailed reporting."""
    
    print("🚀 ENHANCED PERCENTILE SYSTEM TEST SUITE")
    print("=" * 60)
    print("Testing Phase 1 & 2 Implementation:")
    print("• Percentile Calculator (11 properties)")
    print("• Property Enhancer (frontmatter integration)")
    print("• Category Ranges Database (8 categories × 11 properties)")
    print("• Unit Parsing (cm⁻¹, mm²/s, µm/m·K, J/g·K, %)")
    print("• Laser-specific Properties (absorption, reflectivity)")
    print("• Thermal Properties (diffusivity, expansion, specific heat)")
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
        print("🎉 EXCELLENT: Enhanced system is highly reliable!")
    elif success_rate >= 90:
        print("✅ GOOD: Enhanced system is working well!")
    elif success_rate >= 80:
        print("⚠️  FAIR: Enhanced system needs some attention.")
    else:
        print("❌ POOR: Enhanced system needs significant work.")
    
    print("=" * 60)
    
    # Return success status
    return failures == 0 and errors == 0


def run_specific_test_category(category):
    """Run tests for a specific category."""
    
    suite = unittest.TestSuite()
    
    if category.lower() == 'calculator':
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestPercentileCalculator))
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestPercentileCalculatorIntegration))
    elif category.lower() == 'enhancer':
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestPropertyEnhancer))
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestPropertyEnhancerIntegration))
    elif category.lower() == 'ranges':
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestCategoryRanges))
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestCategoryRangesIntegration))
    else:
        print(f"❌ Unknown test category: {category}")
        print("Available categories: calculator, enhancer, ranges")
        return False
    
    runner = unittest.TextTestRunner(verbosity=2)
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
