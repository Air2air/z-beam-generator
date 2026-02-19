#!/usr/bin/env python3
"""
Deployment orchestrator for frontmatter export.

Usage:
    python3 scripts/operations/deploy_all.py --skip-tests
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOMAINS = ["materials", "contaminants", "compounds", "settings"]


def run_command(command: list[str]) -> int:
    """Run a command from project root and stream output."""
    process = subprocess.run(command, cwd=PROJECT_ROOT)
    return process.returncode


def run_exports() -> int:
    """Export all supported domains."""
    print("=" * 80)
    print("🚀 STARTING DEPLOYMENT")
    print("=" * 80)

    for domain in DOMAINS:
        print(f"\n📦 Exporting domain: {domain}")
        exit_code = run_command(["python3", "run.py", "--export", "--domain", domain])
        if exit_code != 0:
            print(f"❌ Export failed for domain: {domain} (exit code: {exit_code})")
            return exit_code

    print("\n" + "=" * 80)
    print("✅ DEPLOYMENT COMPLETE")
    print("=" * 80)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deploy all frontmatter domains")
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Accepted for compatibility; deployment runs exports only.",
    )
    return parser.parse_args()


def main() -> int:
    _ = parse_args()
    return run_exports()


if __name__ == "__main__":
    sys.exit(main())
