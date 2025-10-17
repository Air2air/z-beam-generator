# Z-Beam Generator - Makefile
# Data quality validation and automation

.PHONY: help validate validate-strict test clean install-hooks

# Default target
help:
	@echo "Z-Beam Generator - Data Quality Commands"
	@echo ""
	@echo "Available targets:"
	@echo "  make validate        - Run data validation (warnings allowed)"
	@echo "  make validate-strict - Run validation (fail on any errors)"
	@echo "  make validate-report - Generate detailed validation report"
	@echo "  make fix-units       - Auto-fix unit standardization issues"
	@echo "  make fix-values      - Auto-fix qualitative value issues"
	@echo "  make install-hooks   - Install pre-commit validation hook"
	@echo "  make test            - Run all tests including validation"
	@echo "  make clean           - Clean generated reports and caches"
	@echo ""

# Run validation (allow warnings)
validate:
	@echo "Running data quality validation..."
	@python3 scripts/validation/comprehensive_validation_agent.py || true
	@echo ""
	@echo "✅ Validation complete. Check validation_report.json for details."

# Run validation (strict mode - fail on errors)
validate-strict:
	@echo "Running strict data quality validation..."
	@python3 scripts/validation/comprehensive_validation_agent.py
	@echo ""
	@echo "✅ All validations passed!"

# Generate detailed report
validate-report: validate
	@echo ""
	@echo "Generating detailed HTML report..."
	@python3 << 'EOF'
import json
from datetime import datetime

with open('validation_report.json') as f:
    report = json.load(f)

errors = report.get('ERROR', [])
warnings = report.get('WARNING', [])

html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Data Validation Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .error {{ color: #d32f2f; }}
        .warning {{ color: #f57c00; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #333; color: white; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>Data Quality Validation Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p><span class="error">Errors: {len(errors)}</span></p>
        <p><span class="warning">Warnings: {len(warnings)}</span></p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <h2 class="error">Errors ({len(errors)})</h2>
    <table>
        <tr>
            <th>Material</th>
            <th>Type</th>
            <th>Message</th>
        </tr>
"""

for error in errors:
    html += f"""
        <tr>
            <td>{error.get('material', 'N/A')}</td>
            <td>{error.get('type', 'N/A')}</td>
            <td>{error.get('message', 'N/A')}</td>
        </tr>
"""

html += f"""
    </table>
    
    <h2 class="warning">Warnings ({len(warnings)})</h2>
    <table>
        <tr>
            <th>Material</th>
            <th>Type</th>
            <th>Message</th>
        </tr>
"""

for warning in warnings[:50]:  # Limit to first 50
    html += f"""
        <tr>
            <td>{warning.get('material', 'N/A')}</td>
            <td>{warning.get('type', 'N/A')}</td>
            <td>{warning.get('message', 'N/A')}</td>
        </tr>
"""

if len(warnings) > 50:
    html += f"""
        <tr>
            <td colspan="3"><em>... and {len(warnings) - 50} more warnings</em></td>
        </tr>
"""

html += """
    </table>
</body>
</html>
"""

with open('validation_report.html', 'w') as f:
    f.write(html)

print("✅ HTML report generated: validation_report.html")
EOF

# Auto-fix unit standardization
fix-units:
	@echo "Running unit standardization fixes..."
	@python3 scripts/validation/fix_unit_standardization.py
	@echo ""
	@echo "✅ Unit fixes complete. Run 'make validate' to verify."

# Auto-fix qualitative values
fix-values:
	@echo "Running qualitative value fixes..."
	@python3 scripts/validation/fix_qualitative_values.py
	@echo ""
	@echo "✅ Value fixes complete. Run 'make validate' to verify."

# Install pre-commit hook
install-hooks:
	@echo "Installing pre-commit validation hook..."
	@chmod +x scripts/validation/validate_pre_commit.py
	@mkdir -p .git/hooks
	@ln -sf ../../scripts/validation/validate_pre_commit.py .git/hooks/pre-commit
	@echo "✅ Pre-commit hook installed!"
	@echo ""
	@echo "The hook will run automatically on 'git commit'."
	@echo "To bypass: git commit --no-verify"

# Run all tests
test: validate
	@echo "Running pytest..."
	@pytest tests/ -v

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	@rm -f validation_report.json
	@rm -f validation_report.html
	@rm -f unit_fixes_report.json
	@rm -f qualitative_fixes_report.json
	@rm -f remaining_fixes_report.json
	@rm -f ratio_analysis_report.json
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete!"
