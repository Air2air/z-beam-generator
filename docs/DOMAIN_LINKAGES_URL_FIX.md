# Domain Linkages URL Fix Documentation
**Date**: December 16, 2025  
**Issue**: Domain linkage URLs missing required suffixes causing 404 errors  
**Scope**: 424 files with domain_linkages across all domains

## Problem Summary

All domain_linkages URLs are **incorrect and will result in 404 errors** when clicked. The URLs are missing required suffixes that match the actual file slugs.

### Critical Issues

1. **Contaminant URLs**: Missing `-contamination` suffix
   - **Current**: `/contaminants/organic-residue/adhesive/adhesive-residue`
   - **Correct**: `/contaminants/organic-residue/adhesive/adhesive-residue-contamination`
   - **Affected URLs**: 1,824 incorrect contaminant links

2. **Materials URLs**: Missing `-laser-cleaning` suffix  
   - **Current**: `/materials/stone/igneous/Granite`
   - **Correct**: `/materials/stone/igneous/granite-laser-cleaning`
   - **Affected URLs**: 1,063 incorrect materials links

3. **Case Sensitivity**: Materials URLs use incorrect capitalization
   - **Current**: `/materials/stone/igneous/Granite` (capital G)
   - **Correct**: `/materials/stone/igneous/granite-laser-cleaning` (lowercase)

## Affected Files

- **Total files with domain_linkages**: 424
- **Domains affected**: Materials (153), Contaminants (98), Settings (153), Compounds (20)
- **Total incorrect URLs**: 2,887+ (1,824 contaminant + 1,063 materials)

## Examples of Incorrect URLs

### Settings → Contaminants
```yaml
# frontmatter/settings/acrylic-pmma-settings.yaml
domain_linkages:
  related_contaminants:
    - id: adhesive-residue
      url: /contaminants/organic-residue/adhesive/adhesive-residue  # ❌ WRONG
      # Should be: /contaminants/organic-residue/adhesive/adhesive-residue-contamination
```

### Compounds → Contaminants  
```yaml
# frontmatter/compounds/acetaldehyde-compound.yaml
domain_linkages:
  produced_by_contaminants:
    - id: plastic-residue
      url: /contaminants/organic-residue/polymer/plastic-residue  # ❌ WRONG
      # Should be: /contaminants/organic-residue/polymer/plastic-residue-contamination
```

### Contaminants → Materials (hypothetical based on pattern)
```yaml
domain_linkages:
  related_materials:
    - id: granite
      url: /materials/stone/igneous/Granite  # ❌ WRONG (capitalization + missing suffix)
      # Should be: /materials/stone/igneous/granite-laser-cleaning
```

## Verification Commands

```bash
# Count incorrect contaminant URLs
grep -rh "url: /contaminants/" frontmatter/ | grep -v "\-contamination" | wc -l
# Result: 1824

# Count incorrect materials URLs  
grep -rh "url: /materials/" frontmatter/ | grep -v "laser-cleaning" | wc -l
# Result: 1063

# View sample incorrect contaminant URLs
grep -rh "url: /contaminants/" frontmatter/ | grep -v "\-contamination" | head -10

# View sample incorrect materials URLs
grep -rh "url: /materials/" frontmatter/ | grep -v "laser-cleaning" | head -10
```

## Actual File Structure

### Contaminants
```bash
frontmatter/contaminants/adhesive-residue-contamination.yaml
  slug: adhesive-residue-contamination
  category: organic-residue
  subcategory: adhesive
  → URL: /contaminants/organic-residue/adhesive/adhesive-residue-contamination
```

### Materials
```bash
frontmatter/materials/acrylic-pmma-laser-cleaning.yaml
  slug: acrylic-pmma  # Note: slug DOES NOT include -laser-cleaning
  category: plastic
  subcategory: thermoplastic
  → URL: /materials/plastic/thermoplastic/acrylic-pmma-laser-cleaning
```

**Important**: Materials have a special case where:
- **Filename** includes `-laser-cleaning`
- **Slug** does NOT include `-laser-cleaning`  
- **URL** MUST include `-laser-cleaning` suffix

## Fix Strategy

### Option 1: Automated Script (Recommended)
Create `scripts/fix-domain-linkage-urls.js` to:

1. **Find all YAML files** with `domain_linkages`
2. **For contaminant URLs**: Add `-contamination` suffix to slug portion
3. **For materials URLs**: Add `-laser-cleaning` suffix AND lowercase the slug
4. **Preserve structure**: Maintain YAML formatting, indentation, comments
5. **Verify changes**: Test sample URLs before/after

