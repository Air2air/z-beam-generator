#!/usr/bin/env python3
"""
Comprehensive Test Runner for Z-Beam Generator

This script runs all tests in the correct order and provides a clear summary.
It only tests materials with complete frontmatter files unless specifically testing invalid frontmatter.

Usage:
    python3 run_comprehensive_tests.py          # Run all tests
    python3 run_comprehensive_tests.py --quick  # Run core tests only
    python3 run_comprehensive_tests.py --verbose # Detailed output
"""

import sys
import os
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Tuple
import yaml

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class ComprehensiveTestRunner:
    """Comprehensive test runner for Z-Beam Generator"""

    def __init__(self, quick_mode: bool = False, verbose: bool = False):
        self.quick_mode = quick_mode
        self.verbose = verbose
        self.results = {}
        self.start_time = time.time()

    def get_available_frontmatter_materials(self) -> List[str]:
        """Get list of materials that have complete frontmatter files"""
        frontmatter_dir = Path("content/components/frontmatter")
        available_materials = []

        if not frontmatter_dir.exists():
            print("❌ Frontmatter directory not found")
            return []

        for frontmatter_file in frontmatter_dir.glob("*-laser-cleaning.md"):
            material_name = frontmatter_file.stem.replace("-laser-cleaning", "").title()

            # Check if frontmatter is complete
            if self._is_frontmatter_complete(frontmatter_file):
                available_materials.append(material_name)

        return sorted(available_materials)

    def _is_frontmatter_complete(self, frontmatter_file: Path) -> bool:
        """Check if frontmatter file has all required fields"""
        try:
            with open(frontmatter_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract frontmatter
            if not content.startswith('---'):
                return False

            end_pos = content.find('---', 3)
            if end_pos == -1:
                return False

            frontmatter_content = content[3:end_pos].strip()
            frontmatter_data = yaml.safe_load(frontmatter_content)

            # Required fields for basic testing
            required_fields = ['name', 'category', 'properties', 'applications']

            for field in required_fields:
                if field not in frontmatter_data:
                    return False
                if not frontmatter_data[field]:
                    return False

            return True

        except Exception:
            return False

    def run_test_suite(self, test_files: List[str], description: str) -> Tuple[bool, str]:
        """Run a suite of test files"""
        print(f"\n🧪 Running {description}...")

        success_count = 0
        total_count = len(test_files)
        failed_tests = []

        for test_file in test_files:
            test_path = Path("tests") / test_file
            if not test_path.exists():
                print(f"⚠️  Test file not found: {test_file}")
                continue

            print(f"  📋 Running {test_file}..." if self.verbose else f"  📋 {test_file}...", end="")

            try:
                # Set PYTHONPATH for proper imports
                env = os.environ.copy()
                env['PYTHONPATH'] = str(project_root)

                result = subprocess.run(
                    [sys.executable, str(test_path)],
                    capture_output=not self.verbose,
                    text=True,
                    env=env,
                    timeout=300  # 5 minute timeout
                )

                if result.returncode == 0:
                    success_count += 1
                    print(" ✅" if not self.verbose else "")
                else:
                    failed_tests.append(test_file)
                    print(" ❌" if not self.verbose else "")
                    if self.verbose:
                        print(f"      Error: {result.stderr}")

            except subprocess.TimeoutExpired:
                failed_tests.append(test_file)
                print(" ⏰ (timeout)" if not self.verbose else " ⏰ TIMEOUT")
            except Exception as e:
                failed_tests.append(test_file)
                print(f" 💥 ({type(e).__name__})" if not self.verbose else f" 💥 {type(e).__name__}: {e}")

        success = success_count == total_count
        summary = f"{success_count}/{total_count} passed"

        if failed_tests:
            summary += f" (failed: {', '.join(failed_tests)})"

        print(f"   📊 {description}: {summary}")

        return success, summary

    def run_pytest_suite(self, test_pattern: str, description: str) -> Tuple[bool, str]:
        """Run pytest with specific pattern"""
        print(f"\n🧪 Running {description}...")

        try:
            cmd = [sys.executable, "-m", "pytest", test_pattern, "-v", "--tb=short"]
            if not self.verbose:
                cmd.extend(["-q"])

            result = subprocess.run(
                cmd,
                capture_output=not self.verbose,
                text=True,
                cwd=str(project_root),
                timeout=600  # 10 minute timeout for full suite
            )

            success = result.returncode == 0

            if success:
                print("   📊 pytest suite: ✅ PASSED")
                return success, "PASSED"
            else:
                print("   📊 pytest suite: ❌ FAILED")
                if not self.verbose and result.stdout:
                    # Show last few lines of output
                    lines = result.stdout.strip().split('\n')
                    for line in lines[-5:]:
                        if line.strip():
                            print(f"      {line}")
                return success, "FAILED"

        except subprocess.TimeoutExpired:
            print("   📊 pytest suite: ⏰ TIMEOUT")
            return False, "TIMEOUT"
        except Exception as e:
            print(f"   📊 pytest suite: 💥 {type(e).__name__}")
            return False, "ERROR"

    def run_frontmatter_tests(self) -> Tuple[bool, str]:
        """Run frontmatter-specific tests"""
        frontmatter_tests = [
            "test_frontmatter_dependency_chain.py",
            "test_cascading_failure.py"
        ]

        return self.run_test_suite(frontmatter_tests, "Frontmatter Dependency Tests")

    def run_core_tests(self) -> Tuple[bool, str]:
        """Run core functionality tests"""
        core_tests = [
            "test_ai_detection_config.py",
            "test_content_generation.py",
            "test_dynamic_components.py",
            "test_dynamic_prompt_generation.py",
            "test_dynamic_prompt_system.py",
            "test_frontmatter_iterations.py",
            "test_modified_prompts.py",
            "test_nationality_fix.py",
            "test_prompt_optimizer.py",
            "test_template_substitution.py",
            "test_validation_diagnostics.py"
        ]

        return self.run_test_suite(core_tests, "Core Functionality Tests")

    def run_all_tests(self) -> Dict[str, Tuple[bool, str]]:
        """Run all test suites"""
        print("🚀 Z-BEAM GENERATOR COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        print(f"📅 Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🏃 Mode: {'Quick' if self.quick_mode else 'Full'}")
        print(f"📝 Verbose: {'Yes' if self.verbose else 'No'}")

        # Check available materials
        available_materials = self.get_available_frontmatter_materials()
        print(f"📋 Available materials with complete frontmatter: {len(available_materials)}")
        if available_materials:
            print(f"   Materials: {', '.join(available_materials[:5])}{'...' if len(available_materials) > 5 else ''}")

        results = {}

        # Run pytest suite first (fastest)
        if not self.quick_mode:
            results['pytest'] = self.run_pytest_suite("test_*.py", "Pytest Test Suite")

        # Run frontmatter tests
        results['frontmatter'] = self.run_frontmatter_tests()

        # Run core tests (skip if quick mode)
        if not self.quick_mode:
            results['core'] = self.run_core_tests()

        return results

    def print_summary(self, results: Dict[str, Tuple[bool, str]]):
        """Print comprehensive test summary"""
        end_time = time.time()
        duration = end_time - self.start_time

        print("\n" + "=" * 60)
        print("🎯 TEST SUMMARY")
        print("=" * 60)

        total_passed = 0
        total_failed = 0

        for test_type, (success, summary) in results.items():
            status = "✅" if success else "❌"
            print(f"{status} {test_type.upper()}: {summary}")

            if success:
                total_passed += 1
            else:
                total_failed += 1

        print("-" * 60)
        print(f"⏱️  Total time: {duration:.1f}s")
        print(f"📊 Overall: {total_passed}/{total_passed + total_failed} suites passed")

        if total_failed == 0:
            print("\n🎉 ALL TESTS PASSED! 🎉")
            print("✅ System is ready for production use")
        else:
            print(f"\n⚠️  {total_failed} test suite(s) failed")
            print("❌ Please review and fix issues before deployment")

        print("\n📝 Notes:")
        print("   • Tests only run on materials with complete frontmatter files")
        print("   • Frontmatter dependency is validated and enforced")
        print("   • Cascading failures are tested and documented")
        print("   • No fallbacks or mocks in production code (tests may use mocks)")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Comprehensive Test Runner for Z-Beam Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python3 run_comprehensive_tests.py              # Full test suite
  python3 run_comprehensive_tests.py --quick      # Core tests only
  python3 run_comprehensive_tests.py --verbose    # Detailed output
  python3 run_comprehensive_tests.py --quick --verbose  # Quick with details
        """
    )

    parser.add_argument('--quick', '-q', action='store_true',
                       help='Run quick test suite (skip slow tests)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')

    args = parser.parse_args()

    runner = ComprehensiveTestRunner(quick_mode=args.quick, verbose=args.verbose)
    results = runner.run_all_tests()
    runner.print_summary(results)

    # Exit with appropriate code
    success = all(success for success, _ in results.values())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
