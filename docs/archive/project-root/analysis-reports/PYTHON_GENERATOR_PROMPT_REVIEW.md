# Critical Review: PYTHON_GENERATOR_PROMPT.md

**Date:** October 9, 2025  
**Reviewer:** GitHub Copilot  
**Document Under Review:** `PYTHON_GENERATOR_PROMPT.md`  
**Status:** 🔴 **CRITICAL ISSUES FOUND**

---

## Executive Summary

Your document contains **fundamental architectural mismatches** with the actual Z-Beam Generator codebase. Following this guide will produce incompatible output that will fail integration. Below is a detailed analysis with specific corrections needed.

---

## 🔴 Critical Issues Requiring Immediate Correction

### Issue #1: Wrong File Format

**Your Document States:**
```markdown
---
title: "..."
description: "..."
---

# Markdown Content Here
Your markdown content goes after the frontmatter section...
```

**Actual Reality:**
```yaml
# Pure YAML file - NO markdown content
name: Brass
category: Metal
subcategory: non_ferrous
title: Brass Laser Cleaning
description: Laser cleaning parameters for Brass
materialProperties:
  density:
    value: 8.44
# ... continues with pure YAML
```

**Problem:** Z-Beam Generator produces **pure YAML files** (`.yaml` extension), not markdown files with frontmatter. There is NO markdown content section.

**Fix Required:** Remove all references to markdown content and `---` delimiters. Change examples to pure YAML format.

---

### Issue #2: Missing Critical Fields in Property Structures

**Your Document Shows:**
```yaml
properties:
  density:
    value: number
    unit: string
    min: number
    max: number
```

**Actual Files Require:**
```yaml
materialProperties:           # ← Called materialProperties, not properties
  density:
    value: 8.44
    unit: g/cm³
    confidence: 95            # ← MISSING from your guide
    description: "..."        # ← MISSING from your guide
    min: 0.53
    max: 22.6
```

**Problem:** Every property requires `confidence` and `description` fields. These are not optional.

**Fix Required:** 
1. Rename `properties` to `materialProperties`
2. Add `confidence: number` (required)
3. Add `description: string` (required)
4. Update ALL examples to include these fields

---

### Issue #3: Completely Wrong Image Structure

**Your Document Shows:**
```yaml
images:
  hero:
    url: string
    alt: string
    width: number      # ← Does not exist
    height: number     # ← Does not exist
  micro:               # ← Wrong location
    url: string
    alt: string
  social:              # ← Does not exist
    url: string
    alt: string
```

**Actual Structure:**
```yaml
images:
  hero:
    alt: "Description"
    url: "/images/material/brass-laser-cleaning-hero.jpg"
    # Note: NO width/height, NO micro, NO social

# Micro image is in caption section:
caption:
  beforeText: "..."
  afterText: "..."
  imageUrl:           # ← Micro image is HERE
    alt: "..."
    url: "/images/material/brass-laser-cleaning-micro.jpg"
```

**Problem:** 
1. No `width`/`height` fields exist
2. `micro` image belongs in `caption.imageUrl`, NOT in `images`
3. No `social` image structure exists
4. Only `hero` image is in `images` section

**Fix Required:** 
1. Remove `width`, `height`, `micro`, and `social` from `images`
2. Document that `images` contains ONLY `hero`
3. Document that micro image is in `caption.imageUrl`

---

### Issue #4: Wrong Author Structure

**Your Document Shows:**
```yaml
author:
  name: string
  title: string
  expertise: [string]        # ← Wrong: Array
  bio: string                # ← Does not exist
  email: string              # ← Does not exist
  affiliation: string        # ← Does not exist
  image: string
```

**Actual Structure:**
```yaml
author:
  id: 2                      # ← MISSING from your guide
  name: Alessandro Moretti
  sex: m                     # ← MISSING from your guide
  title: Ph.D.
  country: Italy             # ← MISSING from your guide
  expertise: "Single string" # ← String, not array
  image: "/images/author/alessandro-moretti.jpg"
```

