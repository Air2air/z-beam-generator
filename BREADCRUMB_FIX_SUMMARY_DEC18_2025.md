# Breadcrumb and Field Order Issues - Summary Report

**Date**: December 18, 2025  
**Status**: ✅ **FIX IMPLEMENTED** - Config changes committed, regeneration required

---

## Issue 1: Breadcrumb Format Regression ✅ **FIXED IN CONFIG**

### Problem
- **Current**: `breadcrumb_text: "Home / Materials / stone / Alabaster"` (text string)
- **Expected**: `breadcrumb: [{label: Home, href: /}, {label: Materials, href: /materials}, ...]` (array)

### Root Cause
BreadcrumbGenerator in UniversalExporter was generating text strings, overwriting the proper array structure from TrivialFrontmatterExporter.

### Fix Applied
✅ Removed breadcrumb generator from all 4 export configs:
- `export/config/materials.yaml`
- `export/config/contaminants.yaml`
- `export/config/compounds.yaml`
- `export/config/settings.yaml`

**Commit**: 67ffb090 "Fix breadcrumb generation: remove text-based generators"

---

## Issue 2: Field Order Normalization ⚠️ **NEEDS ACTION**

### Current Status
**0/422 files** have correct field order:
- Materials: 0/152 valid (4 issues each)
- Contaminants: 0/97 valid (2 issues each)
- Compounds: 0/20 valid (2 issues each)
- Settings: 0/153 valid (2 issues each)

### Common Issues Found
1. **Field order incorrect**: title, images, regulatory_standards out of order
2. **Wrong breadcrumb field**: Has `breadcrumb_text` instead of `breadcrumb` array
3. **Unexpected fields**: applications, characteristics, components, contamination, voice_enhanced

### Why Fields Are Out of Order
The frontmatter files were generated and various enrichers/generators have added fields in different orders over time, causing the current state to diverge from the canonical field order specification.

---

## Required Actions

### 1. Regenerate All Frontmatter ⏳ **REQUIRED**

The breadcrumb config fix requires regenerating all frontmatter files to apply the changes.

**In z-beam repository**:
```bash
cd /Users/todddunning/Desktop/Z-Beam/z-beam
python3 -m app.scripts.regenerate-all-frontmatter
```

This will:
- Generate proper `breadcrumb` arrays (not `breadcrumb_text`)
- Use TrivialFrontmatterExporter's `_generate_breadcrumb()` method
- Fix the structure for all 422 files

### 2. Verify Breadcrumb Structure ⏳ **AFTER REGENERATION**

```bash
cd /Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/materials
grep -A 10 "^breadcrumb:" alabaster-laser-cleaning.yaml

# Should show:
# breadcrumb:
#   - label: Home
#     href: /
#   - label: Materials
#     href: /materials
#   ...
```

### 3. Check Field Order Again ⏳ **AFTER REGENERATION**

```bash
cd /Users/todddunning/Desktop/Z-Beam/z-beam-generator
python3 scripts/check_field_order.py
```

If still issues, the field order specification may need updating or the export process needs to respect field order.

---

## Technical Details

### Breadcrumb Generation Flow

**Correct**:
```
TrivialFrontmatterExporter
  → _generate_breadcrumb()
    → Returns: [{label: "Home", href: "/"}, {label: "Materials", href: "/materials"}, ...]
```

**Was Wrong (Now Fixed)**:
```
UniversalExporter BreadcrumbGenerator  
  → template.format(**frontmatter)
    → Returns: "Home / Materials / stone / Alabaster" (text string)
    → Overwrote proper array structure ❌
```

### Field Order Specification

Located in: `data/schemas/FrontmatterFieldOrder.yaml`

**Materials expected order** (top fields):
1. id
2. name
3. slug
4. category
5. subcategory
6. content_type
7. schema_version
8. datePublished
9. dateModified
10. author
11. title
12. description
13. images
14. micro
15. faq
...
19. seo_description
20. **breadcrumb** (not breadcrumb_text!)

---

## Testing After Regeneration

### Breadcrumb Format Test
```bash
# Check 3 sample files from each domain
cd /Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter

# Materials
grep "breadcrumb:" materials/alabaster-laser-cleaning.yaml
grep "breadcrumb_text:" materials/alabaster-laser-cleaning.yaml  # Should be empty

# Contaminants  
grep "breadcrumb:" contaminants/adhesive-residue-contaminant.yaml
grep "breadcrumb_text:" contaminants/adhesive-residue-contaminant.yaml  # Should be empty

# Compounds
grep "breadcrumb:" compounds/pahs-compound.yaml

# Settings
grep "breadcrumb:" settings/aluminum-bronze-settings.yaml
```

### Field Order Test
```bash
cd /Users/todddunning/Desktop/Z-Beam/z-beam-generator
python3 scripts/check_field_order.py

# Expected after regeneration:
# Materials: X/152 valid (hopefully improved)
# Contaminants: X/97 valid
# Compounds: X/20 valid
# Settings: X/153 valid
```

---

## Commits

1. **67ffb090** (Dec 18, 2025): "Fix breadcrumb generation: remove text-based generators"
   - Removed incorrect breadcrumb generators from all 4 configs
   - Added documentation file
   - Ready for frontmatter regeneration

---

## Next Steps

1. ⏳ Regenerate all frontmatter in z-beam repository
2. ⏳ Verify breadcrumb arrays are generated correctly
3. ⏳ Check field order status
4. ⏳ Commit regenerated frontmatter files
5. ⏳ Test website breadcrumb navigation

---

**Status**: Config fixes complete, waiting for frontmatter regeneration  
**Impact**: All 422 frontmatter files need regeneration  
**Priority**: HIGH - Website breadcrumb navigation currently using wrong format
