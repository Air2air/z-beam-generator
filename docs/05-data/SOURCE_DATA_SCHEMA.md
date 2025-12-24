# Source Data Schema Reference

**Version**: 2.0.0  
**Last Updated**: December 23, 2025  
**Purpose**: Defines the canonical structure for all source YAML files

---

## 🎯 Overview

This document defines the **required structure** for all source data files:
- `data/materials/Materials.yaml`
- `data/contaminants/Contaminants.yaml`
- `data/settings/Settings.yaml`
- `data/compounds/Compounds.yaml`

**Key Principle**: Source data should contain **raw facts only**. Generated content, enrichments, and frontend metadata belong in frontmatter (export output), not source files.

**Related Policies** (MANDATORY reading):
- `DATA_STORAGE_POLICY.md` - Single source of truth, dual-write architecture
- `DATA_FLOW.md` - Three-layer architecture (source → export → frontmatter)
- `MATERIAL_NAME_CONSISTENCY_POLICY.md` - ID format rules across domains
- `FRONTMATTER_SOURCE_OF_TRUTH_POLICY.md` - Never edit generated files

---

## 📋 Materials.yaml Schema

### Top-Level Structure
```yaml
schema_version: "2.0.0"
last_updated: "YYYY-MM-DD"
category_metadata:
  {category_name}:
    article_type: "material"
    description: "..."
material_index:
  {Display Name}: {category}
materials:
  {material-slug-laser-cleaning}:
    # Material fields (see below)
```

### Material Entry Structure

#### ✅ REQUIRED Core Fields
```yaml
name: "Aluminum"                    # Display name (no suffix)
id: "aluminum-laser-cleaning"       # Unique identifier with suffix
category: "metal"                   # Primary category
subcategory: "non-ferrous"          # Secondary classification
full_path: "/materials/metal/non-ferrous/aluminum-laser-cleaning"
title: "Aluminum Laser Cleaning"   # SEO title
```

#### ✅ REQUIRED Content Fields
```yaml
author:
  id: 1                             # Author ID (1-4)

micro:                              # Microscopic descriptions
  before: "..."                     # Pre-cleaning state
  after: "..."                      # Post-cleaning state

faq:                                # FAQ items
  - question: "..."
    answer: "..."
  - question: "..."
    answer: "..."

images:                             # Image metadata
  hero:
    url: "/images/material/aluminum-laser-cleaning-hero.jpg"
    alt: "..."
  micro:
    url: "/images/material/aluminum-laser-cleaning-micro.jpg"
    alt: "..."
```

#### ✅ REQUIRED Data Fields
```yaml
properties:                         # Measured properties
  material_characteristics:
    label: "Material Characteristics"
    description: "..."
    density:
      value: 2.7
      unit: "g/cm³"
      confidence: 98
      min: 0.53
      max: 22.6
    # ... other properties

characteristics:                    # Material characteristics
  crystallineStructure:
    value: "FCC"
    unit: "crystal system"
    description: "..."
    source: "ai_research"
  # ... other characteristics
```

#### ✅ REQUIRED Relationships Block
```yaml
relationships:                      # ALL relationship data
  contaminated_by:                  # Contaminant relationships
    presentation: "card"            # Display variant
    items:
      - id: "adhesive-residue-contamination"
      - id: "blood-residue-contamination"
  
  industry_applications:            # Industry list
    - "Aerospace"
    - "Medical Devices"
    - "Electronics Manufacturing"
  
  regulatory_standards:             # Regulatory compliance
    presentation: "card"
    items:
      - name: "FDA"
        longName: "Food and Drug Administration"
        description: "FDA 21 CFR 1040.10 - Laser Product Performance Standards"
        url: "https://..."
        image: "/images/logo/logo-org-fda.png"
```

#### ✅ OPTIONAL Metadata Fields
```yaml
metadata:                           # System metadata
  last_updated: "2025-12-23T10:30:00Z"
  normalization_applied: true
  restructured_date: "2025-12-23T10:30:00Z"
  structure_version: "2.0"
```

