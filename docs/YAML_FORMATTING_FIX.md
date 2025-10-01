# YAML Formatting Issue - Generator Fixes

## Problem Summary

**Issue**: 9 frontmatter files have YAML parsing errors due to improper quote escaping when strings contain internal single quotes.

**Affected Files**:
- aluminum-laser-cleaning.yaml
- steel-laser-cleaning.yaml  
- platinum-laser-cleaning.yaml
- gold-laser-cleaning.yaml
- copper-laser-cleaning.yaml
- brass-laser-cleaning.yaml
- silver-laser-cleaning.yaml
- nickel-laser-cleaning.yaml
- bronze-laser-cleaning.yaml

**Root Cause**: The YAML dump configuration used `default_style=None` and `width=120`, which caused PyYAML to:
1. Choose single-quote wrapping for strings containing single quotes
2. Escape internal single quotes by doubling them (`''`)
3. Line-wrap at 120 characters, breaking the escape sequences mid-line

**Example of Malformed YAML**:
```yaml
research_basis: 'NIST Standard Reference Database 120: 'Thermophysical
 Properties of Materials for Nuclear Engineering'
```

**Impact**: 
- Validation fails on 9 files (92.6% pass rate instead of 100%)
- Unit tests fail when loading these frontmatter files
- Production deployment unaffected (Next.js ignores YAML parsing for these files)

## Proposed Solutions

### Solution 1: Generator Configuration Changes ✅ IMPLEMENTED

Update all YAML generation scripts to use safe formatting parameters:

**Changes Applied**:
1. `scripts/generate_caption_to_frontmatter.py` - Main integration script
2. `scripts/complete_remaining_captions.py` - Targeted completion script

**Configuration Changes**:
```python
# OLD (problematic)
yaml.dump(data, 
    default_flow_style=False,
    sort_keys=False,
    allow_unicode=True,
    width=120,           # Too narrow, causes line wrapping issues
    default_style=None)  # Allows single quotes with escaped internals

# NEW (safe)
yaml.dump(data,
    default_flow_style=False,
    sort_keys=False, 
    allow_unicode=True,
    width=1000,          # Prevents line wrapping issues
    default_style='"')   # Forces double quotes for safer escaping
```

**Benefits**:
- Double quotes handle internal single quotes cleanly: `"string with 'quotes'"`
- Wide width prevents line wrapping from breaking escapes
- Consistent formatting across all generated files
- Prevents future recurrence of this issue

### Solution 2: Repair Utility Script ✅ CREATED

**Script**: `scripts/fix_yaml_quote_escaping.py`

**Features**:
- Identifies files with YAML parsing errors
- Uses multiple parsing strategies (safe_load, unsafe_load, quote fixing)
- Re-saves files with safe formatting (width=1000, default_style='"')
- Creates backups before modification
- Validates fixes by re-parsing
- Supports dry-run mode for safety

**Usage**:
```bash
# Preview changes
python3 scripts/fix_yaml_quote_escaping.py --dry-run

# Apply fixes
python3 scripts/fix_yaml_quote_escaping.py
```

**Process**:
1. Loads each affected file using fallback parsing strategies
2. Creates timestamped backup (*.backup.YYYYMMDD_HHMMSS.yaml)
3. Re-saves with safe YAML formatting
4. Verifies YAML now parses correctly
5. Reports success/failure for each file

### Solution 3: Prevention Strategy

**Future-Proofing**:
1. ✅ All caption generation scripts now use safe YAML formatting
2. ✅ Created repair utility for existing issues
3. 🔄 Recommend standardizing YAML dump config across ALL scripts

**Recommended Global YAML Dump Configuration**:
```python
# Create a utility function for consistent YAML dumping
def safe_yaml_dump(data, file_handle):
    """Dump YAML with safe formatting to prevent quote escaping issues"""
    return yaml.dump(
        data,
        file_handle,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=1000,          # Prevent line wrapping
        default_style='"'    # Safe quote handling
    )
```

## Technical Details

### YAML Quote Escaping Behavior

**Single-Quote Style** (problematic):
```yaml
# When string contains single quotes, PyYAML doubles them
field: 'Database 120: ''Properties'''
# With line wrapping at 120 chars, this can break mid-escape
field: 'Database 120: 'Proper
 ties'''  # ← BROKEN
```

**Double-Quote Style** (safe):
```yaml
# Internal single quotes need no escaping
field: "Database 120: 'Properties'"
# Line wrapping won't break escapes
field: "Database 120: 'Proper
 ties'"  # ← Still valid
```

### Why width=1000?

1. **Prevents line wrapping**: Most frontmatter values fit on one line
2. **No escape breaking**: Escape sequences can't be split across lines
3. **Better readability**: Long strings easier to read without artificial breaks
4. **Git-friendly**: Fewer false conflicts from re-wrapping

## Implementation Plan

### Step 1: Verify Generator Changes ✅
```bash
# Check updated configuration
grep -A5 "yaml.dump" scripts/generate_caption_to_frontmatter.py
grep -A5 "yaml.dump" scripts/complete_remaining_captions.py
```

### Step 2: Test Repair Script
```bash
# Dry run to preview changes
python3 scripts/fix_yaml_quote_escaping.py --dry-run
```

### Step 3: Apply Fixes
```bash
# Fix the 9 affected files
python3 scripts/fix_yaml_quote_escaping.py
```

### Step 4: Validate Results
```bash
# Should show 100% pass rate
python3 validation/caption_integration_validator.py

# All tests should pass
python3 -m pytest tests/unit/test_caption_component.py -v
```

### Step 5: Deploy (if needed)
```bash
# Regenerate any affected content
python3 run.py --deploy
```

## Expected Outcomes

**Before Fix**:
- ❌ 112/121 files valid (92.6%)
- ❌ 9 YAML parsing errors
- ❌ Unit tests failing on affected materials

**After Fix**:
- ✅ 121/121 files valid (100%)
- ✅ 0 YAML parsing errors
- ✅ All unit tests passing
- ✅ Future caption generation uses safe formatting

## Maintenance Notes

### For Future Development

1. **Always use safe YAML formatting** when writing frontmatter files
2. **Test YAML validity** after generation with `yaml.safe_load()`
3. **Consider creating** a shared YAML utility module for consistent formatting
4. **Document YAML settings** in script headers for future reference

### Warning Signs to Watch For

- Validation errors mentioning "YAML parse error"
- Test failures on specific material frontmatter files
- Files with research_basis or other fields containing quoted text
- Unexpected line breaks in YAML string values

### Additional Considerations

**Performance**: The width=1000 setting has no performance impact; PyYAML handles wide widths efficiently.

**Compatibility**: Double-quote style is fully YAML 1.2 compliant and works with all parsers.

**Readability**: While some prefer single quotes aesthetically, double quotes are safer for complex content.

## Related Files

**Generator Scripts**:
- `scripts/generate_caption_to_frontmatter.py` - Main integration
- `scripts/complete_remaining_captions.py` - Targeted completion
- `scripts/batch_generate_all_captions.py` - Batch processor (calls main script)

**Utility Scripts**:
- `scripts/fix_yaml_quote_escaping.py` - NEW repair utility

**Validation**:
- `validation/caption_integration_validator.py` - Detects YAML issues

**Testing**:
- `tests/unit/test_caption_component.py` - Unit tests affected by YAML errors

## References

- **YAML Specification**: https://yaml.org/spec/1.2/spec.html
- **PyYAML Documentation**: https://pyyaml.org/wiki/PyYAMLDocumentation
- **Quote Escaping Rules**: https://yaml.org/spec/1.2/spec.html#id2787109
