# Frontmatter Field Order System
**Status**: ✅ IMPLEMENTED  
**Date**: December 16, 2025  
**Purpose**: Centralized specification for standardized field order across all domains

---

## 📋 Overview

The **Frontmatter Field Order** system provides a single source of truth for field organization in all frontmatter files. It ensures consistency across 424 files and makes field order maintainable from one central location.

### Key Benefits

1. **✅ Consistency** - All files follow same field order
2. **✅ Maintainability** - Update order in one place
3. **✅ Validation** - Automated checks ensure compliance
4. **✅ Documentation** - Clear specification for developers
5. **✅ Exporter Integration** - Generators use correct order automatically

---

## 🏗️ Architecture

### File Structure

```
data/schemas/
└── FrontmatterFieldOrder.yaml    # Central field order specification

shared/validation/
└── field_order.py                # Validator and reorder tool (529 lines)
```

### Data Flow

```
┌─────────────────────────────────────────────────────┐
│  data/schemas/FrontmatterFieldOrder.yaml            │
│  ═══════════════════════════════════════            │
│  • materials.field_order (56 fields)                │
│  • contaminants.field_order (38 fields)             │
│  • compounds.field_order (25 fields)                │
│  • settings.field_order (34 fields)                 │
│  • Nested structure specs                           │
│  • Required fields lists                            │
└─────────────────┬───────────────────────────────────┘
                  │
                  ↓ (Read specification)
┌─────────────────────────────────────────────────────┐
│  shared/validation/field_order.py                   │
│  ═══════════════════════════════════                │
│  • Load schema                                      │
│  • Validate file against spec                      │
│  • Check required fields                           │
│  • Detect out-of-order fields                      │
│  • Reorder fields automatically                    │
└─────────────────┬───────────────────────────────────┘
                  │
                  ↓ (Used by)
┌─────────────────────────────────────────────────────┐
│  export/*/trivial_exporter.py                       │
│  ═══════════════════════════                        │
│  • Read field order spec                            │
│  • Generate frontmatter in correct order            │
│  • Ensure consistency                               │
└─────────────────┬───────────────────────────────────┘
                  │
                  ↓ (Output)
┌─────────────────────────────────────────────────────┐
│  frontmatter/*/                                     │
│  ═══════════════                                    │
│  • All files have standardized field order          │
│  • Consistent structure across domains              │
│  • Easy to review and maintain                      │
└─────────────────────────────────────────────────────┘
```

---

## 📝 Field Order Specification

### Materials Domain (56 fields)

**Identity** → **Classification** → **Physical Properties** → **Optical Properties** →  
**Mechanical Properties** → **Chemical Properties** → **Laser Parameters** →  
**Safety** → **Content** → **Linkages** → **Author** → **Navigation** → **Metadata**

```yaml
materials:
  field_order:
    # Identity (5 fields)
    - id
    - name
    - slug
    - display_name
    - scientific_name
    
    # Classification (4 fields)
    - category
    - subcategory
    - metal_type
    - alloy_family
    
    # ... (see full spec in FrontmatterFieldOrder.yaml)
```

### Contaminants Domain (38 fields)

**Identity** → **Classification** → **Physical Properties** → **Optical Properties** →  
**Chemical Properties** → **Removal Characteristics** → **Safety** →  
**Content** → **Linkages** → **Author** → **Navigation** → **Metadata**

### Compounds Domain (25 fields)

**Identity** → **Chemical Identity** → **Classification** → **Exposure Limits** →  
**Health & Safety** → **Content** → **Linkages** → **Author** → **Navigation** → **Metadata**

### Settings Domain (34 fields)

**Identity** → **Classification** → **Laser Parameters** → **System Configuration** →  
**Process Parameters** → **Quality Metrics** →  
**Content** → **Linkages** → **Author** → **Navigation** → **Metadata**

---

## 🔧 Usage

### 1. Validate Field Order

```bash
# Validate all files in a domain
python3 shared/validation/field_order.py --domain materials
python3 shared/validation/field_order.py --domain compounds
```

