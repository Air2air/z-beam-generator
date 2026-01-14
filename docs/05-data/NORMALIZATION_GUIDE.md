# Normalization Guide

**Created**: December 12, 2025 (Consolidated from 5 source documents)  
**Status**: Complete reference for all normalization operations  
**Purpose**: Ensure consistent data formatting across all YAML files

---

## 📚 Document Sources

This consolidated guide combines:
1. **FRONTMATTER_NORMALIZATION_ANALYSIS_DEC11_2025.md** (10.4 KB)
2. **NORMALIZATION_IMPLEMENTATION_COMPLETE_DEC11_2025.md** (12.4 KB)
3. **NORMALIZED_EXPORT_IMPLEMENTATION.md** (8.2 KB)
4. **ADDITIONAL_NORMALIZATIONS_DEC11_2025.md** (10.9 KB)
5. **AUTHOR_NORMALIZATION_PLAN_DEC11_2025.md** (16.5 KB)

**Archive Location**: `docs/archive/2025-12/normalization/`

---

## 🎯 Overview

Normalization ensures:
- ✅ **Consistent formatting** across all YAML files
- ✅ **Schema compliance** with defined data models
- ✅ **Predictable data access** for all systems
- ✅ **No silent failures** from missing/malformed data

---

## 📋 Normalization Categories

### 1. Author Normalization

**Goal**: Consistent author representation across all data files.

#### Author Registry (Authoritative Source)

**Location**: `shared/voice/profiles/*.yaml`

| ID | Full Name | Country |
|----|-----------|---------|
| 1 | Ikmanda Roswati, Ph.D. | Indonesia |
| 2 | Alessandro Moretti, Ph.D. | Italy |
| 3 | Yi-Chun Lin, Ph.D. | Taiwan |
| 4 | Todd Dunning, MA | United States |

#### Author Field Structure

**Standard Format**:
```yaml
author:
  id: 3
  name: "Yi-Chun Lin"
```

**Common Issues Fixed**:
```yaml
# ❌ BEFORE - Inconsistent formats
author: "Yi-Chun Lin"                    # String instead of object
author: {id: 3}                          # Missing name
author: {name: "Yi-Chun"}                # Missing id, wrong name format
author: {id: 3, name: "Yi-Chun Lin, Ph.D."}  # Extra credentials in name

# ✅ AFTER - Normalized format
author:
  id: 3
  name: "Yi-Chun Lin"
```

#### Normalization Rules

1. **Always use object format** with `id` and `name` fields
2. **Name format**: "FirstName LastName" (no credentials)
3. **ID must match registry**: 1-4 only
4. **No fallbacks**: Fail if author missing or invalid

#### Implementation

```python
def normalize_author(author_data):
    """Normalize author field to consistent format."""
    if isinstance(author_data, str):
        # Convert string to object
        author_id = resolve_author_id_from_name(author_data)
        return {
            'id': author_id,
            'name': get_author_name(author_id)
        }
    
    if isinstance(author_data, dict):
        # Validate and normalize object
        if 'id' not in author_data:
            raise ValueError("Author missing 'id' field")
        
        author_id = author_data['id']
        if author_id not in [1, 2, 3, 4]:
            raise ValueError(f"Invalid author ID: {author_id}")
        
        # Standardize name format (remove credentials)
        correct_name = get_author_name(author_id)
        
        return {
            'id': author_id,
            'name': correct_name
        }
    
    raise ValueError("Author must be string or dict")
```

---

### 2. Frontmatter Normalization

**Goal**: Ensure all frontmatter files match schema and format conventions.

#### Field Ordering

**Standard Order** (for readability):
```yaml
# 1. Metadata
slug: aluminum-alloy-6061
title: "Aluminum Alloy 6061"

# 2. Author
author:
  id: 2
  name: "Alessandro Moretti"

# 3. Content
description: "Comprehensive description..."
micro: "Brief micro content..."

# 4. Properties (if applicable)
properties:
  density: ...
  hardness: ...

# 5. References (if applicable)
related_materials: []
related_contaminants: []
```

#### Boolean Normalization

