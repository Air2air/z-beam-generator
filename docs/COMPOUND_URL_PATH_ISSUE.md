# Compound URL Path Issue - Backend Fix Required

**Date**: January 8, 2026  
**Issue**: Compound card links on contaminant pages return 404 errors  
**Root Cause**: Mismatch between `fullPath` in compound frontmatter and what Next.js generates for static pages

---

## Problem Summary

When clicking on compound cards (e.g., "Carbon Dioxide", "Nitrogen Oxides") from contaminant detail pages like `/contaminants/biological/growth/algae-growth-contamination`, the links return 404 errors.

**Example failing URLs**:
- `/compounds/asphyxiant/simple_asphyxiant/carbon-dioxide-compound` (404)
- `/compounds/toxic_gas/oxidizing_gas/nitrogen-oxides-compound` (404)

---

## Technical Analysis

### How Frontend Routing Works

1. **Next.js Dynamic Routes**: `/app/compounds/[category]/[subcategory]/[slug]/page.tsx`
2. **Static Page Generation**: Uses `generateStaticParams()` which reads:
   - `category` field from compound frontmatter
   - `subcategory` field from compound frontmatter
   - Generates routes: `/compounds/{category}/{subcategory}/{slug}`

3. **Card Links**: Contaminant frontmatter uses `url` field from `producesCompounds` relationship items
   - These URLs come from compound frontmatter `fullPath` field

### The Core Issue

**`fullPath` is the source of truth** (per user directive), but Next.js static page generation constructs URLs from `category` + `subcategory` fields.

**When these don't match → 404 errors.**

---

## Current State Analysis

### Example: Carbon Dioxide Compound

**Compound Frontmatter** (`frontmatter/compounds/carbon-dioxide-compound.yaml`):
```yaml
id: carbon-dioxide-compound
name: Carbon Dioxide
category: asphyxiant
subcategory: simple_asphyxiant
fullPath: /compounds/asphyxiant/simple_asphyxiant/carbon-dioxide-compound
```

**Contaminant Reference** (`frontmatter/contaminants/algae-growth-contamination.yaml`):
```yaml
producesCompounds:
  items:
    - id: carbon-dioxide-compound
      url: /compounds/asphyxiant/simple_asphyxiant/carbon-dioxide-compound  # From compound fullPath
```

**Next.js Generates**: `/compounds/asphyxiant/simple_asphyxiant/carbon-dioxide-compound` ✓  
**Card Links To**: `/compounds/asphyxiant/simple_asphyxiant/carbon-dioxide-compound` ✓  
**Expected Result**: Should work (both match)  
**Actual Result**: 404 (likely caching/build issue)

---

### Example: Nitrogen Oxides Compound

**Compound Frontmatter** (`frontmatter/compounds/nitrogen-oxides-compound.yaml`):
```yaml
id: nitrogen-oxides-compound
name: Nitrogen Oxides
category: toxic_gas
subcategory: oxidizing_gas
fullPath: /compounds/toxic_gas/oxidizing_gas/nitrogen-oxides-compound
```

**Next.js Generates**: `/compounds/toxic_gas/oxidizing_gas/nitrogen-oxides-compound` ✓  
**Card Links To**: `/compounds/toxic_gas/oxidizing_gas/nitrogen-oxides-compound` ✓  
**Expected Result**: Should work  
**Actual Result**: 404

---

## Required Backend Fix

Since `fullPath` is the **source of truth**, backend must ensure consistency across all compound frontmatter files.

### Option 1: Parse fullPath to Update category/subcategory (RECOMMENDED)

Backend script should:

1. **Read fullPath from each compound**:
   ```
   /compounds/{category}/{subcategory}/{slug}
   ```

2. **Extract category and subcategory** from fullPath:
   ```python
   # Example: /compounds/toxic_gas/oxidizing_gas/nitrogen-oxides-compound
   parts = fullPath.split('/')
   category = parts[2]      # 'toxic_gas'
   subcategory = parts[3]   # 'oxidizing_gas'
   slug = parts[4]          # 'nitrogen-oxides-compound'
   ```

3. **Update compound frontmatter** to match:
   ```yaml
   category: toxic_gas        # Extracted from fullPath
   subcategory: oxidizing_gas # Extracted from fullPath
   fullPath: /compounds/toxic_gas/oxidizing_gas/nitrogen-oxides-compound  # Source of truth
   ```

4. **Update all contaminant references** to use correct fullPath-derived URLs