**Problem:** Wrong fields, wrong types

**Fix Required:**
1. Add `id: number` (required)
2. Add `sex: string` (required)
3. Add `country: string` (required)
4. Change `expertise` from array to single string
5. Remove `bio`, `email`, `affiliation`

---

### Issue #5: Caption Structure Fundamentally Wrong

**Your Document Shows:**
```yaml
caption:
  material: string
  title: string
  description: string
  beforeText: string
  afterText: string
  images:                    # ← Wrong nesting
    micro:
      url: string
      alt: string
  quality_metrics: {}
  laserParams: {}
```

**Actual Structure:**
```yaml
caption:
  beforeText: "Long text..."
  afterText: "Long text..."
  description: "Brief description"
  alt: "Alt text for caption"
  technicalAnalysis:         # ← MISSING from your guide
    focus: surface_analysis
    uniqueCharacteristics: [...]
    contaminationProfile: "..."
  microscopy:                # ← MISSING from your guide
    parameters: "..."
    qualityMetrics: "..."
  generation:                # ← MISSING from your guide
    method: "..."
    timestamp: "..."
    generator: "..."
    componentType: "..."
  author: "Author Name"      # ← Just string, not object
  materialProperties:        # ← MISSING from your guide
    materialType: "..."
    analysisMethod: "..."
  imageUrl:                  # ← Direct at caption level, not nested
    alt: "..."
    url: "/images/material/brass-laser-cleaning-micro.jpg"
```

**Problem:** Completely different structure with missing required sections

**Fix Required:**
1. Remove `material`, `title`, `images`, `quality_metrics`, `laserParams`
2. Add `technicalAnalysis` object (required)
3. Add `microscopy` object (required)
4. Add `generation` object with metadata (required)
5. Add `materialProperties` object (required)
6. Move `imageUrl` to top level of caption (not nested under `images`)
7. Document that `author` in caption is a string, not an object

---

### Issue #6: Missing Critical Root-Level Fields

**Your Document Omits These Required Fields:**
```yaml
# Required but not documented:
applications: []              # Array of application strings
regulatoryStandards: []       # Array of standard strings
environmentalImpact: []       # Array of impact objects
outcomeMetrics: []            # Array of metric objects
metadata:                     # Required metadata section
  lastUpdated: "ISO timestamp"
  captionIntegrated: true
```

**Fix Required:** Add complete documentation for these required fields.

---

### Issue #7: Field Naming Inconsistency

**Your Document Claims:**
> "Primary Rule: Use **camelCase** for all field names"

**Actual Reality:**
```yaml
name: Brass                   # lowercase
category: Metal              # lowercase
subcategory: non_ferrous     # snake_case
title: Brass                 # lowercase
materialProperties:          # camelCase
  thermalConductivity:       # camelCase
```

**Problem:** Mixed naming conventions - not all camelCase

**Fix Required:** 
1. Change rule to: "Use lowercase for top-level descriptive fields (`name`, `category`, `title`)"
2. Document: "Use snake_case for `subcategory`"
3. Keep: "Use camelCase for nested property names"

---

## 📋 Suggested Modifications to Present Back

Please create a corrected version with these changes:

### 1. Update Introduction Section

```markdown
## Overview
This document provides standardized YAML data structure conventions for 
generating content components for the Z-Beam laser cleaning system.

**File Format:** Pure YAML files with `.yaml` extension  
**Output Location:** `content/components/frontmatter/`  
**File Naming:** `{material-name}-laser-cleaning.yaml` (kebab-case)  
**NO MARKDOWN CONTENT** - Pure YAML data structures only
```

### 2. Correct Field Naming Rules

