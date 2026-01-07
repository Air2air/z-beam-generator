# Frontmatter Field Ordering Standards

**Version**: 5.0.0  
**Date**: January 6, 2026  
**Audience**: Backend generators, data processing scripts  
**Purpose**: Standardize YAML frontmatter field ordering for consistency and maintainability

---

## 🎯 Executive Summary

**All frontmatter YAML files MUST follow this exact field order.** Proper ordering ensures:
- Consistent parsing and validation
- Easier debugging and code review
- Predictable frontend data consumption
- Reduced merge conflicts
- Better maintainability

**Critical Issue Fixed**: `subcategory` field was appearing at line 681 instead of line 5 in carbon-dioxide-compound.yaml, causing 404 routing errors.

---

## 📋 Universal Field Order (All Content Types)

### Section 1: Core Identity (Lines 1-10)
```yaml
id: [slug]
name: [Display Name]
displayName: [Full Display Name with Symbols]
category: [primary-category]
subcategory: [sub-category]              # ⚠️ MUST be here, not at bottom of file
hazard_class: [classification]           # compounds/contaminants only
datePublished: [ISO-8601 timestamp]
dateModified: [ISO-8601 timestamp]
contentType: [material|compound|contaminant|settings]
schemaVersion: [version string]
```

### Section 2: Navigation & SEO (Lines 11-30)
```yaml
fullPath: [/full/url/path]
breadcrumb:
  - label: [text]
    href: [path]
pageTitle: [SEO Title]
pageDescription: [Full description for page content]
metaDescription: [160 char meta description]
```

### Section 3: Technical Properties (Lines 31+)
```yaml
# Chemical/Material specific fields
chemical_formula: [formula]
cas_number: [CAS registry]
molecular_weight: [number]

# Material properties
density: [value]
melting_point: [value]
# ... etc
```

### Section 4: Content Fields (Variable position)
```yaml
health_effects: [text]
exposure_guidelines: [text]
detection_methods: [text]
first_aid: [text]
# ... other content fields
```

### Section 5: Media Assets (After content)
```yaml
images:
  hero:
    url: [path]
    alt: [description]
    width: [number]
    height: [number]
  micro:
    url: [path]
    alt: [description]
```

### Section 6: Relationships (After images)
```yaml
industry_applications:
  automotive:
    relevance: high
    examples:
      - [text]
  aerospace:
    relevance: medium
    examples:
      - [text]
```

### Section 7: Nested Objects (End of file)
```yaml
# Complex nested structures like safety_data, regulatory_standards
safety_data:
  physical_hazards:
    flammability:
      # ...
```

---

## 📄 Content-Type Specific Examples

### Materials
```yaml
id: aluminum-laser-cleaning
name: Aluminum
displayName: Aluminum (Al)
category: metal
subcategory: non-ferrous
datePublished: '2026-01-06T00:00:00.000Z'
dateModified: '2026-01-06T00:00:00.000Z'
contentType: material
schemaVersion: 5.0.0
fullPath: /materials/metal/non-ferrous/aluminum-laser-cleaning
breadcrumb:
  - label: Home
    href: /
  - label: Materials
    href: /materials
  - label: Metal
    href: /materials/metal
  - label: Non-Ferrous
    href: /materials/metal/non-ferrous
pageTitle: Aluminum Laser Cleaning
pageDescription: Comprehensive guide to aluminum laser cleaning...
metaDescription: Aluminum laser cleaning parameters, settings...
density: 2.70
melting_point: 660.3
thermal_conductivity: 237
# ... rest of properties
micro: [content text]
description: [content text]
subtitle: [content text]
author: [author object]
images:
  hero:
    url: /images/materials/aluminum-laser-cleaning-hero.jpg
    alt: Aluminum laser cleaning visualization
    width: 1200
    height: 630
industry_applications:
  automotive:
    relevance: high
    examples:
      - Engine block cleaning
```

