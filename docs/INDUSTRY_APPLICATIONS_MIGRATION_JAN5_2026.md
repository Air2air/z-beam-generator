# Industry Applications Migration - January 5, 2026

## Problem Statement

All 153 materials files have `operational.industry_applications` in the **old flat list format** instead of the required relationship section structure with `_section` metadata.

### Current (Incorrect) Structure
```yaml
operational:
  industry_applications:
  - Aerospace
  - Automotive
  - Construction
  - Electronics Manufacturing
```

### Required Structure
```yaml
operational:
  industry_applications:
    presentation: card
    items:
      - id: aerospace
      - id: automotive
      - id: construction
      - id: electronics-manufacturing
    _section:
      sectionTitle: Industry Applications
      sectionDescription: Industries and sectors where this material is commonly processed with laser cleaning
      icon: building
      order: 1
      variant: default
```

## Impact

**Error Message:**
```
Error: Missing required _section metadata for industry_applications. 
All sections MUST have explicit _section metadata with sectionTitle and sectionDescription.
```

**Affected Files:** All 153 materials in `frontmatter/materials/*.yaml`

## Migration Requirements

### 1. Transform Data Structure

**Old Format (Flat List):**
```yaml
operational:
  industry_applications:
  - Aerospace
  - Automotive
```

**New Format (Relationship Section):**
```yaml
operational:
  industry_applications:
    presentation: card
    items:
      - id: aerospace        # Lowercase, hyphenated slug
        name: Aerospace      # Display name (required)
      - id: automotive       # Generated from display name
        name: Automotive     # Display name (required)
    _section:
      sectionTitle: Industry Applications
      sectionDescription: Industries and sectors where this material is commonly processed with laser cleaning
      icon: building
      order: 1
      variant: default
```

### 2. ID Generation Rules

Convert display names to slugified IDs **AND preserve original name**:
- **Aerospace** → `id: aerospace`, `name: Aerospace`
- **Automotive** → `id: automotive`, `name: Automotive`
- **Electronics Manufacturing** → `id: electronics-manufacturing`, `name: Electronics Manufacturing`
- **Food and Beverage Processing** → `id: food-and-beverage-processing`, `name: Food and Beverage Processing`
- **Marine** → `id: marine`, `name: Marine`

**Algorithm:**
1. **name**: Keep original display text exactly as-is
2. **id**: Convert to lowercase → Replace spaces with hyphens → Remove special characters (keep only a-z, 0-9, hyphens) → Remove leading/trailing hyphens

### 3. Standard _section Metadata

**All materials must use identical _section metadata:**

```yaml
_section:
  sectionTitle: Industry Applications
  sectionDescription: Industries and sectors where this material is commonly processed with laser cleaning
  icon: building
  order: 1
  variant: default
```

**Field Requirements:**
- `sectionTitle`: "Industry Applications" (exact string)
- `sectionDescription`: Standard description (exact string above)
- `icon`: "building" (Lucide icon name)
- `order`: 1 (integer)
- `variant`: "default" (string)

## Migration Script

```python
#!/usr/bin/env python3
"""
Migrate operational.industry_applications from flat list to relationship section format.
Run: python3 migrate_industry_applications.py
"""

import os
import re
import yaml
from pathlib import Path

def slugify(text):
    """Convert display name to slug ID."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)  # Remove special chars
    text = re.sub(r'[-\s]+', '-', text)    # Replace spaces/dashes
    return text.strip('-')

def migrate_file(file_path):
    """Migrate a single YAML file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse YAML
    data = yaml.safe_load(content)
    
    # Check if migration needed
    if 'operational' not in data:
        return False
    
    industry_apps = data.get('operational', {}).get('industry_applications')
    
    # Already migrated (has presentation key)
    if isinstance(industry_apps, dict) and 'presentation' in industry_apps:
        return False
    
    # Old flat list format
    if isinstance(industry_apps, list):
        # Convert to relationship structure
        items = [{'id': slugify(name)} for name in industry_apps]
         with both id AND name
        items = [{'id': slugify(name), 'name': name_applications'] = {
            'presentation': 'card',
            'items': items,
            '_section': {
                'sectionTitle': 'Industry Applications',
                'sectionDescription': 'Industries and sectors where this material is commonly processed with laser cleaning',
                'icon': 'building',
                'order': 1,
                'variant': 'default'
            }
        }
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        return True
    
    return False

def main():
    materials_dir = Path('frontmatter/materials')
    
    migrated = 0
    skipped = 0
    
    for yaml_file in materials_dir.glob('*.yaml'):
        if migrate_file(yaml_file):
            print(f"✅ Migrated: {yaml_file.name}")
            migrated += 1
        else:
            print(f"⏭️  Skipped: {yaml_file.name}")
            skipped += 1
    
    print(f"\n📊 Summary:")
    print(f"   Migrated: {migrated}")
    print(f"   Skipped: {skipped}")
    print(f"   Total: {migrated + skipped}")

if __name__ == '__main__':
    main()
```

## Verification Steps

### 1. Check Migration Completeness

```bash
# Count files with old format (should be 0 after migration)
grep -l "operational:" frontmatter/materials/*.yaml | while read file; do
  if ! grep -A 15 "industry_applications:" "$file" | grep -q "_section:"; then
    echo "$file"
  fi
done | wc -l
```

**Expected:** 0 files

