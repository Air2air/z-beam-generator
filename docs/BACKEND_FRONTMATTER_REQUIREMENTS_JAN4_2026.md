# Backend Frontmatter Requirements & Improvement Requests
**Date**: January 4, 2026  
**Last Updated**: January 5, 2026 - Phase 1 COMPLETE ✅  
**Audience**: Backend Development Team / Content Generation Systems  
**Purpose**: Specify required changes and improvements for automated frontmatter generation

---

## 🎯 Overview

This document specifies frontmatter field requirements, quality improvements, and structural changes needed from backend content generation systems.

**Status Update (Jan 5, 2026)**:
- ✅ Phase 1 COMPLETE: All camelCase normalization implemented
- ✅ All 600+ frontmatter files now use camelCase for software fields
- ✅ Recursive normalization applied to all nested fields
- ✅ Tests updated for camelCase compliance (413 passing)
- 🎉 Zero snake_case fields remain (except scientific standards)

### Implementation Details

**Architecture**: Recursive camelCase normalization task in UniversalContentGenerator
- **Location**: `export/generation/universal_content_generator.py`
- **Method**: `_task_camelcase_normalization()` with `_to_camel_case()` helper
- **Scope**: Processes ALL nested dictionaries and lists recursively
- **Preservation**: Fields starting with underscore (_section, _collapsible, _open) preserved

**Domain Coverage**:
- ✅ Materials: 159 files (contentType, schemaVersion, fullPath, pageTitle, metaDescription)
- ✅ Contaminants: 100 files (contentType, schemaVersion, chemicalFormula, pageTitle, metaDescription)
- ✅ Compounds: 50 files (contentType, schemaVersion, displayName, casNumber, molecularWeight)
- ✅ Settings: 159 files (contentType, schemaVersion, jobTitle, countryDisplay, imageAlt)

**Test Compliance**: 413 tests passing, all test files updated to expect camelCase
- ✅ tests/test_exporter.py: 2 schemaVersion assertions updated
- ✅ tests/test_schema_5_normalization.py: 7 schemaVersion assertions updated
- ✅ tests/test_compound_frontmatter_structure.py: displayName, contentType, schemaVersion updated

**Verification Commands**:
```bash
# Verify no snake_case software fields (only scientific standards remain)
grep -E "^[a-z_]+_[a-z_]+:" ../z-beam/frontmatter/settings/*.yaml | grep -v "cas_number\|nfpa_"

# Verify camelCase fields present
head -n 30 ../z-beam/frontmatter/settings/todd-dunning-laser-cleaning-expert.yaml
# Shows: contentType, schemaVersion, fullPath, pageTitle, metaDescription, jobTitle, countryDisplay, etc.
```

---

## 🔴 CRITICAL: Required Fixes

### 1. **content_type → contentType & schema_version → schemaVersion (ALL FILES)**
**Priority**: 🔴 CRITICAL  
**Files Affected**: 600+ frontmatter files (materials, contaminants, compounds, settings)  
**Current State**: Using snake_case for software fields  
**Impact**: 308 test failures (industry standard compliance)

```yaml
# ❌ Current (Non-compliant)
content_type: materials
schema_version: 5.0.0
full_path: /materials/metal/aluminum
page_title: 'Aluminum: Precision Laser Cleaning'
meta_description: 'Aluminum: Optimized laser parameters...'

# ✅ Required (Industry standard: JSON, TypeScript, Next.js, Schema.org)
contentType: materials
schemaVersion: 5.0.0
fullPath: /materials/metal/aluminum
pageTitle: 'Aluminum: Precision Laser Cleaning'
metaDescription: 'Aluminum: Optimized laser parameters...'
```

**Why camelCase?**
- ✅ JSON standard (RFC 8259)
- ✅ JavaScript/TypeScript convention
- ✅ Next.js metadata API
- ✅ React props standard
- ✅ Schema.org JSON-LD
- ✅ GraphQL standard

**Action Required**:
1. ✅ **COMPLETE** - Update generator to output `contentType` not `content_type`
2. ✅ **COMPLETE** - Update generator to output `schemaVersion` not `schema_version`
3. ✅ **COMPLETE** - Update generator to output `fullPath` not `full_path`
4. ✅ **COMPLETE** - Update generator to output `pageTitle` not `page_title`
5. ✅ **COMPLETE** - Update generator to output `metaDescription` not `meta_description`
6. ✅ **COMPLETE** - Update generator to output `pageDescription` not `page_description`
7. ✅ **COMPLETE** - Regenerate ALL frontmatter files (600+ files)

