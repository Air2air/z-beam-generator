# Data Flow Documentation

**Purpose**: Document how data flows from source files through enrichers to frontmatter output.

**Created**: December 19, 2025  
**Last Updated**: December 19, 2025

---

## Overview

The Z-Beam export system follows a three-layer architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: SOURCE DATA (Single Source of Truth)                   │
│ • data/materials/Materials.yaml                                  │
│ • data/contaminants/Contaminants.yaml                           │
│ • data/compounds/Compounds.yaml                                 │
│ • data/settings/Settings.yaml                                   │
│ • data/associations/DomainAssociations.yaml                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 2: EXPORT PROCESS (Transformation Logic)                  │
│ • export/core/frontmatter_exporter.py (orchestrator)              │
│ • export/config/*.yaml (domain configurations)                  │
│ • export/enrichers/**/*.py (enrichment logic)                   │
│ • shared/validation/domain_associations.py (relationships)      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 3: FRONTMATTER FILES (Generated Output)                   │
│ • ../z-beam/frontmatter/materials/*.yaml                        │
│ • ../z-beam/frontmatter/contaminants/*.yaml                     │
│ • ../z-beam/frontmatter/compounds/*.yaml                        │
│ • ../z-beam/frontmatter/settings/*.yaml                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Field Data Flow Examples

### Example 1: Compound Linkage URLs

**Field**: `relationships.produces_compounds[].url`

**Flow**:

1. **SOURCE** (`data/compounds/Compounds.yaml`):
   ```yaml
   compounds:
     pahs:
       id: pahs
       full_path: /compounds/carcinogen/aromatic-hydrocarbon/pahs-compound  # SINGLE SOURCE
       category: carcinogen
       subcategory: aromatic_hydrocarbon
   ```

2. **ASSOCIATIONS** (`data/associations/DomainAssociations.yaml`):
   ```yaml
   contaminant_produces_compounds:
     fire-damage:
       - pahs-compound  # References compound ID
   ```

3. **TRANSFORMATION** (`shared/validation/domain_associations.py`):
   ```python
   # Read full_path from Compounds.yaml (single source of truth)
   compound_data = compounds_data['compounds']['pahs']
   url = compound_data.get('full_path')  # "/compounds/carcinogen/aromatic-hydrocarbon/pahs-compound"
   
   # Build relationship linkage
   relationship = {
       'id': 'pahs-compound',
       'url': url,  # FROM FULL_PATH
       'category': compound_data['category'],
       'subcategory': compound_data['subcategory']
   }
   ```

4. **OUTPUT** (`../z-beam/frontmatter/contaminants/fire-damage-contamination.yaml`):
   ```yaml
   relationships:
     produces_compounds:
       - id: pahs-compound
         url: /compounds/carcinogen/aromatic-hydrocarbon/pahs-compound
         category: carcinogen
         subcategory: aromatic_hydrocarbon
   ```

**Key Principle**: URL comes from `full_path` field (single source), not derived from category/subcategory.

---

### Example 2: Material Name and Display

**Field**: `name`, `display_name`

**Flow**:

1. **SOURCE** (`data/materials/Materials.yaml`):
   ```yaml
   materials:
     aluminum:
       name: Aluminum  # Source name
       # No display_name in source
   ```

2. **ENRICHMENT** (`export/enrichers/metadata/name_enricher.py`):
   ```python
   # If display_name missing, copy from name
   if 'display_name' not in frontmatter:
       frontmatter['display_name'] = frontmatter['name']
   ```

3. **OUTPUT** (`../z-beam/frontmatter/materials/aluminum-material.yaml`):
   ```yaml
   name: Aluminum
   display_name: Aluminum  # Enriched
   ```

**Key Principle**: Enrichers add computed fields but never modify source data.

---

### Example 3: Breadcrumb Navigation

**Field**: `breadcrumb`

**Flow**:

1. **SOURCE** (`data/materials/Materials.yaml`):
   ```yaml
   materials:
     alabaster:
       category: stone
       subcategory: sedimentary
   ```

2. **ENRICHMENT** (`export/core/frontmatter_exporter.py` - BreadcrumbEnricher):
   ```python
   # Build breadcrumb from category hierarchy
   breadcrumb = [
       {'label': 'Home', 'href': '/'},
       {'label': 'Materials', 'href': '/materials'},
       {'label': 'Stone', 'href': '/materials/stone'},
       {'label': 'Sedimentary', 'href': '/materials/stone/sedimentary'}
   ]
   ```

3. **OUTPUT** (`../z-beam/frontmatter/materials/alabaster-material.yaml`):
   ```yaml
   breadcrumb:
     - label: Home
       href: /
     - label: Materials
       href: /materials
     - label: Stone
       href: /materials/stone
     - label: Sedimentary
       href: /materials/stone/sedimentary
   ```

**Key Principle**: Breadcrumbs computed from category hierarchy, not stored in source.

---

### Example 4: Field Defaults via UniversalLinkageEnricher

**Field**: `produces_compounds[].concentration_range`

**Flow**:

1. **ASSOCIATIONS** (`data/associations/DomainAssociations.yaml`):
   ```yaml
   contaminant_produces_compounds:
     fire-damage:
       - carbon-monoxide  # No concentration_range specified
   ```

2. **SOURCE** (`data/compounds/Compounds.yaml`):
   ```yaml
   compounds:
     carbon-monoxide:
       concentration_range: "100-500 ppm"  # Default value
   ```

3. **ENRICHMENT** (`export/enrichers/linkage/universal_linkage_enricher.py`):
   ```python
   # Auto-fill missing fields from source
   if 'concentration_range' not in linkage_item:
       linkage_item['concentration_range'] = compound_data['concentration_range']
   ```

4. **OUTPUT** (`../z-beam/frontmatter/contaminants/fire-damage-contamination.yaml`):
   ```yaml
   relationships:
     produces_compounds:
       - id: carbon-monoxide
         concentration_range: "100-500 ppm"  # Enriched from source
   ```

**Key Principle**: Enrichers fill missing fields from source, don't override existing values.

---

## Enricher Execution Order

Enrichers run in specific order (defined in `export/config/{domain}.yaml`):

1. **Structural** - Set up basic frontmatter structure
2. **Metadata** - Populate name, display_name, slug
3. **Relationships** - Add relationship linkages
4. **Linkage** - Fill missing fields in linkages
5. **Grouping** - Group relationships by category
6. **Cleanup** - Remove temporary fields, validate

**Example Order** (from `export/config/contaminants.yaml`):
```yaml
enrichers:
  - type: slug          # 1. Add slug field
  - type: author        # 2. Add author info
  - type: relationships # 3. Add relationship linkages
  - type: universal_linkage  # 4. Fill missing compound fields
  - type: cleanup       # 5. Remove temp fields
```

---

## Data Validation Points

### 1. Source Data Validation

**Location**: `shared/validation/schema_validator.py`  
**Timing**: On load (lazy validation)  
**Checks**:
- Required fields present
- Field types correct
- Enum values valid

### 2. Enricher Output Validation

**Location**: `export/enrichers/validation.py`  
**Timing**: After each enricher (optional)  
**Checks**:
- Enriched fields have correct structure
- Required fields populated
- No empty/invalid URLs

### 3. Final Output Validation

**Location**: `export/core/frontmatter_exporter.py`  
**Timing**: Before writing frontmatter  
**Checks**:
- All required fields present
- YAML structure valid
- No null values in critical fields

---

## Key Architectural Principles

### 1. Single Source of Truth

**Principle**: Each data point has ONE authoritative source.

**Example**: Compound URLs
- ✅ **Correct**: Read from `full_path` in Compounds.yaml
- ❌ **Wrong**: Derive from category/subcategory in enricher

### 2. Enrichment vs Modification

**Principle**: Enrichers ADD fields, never MODIFY source data.

**Example**: display_name
- ✅ **Correct**: Copy from `name` if missing
- ❌ **Wrong**: Replace `name` with formatted version

### 3. Fail-Fast Configuration

**Principle**: Missing required data fails immediately.

**Example**: Full path lookup
- ✅ **Correct**: Fail if compound not found
- ❌ **Wrong**: Use fallback URL like `/compounds/general/misc/{id}`

### 4. Validation at Every Layer

**Principle**: Validate at source, enrichment, and output.

**Example**: Relationship URLs
- Source: full_path must exist in source data
- Enrichment: Validator checks URL structure
- Output: Schema validation before writing file

---

## Common Data Flow Patterns

### Pattern 1: Direct Copy

**Usage**: Simple fields that don't need transformation

**Example**: `name`, `category`, `subcategory`

**Code**:
```python
frontmatter['name'] = source_data['name']
```

---

### Pattern 2: Computed Field

**Usage**: Fields derived from other data

**Example**: `slug` (from name)

**Code**:
```python
from shared.text.utils.formatters import generate_slug
frontmatter['slug'] = generate_slug(source_data['name'])
```

---

### Pattern 3: Lookup and Join

**Usage**: Relationships between domains

**Example**: `produces_compounds` linkages

**Code**:
```python
# 1. Get compound IDs from associations
compound_ids = associations['contaminant_produces_compounds'][contaminant_id]

# 2. Look up each compound in Compounds.yaml
for compound_id in compound_ids:
    compound_data = compounds_data['compounds'][compound_id]
    
    # 3. Build linkage with data from source
    linkage = {
        'id': compound_id,
        'url': compound_data['full_path'],  # FROM SOURCE
        'category': compound_data['category']
    }
```

---

### Pattern 4: Default Value Fill

**Usage**: Optional fields with defaults

**Example**: `concentration_range` in compound linkages

**Code**:
```python
# If field missing, fill from source
if 'concentration_range' not in linkage:
    linkage['concentration_range'] = compound_data['concentration_range']
```

---

## Debugging Data Flow Issues

### Issue: Field Not Appearing in Output

**Steps**:
1. Check if field in source YAML
2. Check if enricher copies field
3. Check if field removed by cleanup enricher
4. Enable debug logging: `export.enrichers=DEBUG`

### Issue: Wrong Field Value

**Steps**:
1. Check source data value
2. Check which enricher modifies field
3. Check enricher execution order
4. Look for multiple enrichers touching same field

### Issue: Empty/Null Field

**Steps**:
1. Check if field optional or required
2. Check if enricher fills default
3. Check if validation allows null
4. Look for missing data in source

---

## Related Documentation

- **Architecture**: `docs/02-architecture/export-system.md`
- **Enrichers**: `docs/03-components/enrichers/`
- **Validation**: `docs/08-development/DATA_VALIDATION_STRATEGY.md`
- **Schema**: `data/schemas/`

---

## Maintenance Notes

**When Adding New Fields**:
1. Add to source YAML schema
2. Document in this file (add example)
3. Add enricher if computation needed
4. Add validation if critical field
5. Test export end-to-end

**When Modifying Enrichers**:
1. Document change in this file
2. Update affected field examples
3. Add validation to catch errors
4. Test with multiple domains

**When Changing Data Structure**:
1. Update ALL three layers (source, enrichment, output)
2. Update schema definitions
3. Update this documentation
4. Run migration script if needed
5. Re-export all domains