```markdown
## Naming Convention Standard

### Primary Rules:
- **Top-level fields:** lowercase (`name`, `category`, `title`, `description`)
- **Subcategory field:** snake_case (`subcategory`)
- **Nested properties:** camelCase (`meltingPoint`, `thermalConductivity`, `materialProperties`)
- **File names:** kebab-case (`brass-laser-cleaning.yaml`)

### Examples:
```yaml
# Top-level: lowercase
name: Brass
category: Metal
title: Brass Laser Cleaning

# Special: snake_case
subcategory: non_ferrous

# Nested: camelCase
materialProperties:
  thermalConductivity:
    value: 120
    unit: W/m·K
```
```

### 3. Correct Property Structure Template

```yaml
materialProperties:                    # Use materialProperties (not properties)
  density:
    value: 8.44                       # Numeric value
    unit: g/cm³                       # Unit of measurement
    confidence: 95                    # REQUIRED: Confidence level (0-100)
    description: "Typical density..." # REQUIRED: Property description
    min: 0.53                         # Optional: Minimum value
    max: 22.6                         # Optional: Maximum value
  meltingPoint:
    value: 915
    unit: °C
    confidence: 92
    description: "Solidus temperature for common brass alloys"
    min: null                         # Use null when no range
    max: null
  thermalConductivity:
    value: 120
    unit: W/m·K
    confidence: 90
    description: "Thermal conductivity for 70/30 brass at 20°C"
    min: 6.0
    max: 429.0
```

### 4. Correct Image Structure Template

```yaml
images:
  hero:                               # ONLY hero image in images section
    alt: "Brass surface undergoing laser cleaning showing precise contamination removal"
    url: "/images/material/brass-laser-cleaning-hero.jpg"
    # Note: NO width, NO height, NO micro, NO social in images section

# Micro image is in caption.imageUrl (see caption section below)
```

**Important Notes:**
- ❌ Do NOT add `width` or `height` fields
- ❌ Do NOT add `micro` to `images` section
- ❌ Do NOT add `social` to `images` section
- ✅ Only `hero` image belongs in `images`
- ✅ Micro image goes in `caption.imageUrl`

### 5. Correct Author Structure Template

```yaml
author:
  id: 2                               # REQUIRED: Author ID number
  name: Alessandro Moretti            # REQUIRED: Full name
  sex: m                              # REQUIRED: m or f
  title: Ph.D.                        # REQUIRED: Professional title
  country: Italy                      # REQUIRED: Country
  expertise: "Laser-Based Additive Manufacturing"  # REQUIRED: Single string (NOT array)
  image: "/images/author/alessandro-moretti.jpg"   # REQUIRED: Author photo path
```

**Important Notes:**
- ❌ Do NOT use `expertise` as an array
- ❌ Do NOT add `bio` field
- ❌ Do NOT add `email` field
- ❌ Do NOT add `affiliation` field
- ✅ `expertise` is a single string

### 6. Correct Caption Structure Template

```yaml
caption:
  beforeText: |
    At 500x magnification, the surface of the contaminated brass reveals a complex 
    and uneven topography... [lengthy technical description of contaminated surface]
  
  afterText: |
    After laser cleaning, the brass surface at 500x magnification presents a 
    remarkable transformation... [lengthy technical description of cleaned surface]
  
  description: "Microscopic analysis of brass surface before and after laser cleaning treatment"
  
  alt: "Microscopic view of brass surface showing laser cleaning effects"
  
  technicalAnalysis:                  # REQUIRED: Technical analysis section
    focus: surface_analysis
    uniqueCharacteristics:
      - brass_specific
    contaminationProfile: "brass surface contamination"
  
  microscopy:                         # REQUIRED: Microscopy parameters
    parameters: "Microscopic analysis of brass"
    qualityMetrics: "Surface improvement analysis"
  
  generation:                         # REQUIRED: Generation metadata
    method: frontmatter_integrated_generation
    timestamp: "2025-10-04T21:26:36.443423Z"
    generator: FrontmatterCaptionGenerator
    componentType: ai_caption_frontmatter
  
  author: Alessandro Moretti          # String reference to author (NOT object)
  
  materialProperties:                 # REQUIRED: Material analysis properties
    materialType: Metal
    analysisMethod: ai_microscopy
  
  imageUrl:                           # REQUIRED: Micro image location
    alt: "Microscopic view of Brass surface after laser cleaning showing detailed surface structure"
    url: "/images/material/brass-laser-cleaning-micro.jpg"
```

