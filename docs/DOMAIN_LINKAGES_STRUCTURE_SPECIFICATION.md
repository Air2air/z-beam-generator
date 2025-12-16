# Domain Linkages Structure Specification

**Version:** 1.0.0  
**Date:** December 15, 2025  
**Status:** Proposed for Review

---

## Executive Summary

This specification defines the new **`domain_linkages`** structure that replaces scattered linkage data across all domains with a unified, standardized format. Every linkage includes complete metadata for UI rendering: `id`, `title`, `url`, and `image`.

---

## 1. Current State (Before Migration)

### 1.1 Scattered Linkage Data

Currently, linkages are spread across multiple fields with inconsistent formats:

```yaml
# Contaminants.yaml - CURRENT FORMAT
adhesive-residue:
  # Material linkages (simple array)
  valid_materials:
    - Aluminum
    - Steel
    - Stainless Steel
    # ... 49 total
  
  # Regulatory references (nested in eeat)
  eeat:
    citations:
      - "IEC 60825 - Safety of Laser Products"
      - "OSHA 29 CFR 1926.95 - Personal Protective Equipment"
  
  # Compound linkages (with DUPLICATE exposure limits)
  laser_properties:
    safety_data:
      fumes_generated:
        - compound: Formaldehyde
          concentration_mg_m3: 1-10
          exposure_limit_mg_m3: 0.3    # ❌ DUPLICATE (in Compounds.yaml)
          hazard_class: carcinogenic   # ❌ DUPLICATE (in Compounds.yaml)
      
      # PPE requirements (inconsistent format)
      ppe_requirements:
        eye_protection: goggles        # ❌ Simple string
        respiratory: full_face         # ❌ No metadata
        skin_protection: gloves        # ❌ No context
```

### 1.2 Problems with Current Format

1. **No UI metadata** - Material names don't have URLs or images
2. **Duplicate data** - Exposure limits stored in two places (data integrity risk)
3. **Inconsistent schemas** - Different formats for similar data
4. **No bidirectional links** - Materials don't know which contaminants they have
5. **Hard to query** - Cannot easily find "all materials for this contaminant"
6. **Legacy references** - String citations instead of standard IDs

---

## 2. Proposed Structure: `domain_linkages`

### 2.1 Complete Schema

```yaml
domain_linkages:
  
  # Material Linkages
  related_materials:
    - id: "aluminum"                              # Kebab-case identifier
      title: "Aluminum"                           # Human-readable name
      url: "/materials/metals/aluminum/aluminum"  # Page URL
      image: "/images/materials/aluminum.jpg"     # Hero image
      frequency: "common"                         # How common this pairing is
      severity: "moderate"                        # Cleaning difficulty
      typical_context: "general"                  # Use case context
  
  # Compound Linkages
  related_compounds:
    - id: "formaldehyde"                          # Kebab-case identifier
      title: "Formaldehyde"                       # Human-readable name
      url: "/compounds/formaldehyde"              # Page URL
      image: "/images/compounds/formaldehyde.jpg" # Molecule image
      source: "thermal_decomposition"             # How it's produced
      concentration_range_mg_m3: "1-10"           # Context-specific data
      # NOTE: exposure_limit comes from Compounds.yaml (no duplication)
  
  # Regulatory Standards
  regulatory_compliance:
    - id: "iec-60825"                             # Standard ID
      title: "IEC 60825"                          # Standard name
      url: "https://webstore.iec.ch/..."          # Official URL
      image: "/images/standards/iec-logo.svg"     # Organization logo
      applicability: "laser_operation"            # What it applies to
      requirement: "International standard..."     # Brief description
  
  # PPE Requirements
  ppe_requirements:
    - id: "ppe-respiratory-full-face"             # PPE spec ID
      title: "Full-Face Respirator"               # PPE name
      url: "/ppe/ppe-respiratory-full-face"       # PPE spec page
      image: "/images/ppe/ppe-respiratory-full-face.jpg"
      reason: "toxic_fumes"                       # Why it's needed
      required: true                              # Mandatory or recommended
      context: "carcinogenic_compounds_present"   # When it's needed
```

---

## 3. Field Definitions

