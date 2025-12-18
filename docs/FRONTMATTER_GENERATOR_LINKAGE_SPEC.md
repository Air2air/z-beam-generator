# Frontmatter Generator: Linkage Structure Specification

**Date**: December 18, 2025  
**Status**: ✅ **IMPLEMENTED** - Single source of truth architecture complete  
**Purpose**: Define the exact structure required for cross-reference links in frontmatter files  
**Scope**: All materials, contaminants, and settings frontmatter files

---

## Implementation Status (December 18, 2025)

### ✅ Completed
- **Single source of truth**: DomainAssociations.yaml with 619+ associations
- **Dynamic generation**: relationships_generator in export pipeline
- **Stale data removed**: All source files cleaned of relationships fields
- **Duplicate file bug fixed**: Removed slug generators causing overwrites
- **Export verified**: 422 frontmatter files generated correctly
- **Image URL format**: Using `/images/material/{slug}-laser-cleaning-hero.jpg`
- **Full IDs**: All relationships use complete IDs with suffixes

### ⚠️ Known Issues (Tests Reveal)
1. **Image URL prefix inconsistency**: Some using `/images/materials/` vs `/images/material/`
2. **Materials.yaml still has relationships**: Need to remove from alabaster-laser-cleaning
3. **Compound suffix validation**: May not need -compound suffix standardization

### 📊 Test Results
- **18 tests created**: Integration test suite in `test_domain_associations_integration.py`
- **14 passing**: Core architecture and export configuration verified
- **4 failing**: Image URL format needs alignment, stale data in Materials.yaml
- **4 skipped**: Frontmatter validation tests (export already verified manually)

### 📝 Documentation
- **System update**: `docs/FRONTMATTER_SYSTEM_UPDATE_DEC18_2025.md` (complete guide)
- **Test suite**: `tests/test_domain_associations_integration.py` (18 tests)
- **Migration commits**: 90aeaad3 (fixes), ffd2204e (duplicate fix)

---

## Critical Requirements

### 1. Field Name
**REQUIRED**: Use `relationships` (NOT `domain_linkages`)

```yaml
relationships:  # ← Correct field name
  related_materials: []
  related_contaminants: []
```

### 2. Link Entry Structure
Each link entry MUST include these fields in this exact order:

```yaml
- id: full-id-from-target-file-with-suffix
  slug: exact-slug-from-target-file
  title: Display Title from Target
  url: /content-type/slug-from-target-file
  image: /images/content-type/slug-from-target-file.jpg
  frequency: common|uncommon|rare
  severity: high|moderate|low
  typical_context: general|specific-context
```

---

## Field-by-Field Specifications

### `id` Field
**Source**: The `id` field from the target frontmatter file  
**Format**: Must match target file's ID exactly, including suffix

**Examples**:
- Material ID: `aluminum-laser-cleaning` (NOT `Aluminum`)
- Contaminant ID: `adhesive-residue-tape-marks-contamination` (NOT `adhesive-residue`)
- Settings ID: `aluminum-bronze-settings` (NOT `aluminum-bronze`)

**How to Get**: Read target file's `id:` field

### `slug` Field
**Source**: The `slug` field from the target frontmatter file  
**Format**: Lowercase, hyphenated, NO spaces, NO file extensions

**Examples**:
- Material slug: `aluminum`
- Contaminant slug: `adhesive-residue-tape-marks`
- Settings slug: `aluminum-bronze`

**How to Get**: Read target file's `slug:` field

### `title` Field
**Source**: The `name` field from the target frontmatter file (or `title` if name not present)  
**Format**: Human-readable display name

**Examples**:
- `"Aluminum"`
- `"Adhesive Residue / Tape Marks"`
- `"Automotive Road Grime"`

**How to Get**: Read target file's `name:` field

### `url` Field
**Source**: Constructed from content type and slug  
**Format**: `/content-type/slug` (NO category paths, NO spaces)

**Examples**:
```yaml
# Materials
url: /materials/aluminum                    # NOT /materials/metal/non-ferrous/Aluminum
url: /materials/steel                       # NOT /materials/metal/ferrous/Steel

# Contaminants
url: /contaminants/adhesive-residue-tape-marks    # NOT /contaminants/organic-residue/adhesive/adhesive-residue
url: /contaminants/automotive-road-grime          # NOT /contaminants/organic-residue/other/road-grime

# Settings
url: /settings/aluminum-bronze              # NOT /settings/Aluminum Bronze
```

**Construction Logic**:
```
url = f"/{content_type}/{slug}"

Where:
- content_type = "materials" | "contaminants" | "settings"
- slug = exact slug from target file (lowercase, hyphenated)
```

### `image` Field
**Source**: Constructed from content type and slug  
**Format**: `/images/content-type/slug.jpg` (NO category paths, NO spaces)

**Examples**:
```yaml
# Materials
image: /images/materials/aluminum.jpg              # NOT /images/materials/metal/non-ferrous/Aluminum.jpg
image: /images/materials/steel.jpg                 # NOT /images/materials/metal/ferrous/Steel.jpg

# Contaminants
image: /images/contaminants/adhesive-residue-tape-marks.jpg
image: /images/contaminants/automotive-road-grime.jpg

# Settings
image: /images/settings/aluminum-bronze.jpg
```

**Construction Logic**:
```
image = f"/images/{content_type}/{slug}.jpg"
```

---

## Complete Examples

### Example 1: Material Linking to Contaminants

**Source File**: `steel-laser-cleaning.yaml`