**Important Notes:**
- ❌ Do NOT add `material` field
- ❌ Do NOT add `title` field
- ❌ Do NOT nest `imageUrl` under `images`
- ❌ Do NOT add `quality_metrics` or `laserParams`
- ✅ `author` in caption is a string, not an object
- ✅ `imageUrl` is at top level of caption
- ✅ All five subsections are required: `technicalAnalysis`, `microscopy`, `generation`, `materialProperties`, `imageUrl`

### 7. Add Missing Required Fields Section

```yaml
# REQUIRED: Applications array
applications:
  - "Architecture"
  - "Hardware Manufacturing"
  - "Marine"
  - "Musical Instruments"
  - "Plumbing"
  - "Valves and Fittings"

# REQUIRED: Machine settings with same structure as materialProperties
machineSettings:
  powerRange:
    value: 90
    unit: W
    confidence: 92
    description: "Optimal average power for Brass oxide removal without substrate damage"
    min: 70
    max: 120
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: "Near-IR wavelength optimized for Brass absorption"
    min: 532
    max: 1064
  spotSize:
    value: 80
    unit: μm
    confidence: 84
    description: "Beam spot diameter for balanced cleaning efficiency"
    min: 50
    max: 120
  repetitionRate:
    value: 50
    unit: kHz
    confidence: 87
    description: "Optimal repetition rate for efficient cleaning coverage"
    min: 20
    max: 100
  pulseWidth:
    value: 12
    unit: ns
    confidence: 85
    description: "Nanosecond pulse duration for effective contaminant removal"
    min: 8
    max: 20
  scanSpeed:
    value: 500
    unit: mm/s
    confidence: 86
    description: "Optimal scanning speed for uniform cleaning"
    min: 300
    max: 800
  energyDensity:
    value: 4.5
    unit: J/cm²
    confidence: 89
    description: "Fluence threshold for effective Brass surface cleaning"
    min: 3.0
    max: 6.5
  overlapRatio:
    value: 40
    unit: '%'
    confidence: 83
    description: "Optimal beam overlap for uniform cleaning coverage"
    min: 30
    max: 60
  passCount:
    value: 2
    unit: passes
    confidence: 85
    description: "Recommended number of passes for complete contaminant removal"
    min: 1
    max: 4

# REQUIRED: Regulatory standards array
regulatoryStandards:
  - "FDA 21 CFR 1040.10 - Laser Product Performance Standards"
  - "ANSI Z136.1 - Safe Use of Lasers"
  - "IEC 60825 - Safety of Laser Products"
  - "OSHA 29 CFR 1926.95 - Personal Protective Equipment"

# REQUIRED: Environmental impact array
environmentalImpact:
  - benefit: "Chemical Waste Elimination"
    description: "Eliminates hazardous chemical waste streams"
    applicableIndustries:
      - "Semiconductor"
      - "Electronics"
      - "Medical"
      - "Nuclear"
    quantifiedBenefits: "Up to 100% reduction in chemical cleaning agents"
    sustainabilityBenefit: ""
  - benefit: "Water Usage Reduction"
    description: "Dry process requires no water"
    applicableIndustries: []
    quantifiedBenefits: ""
    sustainabilityBenefit: "Significant water conservation in industrial processes"
  - benefit: "Energy Efficiency"
    description: "Focused energy delivery with minimal waste heat"
    applicableIndustries: []
    quantifiedBenefits: ""
    sustainabilityBenefit: ""
  - benefit: "Air Quality Improvement"
    description: "Eliminates volatile organic compounds from chemical cleaning"
    applicableIndustries: []
    quantifiedBenefits: ""
    sustainabilityBenefit: ""

# REQUIRED: Outcome metrics array
outcomeMetrics:
  - metric: "Contaminant Removal Efficiency"
    description: "Percentage of target contaminants successfully removed from surface"
    measurementMethods:
      - "Before/after microscopy"
      - "Chemical analysis"
      - "Mass spectrometry"
    typicalRanges: "95-99.9% depending on application and material"
    factorsAffecting:
      - "Contamination type"
      - "Adhesion strength"
      - "Surface geometry"
    units: []
  - metric: "Processing Speed"
    description: "Rate of surface area processed per unit time"
    measurementMethods: []
    typicalRanges: ""
    factorsAffecting: []
    units:
      - "m²/h"
      - "cm²/min"
      - "mm²/s"
  - metric: "Surface Quality Preservation"
    description: "Maintenance of original surface characteristics after cleaning"
    measurementMethods: []
    typicalRanges: ""
    factorsAffecting: []
    units: []
  - metric: "Thermal Damage Avoidance"
    description: "Prevention of heat-related material alterations during cleaning"
    measurementMethods: []
    typicalRanges: ""
    factorsAffecting: []
    units: []

# REQUIRED: Tags array
tags:
  - metal
  - manufacturing
  - aerospace
  - automotive
  - decoating
  - oxide-removal
  - surface-preparation
  - reflective-surface
  - conductive
  - alessandro-moretti

# REQUIRED: Metadata section
metadata:
  lastUpdated: "2025-10-04T21:27:14.179442"
  captionIntegrated: true
```

