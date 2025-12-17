# Domain Linkages Safety Data Enhancement - Implementation Guide

**Implementation Date**: December 17, 2025  
**Status**: ✅ Phase 1 & 2 Complete  
**Files Enhanced**: 24 contaminant frontmatter files  

---

## Overview

This enhancement adds safety and technical data fields to `domain_linkages.produces_compounds` entries in contaminant frontmatter files, enabling richer UI components that display regulatory compliance information alongside navigational links.

---

## Enhanced Schema

### New Fields Added to `produces_compounds` Entries

```yaml
domain_linkages:
  produces_compounds:
    - id: carbon-monoxide-compound
      title: Carbon Monoxide
      # ... existing fields (id, title, url, image, category, etc.) ...
      
      # NEW: Exposure Limits
      exposure_limits:
        osha_pel_mg_m3: 55          # OSHA Permissible Exposure Limit
        niosh_rel_mg_m3: 40         # NIOSH Recommended Exposure Limit
        acgih_tlv_mg_m3: 29         # ACGIH Threshold Limit Value
        idlh_mg_m3: null            # Immediately Dangerous to Life/Health
      
      # NEW: Concentration Range (optional, when available)
      concentration_range:
        min_mg_m3: 10               # Minimum concentration
        max_mg_m3: 50               # Maximum concentration
        typical_mg_m3: 30           # Average/expected concentration
      
      # NEW: Calculated Fields
      exceeds_limits: false         # Does typical_mg_m3 > acgih_tlv_mg_m3?
      monitoring_required: false    # Same as exceeds_limits
      
      # NEW: Control Measures
      control_measures:
        ventilation_required: true  # Is ventilation needed?
        ppe_level: enhanced         # none/basic/enhanced/full
        filtration_type: activated_carbon  # Type of filtration (or null)
      
      # NEW: Particulate Properties (optional, when available)
      particulate_properties:
        respirable_fraction: 0.7    # Fraction of respirable particles
        size_range_um: [0.1, 10.0]  # Size range in micrometers
```

---

## Data Sources

### 1. Exposure Limits
**Source**: Compound frontmatter files (`frontmatter/compounds/**/*.yaml`)

```yaml
# From compound frontmatter
exposure_limits:
  osha_pel_mg_m3: 55
  niosh_rel_mg_m3: 40
  acgih_tlv_mg_m3: 29
  idlh_mg_m3: null
```

### 2. Concentration Range
**Source**: Compound frontmatter `typical_concentration_range` field (when available)

```yaml
# From compound frontmatter
typical_concentration_range:
  min_mg_m3: 10
  max_mg_m3: 50
  typical_mg_m3: 30
```

### 3. Control Measures
**Source**: Calculated from contaminant's safety_data (when available)
- `ventilation_required`: Based on existence of `ventilation_requirements`
- `ppe_level`: Determined from `ppe_requirements.respiratory` field
- `filtration_type`: From `ventilation_requirements.filtration_type`

---

## Migration Tool

### Script Location
`scripts/migrate_domain_linkages_safety_data.py`

### Usage

```bash
# Dry run on single file (test mode)
python3 scripts/migrate_domain_linkages_safety_data.py \
  --dry-run \
  --file frontmatter/contaminants/rust-oxidation-contamination.yaml

# Dry run on all files
python3 scripts/migrate_domain_linkages_safety_data.py --dry-run

# Apply to single file
python3 scripts/migrate_domain_linkages_safety_data.py \
  --file frontmatter/contaminants/rust-oxidation-contamination.yaml

# Apply to all files
python3 scripts/migrate_domain_linkages_safety_data.py
```

### Migration Output

```
======================================================================
Domain Linkages Safety Data Migration
======================================================================
Mode: LIVE
Files to process: 99

📄 Processing: frontmatter/contaminants/rust-oxidation-contamination.yaml
   ✅ Enhanced domain_linkages

======================================================================
Migration Summary
======================================================================
Total files processed: 99
Successful: 24
Failed: 75
Warnings: 0

✅ Migration complete!
```

**Note**: 75 "failures" are files that don't have `produces_compounds` in their domain_linkages yet. These will be enhanced once that data is added.

---

## Migration Status Tracking

Each enhanced file receives a migration status marker:

```yaml
safety_data:
  _migration_status:
    domain_linkages_enhanced: true
    enhancement_date: '2025-12-17'
    validated: true
```

This allows the system to track which files have been processed and when.

---

## Validation & Testing

### Test Suite
`tests/test_domain_linkages_safety_enhancement.py`

**Tests verify:**
- ✅ Enhanced files exist (minimum 20 files)
- ✅ Compounds have `exposure_limits` field
- ✅ `exposure_limits` structure is correct (4 fields, proper types)
- ✅ `exceeds_limits` field exists and is boolean
- ✅ `monitoring_required` field exists and is boolean
- ✅ `control_measures` structure is correct (3 fields, proper values)
- ✅ `concentration_range` structure is correct (when present)
- ✅ Migration status metadata exists
- ✅ Original fields are preserved
- ✅ `exceeds_limits` calculation logic is correct

### Running Tests

```bash
# Run domain linkages safety enhancement tests
python3 -m pytest tests/test_domain_linkages_safety_enhancement.py -v

# Run with coverage
python3 -m pytest tests/test_domain_linkages_safety_enhancement.py --cov
```

**Expected Result**: All 10 tests passing ✅

---

## Field Specifications

