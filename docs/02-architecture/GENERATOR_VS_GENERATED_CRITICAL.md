# Generator vs. Generated Files - Critical Pattern

**Date**: November 3, 2025  
**Audience**: AI Assistants, Future Developers  
**Priority**: 🚨 **CRITICAL** - Read before ANY frontmatter fixes

---

## The Fundamental Problem

When you see issues in frontmatter files (e.g., missing min/max ranges, incorrect structure), your instinct is to **patch the files directly**. 

**This is WRONG and will waste hours of work.**

---

## Why Direct Patches Fail

### The Data Flow
```
Materials.yaml + Categories.yaml
         ↓
  trivial_exporter.py (GENERATOR)
         ↓
   frontmatter/*.yaml (GENERATED)
         ↓
    Next.js Production Site
```

### What Happens When You Patch Generated Files
1. ✅ You run script to fix all 132 frontmatter files
2. ✅ Files look perfect - all issues fixed!
3. ❌ User runs `--deploy` 
4. ❌ Exporter regenerates ALL files from Materials.yaml
5. ❌ Your patches are **COMPLETELY OVERWRITTEN**
6. ❌ All issues come back - user rightfully frustrated

---

## The Correct Approach

### Rule: Fix the GENERATOR, Not the GENERATED

**For ANY frontmatter issue:**