```javascript
// Pseudocode for fix script
const fixContaminantUrls = (url) => {
  // /contaminants/{cat}/{subcat}/{slug} → /contaminants/{cat}/{subcat}/{slug}-contamination
  return url.replace(
    /^(\/contaminants\/[^\/]+\/[^\/]+\/)([^\/]+)$/,
    '$1$2-contamination'
  );
};

const fixMaterialsUrls = (url) => {
  // /materials/{cat}/{subcat}/{slug} → /materials/{cat}/{subcat}/{slug-lowercase}-laser-cleaning
  return url.replace(
    /^(\/materials\/[^\/]+\/[^\/]+\/)([^\/]+)$/,
    (match, path, slug) => path + slug.toLowerCase() + '-laser-cleaning'
  );
};
```

### Option 2: Manual Fix Pattern
For each domain_linkages entry:

```yaml
# BEFORE
- id: adhesive-residue
  url: /contaminants/organic-residue/adhesive/adhesive-residue

# AFTER  
- id: adhesive-residue
  url: /contaminants/organic-residue/adhesive/adhesive-residue-contamination
```

### Option 3: External Generator Fix
If domain_linkages are **generated by external system**:
1. Update the generator to append correct suffixes
2. Regenerate all 424 frontmatter files
3. Deploy updated files

## Testing Plan

### Before Fix
```bash
# Test broken links (should 404)
curl -I http://localhost:3000/contaminants/organic-residue/adhesive/adhesive-residue
# Expected: 404 Not Found
```

### After Fix  
```bash
# Test corrected links (should 200)
curl -I http://localhost:3000/contaminants/organic-residue/adhesive/adhesive-residue-contamination
# Expected: 200 OK

# Verify materials links work
curl -I http://localhost:3000/materials/plastic/thermoplastic/acrylic-pmma-laser-cleaning
# Expected: 200 OK
```

### Visual Testing
1. Navigate to settings page: http://localhost:3000/settings/plastic/thermoplastic/acrylic-pmma-settings
2. Verify "Related Contaminants" cards display
3. Click each card link
4. Verify destination pages load (not 404)

## Implementation Steps

### Step 1: Create Fix Script
```bash
# Create script file
touch scripts/fix-domain-linkage-urls.js

# Add dependencies (if needed)
npm install --save-dev glob js-yaml
```

### Step 2: Run Fix Script
```bash
# Dry run (show what would change)
node scripts/fix-domain-linkage-urls.js --dry-run

# Apply fixes
node scripts/fix-domain-linkage-urls.js

# Verify changes
git diff frontmatter/
```

### Step 3: Test Changes
```bash
# Start dev server
npm run dev

# Test sample URLs manually or with curl
# Check domain_linkages cards render and links work
```

### Step 4: Commit Changes
```bash
git add frontmatter/
git commit -m "fix: Correct domain_linkages URLs with required suffixes

- Add -contamination suffix to contaminant URLs (1,824 fixes)
- Add -laser-cleaning suffix to materials URLs (1,063 fixes)
- Lowercase materials slugs for consistency
- Fixes 404 errors on all cross-domain relationship cards

Affects: 424 frontmatter files (Materials, Contaminants, Settings, Compounds)"
```

## Risk Assessment

### Low Risk
- **Only URL strings change** - no YAML structure modifications
- **Existing IDs unchanged** - id fields remain intact
- **Image paths unaffected** - only url fields modified
- **Reversible** - git history preserves originals

### Testing Required
- ✅ Settings pages display contaminant cards with working links
- ✅ Materials pages display relationship cards with working links
- ✅ Compounds pages display contaminant cards with working links
- ✅ All domain_linkages sections render properly
- ✅ No broken YAML after edits

## Success Criteria

1. ✅ All 1,824 contaminant URLs include `-contamination` suffix
2. ✅ All 1,063 materials URLs include `-laser-cleaning` suffix
3. ✅ All materials URLs use lowercase slugs
4. ✅ No 404 errors when clicking domain_linkages cards
5. ✅ YAML files parse without errors
6. ✅ Dev server loads all pages successfully

## Notes

- **Suffix requirement** comes from actual file naming conventions
- **Contaminants**: All files end with `-contamination.yaml`
- **Materials**: All files end with `-laser-cleaning.yaml` but slugs don't include suffix
- **URL routing** expects full slug with suffix in path
- **This affects SEO**: Broken internal links hurt crawlability

## Next Steps

1. **Decide approach**: Automated script vs external generator update
2. **Create/run fix script** if using automated approach
3. **Test thoroughly** on localhost before deploying
4. **Deploy changes** to production
5. **Verify in production** that links work correctly

## Related Files

- `scripts/fix-parentheses-in-slugs.js` - Similar pattern for slug normalization
- `app/utils/contentAPI.ts` - Content loading logic
- `app/components/DomainLinkages/DomainLinkageSection.tsx` - Card rendering component
- `FRONTMATTER_GENERATION_GUIDE_V2.md` - Cross-domain frontmatter structure
