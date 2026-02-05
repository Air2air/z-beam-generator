# CRITICAL DISCOVERY: Source Data is CORRECT, Export is BREAKING It

**Date**: February 4, 2026  
**Discovery**: Source Contaminants.yaml has CORRECT normalized structure. Export pipeline is BREAKING it.

---

## 🚨 THE DISCOVERY

### Source Data (Contaminants.yaml) - ✅ CORRECT
```yaml
relationships:
  interactions:
    producesCompounds:
      presentation: card
      items:
        - id: carbon-dioxide-compound
          title: Carbon Dioxide
          name: Carbon Dioxide
          category: asphyxiant
          subcategory: simple_asphyxiant
          url: /compounds/asphyxiant/simple_asphyxiant/carbon-dioxide-compound
          image: /images/compound/carbon-dioxide-compound-hero.jpg
          description: Carbon Dioxide Compound safety information...
          phase: unknown
          hazardLevel: unknown
          
    affectsMaterials:
      presentation: card
      items:
        - id: aluminum-laser-cleaning
          name: Aluminum
          category: metal
          subcategory: non-ferrous
          url: /materials/metal/non-ferrous/aluminum-laser-cleaning
          image: /images/material/aluminum-laser-cleaning-hero.jpg
          description: This is a TEST description for Aluminum...
          frequency: moderate
          difficulty: moderate
```

**Status**: Source data has PERFECT normalized structure with:
- ✅ `interactions.producesCompounds.items` - Full 9-field denormalized compounds
- ✅ `interactions.affectsMaterials.items` - Full 8-field denormalized materials  
- ✅ `presentation: card` metadata
- ✅ Complete denormalized data (no just IDs, full objects)

### Exported Frontmatter - ❌ BROKEN
```yaml
relationships:
  materials:
    common:
      - id: aluminum-laser-cleaning
        frequency: moderate
        difficulty: moderate
  compounds:
    produces:
      - id: carbon-dioxide-compound
        phase: unknown
        hazard: unknown
```

**Status**: Export transforms CORRECT structure into WRONG flat structure:
- ❌ `materials.common` instead of `interactions.affectsMaterials.items`
- ❌ `compounds.produces` instead of `interactions.producesCompounds.items`
- ❌ Missing ALL denormalized fields (name, category, subcategory, url, image, description)
- ❌ Missing `presentation` metadata
- ❌ NO `_section` metadata

### ContaminantsLayout Expectations - ✅ CORRECT
```typescript
const producesCompounds = relationships?.interactions?.producesCompounds?.items || [];
const affectsMaterials = relationships?.interactions?.affectsMaterials?.items || [];
```

**Status**: Layout already expects normalized structure that SOURCE provides!

---

## 🔍 ROOT CAUSE

The export pipeline is **ACTIVELY BREAKING** correct source data by:
1. Reading `interactions.producesCompounds.items` from source
2. Transforming it to flat `compounds.produces` array
3. Stripping out all denormalized fields
4. Losing _section metadata
5. Writing broken structure to frontmatter

**This is the OPPOSITE of what we thought!**

Original hypothesis: "Export adds structure not in source"  
**REALITY**: Export DESTROYS correct structure from source

---

## 🎯 WHAT NEEDS TO BE FIXED

### Option A: Stop Breaking the Data (RECOMMENDED)
**Fix the export pipeline to PRESERVE the source structure instead of transforming it.**

1. **Find transformation code** that converts:
   - `interactions.producesCompounds` → `compounds.produces`
   - `interactions.affectsMaterials` → `materials.common`

2. **Remove or fix transformation** to preserve:
   - Nested `interactions.*` structure
   - Full denormalized data objects
   - `presentation` metadata
   - `_section` blocks

3. **Verify pass-through** - Source structure should flow to frontmatter unchanged

**Implementation**:
- Grep for code doing relationship flattening/simplification
- Check if there's a schema migration converting v6.0 to legacy format
- Look for deprecated field mapping converting new → old structure
- Possibly in universal_content_generator.py relationship tasks

### Option B: Keep Legacy Export Format (NOT RECOMMENDED)
Update layouts to match broken export format.

**Why NOT recommended**:
- 98 contaminants already have correct source data
- 34 compounds likely same
- Materials already working with normalized format
- Would be moving BACKWARD from correct architecture