### 8. Complete File Template (Based on Real brass-laser-cleaning.yaml)

```yaml
# ==============================================================================
# Z-BEAM GENERATOR FRONTMATTER TEMPLATE
# File: {material-name}-laser-cleaning.yaml
# Format: Pure YAML (NO markdown content)
# ==============================================================================

# TOP-LEVEL FIELDS (lowercase)
name: Brass
category: Metal
subcategory: non_ferrous                # snake_case
title: Brass Laser Cleaning
description: Laser cleaning parameters for Brass

# MATERIAL PROPERTIES (nested objects with confidence & description)
materialProperties:
  density:
    value: 8.44
    unit: g/cm³
    confidence: 95
    description: "Typical density for 70/30 brass (CuZn30) at room temperature"
    min: 0.53
    max: 22.6
  meltingPoint:
    value: 915
    unit: °C
    confidence: 92
    description: "Solidus temperature for common brass alloys"
    min: null
    max: null
  thermalConductivity:
    value: 120
    unit: W/m·K
    confidence: 90
    description: "Thermal conductivity for 70/30 brass at 20°C"
    min: 6.0
    max: 429.0
  tensileStrength:
    value: 340
    unit: MPa
    confidence: 88
    description: "Typical tensile strength for annealed brass"
    min: 3.0
    max: 3000.0
  hardness:
    value: 75
    unit: HV
    confidence: 85
    description: "Vickers hardness for annealed brass"
    min: 0.5
    max: 3500
  youngsModulus:
    value: 110
    unit: GPa
    confidence: 92
    description: "Young's modulus of elasticity"
    min: 5
    max: 411
  laserAbsorption:
    value: 38.5
    unit: '%'
    confidence: 92
    description: "laserAbsorption from Materials.yaml"
    min: 0.02
    max: 100
  laserReflectivity:
    value: 62.0
    unit: '%'
    confidence: 92
    description: "laserReflectivity from Materials.yaml"
    min: 5
    max: 98

# APPLICATIONS
applications:
  - "Architecture"
  - "Hardware Manufacturing"
  - "Marine"
  - "Musical Instruments"
  - "Plumbing"
  - "Valves and Fittings"

# MACHINE SETTINGS (same structure as materialProperties)
machineSettings:
  powerRange:
    value: 90
    unit: W
    confidence: 92
    description: "Optimal average power for oxide removal"
    min: 70
    max: 120
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: "Near-IR wavelength optimized for Brass"
    min: 532
    max: 1064

# REGULATORY STANDARDS
regulatoryStandards:
  - "FDA 21 CFR 1040.10 - Laser Product Performance Standards"
  - "ANSI Z136.1 - Safe Use of Lasers"
  - "IEC 60825 - Safety of Laser Products"

# AUTHOR (required fields)
author:
  id: 2
  name: Alessandro Moretti
  sex: m
  title: Ph.D.
  country: Italy
  expertise: "Laser-Based Additive Manufacturing"
  image: "/images/author/alessandro-moretti.jpg"

# IMAGES (only hero)
images:
  hero:
    alt: "Brass surface undergoing laser cleaning"
    url: "/images/material/brass-laser-cleaning-hero.jpg"

# ENVIRONMENTAL IMPACT
environmentalImpact:
  - benefit: "Chemical Waste Elimination"
    description: "Eliminates hazardous waste streams"
    applicableIndustries:
      - "Semiconductor"
      - "Electronics"
    quantifiedBenefits: "Up to 100% reduction"
    sustainabilityBenefit: ""

# OUTCOME METRICS
outcomeMetrics:
  - metric: "Contaminant Removal Efficiency"
    description: "Percentage removed"
    measurementMethods:
      - "Before/after microscopy"
    typicalRanges: "95-99.9%"
    factorsAffecting:
      - "Contamination type"
    units: []

# CAPTION (complex structure with micro image)
caption:
  beforeText: |
    Detailed technical analysis of contaminated surface...
  afterText: |
    Detailed technical analysis of cleaned surface...
  description: "Microscopic analysis of brass surface"
  alt: "Microscopic view of brass surface"
  technicalAnalysis:
    focus: surface_analysis
    uniqueCharacteristics:
      - brass_specific
    contaminationProfile: "brass surface contamination"
  microscopy:
    parameters: "Microscopic analysis of brass"
    qualityMetrics: "Surface improvement analysis"
  generation:
    method: frontmatter_integrated_generation
    timestamp: "2025-10-04T21:26:36.443423Z"
    generator: FrontmatterCaptionGenerator
    componentType: ai_caption_frontmatter
  author: Alessandro Moretti
  materialProperties:
    materialType: Metal
    analysisMethod: ai_microscopy
  imageUrl:
    alt: "Microscopic view of Brass surface"
    url: "/images/material/brass-laser-cleaning-micro.jpg"

# TAGS
tags:
  - metal
  - manufacturing
  - aerospace
  - automotive
  - oxide-removal

# METADATA
metadata:
  lastUpdated: "2025-10-04T21:27:14.179442"
  captionIntegrated: true
```

