# Contaminant Breadcrumb Structure Guide

**For: Frontmatter Generator AI Assistant**  
**Date: December 15, 2025**  
**Status: Active**

---

## Overview

This document defines the **exact breadcrumb structure** for all contaminant pages in the Z-Beam system. The breadcrumb URLs must match the Next.js routing structure to ensure proper navigation and SEO.

## URL Structure

Contaminant pages follow a three-level hierarchical structure:

```
/contamination/{category}/{subcategory}/{slug}
```

### Required Metadata Fields

Every contaminant frontmatter file must have these fields:

- **`category`**: Top-level contamination category
- **`subcategory`**: Second-level category  
- **`slug`**: Unique identifier for the specific contaminant

### Example Metadata

```yaml
metadata:
  name: Adhesive Residue / Tape Marks
  slug: adhesive-residue-contamination
  category: organic-residue
  subcategory: adhesive
```

---

## Breadcrumb Array Structure

### Template

```yaml
breadcrumb:
  - label: Home
    href: /
  - label: Contamination
    href: /contamination
  - label: {Category Display Name}
    href: /contamination/{category}
  - label: {Contaminant Display Name}
    href: /contamination/{category}/{subcategory}/{slug}
```

### Complete Example

```yaml
metadata:
  name: Adhesive Residue / Tape Marks
  slug: adhesive-residue-contamination
  category: organic-residue
  subcategory: adhesive
  
  breadcrumb:
    - label: Home
      href: /
    - label: Contamination
      href: /contamination
    - label: Organic-Residue
      href: /contamination/organic-residue
    - label: Adhesive Residue / Tape Marks
      href: /contamination/organic-residue/adhesive/adhesive-residue-contamination
```

---

## Common Categories and Subcategories

### Organic Residue
- `category: organic-residue`
- Subcategories: `adhesive`, `petroleum`, `lubricant`, `wax`, `polymer`, `marking`, `natural`, `cleaning-agent`, `other`
- **Note**: `biological-fluid` subcategory removed (Dec 15, 2025) - brake dust moved to inorganic-coating/mineral, hydraulic fluid moved to petroleum

### Oxidation
- `category: oxidation`
- Subcategories: `ferrous`, `non-ferrous`, `battery`
- **Note**: Corrosion inhibitor moved from oxidation/non-ferrous to inorganic-coating/coating (Dec 15, 2025)

### Biological
- `category: biological`
- Subcategories: `growth`, `deposit`

### Inorganic Coating
- `category: inorganic-coating`
- Subcategories: `paint`, `mineral`, `ceramic`, `coating`, `hazardous`

### Metallic Coating
- `category: metallic-coating`
- Subcategories: `plating`, `anodizing`

### Thermal Damage
- `category: thermal-damage`
- Subcategories: `scale`, `fire`
- **Note**: `coating` subcategory removed (Dec 15, 2025) - cutting fluid moved to organic-residue/lubricant, thermal paste moved to organic-residue/other

### Chemical Residue
- `category: chemical-residue`
- Subcategories: `industrial`, `hazardous`

### Aging
- `category: aging`
- Subcategories: `photodegradation`

---

## ⚠️ Common Mistakes to AVOID

### ❌ Mistake 1: Double "contamination" Suffix
**WRONG:**
```yaml
href: /contamination/organic-residue/adhesive-residue-contamination-contamination
```

**CORRECT:**
```yaml
href: /contamination/organic-residue/adhesive/adhesive-residue-contamination
```

### ❌ Mistake 2: Missing Subcategory Level
**WRONG:**
```yaml
href: /contamination/organic-residue/adhesive-residue-contamination
```

**CORRECT:**
```yaml
href: /contamination/organic-residue/adhesive/adhesive-residue-contamination
```

### ❌ Mistake 3: Slug Only (No Category/Subcategory)
**WRONG:**
```yaml
href: /contamination/adhesive-residue-contamination
```

**CORRECT:**
```yaml
href: /contamination/organic-residue/adhesive/adhesive-residue-contamination
```

---

## Validation Checklist

Before generating contaminant frontmatter, verify:

- [ ] `category` field is defined
- [ ] `subcategory` field is defined
- [ ] `slug` field is defined
- [ ] Breadcrumb array has 4 items (Home, Contamination, Category, Item)
- [ ] Final breadcrumb href includes all three levels: `/contamination/{category}/{subcategory}/{slug}`
- [ ] No double "contamination" suffix in the URL
- [ ] Slug matches the `slug` metadata field exactly

---

## Technical Notes

### Next.js Routing Structure

The breadcrumb URLs correspond to this file structure:
```
app/contaminants/[category]/[subcategory]/[slug]/page.tsx
```

### URL Building Logic

The correct URL is built as:
```typescript
const correctUrl = `/contamination/${category}/${subcategory}/${slug}`;
```

### Category Display Names

Use proper capitalization and formatting for category labels:
- `organic-residue` → `Organic-Residue`
- `metallic-coating` → `Metallic-Coating`
- `thermal-damage` → `Thermal-Damage`

---

## Bulk Fix Script

If contaminant files have incorrect breadcrumbs, use this Python script:

```python
#!/usr/bin/env python3
import yaml
from pathlib import Path

contaminants_dir = Path('frontmatter/contaminants')
for file_path in contaminants_dir.glob('*.yaml'):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    metadata = data['metadata']
    category = metadata['category']
    subcategory = metadata['subcategory']
    slug = metadata['slug']
    
    # Build correct URL
    correct_url = f"/contamination/{category}/{subcategory}/{slug}"
    
    # Update last breadcrumb
    metadata['breadcrumb'][-1]['href'] = correct_url
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
```

---

## Related Documentation

- **Routing**: `app/contaminants/[category]/[subcategory]/[slug]/page.tsx`
- **Content Config**: `app/config/contentTypes.ts`
- **Breadcrumb Generation**: `app/utils/breadcrumbs.ts`

---

## Version History

- **v1.1** (Dec 15, 2025): Category Accuracy Corrections
  - Corrected 5 category misassignments:
    - `brake-dust`: organic-residue/biological-fluid → inorganic-coating/mineral
    - `hydraulic-fluid`: organic-residue/biological-fluid → organic-residue/petroleum
    - `cutting-fluid`: thermal-damage/coating → organic-residue/lubricant
    - `thermal-paste`: thermal-damage/coating → organic-residue/other
    - `corrosion-inhibitor`: oxidation/non-ferrous → inorganic-coating/coating
  - Updated subcategory listings to reflect accurate taxonomy

- **v1.0** (Dec 15, 2025): Initial documentation
  - Fixed 98 contaminant files with incorrect breadcrumb structure
  - Established three-level URL pattern as standard
