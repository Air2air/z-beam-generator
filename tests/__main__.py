#!/usr/bin/env python3
"""
Z-Beam Test Suite Main Runner

Provides comprehensive test suite execution with enhanced reporting and more functionality:
- Default: Run all available tests including API response validation

Usage:
    python3 -m tests                # Run all tests (default)
    python3 -m tests --help         # Show help information
"""

import sys
import subprocess
import time
import argparse
from pathlib import Path

# Add parent directory to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_test_suite(test_file: str, description: str) -> tuple[bool, float]:
    """Run a test suite and return success status and duration"""
    print(f"🚀 RUNNING {description.upper()}")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Run the test file from the tests directory
        test_path = Path(__file__).parent / test_file
        result = subprocess.run(
            [sys.executable, str(test_path)],
            cwd=Path(__file__).parent.parent,  # Run from project root
            capture_output=False,  # Show output in real-time
            text=True
        )
        
        duration = time.time() - start_time
        success = result.returncode == 0
        
        print(f"\n⏱️  Duration: {duration:.2f} seconds")
        print(f"🏁 Result: {'✅ PASSED' if success else '❌ FAILED'}")
        
        return success, duration
        
    except Exception as e:
        duration = time.time() - start_time
        print(f"\n❌ Error running {test_file}: {e}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print("🏁 Result: ❌ FAILED")
        
        return False, duration

def run_all_tests() -> dict:
    """Run comprehensive test suite (excluding cleanup)"""
    print("🧪 Z-BEAM COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print("Running all core system tests...")
    
    # Define available test suites (EXCLUDING cleanup)
    test_suites = [
        ("test_api_comprehensive.py", "API Provider Tests"),
        ("test_api_providers.py", "API Integration Tests"), 
        ("test_author_component.py", "Author Component Tests"),
        ("test_authors.py", "Author System Tests"),
        ("test_component_config.py", "Component Configuration Tests"),
        ("test_dynamic_system.py", "Dynamic System Tests"),
        ("test_integration.py", "Integration Tests"),
        ("test_templates.py", "Template Tests")
    ]
    
    return run_test_suites(test_suites, "COMPLETE")

def run_cleanup_only() -> dict:
    """Run only cleanup tests"""
    print("🧹 Z-BEAM CLEANUP SUITE")
    print("=" * 60)
    print("Running cleanup system tests...")
    
    test_suites = [
        ("../cleanup/test_cleanup.py", "Cleanup System Tests")
    ]
    
    return run_test_suites(test_suites, "CLEANUP")

def run_with_coverage(cleanup_only: bool = False) -> dict:
    """Run tests with coverage analysis"""
    print("📊 Z-BEAM COVERAGE ANALYSIS")
    print("=" * 60)
    print("Running tests with coverage tracking...")
    
    try:
        import coverage
        
        # Initialize coverage
        cov = coverage.Coverage()
        cov.start()
        
        # Run appropriate test suite
        if cleanup_only:
            results = run_cleanup_only()
        else:
            results = run_all_tests()
        
        # Stop coverage and generate report
        cov.stop()
        cov.save()
        
        print("\n📈 COVERAGE REPORT")
        print("=" * 50)
        cov.report()
        
        # Generate HTML coverage report
        html_dir = Path(__file__).parent / "coverage_html"
        cov.html_report(directory=str(html_dir))
        print(f"\n📋 HTML Report: {html_dir}/index.html")
        
        return results
        
    except ImportError:
        print("❌ Coverage package not installed. Install with:")
        print("   pip install coverage")
        print("\nRunning tests without coverage...")
        
        # Fallback to regular test run
        if cleanup_only:
            return run_cleanup_only()
        else:
            return run_all_tests()
    except Exception as e:
        print(f"❌ Coverage analysis failed: {e}")
        print("Running tests without coverage...")
        
        # Fallback to regular test run
        if cleanup_only:
            return run_cleanup_only()
        else:
            return run_all_tests()

def run_test_suites(test_suites: list, suite_type: str) -> dict:
    """Run a list of test suites and return results"""
    
    # Check that all test files exist
    missing_files = []
    for test_file, suite_name in test_suites:
        test_path = Path(__file__).parent / test_file
        if not test_path.exists():
            missing_files.append(test_file)
    
    if missing_files:
        print(f"❌ Missing test files: {', '.join(missing_files)}")
        return {"success": False, "error": "Missing test files"}
    
    # Run each test suite
    results = []
    total_start_time = time.time()
    
    for test_file, description in test_suites:
        print()
        success, duration = run_test_suite(test_file, description)
        results.append({
            'name': description,
            'success': success,
            'duration': duration,
            'file': test_file
        })
    
    total_duration = time.time() - total_start_time
    
    # Generate comprehensive summary
    print("\n" + "=" * 60)
    print(f"📊 {suite_type} TEST RESULTS")
    print("=" * 60)
    
    passed = sum(1 for r in results if r['success'])
    failed = len(results) - passed
    success_rate = (passed / len(results)) * 100 if results else 0
    
    print("📈 OVERALL STATISTICS:")
    print(f"   Total Test Suites: {len(results)}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📊 Success Rate: {success_rate:.1f}%")
    print(f"   ⏱️  Total Duration: {total_duration:.2f} seconds")
    
    print("\n📋 DETAILED RESULTS:")
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"   {result['name']:<35} {status} ({result['duration']:.2f}s)")
    
    # Failed suites
    failed_suites = [r['name'] for r in results if not r['success']]
    if failed_suites:
        print("\n⚠️  FAILED SUITES:")
        for suite in failed_suites:
            print(f"   ❌ {suite}")
    
    # System assessment
    print("\n🎯 SYSTEM ASSESSMENT:")
    if success_rate == 100:
        print("🎉 EXCELLENT! All test suites passed.")
        print("   The Z-Beam system is fully operational and ready for production use.")
        assessment = "EXCELLENT"
    elif success_rate >= 80:
        print("✅ GOOD! Most test suites passed.")
        print("   The system is largely functional with minor issues to address.")
        assessment = "GOOD"
    elif success_rate >= 60:
        print("⚠️  FAIR! Some test suites passed.")
        print("   The system has core functionality but needs improvements.")
        assessment = "FAIR"
    else:
        print("❌ POOR! Many test suites failed.")
        print("   The system has significant issues that need to be resolved.")
        assessment = "POOR"
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if assessment == "EXCELLENT":
        print("   • System is ready for production use")
        print("   • Consider setting up continuous integration")
        print("   • Monitor API usage and performance in production")
    elif assessment == "GOOD":
        print("   • Review and fix failing test suites")
        print("   • System can be used with caution")
        print("   • Monitor for any issues in production")
    elif assessment == "FAIR":
        print("   • Fix failing test suites before production use")
        print("   • Review error messages and system configuration")
        print("   • Verify API keys and dependencies")
    else:
        print("   • System requires significant debugging")
        print("   • Review all error messages and logs")
        print("   • Check system dependencies and configuration")
    
    print("\n📝 NEXT STEPS:")
    if failed_suites:
        print("   1. Review and fix failing tests")
        print("   2. Re-run test suite: python3 -m tests")
        print("   3. Check system configuration and dependencies")
    else:
        print("   1. Deploy to production environment")
        print("   2. Set up monitoring and logging")
        print("   3. Configure automated workflows")
    
    return {
        "success": passed == len(results),
        "passed": passed,
        "failed": failed,
        "total": len(results),
        "success_rate": success_rate,
        "duration": total_duration,
        "results": results
    }

def main():
    """Main test runner with simplified command structure"""
    parser = argparse.ArgumentParser(
        description="Z-Beam Generator Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 -m tests              # Run all tests (default)
  python3 -m tests --cleanup    # Run only cleanup tests

Test Suite:
  Core Tests: System functionality, API response validation, configuration, integration
  Cleanup Tests: Dead files, unused files, temporary files, empty directories
        """
    )
    
    # Optional flags
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Run only cleanup system tests'
    )
    
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Run tests with coverage analysis'
    )
    
    args = parser.parse_args()
    
    # Run appropriate test suite
    if args.coverage:
        # Coverage mode - can be combined with cleanup
        results = run_with_coverage(cleanup_only=args.cleanup)
    elif args.cleanup:
        # Cleanup only mode
        results = run_cleanup_only()
    else:
        # Standard test mode
        results = run_all_tests()
    
    # Return appropriate exit code
    return 0 if results.get("success", False) else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