**Standard Format**: Use lowercase `true`/`false` (YAML standard)

```yaml
# ❌ WRONG - Inconsistent boolean formats
is_active: True       # Python-style
is_active: TRUE       # Uppercase
is_active: yes        # YAML alternate
is_active: "true"     # String

# ✅ CORRECT - Lowercase boolean
is_active: true
is_active: false
```

#### Numeric Formatting

**Rules**:
1. **Integers**: No decimals (`1500` not `1500.0`)
2. **Floats**: Use decimal point when needed (`2.7`, `8.96`)
3. **Ranges**: Use `min`/`max` structure (not `range` array)
4. **Null values**: Use `null` (not `None`, empty string, or 0)

```yaml
# ✅ CORRECT numeric formats
density: 2.7          # Float with decimal
hardness: 95          # Integer without decimal
melting_point:        # Range with min/max
  min: 582
  max: 652
```

#### URL Normalization

**Contaminant URLs**: Must use kebab-case slug format

```yaml
# ❌ WRONG - Inconsistent URL formats
url: /contaminants/Rust_Oxidation
url: /contaminants/rust oxidation
url: /laser-cleaning/contaminants/rust-oxidation

# ✅ CORRECT - Kebab-case slug
url: /contaminants/rust-oxidation
```

**Materials URLs**: Similar format
```yaml
url: /materials/aluminum-alloy-6061
```

#### Null Handling

**Policy**: Use `null` explicitly, never omit required fields

```yaml
# ❌ WRONG - Field missing or wrong null format
# (field omitted)
min_thickness: None
min_thickness: ""
min_thickness: 0      # 0 is a value, not null

# ✅ CORRECT - Explicit null
min_thickness: null
```

---

### 3. Property Normalization

**Goal**: Consistent property value formatting across all materials.

#### Range Format

**Standard Structure**:
```yaml
property_name:
  min: <number>
  max: <number>
  unit: "<unit_string>"
```

**Examples**:
```yaml
density:
  min: 2.63
  max: 2.80
  unit: "g/cm³"

hardness:
  min: 95
  max: 150
  unit: "HB"

melting_point:
  min: 582
  max: 652
  unit: "°C"
```

#### Single Value Properties

For properties with single values (not ranges):
```yaml
property_name:
  value: <number>
  unit: "<unit_string>"
```

#### Property Completeness

**Required Fields**:
- All numeric properties must have `unit` field
- Ranges must have both `min` and `max` (or use `null`)
- Values must be numbers (not strings)

```yaml
# ❌ WRONG
density: "2.7 g/cm³"          # String instead of structured
hardness: {min: 95}           # Missing max
melting_point: {min: 582, max: 652}  # Missing unit

# ✅ CORRECT
density:
  value: 2.7
  unit: "g/cm³"
hardness:
  min: 95
  max: 150
  unit: "HB"
melting_point:
  min: 582
  max: 652
  unit: "°C"
```

---

### 4. Additional Normalizations

#### String Formatting

**Rules**:
1. **Quotes**: Always use double quotes for strings
2. **Multiline**: Use `|` or `>` for long text
3. **Escaping**: Escape special characters properly

```yaml
# Single-line strings
title: "Aluminum Alloy 6061"

# Multiline strings (preserves newlines)
description: |
  First paragraph of description.
  
  Second paragraph with more detail.

# Multiline folded (single line output)
micro: >
  This is a long micro content that wraps
  but will be output as single line.
```

#### Array Formatting

**Rules**:
1. **Empty arrays**: Use `[]` not omission
2. **Single item**: Use array format `[item]` or `- item`
3. **Multiple items**: Use `-` list format

```yaml
# Empty array
related_materials: []

# Single item (both valid)
related_materials: ["steel"]
related_materials:
  - steel

# Multiple items
related_materials:
  - steel
  - titanium
  - aluminum
```

#### Whitespace Normalization

**Rules**:
1. **Indentation**: 2 spaces (not tabs)
2. **Blank lines**: Max 1 blank line between sections
3. **Trailing whitespace**: Remove all
4. **Line endings**: LF (\\n) not CRLF (\\r\\n)

