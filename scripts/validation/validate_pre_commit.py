#!/usr/bin/env python3
"""
Pre-commit hook for data validation.

This script runs quick validation checks before allowing a commit.
Install with: ln -s ../../scripts/validation/validate_pre_commit.py .git/hooks/pre-commit

Exit codes:
  0 - Validation passed
  1 - Critical errors found (block commit)
  2 - Warnings only (allow commit with message)
"""

import sys
import subprocess
from pathlib import Path

def get_staged_yaml_files():
    """Get list of staged YAML files"""
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
        capture_output=True,
        text=True
    )
    
    files = result.stdout.strip().split('\n')
    yaml_files = [f for f in files if f.endswith('.yaml') or f.endswith('.yml')]
    
    # Filter for relevant files
    relevant = []
    for f in yaml_files:
        if 'frontmatter' in f or \
           'data/Categories.yaml' in f or \
           'data/Materials.yaml' in f:
            relevant.append(f)
    
    return relevant

def run_validation():
    """Run comprehensive validation"""
    print("🔍 Running data quality validation...")
    
    result = subprocess.run(
        ['python3', 'scripts/validation/comprehensive_validation_agent.py'],
        capture_output=True,
        text=True
    )
    
    return result.returncode, result.stdout, result.stderr

def main():
    # Check if we're in the right directory
    if not Path('scripts/validation/comprehensive_validation_agent.py').exists():
        print("❌ Validation script not found. Are you in the project root?")
        sys.exit(1)
    
    # Get staged YAML files
    staged_files = get_staged_yaml_files()
    
    if not staged_files:
        print("✅ No YAML data files to validate.")
        sys.exit(0)
    
    print(f"📝 Validating {len(staged_files)} staged YAML file(s)...")
    for f in staged_files:
        print(f"  - {f}")
    print()
    
    # Run validation
    exit_code, stdout, stderr = run_validation()
    
    # Parse validation results
    import json
    try:
        with open('validation_report.json') as f:
            report = json.load(f)
        
        errors = len(report.get('ERROR', []))
        warnings = len(report.get('WARNING', []))
        
        print("\n" + "=" * 70)
        print("VALIDATION RESULTS")
        print("=" * 70)
        print(f"Errors:   {errors}")
        print(f"Warnings: {warnings}")
        print("=" * 70)
        
        if errors > 0:
            print("\n❌ COMMIT BLOCKED: Critical errors found!")
            print("\nTop errors:")
            for error in report['ERROR'][:5]:
                print(f"  • {error['material']}: {error['message']}")
            
            if len(report['ERROR']) > 5:
                print(f"  ... and {len(report['ERROR']) - 5} more")
            
            print("\nRun: python3 scripts/validation/comprehensive_validation_agent.py")
            print("To see full validation report.")
            print("\nTo bypass this check (not recommended):")
            print("  git commit --no-verify")
            sys.exit(1)
        
        elif warnings > 0:
            print("\n⚠️  WARNINGS FOUND (commit allowed)")
            print("\nTop warnings:")
            for warning in report['WARNING'][:3]:
                print(f"  • {warning['material']}: {warning['message']}")
            
            if len(report['WARNING']) > 3:
                print(f"  ... and {len(report['WARNING']) - 3} more")
            
            print("\nReview recommended but commit will proceed.")
            sys.exit(0)
        
        else:
            print("\n✅ All validations passed!")
            sys.exit(0)
    
    except FileNotFoundError:
        print("\n❌ Validation report not found. Validation may have failed.")
        print(stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print("\n❌ Could not parse validation report.")
        sys.exit(1)

if __name__ == '__main__':
    main()
