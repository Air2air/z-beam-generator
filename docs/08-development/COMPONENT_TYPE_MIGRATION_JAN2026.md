# Component Type Migration (January 2026)

## Overview
This document tracks the migration from legacy component naming to standardized schema-based naming.

## Changes Made

### 1. Caption → Micro (All Domains)
**Date**: January 13, 2026  
**Reason**: `caption` was deprecated in favor of `micro` to match schema terminology

**Affected Files**:
- `generation/backfill/config/materials.yaml` - REMOVED caption field
- `generation/backfill/config/contaminants.yaml` - REMOVED caption field
- `generation/backfill/config/compounds.yaml` - REMOVED caption field
- `generation/backfill/config/settings.yaml` - REMOVED caption field

**Migration Guide**:
```yaml
# ❌ OLD (deprecated)
fields:
  - field: caption
    component_type: caption

# ✅ NEW (correct)
# Use 'micro' field directly in data YAML, not in backfill config
# Micro is already generated as part of existing system
```

**Why**: The `caption` field was never part of the schema. Content previously labeled as "caption" is actually the `micro` component.

### 2. Description → PageDescription (Materials Domain Only)
**Date**: January 13, 2026  
**Reason**: Materials domain uses `pageDescription` component type in schema

**Affected Files**:
- `generation/backfill/config/materials.yaml` - Changed `description` → `pageDescription`
- `generation/config.yaml` - Added `pageDescription` extraction strategy
- `tests/test_generation_pipeline.py` - Updated test component types
- `tests/test_batch_report_format.py` - Updated report checks
- `tests/test_voice_pipeline_corrected.py` - Updated generation calls

**Migration Guide**:
```yaml
# ❌ OLD (incorrect for materials)
fields:
  - field: pageDescription
    component_type: description  # Wrong!

# ✅ NEW (correct for materials)
fields:
  - field: pageDescription
    component_type: pageDescription  # Matches schema
```

**Important**: Other domains (contaminants, compounds, settings) may still use `description` - this change is **materials-specific only**.

## Schema Alignment

### Materials Domain Components
Per `data/schemas/section_display_schema.yaml`:
- `micro` - Brief technical overview (100 words)
- `pageDescription` - Main page description (160 words)
- `excerpt` - Hook/summary (80 words) [DEPRECATED - field removed]
- `faq` - FAQ section (400 words)
- `seo_description` - SEO meta description (160 words)
- `meta_description` - Short meta (155 chars)
- `page_title` - Page title (60 chars)
- `power_intensity` - Technical parameters (120 words)

### Contaminants Domain Components
- `micro` - Brief overview (100 words)
- `pageDescription` - Main description (160 words)
- `excerpt` - Summary (80 words) [DEPRECATED - field removed]
- `faq` - FAQ (400 words)
- `seo_description` - SEO description (160 words)
- `appearance` - Visual description (120 words)
- `compounds` - Chemical composition (150 words)

### Compounds Domain Components
- `pageDescription` - Main description (160 words)
- `health_effects` - Health impact (200 words)
- `detection_methods` - Testing methods (150 words)
- `emergency_response` - Emergency procedures (180 words)
- `exposure_guidelines` - Safety limits (160 words)

### Settings Domain Components
- `pageDescription` - Main description (160 words)
- `faq` - FAQ (400 words)
- `challenges` - Common issues (180 words)

## Testing Updates

### Tests Updated
1. `tests/test_generation_pipeline.py`:
   - Line 103: `"caption"` → `"micro"`
   - Line 146: `['caption', 'description', 'faq']` → `['micro', 'pageDescription', 'faq']`

2. `tests/test_batch_report_format.py`:
   - Line 35: `'GENERATED CAPTION'` → `'GENERATED MICRO'`

3. `tests/test_voice_pipeline_corrected.py`:
   - Line 55: `component_type='caption'` → `component_type='micro'`

### Tests NOT Changed
Tests using generic `component_type="description"` were preserved when:
- Testing contaminants/compounds/settings domains (correct usage)
- Testing generic component functionality (domain-agnostic)
- Not specific to materials domain

## Configuration Requirements

### Extraction Strategy Required
All component types MUST have an extraction strategy defined in `generation/config.yaml`:

```yaml
component_extraction:
  micro:
    extraction_strategy: before_after  # Extract before/after paragraphs
  pageDescription:
    extraction_strategy: raw           # Return text as-is
  # excerpt: # DEPRECATED - field removed
    extraction_strategy: raw           # Return text as-is
  faq:
    extraction_strategy: json_list     # Parse as JSON array
```

### Backfill Configuration
Materials backfill now generates 3 text fields:

```yaml
# generation/backfill/config/materials.yaml
generators:
  - type: multi_field_text
    fields:
      - field: pageDescription
        component_type: pageDescription  # ← Must match schema
      # - field: excerpt     # DEPRECATED - field removed
      #   component_type: excerpt
      - field: faq
        component_type: faq
```

## Documentation Already Correct ✅
These docs already used correct terminology:
- `docs/FRONTMATTER_NORMALIZED_STRUCTURE.md` - Uses `pageDescription` (11 occurrences)
- `docs/05-data/SOURCE_DATA_SCHEMA.md` - Correct field names
- `docs/09-reference/GENERATION_VS_DISPLAY_TERMINOLOGY.md` - Accurate component types

## Verification Commands

### Check Current Configuration
```bash
# Verify materials backfill config
grep -A 10 "fields:" generation/backfill/config/materials.yaml

# Verify extraction strategies
grep -A 15 "component_extraction:" generation/config.yaml

# Check for remaining caption references
grep -r "caption" generation/backfill/config/ --include="*.yaml"
# Should return: no matches
```

### Test Generation
```bash
# Generate pageDescription for aluminum
python3 run.py --domain materials --item aluminum-laser-cleaning

# Verify fields populated
python3 -c "
import yaml
data = yaml.safe_load(open('data/materials/Materials.yaml'))
al = data['materials']['aluminum-laser-cleaning']
print(f\"pageDescription: {len(al.get('pageDescription', ''))} chars\")
print(f\"excerpt: {len(al.get('excerpt', ''))} chars\")
print(f\"faq: {len(str(al.get('faq', [])))} chars\")
"
```

### Run Tests
```bash
# Run updated tests
pytest tests/test_generation_pipeline.py -v
pytest tests/test_batch_report_format.py -v
pytest tests/test_voice_pipeline_corrected.py -v
```

## Rollback Procedure (If Needed)

If issues arise, revert with:

```bash
git show HEAD~1:generation/backfill/config/materials.yaml > generation/backfill/config/materials.yaml
git show HEAD~1:generation/config.yaml > generation/config.yaml
```

Then regenerate affected content.

## Future Migrations

### Potential Candidates
- `seo_description` → May consolidate with `meta_description`
- `power_intensity` → May move to dedicated settings schema

### Migration Checklist Template
When migrating component types:
1. [ ] Check schema definition (`data/schemas/section_display_schema.yaml`)
2. [ ] Update backfill configs (all affected domains)
3. [ ] Add extraction strategy (`generation/config.yaml`)
4. [ ] Update tests (search for old component name)
5. [ ] Verify documentation already correct
6. [ ] Test generation end-to-end
7. [ ] Update this migration doc

## References
- **Schema Definition**: `data/schemas/section_display_schema.yaml`
- **Backfill Configs**: `generation/backfill/config/*.yaml`
- **Extraction Strategies**: `generation/config.yaml` (component_extraction section)
- **Test Files**: `tests/test_generation_pipeline.py`, `tests/test_batch_report_format.py`, `tests/test_voice_pipeline_corrected.py`
