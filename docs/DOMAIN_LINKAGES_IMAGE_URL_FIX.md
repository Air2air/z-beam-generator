# Domain Linkages Image URL Correction Guide

**Date**: December 16, 2025  
**Status**: ✅ **IMPLEMENTED** - Code fix complete, frontmatter regeneration pending  
**Issue**: Domain linkages in frontmatter files contain incorrect image URL patterns  
**Impact**: Material cards in domain linkages sections display placeholder images instead of actual images  
**Priority**: HIGH - Affects visual presentation on all pages with domain linkages

---

## ✅ Implementation Complete

**Fixed in**: `shared/validation/domain_associations.py` (December 16, 2025)

All four image URL construction methods have been updated:
- Line 293: `get_contaminants_for_material()` ✅
- Line 340: `get_materials_for_contaminant()` ✅  
- Line 386: `get_compounds_for_contaminant()` ✅
- Line 431: `get_contaminants_for_compound()` ✅

**Next Step**: Regenerate frontmatter files to apply corrected URLs

---

## Problem Summary

Domain linkages in frontmatter files (materials, contaminants, compounds) reference image URLs that don't match the actual file naming conventions used by the target pages.

### Current Incorrect Patterns
```yaml
domain_linkages:
  compatible_materials:
    - id: aluminum
      image: /images/materials/aluminum.jpg  # ❌ WRONG
      
  produced_by_contaminants:
    - id: adhesive-residue
      image: /images/contaminants/adhesive-residue.jpg  # ❌ WRONG
      
  produces_compounds:
    - id: acetaldehyde
      image: /images/compounds/acetaldehyde.jpg  # ❌ WRONG
```

---

## Correct URL Patterns

### Materials
**Pattern**: `/images/material/{material-slug}-laser-cleaning-hero.jpg`
- Use **singular** "material" (not "materials")
- Include full slug with `-laser-cleaning` suffix
- End with `-hero.jpg`

**Examples**:
```yaml
# ✅ CORRECT
- id: aluminum
  image: /images/material/aluminum-laser-cleaning-hero.jpg

- id: stainless-steel
  image: /images/material/stainless-steel-laser-cleaning-hero.jpg

- id: aluminum-bronze
  image: /images/material/aluminum-bronze-laser-cleaning-hero.jpg
```

### Contaminants
**Pattern**: `/images/contaminant/{contaminant-slug}-contamination-hero.jpg`
- Use **singular** "contaminant" (not "contaminants")
- Include full slug with `-contamination` suffix
- End with `-hero.jpg`

**Examples**:
```yaml
# ✅ CORRECT
- id: adhesive-residue
  image: /images/contaminant/adhesive-residue-contamination-hero.jpg

- id: plastic-residue
  image: /images/contaminant/plastic-residue-contamination-hero.jpg

- id: oil-grease
  image: /images/contaminant/oil-grease-contamination-hero.jpg
```

### Compounds
**Pattern**: `/images/compound/{compound-slug}-compound-hero.jpg`
- Use **singular** "compound" (not "compounds")
- Include full slug with `-compound` suffix
- End with `-hero.jpg`

**Examples**:
```yaml
# ✅ CORRECT
- id: acetaldehyde
  image: /images/compound/acetaldehyde-compound-hero.jpg

- id: toluene
  image: /images/compound/toluene-compound-hero.jpg

- id: formaldehyde
  image: /images/compound/formaldehyde-compound-hero.jpg
```

---

## Complete Before/After Example

### Contaminant Page (adhesive-residue-contamination.yaml)

**BEFORE (Incorrect)**:
```yaml
domain_linkages:
  compatible_materials:
    - id: aluminum
      title: Aluminum Alloys
      url: /materials/aluminum-laser-cleaning
      image: /images/materials/aluminum.jpg  # ❌ WRONG
      
  produces_compounds:
    - id: acetaldehyde
      title: Acetaldehyde (C₂H₄O)
      url: /compounds/irritant/aldehyde/acetaldehyde-compound
      image: /images/compounds/acetaldehyde.jpg  # ❌ WRONG
```

