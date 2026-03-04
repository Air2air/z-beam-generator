#!/usr/bin/env python3
"""Run canonical end-to-end contract/parity validation in one command."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

CHECKS = [
    (
        "Prompt/section contract",
        [sys.executable, "scripts/validation/validate_prompt_section_contract.py"],
    ),
    (
        "Text contract artifact",
        [sys.executable, "scripts/validation/validate_text_contract_artifact.py"],
    ),
    (
        "Field contract parity",
        [sys.executable, "scripts/validation/validate_field_contract_parity.py", "--all-domains"],
    ),
    (
        "Prompt source centralization",
        [sys.executable, "scripts/validation/validate_prompt_source_centralization.py"],
    ),
    (
        "Domain bootstrap integrity",
        [sys.executable, "scripts/validation/validate_domain_bootstrap.py"],
    ),
    (
        "Catalog subject resolution",
        [sys.executable, "scripts/validation/validate_catalog_subject_resolution.py"],
    ),
    (
        "Full-page text field contract",
        [sys.executable, "-m", "pytest", "tests/services/test_full_page_text_fields_contract.py", "-q"],
    ),
]


def run_check(name: str, command: list[str]) -> int:
    print(f"\n=== {name} ===")
    result = subprocess.run(command, cwd=REPO_ROOT)
    if result.returncode == 0:
        print(f"✅ {name} passed")
    else:
        print(f"❌ {name} failed (exit {result.returncode})")
    return result.returncode


def main() -> int:
    failures = 0
    for name, command in CHECKS:
        rc = run_check(name, command)
        if rc != 0:
            failures += 1

    print("\n=== Canonical Pipeline Validation Summary ===")
    if failures == 0:
        print("✅ All checks passed")
        return 0

    print(f"❌ {failures} check(s) failed")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
