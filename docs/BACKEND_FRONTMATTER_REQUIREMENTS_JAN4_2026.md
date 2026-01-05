# Backend Frontmatter Requirements & Improvement Requests
**Date**: January 4, 2026 (Updated: January 5, 2026)  
**Audience**: Backend Development Team / Content Generation Systems  
**Purpose**: Specify required changes and improvements for automated frontmatter generation

---

## 🎯 Overview

This document specifies frontmatter field requirements, quality improvements, and structural changes needed from backend content generation systems.

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
1. ✅ Update generator to output `contentType` not `content_type`
2. ✅ Update generator to output `schemaVersion` not `schema_version`
3. ✅ Update generator to output `fullPath` not `full_path`
4. ✅ Update generator to output `pageTitle` not `page_title`
5. ✅ Update generator to output `metaDescription` not `meta_description`
6. ✅ Update generator to output `pageDescription` not `page_description`
7. ✅ Keep `machine_settings` as snake_case (domain data, not software metadata)
8. ✅ Regenerate ALL frontmatter files (600+ files)

**Verification**: Run `npm test` - Type Safety test will pass when fixed

**Important**: See "Field Naming Rules" section below for complete snake_case vs camelCase guide

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

### 3. **display_name → displayName (Compounds)**
**Priority**: 🟡 MEDIUM  
**Files Affected**: ~50 compound files  
**Current State**: Using snake_case for software field  

```yaml
# ❌ Current (Inconsistent)
display_name: Ammonia (NH₃)

# ✅ Required (Consistent camelCase)
displayName: Ammonia (NH₃)
```

**Action Required**:
1. Update generation code: `display_name` → `displayName`
2. Regenerate all compound files with corrected field name

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

#### Settings
```yaml
# Machine Parameters (Domain Data)
machine_settings:            # ✅ snake_case (equipment/parameter data)
  pulse_duration: number
  beam_diameter: number
  scanning_speed: number
  # ... other machine parameters
```

---

## ⚠️ Field Naming Rules: snake_case vs camelCase

**Critical Distinction**: Software metadata uses camelCase, domain/scientific data uses snake_case

### ✅ Use camelCase (Software/Metadata Fields):
These are **software concerns** - routing, SEO, system metadata:
- `contentType` - System classification
- `schemaVersion` - Data schema version
- `fullPath` - URL routing
- `pageTitle` - SEO/display title
- `metaDescription` - SEO meta tag
- `pageDescription` - Page content
- `datePublished` - Timestamp
- `dateModified` - Timestamp
- `displayName` - UI display (compounds)

### ✅ Use snake_case (Scientific/Domain Fields):
These are **domain-specific data** - scientific, technical, regulatory:
- `machine_settings` - Equipment parameters (Settings)
- `chemical_formula` - Scientific notation (NH₃, H₂O)
- `cas_number` - CAS Registry standard
- `molecular_weight` - Scientific measurement
- `exposure_limits` - OSHA/NIOSH regulatory standard
- `hazard_class` - GHS classification standard
- `pulse_duration` - Technical parameter
- `beam_diameter` - Technical parameter
- `scanning_speed` - Technical parameter

### 🎯 Rule of Thumb:
```
IF field affects software behavior (routing, SEO, UI) → camelCase
IF field represents domain knowledge (science, tech specs) → snake_case
```

### ✅ Examples (Correct Usage):
```yaml
# Settings file
contentType: settings              # ✅ Software metadata (camelCase)
schemaVersion: 5.0.0              # ✅ Software metadata (camelCase)
machine_settings:                 # ✅ Domain data (snake_case)
  pulse_duration: 100             # ✅ Technical spec (snake_case)
  beam_diameter: 1.5              # ✅ Technical spec (snake_case)

# Compound file
contentType: compound             # ✅ Software metadata (camelCase)
displayName: Ammonia (NH₃)        # ✅ Software metadata (camelCase)
chemical_formula: NH₃             # ✅ Scientific data (snake_case)
cas_number: 7664-41-7            # ✅ Registry standard (snake_case)
exposure_limits:                  # ✅ Regulatory data (snake_case)
  osha_pel_ppm: 50               # ✅ Regulatory standard (snake_case)
```

