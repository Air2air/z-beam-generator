#!/usr/bin/env python3
"""
validate_data_completeness.py

Threshold-based source-data completeness validator.

Purpose:
- Reuse scripts/audit/data_completeness.py analysis logic
- Produce machine-readable JSON artifact for CI/reporting
- Fail build when severity counts exceed configured thresholds

Examples:
  python3 scripts/validation/validate_data_completeness.py
  python3 scripts/validation/validate_data_completeness.py --max-critical 0 --max-high 0
  python3 scripts/validation/validate_data_completeness.py --max-medium -1 --max-low -1
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.audit.data_completeness import build_report, run_audit

SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW")


def evaluate_thresholds(
    severity_counts: Dict[str, int],
    max_critical: int,
    max_high: int,
    max_medium: int,
    max_low: int,
) -> Tuple[bool, List[str]]:
    """Return pass/fail and violation messages for severity thresholds.

    A threshold of -1 disables enforcement for that severity.
    """
    limits = {
        "CRITICAL": max_critical,
        "HIGH": max_high,
        "MEDIUM": max_medium,
        "LOW": max_low,
    }

    violations: List[str] = []
    for severity in SEVERITIES:
        limit = limits[severity]
        count = severity_counts.get(severity, 0)
        if limit >= 0 and count > limit:
            violations.append(
                f"{severity}: {count} > allowed {limit}"
            )

    return len(violations) == 0, violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate source data completeness with severity thresholds")
    parser.add_argument("--max-critical", type=int, default=0, help="Max allowed CRITICAL findings (default: 0)")
    parser.add_argument("--max-high", type=int, default=0, help="Max allowed HIGH findings (default: 0)")
    parser.add_argument("--max-medium", type=int, default=-1, help="Max allowed MEDIUM findings (-1 disables)")
    parser.add_argument("--max-low", type=int, default=-1, help="Max allowed LOW findings (-1 disables)")
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("tasks/data_completeness_report.json"),
        help="Output path for machine-readable JSON report",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("tasks/data_completeness_report.md"),
        help="Output path for markdown report",
    )

    args = parser.parse_args()

    findings, domain_items = run_audit()
    severity_counts = Counter(f.severity for f in findings)

    report_md = build_report(findings, domain_items)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(report_md, encoding="utf-8")

    findings_json = [
        {
            "severity": f.severity,
            "domain": f.domain,
            "itemId": f.item_id,
            "field": f.field,
            "message": f.message,
        }
        for f in findings
    ]

    summary = {
        "totals": {severity: severity_counts.get(severity, 0) for severity in SEVERITIES},
        "totalFindings": len(findings),
        "domainItemCounts": {domain: len(items) for domain, items in domain_items.items()},
        "thresholds": {
            "maxCritical": args.max_critical,
            "maxHigh": args.max_high,
            "maxMedium": args.max_medium,
            "maxLow": args.max_low,
        },
        "reports": {
            "markdown": str(args.output_md),
            "json": str(args.output_json),
        },
        "findings": findings_json,
    }

    passed, violations = evaluate_thresholds(
        severity_counts,
        max_critical=args.max_critical,
        max_high=args.max_high,
        max_medium=args.max_medium,
        max_low=args.max_low,
    )

    summary["passed"] = passed
    summary["violations"] = violations

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("DATA COMPLETENESS VALIDATION")
    for severity in SEVERITIES:
        print(f"  {severity:8}: {severity_counts.get(severity, 0)}")
    print(f"  TOTAL   : {len(findings)}")
    print(f"  JSON    : {args.output_json}")
    print(f"  MARKDOWN: {args.output_md}")

    if passed:
        print("✅ Thresholds satisfied")
        return 0

    print("❌ Thresholds exceeded")
    for violation in violations:
        print(f"  - {violation}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
