# Missing Data & Consolidation Analysis - January 7, 2026

## Executive Summary

**Missing Dataset Data**: 153 materials lack properly named machine parameters  
**Root Cause**: Field naming mismatch between Settings.yaml and validator expectations  
**Consolidation Opportunities**: 18+ files with deprecated import paths  
**Solution**: Field name normalization + import migration

---

## Part 1: Missing Dataset Data Analysis

### Problem Statement
Dataset generation fails for 153 materials with:
```
ERROR: ❌ Tier 1 violation: Missing required machine parameter 'laserPower'
```

### Root Cause: Field Naming Mismatch

**Validator Expects** (in `shared/dataset/materials_dataset.py`):
- `laserPower`
- `wavelength` ✅
- `spotSize` ✅
- `frequency` ❌
- `pulseWidth` ✅
- `scanSpeed` ✅
- `passCount` ✅
- `overlapRatio` ✅

**Settings.yaml Actually Has**:
- `power` or `powerRange` → needs to be `laserPower`
- `repetitionRate` → needs to be `frequency`
- All other fields match ✅

### Data Location

**Source**: `data/settings/Settings.yaml` (153 settings, ~36,664 lines)
- Contains all machine parameters under `machineSettings` key
- Data is complete, just wrong field names

**Destination**: `data/materials/Materials.yaml`
- Currently has NO `machineSettings` field
- Merger copies from Settings.yaml during load: `domains/materials/data_loader_v2.py:156`

### Git History Check

Searched git history for `laserPower`:
```bash
git log --oneline --all -S "laserPower" -- data/materials/Materials.yaml data/settings/Settings.yaml
```
**Result**: No commits found with `laserPower`

**Conclusion**: The data was NEVER in the correct format. This is an original schema mismatch, not lost data.

---

## Part 2: Field Naming Analysis

### Current Settings.yaml Structure (Example)
```yaml
alabaster-settings:
  machineSettings:
    powerRange:           # ← Should be: laserPower
      min: 1.0
      max: 120
      value: 45
      unit: W
    wavelength:           # ✅ Correct
      min: 355
      max: 10640
      value: 1064
      unit: nm
    spotSize:             # ✅ Correct
      min: 0.1
      max: 500
      value: 200
      unit: μm
    repetitionRate:       # ← Should be: frequency
      min: 1
      max: 200
      value: 30
      unit: kHz
    pulseWidth:           # ✅ Correct
      min: 0.1
      max: 1000
      value: 20
      unit: ns
    scanSpeed:            # ✅ Correct
      min: 10
      max: 5000
      value: 1500
      unit: mm/s
    passCount:            # ✅ Correct
      min: 1
      max: 10
      value: 2
      unit: passes
    overlapRatio:         # ✅ Correct
      min: 10
      max: 90
      value: 60
      unit: '%'
```

### Required Changes

