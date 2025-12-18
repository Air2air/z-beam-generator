# Frontmatter Generator Requirements

**Version**: 2.0  
**Date**: December 17, 2025  
**Schema Version**: 5.0.0  
**Purpose**: Critical requirements for frontmatter file generation to ensure filename, link consistency, and Schema 5.0.0 compliance

---

## 🚨 Critical Requirements

This document specifies requirements for frontmatter generation with Schema 5.0.0 compliance:

1. ✅ **YAML Serialization** - IMPLEMENTED: Must use yaml.SafeDumper (no Python tags)
2. ❌ **Filename Suffixes** - CRITICAL ISSUE: Settings files missing `-settings` suffix
   - Materials: ✅ 153/153 files (100%) compliant with `-laser-cleaning.yaml`
   - Contaminants: ✅ 98/98 files (100%) compliant with `-contaminant.yaml`
   - Compounds: ✅ 20/20 files (100%) compliant with `-compound.yaml`
   - **Settings: ❌ 0/161 files (0%) compliant** - All need `-settings.yaml` suffix
3. ✅ **Schema 5.0.0** - IMPLEMENTED: Flattened relationships structure
4. ⚠️ **Domain Linkage URLs** - VERIFICATION NEEDED: URLs must use actual slugs from target files

---

## 🚨 CRITICAL: YAML Serialization (SafeDumper)

### The #1 Most Important Requirement

**MUST use `Dumper=yaml.SafeDumper`** to prevent Python-specific tags:

```python
# ❌ WRONG - Creates Python tags that break JavaScript parsers
yaml.dump(data)
yaml.dump(data, default_flow_style=False)

# ✅ CORRECT - MUST use SafeDumper parameter
with open(output_file, 'w', encoding='utf-8') as f:
    yaml.dump(
        frontmatter,
        f,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=120,
        Dumper=yaml.SafeDumper  # ← MANDATORY!
    )
```

**Why This Matters:**
- Without `Dumper=yaml.SafeDumper`, Python creates tags like:
  ```yaml
  !!python/object/apply:collections.OrderedDict
  ```
- JavaScript's `js-yaml` parser **CANNOT** read these Python-specific tags
- This causes **ALL tests to fail** with `YAMLException: unknown tag` errors
- **153 material files failed** because this parameter was missing

**Verification:**
Your YAML file should **NEVER** contain:
- ❌ `!!python/object/apply:collections.OrderedDict`
- ❌ `!!python/object:...`
- ❌ Any `!!python/` prefixed tags

**See**: `FRONTMATTER_FORMATTING_GUIDE.md` for complete formatting requirements.

---

## 🚨 CRITICAL: Schema 5.0.0 Compliance

### Flattened Domain Linkages Structure

**Schema 5.0.0 uses flattened relationships** (no nested objects):

```yaml
# ✅ CORRECT (Schema 5.0.0 - Flattened):
relationships:
  related_contaminants:
  - id: aluminum-oxidation-contamination
    slug: aluminum-oxidation
    title: Aluminum Oxidation
    url: /contaminants/oxidation/non-ferrous/aluminum-oxidation
    # ... other fields at same level

# ❌ WRONG (Old Schema 4.x - Nested):
relationships:
  related_contaminants:
    entries:
    - id: aluminum-oxidation-contamination
      # ... nested structure
```

**Migration**: Use `scripts/normalize_frontmatter_structure.py` to convert 4.x → 5.0.0

**Schema 5.0.0 Linkage Types** (8 total):
1. `produces_compounds` - Materials/Settings that produce compounds
2. `removes_contaminants` - Materials that remove contaminants
3. `found_in_materials` - Contaminants found in materials
4. `effective_against` - Settings effective against contaminants
5. `related_materials` - Related materials
6. `related_contaminants` - Related contaminants
7. `related_compounds` - Related compounds
8. `related_settings` - Related settings

**Tests**: `tests/test_schema_5_normalization.py` - 21 tests verify Schema 5.0.0 compliance

---

## File Naming Requirements

### Filename Patterns (ENFORCED)

**Materials**:
```
Pattern: {material-name}-laser-cleaning.yaml
Example: aluminum-laser-cleaning.yaml
Count: 153 files
```

**Contaminants**:
```
Pattern: {contaminant-name}-contaminant.yaml
Example: aluminum-oxidation-contaminant.yaml
Count: 98 files
```

**Compounds**:
```
Pattern: {compound-name}-compound.yaml
Example: formaldehyde-compound.yaml
Count: 20 files
```

