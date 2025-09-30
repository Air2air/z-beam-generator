#!/usr/bin/env python3
"""
Z-Beam Cleanup Manager

Standalone cleanup system decoupled from test framework.
Provides comprehensive project maintenance and file organization.
"""

import argparse
from pathlib import Path

from cleanup.test_cleanup import CleanupManager


def main():
    parser = argparse.ArgumentParser(description="Z-Beam Cleanup Manager")
    parser.add_argument("--scan", action="store_true", help="Run cleanup scan")
    parser.add_argument(
        "--report", action="store_true", help="Generate detailed report"
    )
    parser.add_argument("--summary", action="store_true", help="Show quick summary")

    args = parser.parse_args()

    manager = CleanupManager(Path.cwd())

    if args.summary or (not args.scan and not args.report):
        print(manager.get_summary())
    elif args.scan:
        results = manager.scan()
        print(f"Found {results['total_issues']} cleanup opportunities")
        for category, items in results["categories"].items():
            print(f"  {category}: {len(items)} items")
    elif args.report:
        report_path = manager.generate_report()
        print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()