### 9. Add Reference Section at Start

```markdown
## Reference Implementation

**Authoritative Source:** `content/components/frontmatter/brass-laser-cleaning.yaml`

This document describes the exact structure used in that file. When in doubt, 
refer to the actual frontmatter files in the repository as the source of truth.

### Quick Reference Files:
- **Metals:** `brass-laser-cleaning.yaml`, `titanium-laser-cleaning.yaml`
- **Ceramics:** `porcelain-laser-cleaning.yaml`
- **Woods:** `beech-laser-cleaning.yaml`
- **Composites:** `carbon-fiber-reinforced-polymer-laser-cleaning.yaml`
```

---

## ✅ What to Keep from Current Document

These aspects are correct and should be preserved:

1. ✅ `beforeText` / `afterText` use camelCase (not snake_case)
2. ✅ Image path pattern: `/images/material/{name}-laser-cleaning-{type}.jpg`
3. ✅ File naming convention: kebab-case
4. ✅ General concept of nested objects with value/unit
5. ✅ Emphasis on structured data
6. ✅ Use of null for missing min/max values

---

## 📝 Validation Checklist (Updated)

Before generating frontmatter, verify:

- [ ] File format is **pure YAML** (`.yaml` extension, NO markdown content)
- [ ] Top-level fields use **lowercase** (`name`, `category`, `title`)
- [ ] `subcategory` uses **snake_case**
- [ ] Nested properties use **camelCase** (`materialProperties`, `meltingPoint`)
- [ ] **Every property** has `value`, `unit`, `confidence`, `description`, `min`, `max`
- [ ] `images` contains **ONLY** `hero` (no micro, no social, no width/height)
- [ ] `caption.imageUrl` contains the micro image (NOT in `images`)
- [ ] `author` has all required fields: `id`, `name`, `sex`, `title`, `country`, `expertise`, `image`
- [ ] `author.expertise` is a **string** (not array)
- [ ] `caption` includes all five required subsections
- [ ] `caption.author` is a **string** (not object)
- [ ] All root-level arrays are present: `applications`, `regulatoryStandards`, `environmentalImpact`, `outcomeMetrics`, `tags`
- [ ] `metadata` section includes `lastUpdated` and `captionIntegrated`
- [ ] `machineSettings` uses same structure as `materialProperties`