### `exposure_limits`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `osha_pel_mg_m3` | number \| null | Yes | OSHA Permissible Exposure Limit |
| `niosh_rel_mg_m3` | number \| null | Yes | NIOSH Recommended Exposure Limit |
| `acgih_tlv_mg_m3` | number | Yes | ACGIH Threshold Limit Value |
| `idlh_mg_m3` | number \| null | Yes | Immediately Dangerous to Life/Health |

### `concentration_range`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `min_mg_m3` | number | Yes | Minimum concentration |
| `max_mg_m3` | number | Yes | Maximum concentration |
| `typical_mg_m3` | number | Yes | Average/expected concentration |

**Constraints:**
- `min_mg_m3 <= typical_mg_m3 <= max_mg_m3`
- All values must be >= 0

### `exceeds_limits`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `exceeds_limits` | boolean | Yes | Whether typical concentration exceeds ACGIH TLV |

**Calculation:**
```
exceeds_limits = (concentration_range.typical_mg_m3 > exposure_limits.acgih_tlv_mg_m3)
```

### `monitoring_required`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `monitoring_required` | boolean | Yes | Whether air monitoring is required |

**Logic:** Same as `exceeds_limits` value.

### `control_measures`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ventilation_required` | boolean | Yes | Whether ventilation system is required |
| `ppe_level` | enum | Yes | PPE requirement level |
| `filtration_type` | string \| null | Yes | Type of filtration needed |

**PPE Level Values:**
- `none` - No special PPE required
- `basic` - Safety glasses, gloves
- `enhanced` - Respirator, full coverage
- `full` - Full hazmat suit, SCBA

---

## UI Integration Examples

### Enhanced Domain Linkage Card

```tsx
<DomainLinkageCard
  title="Formaldehyde"
  url="/compounds/carcinogen/aldehyde/formaldehyde-compound"
  severity="moderate"
  exceedsLimits={true}
  concentration="1-10 mg/m³"
  exposureLimit="0.3 mg/m³ (ACGIH)"
  monitoringRequired={true}
  ppeLevel="enhanced"
/>
```

**Visual Features:**
- ⚠️ Warning badge if `exceeds_limits` is true
- Color-coded border based on severity
- Concentration vs. limit comparison display
- PPE level icon
- "Monitoring Required" indicator

### Hazardous Compounds Table

```tsx
<HazardousCompoundsTable
  compounds={domain_linkages.produces_compounds}
  showConcentrations={true}
  showExposureLimits={true}
  highlightExceeds={true}
/>
```

**Table Columns:**
- Compound (clickable link to compound page)
- Typical Concentration
- ACGIH TLV Limit
- Status (Exceeds/Within Limit)
- Monitoring Required (Yes/No)
- PPE Level

---

## Backward Compatibility

### Existing Code
All existing `domain_linkages` code continues to work unchanged. The new fields are additive only.

### Legacy `safety_data.fumes_generated`
The old `fumes_generated` structure is NOT removed. Both structures coexist during the transition period (Phase 2 - Dual-Write).

### Optional Fields
All new fields are optional. Components should check for field existence before using them.

---

## Next Steps (Phase 3 & 4)

### Phase 3: UI Component Updates
- [ ] Update `DomainLinkageSection` component
- [ ] Enhance domain linkage cards with safety indicators
- [ ] Update `HazardousFumesTable` to use new structure
- [ ] Add warning badges for exceeded limits
- [ ] Implement fallback logic for legacy structure

### Phase 4: Cleanup & Deprecation
- [ ] Remove `safety_data.fumes_generated` from all files
- [ ] Remove fallback code from UI components
- [ ] Archive migration scripts
- [ ] Update all documentation

---

## Troubleshooting

### Compound Not Enhanced

**Symptom**: A compound in `produces_compounds` doesn't have the new fields.

**Possible Causes:**
1. Compound frontmatter file doesn't exist
2. Compound frontmatter missing `exposure_limits` field
3. Migration script encountered an error

**Solution:**
1. Check if compound file exists: `frontmatter/compounds/**/{compound-id}.yaml`
2. Verify compound has `exposure_limits` in its frontmatter
3. Re-run migration: `python3 scripts/migrate_domain_linkages_safety_data.py --file {contaminant-file}`

### Migration Failed for File

**Symptom**: Migration reports "FAILED" for a specific file.

**Common Reasons:**
- File doesn't have `domain_linkages.produces_compounds`
- YAML parsing error
- Invalid compound ID

**Solution:**
1. Check if file has `produces_compounds`: `grep -A 5 "produces_compounds" {file}`
2. Validate YAML syntax: `python3 -c "import yaml; yaml.safe_load(open('{file}'))"`
3. Check error in migration warnings

### Test Failures

**Symptom**: Tests in `test_domain_linkages_safety_enhancement.py` fail.

**Solution:**
1. Check test output for specific assertion failures
2. Verify enhanced files exist: `grep -l "domain_linkages_enhanced" frontmatter/contaminants/*.yaml`
3. Check field structures match specification
4. Re-run migration if needed

---

## References

- **Proposal Document**: `docs/DOMAIN_LINKAGES_SAFETY_DATA_ENHANCEMENT.md`
- **Migration Script**: `scripts/migrate_domain_linkages_safety_data.py`
- **Test Suite**: `tests/test_domain_linkages_safety_enhancement.py`
- **Enhanced Files**: `frontmatter/contaminants/*.yaml` (24 files)

---

**Last Updated**: December 17, 2025  
**Implementation Status**: Phase 1 & 2 Complete ✅