### 3.1 Universal Fields (All Linkages)

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | string | ✅ | Kebab-case unique identifier | `"aluminum"`, `"formaldehyde"` |
| `title` | string | ✅ | Human-readable display name | `"Aluminum"`, `"Full-Face Respirator"` |
| `url` | string | ✅ | Relative or absolute URL to entity | `"/materials/metals/aluminum/aluminum"` |
| `image` | string | ✅ | Path to hero/thumbnail image | `"/images/materials/aluminum.jpg"` |

### 3.2 Material-Specific Fields

| Field | Type | Required | Description | Values |
|-------|------|----------|-------------|--------|
| `frequency` | string | ✅ | How common this pairing is | `"common"`, `"occasional"`, `"rare"` |
| `severity` | string | ✅ | Cleaning difficulty | `"low"`, `"moderate"`, `"high"` |
| `typical_context` | string | ✅ | Use case context | `"manufacturing"`, `"shipping"`, `"general"` |

### 3.3 Compound-Specific Fields

| Field | Type | Required | Description | Values |
|-------|------|----------|-------------|--------|
| `source` | string | ✅ | How compound is produced | `"thermal_decomposition"`, `"photochemical"`, `"mechanical"` |
| `concentration_range_mg_m3` | string | ✅ | Typical concentration | `"1-10"`, `"5-25"`, `"varies"` |

**Note:** `exposure_limit_mg_m3` is **NOT** included (comes from Compounds.yaml)

### 3.4 Regulatory-Specific Fields

| Field | Type | Required | Description | Values |
|-------|------|----------|-------------|--------|
| `applicability` | string | ✅ | What standard applies to | `"laser_operation"`, `"ppe_requirements"`, `"chemical_handling"` |
| `requirement` | string | ✅ | Brief description (100 chars) | Truncated from standard's `description` field |

### 3.5 PPE-Specific Fields

| Field | Type | Required | Description | Values |
|-------|------|----------|-------------|--------|
| `reason` | string | ✅ | Why PPE is needed | `"toxic_fumes"`, `"particulate_generation"`, `"chemical_contact"` |
| `required` | boolean | ✅ | Mandatory vs recommended | `true`, `false` |
| `context` | string | ✅ | When it's needed | `"all_operations"`, `"carcinogenic_compounds_present"`, `"enclosed_spaces"` |

---

## 4. Complete Example: Adhesive Residue

### 4.1 BEFORE (Current Format)

```yaml
adhesive-residue:
  valid_materials:
    - Aluminum
    - Steel
    - Stainless Steel
    # ... 46 more (no URLs, no images, no metadata)
  
  eeat:
    citations:
      - "IEC 60825 - Safety of Laser Products"
      - "OSHA 29 CFR 1926.95 - Personal Protective Equipment"
  
  laser_properties:
    safety_data:
      fumes_generated:
        - compound: Formaldehyde
          concentration_mg_m3: 1-10
          exposure_limit_mg_m3: 0.3      # DUPLICATE
          hazard_class: carcinogenic     # DUPLICATE
        - compound: Benzene
          concentration_mg_m3: 0.5-5
          exposure_limit_mg_m3: 0.5      # DUPLICATE
          hazard_class: carcinogenic     # DUPLICATE
        # ... 4 more
      
      ppe_requirements:
        eye_protection: goggles          # No details
        respiratory: full_face           # No standards
        skin_protection: gloves          # No specifications
```

### 4.2 AFTER (New Format)

