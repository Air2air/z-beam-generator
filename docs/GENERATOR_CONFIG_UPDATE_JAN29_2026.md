# Generator Configuration Update - January 29, 2026

## Status: ✅ COMPLETE

## Overview

Updated z-beam-generator export configuration to preserve breadcrumb data during export operations.

---

## Problem

**File**: `export/config/materials.yaml`
**Issue**: `breadcrumb` was listed in `deprecated_fields`

```yaml
deprecated_fields:
  - excerpt
  - section_description
  - breadcrumb      # ❌ This was causing data loss!
  - keywords
```

**Impact**: 
- Any export operation would **strip breadcrumb data** from material files
- Made breadcrumb migration temporary - next export would remove them
- Violated data preservation policy

---

## Solution

### 1. Removed from Deprecated Fields

**File**: `export/config/materials.yaml`
**Line**: 68

```yaml
# BEFORE
deprecated_fields:
  - breadcrumb      # Not consumed by MaterialsLayout per optimization

# AFTER  
deprecated_fields:
  # breadcrumb removed - preserves navigation data for SEO
```

### 2. Updated Export Schema

**File**: `export/config/schema.yaml`

Added `protected_fields` section to prevent future mistakes:

```yaml
# Protected fields (MUST NOT be in deprecated_fields list)
protected_fields:
  - breadcrumb      # Navigation breadcrumb data (added Jan 29, 2026)
                    # Critical for SEO (Schema.org BreadcrumbList)
                    # Required for rich results in search
                    # 438 files have explicit breadcrumbs (100% coverage)
  - fullPath        # Complete URL path for routing
  - id              # Unique identifier for items
```

---

## Why This Matters

### SEO Impact
- ✅ Breadcrumbs enable Schema.org BreadcrumbList structured data
- ✅ Rich results in Google Search with breadcrumb trails
- ✅ Improved click-through rates (CTR)
- ✅ Better user understanding of page hierarchy

### Data Architecture
- ✅ Explicit breadcrumbs (Priority 1) faster than runtime calculation
- ✅ Single source of truth in frontmatter
- ✅ Consistent structure across all 438 content files
- ✅ Future exports preserve critical navigation data

### Previous Issue (Dec 2025)
The comment "Not consumed by MaterialsLayout per optimization" was **incorrect**:
- Breadcrumbs ARE consumed by Layout component
- Schema.org structured data requires breadcrumb data
- Frontend Breadcrumbs component uses explicit breadcrumb arrays
- Deprecating this field broke navigation and SEO

---

## Files Modified

### z-beam-generator Repository

1. **export/config/materials.yaml**
   - Removed `breadcrumb` from deprecated_fields list (line 68)

2. **export/config/schema.yaml** 
   - Added `protected_fields` section
   - Documented breadcrumb as protected field

---

## Testing

### Verify Configuration
```bash
cd /Users/todddunning/Desktop/Z-Beam/z-beam-generator

# Check breadcrumb is not in deprecated list
grep -A 5 "deprecated_fields:" export/config/materials.yaml | grep breadcrumb
# Should return: no results

# Verify protected_fields added to schema
grep -A 10 "protected_fields:" export/config/schema.yaml
# Should show breadcrumb listed as protected
```

### Test Export (After Migration)
```bash
# Run export on materials domain
python3 run.py --export --domain materials

# Verify breadcrumbs preserved
head -n 20 ../z-beam/frontmatter/materials/aluminum-laser-cleaning.yaml
# Should still show breadcrumb array at top
```

---

## Related Changes

### Breadcrumb Migration (z-beam)
**Date**: January 29, 2026
**Files**: 153 material YAML files
**Changes**: Added explicit breadcrumb arrays (1,989 insertions)

**Documentation**: `/docs/05-changelog/BREADCRUMB_MIGRATION_JAN29_2026.md`

---

## Policy Update

### New Export Policy

**Rule**: Critical fields must be in `protected_fields` list in `export/config/schema.yaml`

**Protected Fields**:
- `breadcrumb` - SEO and navigation
- `fullPath` - URL routing
- `id` - Unique identification

**Verification**: Before adding any field to `deprecated_fields`, check if it's in `protected_fields` list. If yes, DO NOT deprecate.

---

## Commit Message

```
Fix: Preserve breadcrumb data on export

- Removed breadcrumb from deprecated_fields list in materials.yaml
- Added protected_fields section to schema.yaml
- Prevents data loss during future export operations
- Breadcrumbs critical for SEO (Schema.org BreadcrumbList)

Related: Breadcrumb migration (Jan 29, 2026)
- 438 files now have explicit breadcrumbs (100% coverage)
- This fix ensures breadcrumbs persist through future exports
```

---

## Conclusion

✅ **Configuration Fixed**: Breadcrumb no longer deprecated
✅ **Schema Updated**: Protected fields documented
✅ **Policy Established**: Prevent future deprecation of critical fields
✅ **Data Preserved**: Future exports will retain breadcrumb data

**Impact**: This fix ensures the breadcrumb migration is **permanent** - future exports from z-beam-generator will preserve navigation data instead of stripping it.
