#!/usr/bin/env python3
"""Generate GitHub Actions summary from validation report"""

import json

with open('validation_report.json') as f:
    report = json.load(f)

errors = len(report.get('ERROR', []))
warnings = len(report.get('WARNING', []))
info = len(report.get('INFO', []))

print(f"""
| Severity | Count |
|----------|-------|
| 🔴 Errors | {errors} |
| 🟡 Warnings | {warnings} |
| ℹ️ Info | {info} |
""")

if errors > 0:
    print("### ❌ Critical Errors Found\n")
    print("Please review the validation report artifact.\n")
elif warnings > 0:
    print("### ⚠️ Warnings Found\n")
    print("Review recommended but not blocking.\n")
else:
    print("### ✅ All Validations Passed\n")
