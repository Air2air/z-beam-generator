# Frontmatter Reorganization Required - Backend AI Assistant Guide

**Date**: January 14, 2026  
**Status**: ACTIONABLE - Backend must reorganize frontmatter structure  
**Priority**: HIGH - Affects maintainability and data consistency  
**Scope**: All frontmatter files (materials, contaminants, compounds)

---

## 🚨 Current Problems Identified

### Problem 1: Scattered Core Metadata
**Issue**: Critical metadata fields are spread throughout the file instead of grouped logically.

**Current (BAD)**:
```yaml
id: aluminum-laser-cleaning          # Line 1
name: Aluminum                        # Line 2
# ... 720 lines of content ...
datePublished: '2026-01-06'          # Line 725
dateModified: '2026-01-14'           # Line 726
contentType: material                # Line 727
schemaVersion: 5.0.0                 # Line 728
```

**Impact**: Hard to find metadata, violates "most important info first" principle.

---

### Problem 2: Duplicate/Legacy Fields
**Issue**: Same content stored in multiple locations with different naming conventions.

**Duplicates Found**:
```yaml
# DUPLICATE 1: Micro content (3 locations!)
micro: 'BEFORE: Laser cleaning...'                    # Line 41
components.micro: 'BEFORE: Laser cleaning...'         # Line 814
components: 
  micro: ...                                          # Line 743

# DUPLICATE 2: Material characteristics (3 versions!)
properties:
  materialCharacteristics:
    description: "When working with aluminum..."      # Lines 6-40
materialCharacteristics_description: "When laser..."  # Line 801
properties.materialCharacteristics.description: "..." # Line 808

# DUPLICATE 3: Laser interaction (3 versions!)
properties:
  laserMaterialInteraction:
    description: "Laser energy interacts..."          # Lines 25-40
laserMaterialInteraction_description: "When laser..." # Line 804
properties.laserMaterialInteraction.description: "..." # Line 811

# DUPLICATE 4: Related materials (2 locations)
related_materials: []                                 # Line 807
relationships.relatedMaterials: "When you're..."      # Line 819
```

**Impact**: 
- Wastes storage space (841 lines could be ~600)
- Creates confusion about which field is canonical
- Risk of inconsistent data between duplicates
- Harder to maintain and update

---

### Problem 3: Illogical Field Grouping
**Issue**: Related fields are separated by hundreds of lines.

**Current Order (BAD)**:
```yaml
1-5:    Core ID (id, name, category) ✅
6-40:   Properties (good location) ✅
41-45:  Micro content ❌ (should be with components)
46-56:  Images ❌ (should be near top for quick access)
57-679: Relationships (huge section) ⚠️
680-711: Author ❌ (should be near top)
712-724: Card settings ❌ (should be near SEO)
725-728: Core metadata ❌ (should be at top!)
729-742: Contamination taxonomy ⚠️
743-784: Components ✅
785-793: E-E-A-T ❌ (should be with author)
794-796: FAQ ✅
797-820: Legacy/duplicate fields ❌ (DELETE)
```

**Impact**: Hard to navigate, find, and maintain fields.

---

### Problem 4: Legacy Fields Not Removed
**Issue**: Old snake_case fields from previous schema versions still present.

**Legacy Fields to DELETE**:
```yaml
materialCharacteristics_description          # Superseded by properties.materialCharacteristics
laserMaterialInteraction_description         # Superseded by properties.laserMaterialInteraction
properties.materialCharacteristics.description  # Duplicate of nested structure
properties.laserMaterialInteraction.description # Duplicate of nested structure
relationships.relatedMaterials               # Text field, should be structured array
```

---

## ✅ Recommended Frontmatter Structure

### Canonical Field Order