---

## 🔧 Normalization Tools

### 1. Frontmatter Exporter

**Location**: `export/core/trivial_exporter.py`

**Purpose**: Generate normalized frontmatter from source data (Materials.yaml, Contaminants.yaml, etc.)

**Usage**:
```bash
# Regenerate all frontmatter with normalization
python3 run.py --deploy

# Regenerate specific domain
python3 run.py --deploy --domain materials
```

**Normalization Applied**:
- Author field standardization
- Boolean lowercase conversion
- Numeric formatting
- URL kebab-case
- Field ordering
- Null value handling

### 2. YAML Validator

**Location**: `scripts/validation/`

**Purpose**: Validate YAML files against schema and normalization rules

**Usage**:
```bash
# Validate all YAML files
python3 scripts/validation/validate_yaml.py

# Validate specific file
python3 scripts/validation/validate_yaml.py data/materials/Materials.yaml
```

**Checks**:
- Schema compliance
- Required fields present
- Correct data types
- Normalization rules followed

### 3. Batch Normalization Script

**Purpose**: Fix normalization issues across all files

```python
#!/usr/bin/env python3
"""Batch normalize all YAML files."""

import yaml
from pathlib import Path

def normalize_yaml_file(file_path):
    """Normalize a single YAML file."""
    with open(file_path) as f:
        data = yaml.safe_load(f)
    
    # Apply normalization functions
    data = normalize_authors(data)
    data = normalize_booleans(data)
    data = normalize_numbers(data)
    data = normalize_urls(data)
    data = normalize_nulls(data)
    
    # Write back with consistent formatting
    with open(file_path, 'w') as f:
        yaml.dump(data, f, 
                 default_flow_style=False,
                 allow_unicode=True,
                 sort_keys=False,
                 indent=2)

# Usage
for yaml_file in Path('data').rglob('*.yaml'):
    normalize_yaml_file(yaml_file)
```

---

## 📊 Normalization Checklist

Before committing changes:

### Author Fields
- [ ] All `author` fields use object format `{id, name}`
- [ ] Author IDs are 1-4 only
- [ ] Author names match registry (no credentials)
- [ ] No string-format authors

### Boolean Fields
- [ ] All booleans are lowercase (`true`/`false`)
- [ ] No Python-style (`True`/`False`)
- [ ] No string booleans (`"true"`)

### Numeric Fields
- [ ] Integers have no decimals (95 not 95.0)
- [ ] Floats have decimals when needed (2.7)
- [ ] Ranges use `min`/`max` structure
- [ ] All properties have `unit` field

### URL Fields
- [ ] All URLs use kebab-case slugs
- [ ] No spaces, underscores, or uppercase
- [ ] Correct path prefix (/materials/, /contaminants/)

### Null Fields
- [ ] Explicit `null` used (not omitted)
- [ ] No empty strings for nulls
- [ ] No `None` (Python-style)
- [ ] No 0 values used as null

### String Fields
- [ ] Double quotes for strings
- [ ] Multiline text uses `|` or `>`
- [ ] No trailing whitespace
- [ ] Special characters escaped

### Array Fields
- [ ] Empty arrays use `[]`
- [ ] Consistent list format (`-` for items)
- [ ] No omitted arrays (use `[]`)

### Whitespace
- [ ] 2-space indentation (no tabs)
- [ ] Max 1 blank line between sections
- [ ] LF line endings (no CRLF)
- [ ] No trailing whitespace

---

## 🚨 Common Issues & Solutions

### Issue 1: Author Format Inconsistency

**Symptom**: Authors as strings, missing IDs, or wrong names

**Detection**:
```bash
# Find string-format authors
grep -r "^author: \"" data/
```

**Solution**:
```python
# Run author normalization
python3 scripts/normalization/normalize_authors.py
```

### Issue 2: Boolean Format Variations

**Symptom**: `True`, `TRUE`, `yes`, `"true"` instead of `true`

**Detection**:
```bash
# Find Python-style booleans
grep -r ": True$" data/
grep -r ": False$" data/
```