**Output**:
```
Validating compounds domain files...

VALIDATION RESULTS:
  Total files: 20
  Valid: 20 (100.0%)
  Invalid: 0

✅ All 20 files valid!
```

### 2. Reorder Files (Dry Run)

```bash
# See what would be changed
python3 shared/validation/field_order.py --domain materials --reorder --dry-run
```

**Output**:
```
DRY RUN: Reordering materials domain files...

DRY RUN REORDER RESULTS:
  Total files: 153
  Reordered: 42
  Unchanged: 111

📝 Files that would be reordered:
  aluminum-laser-cleaning.yaml
  copper-laser-cleaning.yaml
  ...
```

### 3. Reorder Files (Apply Changes)

```bash
# Actually reorder files
python3 shared/validation/field_order.py --domain materials --reorder
```

**Output**:
```
Reordering materials domain files...

REORDER RESULTS:
  Total files: 153
  Reordered: 42
  Unchanged: 111

📝 Files reordered: [list of files]
```

### 4. Use in Exporters

```python
from shared.validation.field_order import FrontmatterFieldOrderValidator

# Initialize
validator = FrontmatterFieldOrderValidator()

# Get field order for domain
field_order = validator.get_field_order('materials')
# Returns: ['id', 'name', 'slug', 'display_name', ...]

# Reorder data before export
from collections import OrderedDict
ordered_data = validator.reorder_fields(material_data, 'materials')

# Export with correct field order
with open(output_file, 'w') as f:
    yaml.dump(dict(ordered_data), f, sort_keys=False)
```

---

## ✅ Validation Rules

### Required Fields Check

Each domain has mandatory fields:

**Materials**:
- `id`, `name`, `slug`, `category`, `subcategory`
- `relationships`, `author`, `type`, `domain`

**Compounds**:
- `id`, `name`, `slug`, `chemical_formula`, `category`, `subcategory`
- `relationships`, `author`, `type`, `domain`

### Field Order Check

Fields must appear in specification order:
- Identity fields first
- Classification fields second
- Properties grouped logically
- Content fields near end
- Metadata fields last

### Unexpected Fields Warning

Fields not in specification are flagged:
```
⚠️ Unexpected fields (not in spec): legacy_field, deprecated_field
```

---

## 📊 Current Status (Dec 16, 2025)

### Implementation Complete
- ✅ Schema defined (`FrontmatterFieldOrder.yaml`)
- ✅ Validator implemented (`field_order.py`)
- ✅ CLI tool created
- ✅ Dry-run and apply modes

### Validation Results

| Domain | Total Files | Valid | Invalid | Compliance |
|--------|------------|-------|---------|------------|
| **Compounds** | 20 | 20 | 0 | 100.0% ✅ |
| **Contaminants** | 98 | TBD | TBD | TBD |
| **Materials** | 153 | 0 | 153 | 0.0% ⚠️ |
| **Settings** | 153 | TBD | TBD | TBD |

**Materials Issues**: Legacy fields from previous structure
- Fields like `description`, `eeat`, `properties`
- Need schema update or migration

---

## 🚀 Next Steps

### 1. Schema Refinement
**Priority**: HIGH  
**Timeline**: 2 hours

- Update materials spec to include legacy fields
- Decide which fields to keep vs deprecate
- Create migration plan for deprecated fields

### 2. Batch Reorder
**Priority**: MEDIUM  
**Timeline**: 1 hour

Once schema refined:
```bash
python3 shared/validation/field_order.py --domain materials --reorder
python3 shared/validation/field_order.py --domain contaminants --reorder
python3 shared/validation/field_order.py --domain settings --reorder
```

### 3. Exporter Integration
**Priority**: HIGH  
**Timeline**: 2-3 hours

Update all exporters to use field order validator:
- `export/core/trivial_exporter.py`
- `export/contaminants/trivial_exporter.py`
- `export/compounds/trivial_exporter.py`

### 4. CI/CD Integration
**Priority**: MEDIUM  
**Timeline**: 1 hour

Add field order validation to test suite:
- Pre-commit hook
- CI/CD pipeline check
- Block merges if field order invalid

---