```yaml
# ============================================================================
# SECTION 1: CORE IDENTIFICATION (Lines 1-10)
# ============================================================================
id: aluminum-laser-cleaning
name: Aluminum
displayName: Aluminum Laser Cleaning
category: metal
subcategory: non-ferrous

# ============================================================================
# SECTION 2: CONTENT METADATA (Lines 11-20)
# ============================================================================
contentType: material
schemaVersion: 5.0.0
datePublished: '2026-01-06T00:00:00.000Z'
dateModified: '2026-01-14T08:29:17.458963+00:00'
fullPath: /materials/metal/non-ferrous/aluminum-laser-cleaning

# ============================================================================
# SECTION 3: SEO & PAGE PRESENTATION (Lines 21-35)
# ============================================================================
pageTitle: Aluminum
metaDescription: >
  Laser cleaning process starts on aluminum surface...
card:
  title: Aluminum Laser Cleaning
  description: >
    Expert guide on laser cleaning aluminum...
  image: /images/material/aluminum-laser-cleaning-hero.jpg
  badge:
    text: Non-Ferrous
    variant: blue

# ============================================================================
# SECTION 4: AUTHOR & EXPERTISE (Lines 36-60)
# ============================================================================
author:
  name: Dr. Sarah Mitchell
  credentials: Ph.D. in Materials Engineering
  affiliations:
    - International Laser Safety Institute
    - Society of Manufacturing Engineers
  yearsExperience: 15
  specializations:
    - Laser processing of non-ferrous metals
    - Industrial surface treatment
  bio: >
    Dr. Sarah Mitchell specializes in laser surface treatment...
  
eeat:
  experience: 15+ years in laser materials processing
  expertise: Ph.D. Materials Engineering, 50+ peer-reviewed publications
  authoritativeness: Keynote speaker at 10+ international conferences
  trustworthiness: ISO 9001 certified processes, third-party verified methods

# ============================================================================
# SECTION 5: MEDIA ASSETS (Lines 61-75)
# ============================================================================
images:
  hero:
    url: /images/material/aluminum-laser-cleaning-hero.jpg
    alt: Aluminum surface undergoing laser cleaning showing precise contamination removal
    width: 1200
    height: 630
  micro:
    url: /images/material/aluminum-laser-cleaning-micro.jpg
    alt: Aluminum microscopic view showing detailed contamination removal
    width: 800
    height: 600

# ============================================================================
# SECTION 6: CONTENT COMPONENTS (Lines 76-150)
# ============================================================================
components:
  micro: >
    BEFORE: Laser cleaning of aluminum removes surface oxides...
    AFTER: Aluminum surface exhibits improved smoothness after treatment...

properties:
  materialCharacteristics:
    title: Aluminum's Distinctive Traits
    description: >
      When working with aluminum, a non-ferrous metal known for...
    _metadata:
      icon: wrench
      order: 70
      variant: default
      generatedAt: '2026-01-14T08:26:41.000Z'
  
  laserMaterialInteraction:
    title: Aluminum Laser Interaction Dynamics
    description: >
      Laser energy interacts with aluminum by primarily reflecting...
    _metadata:
      icon: zap
      order: 71
      variant: default
      generatedAt: '2026-01-14T08:27:32.000Z'

faq: >
  Q: Question 1: What safety considerations should we keep in mind...
  A: Professionals often deal with aluminum's shiny and reflective surface...

# ============================================================================
# SECTION 7: RELATIONSHIPS (Lines 151-650)
# ============================================================================
relationships:
  interactions:
    contaminatedBy:
      presentation: card
      items:
        - id: adhesive-residue-contamination
          name: Adhesive Residue / Tape Marks
          # ... (keep all relationship data)
      _section:
        sectionTitle: Common Contaminants
        sectionDescription: >
          Contaminants frequently encountered on aluminum surfaces...
        icon: droplet
        order: 1
        variant: default
  
  operational:
    industryApplications:
      presentation: card
      items:
        - id: aerospace-manufacturing
          name: Aerospace Component Cleaning
          # ... (keep all industry applications)
      _section:
        sectionTitle: Industry Applications
        sectionDescription: >
          Key industries and applications for aluminum laser cleaning...
        icon: building
        order: 1
        variant: default
  
  safety:
    regulatoryStandards:
      presentation: card
      items:
        - id: ansi-z136
          name: ANSI Z136.1 Safe Use of Lasers
          # ... (keep all standards)
      _section:
        sectionTitle: Safety & Regulatory Compliance
        sectionDescription: >
          Essential safety standards and regulations...
        icon: shield-check
        order: 1
        variant: default

# ============================================================================
# SECTION 8: TAXONOMY (Lines 651-680) - Optional/Legacy
# ============================================================================
contamination:
  description: >
    Aluminum surfaces commonly accumulate various contaminants...
  prevalence:
    - type: organic
      frequency: high
      impact: moderate
```

---

## 🗑️ Fields to DELETE Immediately

**These fields are duplicates or legacy - REMOVE from all frontmatter files:**