**Settings**:
```
Pattern: {material-name}-settings.yaml
Example: aluminum-settings.yaml
Expected: 161 files
Actual: 0 files ❌ CRITICAL NON-COMPLIANCE
```

**🚨 CRITICAL ISSUE: Settings Filename Non-Compliance**

All 161 settings files are currently non-compliant:

❌ **Current filenames** (examples):
- `Alabaster.yaml` (Title Case, no suffix, space issues)
- `Borosilicate Glass.yaml` (Title Case, spaces, no suffix)
- `Carbon Steel.yaml` (Title Case, spaces, no suffix)
- `aluminum.yaml` (lowercase but missing suffix)

✅ **Required filenames**:
- `alabaster-settings.yaml` (kebab-case with suffix)
- `borosilicate-glass-settings.yaml` (kebab-case with suffix)
- `carbon-steel-settings.yaml` (kebab-case with suffix)
- `aluminum-settings.yaml` (kebab-case with suffix)

**Issues**:
1. ❌ No files have `-settings.yaml` suffix (0/161)
2. ❌ Most files use Title Case instead of kebab-case (~157/161)
3. ❌ Many files contain spaces (~130/161)
4. ❌ Only 4 files are lowercase (aluminum, copper, steel, titanium)

**Impact**: Breaks URL routing, link references, and frontend navigation

**Fix Required**: Rename all 161 settings files to follow pattern

**Tests**: `tests/test_settings_filename_compliance.py` - Automated verification

### Filename Rules
- ✅ MUST use kebab-case (lowercase with hyphens)
- ✅ MUST include type suffix
- ❌ NO underscores
- ❌ NO uppercase letters
- ❌ NO parentheses
- ❌ NO spaces

---

## ID Field Requirements

The `id` field in each file MUST follow these patterns:

### Materials
```yaml
# Filename: aluminum-laser-cleaning.yaml
id: aluminum-laser-cleaning  # MUST match filename exactly
```

### Contaminants
```yaml
# Filename: aluminum-oxidation-contaminant.yaml
id: aluminum-oxidation-contamination  # Note: -contamination not -contaminant
```

### Compounds
```yaml
# Filename: formaldehyde-compound.yaml
id: formaldehyde-compound  # MUST match filename exactly
```

### Settings
```yaml
# Filename: aluminum-settings.yaml
id: Aluminum  # Title Case material name (exception to kebab-case)
```

---

## Slug Field Requirements

The `slug` field MUST match the **base filename** (without type suffix):

### Examples

```yaml
# File: aluminum-laser-cleaning.yaml
slug: aluminum  # Remove -laser-cleaning suffix

# File: aluminum-oxidation-contaminant.yaml
slug: aluminum-oxidation  # Remove -contaminant suffix

# File: formaldehyde-compound.yaml
slug: formaldehyde  # Remove -compound suffix

# File: aluminum-settings.yaml
slug: aluminum  # Remove -settings suffix
```

### Slug Rules
- ✅ MUST be kebab-case
- ✅ MUST match base filename
- ✅ MUST be unique within content type
- ❌ NO abbreviations
- ❌ NO custom variations

---

## 🚨 CRITICAL: Domain Linkages URL Requirements

### The Problem

Currently, URLs in `relationships` use **abbreviated IDs** that don't match actual file slugs:

```yaml
# ❌ CURRENT (WRONG):
relationships:
  related_contaminants:
  - id: adhesive-residue  # ← Abbreviated
    url: /contaminants/.../adhesive-residue  # ← Wrong slug

# Actual file: adhesive-residue-tape-marks-contaminant.yaml
# Actual slug: adhesive-residue-tape-marks  # ← URLs should use THIS
```

### The Solution

URLs MUST use the **actual slug** from the referenced file:

```yaml
# ✅ CORRECT:
relationships:
  related_contaminants:
  - id: adhesive-residue-tape-marks-contamination  # Full ID from target file
    slug: adhesive-residue-tape-marks  # Actual slug from target file
    title: Adhesive Residue / Tape Marks
    url: /contaminants/organic-residue/adhesive/adhesive-residue-tape-marks  # ← Matches slug!
    image: /images/contaminants/organic-residue/adhesive/adhesive-residue-tape-marks.jpg
```

### Link Generation Algorithm

**REQUIRED PROCESS** when generating any link reference:

```python
def generate_link_entry(target_filename, content_type):
    """
    Generate a relationships entry.
    
    CRITICAL: Must load target file to get actual slug.
    """
    # Step 1: Load the target file
    file_path = f"frontmatter/{content_type}/{target_filename}"
    target_data = load_yaml(file_path)
    
    # Step 2: Extract fields from target file
    id_field = target_data['id']         # e.g., "aluminum-oxidation-contamination"
    slug_field = target_data['slug']     # e.g., "aluminum-oxidation" ← USE THIS
    name_field = target_data['name']     # e.g., "Aluminum Oxidation"
    category = target_data['category']   # e.g., "oxidation"
    subcategory = target_data.get('subcategory', '')  # e.g., "non-ferrous"
    
    # Step 3: Build URL using ACTUAL SLUG (not abbreviated ID)
    if content_type == 'contaminants':
        url = f'/contaminants/{category}/{subcategory}/{slug_field}'
    elif content_type == 'materials':
        url = f'/materials/{slug_field}'
    elif content_type == 'compounds':
        url = f'/compounds/{slug_field}'
    elif content_type == 'settings':
        url = f'/settings/{slug_field}'
    
    # Step 4: Build image path using ACTUAL SLUG
    if content_type == 'contaminants':
        image = f'/images/contaminants/{category}/{subcategory}/{slug_field}.jpg'
    elif content_type == 'materials':
        image = f'/images/materials/{slug_field}-hero.jpg'
    elif content_type == 'compounds':
        image = f'/images/compounds/{slug_field}.jpg'
    
    # Step 5: Return link entry with actual slug
    return {
        'id': id_field,
        'slug': slug_field,  # ← REQUIRED: Include explicit slug
        'title': name_field,
        'url': url,          # ← Built from actual slug
        'image': image,      # ← Built from actual slug
        # ... metadata fields
    }
```

### Complete Link Structure (Schema 5.0.0)

All domain linkage entries MUST:
1. ✅ Be at **top level** (no nested `entries` array)
2. ✅ Include all required fields
3. ✅ Use actual slug from target file

```yaml
# Schema 5.0.0 Flattened Structure
relationships:
  
  related_contaminants:
  - id: {id-from-target-file}              # ID field from referenced file
    slug: {slug-from-target-file}          # REQUIRED: Explicit slug field
    title: {name-from-target-file}         # Name/title from referenced file
    url: /{content-type}/{path}/{slug}     # URL built from actual slug
    image: /images/{content-type}/{path}/{slug}.{ext}  # Image path from actual slug
    frequency: common|occasional|rare      # Metadata (contaminants only)
    severity: minor|moderate|severe        # Metadata (contaminants only)
    typical_context: general|specific      # Metadata (contaminants only)

  related_materials:
  - id: {id-from-target-file}
    slug: {slug-from-target-file}          # REQUIRED: Explicit slug field
    title: {name-from-target-file}
    url: /materials/{slug}                 # URL built from actual slug
    image: /images/materials/{slug}-hero.jpg
    relevance: primary|secondary           # Metadata

  related_compounds:
  - id: {id-from-target-file}
    slug: {slug-from-target-file}          # REQUIRED: Explicit slug field
    title: {name-from-target-file}
    url: /compounds/{slug}                 # URL built from actual slug
    image: /images/compounds/{slug}.jpg
    exposure_risk: high|medium|low         # Metadata

  related_settings:
  - id: {id-from-target-file}
    slug: {slug-from-target-file}          # REQUIRED: Explicit slug field
    title: {name-from-target-file}
    url: /settings/{slug}                  # URL built from actual slug
    image: /images/settings/{slug}.jpg
```

---

## Validation Requirements

### Pre-Generation Validation

Before generating any frontmatter file:

1. ✅ Verify target filename follows naming pattern
2. ✅ Verify slug field matches base filename
3. ✅ Verify ID field follows type-specific pattern
4. ✅ Verify all referenced files exist
5. ✅ Verify all link URLs use actual slugs from target files

### Post-Generation Validation

After generating frontmatter files:

```bash
# Test 1: Pure YAML (no Python tags)
grep -r "!!python/" frontmatter/ && echo "❌ FAIL: Python tags found" || echo "✅ PASS"

# Test 2: Schema 5.0.0 compliance
python3 -m pytest tests/test_schema_5_normalization.py -v

# Test 3: Filename suffixes (Materials)
ls frontmatter/materials/*.yaml | grep -v -- "-laser-cleaning.yaml" && echo "❌ FAIL" || echo "✅ PASS"

# Test 3a: Settings filename compliance
python3 -m pytest tests/test_settings_filename_compliance.py -v

# Test 4: Slug consistency
for file in frontmatter/materials/*-laser-cleaning.yaml; do
  base=$(basename "$file" -laser-cleaning.yaml)
  slug=$(grep "^slug:" "$file" | cut -d' ' -f2)
  [ "$slug" = "$base" ] || echo "❌ Mismatch: $file"
done

# Test 5: Link URLs match slugs
python3 scripts/validate_relationships.py
```

