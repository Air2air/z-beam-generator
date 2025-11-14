# Category Range Compliance Testing

## Overview

The `test_category_range_compliance.py` test suite validates that all material property values in frontmatter files fall within their defined category ranges from `Categories.yaml`. This is a **critical data quality check** that should be run on every commit.

## Test Suite Details

### Test File
```
tests/test_category_range_compliance.py
```

### Test Coverage
- **122 materials** validated
- **2,073 properties** checked
- **9 categories** covered (ceramic, metal, glass, plastic, wood, stone, composite, semiconductor, masonry)

### Test Functions

| Test | Marker | Purpose | Status |
|------|--------|---------|--------|
| `test_all_materials_have_valid_ranges` | `smoke` | Main validation - checks all property values | ❌ 115 violations |
| `test_category_ranges_exist` | `unit` | Verifies Categories.yaml structure | ✅ Passing |
| `test_critical_properties_have_ranges` | `unit` | Ensures key properties have ranges | ✅ Passing |
| `test_no_zero_ranges` | `unit` | No min == max ranges | ✅ Passing |
| `test_ranges_have_proper_units` | `unit` | All ranges have units | ❌ 1 missing |
| `test_sample_materials_spot_check` | `smoke` | Validates specific materials | ❌ Edge case |

## Running the Tests

### Full Test Suite
```bash
# Run all range compliance tests
pytest tests/test_category_range_compliance.py -v

# Run with detailed output
pytest tests/test_category_range_compliance.py -v -s
```

### Specific Test Categories

**Run only smoke tests** (quick validation):
```bash
pytest tests/test_category_range_compliance.py -m smoke -v
```

**Run only unit tests** (fast structure checks):
```bash
pytest tests/test_category_range_compliance.py -m unit -v
```

**Run with data validation marker**:
```bash
pytest -m data_validation -v
```

### Standalone Script
```bash
# Run as standalone script for detailed report
python3 tests/test_category_range_compliance.py
```

## Test Markers

The test suite uses the following pytest markers:

- `@pytest.mark.data_validation` - Module-level marker for all tests
- `@pytest.mark.integration` - Module-level marker (requires Categories.yaml and frontmatter files)
- `@pytest.mark.regression` - Module-level marker (prevents regression of data quality)
- `@pytest.mark.smoke` - Quick critical validation tests
- `@pytest.mark.unit` - Fast structure/configuration tests

## Integration with CI/CD

### Recommended CI Configuration

```yaml
# GitHub Actions example
- name: Run Range Compliance Tests
  run: |
    pytest tests/test_category_range_compliance.py -v --tb=short
  continue-on-error: true  # Allow pipeline to continue but flag issues

# Or for strict enforcement:
- name: Run Critical Data Validation
  run: |
    pytest -m "data_validation and smoke" -v
```

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Run quick range compliance smoke tests
pytest tests/test_category_range_compliance.py -m smoke -q
if [ $? -ne 0 ]; then
    echo "❌ Range compliance tests failed. Fix violations before committing."
    exit 1
fi
```

## Current Status

### Known Issues (as of Oct 15, 2025)

**115 violations found** across categories:

1. **Unit conversion issues** (39 cases):
   - SpecificHeat values appear to be kJ/kg·K not J/kg·K
   - Example: Birch `1.38 J/kg·K` should be `1380 J/kg·K`

2. **Scale/multiplier issues** (18 cases):
   - Wood hardness values need multiplier
   - Example: Oak `5.0 lbf` should be `500 lbf`

3. **Decimal placement errors** (10 cases):
   - Beech density: `720 g/cm³` should be `0.72 g/cm³`
   - Various oxidationResistance values

4. **Category range adjustments needed** (48 cases):
   - Specialty materials legitimately exceed current ranges
   - Examples: Copper (98.6%), Silver (429 W/(m·K))

See `RANGE_COMPLIANCE_TEST_RESULTS.md` for detailed breakdown.

## Fixing Violations

### Priority Actions

**High Priority** (Data Errors):
```bash
# Fix unit conversions
python3 scripts/fix_unit_conversions.py

# Fix decimal placement
python3 scripts/fix_decimal_errors.py
```

**Medium Priority** (Range Adjustments):
```bash
# Update category ranges for specialty materials
# Edit data/Categories.yaml manually or use:
python3 scripts/adjust_category_ranges.py
```

### Validation Workflow

1. Fix data issues
2. Re-run tests: `pytest tests/test_category_range_compliance.py`
3. Review remaining violations
4. Adjust category ranges if legitimate exceptions
5. Repeat until all tests pass

## Test Output Examples

### Passing Test
```
tests/test_category_range_compliance.py::TestCategoryRangeCompliance::test_category_ranges_exist PASSED

✅ Range Validation Passed:
   Files checked: 122
   Properties validated: 2073
   Violations: 0
```

### Failing Test
```
tests/test_category_range_compliance.py::TestCategoryRangeCompliance::test_all_materials_have_valid_ranges FAILED

❌ RANGE VIOLATIONS FOUND: 115 properties outside category ranges

Material: Copper (metal)
  Property: laserReflectivity
  Value: 98.6 %
  Expected range: 5 - 98 %
  File: copper-laser-cleaning.yaml
```

## Performance

- **Test execution time**: ~3 seconds for full suite
- **Smoke tests only**: ~1 second
- **Unit tests only**: <0.1 seconds

## Dependencies

- `pytest` - Test framework
- `pytest-markers` - Test categorization
- `pyyaml` - YAML parsing
- Python 3.12+

No external API calls required - tests run entirely offline.

## Related Documentation

- `RANGE_COMPLIANCE_TEST_RESULTS.md` - Detailed violation analysis
- `docs/DATA_ARCHITECTURE.md` - Data structure documentation
- `data/Categories.yaml` - Source of truth for ranges
- `CATEGORY_RANGES_VALIDATION_REPORT.md` - Manual validation report

## Troubleshooting

### Test Collection Fails
```bash
# Verify pytest can find the test
pytest tests/test_category_range_compliance.py --collect-only
```

### Import Errors
```bash
# Ensure PYTHONPATH includes project root
export PYTHONPATH=/path/to/z-beam-generator:$PYTHONPATH
pytest tests/test_category_range_compliance.py
```

### Timeout Issues
```bash
# Increase timeout if needed (default: 30s)
pytest tests/test_category_range_compliance.py --timeout=60
```

## Contributing

When adding new materials or modifying category ranges:

1. Run the full test suite
2. Fix any violations introduced
3. Update category ranges if legitimate exceptions
4. Document reasoning in commit message
5. Ensure all tests pass before merging

## Contact

For questions about range compliance testing:
- See `GROK_INSTRUCTIONS.md` for fail-fast principles
- See `DATA_ARCHITECTURE.md` for range propagation logic
- See `docs/QUICK_REFERENCE.md` for common issues
