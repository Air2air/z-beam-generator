# Frontmatter Link Correction Requirements

**Date**: December 18, 2025  
**Status**: Critical - All cross-reference links need correction  
**Scope**: 424 frontmatter files

---

## Issues Summary

The frontmatter files have **3 critical link structure issues** that cause 404 errors:

### Issue 1: Abbreviated Link IDs
❌ **Current**: Links use custom abbreviated IDs  
✅ **Required**: Use full ID from target file

```yaml
# ❌ CURRENT (WRONG):
relationships:
  related_contaminants:
  - id: adhesive-residue  # Abbreviated custom ID

# ✅ REQUIRED (CORRECT):
relationships:
  related_contaminants:
  - id: adhesive-residue-tape-marks-contamination  # Full ID from target file
```

### Issue 2: Missing Slug Field
❌ **Current**: Links don't include explicit slug field  
✅ **Required**: Add slug field from target file for validation

```yaml
# ❌ CURRENT (WRONG):
- id: adhesive-residue
  title: Adhesive Residue / Tape Marks
  url: /contaminants/.../adhesive-residue

# ✅ REQUIRED (CORRECT):
- id: adhesive-residue-tape-marks-contamination
  slug: adhesive-residue-tape-marks  # ← ADD THIS
  title: Adhesive Residue / Tape Marks
  url: /contaminants/.../adhesive-residue-tape-marks
```

### Issue 3: Wrong URLs (Don't Match Slugs)
❌ **Current**: URLs use abbreviated versions that don't match actual file slugs  
✅ **Required**: URLs must use exact slug from target file

```yaml
# Target file: adhesive-residue-tape-marks-contaminant.yaml
# Target slug: adhesive-residue-tape-marks

# ❌ CURRENT (WRONG):
url: /contaminants/organic-residue/adhesive/adhesive-residue
image: /images/contaminants/organic-residue/adhesive/adhesive-residue.jpg

# ✅ REQUIRED (CORRECT):
url: /contaminants/organic-residue/adhesive/adhesive-residue-tape-marks
image: /images/contaminants/organic-residue/adhesive/adhesive-residue-tape-marks.jpg
```

---

## Real-World Examples

### Example 1: Material → Contaminant Links

**Source File**: `aluminum-laser-cleaning.yaml`

**Current (Wrong)**:
```yaml
relationships:
  related_contaminants:
  - id: adhesive-residue
    title: Adhesive Residue / Tape Marks
    url: /contaminants/organic-residue/adhesive/adhesive-residue
    image: /images/contaminants/organic-residue/adhesive/adhesive-residue.jpg
```

**Target File**: `adhesive-residue-tape-marks-contaminant.yaml`
```yaml
id: adhesive-residue-tape-marks-contamination
slug: adhesive-residue-tape-marks
name: Adhesive Residue / Tape Marks
```

**Required (Correct)**:
```yaml
relationships:
  related_contaminants:
  - id: adhesive-residue-tape-marks-contamination  # ← Use full ID from target
    slug: adhesive-residue-tape-marks              # ← Add slug from target
    title: Adhesive Residue / Tape Marks
    url: /contaminants/organic-residue/adhesive/adhesive-residue-tape-marks  # ← Use slug
    image: /images/contaminants/organic-residue/adhesive/adhesive-residue-tape-marks.jpg
```

### Example 2: Contaminant → Material Links

**Source File**: `aluminum-oxidation-contaminant.yaml`

**Current (Wrong)**:
```yaml
relationships:
  related_materials:
  - id: aluminum
    title: Aluminum
    url: /materials/aluminum
```

**Target File**: `aluminum-laser-cleaning.yaml`
```yaml
id: aluminum-laser-cleaning
slug: aluminum
name: Aluminum
```

**Required (Correct)**:
```yaml
relationships:
  related_materials:
  - id: aluminum-laser-cleaning  # ← Use full ID from target
    slug: aluminum               # ← Add slug from target
    title: Aluminum
    url: /materials/aluminum     # ← Already correct (slug matches)
    image: /images/materials/aluminum-hero.jpg
```

---

## Link Generation Algorithm

**REQUIRED PROCESS** for all link entries:

```python
def generate_link_entry(target_filename, content_type, category=None, subcategory=None):
    """
    Generate a correct link entry by loading target file.
    
    CRITICAL: Must load target file to get actual ID and slug.
    """
    # Step 1: Load target file
    file_path = f"frontmatter/{content_type}/{target_filename}"
    target_data = load_yaml(file_path)
    
    # Step 2: Extract fields from target file
    target_id = target_data['id']        # Full ID (e.g., "adhesive-residue-tape-marks-contamination")
    target_slug = target_data['slug']    # Actual slug (e.g., "adhesive-residue-tape-marks")
    target_name = target_data['name']    # Display name
    
    # Step 3: Build URL using actual slug
    if content_type == 'contaminants':
        target_category = target_data['category']
        target_subcategory = target_data.get('subcategory', '')
        url = f'/contaminants/{target_category}/{target_subcategory}/{target_slug}'
        image = f'/images/contaminants/{target_category}/{target_subcategory}/{target_slug}.jpg'
    elif content_type == 'materials':
        url = f'/materials/{target_slug}'
        image = f'/images/materials/{target_slug}-hero.jpg'
    elif content_type == 'compounds':
        url = f'/compounds/{target_slug}'
        image = f'/images/compounds/{target_slug}.jpg'
    elif content_type == 'settings':
        url = f'/settings/{target_slug}'
        image = f'/images/settings/{target_slug}.jpg'
    
    # Step 4: Return complete link entry
    return {
        'id': target_id,      # ← Full ID from target file
        'slug': target_slug,  # ← Actual slug from target file
        'title': target_name,
        'url': url,           # ← Built from actual slug
        'image': image,       # ← Built from actual slug
        # ... metadata fields
    }
```

