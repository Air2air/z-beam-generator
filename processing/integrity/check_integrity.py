#!/usr/bin/env python3
"""
System Integrity Check CLI
===========================

Standalone tool to verify system health.

Usage:
    python3 -m processing.integrity.check_integrity        # Run all checks
    python3 -m processing.integrity.check_integrity --quick # Run fast checks only
    python3 -m processing.integrity.check_integrity --json  # Output JSON
"""

import sys
import json
import argparse
from processing.integrity import IntegrityChecker


def main():
    parser = argparse.ArgumentParser(description='Run system integrity checks')
    parser.add_argument('--quick', action='store_true', 
                        help='Run only fast checks (skip API health, tests)')
    parser.add_argument('--json', action='store_true',
                        help='Output results as JSON')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed check information')
    parser.add_argument('--fail-on-warn', action='store_true',
                        help='Exit with error code if warnings detected')
    
    args = parser.parse_args()
    
    # Run checks
    checker = IntegrityChecker()
    
    if args.quick:
        results = checker.run_quick_checks()
    else:
        results = checker.run_all_checks()
    
    # Output results
    if args.json:
        summary = checker.get_summary_dict(results)
        print(json.dumps(summary, indent=2))
    else:
        checker.print_report(results, verbose=args.verbose)
    
    # Exit code
    if checker.has_failures(results):
        sys.exit(1)  # Failures always exit with error
    elif args.fail_on_warn and checker.has_warnings(results):
        sys.exit(2)  # Warnings exit with error if --fail-on-warn
    else:
        sys.exit(0)  # Success


if __name__ == '__main__':
    main()