#### ❌ PROHIBITED Fields (Generated Content)
```yaml
# These belong in FRONTMATTER only, NOT source data:
card: {...}                         # ❌ Frontend card metadata
components: {...}                   # ❌ Generated descriptions
description: "..."                  # ❌ Generated long-form content
settings_description: "..."         # ❌ Generated settings text
meta_description: "..."             # ❌ SEO meta description
page_title: "..."                   # ❌ SEO page title
contamination: {...}                # ❌ Derived validation rules
eeat: {...}                         # ❌ Quality signals
voice_enhanced: "..."               # ❌ Generation timestamp
```

---

## 🔄 Relationship Field Specification

### Structure Rules

1. **ALL relationships MUST be inside `relationships:` block**
2. **Presentation-based relationships** (card/list/table display):
   ```yaml
   relationships:
     {field_name}:
       presentation: "card"  # or "list" or "table"
       items:
         - id: "item-slug"
         - id: "another-item"
   ```

3. **Simple list relationships** (no presentation needed):
   ```yaml
   relationships:
     industry_applications:
       - "Industry 1"
       - "Industry 2"
   ```

4. **Rich object relationships** (with metadata):
   ```yaml
   relationships:
     regulatory_standards:
       presentation: "card"
       items:
         - name: "FDA"
           longName: "Full Organization Name"
           description: "Standard description"
           url: "https://..."
           image: "/path/to/logo.png"
   ```

### Common Relationship Fields

| Field Name | Type | Structure | Example |
|------------|------|-----------|---------|
| `contaminated_by` | Presentation | ID references | `items: [{id: "rust-oxidation"}]` |
| `industry_applications` | Simple list | String array | `["Aerospace", "Medical"]` |
| `regulatory_standards` | Rich objects | Full metadata | See above |
| `removes_contaminants` | Presentation | ID references | Added by export enricher |
| `related_materials` | Presentation | ID references | Added by export enricher |
| `related_settings` | Presentation | ID references | Added by export enricher |
| `produces_compounds` | Presentation | ID references | Added by export enricher |

---

## 🚨 Common Structural Violations

### ❌ VIOLATION #1: Relationships Outside Block
```yaml
# WRONG - regulatory_standards at top level
materials:
  aluminum-laser-cleaning:
    name: "Aluminum"
    regulatory_standards:      # ❌ WRONG LOCATION
      - name: "FDA"
    relationships:
      contaminated_by: {...}
```

```yaml
# CORRECT - ALL relationships inside block
materials:
  aluminum-laser-cleaning:
    name: "Aluminum"
    relationships:
      regulatory_standards:    # ✅ CORRECT LOCATION
        presentation: "card"
        items:
          - name: "FDA"
      contaminated_by: {...}
```

### ❌ VIOLATION #2: Generated Content in Source
```yaml
# WRONG - Generated descriptions in source
materials:
  aluminum-laser-cleaning:
    name: "Aluminum"
    description: "Long generated text..."        # ❌ Generated content
    components:                                   # ❌ Generated content
      description: "Another long text..."
      micro: {...}
    card:                                         # ❌ Frontend metadata
      heading: "Aluminum"
```

```yaml
# CORRECT - Only raw facts in source
materials:
  aluminum-laser-cleaning:
    name: "Aluminum"
    micro:                                        # ✅ Raw content
      before: "..."
      after: "..."
    properties:                                   # ✅ Raw data
      material_characteristics: {...}
```

### ❌ VIOLATION #3: Inconsistent ID Formats
```yaml
# WRONG - Missing suffix
materials:
  aluminum:                    # ❌ Missing "-laser-cleaning"
    name: "Aluminum"
    id: "aluminum"             # ❌ Inconsistent
```

```yaml
# CORRECT - Consistent ID format
materials:
  aluminum-laser-cleaning:     # ✅ With suffix
    name: "Aluminum"
    id: "aluminum-laser-cleaning"  # ✅ Matches key
```

---

## 🔍 Validation Rules