### Compounds
```yaml
id: carbon-dioxide-compound
name: Carbon Dioxide
displayName: Carbon Dioxide (CO₂)
category: asphyxiant
subcategory: simple_asphyxiant          # ⚠️ CRITICAL: Must be here!
hazard_class: asphyxiant
datePublished: '2026-01-06T00:00:00.000Z'
dateModified: '2026-01-06T00:00:00.000Z'
contentType: compound
schemaVersion: 5.0.0
fullPath: /compounds/asphyxiant/simple_asphyxiant/carbon-dioxide-compound
breadcrumb:
  - label: Home
    href: /
  - label: Compounds
    href: /compounds
  - label: Asphyxiant
    href: /compounds/asphyxiant
  - label: Simple_Asphyxiant
    href: /compounds/asphyxiant/simple_asphyxiant
pageTitle: Carbon Dioxide
pageDescription: Carbon Dioxide Compound safety information...
metaDescription: Carbon Dioxide laser cleaning guide...
chemical_formula: CO₂
cas_number: 124-38-9
molecular_weight: 44.01
formula: CO₂                             # ⚠️ Note: different from chemical_formula
health_effects: [content text]
exposure_guidelines: [content text]
detection_methods: [content text]
first_aid: [content text]
images:
  hero:
    url: /images/compound/carbon-dioxide-compound-hero.jpg
    alt: Carbon Dioxide visualization
ppe_requirements: [content text]
safety_data:
  physical_hazards:
    # ... nested structure
```

### Contaminants
```yaml
id: rust-oxidation-contamination
name: Rust (Oxidation)
displayName: Rust (Iron Oxide Oxidation)
category: oxidation
subcategory: ferrous
hazard_class: respiratory_irritant
datePublished: '2026-01-06T00:00:00.000Z'
dateModified: '2026-01-06T00:00:00.000Z'
contentType: contaminant
schemaVersion: 5.0.0
fullPath: /contaminants/oxidation/ferrous/rust-oxidation-contamination
breadcrumb:
  - label: Home
    href: /
  - label: Contaminants
    href: /contaminants
  - label: Oxidation
    href: /contaminants/oxidation
  - label: Ferrous
    href: /contaminants/oxidation/ferrous
pageTitle: Rust Oxidation Laser Cleaning
pageDescription: Professional rust removal using laser cleaning...
metaDescription: Rust laser cleaning guide...
chemical_composition: Fe₂O₃, Fe₃O₄, FeO(OH)
common_locations: [text]
health_hazards: [text]
# ... rest of properties
```

### Settings
```yaml
id: aluminum-settings
name: Aluminum Settings
displayName: Aluminum Laser Cleaning Settings
category: metal
subcategory: non-ferrous
datePublished: '2026-01-06T00:00:00.000Z'
dateModified: '2026-01-06T00:00:00.000Z'
contentType: settings
schemaVersion: 5.0.0
fullPath: /settings/metal/non-ferrous/aluminum-settings
breadcrumb:
  - label: Home
    href: /
  - label: Settings
    href: /settings
  - label: Metal
    href: /settings/metal
  - label: Non-Ferrous
    href: /settings/metal/non-ferrous
pageTitle: Aluminum Laser Settings
pageDescription: Optimized laser cleaning settings for aluminum...
metaDescription: Aluminum laser cleaning parameters...
relatedMaterial: aluminum-laser-cleaning
power_range:
  min: 50
  max: 200
  unit: W
frequency_range:
  min: 20
  max: 100
  unit: kHz
# ... machine settings
```

---

## 🚨 Common Mistakes to Avoid

### ❌ WRONG: subcategory at end of file
```yaml
id: carbon-dioxide-compound
name: Carbon Dioxide
category: asphyxiant
# ... 680 lines of content ...
subcategory: simple_asphyxiant          # ❌ TOO LATE!
formula: CO₂
```
**Impact**: Routing fails, generates 404 errors

### ✅ CORRECT: subcategory near top
```yaml
id: carbon-dioxide-compound
name: Carbon Dioxide
category: asphyxiant
subcategory: simple_asphyxiant          # ✅ CORRECT POSITION
datePublished: '2026-01-06T00:00:00.000Z'
```

### ❌ WRONG: Mixed metadata and content
```yaml
id: aluminum-laser-cleaning
micro: [content]                         # ❌ Too early
name: Aluminum
category: metal
```

