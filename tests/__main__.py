#!/usr/bin/env python3
"""
Z-Beam Test Suite Main Runner

Simplified test runner for core functionality:
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
    """Run complete test suite with API response validation"""
    print("🧪 Z-BEAM TEST SUITE")
    print("=" * 60)
    print("Running all tests including API response validation...")
    
    test_suites = [
        ("test_authors.py", "Author System Tests"),
        ("test_author_component.py", "Author Component Tests"), 
        ("test_templates.py", "Component Template Tests"),
        ("test_dynamic_system.py", "Dynamic System Tests"),
        ("test_api_comprehensive.py", "API Response & Integration Tests"),
        ("test_component_config.py", "Component Configuration Tests"), 
        ("test_integration.py", "Integration Tests")
    ]
    
    return run_test_suites(test_suites, "COMPLETE")

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
    
    print(f"📈 OVERALL STATISTICS:")
    print(f"   Total Test Suites: {len(results)}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📊 Success Rate: {success_rate:.1f}%")
    print(f"   ⏱️  Total Duration: {total_duration:.2f} seconds")
    
    print(f"\n📋 DETAILED RESULTS:")
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"   {result['name']:<35} {status} ({result['duration']:.2f}s)")
    
    # Failed suites
    failed_suites = [r['name'] for r in results if not r['success']]
    if failed_suites:
        print(f"\n⚠️  FAILED SUITES:")
        for suite in failed_suites:
            print(f"   ❌ {suite}")
    
    # System assessment
    print(f"\n🎯 SYSTEM ASSESSMENT:")
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
    print(f"\n💡 RECOMMENDATIONS:")
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
    
    print(f"\n📝 NEXT STEPS:")
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

Test Suite:
  Core Tests: System functionality, API response validation, configuration, integration
        """
    )
    
    # Optional verbose flag
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Always run all tests
    results = run_all_tests()
    
    # Return appropriate exit code
    return 0 if results.get("success", False) else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