### Required Field Validation
- [ ] `name` - Present and non-empty
- [ ] `id` - Present and matches dictionary key
- [ ] `category` - Present and valid
- [ ] `subcategory` - Present and valid
- [ ] `full_path` - Present and correctly formatted
- [ ] `title` - Present and non-empty
- [ ] `author.id` - Present and valid (1-4)
- [ ] `relationships` - Present (can be empty dict)

### Relationship Validation
- [ ] `regulatory_standards` - Inside relationships block
- [ ] `contaminated_by` - Inside relationships block
- [ ] `industry_applications` - Inside relationships block
- [ ] All relationship fields have proper structure (presentation + items OR simple list)

### Prohibited Field Validation
- [ ] `card` - Must not exist in source
- [ ] `components` - Must not exist in source
- [ ] `description` - Must not exist in source (except in nested objects)
- [ ] `settings_description` - Must not exist in source
- [ ] `meta_description` - Must not exist in source
- [ ] `page_title` - Must not exist in source
- [ ] `contamination` - Must not exist in source
- [ ] `eeat` - Must not exist in source (export generates)
- [ ] `voice_enhanced` - Must not exist in source (export generates)

### ID Format Validation
- [ ] Material IDs end with `-laser-cleaning` (per MATERIAL_NAME_CONSISTENCY_POLICY.md)
- [ ] Contaminant IDs end with `-contamination`
- [ ] Setting IDs end with `-settings` (e.g., `aluminum-settings` not `aluminum`)
- [ ] Compound IDs end with `-compound` (e.g., `carbon-monoxide-compound`)
- [ ] Dictionary key matches `id` field value

**Reference**: See `docs/08-development/MATERIAL_NAME_CONSISTENCY_POLICY.md` for complete cross-domain naming rules.

**Domain Suffix Summary**:
- Materials: `-laser-cleaning`
- Settings: `-settings`
- Contaminants: `-contamination`
- Compounds: `-compound`
- Associations: NO suffix (base slug only)

---

## 📊 Schema Compliance Report

Run validation:
```bash
python3 scripts/validation/validate_source_schema.py
```

Expected output:
```
SOURCE DATA SCHEMA VALIDATION
================================================

✅ Materials.yaml
   - 153 items validated
   - 0 structural violations
   - 0 prohibited fields found
   - 0 relationship misplacements

✅ Contaminants.yaml
   - 98 items validated
   - 0 structural violations

✅ Settings.yaml
   - 153 items validated
   - 0 structural violations

✅ Compounds.yaml
   - 34 items validated
   - 0 structural violations

================================================
OVERALL: 100% Schema Compliance
```

---

## 🔧 Migration Tools

### Normalize Existing Data
```bash
# Move relationships to correct location
python3 scripts/migration/normalize_relationships_structure.py

# Remove generated content from source
python3 scripts/migration/remove_generated_fields.py

# Validate after migration
python3 scripts/validation/validate_source_schema.py
```

---

**MANDATORY Reading**:
- **DATA_STORAGE_POLICY.md** - Single source of truth, dual-write to frontmatter
- **DATA_FLOW.md** - Three-layer architecture (source → export → frontmatter)
- **MATERIAL_NAME_CONSISTENCY_POLICY.md** - ID format across all domains
- **FRONTMATTER_SOURCE_OF_TRUTH_POLICY.md** - Never edit generated output files

**Reference Documentation**:
- **Export Schema**: `export/config/schema.json` - Frontmatter structure
- **Field Order**: `data/schemas/FrontmatterFieldOrder.yaml` - Output field ordering
- **DATA_ARCHITECTURE_GUIDE.md** - Complete architecture overview
- **Data Flow**: `docs/05-data/DATA_FLOW.md` - How data moves through system
- **Field Order**: `data/schemas/FrontmatterFieldOrder.yaml` - Output field ordering

---

## ✅ Checklist for New Data

Before adding new materials/contaminants/settings:

- [ ] Read this schema document
- [ ] Use correct ID format (with suffix)
- [ ] Place ALL relationships inside `relationships:` block
- [ ] Include ONLY raw facts (no generated content)
- [ ] Validate with schema checker
- [ ] Test export to verify frontmatter generation