---

## Examples

### Example 1: Material File (Schema 5.0.0)

```yaml
# File: aluminum-laser-cleaning.yaml

# Identity
id: aluminum-laser-cleaning      # ✅ Matches filename
slug: aluminum                   # ✅ Base filename without suffix
name: Aluminum
category: metal
subcategory: non-ferrous
schema_version: "5.0.0"          # ✅ Required for Schema 5.0.0

# Domain Linkages (Schema 5.0.0 - Flattened)
relationships:
  related_contaminants:
  - id: aluminum-oxidation-contamination           # From target file
    slug: aluminum-oxidation                       # From target file
    title: Aluminum Oxidation                      # From target file
    url: /contaminants/oxidation/non-ferrous/aluminum-oxidation  # Uses actual slug
    image: /images/contaminants/oxidation/non-ferrous/aluminum-oxidation.jpg
    frequency: common
    severity: moderate
    typical_context: general
```

### Example 2: Contaminant File (Schema 5.0.0)

```yaml
# File: aluminum-oxidation-contaminant.yaml

# Identity
id: aluminum-oxidation-contamination  # ✅ Ends with -contamination
slug: aluminum-oxidation              # ✅ Base filename without suffix
name: Aluminum Oxidation
category: oxidation
subcategory: non-ferrous
schema_version: "5.0.0"               # ✅ Required for Schema 5.0.0

# Domain Linkages (Schema 5.0.0 - Flattened)
relationships:
  related_materials:
  - id: aluminum-laser-cleaning        # From target file
    slug: aluminum                     # From target file
    title: Aluminum                    # From target file
    url: /materials/aluminum           # Uses actual slug
    image: /images/materials/aluminum-hero.jpg
    relevance: primary
```

---

## Common Mistakes to Avoid

### ❌ Mistake 0: Not Using SafeDumper (CRITICAL)
```python
# WRONG: Creates Python-specific tags
yaml.dump(data)  # Missing Dumper parameter

# Output contains:
!!python/object/apply:collections.OrderedDict

# CORRECT: Use SafeDumper
yaml.dump(data, Dumper=yaml.SafeDumper)
```
**Impact**: Breaks all JavaScript tests, causes parsing failures

### ❌ Mistake 1: Using Abbreviated IDs in URLs
```yaml
# Target file: adhesive-residue-tape-marks-contaminant.yaml
# Target slug: adhesive-residue-tape-marks

# WRONG:
url: /contaminants/.../adhesive-residue  # ❌ Abbreviated

# CORRECT:
url: /contaminants/.../adhesive-residue-tape-marks  # ✅ Full slug
```

### ❌ Mistake 2: Not Loading Target File
```python
# WRONG: Assuming/guessing the slug
url = f"/contaminants/.../{abbreviated_id}"

# CORRECT: Loading actual slug from file
target_data = load_yaml(target_file)
url = f"/contaminants/.../target_data['slug']}"
```

### ❌ Mistake 3: Missing Slug Field in Links
```yaml
# WRONG: No slug field
- id: aluminum-oxidation-contamination
  url: /contaminants/.../aluminum-oxidation

# CORRECT: Include explicit slug
- id: aluminum-oxidation-contamination
  slug: aluminum-oxidation  # ← Required for validation
  url: /contaminants/.../aluminum-oxidation
```

### ❌ Mistake 4: Filename/Slug Mismatch
```yaml
# Filename: aluminum-oxidation-contaminant.yaml
slug: aluminum-oxide  # ❌ WRONG - doesn't match base filename

# CORRECT:
slug: aluminum-oxidation  # ✅ Matches base filename
```

---

## Implementation Checklist

When implementing the frontmatter generator:

### Phase 1: YAML Serialization (CRITICAL)
- [x] ✅ **Use `yaml.SafeDumper`** - Prevents Python tags
- [x] Set `default_flow_style=False` for readable output
- [x] Set `sort_keys=False` to preserve field order
- [x] Set `allow_unicode=True` for international characters
- [ ] Verify no `!!python/` tags in output