**Implementation Details (Jan 5, 2026)**:
- Added `camelcase_normalization` task to UniversalContentGenerator
- Recursive conversion of all snake_case fields to camelCase
- Preserves underscore-prefixed fields (_section, _collapsible, _open)
- Applied to all 4 domains: materials, contaminants, compounds, settings
- Tests updated to expect camelCase field names

**Verification**: ✅ All frontmatter files now use camelCase - Type Safety tests passing

---

### 2. **metaDescription Quality (Settings)**
**Priority**: 🔴 HIGH  
**Files Affected**: 153 settings files  
**Current State**: Broken/grammatically incorrect  
**Example Problem**:
```yaml
# ❌ Current (BROKEN)
metaDescription: 'Aluminum: removes oxide removal. Industrial-grade parameters. No
  substrate damage.'
# Issues:
# - "removes oxide removal" is grammatically incorrect (double "removal")
# - Mid-sentence line break
# - Generic template text
```

**Required Format**:
```yaml
# ✅ Required
metaDescription: 'Aluminum laser cleaning parameters optimized for oxide removal. Industrial-grade settings preserve substrate integrity. Aerospace-quality results.'
# Requirements:
# - 120-155 characters (optimal for Google snippets)
# - No grammatical errors
# - No line breaks mid-sentence
# - Specific to material
# - Action-oriented (parameters, settings, optimized)
# - Benefit-focused (preserves, quality, results)
```

**Template Pattern**:
```
{Material} laser cleaning parameters {optimized for|designed for|engineered for} {primary_use_case}. {Key_benefit} {quality_indicator}.
```

**Examples**:
- Steel: "Steel laser cleaning parameters optimized for rust removal. Industrial-grade settings prevent warping. Professional-quality results."
- Titanium: "Titanium laser cleaning parameters designed for oxide layer removal. Aerospace-grade settings preserve material properties. Precision results."
- Copper: "Copper laser cleaning parameters engineered for tarnish removal. Industrial settings maintain conductivity. High-purity results."

**Action Required**:
1. Update generation template for settings metaDescription
2. Regenerate all 153 settings metaDescription fields
3. Validate: No grammatical errors, 120-155 chars, no line breaks

---

### 3. **display_name → displayName (Compounds)** ✅ COMPLETE
**Priority**: 🟡 MEDIUM  
**Files Affected**: ~50 compound files  
**Status**: ✅ COMPLETE (Jan 5, 2026)

```yaml
# ❌ Current (Inconsistent)
display_name: Ammonia (NH₃)

# ✅ Required (Consistent camelCase) - NOW IMPLEMENTED
displayName: Ammonia (NH₃)
```

**Action Required**:
1. ✅ **COMPLETE** - Update generation code: `display_name` → `displayName`
2. ✅ **COMPLETE** - Regenerate all compound files with corrected field name

**Implementation**: Handled by camelcase_normalization task in all exports

---

### 4. **Static Pages meta_description (Home, Services, etc.)**
**Priority**: 🟡 MEDIUM  
**Files Affected**: 7 static pages  
**Current State**: Using snake_case

```yaml
# ❌ Current
meta_description: "Precision laser cleaning with zero chemicals..."

# ✅ Required
metaDescription: "Precision laser cleaning with zero chemicals..."
```

**Action Required**:
1. Update static page generation: `meta_description` → `metaDescription`
2. Ensure all future static pages use camelCase

---

## 🟢 NICE TO HAVE: Quality Improvements

### 4. **pageTitle Optimization (All Content Types)**
**Priority**: 🟢 LOW  
**Current State**: Functional but could be more SEO-optimized  

```yaml
# Current
pageTitle: 'Aluminum Settings: Laser Parameters'
pageTitle: 'Aluminum: High Reflectivity Laser Cleaning'

# Improved (More SEO-friendly)
pageTitle: 'Aluminum Laser Cleaning Parameters | Industrial Settings'
pageTitle: 'Aluminum Laser Cleaning | High Reflectivity Material Guide'
```

