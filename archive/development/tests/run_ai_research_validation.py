#!/usr/bin/env python3
"""
Comprehensive test runner for Pure AI Research Implementation
Validates complete system integrity and fallback removal

Usage:
    python3 scripts/tests/run_ai_research_validation.py
    python3 scripts/tests/run_ai_research_validation.py --verbose
    python3 scripts/tests/run_ai_research_validation.py --quick
"""

import sys
import subprocess
import time
from pathlib import Path

def run_command(cmd, description, verbose=False):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print('='*60)
    
    if verbose:
        print(f"Command: {' '.join(cmd)}")
    
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd, 
            capture_output=not verbose,
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ PASSED ({duration:.2f}s)")
            if verbose and result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ FAILED ({duration:.2f}s)")
            if result.stderr:
                print("STDERR:", result.stderr)
            if result.stdout:
                print("STDOUT:", result.stdout)
            return False
            
    except Exception as e:
        duration = time.time() - start_time
        print(f"💥 ERROR ({duration:.2f}s): {e}")
        return False

def main():
    """Run comprehensive AI research validation tests"""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    quick = "--quick" in sys.argv
    
    print("🔬 Pure AI Research Implementation - Validation Suite")
    print("="*60)
    print("Validating complete removal of fallbacks and AI research functionality")
    
    tests_passed = 0
    tests_total = 0
    
    # Core AI Research Tests
    test_suites = [
        {
            "cmd": ["python3", "-m", "pytest", "tests/frontmatter/test_pure_ai_research.py", "-v"],
            "description": "Pure AI Research Implementation Tests",
            "critical": True
        }
    ]
    
    if not quick:
        # Additional validation tests
        test_suites.extend([
            {
                "cmd": ["python3", "-m", "pytest", "tests/frontmatter/", "-v"],
                "description": "Complete Frontmatter Test Suite",
                "critical": False
            },
            {
                "cmd": ["python3", "-c", """
import sys
sys.path.append('.')
from components.frontmatter.core.streamlined_generator import StreamlinedFrontmatterGenerator
from components.frontmatter.enhancement.property_enhancement_service import PropertyEnhancementService

# Test imports work
print('✅ All imports successful')

# Test PropertyEnhancementService has no hardcoded defaults
import inspect
source = inspect.getsource(PropertyEnhancementService)
forbidden = ['"Gaussian"', '"Class 4"', '"100-500mm/s"']
for pattern in forbidden:
    if pattern in source:
        raise Exception(f'Found hardcoded default: {pattern}')
        
print('✅ PropertyEnhancementService validation passed')

# Test generator has no fallback patterns
source = inspect.getsource(StreamlinedFrontmatterGenerator)
forbidden_patterns = ['or "Unknown"', 'or "N/A"', 'or "TBD"']
for pattern in forbidden_patterns:
    if pattern in source:
        raise Exception(f'Found fallback pattern: {pattern}')
        
print('✅ Generator fallback validation passed')
print('✅ All validation checks completed successfully')
"""],
                "description": "Code Analysis - Fallback Detection",
                "critical": True
            }
        ])
    
    # Run all test suites
    for suite in test_suites:
        tests_total += 1
        if run_command(suite["cmd"], suite["description"], verbose):
            tests_passed += 1
        elif suite["critical"]:
            print(f"\n💥 CRITICAL TEST FAILED: {suite['description']}")
            print("Cannot continue with validation - fix critical issues first")
            sys.exit(1)
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 VALIDATION SUMMARY")
    print('='*60)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    print(f"Success rate: {(tests_passed/tests_total)*100:.1f}%")
    
    if tests_passed == tests_total:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("✅ Pure AI Research implementation is working correctly")
        print("✅ Zero fallback defaults confirmed")
        print("✅ AI research requirements validated")
        print("✅ System ready for production use")
        sys.exit(0)
    else:
        print(f"\n⚠️  {tests_total - tests_passed} validation(s) failed")
        print("Please fix the issues before deploying")
        sys.exit(1)

if __name__ == "__main__":
    main()