### 2. Verify _section Metadata

```bash
# Check all files have proper _section structure
grep -r "industry_applications:" frontmatter/materials/*.yaml -A 20 | grep "_section:" | wc -l
```

**Expected:** 153 (one per material file)

### 3. Validate Schema Compliance

```bash
# Run frontmatter validation
npm run validate:frontmatter
```

**Expected:** 0 errors related to industry_applications

### 4. Test Frontend Rendering

```bash
# Build and check for errors
npm run build
```

**Expected:** Build succeeds with 0 errors

### 5. Spot Check Sample Files

**Check aluminum-laser-cleaning.yaml:**
```bash
grep -A 25 "industry_applications:" frontmatter/materials/aluminum-laser-cleaning.yaml
```

**Expected Output:**
```yaml
    industry_applications:
      presentation: card
      items:
        - id: aerospace
        - id: automotive
        - id: construction
        - id: electronics-manufacturing
        - id: food-and-beverage-processing
        - id: marine
        - id: packaging
        - id: rail-transport
        - id: renewable-energy
      _section:
        sectionTitle: Industry Applications
        sectionDescription: Industries and sectors where this material is commonly processed with laser cleaning
        icon: building
        order: 1
        variant: default
```

## Example Transformations

### Example 1: Aluminum
**Before:**
```yaml
operational:
  industry_applications:
  - Aerospace
  - Automotive
  - Construction
  - Electronics Manufacturing
  - Food and Beverage Processing
  - Marine
  - Packaging
  - Rail Transport
  - Renewable Energy
```

**After:**
```yaml
operational:
  industry_applications:
    presentation: card
    items:
      - id: aerospace
        name: Aerospace
      - id: automotive
        name: Automotive
      - id: construction
        name: Construction
      - id: electronics-manufacturing
        name: Electronics Manufacturing
      - id: food-and-beverage-processing
        name: Food and Beverage Processing
      - id: marine
        name: Marine
      - id: packaging
        name: Packaging
      - id: rail-transport
        name: Rail Transport
      - id: renewable-energy
        name: Renewable Energy
    _section:
      sectionTitle: Industry Applications
      sectionDescription: Industries and sectors where this material is commonly processed with laser cleaning
      icon: building
      order: 1
      variant: default
```

### Example 2: Porcelain
**Before:**
```yaml
operational:
  industry_applications:
  - Cultural Heritage
  - Medical Devices
  - Electronics Manufacturing
  - Aerospace
  - Energy Sector
  - Automotive Manufacturing
  - Food Processing
  - Chemical Processing
  - Semiconductor Manufacturing
```  name: Cultural Heritage
      - id: medical-devices
        name: Medical Devices
      - id: electronics-manufacturing
        name: Electronics Manufacturing
      - id: aerospace
        name: Aerospace
      - id: energy-sector
        name: Energy Sector
      - id: automotive-manufacturing
        name: Automotive Manufacturing
      - id: food-processing
        name: Food Processing
      - id: chemical-processing
        name: Chemical Processing
      - id: semiconductor-manufacturing
        name: Semiconductor M
      - id: cultural-heritage
      - id: medical-devices
      - id: electronics-manufacturing
      - id: aerospace
      - id: energy-sector
      - id: automotive-manufacturing
      - id: food-processing
      - id: chemical-processing
      - id: semiconductor-manufacturing
    _section:
      sectionTitle: Industry Applications
      sectitems have both `id` (slugified) AND `name` (display text) fieldsommonly processed with laser cleaning
      icon: building
      order: 1
      variant: default
```

## Testing Checklist

After migration, verify:

- [ ] All 153 materials files migrated
- [ ] Zero files with old flat list format
- [ ] All files have `_section` metadata with 5 required fields
- [ ] `sectionTitle` is "Industry Applications" (exact match)
- [ ] `sectionDescription` matches standard text
- [ ] `icon` is "building"
- [ ] `order` is 1
- [ ] `variant` is "default"
- [ ] All industry names converted to valid slugs (lowercase, hyphenated)
- [ ] `presentation` is "card"
- [ ] Build succeeds with 0 errors
- [ ] Frontend renders industry_applications sections correctly
- [ ] No console errors about missing _section metadata

## Rollback Procedure

If migration causes issues:

```bash
# Restore from git
git checkout HEAD -- frontmatter/materials/*.yaml

# Or restore specific file
git checkout HEAD -- frontmatter/materials/aluminum-laser-cleaning.yaml
```

## Timeline

**Estimated Time:** 15 minutes
- Script execution: 2-3 minutes
- Verification: 5 minutes
- Testing: 5 minutes
- Documentation: 3 minutes

## Contact

Questions or issues during migration:
- Frontend Team: Review relationship section architecture
- Schema Team: Validate _section metadata requirements
- DevOps: Coordinate deployment timing

## Related Documentation

- `docs/BACKEND_RELATIONSHIP_REQUIREMENTS_JAN5_2026.md` - Complete relationship section requirements
- `schemas/frontmatter-v5.0.0.json` - JSON Schema validation
- `docs/proposals/MATERIALS_DUPLICATION_RESOLUTION_JAN5_2026.md` - Previous migration reference

---

**Status:** PENDING MIGRATION  
**Priority:** HIGH - Blocking frontend rendering  
**Assigned To:** Backend Team  
**Due Date:** January 6, 2026