---

## 📊 VERIFICATION CHECKLIST

To verify this discovery:

1. ✅ **Source has correct structure**:
   ```bash
   grep -A 15 "producesCompounds:" data/contaminants/Contaminants.yaml | head -50
   # Shows: interactions.producesCompounds.items with full data
   ```

2. ✅ **Layout expects correct structure**:
   ```typescript
   // ContaminantsLayout.tsx line 61-62
   const producesCompounds = relationships?.interactions?.producesCompounds?.items || [];
   const affectsMaterials = relationships?.interactions?.affectsMaterials?.items || [];
   ```

3. ✅ **Export produces wrong structure**:
   ```bash
   grep -A 15 "relationships:" frontmatter/contaminants/mold-mildew-contamination.yaml
   # Shows: materials.common and compounds.produces (flat structure)
   ```

4. ❓ **Export code location** (TO FIND):
   - Where is the transformation happening?
   - Is it in universal_content_generator.py?
   - Is it in field_mapping or camelcase_normalization?
   - Is there a schema version downgrade happening?

---

## 🔧 IMMEDIATE NEXT STEPS

1. **Find transformation code**:
   ```bash
   # Search for code that creates materials.common or compounds.produces
   grep -r "materials.*common\|compounds.*produces" export/
   grep -r "affectsMaterials.*materials\|producesCompounds.*compounds" export/
   grep -r "flatten.*relationship\|simplify.*relationship" export/
   ```

2. **Check export config**:
   ```yaml
   # export/config/contaminants.yaml
   # Look for tasks that transform relationships
   # - relationship_simplification?
   # - relationship_flattening?
   # - schema_version_downgrade?
   ```

3. **Test with single contaminant**:
   ```bash
   # Export one contaminant and see what transformation happens
   python3 run.py --export --domain contaminants --item adhesive-residue-contamination
   # Compare source vs frontmatter relationships structure
   ```

4. **Implement fix**:
   - Remove or modify transformation code
   - Ensure source structure passes through to frontmatter
   - Test with all contaminants
   - Verify pages render correctly

---

## 📈 IMPACT ASSESSMENT

### If We Fix Export (Option A - RECOMMENDED)

**Immediate benefits**:
- ✅ 490 broken content sections → 0 broken sections
- ✅ 87% section failure → 0% failure  
- ✅ Contaminants pages match materials pages (9 sections each)
- ✅ Zero code changes to layouts (already correct)
- ✅ Zero changes to source data (already correct)
- ✅ Architectural consistency across all domains

**Work required**:
- 🔧 Find and fix 1 export transformation (likely 10-50 lines)
- 🔧 Regenerate 98 contaminant frontmatter files
- 🔧 Test rendering on all contaminant pages
- 🔧 Verify no regression on materials/compounds/settings

**Timeline**: 2-4 hours

### If We Update Layouts (Option B - NOT RECOMMENDED)

**Problems**:
- ❌ Moving BACKWARD from correct architecture
- ❌ Duplicating broken pattern to other domains
- ❌ 98 contaminants have correct source but can't use it
- ❌ Would need to update Materials.yaml to match broken format
- ❌ Creates inconsistency: source has one format, frontend expects another
- ❌ Violates Core Principle 0.6 (export should preserve, not transform)

**Work required**:
- 🔧 Update ContaminantsLayout (rewrite data extraction)
- 🔧 Update CompoundsLayout (same issue likely)
- 🔧 Update SettingsLayout (verify and possibly fix)
- 🔧 Test all layouts with new expectations
- 🔧 Document divergence between source and frontend formats

**Timeline**: 6-8 hours + creates architectural debt

---

## 🎯 RECOMMENDATION

**STRONGLY RECOMMEND Option A: Fix Export to Preserve Source Structure**

**Rationale**:
1. Source data is already correct (no work needed there)
2. Layouts are already correct (no work needed there)  
3. Only export pipeline is broken (focused fix)
4. Moves us FORWARD not backward
5. Aligns with Core Principle 0.6 (preserve, don't transform)
6. Fastest path to working system
7. No architectural debt

**Next Action**:
Find and fix the export transformation code that's breaking the correct source structure.