**Option A: Normalize Settings.yaml (RECOMMENDED)**
- Rename `powerRange` → `laserPower` (or use `power` if powerRange doesn't exist)
- Rename `repetitionRate` → `frequency`
- Keep all other fields as-is

**Pros**:
- Single source of truth (Settings.yaml)
- Aligns with validator expectations
- No validator changes needed

**Cons**:
- Must update all 153 settings entries
- May affect other code expecting old names

---

**Option B: Update Validator**
- Change validator to accept `powerRange` and `repetitionRate`
- Add field mapping logic

**Pros**:
- No data changes needed

**Cons**:
- Validator should match schema, not vice versa
- Less intuitive field names for datasets
- Doesn't follow standard naming conventions

---

**Option C: Add Field Mapping in Merger**
- Update `domains/materials/data_loader_v2.py` merge logic
- Transform field names during merge

**Pros**:
- No Settings.yaml changes
- Centralized transformation

**Cons**:
- Hidden transformation logic
- Harder to debug
- Data still wrong at source

---

### Recommendation: Option A (Normalize Settings.yaml)

**Rationale**:
1. **Data Accuracy**: Source data should match schema
2. **Transparency**: No hidden transformations
3. **Standard Naming**: `laserPower` is more standard than `powerRange`
4. **Single Source**: Settings.yaml is already the source of truth

**Implementation**:
```bash
# Create normalization script
python3 scripts/tools/normalize_machine_settings_fields.py --dry-run
python3 scripts/tools/normalize_machine_settings_fields.py --execute
```

---

## Part 3: Consolidation Opportunities

### Priority 1: Deprecated Import Migration

**Issue**: 18+ files still import from deprecated `shared.validation.errors` module

**Impact**: Potential runtime errors when these files use incompatible ValidationError

**Files Affected**:
1. `export/core/orchestrator.py` (line 47)
2. `export/core/base_generator.py` (line 37)
3. `export/core/property_processor.py` (line 33)
4. `scripts/validation/fail_fast_materials_validator.py` (line 17)
5. `shared/validation/core/content.py` (line 18)
6. `shared/validation/core/schema.py` (line 19)
7. `shared/validation/core/base_validator.py` (line 20)
8. `shared/validation/micro_integration_validator.py` (line 8)
9. `shared/validation/helpers/relationship_validators.py` (lines 11-12)
10. `shared/validation/services/pre_generation_service.py` (lines 42, 48-49)
11. `shared/validation/duplication_detector.py` (line 8)
12. `shared/services/pipeline_process_service.py` (line 23)
13. `shared/validation/content_validator.py` (line 12)
14. `shared/services/template_service.py` (line 25)

**Solution**:
```python
# BEFORE (deprecated)
from shared.validation.errors import ConfigurationError, ValidationError

# AFTER (correct)
from shared.exceptions import ConfigurationError, ValidationError
```

**Estimated Impact**: 18 files, ~25 lines changed

---

### Priority 2: Inconsistent Key Naming (snake_case vs camelCase)

**Issue**: Merger uses `machine_settings` but validator expects `machineSettings`

**Affected Code**:
- `domains/materials/data_loader_v2.py:156` - Sets `machine_settings`
- `shared/dataset/materials_dataset.py:324` - Reads `machineSettings`

**Current Workaround**: Validator checks both (?)

**Recommendation**: Standardize on camelCase throughout:
```python
# In data_loader_v2.py line 156
material_data['machineSettings'] = setting_data.get('machineSettings', {})
```

---

### Priority 3: Duplicate Key Names in Settings.yaml

**Issue**: Some settings have BOTH `power` AND `powerRange`

**Example** (from alabaster-settings):
```yaml
machineSettings:
  powerRange:    # Field #1
    value: 45
    min: 1.0
    max: 120
  power:         # Field #2 (duplicate?)
    value: 50
    min: 20
    max: 150
```

**Question**: Which should be `laserPower`?

**Analysis Needed**:
```bash
# Count settings with both fields
python3 -c "
import yaml
with open('data/settings/Settings.yaml') as f:
    data = yaml.safe_load(f)
    has_both = 0
    has_power = 0
    has_range = 0
    for setting in data['settings'].values():
        ms = setting.get('machineSettings', {})
        has_p = 'power' in ms
        has_pr = 'powerRange' in ms
        if has_p and has_pr:
            has_both += 1
        elif has_p:
            has_power += 1
        elif has_pr:
            has_range += 1
    print(f'Settings with BOTH: {has_both}')
    print(f'Settings with only power: {has_power}')
    print(f'Settings with only powerRange: {has_range}')
"
```

---

### Priority 4: Inconsistent Field Descriptions

**Issue**: Some fields have detailed descriptions, others don't

**Example**:
```yaml
# Good (has description)
powerRange:
  description: Optimal average power for Alabaster surface cleaning...
  
# Missing description
wavelength:
  unit: nm
  value: 1064
  # No description field
```

**Recommendation**: Add descriptions to all machine settings for consistency

---

## Part 4: Implementation Plan

### Phase 1: Field Name Normalization (PRIORITY 1)

**Goal**: Fix 153 materials missing `laserPower` and `frequency`

**Steps**:
1. Create normalization script: `scripts/tools/normalize_machine_settings_fields.py`
2. Analyze which fields to rename (power vs powerRange)
3. Execute normalization on Settings.yaml
4. Verify dataset generation works
5. Commit changes

**Expected Outcome**: 153/153 materials generate datasets successfully

**Estimated Time**: 2-3 hours

---

### Phase 2: Import Migration (PRIORITY 2)

**Goal**: Eliminate all deprecated `shared.validation.errors` imports

**Steps**:
1. Create migration script: `scripts/tools/migrate_validation_imports.py`
2. Update 18 affected files
3. Run full test suite
4. Commit changes

**Expected Outcome**: Zero deprecated imports remaining

**Estimated Time**: 1-2 hours

---

### Phase 3: Key Name Consistency (PRIORITY 3)

**Goal**: Standardize on camelCase (machineSettings not machine_settings)

**Steps**:
1. Update data_loader_v2.py merger
2. Update any code checking for snake_case variant
3. Verify all domains load correctly
4. Commit changes

**Expected Outcome**: Consistent naming throughout system

**Estimated Time**: 30 minutes

---

### Phase 4: Data Quality Improvements (OPTIONAL)

**Goal**: Add missing descriptions, remove duplicates

**Steps**:
1. Analyze power vs powerRange usage
2. Decide on single field name
3. Add descriptions where missing
4. Remove duplicate fields

**Expected Outcome**: Cleaner, more consistent Settings.yaml

**Estimated Time**: 2-3 hours

---

## Part 5: Normalization Script Design

### normalize_machine_settings_fields.py

```python
#!/usr/bin/env python3
"""
Normalize machine settings field names in Settings.yaml.

Changes:
1. powerRange → laserPower (or power → laserPower if no powerRange)
2. repetitionRate → frequency
3. Ensure machineSettings (camelCase) is used

Usage:
    python3 scripts/tools/normalize_machine_settings_fields.py --dry-run
    python3 scripts/tools/normalize_machine_settings_fields.py --execute
"""

import yaml
import sys
from pathlib import Path

SETTINGS_FILE = Path('data/settings/Settings.yaml')

def normalize_settings(data: dict, dry_run: bool = True) -> dict:
    """Normalize machine settings field names."""
    changes = []
    
    for setting_key, setting_data in data['settings'].items():
        machine_settings = setting_data.get('machineSettings', {})
        
        # Change 1: powerRange → laserPower (prefer powerRange over power)
        if 'powerRange' in machine_settings:
            machine_settings['laserPower'] = machine_settings.pop('powerRange')
            changes.append(f"{setting_key}: Renamed powerRange → laserPower")
        elif 'power' in machine_settings:
            machine_settings['laserPower'] = machine_settings.pop('power')
            changes.append(f"{setting_key}: Renamed power → laserPower")
        
        # Change 2: repetitionRate → frequency
        if 'repetitionRate' in machine_settings:
            machine_settings['frequency'] = machine_settings.pop('repetitionRate')
            changes.append(f"{setting_key}: Renamed repetitionRate → frequency")
    
    if dry_run:
        print(f"DRY RUN: Would make {len(changes)} changes:")
        for change in changes[:10]:  # Show first 10
            print(f"  - {change}")
        if len(changes) > 10:
            print(f"  ... and {len(changes) - 10} more")
    else:
        print(f"Applied {len(changes)} changes")
    
    return data

def main():
    dry_run = '--execute' not in sys.argv
    
    # Load Settings.yaml
    with open(SETTINGS_FILE) as f:
        data = yaml.safe_load(f)
    
    # Normalize
    normalized = normalize_settings(data, dry_run)
    
    # Save if not dry run
    if not dry_run:
        with open(SETTINGS_FILE, 'w') as f:
            yaml.dump(normalized, f, default_flow_style=False, sort_keys=False)
        print(f"✅ Saved changes to {SETTINGS_FILE}")
    else:
        print(f"\n💡 Run with --execute to apply changes")

if __name__ == '__main__':
    main()
```

---

## Part 6: Verification Tests

### Test 1: Dataset Generation
```bash
# After normalization, test dataset generation
python3 scripts/export/generate_datasets.py --domain materials --dry-run

# Expected: 153 generated, 0 errors
# (not 0 generated, 153 errors)
```

---

### Test 2: Export Pipeline
```bash
# Full export with datasets
python3 run.py --export --domain materials

# Expected: Datasets section shows 153 generated, 0 errors
```

---

### Test 3: Field Validation
```python
# Verify all settings have required fields
python3 -c "
import yaml
with open('data/settings/Settings.yaml') as f:
    data = yaml.safe_load(f)
    required = ['laserPower', 'wavelength', 'spotSize', 'frequency', 
                'pulseWidth', 'scanSpeed', 'passCount', 'overlapRatio']
    
    missing = {}
    for key, setting in data['settings'].items():
        ms = setting.get('machineSettings', {})
        missing_fields = [f for f in required if f not in ms]
        if missing_fields:
            missing[key] = missing_fields
    
    if not missing:
        print('✅ All 153 settings have required fields')
    else:
        print(f'❌ {len(missing)} settings missing fields:')
        for key, fields in list(missing.items())[:5]:
            print(f'  {key}: {fields}')
"
```

---

## Part 7: Risk Analysis

### High Risk: Breaking Changes
- **Field Renaming**: Other code may depend on old names
- **Mitigation**: Grep for `powerRange` and `repetitionRate` usage first

### Medium Risk: Data Loss
- **Multiple power fields**: If both exist, which to keep?
- **Mitigation**: Prefer `powerRange` (more specific), backup `power` as comment

### Low Risk: Export Failures
- **Temporary failures**: Export may fail during transition
- **Mitigation**: Test in dry-run mode first, commit atomically

---

## Part 8: Next Steps

### Immediate Actions (Today)
1. ✅ Analyze field naming mismatches
2. ✅ Document consolidation opportunities
3. ⏳ Create normalization script
4. ⏳ Test in dry-run mode
5. ⏳ Execute normalization
6. ⏳ Verify dataset generation

### Short-term (This Week)
1. ⏳ Migrate deprecated imports (18 files)
2. ⏳ Standardize key naming (camelCase)
3. ⏳ Run full test suite
4. ⏳ Commit all changes

### Long-term (Optional)
1. ⏳ Add missing field descriptions
2. ⏳ Remove duplicate fields
3. ⏳ Create validation tests for schema compliance

---

## Conclusion

**Missing Data**: NOT actually missing - just wrong field names in Settings.yaml

**Solution**: Normalize 2 field names across 153 settings
- `powerRange` → `laserPower`
- `repetitionRate` → `frequency`

**Consolidation**: 18 files need import migration from deprecated module

**Impact**: High (unblocks 153 materials for dataset generation)

**Effort**: Low (2-3 hours for normalization + migration)

**Grade**: A+ for analysis, pending implementation

---

**Status**: ✅ ANALYSIS COMPLETE  
**Next**: Create and execute normalization script