**Solution**:
```python
# Run boolean normalization
python3 scripts/normalization/normalize_booleans.py
```

### Issue 3: Numeric Formatting Issues

**Symptom**: Integers with `.0`, strings for numbers, missing units

**Detection**:
```bash
# Find integers with decimals
grep -r ": [0-9]\+\.0$" data/
```

**Solution**:
```python
# Run numeric normalization
python3 scripts/normalization/normalize_numbers.py
```

### Issue 4: URL Format Inconsistency

**Symptom**: Spaces, underscores, uppercase in URLs

**Detection**:
```bash
# Find non-kebab-case URLs
grep -r "url: " frontmatter/ | grep -E "[A-Z_]"
```

**Solution**:
```python
# Run URL normalization
python3 scripts/normalization/normalize_urls.py
```

---

## 📈 Verification

### Automated Verification

**Run validation suite**:
```bash
# Validate all YAML files
python3 scripts/validation/validate_all.py

# Expected output:
# ✅ Materials.yaml: 159 materials validated
# ✅ Contaminants.yaml: 99 contaminants validated
# ✅ Settings.yaml: 45 settings validated
# ✅ All frontmatter files validated
# 
# Total: 303 files validated, 0 errors
```

### Manual Spot Checks

**Author fields**:
```bash
# Should return only object-format authors
grep -A 2 "^author:" data/materials/Materials.yaml | head -30
```

**Boolean fields**:
```bash
# Should return only lowercase true/false
grep ": true$\|: false$" data/materials/Materials.yaml | head -20
```

**URL fields**:
```bash
# Should return only kebab-case URLs
grep "^url: " frontmatter/contaminants/*.yaml | head -20
```

---

## 🔄 Regeneration Workflow

**When to regenerate frontmatter**:
1. After modifying Materials.yaml, Contaminants.yaml, or Settings.yaml
2. After updating export logic in `export/core/trivial_exporter.py`
3. After changing normalization rules
4. As part of deployment process

**Regeneration command**:
```bash
# Full regeneration with normalization
python3 run.py --deploy

# Verify changes
git diff frontmatter/
```

**Post-regeneration checks**:
```bash
# 1. Validate all files
python3 scripts/validation/validate_all.py

# 2. Check for unexpected changes
git diff --stat frontmatter/

# 3. Spot-check random files
cat frontmatter/materials/aluminum-alloy-6061.yaml
cat frontmatter/contaminants/rust-oxidation.yaml

# 4. Run tests
pytest tests/test_frontmatter_normalization.py
```

---

## 📚 Related Documentation

**Policies** (in docs/08-development/):
- `AUTHOR_ASSIGNMENT_POLICY.md` - Author assignment rules
- `NUMERIC_FORMATTING_POLICY.md` - Numeric formatting standards
- `CONTAMINANT_URL_POLICY.md` - URL formatting for contaminants

**Data Architecture** (in docs/05-data/):
- `DATA_STORAGE_POLICY.md` - Where data is stored
- `DATA_ARCHITECTURE.md` - Data flow and relationships
- `ZERO_NULL_POLICY.md` - Null value handling

**Export System** (in export/docs/):
- `ARCHITECTURE.md` - Export system architecture
- `API_REFERENCE.md` - Export API documentation

---

## ✅ Success Criteria

**System is properly normalized when**:

- ✅ All author fields use object format with ID 1-4
- ✅ All booleans are lowercase `true`/`false`
- ✅ All numbers formatted correctly (integers, floats, ranges)
- ✅ All URLs use kebab-case slugs
- ✅ All null values explicit (`null` not omitted)
- ✅ All YAML files pass schema validation
- ✅ Consistent 2-space indentation throughout
- ✅ No trailing whitespace or CRLF line endings
- ✅ Frontmatter files match source data exactly

**Validation command returns zero errors**:
```bash
python3 scripts/validation/validate_all.py
# Exit code: 0 (success)
```

---

**Last Updated**: December 12, 2025  
**Maintainer**: Data Architecture Team  
**Questions**: See root `DOCUMENTATION_MAP.md` for navigation