#### Step 1: Identify the Root Cause
- Is this a **generator bug** (exporter not adding fields)?
- Is this a **source data issue** (Materials.yaml incomplete)?
- Is this a **template conformity** issue (structure doesn't match template)?

#### Step 2: Fix the Generator
Edit: `components/frontmatter/core/trivial_exporter.py`

Common fixes:
- `_enrich_material_properties()` - Add property min/max ranges
- `_enrich_machine_settings()` - Add machine setting ranges
- `export_single()` - Filter which fields get exported
- `_flatten_property_value()` - Fix nested structures

#### Step 3: Regenerate ALL Files
```bash
python3 run.py --deploy --no-completeness-check
```

This regenerates all 132+ frontmatter files with the fix applied.

#### Step 4: Verify Persistence
Check files again - if they still have issues, the generator fix didn't work.
**DO NOT** go back to patching files directly!

---

## Real Examples from November 3, 2025

### Example 1: Missing Machine Settings Ranges

**❌ WRONG Approach:**
```python
# scripts/tools/add_machine_settings_ranges.py
for file in frontmatter_files:
    data = yaml.load(file)
    for setting in data['machine_settings']:
        # Add min/max from Categories.yaml
        setting['min'] = ranges[setting_name]['min']
        setting['max'] = ranges[setting_name]['max']
    yaml.dump(data, file)
```

**Why it fails:** Next `--deploy` regenerates from Materials.yaml without ranges

**✅ RIGHT Approach:**
```python
# components/frontmatter/core/trivial_exporter.py
def _enrich_machine_settings(self, settings: Dict, category_ranges: Dict) -> Dict:
    enriched = {}
    for setting_name, setting_value in settings.items():
        # Fix: Actually use machine_settings_ranges
        enriched[setting_name] = self._add_min_max(
            setting_value, 
            setting_name, 
            self.machine_settings_ranges  # Use this, not category_ranges
        )
    return enriched
```

Then: `python3 run.py --deploy --no-completeness-check`

### Example 2: Invalid Root-Level Keys

**❌ WRONG Approach:**
```python
# scripts/tools/remove_invalid_keys.py
for file in frontmatter_files:
    data = yaml.load(file)
    # Remove characteristics and applications
    data.pop('characteristics', None)
    data.pop('applications', None)
    yaml.dump(data, file)
```

**Why it fails:** Materials.yaml has these keys → exporter copies them → they come back

**✅ RIGHT Approach:**
```python
# components/frontmatter/core/trivial_exporter.py
def export_single(self, material_name: str, material_data: Dict):
    # Define exportable fields whitelist
    EXPORTABLE_FIELDS = {
        'category', 'subcategory', 'title', 'subtitle',
        'properties', 'machine_settings', 'faq', ...
        # characteristics NOT in list
        # applications NOT in list
    }
    
    for key, value in material_data.items():
        if key not in EXPORTABLE_FIELDS:
            continue  # Skip forbidden fields
```

Then: `python3 run.py --deploy --no-completeness-check`

---

## Detection: Is This a Generator Issue?

Ask yourself:
1. **Does the issue appear in ALL or MOST files?** → Likely generator bug
2. **Does the issue reappear after regeneration?** → Definitely generator bug  
3. **Do the files match Materials.yaml exactly?** → Generator is correct, fix source data

---

## Common Generator Bugs

### 1. Not Adding Category Ranges
**Symptom**: Properties missing `min`/`max` fields  
**Fix Location**: `_enrich_material_properties()` or `_enrich_machine_settings()`  
**Check**: Is `_add_min_max()` actually being called? With correct range dict?

### 2. Exporting Forbidden Fields
**Symptom**: Root-level keys that shouldn't exist (characteristics, applications)  
**Fix Location**: `export_single()` - add EXPORTABLE_FIELDS whitelist  
**Check**: Are you filtering keys before copying?

### 3. Creating Nested Structure
**Symptom**: Properties wrapped in `properties:` key  
**Fix Location**: `_enrich_material_properties()` or data source  
**Check**: Are you preserving bad nesting from Materials.yaml?

### 4. Missing Required Fields
**Symptom**: frontmatter_template.yaml requires fields not present  
**Fix Location**: Check if Materials.yaml has the data, add to exporter if needed  
**Check**: Is the field in the EXPORTABLE_FIELDS whitelist?

---

## Verification Checklist

After fixing the generator and redeploying:

- [ ] Run validation script to check ALL files
- [ ] Manually inspect 3-5 sample files
- [ ] Run `--deploy` AGAIN to verify fixes persist
- [ ] Check that generated files match frontmatter_template.yaml
- [ ] Document the fix in this file with date and example

---

## Historical Failures (Learn From These)

### November 3, 2025 - Multiple Repeated Failures
- **Issue**: Missing min/max in machine_settings (112/132 files)
- **Failed Attempts**: 
  - Created `fix_frontmatter_conformity.py` to patch files
  - Fixed properties but not machine_settings
  - Claimed success without verifying persistence
- **Root Cause**: Never fixed `_enrich_machine_settings()` in exporter
- **User Frustration**: "Why must I keep discovering violations that I have asked several times to fix?"
- **Lesson**: AI kept fixing symptoms, not root cause

### November 3, 2025 - Invalid Keys Returning
- **Issue**: `characteristics` and `applications` in frontmatter
- **Failed Attempts**: Removed from files with script
- **Root Cause**: Exporter copied ALL fields from Materials.yaml without filtering
- **Fix**: Added EXPORTABLE_FIELDS whitelist to `export_single()`
- **Lesson**: Generated files reflect generator logic - fix the logic!

---

## For AI Assistants

### Before Creating ANY Fix Script

1. **STOP** - Read this document completely
2. **IDENTIFY** - Is this a generator issue or source data issue?
3. **PLAN** - Will my fix survive the next `--deploy`?
4. **FIX GENERATOR** - Edit trivial_exporter.py, not frontmatter files
5. **REGENERATE** - Run --deploy to apply fix
6. **VERIFY** - Check persistence with second --deploy

### Red Flags You're Doing It Wrong

- Creating scripts in `scripts/tools/fix_frontmatter_*.py`
- Reading/writing `frontmatter/materials/*.yaml` directly
- Claiming "fixed all 132 files!" without redeploying
- User says "this issue came back" or "you fixed this before"

### Green Flags You're Doing It Right

- Editing `components/frontmatter/core/trivial_exporter.py`
- Running `--deploy` after changes
- Verifying with second `--deploy` to check persistence
- No one-off patch scripts needed

---

## Exception: When Patching Is Correct

**Only patch frontmatter files directly if:**
1. You're fixing a one-time migration issue
2. The generator is ALREADY correct for future exports
3. You document WHY patching is needed this time

**Example**: Migrating old files to new structure when generator already updated.

---

## Summary

| Symptom | Wrong Fix | Right Fix |
|---------|-----------|-----------|
| Missing min/max | Patch 132 files | Fix `_enrich_*()` → deploy |
| Invalid keys | Remove from files | Add whitelist → deploy |
| Wrong structure | Reformat files | Fix `_enrich_*()` → deploy |
| Missing fields | Add to files | Check source data or exporter |

**Remember**: Frontmatter files are **OUTPUT**, not **SOURCE**. Fix the source or the generator, never the output.

---

## File Locations Quick Reference

```
Source Data:
  materials/data/Materials.yaml       ← Material-specific data
  materials/data/Categories.yaml      ← Category ranges, taxonomy

Generator:
  components/frontmatter/core/trivial_exporter.py   ← FIX HERE

Generated Output:
  frontmatter/materials/*.yaml        ← DO NOT FIX HERE

Template:
  materials/data/frontmatter_template.yaml          ← Canonical structure
```

---

**Last Updated**: November 3, 2025  
**Next Review**: When any frontmatter issue is reported  
**Maintainer**: See `.github/copilot-instructions.md`