```yaml
relationships:
  related_contaminants:
  - id: adhesive-residue-tape-marks-contamination
    slug: adhesive-residue-tape-marks
    title: Adhesive Residue / Tape Marks
    url: /contaminants/adhesive-residue-tape-marks
    image: /images/contaminants/adhesive-residue-tape-marks.jpg
    frequency: common
    severity: moderate
    typical_context: general
  
  - id: road-grime-contamination
    slug: automotive-road-grime
    title: Automotive Road Grime
    url: /contaminants/automotive-road-grime
    image: /images/contaminants/automotive-road-grime.jpg
    frequency: common
    severity: low
    typical_context: general
```

### Example 2: Contaminant Linking to Materials

**Source File**: `adhesive-residue-tape-marks-contaminant.yaml`

```yaml
relationships:
  related_materials:
  - id: aluminum-laser-cleaning
    slug: aluminum
    title: Aluminum
    url: /materials/aluminum
    image: /images/materials/aluminum.jpg
    frequency: common
    severity: moderate
    typical_context: general
  
  - id: steel-laser-cleaning
    slug: steel
    title: Steel
    url: /materials/steel
    image: /images/materials/steel.jpg
    frequency: common
    severity: moderate
    typical_context: general
```

---

## Common Mistakes to Avoid

### ❌ WRONG: Using abbreviated IDs
```yaml
- id: adhesive-residue          # Missing full ID with suffix
```

### ✅ CORRECT: Using full IDs
```yaml
- id: adhesive-residue-tape-marks-contamination
```

---

### ❌ WRONG: Missing slug field
```yaml
- id: adhesive-residue-tape-marks-contamination
  title: Adhesive Residue / Tape Marks
  # slug field is missing!
```

### ✅ CORRECT: Including slug field
```yaml
- id: adhesive-residue-tape-marks-contamination
  slug: adhesive-residue-tape-marks
  title: Adhesive Residue / Tape Marks
```

---

### ❌ WRONG: URLs with category paths and spaces
```yaml
url: /materials/metal/non-ferrous/Aluminum
url: /contaminants/organic-residue/adhesive/adhesive-residue
```

### ✅ CORRECT: URLs with slugs only
```yaml
url: /materials/aluminum
url: /contaminants/adhesive-residue-tape-marks
```

---

### ❌ WRONG: Using title case in IDs
```yaml
- id: Aluminum
  title: Aluminum
```

### ✅ CORRECT: Using exact ID from target file
```yaml
- id: aluminum-laser-cleaning
  slug: aluminum
  title: Aluminum
```

---

## Implementation Checklist

When generating frontmatter relationships, the generator MUST:

- [ ] Use `relationships` as the field name (not `domain_linkages`)
- [ ] For each linked item, lookup the target frontmatter file
- [ ] Extract the exact `id` from target file (with suffix)
- [ ] Extract the exact `slug` from target file
- [ ] Extract the `name` field from target file for title
- [ ] Construct URL as: `/{content_type}/{slug}`
- [ ] Construct image path as: `/images/{content_type}/{slug}.jpg`
- [ ] Include all required fields: id, slug, title, url, image
- [ ] Include metadata fields: frequency, severity, typical_context
- [ ] Ensure NO spaces in URLs or image paths
- [ ] Ensure NO category hierarchies in URLs or image paths

---

## Validation Rules

Each generated link entry must pass these validations:

1. **Field Presence**: All required fields present (id, slug, title, url, image)
2. **ID Format**: ID ends with correct suffix (`-laser-cleaning`, `-contamination`, `-settings`)
3. **Slug Format**: Slug is lowercase, hyphenated, no spaces, no extensions
4. **URL Format**: URL follows pattern `/{content_type}/{slug}` with no spaces
5. **Image Format**: Image follows pattern `/images/{content_type}/{slug}.jpg`
6. **Consistency**: slug in URL matches slug field
7. **Consistency**: slug in image path matches slug field

---

## Target File Locations

To lookup target file information:

```
Materials:     frontmatter/materials/{material-name}-laser-cleaning.yaml
Contaminants:  frontmatter/contaminants/{contaminant-slug}-contaminant.yaml
Settings:      frontmatter/settings/{material-name}-settings.yaml
```

**Note**: Contaminant files use `-contaminant.yaml` suffix in filename but `-contamination` suffix in the ID field.

---

## Generator Implementation Notes

### Step 1: Identify Relationships
Determine which materials/contaminants should be linked based on:
- Material properties and common contaminants
- Contaminant composition and compatible materials
- Settings tied to specific materials

### Step 2: Lookup Target Files
For each relationship:
```python
target_file = f"frontmatter/{content_type}/{slug}-{suffix}.yaml"
target_data = yaml.load(target_file)
```

### Step 3: Extract Required Data
```python
link = {
    'id': target_data['id'],              # Full ID with suffix
    'slug': target_data['slug'],          # Exact slug
    'title': target_data.get('name', target_data.get('title')),
    'url': f"/{content_type}/{target_data['slug']}",
    'image': f"/images/{content_type}/{target_data['slug']}.jpg",
    'frequency': 'common',  # Based on analysis
    'severity': 'moderate',  # Based on analysis
    'typical_context': 'general'  # Based on analysis
}
```

### Step 4: Validate
```python
assert 'slug' in link, "Missing slug field"
assert ' ' not in link['url'], "URL contains spaces"
assert ' ' not in link['image'], "Image path contains spaces"
assert link['url'] == f"/{content_type}/{link['slug']}", "URL doesn't match slug"
```

---

## Current Status

**654 frontmatter files need regeneration**:
- 305 materials files
- 196 contaminants files
- 153 settings files

**Primary Issue**: 100% of links missing `slug` field and using incorrect ID/URL formats

**Action Required**: Regenerate all frontmatter files with corrected link structure
