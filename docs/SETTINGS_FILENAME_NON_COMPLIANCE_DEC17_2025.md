# Settings Filename Non-Compliance Report

**Date**: December 17, 2025  
**Issue**: Critical filename non-compliance in settings frontmatter  
**Impact**: All 161 settings files violate naming requirements  
**Status**: 🚨 CRITICAL - Requires immediate attention

---

## Executive Summary

**All 161 settings files are non-compliant** with the naming requirements specified in `FRONTMATTER_GENERATOR_REQUIREMENTS.md`.

**Compliance Rate**: 0/161 (0%)

---

## Required Pattern

According to `FRONTMATTER_GENERATOR_REQUIREMENTS.md`:

```
Pattern: {material-name}-settings.yaml
Rules:
- ✅ MUST use kebab-case (lowercase with hyphens)
- ✅ MUST include -settings suffix
- ❌ NO spaces
- ❌ NO uppercase letters
- ❌ NO parentheses

Examples:
✅ aluminum-settings.yaml
✅ stainless-steel-settings.yaml
✅ carbon-fiber-reinforced-polymer-settings.yaml
```

---

## Current Issues

### Issue 1: Missing `-settings` Suffix
**Count**: 161/161 files (100%)

No settings files have the required `-settings.yaml` suffix.

**Examples**:
```
❌ Alabaster.yaml → ✅ alabaster-settings.yaml
❌ Alumina.yaml → ✅ alumina-settings.yaml
❌ aluminum.yaml → ✅ aluminum-settings.yaml
❌ Brass.yaml → ✅ brass-settings.yaml
```

### Issue 2: Title Case Instead of kebab-case
**Count**: ~157/161 files (97.5%)

Most files use Title Case with uppercase letters.

**Examples**:
```
❌ Alabaster.yaml → ✅ alabaster-settings.yaml
❌ Borosilicate Glass.yaml → ✅ borosilicate-glass-settings.yaml
❌ Carbon Steel.yaml → ✅ carbon-steel-settings.yaml
❌ Chrome-Plated Steel.yaml → ✅ chrome-plated-steel-settings.yaml
❌ Stainless Steel.yaml → ✅ stainless-steel-settings.yaml
```

### Issue 3: Spaces in Filenames
**Count**: ~130/161 files (80.7%)

Many files contain spaces instead of hyphens.

**Examples**:
```
❌ "Borosilicate Glass.yaml" → ✅ borosilicate-glass-settings.yaml
❌ "Carbon Steel.yaml" → ✅ carbon-steel-settings.yaml
❌ "Stainless Steel.yaml" → ✅ stainless-steel-settings.yaml
❌ "Chrome-Plated Steel.yaml" → ✅ chrome-plated-steel-settings.yaml
```

### Issue 4: Parentheses in Filenames
**Count**: ~10/161 files (6.2%)

Some files contain parentheses.

**Examples**:
```
❌ "Polytetrafluoroethylene (PTFE).yaml" → ✅ polytetrafluoroethylene-ptfe-settings.yaml
❌ "Silicon Carbide (SiC).yaml" → ✅ silicon-carbide-sic-settings.yaml
```

---

## Only 4 Files Are Lowercase

These 4 files are lowercase but still missing the `-settings` suffix:

```
❌ aluminum.yaml → ✅ aluminum-settings.yaml
❌ copper.yaml → ✅ copper-settings.yaml
❌ steel.yaml → ✅ steel-settings.yaml
❌ titanium.yaml → ✅ titanium-settings.yaml
```

---

## Impact

### 1. **Broken URL Routing**
Frontend expects URLs like:
```
/settings/aluminum
/settings/stainless-steel
```

But files are named:
```
Alabaster.yaml (not aluminum.yaml)
Stainless Steel.yaml (not stainless-steel-settings.yaml)
```

### 2. **Broken Link References**
Other frontmatter files reference settings with expected URLs:
```yaml
relationships:
  related_settings:
  - url: /settings/aluminum
    # But file is: aluminum.yaml (missing suffix)
```

### 3. **Broken Validation**
Tests expecting `-settings.yaml` suffix will fail:
```bash
ls frontmatter/settings/*.yaml | grep -v -- "-settings.yaml"
# Returns: 161 non-compliant files
```

### 4. **Inconsistent with Other Domains**
- Materials: ✅ `aluminum-laser-cleaning.yaml`
- Contaminants: ✅ `aluminum-oxidation-contaminant.yaml`
- Compounds: ✅ `formaldehyde-compound.yaml`
- Settings: ❌ `Alabaster.yaml` ← INCONSISTENT