---

## Validation Checklist

For each link entry, verify:

- [ ] **ID field matches target file ID** (not abbreviated)
  - Materials: Should end with `-laser-cleaning`
  - Contaminants: Should end with `-contamination`
  - Compounds: Should end with `-compound`
  - Settings: Should be Title Case name

- [ ] **Slug field present and matches target file slug**
  - Must be explicit in link entry
  - Must match target file's slug field exactly

- [ ] **URL ends with target file slug**
  - Not an abbreviated version
  - Matches slug field in link entry
  - Matches slug field in target file

- [ ] **Image path uses target file slug**
  - Consistent with URL slug
  - Not abbreviated

---

## Scope of Changes

### Files Affected: All 424 frontmatter files
- 153 materials
- 98 contaminants  
- 20 compounds
- 153 settings

### Link Types Affected:
- `related_materials` - Links to material files
- `related_contaminants` - Links to contaminant files
- `related_compounds` - Links to compound files
- `related_settings` - Links to settings files

### Fields to Update in Each Link:
1. `id` - Use full ID from target file
2. `slug` - ADD this field with target file's slug
3. `url` - Update to use target file's slug
4. `image` - Update to use target file's slug

---

## Common Patterns to Fix

### Pattern 1: Abbreviated Contaminant Links
```yaml
# WRONG: Many materials link to contaminants with abbreviated IDs
- id: algae-growth                    # ❌ Abbreviated
  url: /contaminants/.../algae-growth # ❌ Wrong slug

# Target: algae-and-lichen-growth-contaminant.yaml
# ID: algae-growth-contamination
# Slug: algae-and-lichen-growth

# CORRECT:
- id: algae-growth-contamination                  # ✅ Full ID
  slug: algae-and-lichen-growth                   # ✅ Added slug
  url: /contaminants/.../algae-and-lichen-growth  # ✅ Correct slug
```

### Pattern 2: Abbreviated Material Links  
```yaml
# WRONG: Some contaminants link to materials with abbreviated IDs
- id: aluminum                # ❌ Abbreviated
  url: /materials/aluminum    # ✅ URL happens to be correct

# Target: aluminum-laser-cleaning.yaml
# ID: aluminum-laser-cleaning
# Slug: aluminum

# CORRECT:
- id: aluminum-laser-cleaning  # ✅ Full ID
  slug: aluminum               # ✅ Added slug
  url: /materials/aluminum     # ✅ Correct (slug matches)
```

### Pattern 3: Missing Slug Fields (All Links)
```yaml
# WRONG: All links missing explicit slug field
- id: some-id
  title: Some Title
  url: /path/to/something
  # ❌ No slug field

# CORRECT: Add slug field for validation
- id: full-id-from-target
  slug: actual-slug-from-target  # ✅ Added
  title: Some Title
  url: /path/to/actual-slug-from-target
```

---

## Testing & Verification

### Test 1: Check Target Files Exist
```bash
# Verify all link targets resolve to actual files
for material_file in frontmatter/materials/*-laser-cleaning.yaml; do
  echo "Checking links in $(basename $material_file)..."
  # Extract contaminant IDs and verify files exist
  # This needs YAML parsing
done
```

### Test 2: Verify Slug Consistency
```bash
# For each link, verify:
# 1. Target file exists
# 2. Link ID matches target file's ID
# 3. Link slug matches target file's slug  
# 4. URL ends with target file's slug

python3 scripts/validate_link_consistency.py
```

### Test 3: Manual Spot Check
```bash
# Pick 5 random materials and verify their contaminant links
for file in aluminum copper steel titanium brass; do
  echo "=== $file ==="
  # Get first contaminant link
  grep -A 5 "related_contaminants:" frontmatter/materials/${file}-laser-cleaning.yaml | head -10
  echo ""
done
```

---

## Implementation Priority

### Phase 1: Create Lookup Utility (1 hour)
Build function to load target file and extract ID/slug fields

### Phase 2: Update Link Generation (2 hours)  
Modify generator to use lookup utility for all link entries

### Phase 3: Regenerate All Links (automated)
Run generator to update all 424 files with correct links

### Phase 4: Validation (30 minutes)
Run validation scripts to confirm all links correct

---

## Summary

**What's Working:**
- ✅ Filenames have correct suffixes
- ✅ ID fields follow correct patterns
- ✅ Slug fields match base filenames
- ✅ "relationships" key name is correct

**What Needs Fixing:**
- ❌ Link IDs are abbreviated (should be full IDs from target files)
- ❌ Link entries missing explicit slug field
- ❌ Link URLs don't match actual target file slugs
- ❌ Link image paths don't match actual target file slugs

**Critical Rule:**  
Every link entry MUST load the target file and use its actual `id` and `slug` fields. Never abbreviate or assume these values.

**Files Affected:** All 424 frontmatter files need their `relationships` sections regenerated.