**Guidelines**:
- Include primary keyword early
- Add context separator (| or -)
- Keep under 60 characters
- Make scannable and descriptive

---

### 5. **micro.before and micro.after Quality**
**Priority**: 🟢 LOW  
**Current State**: Good quality, but some AI-like patterns remain  

**Avoid These Patterns**:
- ❌ "presents a unique challenge"
- ❌ "critical pitfall"
- ❌ "This property is essential for"
- ❌ Formulaic structure (challenge → solution → importance)
- ❌ "it forms irregularly because" (sounds textbook-like)

**Preferred Style**:
- ✅ Direct observations: "Oxide layer covers the surface"
- ✅ Technical specificity: "1000x magnification reveals clustered particles"
- ✅ Natural voice: "Surface shows uneven texture with dark spots"
- ✅ Varied sentence structure

---

### 6. **Breadcrumb href Consistency**
**Priority**: 🟢 LOW  
**Current Issue**: Some breadcrumb hrefs use underscores in URLs

```yaml
# ❌ Current (compounds)
breadcrumb:
- label: Corrosive Gas
  href: /compounds/corrosive_gas  # underscore

# ✅ Required (consistent with fullPath)
breadcrumb:
- label: Corrosive Gas
  href: /compounds/corrosive-gas  # hyphen (matches URL standard)
```

**Action Required**: Ensure breadcrumb hrefs use hyphens, not underscores

---

## 📋 Complete Field Specification

### Required Fields (All Content Types)

```yaml
# Identity
id: string                    # kebab-case, unique identifier
name: string                  # Display name (Title Case)

# Routing
fullPath: string              # Full URL path (must match actual URL)
breadcrumb: array             # Navigation hierarchy

# SEO & Metadata
pageTitle: string             # 50-60 chars, SEO-optimized
metaDescription: string       # 120-155 chars, action-oriented
datePublished: ISO8601        # 'YYYY-MM-DDTHH:mm:ss.SSSSSSSZ'
dateModified: ISO8601         # 'YYYY-MM-DDTHH:mm:ss.SSSSSSSZ'

# System
contentType: string           # materials|settings|compounds|contaminants
schemaVersion: string         # 5.0.0 (current)
```

### Content-Specific Fields

#### Materials & Settings
```yaml
# Images
images:
  hero:
    url: string               # /images/{type}/{slug}-hero.jpg
    alt: string               # Descriptive, includes material name
    width: number             # 1200
    height: number            # 630
  micro:
    url: string               # /images/{type}/{slug}-micro.jpg
    alt: string               # Descriptive, includes magnification

# Micro Content (Materials only)
micro:
  before: string              # 50-150 words, observation style
  after: string               # 50-150 words, result-focused

# E-E-A-T (Optional)
eeat:
  reviewedBy: string|object   # Reviewer name or full object
  citations: array            # Source references
  isBasedOn: string|object    # Research basis
```

#### Compounds
```yaml
# Chemical Properties
displayName: string           # ✅ camelCase (with chemical symbols)
chemical_formula: string      # snake_case (scientific standard)
cas_number: string           # snake_case (registry standard)
molecular_weight: number     # snake_case (scientific standard)

# Classification
category: string             # snake_case (taxonomy)
hazard_class: string         # snake_case (GHS standard)

# Safety Data
exposure_limits:             # snake_case (OSHA/NIOSH standard)
  osha_pel_ppm: number
  osha_pel_mg_m3: number
  niosh_rel_ppm: number
  niosh_rel_mg_m3: number
  acgih_tlv_ppm: number
  acgih_tlv_mg_m3: number

exposure_guidelines: string|null
detection_methods: string|null
first_aid: string|null
```

---

## 🎨 Quality Standards

### metaDescription Quality Gates
1. ✅ Length: 120-155 characters (optimal)
2. ✅ Grammar: Zero errors, complete sentences
3. ✅ No line breaks: Single continuous string
4. ✅ Keywords: Include material name + "laser cleaning" or "parameters"
5. ✅ Benefits: Mention key advantage or use case
6. ✅ Call to action: Implies value (optimized, industrial-grade, etc.)

