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

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

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
        """,
    )

    parser.add_argument(
        "--components", action="store_true", help="Run component-based tests only"
    )
    parser.add_argument(
        "--services", action="store_true", help="Run service-based tests only"
    )
    parser.add_argument(
        "--quick",
        "-q",
        action="store_true",
        help="Run quick component tests (skip slow tests)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Determine test mode
    if args.components:
        test_mode = "components"
    elif args.services:
        test_mode = "services"
    else:
        test_mode = "all"

    runner = UnifiedTestRunner(
        test_mode=test_mode, quick_mode=args.quick, verbose=args.verbose
    )
    results = runner.run_all_tests()
    runner.print_summary(results)

    # Exit with appropriate code
    success = all(success for success, _ in results.values())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
