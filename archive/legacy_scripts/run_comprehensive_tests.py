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

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

    parser = argparse.ArgumentParser(
        description="Comprehensive Test Runner for Z-Beam Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python3 run_comprehensive_tests.py              # Full test suite
  python3 run_comprehensive_tests.py --quick      # Core tests only
  python3 run_comprehensive_tests.py --verbose    # Detailed output
  python3 run_comprehensive_tests.py --quick --verbose  # Quick with details
        """,
    )

    parser.add_argument(
        "--quick",
        "-q",
        action="store_true",
        help="Run quick test suite (skip slow tests)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    runner = ComprehensiveTestRunner(quick_mode=args.quick, verbose=args.verbose)
    results = runner.run_all_tests()
    runner.print_summary(results)

    # Exit with appropriate code
    success = all(success for success, _ in results.values())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