**AFTER (Correct)**:
```yaml
domain_linkages:
  compatible_materials:
    - id: aluminum
      title: Aluminum Alloys
      url: /materials/aluminum-laser-cleaning
      image: /images/material/aluminum-laser-cleaning-hero.jpg  # ✅ CORRECT
      
  produces_compounds:
    - id: acetaldehyde
      title: Acetaldehyde (C₂H₄O)
      url: /compounds/irritant/aldehyde/acetaldehyde-compound
      image: /images/compound/acetaldehyde-compound-hero.jpg  # ✅ CORRECT
```

---

## Verification Checklist

After regenerating frontmatter, verify:

- [ ] All material image URLs use `/images/material/{slug}-laser-cleaning-hero.jpg`
- [ ] All contaminant image URLs use `/images/contaminant/{slug}-contamination-hero.jpg`
- [ ] All compound image URLs use `/images/compound/{slug}-compound-hero.jpg`
- [ ] Image paths use **singular** domain names (material, contaminant, compound)
- [ ] Image paths include full slugs with appropriate suffixes
- [ ] All paths end with `-hero.jpg`

---

## Implementation Instructions

### For Frontmatter Generator Script

1. **Locate domain_linkages generation code**
2. **Update image URL construction** for each domain type:

```python
# ✅ CORRECT IMAGE URL CONSTRUCTION

# For materials
material_image = f"/images/material/{material_id}-laser-cleaning-hero.jpg"

# For contaminants
contaminant_image = f"/images/contaminant/{contaminant_id}-contamination-hero.jpg"

# For compounds
compound_image = f"/images/compound/{compound_id}-compound-hero.jpg"
```

3. **Regenerate all frontmatter files**
4. **Test visual appearance** on pages with domain linkages:
   - Material cards should show actual material images
   - Contaminant/compound cards use colored backgrounds (working as designed)

---

## Files Requiring Regeneration

### All files with domain_linkages fields:
- **Materials** (`/frontmatter/materials/*.yaml`)
- **Contaminants** (`/frontmatter/contaminants/**/*.yaml`)
- **Compounds** (`/frontmatter/compounds/*.yaml`)

### Test Pages After Regeneration:
1. http://localhost:3000/contaminants/organic-residue/adhesive/adhesive-residue-contamination
   - Check "Compatible Materials" section (should show material images)
   - Check "Hazardous Compounds Generated" section (colored backgrounds)

2. http://localhost:3000/compounds/irritant/aldehyde/acetaldehyde-compound
   - Check "Produced By These Contaminants" section (colored backgrounds)

3. http://localhost:3000/materials/aluminum-laser-cleaning
   - Check "Common Contaminants" section (colored backgrounds)

---

## Related Issues

### Compound Slug Issue
19 compounds may have incorrect slugs (missing `-compound` suffix):
- acetaldehyde, acrolein, ammonia, benzene, benzoapyrene, carbon-dioxide, carbon-monoxide, chromium-vi, formaldehyde, hydrogen-chloride, hydrogen-cyanide, iron-oxide, nitrogen-oxides, pahs, phosgene, styrene, sulfur-dioxide, vocs, zinc-oxide

**Note**: Compound slugs should ALWAYS include the `-compound` suffix to avoid URL collisions.

---

## Technical Context

### Why This Matters
- **Card.tsx** component renders domain linkage cards with `variant="domain-linkage"`
- **Materials** use `variant="default"` which displays thumbnail images
- **Contaminants/Compounds** use `variant="domain-linkage"` with colored backgrounds
- **Incorrect image URLs** cause materials cards to show placeholder images
- **Correct pattern** ensures `Thumbnail` component can find and display actual images

### Display Logic
```tsx
// From Card.tsx
const cardVariant = domain === 'materials' ? 'default' : 'domain-linkage';

// Materials show images
{!isDomainLinkage && <Thumbnail {...thumbnailData} />}

// Contaminants/compounds use colored backgrounds
{isDomainLinkage && severity && (
  <div className={domainLinkageBg} />
)}
```

---

## Questions?

Contact the development team if:
- Image URLs still show placeholders after regeneration
- New domain types are added (require new URL patterns)
- Slug conventions change (update patterns accordingly)

**Last Updated**: December 16, 2025