### ✅ CORRECT: Metadata first, content later
```yaml
id: aluminum-laser-cleaning
name: Aluminum
category: metal
subcategory: non-ferrous
# ... all metadata fields ...
micro: [content]                         # ✅ After metadata
```

---

## 🔍 Field Order Priority Levels

### Priority 1: Critical Routing Fields (MUST be first 10 lines)
- `id`
- `name`
- `displayName`
- `category`
- `subcategory` ⚠️ **CRITICAL**
- `hazard_class` (if applicable)
- `contentType`
- `schemaVersion`

**Reason**: Routing and content discovery depend on these fields being parsed first.

### Priority 2: Navigation & SEO (Lines 11-30)
- `fullPath`
- `breadcrumb`
- `pageTitle`
- `pageDescription`
- `metaDescription`

**Reason**: Frontend components expect these fields in consistent positions for performance.

### Priority 3: Technical Properties (After metadata)
- Chemical formulas
- Physical properties
- Measurements

**Reason**: Grouped for logical organization and easier validation.

### Priority 4: Content Fields (After technical)
- `micro`
- `description`
- `subtitle`
- `health_effects`
- `exposure_guidelines`

**Reason**: Human-readable content follows structured data.

### Priority 5: Relationships (After content)
- `industry_applications`
- `relatedMaterial`
- `compatible_materials`

**Reason**: Relationship objects can be large; keep at end for readability.

### Priority 6: Complex Objects (End of file)
- `safety_data`
- `regulatory_standards`
- `environmental_data`

**Reason**: Large nested structures should not interrupt core fields.

---

## 🛠️ Backend Implementation Guidelines

### For Python Generators
```python
def generate_frontmatter(data: dict) -> str:
    """Generate frontmatter with correct field ordering."""
    field_order = [
        # Priority 1: Critical routing
        'id', 'name', 'displayName', 'category', 'subcategory',
        'hazard_class', 'datePublished', 'dateModified',
        'contentType', 'schemaVersion',
        
        # Priority 2: Navigation
        'fullPath', 'breadcrumb', 'pageTitle',
        'pageDescription', 'metaDescription',
        
        # Priority 3: Technical (content-type specific)
        'chemical_formula', 'cas_number', 'molecular_weight',
        'density', 'melting_point', 'thermal_conductivity',
        
        # Priority 4: Content fields
        'micro', 'description', 'subtitle', 'author',
        'health_effects', 'exposure_guidelines',
        
        # Priority 5: Media
        'images',
        
        # Priority 6: Relationships
        'industry_applications', 'relatedMaterial',
        
        # Priority 7: Complex objects
        'safety_data', 'regulatory_standards'
    ]
    
    ordered_data = OrderedDict()
    for key in field_order:
        if key in data:
            ordered_data[key] = data[key]
    
    # Add any remaining fields not in order list
    for key, value in data.items():
        if key not in ordered_data:
            ordered_data[key] = value
    
    return yaml.dump(ordered_data, sort_keys=False)
```

### For Node.js Generators
```javascript
function generateFrontmatter(data) {
  const fieldOrder = [
    // Priority 1: Critical routing
    'id', 'name', 'displayName', 'category', 'subcategory',
    'hazard_class', 'datePublished', 'dateModified',
    'contentType', 'schemaVersion',
    
    // Priority 2: Navigation
    'fullPath', 'breadcrumb', 'pageTitle',
    'pageDescription', 'metaDescription',
    
    // Priority 3: Technical
    'chemical_formula', 'cas_number', 'molecular_weight',
    
    // Priority 4: Content
    'micro', 'description', 'subtitle', 'author',
    
    // Priority 5: Media
    'images',
    
    // Priority 6: Relationships
    'industry_applications',
    
    // Priority 7: Complex objects
    'safety_data'
  ];
  
  const orderedData = {};
  fieldOrder.forEach(key => {
    if (data[key] !== undefined) {
      orderedData[key] = data[key];
    }
  });
  
  // Add remaining fields
  Object.keys(data).forEach(key => {
    if (!orderedData.hasOwnProperty(key)) {
      orderedData[key] = data[key];
    }
  });
  
  return yaml.dump(orderedData, { sortKeys: false });
}
```

---

## ✅ Validation Checklist

Before committing any frontmatter file:

