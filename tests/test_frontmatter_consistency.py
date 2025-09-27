#!/usr/bin/env python3
"""
Frontmatter Data Consistency Test Runner

Run comprehensive tests to ensure frontmatter generation correctly uses source data
and prevent silent failures like the machine settings unit extraction issue.

Usage:
    python3 test_frontmatter_consistency.py
    python3 test_frontmatter_consistency.py --verbose
    python3 test_frontmatter_consistency.py --test-name test_machine_settings_unit_mapping
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

def run_consistency_tests(verbose=False, test_name=None):
    """Run frontmatter data consistency tests"""
    try:
        from test_frontmatter_data_consistency import TestFrontmatterDataConsistency, TestDataSourceIntegrity
        import unittest
        
        # Create test suite
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        if test_name:
            # Run specific test
            if hasattr(TestFrontmatterDataConsistency, test_name):
                suite.addTest(TestFrontmatterDataConsistency(test_name))
            elif hasattr(TestDataSourceIntegrity, test_name):
                suite.addTest(TestDataSourceIntegrity(test_name))
            else:
                print(f"❌ Test '{test_name}' not found")
                return False
        else:
            # Run all tests
            suite.addTests(loader.loadTestsFromTestCase(TestFrontmatterDataConsistency))
            suite.addTests(loader.loadTestsFromTestCase(TestDataSourceIntegrity))
        
        # Set up test runner
        verbosity = 2 if verbose else 1
        runner = unittest.TextTestRunner(verbosity=verbosity)
        
        print("🧪 Running Frontmatter Data Consistency Tests...")
        print("=" * 60)
        
        # Run tests
        result = runner.run(suite)
        
        print("=" * 60)
        if result.wasSuccessful():
            print("✅ All tests passed! Frontmatter data consistency verified.")
            return True
        else:
            print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
            return False
            
    except Exception as e:
        print(f"❌ Test runner failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Run frontmatter data consistency tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--test-name", "-t", help="Run specific test by name")
    
    args = parser.parse_args()
    
    success = run_consistency_tests(verbose=args.verbose, test_name=args.test_name)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()