```yaml
# DELETE - Superseded by properties.materialCharacteristics
materialCharacteristics_description

# DELETE - Superseded by properties.laserMaterialInteraction  
laserMaterialInteraction_description

# DELETE - Duplicate of properties.materialCharacteristics.description
properties.materialCharacteristics.description

# DELETE - Duplicate of properties.laserMaterialInteraction.description
properties.laserMaterialInteraction.description

# DELETE - Should be structured array in relationships, not text
relationships.relatedMaterials

# DELETE - Duplicate of components.micro
micro: 'BEFORE: ...'  # (when it appears at root level)

# DELETE - Empty/unused arrays
related_materials: []
```

---

## 📋 Implementation Checklist for Backend

### Phase 1: Structural Reorganization
- [ ] Reorder all frontmatter files to match canonical structure (8 sections)
- [ ] Move `datePublished`, `dateModified`, `contentType`, `schemaVersion`, `fullPath` to Section 2 (after core ID)
- [ ] Move `author` and `eeat` to Section 4 (after SEO)
- [ ] Move `images` to Section 5 (after author/eeat)
- [ ] Group `card` settings with SEO in Section 3

### Phase 2: Duplicate Field Removal
- [ ] Delete all `*_description` legacy fields (materialCharacteristics_description, etc.)
- [ ] Delete duplicate `properties.*.description` fields at root level
- [ ] Delete root-level `micro` if `components.micro` exists
- [ ] Delete `relationships.relatedMaterials` text field
- [ ] Delete empty `related_materials: []` arrays

### Phase 3: Consolidation
- [ ] Ensure `micro` content ONLY in `components.micro` (not root level)
- [ ] Ensure material characteristics ONLY in `properties.materialCharacteristics.description`
- [ ] Ensure laser interaction ONLY in `properties.laserMaterialInteraction.description`

### Phase 4: Validation
- [ ] Verify all frontmatter files follow canonical 8-section structure
- [ ] Confirm zero duplicate fields exist
- [ ] Check field count reduction (841 lines → ~600 lines expected)
- [ ] Test frontend still reads all fields correctly after reorganization

---

## 🎯 Expected Outcomes

**Before (Current State)**:
- ❌ 841 lines per file
- ❌ ~50% duplicate/legacy content
- ❌ Metadata scattered across 800 lines
- ❌ 12+ locations to check for updates

**After (Reorganized)**:
- ✅ ~600 lines per file (25% reduction)
- ✅ Zero duplicate fields
- ✅ All metadata in first 75 lines
- ✅ 8 clear sections for easy navigation
- ✅ Single source of truth for each field

---

## 🚀 Migration Priority

**CRITICAL - Do First**:
1. Move core metadata to Section 2 (lines 11-20)
2. Delete duplicate `*_description` fields
3. Consolidate `micro` into `components.micro` only

**HIGH - Do Next**:
4. Reorder author/eeat to Section 4
5. Reorder images to Section 5
6. Group card with SEO in Section 3

**MEDIUM - Polish**:
7. Add section comments for clarity
8. Alphabetize fields within each section (optional)

---

## 📝 Notes for Backend AI

**Key Principles**:
1. **Most Important First**: Core ID and metadata should be in first 20 lines
2. **Single Source of Truth**: Each piece of data exists in exactly ONE location
3. **Logical Grouping**: Related fields stay together (author + eeat, images together, etc.)
4. **No Duplication**: Delete all legacy/duplicate fields immediately
5. **Consistent Structure**: All materials/contaminants/compounds follow same 8-section pattern

**Testing After Changes**:
- Frontend should still render all pages correctly
- All relationship data should still display
- SEO metadata should still work
- No broken image links
- Author/E-E-A-T sections should still render

**Questions?**:
- If unsure about a field's purpose, check `docs/FRONTMATTER_NORMALIZED_STRUCTURE.md`
- If a field seems unused, grep the frontend codebase before deleting
- Preserve all `_section` and `_metadata` structures - frontend depends on these

---

## ✅ Success Criteria

Reorganization is complete when:
1. ✅ All 8 sections present in correct order
2. ✅ Core metadata in first 20 lines
3. ✅ Zero duplicate fields (`grep "description:" | sort | uniq -d` returns nothing)
4. ✅ File size reduced by ~25%
5. ✅ Frontend tests pass
6. ✅ All pages render correctly

**Estimated Time**: 2-3 hours for all material files

**Risk Level**: LOW - Changes are structural only, no data loss
