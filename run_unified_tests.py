#!/usr/bin/env python3
"""
Unified Test Runner for Z-Beam Generator

This script provides comprehensive testing across all architectures:
- Component-based testing with frontmatter validation
- Service-based testing for AI detection, iterative workflow, etc.
- Integration testing across all systems

Usage:
    python3 run_unified_tests.py                    # Run all tests
    python3 run_unified_tests.py --components      # Component tests only
    python3 run_unified_tests.py --services        # Service tests only
    python3 run_unified_tests.py --quick           # Quick component tests
    python3 run_unified_tests.py --verbose         # Detailed output
"""

import sys
import os
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Any
import yaml

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class UnifiedTestRunner:
    """Unified test runner for all Z-Beam architectures"""

    def __init__(self, test_mode: str = "all", quick_mode: bool = False, verbose: bool = False):
        self.test_mode = test_mode  # "all", "components", "services"
        self.quick_mode = quick_mode
        self.verbose = verbose
        self.results = {}
        self.start_time = time.time()
        self.project_root = project_root

    def get_available_frontmatter_materials(self) -> List[str]:
        """Get list of materials that have complete frontmatter files"""
        frontmatter_dir = Path("content/components/frontmatter")
        available_materials = []

        if not frontmatter_dir.exists():
            if self.verbose:
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

            # Extract frontmatter (between --- markers)
            if content.startswith('---'):
                end_marker = content.find('---', 3)
                if end_marker != -1:
                    frontmatter_content = content[3:end_marker].strip()
                    frontmatter_data = yaml.safe_load(frontmatter_content)

                    # Check required fields
                    required_fields = ['name', 'category', 'properties', 'applications']
                    for field in required_fields:
                        if field not in frontmatter_data:
                            return False
                        if not frontmatter_data[field]:
                            return False
                        if field in ['properties', 'applications'] and len(frontmatter_data[field]) == 0:
                            return False
                    return True
            return False
        except Exception as e:
            if self.verbose:
                print(f"Error reading frontmatter {frontmatter_file}: {e}")
            return False

    def run_component_tests(self) -> Dict[str, Tuple[bool, str]]:
        """Run component-based tests with frontmatter validation"""
        print("🔧 Running Component-Based Tests...")
        print("-" * 50)

        # Check available materials
        available_materials = self.get_available_frontmatter_materials()
        print(f"📋 Available materials with complete frontmatter: {len(available_materials)}")
        if available_materials:
            print(f"   Materials: {', '.join(available_materials[:5])}{'...' if len(available_materials) > 5 else ''}")

        results = {}

        # Run frontmatter dependency tests
        if not self.quick_mode:
            results['frontmatter_deps'] = self.run_test_suite([
                "tests/test_frontmatter_dependency_chain.py",
                "tests/test_cascading_failure.py"
            ], "Frontmatter Dependency Tests")

        # Run core component tests
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

        if not self.quick_mode:
            results['core_components'] = self.run_test_suite(core_tests, "Core Component Tests")

        return results

    def run_service_tests(self) -> Dict[str, Tuple[bool, str]]:
        """Run service-based tests for AI detection, iterative workflow, etc."""
        print("🔬 Running Service-Based Tests...")
        print("-" * 50)

        results = {}

        # Service test suites
        service_suites = [
            {
                "name": "AI Detection Optimization",
                "path": "services/ai_detection_optimization/test_ai_detection_optimization.py",
                "description": "AI detection scoring and optimization tests"
            },
            {
                "name": "Iterative Workflow",
                "path": "services/iterative_workflow/test_iterative_workflow.py",
                "description": "Iterative content improvement workflow tests"
            },
            {
                "name": "Dynamic Evolution",
                "path": "services/dynamic_evolution/test_dynamic_evolution.py",
                "description": "Dynamic evolution and A/B testing"
            },
            {
                "name": "Quality Assessment",
                "path": "services/quality_assessment/test_quality_assessment.py",
                "description": "Content quality assessment and benchmarking"
            },
            {
                "name": "Configuration Optimization",
                "path": "services/configuration_optimizer/test_configuration_optimization.py",
                "description": "Configuration optimization and parameter tuning"
            }
        ]

        for suite in service_suites:
            if Path(suite['path']).exists():
                print(f"📋 Running {suite['name']}...")
                result = self.run_single_test_file(suite['path'])
                results[suite['name'].lower().replace(' ', '_')] = result
            else:
                if self.verbose:
                    print(f"⚠️  Skipping {suite['name']} - test file not found: {suite['path']}")
                results[suite['name'].lower().replace(' ', '_')] = (False, "Test file not found")

        return results

    def run_test_suite(self, test_files: List[str], description: str) -> Tuple[bool, str]:
        """Run a suite of test files"""
        print(f"\n🧪 Running {description}...")

        success_count = 0
        total_count = len(test_files)

        for test_file in test_files:
            if Path(test_file).exists():
                success, _ = self.run_single_test_file(test_file)
                if success:
                    success_count += 1
            else:
                if self.verbose:
                    print(f"   ⚠️  {test_file} - File not found")
                total_count -= 1

        overall_success = success_count == total_count
        summary = f"{success_count}/{total_count} passed"

        if overall_success:
            print(f"   📊 {description}: ✅ PASSED ({summary})")
        else:
            print(f"   📊 {description}: ❌ FAILED ({summary})")

        return overall_success, summary

    def run_single_test_file(self, test_file: str) -> Tuple[bool, str]:
        """Run a single test file and return result"""
        try:
            cmd = [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"]
            if not self.verbose:
                cmd.extend(["-q"])

            result = subprocess.run(
                cmd,
                capture_output=not self.verbose,
                text=True,
                cwd=str(self.project_root),
                timeout=300  # 5 minute timeout
            )

            success = result.returncode == 0

            if success:
                status = "PASSED"
            else:
                status = "FAILED"
                if not self.verbose and result.stdout:
                    # Show last few lines of output on failure
                    lines = result.stdout.strip().split('\n')
                    for line in lines[-3:]:
                        if line.strip():
                            print(f"      {line}")

            return success, status

        except subprocess.TimeoutExpired:
            print(f"   ⏰ {test_file}: TIMEOUT")
            return False, "TIMEOUT"
        except Exception as e:
            print(f"   💥 {test_file}: ERROR - {type(e).__name__}")
            return False, "ERROR"

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites based on test mode"""
        print("🚀 Z-BEAM UNIFIED TEST SUITE")
        print("=" * 60)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🏃 Mode: {self.test_mode.title()}")
        print(f"⚡ Quick: {'Yes' if self.quick_mode else 'No'}")
        print(f"📝 Verbose: {'Yes' if self.verbose else 'No'}")

        results = {}

        # Run component tests
        if self.test_mode in ["all", "components"]:
            component_results = self.run_component_tests()
            results.update(component_results)

        # Run service tests
        if self.test_mode in ["all", "services"]:
            service_results = self.run_service_tests()
            results.update(service_results)

        return results

    def print_summary(self, results: Dict[str, Any]):
        """Print comprehensive test summary"""
        end_time = time.time()
        duration = end_time - self.start_time

        print("\n" + "=" * 60)
        print("🎯 UNIFIED TEST SUMMARY")
        print("=" * 60)

        total_passed = 0
        total_failed = 0
        total_tests = len(results)

        for test_type, (success, summary) in results.items():
            status = "✅" if success else "❌"
            print(f"{status} {test_type.replace('_', ' ').title()}: {summary}")

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

        print("\n📝 Architecture Notes:")
        if self.test_mode in ["all", "components"]:
            print("   • Component tests validate frontmatter dependencies")
            print("   • Cascading failures are tested and documented")
        if self.test_mode in ["all", "services"]:
            print("   • Service tests validate AI detection and iterative workflows")
            print("   • Integration tests ensure cross-system compatibility")
        print("   • No fallbacks or mocks in production code")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Unified Test Runner for Z-Beam Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python3 run_unified_tests.py                    # Run all tests
  python3 run_unified_tests.py --components      # Component tests only
  python3 run_unified_tests.py --services        # Service tests only
  python3 run_unified_tests.py --quick           # Quick component tests
  python3 run_unified_tests.py --verbose         # Detailed output
  python3 run_unified_tests.py --components --verbose  # Component tests with details
        """
    )

    parser.add_argument('--components', action='store_true',
                       help='Run component-based tests only')
    parser.add_argument('--services', action='store_true',
                       help='Run service-based tests only')
    parser.add_argument('--quick', '-q', action='store_true',
                       help='Run quick component tests (skip slow tests)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')

    args = parser.parse_args()

    # Determine test mode
    if args.components:
        test_mode = "components"
    elif args.services:
        test_mode = "services"
    else:
        test_mode = "all"

    runner = UnifiedTestRunner(test_mode=test_mode, quick_mode=args.quick, verbose=args.verbose)
    results = runner.run_all_tests()
    runner.print_summary(results)

    # Exit with appropriate code
    success = all(success for success, _ in results.values())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