- [ ] `id` is on line 1
- [ ] `category` is within first 10 lines
- [ ] `subcategory` is immediately after `category` (if applicable)
- [ ] `contentType` and `schemaVersion` are in first 10 lines
- [ ] `fullPath` matches the file location
- [ ] `breadcrumb` array is complete and ordered correctly
- [ ] All metadata fields come before content fields
- [ ] Content fields (`micro`, `description`) come after technical properties
- [ ] `images` object comes after content fields
- [ ] `industry_applications` comes after images
- [ ] Complex nested objects (`safety_data`, etc.) are at the end
- [ ] No duplicate fields exist anywhere in the file
- [ ] YAML is valid (no syntax errors)

---

## 🔧 Automated Validation

### Create Validation Script
```bash
# scripts/validation/validate-field-order.sh

#!/bin/bash
# Validate frontmatter field ordering

errors=0

for file in frontmatter/**/*.yaml; do
  # Check subcategory is in first 10 lines (if it exists)
  if grep -q "^subcategory:" "$file"; then
    line_num=$(grep -n "^subcategory:" "$file" | head -1 | cut -d: -f1)
    if [ "$line_num" -gt 10 ]; then
      echo "❌ ERROR: $file - subcategory at line $line_num (should be < 10)"
      errors=$((errors + 1))
    fi
  fi
  
  # Check id is on line 1
  if ! head -1 "$file" | grep -q "^id:"; then
    echo "❌ ERROR: $file - id is not on line 1"
    errors=$((errors + 1))
  fi
  
  # Check for duplicate fields
  duplicates=$(grep -E "^[a-z_]+:" "$file" | sort | uniq -d)
  if [ -n "$duplicates" ]; then
    echo "❌ ERROR: $file - duplicate fields found:"
    echo "$duplicates"
    errors=$((errors + 1))
  fi
done

if [ $errors -eq 0 ]; then
  echo "✅ All frontmatter files have correct field ordering"
  exit 0
else
  echo "❌ Found $errors files with field ordering issues"
  exit 1
fi
```

---

## 📊 Migration Plan for Existing Files

If existing files have incorrect ordering:

### Step 1: Identify Issues
```bash
npm run validate:field-order
```

### Step 2: Batch Fix Script
```python
# scripts/fix-field-order.py

import yaml
from pathlib import Path
from collections import OrderedDict

FIELD_ORDER = [
    'id', 'name', 'displayName', 'category', 'subcategory',
    'hazard_class', 'datePublished', 'dateModified',
    'contentType', 'schemaVersion', 'fullPath', 'breadcrumb',
    'pageTitle', 'pageDescription', 'metaDescription',
    # ... complete list
]

def reorder_frontmatter(file_path):
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    
    ordered = OrderedDict()
    for key in FIELD_ORDER:
        if key in data:
            ordered[key] = data.pop(key)
    
    # Add remaining fields
    for key, value in data.items():
        ordered[key] = value
    
    with open(file_path, 'w') as f:
        yaml.dump(dict(ordered), f, sort_keys=False)

# Process all files
for file in Path('frontmatter').rglob('*.yaml'):
    reorder_frontmatter(file)
```

### Step 3: Verify Changes
```bash
npm run build
npm run test:all
git diff frontmatter/
```

---

## 🎓 Training Notes for Backend Team

1. **Always use OrderedDict or equivalent** when generating YAML
2. **Never append fields** - always insert in correct position
3. **Validate before commit** - run field order checks
4. **Check similar files** - use existing files as templates
5. **Test routing** - ensure fullPath/category/subcategory work together
6. **Document exceptions** - if a field needs different positioning, document why

---

## 📞 Support & Questions

- **Schema Issues**: See `schemas/frontmatter-v5.0.0.json`
- **Routing Problems**: Check `app/[contentType]/[category]/[subcategory]/[slug]/page.tsx`
- **Validation Errors**: Run `npm run validate:frontmatter`
- **Field Definitions**: See `docs/FRONTEND_REQUIRED_FIELDS_JAN4_2026.md`

---

**Last Updated**: January 6, 2026  
**Next Review**: February 2026  
**Document Owner**: Frontend/Backend Integration Team
