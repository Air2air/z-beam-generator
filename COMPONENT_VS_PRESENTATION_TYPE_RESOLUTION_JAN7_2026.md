# Component Type vs Presentation Type Resolution
**Date**: January 7, 2026  
**Status**: ✅ COMPLETE

## Summary

Successfully resolved the overlap between `component_type` (generation layer) and `presentation_type` (data layer redundancy). Removed all 10 occurrences of redundant `presentation_type` fields from sectionMetadata blocks across all domain YAML files.

## Problem Identified

**Overlap between two distinct concepts:**

1. **`component_type`** (generation layer) - Identifies what's being generated
   - Used by: QualityEvaluatedGenerator, field_router, batch_generator
   - Values: `pageDescription`, `micro`, `faq`, `pageTitle`, etc.
   - Purpose: Routes to correct prompt template and generation logic
   - Location: Python code, CLI flags, component registry

2. **`presentation_type`** (data layer - REDUNDANT) - Duplicates `presentation`
   - Used by: sectionMetadata (internal developer notes)
   - Values: `card`, `descriptive`, `list`, `table`
   - Purpose: UI presentation hint (redundant with `presentation` field)
   - Location: Materials.yaml, Compounds.yaml, Settings.yaml (in `sectionMetadata`)

3. **`presentation`** (data layer - CORRECT) - How to display relationships
   - Used by: Relationship blocks at the key level
   - Values: `card`, `descriptive`, `list`, `table`
   - Purpose: Determines UI presentation format
   - Location: All domain YAML files (at relationship level, NOT in sectionMetadata)

## The Overlap

**`presentation_type` in `sectionMetadata` is redundant** - it duplicates the `presentation` field that's already at the relationship level:

```yaml
# CURRENT (REDUNDANT):
relationships:
  technical:
    related_compounds:
      presentation: card          # ← AUTHORITATIVE
      items: [...]
      _section:
        sectionMetadata:
          presentation_type: card  # ← REDUNDANT!
```

## Resolution Strategy

**Remove `presentation_type` from `sectionMetadata` entirely** - it's redundant with the `presentation` field.

### Changes Required

1. **Data Files** (Materials.yaml, Compounds.yaml, Settings.yaml, Contaminants.yaml):
   - Remove `presentation_type:` from all `sectionMetadata` blocks
   - Keep `presentation:` at the relationship level (authoritative)

2. **Export Config** (export/config/schema.yaml):
   - Remove `presentation_type: string` from sectionMetadata schema

3. **Documentation**:
   - Update to clarify `component_type` (generation) vs `presentation` (UI display)
   - Remove all references to `presentation_type` in sectionMetadata

### Terms Clarified

| Term | Layer | Purpose | Values | Location |
|------|-------|---------|--------|----------|
| **`component_type`** | Generation | What's being generated | pageDescription, micro, faq | Python code |
| **`presentation`** | Data/UI | How to display | card, list, table, descriptive | Relationship level in YAML |
| **`presentation_type`** | DEPRECATED | ~~Redundant duplicate~~ | ~~card, descriptive~~ | ~~To be removed~~ |

## Implementation

### Step 1: Remove from Data Files
- Search: `presentation_type:`
- Files: data/materials/Materials.yaml, data/compounds/Compounds.yaml, data/settings/Settings.yaml
- Action: Delete all `presentation_type:` lines from `sectionMetadata` blocks

### Step 2: Update Schema
- File: export/config/schema.yaml
- Action: Remove `presentation_type: string` from sectionMetadata definition

### Step 3: Verify No Code Dependencies
- Search codebase for `presentation_type` usage
- Confirm only appears in deprecated sectionMetadata blocks
- No Python code should read `presentation_type`

## Benefits

✅ **Eliminates redundancy** - Single source of truth for presentation format  
✅ **Clearer separation** - `component_type` (generation) vs `presentation` (display)  
✅ **Simpler data** - Less noise in sectionMetadata blocks  
✅ **Consistent with policy** - Maximum formatting at source (use `presentation` field)

## Verification

✅ **COMPLETE - All checks passed:**

- [x] Zero occurrences of `presentation_type` in active data files (Materials.yaml, Compounds.yaml, Settings.yaml, Contaminants.yaml)
- [x] `presentation:` field exists at all relationship levels
- [x] Export schema updated (removed presentation_type from sectionMetadata definition)
- [x] No production code reads `sectionMetadata.presentation_type`
- [x] 10 total removals across 3 domain files

## Files Modified

### Data Files (10 removals)
1. **data/materials/Materials.yaml** - 2 occurrences removed
   - `contaminated_by` relationship (line 426)
   - `regulatory_standards` section (line 491)

2. **data/compounds/Compounds.yaml** - 5 occurrences removed
   - `chemical_properties` section (line 132)
   - `produced_from` relationship - id003 (line 449)
   - `produced_from` relationship - id007 (line 1036)
   - `environmental_impact` section (line 1934)
   - `detection_monitoring` section (line 1951)

3. **data/settings/Settings.yaml** - 3 occurrences removed
   - `regulatory_standards` section (line 167)
   - `removes_contaminants` relationship (line 185)
   - `works_on_materials` relationship (line 204)

### Schema Files
4. **export/config/schema.yaml** - Removed `presentation_type: string` from sectionMetadata schema definition

## Results

✅ **Cleaner data structure** - Eliminated redundancy  
✅ **Single source of truth** - `presentation` field at relationship level is authoritative  
✅ **Clearer separation** - `component_type` (generation) vs `presentation` (display)  
✅ **Policy compliant** - Maximum formatting at source (Core Principle 0.6)  
✅ **No regressions** - Export system already uses `presentation` field (not `presentation_type`)