```yaml
adhesive-residue:
  domain_linkages:
    
    related_materials:  # 49 entries
      - id: aluminum
        title: Aluminum
        url: /materials/metals/aluminum/aluminum
        image: /images/materials/aluminum.jpg
        frequency: common
        severity: moderate
        typical_context: general
      
      - id: steel
        title: Steel
        url: /materials/metals/steel/steel
        image: /images/materials/steel.jpg
        frequency: common
        severity: moderate
        typical_context: general
      # ... 47 more materials
    
    related_compounds:  # 6 entries
      - id: formaldehyde
        title: Formaldehyde
        url: /compounds/formaldehyde
        image: /images/compounds/formaldehyde.jpg
        source: thermal_decomposition
        concentration_range_mg_m3: 1-10
        # exposure_limit: Get from Compounds.yaml via id ✅
      
      - id: benzene
        title: Benzene
        url: /compounds/benzene
        image: /images/compounds/benzene.jpg
        source: thermal_decomposition
        concentration_range_mg_m3: 0.5-5
        # exposure_limit: Get from Compounds.yaml via id ✅
      # ... 4 more compounds
    
    regulatory_compliance:  # 2 entries
      - id: iec-60825
        title: IEC 60825
        url: https://webstore.iec.ch/publication/3587
        image: /images/standards/iec-logo.svg
        applicability: laser_operation
        requirement: International standard for laser product safety and classification
      
      - id: osha-29-cfr-1926-95
        title: OSHA 29 CFR 1926.95
        url: https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.95
        image: /images/standards/osha-logo.svg
        applicability: ppe_requirements
        requirement: Requirements for PPE in construction environments
    
    ppe_requirements:  # 3 entries
      - id: ppe-eye-goggles
        title: Safety Goggles
        url: /ppe/ppe-eye-goggles
        image: /images/ppe/ppe-eye-goggles.jpg
        reason: particulate_generation
        required: true
        context: all_operations
      
      - id: ppe-respiratory-full-face
        title: Full-Face Respirator
        url: /ppe/ppe-respiratory-full-face
        image: /images/ppe/ppe-respiratory-full-face.jpg
        reason: toxic_fumes
        required: true
        context: carcinogenic_compounds_present
      
      - id: ppe-skin-nitrile-gloves
        title: Nitrile Gloves
        url: /ppe/ppe-skin-nitrile-gloves
        image: /images/ppe/ppe-skin-nitrile-gloves.jpg
        reason: chemical_contact
        required: true
        context: all_operations
```

---

## 5. Benefits of New Structure

### 5.1 UI Rendering

✅ **Complete metadata** - Every linkage has id, title, url, image  
✅ **Card components** - Can render clickable cards with images  
✅ **Navigation** - Direct links to related entities  
✅ **Visual hierarchy** - Images and titles improve UX

### 5.2 Data Integrity

✅ **Single source of truth** - Exposure limits ONLY in Compounds.yaml  
✅ **No duplication** - Compound data referenced, not copied  
✅ **Consistent updates** - Update once, reflects everywhere  
✅ **Referential integrity** - IDs ensure linkages stay valid

### 5.3 Querying & Discovery

✅ **Bidirectional lookups** - Find materials for contaminant AND vice versa  
✅ **Structured queries** - `SELECT * FROM related_materials WHERE severity='high'`  
✅ **Filtering** - Filter by frequency, severity, context  
✅ **Aggregation** - Count linkages, analyze patterns

### 5.4 Scalability

✅ **Add new fields** - Structure supports extensions  
✅ **Domain-agnostic** - Same pattern for Materials, Settings, Compounds  
✅ **API-ready** - JSON-serializable structure  
✅ **Search-friendly** - Structured data for search indexing

---

## 6. Migration Impact

### 6.1 What Gets Replaced

| Current Field | New Location | Action |
|---------------|--------------|--------|
| `valid_materials` | `domain_linkages.related_materials` | Migrate + enhance with metadata |
| `eeat.citations` | `domain_linkages.regulatory_compliance` | Convert to standard IDs + enhance |
| `fumes_generated` | `domain_linkages.related_compounds` | Remove exposure limits, enhance |
| `ppe_requirements` | `domain_linkages.ppe_requirements` | Convert to PPE IDs + enhance |

### 6.2 What Gets Removed

❌ **Duplicate exposure limits** - `fumes_generated[].exposure_limit_mg_m3`  
❌ **Duplicate hazard classes** - `fumes_generated[].hazard_class`  
❌ **String citations** - Raw citation strings replaced with standard IDs  
❌ **Simple PPE strings** - Replaced with structured references

### 6.3 What Gets Preserved

✅ **All relationship data** - No linkages lost  
✅ **Context-specific info** - Concentration ranges, contexts preserved  
✅ **Laser parameters** - Untouched, remains in `laser_properties`  
✅ **Safety data** - Fire risk, ventilation, etc. remain

---

## 7. Affected Systems

### 7.1 Data Files

- ✅ **Contaminants.yaml** - 98 entries updated
- ✅ **Materials.yaml** - Receives `related_contaminants` (reverse links)
- ✅ **Compounds.yaml** - Receives `produced_by_contaminants` (reverse links)
- ✅ **Settings.yaml** - Future: receives `related_contaminants`

### 7.2 Frontmatter Files

- ⚠️ **Regeneration required** - All frontmatter files must be regenerated after migration
- ⚠️ **Exporter update needed** - Trivial exporter must understand new structure

### 7.3 UI Components

