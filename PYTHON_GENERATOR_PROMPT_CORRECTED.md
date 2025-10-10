# Python Generator - Z-Beam YAML Data Structure Guide

## 🎯 Critical Information

**Authoritative Reference:** `content/components/frontmatter/brass-laser-cleaning.yaml`

This document describes the **exact YAML structure** used by the Z-Beam Python Generator based on actual production files.

---

## Overview

**File Format:** Pure YAML files (`.yaml` extension) - **NO markdown content**  
**Output Location:** `content/components/frontmatter/`  
**File Naming:** `{material-name}-laser-cleaning.yaml` (kebab-case)  
**Purpose:** Generate structured data components for Next.js static site generation

---

## 🎯 Core Principles

### 1. **File Format Rules**
- ✅ Pure YAML format (`.yaml` files)
- ❌ NO markdown frontmatter delimiters (`---`)
- ❌ NO markdown content after YAML
- ✅ Complete data structure in single YAML document

### 2. **Naming Convention Standard**

**Mixed conventions are used strategically:**

- **Top-level fields:** lowercase (`name`, `category`, `title`, `subtitle`, `description`)
- **Subcategory field:** snake_case (`subcategory` → e.g., `non_ferrous`)
- **Nested properties:** camelCase (`materialProperties`, `meltingPoint`, `thermalConductivity`)
- **File names:** kebab-case (e.g., `brass-laser-cleaning.yaml`)

---

## 📋 Required Top-Level Fields

```yaml
name: string                     # Material name (e.g., "Brass")
category: string                 # Category (e.g., "Metal")
subcategory: string              # snake_case (e.g., "non_ferrous")
title: string                    # Page title
subtitle: string                 # Page subtitle/tagline
description: string              # Brief description
```

### Example:
```yaml
name: Brass
category: Metal
subcategory: non_ferrous
title: Brass Laser Cleaning
subtitle: Advanced laser cleaning solutions for brass
description: Laser cleaning parameters for Brass
```

---

## 🧪 Material Properties (6 Required Fields Per Property)

### **CRITICAL**: Each property requires `value`, `unit`, `confidence`, `description`, `min`, `max`

```yaml
materialProperties:              # Use materialProperties (NOT properties)
  propertyName:
    value: number                # Numeric value
    unit: string                 # Unit of measurement
    confidence: number           # REQUIRED: 0-100 confidence level
    description: string          # REQUIRED: Technical description
    min: number | null           # Minimum (or null)
    max: number | null           # Maximum (or null)
```

### Example:
```yaml
materialProperties:
  density:
    value: 8.44
    unit: g/cm³
    confidence: 95
    description: Typical density for 70/30 brass (CuZn30) at room temperature
    min: 0.53
    max: 22.6
  meltingPoint:
    value: 915
    unit: °C
    confidence: 92
    description: Solidus temperature for common brass alloys
    min: null
    max: null
  thermalConductivity:
    value: 120
    unit: W/m·K
    confidence: 90
    description: Thermal conductivity for 70/30 brass at 20°C
    min: 6.0
    max: 429.0
```

---

## ⚙️ Machine Settings (Identical Structure to materialProperties)

```yaml
machineSettings:
  powerRange:
    value: 90
    unit: W
    confidence: 92
    description: Optimal average power for oxide removal
    min: 70
    max: 120
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-IR wavelength optimized for Brass
    min: 532
    max: 1064
  spotSize:
    value: 80
    unit: μm
    confidence: 84
    description: Beam spot diameter for balanced efficiency
    min: 50
    max: 120
  repetitionRate:
    value: 50
    unit: kHz
    confidence: 87
    description: Optimal repetition rate for cleaning
    min: 20
    max: 100
  pulseWidth:
    value: 12
    unit: ns
    confidence: 85
    description: Nanosecond pulse duration
    min: 8
    max: 20
  scanSpeed:
    value: 500
    unit: mm/s
    confidence: 86
    description: Optimal scanning speed
    min: 300
    max: 800
  energyDensity:
    value: 4.5
    unit: J/cm²
    confidence: 89
    description: Fluence threshold for cleaning
    min: 3.0
    max: 6.5
  overlapRatio:
    value: 40
    unit: '%'
    confidence: 83
    description: Optimal beam overlap
    min: 30
    max: 60
  passCount:
    value: 2
    unit: passes
    confidence: 85
    description: Recommended passes
    min: 1
    max: 4
```

---

## 👤 Author Information (7 Required Fields)

```yaml
author:
  id: number                     # REQUIRED: Author ID
  name: string                   # REQUIRED: Full name
  sex: string                    # REQUIRED: "m" or "f"
  title: string                  # REQUIRED: Title (e.g., "Ph.D.")
  country: string                # REQUIRED: Country
  expertise: string              # REQUIRED: Single string (NOT array)
  image: string                  # REQUIRED: Photo path
```

### Example:
```yaml
author:
  id: 2
  name: Alessandro Moretti
  sex: m
  title: Ph.D.
  country: Italy
  expertise: Laser-Based Additive Manufacturing
  image: /images/author/alessandro-moretti.jpg
```

