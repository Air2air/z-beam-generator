# Frontmatter Normalization Guide

**Date**: December 14, 2025  
**Purpose**: Standardize settings and contaminants frontmatter structure to match materials format  
**Status**: Instructions for generator implementation

---

## Executive Summary

Settings and contaminants currently use a **flat structure** (all fields at top level), while materials use a **nested structure** (all fields wrapped in `metadata` property). This document provides instructions for normalizing all frontmatter to use the nested structure, eliminating conditional logic throughout the codebase.

---

## Current vs Target Structure

### Current Structure (Settings & Contaminants - FLAT)

```yaml
name: Alabaster
slug: alabaster-settings
category: stone
subcategory: sedimentary
content_type: unified_settings
schema_version: 4.0.0
active: true
title: Alabaster Laser Cleaning Settings
settings_description: ...
breadcrumb: [...]
images: {...}
machineSettings: {...}
thermalProperties: {...}
# ... all other fields at top level
```

### Target Structure (Materials - NESTED)

```yaml
metadata:
  name: Alabaster
  slug: alabaster-settings
  category: stone
  subcategory: sedimentary
  content_type: unified_settings
  schema_version: 4.0.0
  active: true
  title: Alabaster Laser Cleaning Settings
  settings_description: ...
  breadcrumb: [...]
  images: {...}
  machineSettings: {...}
  thermalProperties: {...}
  # ... all other fields nested under metadata
```

---

## Generator Instructions

### For Settings Generator

**WRAP ALL OUTPUT IN `metadata:` BLOCK**

#### Before (Current):
```yaml
name: {{ material_name }}
slug: {{ slug }}
category: {{ category }}
# ... etc
```

#### After (Target):
```yaml
metadata:
  name: {{ material_name }}
  slug: {{ slug }}
  category: {{ category }}
  # ... etc (all fields indented by 2 spaces)
```

### For Contaminants Generator

**APPLY SAME TRANSFORMATION**

#### Before (Current):
```yaml
name: {{ contaminant_name }}
slug: {{ slug }}
contaminant_type: {{ type }}
# ... etc
```

#### After (Target):
```yaml
metadata:
  name: {{ contaminant_name }}
  slug: {{ slug }}
  contaminant_type: {{ type }}
  # ... etc (all fields indented by 2 spaces)
```

---

## Implementation Steps

### Step 1: Update Generator Templates

**Settings Generator:**
1. Add `metadata:` as first line of output
2. Indent ALL generated fields by 2 spaces
3. Ensure YAML formatting remains valid

**Contaminants Generator:**
1. Add `metadata:` as first line of output
2. Indent ALL generated fields by 2 spaces
3. Ensure YAML formatting remains valid

### Step 2: Regenerate All Files

**Settings:**
```bash
# Regenerate all frontmatter/settings/*.yaml files
# with new nested structure
```

**Contaminants:**
```bash
# Regenerate all frontmatter/contaminants/*.yaml files
# with new nested structure
```

### Step 3: Update Content API Loaders

**File**: `app/utils/contentAPI.ts`

#### Update `getSettingsArticle()`

**Current:**
```typescript
export async function getSettingsArticle(slug: string) {
  // ...
  return {
    name: data.name,
    slug: data.slug,
    category: data.category,
    subcategory: data.subcategory,
    // ... extracting from top level
  };
}
```

**Target:**
```typescript
export async function getSettingsArticle(slug: string) {
  // ...
  return {
    name: data.metadata.name,
    slug: data.metadata.slug,
    category: data.metadata.category,
    subcategory: data.metadata.subcategory,
    // ... extracting from metadata property
  };
}
```

#### Update `getContaminantArticle()`

Apply same transformation - change all `data.fieldName` to `data.metadata.fieldName`

### Step 4: Remove Conditional Logic

After normalization, remove mode-based conditionals:

**File**: `app/components/CardGrid/CardGridSSR.tsx` (lines 93-102)

**Current:**
```typescript
const imageUrl = mode === 'settings' 
  ? settingsData?.images?.hero?.url
  : metadata?.images?.hero?.url;
```

**Target:**
```typescript
const imageUrl = metadata?.images?.hero?.url;
```

**File**: `app/components/ContentPages/ItemPage.tsx` (line 38)

**Current:**
```typescript
const metadata = config.type === 'settings' ? article : (article.metadata as any);
```

