#!/usr/bin/env python3
"""
Fast Test Runner for Z-Beam Generator

This script runs the full test suite with optimized settings to prevent hanging.
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def run_custom_tests():
    """Run custom test files with timeout protection."""
    print("🧪 Running Custom Tests...")

    custom_tests = [
        ("test_content_generation.py", 60),
        ("test_robustness_improvements.py", 120),
        (
            "test_optimization_validation.py",
            300,
        ),  # Increased timeout for heavy optimization testing
        ("test_iterative_improvement.py", 90),
    ]

    results = []

    for test_file, timeout in custom_tests:
        test_path = Path(__file__).parent / test_file
        if test_path.exists():
            print(f"  📋 Running {test_file} (timeout: {timeout}s)...")

            try:
                start_time = time.time()
                result = subprocess.run(
                    [sys.executable, str(test_path)],
                    timeout=timeout,
                    capture_output=True,
                    text=True,
                )
                end_time = time.time()
                duration = end_time - start_time

                if result.returncode == 0:
                    print(f"    ✅ {test_file} PASSED in {duration:.2f}s")
                    results.append(True)
                else:
                    print(f"    ❌ {test_file} FAILED in {duration:.2f}s")
                    print(f"    📄 Output: {result.stdout[-500:]}")  # Last 500 chars
                    if result.stderr:
                        print(f"    ⚠️  Error: {result.stderr[-500:]}")
                    results.append(False)

            except subprocess.TimeoutExpired:
                print(f"    ⏰ {test_file} TIMED OUT after {timeout}s")
                results.append(False)
            except Exception as e:
                print(f"    ❌ {test_file} ERROR: {e}")
                results.append(False)
        else:
            print(f"    ⚠️  {test_file} not found")
            results.append(False)

    return results


def run_tests():
    """Run the full test suite with optimized settings."""
    print("🚀 Running Z-Beam Generator Test Suite...")
    print("=" * 50)

    # Set test environment
    os.environ["TEST_MODE"] = "true"

    all_results = []

    # Run custom tests first
    custom_results = run_custom_tests()
    all_results.extend(custom_results)

    # Run pytest tests
    print("\n📋 Running Pytest Tests...")
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/unit/",  # Run all unit tests
        "-v",
        "--tb=short",
        "--no-cov",  # Disable coverage for speed
        "--disable-warnings",  # Reduce noise
        "--asyncio-mode=auto",  # Handle async tests properly
        "-x",  # Stop on first failure (optional, remove if you want to see all failures)
    ]

    start_time = time.time()

    try:
        print("  📋 Collecting pytest tests...")
        result = subprocess.run(cmd, timeout=300)  # 5 minute timeout
        end_time = time.time()

        duration = end_time - start_time
        print(f"  ✅ Pytest completed in {duration:.2f} seconds")
        print(f"  📊 Exit code: {result.returncode}")

        pytest_passed = result.returncode == 0
        all_results.append(pytest_passed)

        if pytest_passed:
            print("  🎉 Pytest tests passed!")
        else:
            print("  ❌ Some pytest tests failed.")

    except subprocess.TimeoutExpired:
        print("  ⏰ Pytest timed out after 5 minutes")
        all_results.append(False)
    except Exception as e:
        print(f"  ❌ Error running pytest: {e}")
        all_results.append(False)

    # Summary
    print("\n" + "=" * 50)
    print("� TEST SUITE SUMMARY")
    print("=" * 50)

    total_tests = len(all_results)
    passed_tests = sum(all_results)

    print(f"📈 Total test groups: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")

    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"⚠️  {total_tests - passed_tests} test group(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