**Critical:** `expertise` is a **single string**, NOT an array.

---

## 🖼️ Images (Only Hero)

```yaml
images:
  hero:
    alt: string                  # Alt text
    url: string                  # Path to hero image
```

### Example:
```yaml
images:
  hero:
    alt: Brass surface undergoing laser cleaning showing precise contamination removal
    url: /images/material/brass-laser-cleaning-hero.jpg
```

**Critical Points:**
- ❌ Do NOT add `width`, `height`, `micro`, or `social` fields
- ✅ Only `hero` image in `images` section
- ✅ Micro image goes in `caption.imageUrl` (see below)

---

## 📊 Caption (Complex Structure with 5 Required Subsections)

```yaml
caption:
  beforeText: |                  # Multiline string
    Detailed technical analysis of contaminated surface...
  afterText: |                   # Multiline string
    Detailed technical analysis of cleaned surface...
  description: string            # Brief description
  alt: string                    # Alt text
  
  technicalAnalysis:             # REQUIRED subsection
    focus: string
    uniqueCharacteristics: []
    contaminationProfile: string
  
  microscopy:                    # REQUIRED subsection
    parameters: string
    qualityMetrics: string
  
  generation:                    # REQUIRED subsection
    method: string
    timestamp: string            # ISO timestamp
    generator: string
    componentType: string
  
  author: string                 # String (NOT object)
  
  materialProperties:            # REQUIRED subsection
    materialType: string
    analysisMethod: string
  
  imageUrl:                      # REQUIRED: Micro image
    alt: string
    url: string
```

### Example:
```yaml
caption:
  beforeText: |
    At 500x magnification, the surface of the contaminated brass reveals a complex 
    and uneven topography... [lengthy description continues]
  
  afterText: |
    After laser cleaning, the brass surface at 500x magnification presents a remarkable 
    transformation... [lengthy description continues]
  
  description: Microscopic analysis of brass surface before and after laser cleaning treatment
  alt: Microscopic view of brass surface showing laser cleaning effects
  
  technicalAnalysis:
    focus: surface_analysis
    uniqueCharacteristics:
      - brass_specific
    contaminationProfile: brass surface contamination
  
  microscopy:
    parameters: Microscopic analysis of brass
    qualityMetrics: Surface improvement analysis
  
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
    alt: Microscopic view of Brass surface after laser cleaning
    url: /images/material/brass-laser-cleaning-micro.jpg
```

**Critical Points:**
- ✅ `beforeText`/`afterText` use `|` multiline format
- ✅ `author` in caption is STRING (not object)
- ✅ `imageUrl` at top level (not nested)
- ✅ All 5 subsections required
- ❌ Do NOT add `material`, `title`, `quality_metrics`, or `laserParams`

---

## 📋 Additional Required Arrays

### Applications
```yaml
applications:
  - Architecture
  - Hardware Manufacturing
  - Marine
  - Musical Instruments
```

### Regulatory Standards
```yaml
regulatoryStandards:
  - FDA 21 CFR 1040.10 - Laser Product Performance Standards
  - ANSI Z136.1 - Safe Use of Lasers
  - IEC 60825 - Safety of Laser Products
```

### Tags
```yaml
tags:
  - metal
  - manufacturing
  - aerospace
  - oxide-removal
```

### Metadata
```yaml
metadata:
  lastUpdated: "2025-10-04T21:27:14.179442"
  captionIntegrated: true
```

---

## 🌍 Environmental Impact

```yaml
environmentalImpact:
  - benefit: Chemical Waste Elimination
    description: Eliminates hazardous waste streams
    applicableIndustries:
      - Semiconductor
      - Electronics
    quantifiedBenefits: Up to 100% reduction
    sustainabilityBenefit: ''
  - benefit: Water Usage Reduction
    description: Dry process requires no water
    applicableIndustries: []
    quantifiedBenefits: ''
    sustainabilityBenefit: Significant water conservation
```

---

## 📈 Outcome Metrics

```yaml
outcomeMetrics:
  - metric: Contaminant Removal Efficiency
    description: Percentage removed
    measurementMethods:
      - Before/after microscopy
      - Chemical analysis
    typicalRanges: 95-99.9%
    factorsAffecting:
      - Contamination type
      - Adhesion strength
    units: []
  - metric: Processing Speed
    description: Rate of processing
    measurementMethods: []
    typicalRanges: ''
    factorsAffecting: []
    units:
      - m²/h
      - cm²/min
```

---

## 📝 Complete Template Example