**Target:**
```typescript
const metadata = article.metadata as any;
```

**File**: `app/components/ContentPages/ItemPage.tsx` (line 77)

**Current:**
```typescript
metadata={config.type === 'settings' ? article as unknown as ArticleMetadata : article.metadata as unknown as ArticleMetadata}
```

**Target:**
```typescript
metadata={article.metadata as unknown as ArticleMetadata}
```

### Step 5: Testing

**Test all pages after migration:**

1. **Settings Main**: `http://localhost:3001/settings`
   - ✅ Images display correctly
   - ✅ Cards link correctly

2. **Settings Category**: `http://localhost:3001/settings/wood`
   - ✅ Category cards display
   - ✅ Images present
   - ✅ URLs correct

3. **Settings Subcategory**: `http://localhost:3001/settings/wood/hardwood`
   - ✅ Item cards display
   - ✅ Images present
   - ✅ URLs correct

4. **Settings Item**: `http://localhost:3001/settings/wood/hardwood/hickory-settings`
   - ✅ Content displays
   - ✅ Metadata correct
   - ✅ Images render

5. **Repeat for Contaminants**: Test all levels

---

## Benefits of Normalization

### 1. **Cleaner Code**
- Eliminate 4+ conditional checks based on content type
- Single code path for all content types
- Easier to maintain and debug

### 2. **Consistency**
- All frontmatter follows identical structure
- Materials, contaminants, settings work identically
- Predictable data access patterns

### 3. **Future-Proof**
- Adding new content types is simpler
- No need to add new conditionals
- Unified API surface

### 4. **Developer Experience**
- Less cognitive load (one structure to remember)
- Fewer edge cases to handle
- More intuitive code

---

## Trade-Offs

### Advantages
✅ Cleaner codebase (remove conditional logic)  
✅ Consistent structure across all content types  
✅ Easier maintenance and future additions  
✅ More predictable behavior  

### Disadvantages
⚠️ Requires regenerating all settings YAML files (~50-100 files)  
⚠️ Requires regenerating all contaminants YAML files (~30-50 files)  
⚠️ Must update getSettingsArticle and getContaminantArticle functions  
⚠️ Testing required across all pages after migration  
⚠️ One-time migration effort  

---

## Alternative: Keep Current Hybrid

**If you prefer to keep the current working solution:**

- ✅ All functionality already working
- ✅ No regeneration needed
- ✅ No code changes required
- ⚠️ Maintain conditional checks in codebase
- ⚠️ Slightly more complex code

---

## Decision Point

**Option A: Full Normalization (Recommended for Long-Term)**
- Follow all steps above
- Cleaner architecture
- One-time migration effort
- Better for future maintenance

**Option B: Keep Hybrid (Easier for Now)**
- No changes needed
- Everything works
- Accept conditional logic
- Revisit later if needed

---

## Files Affected by Normalization

### Frontmatter Files (Regenerate)
- `frontmatter/settings/*.yaml` (~50-100 files)
- `frontmatter/contaminants/*.yaml` (~30-50 files)

### Code Files (Update)
- `app/utils/contentAPI.ts` - Update getSettingsArticle, getContaminantArticle
- `app/components/CardGrid/CardGridSSR.tsx` - Remove mode conditional
- `app/components/ContentPages/ItemPage.tsx` - Remove config.type conditionals (2 locations)

### Test Files (Verify)
- All settings pages: main, category, subcategory, item
- All contaminants pages: main, category, subcategory, item
- Image display at all levels
- URL building at all levels
- Content rendering at all levels

---

## Success Criteria

After normalization is complete:

1. ✅ All settings frontmatter files have `metadata:` wrapper
2. ✅ All contaminants frontmatter files have `metadata:` wrapper
3. ✅ getSettingsArticle returns `data.metadata.*` fields
4. ✅ getContaminantArticle returns `data.metadata.*` fields
5. ✅ All conditional checks removed from code
6. ✅ All settings pages display correctly
7. ✅ All contaminants pages display correctly
8. ✅ Images display at all levels
9. ✅ URLs build correctly at all levels
10. ✅ Content renders properly on all item pages

---

## Questions?

Contact the development team with any questions about:
- Generator template modifications
- YAML structure concerns
- Testing procedures
- Migration timeline

---

**End of Normalization Guide**
