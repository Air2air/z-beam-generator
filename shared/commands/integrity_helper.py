"""
Pre-Generation Integrity Check Helper

Runs system integrity checks before component generation.
"""

from processing.integrity import IntegrityChecker


def run_pre_generation_check(skip_check: bool = False, quick: bool = True) -> bool:
    """
    Run system integrity checks before generation.
    
    Args:
        skip_check: If True, skip the integrity check entirely
        quick: If True, run only fast checks (recommended for pre-gen)
    
    Returns:
        True if checks passed (or were skipped), False if checks failed
    """
    if skip_check:
        return True
    
    print("🔍 Running pre-generation integrity check...")
    
    try:
        checker = IntegrityChecker()
        
        if quick:
            results = checker.run_quick_checks()
        else:
            results = checker.run_all_checks()
        
        # Check for failures
        if checker.has_failures(results):
            print("❌ INTEGRITY CHECK FAILED")
            checker.print_report(results, verbose=False)
            print("\n⚠️  Fix integrity issues before generating content.")
            print("    Run: python3 run.py --integrity-check --quick")
            return False
        
        # Check for warnings
        if checker.has_warnings(results):
            print("⚠️  Integrity check passed with warnings")
            # Show summary but don't block generation
            pass_count = sum(1 for r in results if r.status.value == "PASS")
            warn_count = sum(1 for r in results if r.status.value == "WARN")
            print(f"    {pass_count} passed, {warn_count} warnings")
        else:
            print("✅ System integrity verified")
            pass_count = sum(1 for r in results if r.status.value == "PASS")
            print(f"    {pass_count} checks passed")
        
        print()
        return True
        
    except Exception as e:
        print(f"⚠️  Integrity check error: {e}")
        print("    Continuing with generation (check failed gracefully)")
        print()
        return True  # Don't block generation on check errors


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