- 📝 **Material cards** - Can now render with images and links
- 📝 **Compound cards** - Fetch exposure limits from Compounds.yaml
- 📝 **Regulatory badges** - Display standard logos and links
- 📝 **PPE requirement cards** - Show specifications and standards

---

## 8. Implementation Plan

### 8.1 Phase 1: Migration Script (1 hour)

1. Fix corrupted `migrate_to_domain_linkages.py`
2. Test on adhesive-residue only
3. Verify output structure matches spec
4. Run full migration (98 contaminants)

### 8.2 Phase 2: Bidirectional Links (1 hour)

1. Generate `related_contaminants` for Materials.yaml
2. Generate `produced_by_contaminants` for Compounds.yaml
3. Validate bidirectional consistency

### 8.3 Phase 3: Frontmatter Regeneration (30 min)

1. Update trivial exporter to handle new structure
2. Regenerate all frontmatter files
3. Verify frontmatter structure matches data

### 8.4 Phase 4: UI Updates (2-3 hours)

1. Update Vue components to use new fields
2. Add card rendering for all linkage types
3. Test navigation between linked entities
4. Deploy

**Total Estimated Time:** 4-5 hours

---

## 9. Validation Checklist

### 9.1 Data Validation

- [ ] All `valid_materials` converted to `related_materials` with metadata
- [ ] All `eeat.citations` converted to `regulatory_compliance` with standard IDs
- [ ] All `fumes_generated` converted to `related_compounds` WITHOUT exposure limits
- [ ] All `ppe_requirements` converted to structured format with PPE IDs
- [ ] No duplicate exposure limits remain in Contaminants.yaml
- [ ] All IDs are valid kebab-case
- [ ] All URLs follow convention

### 9.2 Linkage Validation

- [ ] 1,063 material linkages created (49 materials × ~22 avg contaminants)
- [ ] 376 compound linkages created
- [ ] 20 regulatory standard linkages created
- [ ] 172 PPE requirement linkages created
- [ ] All reverse links populated (Materials → Contaminants, Compounds → Contaminants)

### 9.3 UI Validation

- [ ] Material cards render with images
- [ ] Compound cards fetch exposure limits from Compounds.yaml
- [ ] Regulatory badges display standard logos
- [ ] PPE cards show specifications
- [ ] Navigation between linked entities works
- [ ] Bidirectional navigation functional

---

## 10. Rollback Plan

If migration fails:

1. **Restore from Git** - `git checkout data/contaminants/Contaminants.yaml`
2. **Revert frontmatter** - Regenerate from backup data
3. **Fix script** - Debug migration script issues
4. **Retry** - Run migration again after fixes

**Backup Location:** `scripts/data/migrate_to_domain_linkages.py.backup`

---

## 11. Questions for Review

### 11.1 Structural Questions

1. ✅ **Field naming** - Are `id`, `title`, `url`, `image` the right universal fields?
2. ✅ **Nesting key** - Is `domain_linkages` the right top-level key?
3. ⚠️ **Sub-keys** - Are `related_materials`, `related_compounds`, etc. clear enough?
4. ⚠️ **Material URLs** - Should we use category paths (`/materials/metals/aluminum/aluminum`) or flat (`/materials/aluminum`)?

### 11.2 Data Questions

5. ⚠️ **Default values** - Okay to default `frequency=common`, `severity=moderate` for now?
6. ⚠️ **Context inference** - Okay to infer `typical_context=general` initially?
7. ✅ **Exposure limits** - Confirmed: Remove from contaminants, reference compounds?

### 11.3 Implementation Questions

8. ⚠️ **Migration timing** - Should we migrate all 98 contaminants at once or test on subset first?
9. ⚠️ **Frontmatter timing** - Regenerate immediately after migration or wait for UI updates?
10. ⚠️ **Legacy field removal** - Should we remove `valid_materials`, `eeat.citations` immediately or keep temporarily?

---

## 12. Approval Status

- [ ] **Structure approved** - User confirms `domain_linkages` structure
- [ ] **Fields approved** - User confirms required fields (id, title, url, image)
- [ ] **Migration approved** - User approves migration script execution
- [ ] **Timeline approved** - User confirms 4-5 hour implementation timeline

**Next Step After Approval:** Fix migration script and run test migration on adhesive-residue

---

**Document Version:** 1.0.0  
**Last Updated:** December 15, 2025  
**Status:** ⏳ Awaiting Review