```yaml
# File: brass-laser-cleaning.yaml
# Pure YAML - NO markdown content

name: Brass
category: Metal
subcategory: non_ferrous
title: Brass Laser Cleaning
subtitle: Advanced laser cleaning solutions for brass
description: Laser cleaning parameters for Brass

materialProperties:
  density:
    value: 8.44
    unit: g/cm³
    confidence: 95
    description: Typical density for 70/30 brass at room temperature
    min: 0.53
    max: 22.6
  meltingPoint:
    value: 915
    unit: °C
    confidence: 92
    description: Solidus temperature for common brass alloys
    min: null
    max: null
  thermalConductivity:
    value: 120
    unit: W/m·K
    confidence: 90
    description: Thermal conductivity for 70/30 brass at 20°C
    min: 6.0
    max: 429.0

applications:
  - Architecture
  - Hardware Manufacturing
  - Marine

machineSettings:
  powerRange:
    value: 90
    unit: W
    confidence: 92
    description: Optimal average power
    min: 70
    max: 120
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    description: Near-IR wavelength
    min: 532
    max: 1064

regulatoryStandards:
  - FDA 21 CFR 1040.10 - Laser Product Performance Standards
  - ANSI Z136.1 - Safe Use of Lasers

author:
  id: 2
  name: Alessandro Moretti
  sex: m
  title: Ph.D.
  country: Italy
  expertise: Laser-Based Additive Manufacturing
  image: /images/author/alessandro-moretti.jpg

images:
  hero:
    alt: Brass surface undergoing laser cleaning
    url: /images/material/brass-laser-cleaning-hero.jpg

environmentalImpact:
  - benefit: Chemical Waste Elimination
    description: Eliminates hazardous waste streams
    applicableIndustries:
      - Semiconductor
      - Electronics
    quantifiedBenefits: Up to 100% reduction
    sustainabilityBenefit: ''

outcomeMetrics:
  - metric: Contaminant Removal Efficiency
    description: Percentage removed
    measurementMethods:
      - Before/after microscopy
    typicalRanges: 95-99.9%
    factorsAffecting:
      - Contamination type
    units: []

caption:
  beforeText: |
    At 500x magnification, the surface reveals contamination...
  afterText: |
    After cleaning, the surface shows transformation...
  description: Microscopic analysis of brass surface
  alt: Microscopic view of brass surface
  technicalAnalysis:
    focus: surface_analysis
    uniqueCharacteristics:
      - brass_specific
    contaminationProfile: brass surface contamination
  microscopy:
    parameters: Microscopic analysis of brass
    qualityMetrics: Surface improvement analysis
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
    alt: Microscopic view of Brass surface
    url: /images/material/brass-laser-cleaning-micro.jpg

tags:
  - metal
  - manufacturing
  - aerospace
  - oxide-removal

metadata:
  lastUpdated: "2025-10-04T21:27:14.179442"
  captionIntegrated: true
```

---

## ✅ Validation Checklist

Before generating YAML files, verify:

- [ ] File format is **pure YAML** (`.yaml` extension)
- [ ] **NO** markdown content or `---` delimiters
- [ ] Top-level fields use **lowercase** (`name`, `category`, `title`, `subtitle`, `description`)
- [ ] `subtitle` field is present (required for all materials)
- [ ] `subcategory` uses **snake_case** (e.g., `non_ferrous`)
- [ ] Nested properties use **camelCase** (`materialProperties`, `meltingPoint`)
- [ ] **Every property** has 6 fields: `value`, `unit`, `confidence`, `description`, `min`, `max`
- [ ] `materialProperties` (NOT `properties`)
- [ ] `machineSettings` uses same 6-field structure
- [ ] `images` contains **ONLY** `hero` (no width/height/micro/social)
- [ ] `caption.imageUrl` contains micro image (NOT in `images`)
- [ ] `author` has all 7 required fields
- [ ] `author.expertise` is **string** (NOT array)
- [ ] `caption` includes all 5 subsections
- [ ] `caption.author` is **string** (NOT object)
- [ ] All arrays present: `applications`, `regulatoryStandards`, `tags`, `environmentalImpact`, `outcomeMetrics`
- [ ] `metadata` section included

---

## 🎯 Key Differences from Next.js App

The Python Generator produces YAML data that the Next.js app consumes. Key differences:

| Python Generator Output | Next.js App Usage |
|------------------------|-------------------|
| `materialProperties` | May access as `properties` or `materialProperties` |
| `subcategory` (snake_case) | Normalized to camelCase in components |
| Pure YAML files | Parsed and integrated with TypeScript types |
| `author` object with 7 fields | Can also accept simple string in some contexts |
| `caption.imageUrl` for micro | Components handle both patterns |

**Important:** Generate files according to this spec. The Next.js app handles compatibility.

---

## 🚀 Integration Notes

1. **File naming:** Use kebab-case (e.g., `brass-laser-cleaning.yaml`)
2. **Image paths:** Follow pattern `/images/material/{name}-laser-cleaning-{type}.jpg`
3. **Confidence values:** Use realistic 0-100 scale
4. **Descriptions:** Be technically accurate and detailed
5. **Timestamps:** Use ISO 8601 format
6. **Null values:** Use `null` (not empty string) for missing min/max

---

## 📚 Reference Files

- **Template:** `content/components/frontmatter/brass-laser-cleaning.yaml`
- **Other examples:** Check `/content/components/frontmatter/` directory
- **Type definitions:** `types/centralized.ts` in Next.js app

---

**Document Version:** 2.0 (Corrected)  
**Last Updated:** October 9, 2025  
**Authoritative Source:** Actual brass-laser-cleaning.yaml production file