### ❌ Examples (Incorrect Usage):
```yaml
# ❌ WRONG: Software field in snake_case
content_type: settings            # Should be: contentType
schema_version: 5.0.0            # Should be: schemaVersion
full_path: /settings/aluminum    # Should be: fullPath

# ❌ WRONG: Domain field in camelCase
machineSettings:                  # Should be: machine_settings
  pulseDuration: 100             # Should be: pulse_duration
chemicalFormula: NH₃             # Should be: chemical_formula
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
| camelCase field names | 🔴 CRITICAL | 600+ | 8-10 hours | 308 test failures + industry standard |
| metaDescription quality | 🔴 HIGH | 153 | 2-3 hours | High SEO impact |
| display_name → displayName | 🟡 MEDIUM | 50 | 30 mins | Consistency |
| Static pages meta_description | 🟡 MEDIUM | 7 | 15 mins | Consistency |
| pageTitle optimization | 🟢 LOW | 442 | 4-6 hours | Moderate SEO |
| micro quality | 🟢 LOW | 306 | Ongoing | Content quality |
| Breadcrumb hrefs | 🟢 LOW | ~50 | 30 mins | URL consistency |

---

## 🧪 Verification Commands

After making changes, verify with automated tests:

```bash
# Run full test suite (all 2891 tests)
npm run test:all

# Run specific validation tests
npm run validate:naming          # Check naming conventions
npm run validate:frontmatter     # Validate YAML structure
npm run validate:types           # Check TypeScript type imports

# Integration tests (verify camelCase compliance)
npm test tests/integration/yaml-typescript-integration.test.ts

# Expected result after fixes:
# ✅ 2663+ tests passing
# ✅ Type Safety test passes (0 violations)
# ✅ No snake_case violations in frontmatter files
```

**Success Indicators**:
- ✅ "should use camelCase for software fields" test passes
- ✅ No "content_type (should be camelCase: contentType)" violations
- ✅ No "schema_version (should be camelCase: schemaVersion)" violations

---

## 🚀 Recommended Implementation Order

### Phase 1: Critical Fixes (Week 1) - Estimated 10-12 hours
1. ✅ **Convert all fields to camelCase** (8-10 hours)
   - Update generator: `content_type` → `contentType`
   - Update generator: `schema_version` → `schemaVersion`
   - Update generator: `full_path` → `fullPath`
   - Update generator: `page_title` → `pageTitle`
   - Update generator: `meta_description` → `metaDescription`
   - Update generator: `page_description` → `pageDescription`
   - Regenerate 600+ files (materials, contaminants, compounds, settings)
   - **Verify**: Run `npm test` - Type Safety test should pass (0 violations)
2. ✅ Fix metaDescription generation template (1-2 hours)
   - Eliminate "removes oxide removal" grammatical error
   - Enforce 120-155 character limit
   - Prevent mid-sentence line breaks
3. ✅ Regenerate all 153 settings metaDescription
4. ✅ Update display_name → displayName in compounds
5. ✅ Update static pages meta_description → metaDescription

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
- ✅ All 600+ files use camelCase for software fields (contentType, schemaVersion, etc.)
- ✅ Test suite shows: 2663+ passing, 0 snake_case violations
- ✅ All 153 settings have grammatically correct metaDescriptions (120-155 chars)
- ✅ All compounds use `displayName` (not `display_name`)
- ✅ All static pages use `metaDescription` (not `meta_description`)
- ✅ All breadcrumb hrefs use hyphens (not underscores)

**Automated Verification**:
```bash
npm run test:all  # Must pass with 0 Type Safety violations
```

**Overall Success**:
- 100% naming consistency (camelCase for software, snake_case for scientific)
- 100% metaDescription quality (no grammar errors, proper length)
- Improved SEO performance (measurable in Google Search Console)
- Clean, maintainable frontmatter structure
