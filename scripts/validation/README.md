# Data Quality Validation System

Comprehensive validation infrastructure for Z-Beam material properties database.

## Quick Start

```bash
# Run validation
python3 scripts/validation/comprehensive_validation_agent.py

# Or use make
make validate
```

## Integration Options

### 1. GitHub Actions (CI/CD) ✅ RECOMMENDED

Already configured in `.github/workflows/data-validation.yml`

**Features:**
- ✅ Runs on every push to main/develop
- ✅ Runs on pull requests
- ✅ Uploads validation report artifacts
- ✅ Posts results as PR comment
- ✅ Blocks merge if critical errors found

**Manual trigger:**
```bash
# From GitHub UI: Actions → Data Quality Validation → Run workflow
```

### 2. Pre-commit Hook (Local Development)

Install validation hook to run before every commit:

```bash
make install-hooks
```

Or manually:
```bash
chmod +x scripts/validation/validate_pre_commit.py
ln -s ../../scripts/validation/validate_pre_commit.py .git/hooks/pre-commit
```

**Behavior:**
- 🔴 **Blocks commit** if critical errors found
- 🟡 **Allows commit** with warnings (shows message)
- ✅ **Silent pass** if no issues

**Bypass (not recommended):**
```bash
git commit --no-verify
```

### 3. Make Commands (Development Workflow)

```bash
make validate          # Run validation (warnings allowed)
make validate-strict   # Fail on any errors
make validate-report   # Generate HTML report
make fix-units         # Auto-fix unit issues
make fix-values        # Auto-fix qualitative values
make install-hooks     # Install pre-commit hook
make test              # Run all tests + validation
make clean             # Clean generated files
```

### 4. Direct Python Script

```bash
# Basic validation
python3 scripts/validation/comprehensive_validation_agent.py

# With verbose output
python3 scripts/validation/comprehensive_validation_agent.py --verbose

# Exit codes:
#   0 = No errors (warnings allowed)
#   1 = Critical errors found
```

### 5. Automated Fixes

```bash
# Fix unit standardization issues
python3 scripts/validation/fix_unit_standardization.py

# Fix qualitative/numeric mismatches
python3 scripts/validation/fix_qualitative_values.py

# Fix remaining simple errors
python3 scripts/validation/fix_remaining_errors.py

# Analyze E/TS ratio issues
python3 scripts/validation/analyze_ratio_errors.py
```

## Validation Levels

### 1. Property-Level Validation
- Unit standardization
- Value range checks (physical limits)
- Category-specific ranges
- Confidence threshold monitoring

### 2. Relationship-Level Validation
- Optical energy conservation: A + R ≤ 100%
- Thermal diffusivity: α = k / (ρ × Cp)
- Young's modulus / tensile strength ratios
- Electrical conductivity × resistivity = 1

### 3. Category-Level Validation
- Required properties enforcement
- Forbidden properties detection
- Material taxonomy completeness

## Output Files

```
validation_report.json          # Detailed error/warning list
validation_report.html          # Human-readable HTML report
unit_fixes_report.json          # Unit corrections log
qualitative_fixes_report.json   # Value conversion log
remaining_fixes_report.json     # Magnitude correction log
ratio_analysis_report.json      # E/TS ratio analysis
```

## Current Status

**Errors**: 21 (1.2% error rate)  
**Warnings**: 114  
**Validation Coverage**: 122 materials, 55 properties  

## Category-Specific E/TS Ratio Thresholds

```python
metal:        100-500
ceramic:      500-2000
stone:        500-15000
glass:        500-3000
wood:         50-300
plastic:      30-200
composite:    30-500
semiconductor: 100-1000
masonry:      500-10000
```

## Troubleshooting

### "Validation script not found"
**Solution:** Run from project root directory

### "No module named 'yaml'"
**Solution:** `pip install -r requirements.txt`

### Pre-commit hook not running
**Solution:** 
```bash
chmod +x scripts/validation/validate_pre_commit.py
ls -la .git/hooks/pre-commit  # Should show symlink
```

### Want to skip validation once
**Solution:** `git commit --no-verify`

## Architecture

```
comprehensive_validation_agent.py
├── PROPERTY_RULES (28 rules)
│   ├── Unit validation
│   ├── Range checking
│   └── Category-specific ranges
├── RELATIONSHIP_RULES (4 rules)
│   ├── Optical energy conservation
│   ├── Thermal diffusivity formula
│   ├── E/TS ratios (category-specific)
│   └── Conductivity/resistivity
└── CATEGORY_RULES (9 categories)
    ├── Required properties
    ├── Forbidden properties
    └── Typical ranges
```

## Documentation

- `FINAL_VALIDATION_REPORT.md` - Complete system overview
- `VALIDATION_DEPLOYMENT_COMPLETE.md` - Deployment summary
- `DATA_QUALITY_VALIDATION_REPORT.md` - Technical details
- `VALIDATION_SYSTEM_COMPLETE.md` - Quick reference

## Performance

- **Runtime**: ~2 seconds for 122 materials
- **Memory**: < 100MB
- **Automated Fix Rate**: 40% (119 of 294 issues)
- **False Positive Rate**: < 5%

## Support

For issues or questions:
1. Check validation report: `validation_report.json`
2. Review documentation in root directory
3. Run analysis: `python3 scripts/validation/analyze_ratio_errors.py`

---

**Status**: ✅ Production Ready  
**Last Updated**: October 16, 2025  
**Version**: 1.0.0
