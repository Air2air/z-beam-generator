# Proposal: Strip Parentheses from File Names

## Executive Summary

**Problem**: 3 materials have parentheses in their names, creating filenames like `acrylic-(pmma)-settings.yaml` instead of cleaner `acrylic-pmma-settings.yaml`.

**Solution**: Use existing `slug_utils.py` infrastructure to strip parentheses while preserving the abbreviation information.

**Impact**: 6 files renamed (3 materials × 2 file types)

---

## Current State

### Materials with Parentheses
1. **Acrylic (PMMA)** → `acrylic-(pmma)-laser-cleaning.yaml`, `acrylic-(pmma)-settings.yaml`
2. **Silicon Carbide (SiC)** → `silicon-carbide-(sic)-laser-cleaning.yaml`, `silicon-carbide-(sic)-settings.yaml`
3. **Titanium Alloy (Ti-6Al-4V)** → `titanium-alloy-(ti-6al-4v)-laser-cleaning.yaml`, `titanium-alloy-(ti-6al-4v)-settings.yaml`

### Files Affected
```
# Generator frontmatter
frontmatter/materials/acrylic-(pmma)-laser-cleaning.yaml
frontmatter/settings/acrylic-(pmma)-settings.yaml
frontmatter/materials/silicon-carbide-(sic)-laser-cleaning.yaml
frontmatter/settings/silicon-carbide-(sic)-settings.yaml
frontmatter/materials/titanium-alloy-(ti-6al-4v)-laser-cleaning.yaml
frontmatter/settings/titanium-alloy-(ti-6al-4v)-settings.yaml

# Next.js production (after deploy)
z-beam/frontmatter/materials/acrylic-(pmma)-laser-cleaning.yaml
z-beam/frontmatter/settings/acrylic-(pmma)-settings.yaml
... (same 6 files)
```

---

## Proposed Solution

### Option 1: Use Existing `slug_utils.py` (RECOMMENDED)

**File**: `shared/utils/core/slug_utils.py`

**Already Implemented**: The `create_material_slug()` function already strips parentheses correctly:

```python
def create_material_slug(material_name: str) -> str:
    """
    Create a clean, consistent slug from a material name.
    
    Examples:
        >>> create_material_slug("Acrylic (PMMA)")
        'acrylic-pmma'
        >>> create_material_slug("Silicon Carbide (SiC)")
        'silicon-carbide-sic'
        >>> create_material_slug("Titanium Alloy (Ti-6Al-4V)")
        'titanium-alloy-ti-6al-4v'
    """
    slug = material_name.lower()
    
    # Extract parentheses content and append as part of slug
    slug = re.sub(r"\s*\(([^)]+)\)\s*", r" \1 ", slug)
    
    # Replace non-alphanumeric with spaces, then hyphens
    slug = re.sub(r"[^a-z0-9]+", " ", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    
    return slug.strip("-")
```

**Current Behavior**:
- ✅ Strips parentheses
- ✅ Preserves abbreviation content
- ✅ Converts to clean slug format

**Expected Output**:
| Material Name | Current Filename | Proposed Filename |
|---------------|------------------|-------------------|
| Acrylic (PMMA) | `acrylic-(pmma)-laser-cleaning.yaml` | `acrylic-pmma-laser-cleaning.yaml` |
| Silicon Carbide (SiC) | `silicon-carbide-(sic)-laser-cleaning.yaml` | `silicon-carbide-sic-laser-cleaning.yaml` |
| Titanium Alloy (Ti-6Al-4V) | `titanium-alloy-(ti-6al-4v)-laser-cleaning.yaml` | `titanium-alloy-ti-6al-4v-laser-cleaning.yaml` |

---

## Implementation Plan

### Step 1: Update `trivial_exporter.py` to Use `slug_utils.py`

**Current Code** (lines 1045-1048):
```python
# Simple slug generation (keeps parentheses)
material_slug = name.lower().replace(' ', '-')
```

**Proposed Change**:
```python
from shared.utils.core.slug_utils import create_material_slug

# Use existing slug utility (strips parentheses)
material_slug = create_material_slug(name)
```

**Files to Update**:
1. `export/core/trivial_exporter.py` - Import and use `create_material_slug()`
2. Any other exporters using manual slug generation

### Step 2: Rename Existing Files

**Script**: `scripts/rename_parentheses_files.py`