---

## Required Fields in Each File

Each settings file also needs:

```yaml
# File: alabaster-settings.yaml

id: Alabaster  # ✅ Title Case (exception for settings)
slug: alabaster  # ✅ kebab-case (matches base filename)
content_type: settings
schema_version: "5.0.0"
```

**Note**: Settings ID field is Title Case (exception to kebab-case rule).

---

## Comparison with Other Domains

| Domain | Files | Pattern | Compliance |
|--------|-------|---------|------------|
| Materials | 153 | `{name}-laser-cleaning.yaml` | ✅ 153/153 (100%) |
| Contaminants | 98 | `{name}-contaminant.yaml` | ✅ 98/98 (100%) |
| Compounds | 20 | `{name}-compound.yaml` | ✅ 20/20 (100%) |
| **Settings** | **161** | **`{name}-settings.yaml`** | **❌ 0/161 (0%)** |

---

## Automated Tests

Created comprehensive test suite to verify compliance:

**File**: `tests/test_settings_filename_compliance.py`

**Tests**:
1. ✅ All files have `-settings.yaml` suffix
2. ✅ All files use kebab-case
3. ✅ No spaces in filenames
4. ✅ No uppercase letters in filenames
5. ✅ Slug field matches base filename
6. ✅ ID field is Title Case
7. ✅ Compliance rate reporting

**Run Tests**:
```bash
python3 -m pytest tests/test_settings_filename_compliance.py -v
```

**Expected Result** (current state):
```
FAILED tests/test_settings_filename_compliance.py::TestSettingsFilenameCompliance::test_all_files_have_settings_suffix
FAILED tests/test_settings_filename_compliance.py::TestSettingsFilenameCompliance::test_all_files_use_kebab_case
FAILED tests/test_settings_filename_compliance.py::TestSettingsFilenameCompliance::test_no_spaces_in_filenames
FAILED tests/test_settings_filename_compliance.py::TestSettingsFilenameCompliance::test_no_uppercase_in_filenames

Found 161 files without '-settings.yaml' suffix
Found 161 files not in kebab-case
Found ~130 files with spaces
Found ~157 files with uppercase letters
```

---

## Resolution Required

### Option A: Bulk Rename Script
Create script to rename all 161 files:

```bash
# Script: scripts/rename_settings_files.py
for file in frontmatter/settings/*.yaml:
    # Convert to kebab-case
    new_name = convert_to_kebab_case(file)
    # Add -settings suffix
    new_name = new_name.replace('.yaml', '-settings.yaml')
    # Rename file
    mv "$file" "$new_name"
```

### Option B: Regenerate from Source
Regenerate all settings frontmatter files with correct naming:

```bash
python3 run.py --generate-settings --use-correct-naming
```

### Option C: Manual Fix
Manually rename each of the 161 files (not recommended - error-prone).

---

## Recommended Action

**Immediate**: Use Option A (Bulk Rename Script)
1. Create rename mapping (old → new)
2. Update slug fields if needed
3. Verify ID fields remain Title Case
4. Run rename script with dry-run first
5. Execute rename
6. Run tests to verify compliance
7. Update any references in other files

**Timeline**: 1-2 hours for script + testing

---

## Verification After Fix

Run these commands to verify:

```bash
# 1. Check suffix compliance
ls frontmatter/settings/*.yaml | grep -v -- "-settings.yaml" && echo "❌ FAIL" || echo "✅ PASS"

# 2. Check kebab-case
ls frontmatter/settings/*.yaml | grep -P '[A-Z ]' && echo "❌ FAIL" || echo "✅ PASS"

# 3. Run automated tests
python3 -m pytest tests/test_settings_filename_compliance.py -v

# Expected: ALL TESTS PASS (11/11)
```

---

## Documentation Updates

Updated these documents to reflect the issue:

1. ✅ `docs/FRONTMATTER_GENERATOR_REQUIREMENTS.md` - Added settings non-compliance section
2. ✅ `tests/test_settings_filename_compliance.py` - Created comprehensive test suite
3. ✅ `docs/SETTINGS_FILENAME_NON_COMPLIANCE_DEC17_2025.md` - This report

---

## Priority

🚨 **CRITICAL** - This affects:
- URL routing for all 161 settings pages
- Link references from materials/contaminants
- Consistency across all frontmatter domains
- Validation and testing infrastructure

**Blocks**:
- Production deployment of settings pages
- Cross-domain link integrity
- Automated validation pipelines

**Recommendation**: Fix before any production deployment.
