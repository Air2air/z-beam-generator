#!/usr/bin/env python3
"""
Comprehensive test runner for the entire Z-Beam generator system.
Includes all existing tests plus the new enhanced percentile system tests.
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def discover_all_tests():
    """Discover and run all tests in the test directory."""
    
    print("🔍 DISCOVERING ALL Z-BEAM TESTS")
    print("=" * 50)
    
    # Discover all test files in the tests directory
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Count total tests
    test_count = suite.countTestCases()
    print(f"📊 Discovered {test_count} total tests")
    
    # Run all tests
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    print("\n🚀 RUNNING ALL TESTS")
    print("=" * 50)
    
    result = runner.run(suite)
    
    # Print comprehensive summary
    print("\n" + "=" * 50)
    print("🎯 COMPREHENSIVE TEST RESULTS")
    print("=" * 50)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    successful = total_tests - failures - errors - skipped
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {successful}")
    print(f"❌ Failed: {failures}")
    print(f"💥 Errors: {errors}")
    print(f"⏭️  Skipped: {skipped}")
    
    success_rate = (successful / total_tests * 100) if total_tests > 0 else 0
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    # Detailed failure/error reporting
    if failures > 0:
        print(f"\n❌ TEST FAILURES ({failures}):")
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"  {i}. {test}")
            if len(traceback) > 200:
                print(f"     {traceback[:200]}...")
            else:
                print(f"     {traceback}")
    
    if errors > 0:
        print(f"\n💥 TEST ERRORS ({errors}):")
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"  {i}. {test}")
            if len(traceback) > 200:
                print(f"     {traceback[:200]}...")
            else:
                print(f"     {traceback}")
    
    # Final assessment
    print("\n" + "=" * 50)
    if success_rate >= 95:
        print("🎉 EXCELLENT: Z-Beam system is highly reliable!")
        status_emoji = "🟢"
    elif success_rate >= 90:
        print("✅ GOOD: Z-Beam system is working well!")
        status_emoji = "🟡"
    elif success_rate >= 80:
        print("⚠️  FAIR: Z-Beam system needs attention.")
        status_emoji = "🟠"
    else:
        print("❌ POOR: Z-Beam system needs significant work.")
        status_emoji = "🔴"
    
    print(f"System Status: {status_emoji}")
    print("=" * 50)
    
    return failures == 0 and errors == 0


def run_enhanced_tests_only():
    """Run only the enhanced percentile system tests."""
    from tests.test_enhanced_system import run_enhanced_tests
    return run_enhanced_tests()


def main():
    """Main test runner with options."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Z-Beam Test Runner')
    parser.add_argument('--enhanced-only', action='store_true',
                       help='Run only enhanced percentile system tests')
    parser.add_argument('--quick', action='store_true',
                       help='Run tests with minimal output')
    
    args = parser.parse_args()
    
    if args.quick:
        # Suppress verbose output
        import io
        original_stdout = sys.stdout
        sys.stdout = io.StringIO()
    
    try:
        if args.enhanced_only:
            success = run_enhanced_tests_only()
        else:
            success = discover_all_tests()
        
        if args.quick:
            sys.stdout = original_stdout
            if success:
                print("✅ All tests passed!")
            else:
                print("❌ Some tests failed!")
        
        return 0 if success else 1
        
    except Exception as e:
        if args.quick:
            sys.stdout = original_stdout
        print(f"💥 Test runner error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())