```python
#!/usr/bin/env python3
"""
Rename files with parentheses to clean slug format.

Usage:
    python3 scripts/rename_parentheses_files.py --dry-run  # Preview
    python3 scripts/rename_parentheses_files.py            # Execute
"""

import os
from pathlib import Path
from shared.utils.core.slug_utils import create_material_slug

materials_with_parens = {
    "Acrylic (PMMA)": "Acrylic (PMMA)",
    "Silicon Carbide (SiC)": "Silicon Carbide (SiC)",
    "Titanium Alloy (Ti-6Al-4V)": "Titanium Alloy (Ti-6Al-4V)"
}

def rename_files(dry_run=True):
    """Rename files with parentheses to clean format."""
    
    base_dirs = [
        Path("/Users/todddunning/Desktop/Z-Beam/z-beam-generator/frontmatter"),
        Path("/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter")
    ]
    
    rename_map = []
    
    for base_dir in base_dirs:
        if not base_dir.exists():
            continue
            
        # Find all files with parentheses
        for old_file in base_dir.rglob("*(*)*"):
            if old_file.is_file():
                old_name = old_file.name
                
                # Generate clean filename
                for material_name in materials_with_parens.keys():
                    clean_slug = create_material_slug(material_name)
                    
                    # Check if this file belongs to this material
                    if clean_slug.replace('-', '-(').replace(' ', '') in old_name:
                        # Generate new filename
                        new_name = old_name.replace(
                            f"({material_name.split('(')[1].split(')')[0].lower()})",
                            material_name.split('(')[1].split(')')[0].lower().replace(' ', '-')
                        )
                        
                        new_file = old_file.parent / new_name
                        rename_map.append((old_file, new_file))
                        break
    
    # Execute or preview renames
    for old_path, new_path in rename_map:
        if dry_run:
            print(f"Would rename:")
            print(f"  {old_path.name}")
            print(f"  → {new_path.name}")
        else:
            old_path.rename(new_path)
            print(f"✅ Renamed: {old_path.name} → {new_path.name}")
    
    return len(rename_map)

if __name__ == "__main__":
    import sys
    dry_run = "--dry-run" in sys.argv
    
    count = rename_files(dry_run=dry_run)
    
    if dry_run:
        print(f"\n📋 Would rename {count} files")
        print("Run without --dry-run to execute")
    else:
        print(f"\n✅ Renamed {count} files")
```

### Step 3: Regenerate and Deploy

After updating the exporter:

```bash
# Regenerate frontmatter with clean slugs
python3 run.py --deploy

# Verify clean filenames
find frontmatter -name "*(*)*" | wc -l  # Should be 0
```

---

## Testing Plan

### Unit Tests

```python
# tests/test_slug_parentheses_strip.py

def test_slug_strips_parentheses():
    """Test that slugs don't contain parentheses."""
    from shared.utils.core.slug_utils import create_material_slug
    
    test_cases = {
        "Acrylic (PMMA)": "acrylic-pmma",
        "Silicon Carbide (SiC)": "silicon-carbide-sic",
        "Titanium Alloy (Ti-6Al-4V)": "titanium-alloy-ti-6al-4v",
        "Stainless Steel": "stainless-steel"  # Control case
    }
    
    for material, expected in test_cases.items():
        slug = create_material_slug(material)
        assert slug == expected
        assert '(' not in slug
        assert ')' not in slug

def test_slug_validation_rejects_parentheses():
    """Test that slug validation rejects parentheses."""
    from shared.utils.core.slug_utils import validate_slug
    
    invalid_slugs = [
        "acrylic-(pmma)",
        "silicon-carbide-(sic)",
        "titanium-alloy-(ti-6al-4v)"
    ]
    
    for slug in invalid_slugs:
        assert not validate_slug(slug)
    
    valid_slugs = [
        "acrylic-pmma",
        "silicon-carbide-sic",
        "titanium-alloy-ti-6al-4v"
    ]
    
    for slug in valid_slugs:
        assert validate_slug(slug)
```

### Integration Tests

```bash
# Verify no parentheses in generated files
python3 -c "
from export.core.trivial_exporter import TrivialFrontmatterExporter
exporter = TrivialFrontmatterExporter()

test_materials = ['Acrylic (PMMA)', 'Silicon Carbide (SiC)', 'Titanium Alloy (Ti-6Al-4V)']
for mat in test_materials:
    result = exporter.export_single(mat)
    filename = result['filename']
    assert '(' not in filename
    assert ')' not in filename
    print(f'✅ {mat} → {filename}')
"
```

---

## Migration Strategy

### Phase 1: Preparation (5 minutes)
1. ✅ Verify `slug_utils.py` works correctly (already exists)
2. ✅ Update `trivial_exporter.py` to import and use `create_material_slug()`
3. ✅ Run unit tests

### Phase 2: Rename Existing Files (2 minutes)
1. Run rename script in dry-run mode to preview
2. Execute rename script to update existing files
3. Verify 6 files renamed in generator frontmatter
4. Verify 6 files renamed in Next.js frontmatter

### Phase 3: Regenerate (2 minutes)
1. Run `python3 run.py --deploy`
2. Verify all 362 files regenerated with clean slugs
3. Check that no files with parentheses exist

### Phase 4: Verification (1 minute)
```bash
# Should return 0
find frontmatter -name "*(*)*" | wc -l
find /Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter -name "*(*)*" | wc -l

# Verify clean filenames exist
ls frontmatter/materials/acrylic-pmma-laser-cleaning.yaml
ls frontmatter/settings/silicon-carbide-sic-settings.yaml
ls frontmatter/materials/titanium-alloy-ti-6al-4v-laser-cleaning.yaml
```