---

## 🔄 Migration Path

To update your document:

1. **Remove all markdown-related content**
   - Delete `---` delimiter examples
   - Remove "markdown content here" sections
   - Change all examples to pure YAML

2. **Update all property examples to include:**
   ```yaml
   propertyName:
     value: number
     unit: string
     confidence: number      # ADD THIS
     description: string     # ADD THIS
     min: number | null
     max: number | null
   ```

3. **Fix image structure:**
   - Remove `micro` and `social` from `images`
   - Remove `width` and `height` fields
   - Move micro image documentation to `caption.imageUrl`

4. **Fix author structure:**
   - Add `id`, `sex`, `country`
   - Change `expertise` from array to string
   - Remove `bio`, `email`, `affiliation`

5. **Completely rewrite caption section** using actual structure

6. **Add documentation for:**
   - `applications` array
   - `machineSettings` structure
   - `regulatoryStandards` array
   - `environmentalImpact` array
   - `outcomeMetrics` array
   - `tags` array
   - `metadata` section

7. **Update naming rules** to reflect actual mixed conventions

8. **Add reference** to `brass-laser-cleaning.yaml` as canonical example

---

## 🎯 Deliverable Request

Please provide:

1. **Completely rewritten document** incorporating all corrections
2. **Full YAML template** based on actual `brass-laser-cleaning.yaml`
3. **Updated validation checklist** with all required fields
4. **Removal of all incorrect information** (markdown content, wrong structures)
5. **Addition of all missing required fields** (confidence, description, etc.)

---

## 📊 Impact Assessment

**Current Document Risk Level:** 🔴 **CRITICAL**

Following the current document will produce:
- ❌ Wrong file format (markdown instead of YAML)
- ❌ Missing required fields (confidence, description)
- ❌ Wrong image structure (micro in wrong location)
- ❌ Wrong caption structure (missing 5 required subsections)
- ❌ Wrong author structure (missing id, sex, country)
- ❌ Incomplete property definitions
- ❌ Missing entire sections (environmentalImpact, outcomeMetrics, etc.)

**Result:** Generated files will be **incompatible** with Z-Beam Generator and fail validation.

---

## 🔗 Additional Resources

For reference while updating:

- **Real example:** `content/components/frontmatter/brass-laser-cleaning.yaml`
- **Project instructions:** `.github/copilot-instructions.md`
- **YAML fix tool:** `scripts/tools/fix_frontmatter_yaml_formatting.py`
- **YAML fix documentation:** `docs/YAML_FORMATTING_FIX_SUMMARY.md`

---

**Priority:** 🔴 **URGENT** - Document requires immediate revision before use

**Estimated Effort:** 4-6 hours to completely rewrite with corrections

**Recommendation:** Start fresh using `brass-laser-cleaning.yaml` as template rather than attempting to patch current document.