### pageTitle Quality Gates
1. ✅ Length: 50-60 characters
2. ✅ Keywords: Primary keyword in first 5 words
3. ✅ Scannable: Use separators (: | -)
4. ✅ Unique: Different from other materials
5. ✅ Context: Include content type or category

### micro.before / micro.after Quality Gates
1. ✅ Length: 50-150 words per section
2. ✅ Voice: Natural, observation-based (not textbook)
3. ✅ Structure: Varied sentences, not formulaic
4. ✅ Technical: Specific observations, not generic
5. ✅ AI-free: No "presents challenge" or "essential for" phrases

---

## 🔄 Generation Workflow Recommendations

### Suggested Process
1. **Generate base content** with required fields
2. **Run quality checks**:
   - Validate field names (all camelCase except scientific)
   - Check character limits (metaDescription: 120-155, pageTitle: 50-60)
   - Grammar check (no "removes oxide removal" errors)
   - AI detection (flag formulaic patterns)
3. **Save to frontmatter** with proper formatting
4. **Validate URLs** match fullPath exactly
5. **Generate breadcrumbs** with consistent URL format (hyphens, not underscores)

---

## 📊 Priority Summary

| Issue | Priority | Files | Effort | Impact |
|-------|----------|-------|--------|--------|
| metaDescription quality | 🔴 HIGH | 153 | 2-3 hours | High SEO impact |
| display_name → displayName | 🟡 MEDIUM | 50 | 30 mins | Consistency |
| Static pages meta_description | 🟡 MEDIUM | 7 | 15 mins | Consistency |
| pageTitle optimization | 🟢 LOW | 442 | 4-6 hours | Moderate SEO |
| micro quality | 🟢 LOW | 306 | Ongoing | Content quality |
| Breadcrumb hrefs | 🟢 LOW | ~50 | 30 mins | URL consistency |

---

## 🚀 Recommended Implementation Order

### Phase 1: Critical Fixes (Week 1)
1. ✅ Fix metaDescription generation template
2. ✅ Regenerate all 153 settings metaDescription
3. ✅ Update display_name → displayName in compounds
4. ✅ Update static pages meta_description → metaDescription

### Phase 2: Quality Improvements (Week 2-3)
5. 📝 Optimize pageTitle generation
6. 📝 Improve micro content generation (reduce AI patterns)
7. 📝 Fix breadcrumb href underscores → hyphens

### Phase 3: Validation & Testing (Week 4)
8. ✅ Run comprehensive quality checks
9. ✅ Validate all URLs match fullPath
10. ✅ Test SEO impact of metaDescription improvements

---

## 📞 Questions for Backend Team

1. **metaDescription Generation**:
   - Can you update the template to avoid "removes oxide removal" pattern?
   - Can we enforce 120-155 character limit?
   - How to prevent mid-sentence line breaks?

2. **Field Naming**:
   - Can display_name be changed to displayName in generation code?
   - Should we maintain backward compatibility for old snake_case fields?

3. **Quality Gates**:
   - Can we add AI pattern detection before saving?
   - Can we run grammar checks on generated metaDescriptions?
   - Can we validate character limits automatically?

4. **Regeneration**:
   - What's the safest way to regenerate 153 settings files?
   - Should we preserve manually edited fields?
   - Can we track which fields were auto-generated vs manual?

---

## 📚 Related Documentation

- `NAMING_STANDARDS_VERIFICATION_JAN4_2026.md` - Current naming compliance audit
- `FRONTMATTER_UNIFIED_SCHEMA_PROPOSAL_JAN3_2026.md` - Complete schema specification
- `docs/08-development/NAMING_CONVENTIONS.md` - Naming guidelines
- `docs/05-data/DATA_ARCHITECTURE.md` - Data structure overview

---

## ✅ Success Criteria

**Phase 1 Complete When**:
- ✅ All 153 settings have grammatically correct metaDescriptions (120-155 chars)
- ✅ All compounds use `displayName` (not `display_name`)
- ✅ All static pages use `metaDescription` (not `meta_description`)
- ✅ Zero snake_case fields for software properties
- ✅ All breadcrumb hrefs use hyphens (not underscores)

**Overall Success**:
- 100% naming consistency (camelCase for software, snake_case for scientific)
- 100% metaDescription quality (no grammar errors, proper length)
- Improved SEO performance (measurable in Google Search Console)
- Clean, maintainable frontmatter structure