---

### Option 2: Update Frontend to Use fullPath Only (MORE COMPLEX)

Modify Next.js routing to parse fullPath instead of using category/subcategory:

**Changes Required**:
- `app/utils/categories/generic.ts` → `getAllCategoriesGeneric()`: Parse fullPath to extract category/subcategory
- `app/utils/categories/index.ts` → `generateItemStaticParams()`: Use fullPath parsing
- **Risk**: Breaking change affecting all content types (materials, contaminants, compounds, settings)

**Not recommended** - Option 1 is simpler and safer.

---

## Verification Steps

After backend fix:

1. **Check all compound frontmatter files**:
   ```bash
   # Verify category/subcategory match fullPath
   for file in frontmatter/compounds/*.yaml; do
     echo "File: $file"
     grep -E "^(category|subcategory|fullPath):" "$file"
     echo "---"
   done
   ```

2. **Check for mismatches**:
   ```python
   import yaml
   import glob
   
   for filepath in glob.glob('frontmatter/compounds/*.yaml'):
       with open(filepath) as f:
           data = yaml.safe_load(f)
       
       fullPath = data['fullPath']
       parts = fullPath.split('/')
       expected_category = parts[2]
       expected_subcategory = parts[3]
       
       if data['category'] != expected_category:
           print(f"MISMATCH: {filepath}")
           print(f"  fullPath says: {expected_category}")
           print(f"  category says: {data['category']}")
       
       if data['subcategory'] != expected_subcategory:
           print(f"MISMATCH: {filepath}")
           print(f"  fullPath says: {expected_subcategory}")
           print(f"  subcategory says: {data['subcategory']}")
   ```

3. **Rebuild Next.js static pages**:
   ```bash
   rm -rf .next
   npm run build
   ```

4. **Test URLs**:
   ```bash
   # Test each compound URL from contaminant pages
   curl -I http://localhost:3000/compounds/asphyxiant/simple_asphyxiant/carbon-dioxide-compound
   curl -I http://localhost:3000/compounds/toxic_gas/oxidizing_gas/nitrogen-oxides-compound
   ```

---

## All Compound Categories

Current compound categories found:
```
asphyxiant (1 compound)  ← UNIQUE - only carbon-dioxide
carcinogen (4 compounds)
corrosive_gas (2 compounds)
irritant (3 compounds)
metal_fume (2 compounds)
particulate (11 compounds)
solvent (1 compound)
toxic_gas (6 compounds)
vapor (2 compounds)
```

### Potential Category Issues

**Carbon Dioxide** is the only compound with `category: asphyxiant`. This may be intentional, but verify:
- Should it be `category: toxic_gas, subcategory: simple_asphyxiant`?
- Or keep `category: asphyxiant, subcategory: simple_asphyxiant`?

**Consistency Check**: All other toxic gases use `category: toxic_gas` with various subcategories:
- Carbon Monoxide: `toxic_gas / asphyxiant`
- Nitrogen Oxides: `toxic_gas / oxidizing_gas`
- Sulfur Dioxide: `toxic_gas / {subcategory}`

---

## Action Items for Backend

- [ ] Create Python script: `scripts/fix-compound-paths.py`
- [ ] Parse fullPath from all compound frontmatter files
- [ ] Extract category/subcategory from fullPath structure
- [ ] Update compound frontmatter to ensure category/subcategory match fullPath
- [ ] Update contaminant `producesCompounds` references to use correct URLs
- [ ] Run verification checks
- [ ] Commit changes
- [ ] Trigger frontend rebuild (`rm -rf .next && npm run build`)

---

## Files to Review

**Compound Frontmatter**: `/frontmatter/compounds/*.yaml` (34 files)

**Contaminant References**: Any contaminant with `producesCompounds` relationships:
- `/frontmatter/contaminants/algae-growth-contamination.yaml`
- (Search: `grep -r "producesCompounds:" frontmatter/contaminants/`)

**Frontend Routing**:
- `/app/compounds/[category]/[subcategory]/[slug]/page.tsx`
- `/app/utils/categories/generic.ts` (getAllCategoriesGeneric)
- `/app/utils/categories/index.ts` (generateItemStaticParams)

---

## Related Documentation

- **User Directive**: "I added fullpath specifically to solve these path issues, so we no longer need to construct them."
- **Implication**: `fullPath` is the single source of truth for all URLs
- **Requirement**: Backend must ensure category/subcategory match fullPath for Next.js routing to work