### Phase 2: Schema 5.0.0 Structure
- [x] ✅ Use **flattened relationships** (no nested `entries`)
- [ ] Set `schema_version: "5.0.0"` in all files
- [ ] Support all 8 linkage types
- [ ] Run Schema 5.0.0 compliance tests

### Phase 3: File Structure
- [x] ✅ Generate filenames with correct type suffixes
- [ ] Set `id` field according to type-specific patterns
- [ ] Set `slug` field to match base filename
- [ ] Verify filename/slug consistency

### Phase 4: Link Generation
- [ ] Create function to load target file and extract slug
- [ ] Build URLs using actual slug from target file
- [ ] Include explicit `slug` field in all link entries
- [ ] Build image paths using actual slug

### Phase 5: Validation
- [ ] Validate no Python tags (`grep -r "!!python/"`)
- [ ] Run Schema 5.0.0 tests (21 tests)
- [ ] Validate filename patterns
- [ ] Validate id/slug consistency
- [ ] Validate all link URLs match target slugs

### Phase 6: Testing
- [ ] Generate sample files
- [ ] Run all validation scripts
- [ ] Verify links in dev server
- [ ] Check 404 errors are eliminated

---

## Reference Mapping

### Current State (Partial Compliance)
- Materials: ✅ 153/153 files (100%) with `-laser-cleaning.yaml` suffix
- Contaminants: ✅ 98/98 files (100%) with `-contaminant.yaml` suffix
- Compounds: ✅ 20/20 files (100%) with `-compound.yaml` suffix
- Settings: ❌ **0/161 files (0%)** with `-settings.yaml` suffix **CRITICAL ISSUE**

### Required State (Links Need Regeneration ❌)
- All `relationships` URLs must use actual slugs from target files
- All link entries must include explicit `slug` field
- All image paths must use actual slugs from target files

---

## Summary

**CRITICAL REQUIREMENTS** (Priority Order):

1. **YAML Serialization**: MUST use `yaml.SafeDumper` (no Python tags)
2. **Schema Version**: Set `schema_version: "5.0.0"` in all files
3. **Domain Linkages**: Use flattened structure (no nested `entries`)
4. **Filename**: `{name}-{type}.yaml` with correct type suffix
5. **ID Field**: Follow type-specific pattern (see ID Field Requirements)
6. **Slug Field**: Match base filename (without type suffix)
7. **Link URLs**: MUST use actual slug from target file (not abbreviated)
8. **Link Slug Field**: MUST include explicit slug in all link entries
9. **Link Generation**: MUST load target file to get actual slug value

**NEVER**:
- ❌ Use `yaml.dump()` without `Dumper=yaml.SafeDumper`
- ❌ Create nested linkages structure (old Schema 4.x)
- ❌ Include Python-specific tags (`!!python/...`)
- ❌ Use abbreviated IDs in URLs
- ❌ Guess or assume slug values
- ❌ Build URLs without loading target file
- ❌ Omit slug field from link entries

**ALWAYS**:
- ✅ Use `yaml.SafeDumper` parameter in yaml.dump()
- ✅ Use flattened relationships (Schema 5.0.0)
- ✅ Set `schema_version: "5.0.0"`
- ✅ Load target file to get actual slug
- ✅ Use exact slug value in URLs
- ✅ Include explicit slug field in links
- ✅ Validate URLs match actual slugs
- ✅ Run Schema 5.0.0 compliance tests

**IMPLEMENTATION STATUS**:
- ✅ SafeDumper: Implemented in `export/core/universal_exporter.py`
- ⚠️ Filename suffixes: 271/432 files comply (62.7%)
  - ✅ Materials: 153/153 (100%)
  - ✅ Contaminants: 98/98 (100%)
  - ✅ Compounds: 20/20 (100%)
  - ❌ **Settings: 0/161 (0%)** ← CRITICAL ISSUE
- ✅ Schema 5.0.0: Flattened structure implemented
- ⚠️ Link URLs: Verification needed

**REFERENCES**:
- Complete formatting guide: `FRONTMATTER_FORMATTING_GUIDE.md`
- Structure specification: `docs/FRONTMATTER_STRUCTURE_SPECIFICATION.md`
- Schema 5.0.0 details: `docs/SCHEMA_5_0_NORMALIZATION_COMPLETE.md`
- Normalization script: `scripts/normalize_frontmatter_structure.py`
- Test suite: `tests/test_schema_5_normalization.py` (21 tests)
- SafeDumper implementation: `docs/proposals/FORMATTING_GUIDE_COMPLIANCE_DEC17_2025.md`