---

## Benefits

### 1. **Cleaner URLs**
- Before: `/materials/plastic/acrylic-(pmma)`
- After: `/materials/plastic/acrylic-pmma`

### 2. **Better SEO**
- Parentheses in URLs are encoded as `%28` and `%29`
- Clean hyphens are more readable and SEO-friendly

### 3. **Consistent Naming**
- All 159 materials follow same slug pattern
- No special cases for materials with abbreviations

### 4. **Easier File Management**
- Shell scripts don't need to escape parentheses
- Simpler grep/find operations
- Better compatibility across systems

### 5. **Validation Ready**
- `validate_slug()` already rejects parentheses
- System will prevent future parentheses in slugs

---

## Risks & Mitigation

### Risk 1: Broken Links
**Impact**: Low - only 3 materials affected  
**Mitigation**: Set up redirects in Next.js

```javascript
// next.config.js
module.exports = {
  async redirects() {
    return [
      {
        source: '/materials/plastic/acrylic-(pmma)',
        destination: '/materials/plastic/acrylic-pmma',
        permanent: true
      },
      // ... (5 more redirects)
    ]
  }
}
```

### Risk 2: External References
**Impact**: Low - internal system only  
**Mitigation**: Check for hardcoded references in documentation

```bash
# Search for hardcoded old filenames
grep -r "acrylic-(pmma)" docs/
grep -r "silicon-carbide-(sic)" docs/
grep -r "titanium-alloy-(ti-6al-4v)" docs/
```

### Risk 3: Cached Data
**Impact**: Low - regeneration clears cache  
**Mitigation**: Full deploy regenerates everything from source

---

## Alternative Approaches

### Option 2: Keep Parentheses, Escape in URLs
**Pros**: No file renames needed  
**Cons**: Ugly URLs (`%28`, `%29`), inconsistent with other materials

### Option 3: Remove Abbreviations Entirely
**Example**: `Acrylic (PMMA)` → `acrylic`  
**Pros**: Shortest URLs  
**Cons**: Loses important technical information, creates ambiguity

### Option 4: Use Underscore Separator
**Example**: `acrylic_pmma-laser-cleaning.yaml`  
**Pros**: Visually distinct abbreviation  
**Cons**: Inconsistent with rest of system (all use hyphens)

---

## Recommendation

✅ **Use Option 1** (Implement existing `slug_utils.py`)

**Rationale**:
1. Infrastructure already exists and tested
2. Preserves abbreviation information
3. Creates clean, SEO-friendly URLs
4. Consistent with rest of system
5. Minimal implementation effort (5 lines of code)
6. Easy rollback (just revert exporter change)

**Estimated Time**: 10 minutes total
- 2 min: Update exporter
- 2 min: Rename existing files
- 2 min: Regenerate and deploy
- 2 min: Test and verify
- 2 min: Documentation

---

## Implementation Code

### Update `trivial_exporter.py`

```python
# At top of file
from shared.utils.core.slug_utils import create_material_slug

# Replace lines 1045-1048
def _generate_breadcrumb(self, material_data: Dict, slug: str) -> list:
    # ... existing code ...
    
    name = material_data.get('name', '')
    if name:
        # Use slug_utils for clean slug generation
        material_slug = create_material_slug(name)  # NEW
        
        if subcategory:
            final_href = f"/materials/{category.lower()}/{subcategory.lower()}/{material_slug}"
        else:
            final_href = f"/materials/{category.lower()}/{material_slug}"
        
        breadcrumb.append({
            "label": name,
            "href": final_href
        })
```

### Quick Rename Script (One-liner)

```bash
# Preview renames
for f in frontmatter/**/*\(*\)*.yaml; do 
    new=$(echo "$f" | sed 's/-(\([^)]*\))/-\1/g'); 
    echo "$f → $new"; 
done

# Execute renames (after verification)
for f in frontmatter/**/*\(*\)*.yaml; do 
    new=$(echo "$f" | sed 's/-(\([^)]*\))/-\1/g'); 
    mv "$f" "$new"; 
done
```

---

## Success Criteria

- [ ] No files with parentheses in frontmatter directories
- [ ] All 3 materials have clean slug filenames
- [ ] `validate_slug()` passes for all material slugs
- [ ] Full deployment completes successfully (362 files)
- [ ] Material pages accessible in Next.js
- [ ] Breadcrumb links work correctly
- [ ] No broken references in system

---

## Conclusion

The cleanest solution is to leverage the existing `slug_utils.py` infrastructure, which already handles parentheses stripping correctly. This requires minimal code changes (importing and using one function), provides immediate benefits (cleaner URLs, better SEO), and maintains consistency across the entire system.

**Ready to implement**: All necessary code already exists, just needs to be wired up in the exporter.

---

*Proposal Date: November 26, 2025*  
*Estimated Implementation Time: 10 minutes*  
*Materials Affected: 3*  
*Files to Rename: 6 (+ 6 in Next.js)*