## 🔒 Nested Structure Specifications

### Domain Linkages Structure

```yaml
relationships:
  # Materials domain
  related_contaminants: [...]   # List of contaminant links
  related_compounds: [...]       # List of compound links
  related_settings: [...]        # List of settings links
  
  # Contaminants domain
  related_materials: [...]       # List of material links
  produces_compounds: [...]      # List of compound links
  recommended_settings: [...]    # List of settings links
  
  # Compounds domain
  produced_by_contaminants: [...] # List of contaminant links
  related_materials: [...]        # List of material links
```

### Link Item Structure

```yaml
- id: material-id-laser-cleaning
  title: Material Display Name
  url: /materials/category/subcategory/material-id
  image: /images/materials/category/subcategory/material-id.jpg
  frequency: very_common     # Context-specific field
  severity: high             # Context-specific field
  typical_context: "..."     # Context-specific field
```

### Author Structure

```yaml
author:
  id: 1
  name: Author Name
  country: US
  country_display: United States
  # ... (18 total fields)
  # See FrontmatterFieldOrder.yaml for complete structure
```

---

## 💡 Best Practices

### For Developers

1. **Always check spec first** before adding new fields
2. **Use validator** before committing frontmatter changes
3. **Group related fields** logically in spec
4. **Document field purpose** in schema comments

### For Exporters

1. **Load field order** from spec, don't hardcode
2. **Use OrderedDict** or preserve key order
3. **Set `sort_keys=False`** in YAML dump
4. **Validate output** after generation

### For Content Editors

1. **Don't manually reorder** - use validator tool
2. **Check validation** after manual edits
3. **Report unexpected fields** for schema update
4. **Use dry-run** before applying changes

---

## 📁 Related Files

### Implementation
- `data/schemas/FrontmatterFieldOrder.yaml` - Central specification (379 lines)
- `shared/validation/field_order.py` - Validator and reorder tool (529 lines)

### Related Systems
- `data/associations/DomainAssociations.yaml` - Relationship data
- `shared/validation/domain_associations.py` - Association validator
- `export/*/trivial_exporter.py` - Frontmatter generators

### Documentation
- `DOMAIN_ASSOCIATIONS_ARCHITECTURE_DEC16_2025.md` - Association system
- `docs/DOMAIN_LINKAGES_STRUCTURE.md` - Linkage structure spec

---

## 🎯 Success Criteria

### Phase 1: Foundation (COMPLETE ✅)
- [x] Schema defined with all 4 domains
- [x] Validator implemented with CLI
- [x] Dry-run mode working
- [x] Reorder functionality implemented

### Phase 2: Refinement (PENDING ⏳)
- [ ] Materials schema updated for legacy fields
- [ ] All 424 files validated successfully
- [ ] Decision on deprecated fields

### Phase 3: Integration (PENDING ⏳)
- [ ] Exporters use field order spec
- [ ] CI/CD validation added
- [ ] Documentation complete
- [ ] All files reordered if needed

---

## 📖 Examples

### Valid Compounds File

```yaml
id: pahs-compound
name: Polycyclic Aromatic Hydrocarbons
display_name: PAHs
slug: pahs
chemical_formula: Various
cas_number: N/A
molecular_weight: null
category: carcinogen
subcategory: aromatic_hydrocarbon
# ... continues in spec order
```

**Validation**: ✅ PASS (all fields in correct order)

### Invalid Materials File (Before Reorder)

```yaml
name: Aluminum
id: aluminum-laser-cleaning  # ❌ Out of order (id should be first)
category: metal
slug: aluminum               # ❌ Out of order (slug should be 3rd)
# ...
```

**Validation**: ❌ FAIL (fields out of order)

### After Reorder

```yaml
id: aluminum-laser-cleaning  # ✅ Correct position
name: Aluminum               # ✅ Correct position
slug: aluminum               # ✅ Correct position
category: metal              # ✅ Correct position
# ...
```

**Validation**: ✅ PASS

---

**Document Version**: 1.0  
**Last Updated**: December 16, 2025  
**Status**: Implementation complete, refinement and integration pending
