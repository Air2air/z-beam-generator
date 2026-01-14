# Maximum Formatting at Source - Executive Summary
**Date**: January 6, 2026  
**Status**: READY TO IMPLEMENT  
**Grade**: Current F → Target A

## 🎯 Problem Statement

**VIOLATION**: Export layer creates data fields instead of just transforming existing data.

The current architecture violates **Core Principle 0.6** (Generate to Data, Not Enrichers):
- ❌ Export generates `fullPath`, `breadcrumb`, `metaDescription` during export
- ❌ Export adds `_section` metadata blocks to relationships
- ❌ Export performs camelCase normalization on NEW content

**Result**: Export is doing generation work, which violates the separation of concerns.

## 📊 Current State Analysis

### Source Data (Materials.yaml, etc.)
✅ **Already Present**:
- `contentType`: 'material' (already in source)
- `schemaVersion`: '5.0.0' (already in source)
- `datePublished`: ISO8601 timestamp (already in source)

❌ **Missing** (created during export):
- `fullPath`: '/materials/metal/non-ferrous/aluminum-laser-cleaning'
- `breadcrumb`: [{label: 'Home', href: '/'}, ...] array
- `metaDescription`: SEO description (160 chars)
- `dateModified`: Current timestamp
- `_section` metadata in relationship blocks

### Export Tasks (universal_content_generator.py)
**TIER 1: Data Creation** (Must move to source):
1. `_task_export_metadata` - Creates 4 fields during export
2. `_task_section_metadata` - Creates _section blocks during export

**TIER 2: Format Transformation** (Can stay with grandfather clause):
1. `_task_camelcase_normalization` - Converts snake_case → camelCase (legacy data only)
2. `_task_field_ordering` - Reorders output fields (presentation only)

## ✅ Solution: 3-Phase Implementation

### Phase 1: Backfill Source Data (15 minutes)
**Script**: `scripts/enrichment/backfill_software_metadata.py`

```bash
# Preview changes (dry run)
python3 scripts/enrichment/backfill_software_metadata.py --all --dry-run

# Apply to all 438 items
python3 scripts/enrichment/backfill_software_metadata.py --all --no-dry-run

# Verify changes
git diff data/
```

**Adds to EACH item**:
- `fullPath`: Generated from category/subcategory/id
- `breadcrumb`: 2-4 level navigation array
- `metaDescription`: First 160 chars of micro/description
- `dateModified`: Current timestamp

**Impact**: 438 items × 4 fields = ~1,752 fields added to source data

### Phase 2: Update Generation Layer (30 minutes)
**File**: `generation/core/adapters/domain_adapter.py`

Add `enrich_on_save()` method that:
1. Generates `fullPath` from item hierarchy
2. Generates `breadcrumb` from category chain
3. Generates `metaDescription` from content
4. Sets `dateModified` to current timestamp
5. Preserves `datePublished` if exists, else sets to current

**Integration**: Call in `evaluated_generator.py` before save:
```python
# Before saving to YAML
enriched_data = self.adapter.enrich_on_save(data, domain)
save_to_yaml(enriched_data)
```

### Phase 3: Remove Export Data Creation (15 minutes)
**Files**: `export/config/*.yaml` (4 files)

Remove these tasks from all domain configs:
```yaml
# REMOVE THIS:
- type: export_metadata
  domain: materials
  schema_version: "5.0.0"
  description: Add software metadata fields

# KEEP THIS (grandfather clause):
- type: camelcase_normalization
  description: Convert snake_case → camelCase for software metadata fields
```

**Result**: Export reads complete data from source, only transforms format.

## 📈 Before/After Comparison

### BEFORE (Current - Grade F)
```
Generation → Incomplete Source Data → Export → CREATE missing fields → Frontmatter
```
**Problem**: Export creates `fullPath`, `breadcrumb`, `metaDescription`

### AFTER (Target - Grade A)
```
Generation → Complete Source Data → Export → TRANSFORM format only → Frontmatter
```
**Benefit**: Export only reorders/renames, never creates fields

## 🎯 Success Metrics

✅ **All 438 source items have**:
- fullPath (generated)
- breadcrumb (array)
- metaDescription (160 chars)
- dateModified (current timestamp)

✅ **Export configs have**:
- NO export_metadata task
- NO section_metadata task
- ONLY transformation tasks (camelcase, field_ordering)

✅ **Generation layer**:
- enrich_on_save() method in domain_adapter.py
- Called before every YAML save
- Adds complete metadata to new items

## ⏱️ Time Estimate

**Total**: ~1 hour for complete implementation

- Phase 1 (Backfill): 15 minutes
  - Script ready: `backfill_software_metadata.py`
  - Run backfill: 5 minutes
  - Verify git diff: 5 minutes
  - Commit changes: 5 minutes

- Phase 2 (Generation): 30 minutes
  - Add enrich_on_save(): 15 minutes
  - Integrate in evaluated_generator: 5 minutes
  - Test with new item: 10 minutes

- Phase 3 (Export Cleanup): 15 minutes
  - Remove export_metadata from 4 configs: 5 minutes
  - Test export with complete source: 5 minutes
  - Verify frontmatter unchanged: 5 minutes

## 🚀 Quick Start

```bash
# Step 1: Backfill all source data
cd /Users/todddunning/Desktop/Z-Beam/z-beam-generator
python3 scripts/enrichment/backfill_software_metadata.py --all --no-dry-run

# Step 2: Verify changes
git diff data/materials/Materials.yaml | head -50

# Step 3: Test export (should work identically)
python3 run.py --export --domain materials --limit 2

# Step 4: Commit source data
git add data/
git commit -m "Add complete software metadata to source data

CHANGES:
- Added fullPath, breadcrumb, metaDescription, dateModified to all 438 items
- Materials: 153 items enriched
- Contaminants: 98 items enriched
- Compounds: 34 items enriched
- Settings: 153 items enriched

COMPLIANCE: Core Principle 0.6 - Generate to Data, Not Enrichers
Next: Remove export_metadata task from export configs"

# Step 5: (Later) Update generation layer to add fields to NEW items
# Step 6: (Later) Remove export_metadata task from export configs
```

## 📚 Related Documentation
- `MAXIMUM_FORMATTING_AT_SOURCE_JAN6_2026.md` - Full implementation plan
- `docs/TECHNICAL_DEBT_BUILD_TIME_NORMALIZATION.md` - Grandfather clause
- Core Principle 0.6 - Generate to Data, Not Enrichers

## 🎓 Key Takeaway

**Old Way** (Grade F): Export creates data  
**New Way** (Grade A): Source contains complete data, export transforms only

This aligns with the fundamental principle:
> **Generate complete data to YAML → Export transforms, never creates**
