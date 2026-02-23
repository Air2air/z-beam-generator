"""
Pre-Generation Integrity Check Helper

Runs system integrity checks before component generation.
Includes per-iteration learning architecture validation.
"""

import os

from generation.integrity import IntegrityChecker


def run_pre_generation_check(skip_check: bool = False, quick: bool = True, verbose: bool = False) -> bool:
    """
    Run system integrity checks before generation.
    
    Includes:
    - Configuration validation
    - Parameter propagation
    - Hardcoded value detection
    - Per-iteration learning architecture (NEW)
    - API health (if not quick mode)
    
    Args:
        skip_check: If True, skip the integrity check entirely
        quick: If True, run only fast checks (recommended for pre-gen)
        verbose: If True, show detailed check results
    
    Returns:
        True if checks passed (or were skipped), False if checks failed
    """
    if skip_check:
        if os.getenv("ALLOW_INTEGRITY_BYPASS") != "1":
            raise RuntimeError(
                "Integrity bypass denied: --skip-integrity-check requires ALLOW_INTEGRITY_BYPASS=1"
            )
        print("⚠️  Integrity checks skipped (ALLOW_INTEGRITY_BYPASS=1)")
        return True
    
    print("🔍 Running pre-generation integrity check...")
    print("   Validating: Config, Parameters, Learning Architecture")
    
    try:
        checker = IntegrityChecker()
        
        if quick:
            results = checker.run_quick_checks()
        else:
            results = checker.run_all_checks()
        
        # Check for failures
        if checker.has_failures(results):
            print("❌ INTEGRITY CHECK FAILED")
            
            # Show critical failures
            fail_results = [r for r in results if r.status.value == "FAIL"]
            print(f"\n⚠️  {len(fail_results)} CRITICAL ISSUES DETECTED:")
            for result in fail_results[:5]:  # Show first 5
                print(f"   ❌ {result.check_name}")
                print(f"      {result.message}")
            
            if len(fail_results) > 5:
                print(f"   ... and {len(fail_results) - 5} more issues")
            
            print("\n💡 Fix issues before generating content.")
            print("    Run: python3 run.py --integrity-check")
            return False
        
        # Check for warnings
        if checker.has_warnings(results):
            print("⚠️  Integrity check passed with warnings")
            # Show summary but don't block generation
            pass_count = sum(1 for r in results if r.status.value == "PASS")
            warn_count = sum(1 for r in results if r.status.value == "WARN")
            print(f"    {pass_count} passed, {warn_count} warnings")
            
            if verbose:
                warn_results = [r for r in results if r.status.value == "WARN"]
                for result in warn_results:
                    print(f"   ⚠️  {result.check_name}: {result.message}")
        else:
            print("✅ System integrity verified")
            pass_count = sum(1 for r in results if r.status.value == "PASS")
            print(f"    {pass_count} checks passed")
            
            # Highlight per-iteration learning validation
            learning_checks = [r for r in results if "Per-Iteration" in r.check_name]
            if learning_checks:
                learning_pass = sum(1 for r in learning_checks if r.status.value == "PASS")
                print(f"    ✅ Per-iteration learning: {learning_pass}/{len(learning_checks)} validated")
        
        
    except Exception as e:
        # FAIL-FAST: Do not continue with generation if integrity check itself fails
        # per GROK_INSTRUCTIONS.md Core Principle #5
        raise RuntimeError(
            f"Integrity check failed to execute: {e}. "
            f"Cannot proceed with generation. "
            f"Fix the integrity checker before attempting generation."
        )


def run_post_generation_validation(material: str, component_type: str, quick: bool = True) -> bool:
    """
    Run post-generation validation to verify learning data was captured.
    
    Validates:
    - Detection result logged to database
    - Generation parameters logged
    - Realism evaluation occurred (if applicable)
    - Learning data captured for iteration
    
    Args:
        material: Material name that was generated
        component_type: Component type (micro, subtitle, faq)
        quick: If True, skip expensive validations
    
    Returns:
        True if validation passed, False otherwise
    """
    try:
        print("🔍 Running post-generation validation...")
        
        checker = IntegrityChecker()
        results = checker.run_post_generation_checks(
            material=material,
            component_type=component_type,
            detection_id=None  # Will find latest
        )
        
        # Check results
        if checker.has_failures(results):
            print("⚠️  Post-generation validation found issues:")
            fail_results = [r for r in results if r.status.value == "FAIL"]
            for result in fail_results:
                print(f"   ❌ {result.check_name}: {result.message}")
            print()
            return False
        
        # All good
        print("✅ Post-generation validation passed")
        pass_count = sum(1 for r in results if r.status.value == "PASS")
        print(f"    {pass_count} checks passed")
        
    except Exception as e:
        # FAIL-FAST: Post-generation validation failure means learning data incomplete
        # per GROK_INSTRUCTIONS.md Core Principle #5
        raise RuntimeError(
            f"Post-generation validation failed: {e}. "
            f"Learning data may be incomplete or corrupted."
        )


def run_learning_architecture_tests(verbose: bool = False) -> bool:
    """
    Run integration tests for per-iteration learning architecture.
    
    This runs the pytest test suite to validate:
    - Realism evaluation on every iteration
    - Dual-objective scoring
    - Learning logged on success and failure
    - No global evaluation
    
    Args:
        verbose: If True, show detailed test output
    
    Returns:
        True if all tests passed, False otherwise
    """
    try:
        import subprocess
        import sys
        
        print("🧪 Running learning architecture integration tests...")
        print("   Test suite: tests/integration/test_per_iteration_learning.py")
        print()
        
        # Run pytest
        cmd = [
            sys.executable, '-m', 'pytest',
            'tests/integration/test_per_iteration_learning.py',
            '-v' if verbose else '-q',
            '--tb=short'
        ]
        
        result = subprocess.run(cmd, capture_output=not verbose)
        
        if result.returncode == 0:
            print("✅ All learning architecture tests passed")
            return True
        else:
            print("❌ Some learning architecture tests failed")
            if not verbose:
                print("   Run with --verbose for details:")
                print("   pytest tests/integration/test_per_iteration_learning.py -v")
            
    except Exception as e:
        print(f"⚠️  Could not run learning architecture tests: {e}")
        print("    Note: Test infrastructure unavailable (pytest not installed?)")
        # Return False to indicate tests didn't pass (even though infrastructure missing)
        # This is acceptable for optional test validation, but should be documented
        return False


def get_integrity_summary() -> dict:
    """
    Get a quick integrity summary for status reporting.
    
    Returns:
        Dict with summary information
    """
    try:
        checker = IntegrityChecker()
        results = checker.run_quick_checks()
        return checker.get_summary_dict(results)
    except Exception as e:
        return {
            'error': str(e),
            'total_checks': 0,
            'passed': 0,
            'warnings': 0,
            'failed': 0,
            'has_failures': False,
            'has_warnings': False
        }
