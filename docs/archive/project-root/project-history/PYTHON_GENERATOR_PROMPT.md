# Python Generator - Z-Beam Frontmatter Normalization Guide

## Overview
This document provides standardized frontmatter field naming conventions and data structures for generating content that integrates with the Z-Beam Next.js application.

---

## 🎯 Core Principles

### 1. **Naming Convention Standard**
- **Primary Rule**: Use **camelCase** for all field names
- **Exception**: Only use `snake_case` for legacy compatibility fields (marked with ⚠️ below)
- **File Names**: Use `kebab-case` for all file names (e.g., `stainless-steel-laser-cleaning.md`)
- **Avoid**: Mixed conventions within the same data structure

### 2. **Type Safety**
All frontmatter should align with the TypeScript interface `ArticleMetadata` defined in `types/centralized.ts`

---

## 📋 Required Core Fields

```yaml
title: string                    # SEO-optimized full title
subtitle: string                 # Brief descriptive subtitle (optional but recommended)
description: string              # Technical overview with specifications
slug: string                     # URL-safe identifier (kebab-case)
category: string                 # Content category (e.g., "material", "service")
tags: [string]                   # Array of relevant keywords
author: string | AuthorInfo      # Can be simple string or full author object
```

### Example:
```yaml
title: "Laser Cleaning Stainless Steel - Complete Technical Guide"
subtitle: "Precision surface treatment for industrial applications"
description: "Comprehensive guide to laser cleaning stainless steel surfaces..."
slug: "stainless-steel-laser-cleaning"
category: "material"
tags:
  - stainless-steel
  - laser-cleaning
  - surface-treatment
author: "Dr. Sarah Chen"
```

---

## 🖼️ Image Structure (Nested Objects)

### **CRITICAL**: Images use nested object structure

```yaml
images:
  hero:
    url: string                  # Path: /images/material/{material-name}-laser-cleaning-hero.jpg
    alt: string                  # Descriptive alt text for accessibility
    width: number                # Optional: Image width in pixels
    height: number               # Optional: Image height in pixels
  micro:
    url: string                  # Path: /images/material/{material-name}-laser-cleaning-micro.jpg
    alt: string                  # Descriptive alt text for microscopy image
    width: number                # Optional
    height: number               # Optional
  social:
    url: string                  # Path: /images/material/{material-name}-laser-cleaning-micro-social.jpg
    alt: string                  # Alt text for social media sharing
```

### Example:
```yaml
images:
  hero:
    url: "/images/material/stainless-steel-laser-cleaning-hero.jpg"
    alt: "Industrial laser cleaning stainless steel surface"
    width: 1920
    height: 1080
  micro:
    url: "/images/material/stainless-steel-laser-cleaning-micro.jpg"
    alt: "Microscopic view of cleaned stainless steel surface"
  social:
    url: "/images/material/stainless-steel-laser-cleaning-micro-social.jpg"
    alt: "Stainless steel laser cleaning results"
```

**Image Path Pattern**: `/images/material/{material-name}-laser-cleaning-{type}.jpg`
- `{material-name}`: kebab-case material identifier
- `{type}`: `hero`, `micro`, or `micro-social`

---

## 👤 Author Information

### Simple Format (String):
```yaml
author: "Dr. Sarah Chen"
```

### Full Author Object:
```yaml
author:
  name: string                   # Full name
  title: string                  # Professional title
  expertise: [string]            # Array of expertise areas
  bio: string                    # Professional bio
  email: string                  # Contact email
  affiliation: string            # Organization/institution
  image: string                  # Author photo path
```

### Example:
```yaml
author:
  name: "Dr. Sarah Chen"
  title: "Senior Materials Scientist"
  expertise:
    - "Laser Surface Treatment"
    - "Materials Engineering"
    - "Industrial Processing"
  bio: "15+ years of experience in advanced laser processing..."
  email: "sarah.chen@z-beam.com"
  affiliation: "Z-Beam Research Institute"
  image: "/images/authors/sarah-chen.jpg"
```

---

## 🧪 Material Properties (Nested Object with Units)

### **Structure**: Each property is an object with `value`, `unit`, `min`, `max`

```yaml
properties:
  propertyName:
    value: number                # Numeric value (can be string for ranges)
    unit: string                 # Unit of measurement
    min: number                  # Optional: Minimum value in range
    max: number                  # Optional: Maximum value in range
```

### Example:
```yaml
properties:
  density:
    value: 7.85
    unit: "g/cm³"
    min: 7.75
    max: 8.05
  meltingPoint:
    value: 1370
    unit: "°C"
    min: 1350
    max: 1400
  thermalConductivity:
    value: 16.2
    unit: "W/(m·K)"
  tensileStrength:
    value: 505
    unit: "MPa"
    min: 485
    max: 620
```

### Alternative Flat Structure (Legacy Support):
```yaml
density: "7.85 g/cm³"
densityMin: "7.75"
densityMax: "8.05"
meltingPoint: "1370°C"
thermalConductivity: "16.2 W/(m·K)"
```

**Preferred**: Use nested object structure for new content.

---

## ⚙️ Machine Settings

### **Same Structure as Properties**:

```yaml
machineSettings:
  powerRange:
    value: 100
    unit: "W"
    min: 50
    max: 200
  wavelength:
    value: 1064
    unit: "nm"
  pulseWidth:
    value: 10
    unit: "ns"
    min: 5
    max: 50
  repetitionRate:
    value: 20
    unit: "kHz"
    min: 10
    max: 100
  spotSize:
    value: 50
    unit: "μm"
  fluence:
    value: 2.5
    unit: "J/cm²"
```

### Common Machine Settings Fields:
- `powerRange`: Laser power (W)
- `wavelength`: Laser wavelength (nm)
- `pulseWidth` / `pulseDuration`: Pulse duration (ns, ps, fs)
- `repetitionRate` / `frequency`: Pulse frequency (kHz, Hz)
- `spotSize`: Beam spot diameter (μm, mm)
- `fluence` / `fluenceRange`: Energy per area (J/cm²)
- `scanSpeed`: Scanning speed (mm/s, m/min)
- `overlapRatio`: Pulse overlap percentage (%)

---

## 🧬 Chemical Properties

```yaml
chemicalProperties:
  symbol: string                 # Chemical symbol (e.g., "Fe")
  formula: string                # Chemical formula (e.g., "Fe-C-Cr-Ni")
  materialType: string           # Material classification (e.g., "metal", "alloy", "polymer")
  composition: string            # Detailed composition description
  density: string                # Density value with unit
  meltingPoint: string           # Melting point with unit
  thermalConductivity: string    # Thermal conductivity with unit
```

### Example:
```yaml
chemicalProperties:
  symbol: "SS304"
  formula: "Fe-Cr18-Ni8"
  materialType: "metal alloy"
  composition: "Iron-based alloy with 18% chromium and 8% nickel"
  density: "7.93 g/cm³"
  meltingPoint: "1400-1450°C"
  thermalConductivity: "16.2 W/(m·K)"
```

---

## 📊 Caption Data (Microscopy Images)

### **Structure**: Nested object for before/after image comparisons

```yaml
caption:
  material: string               # Material name
  title: string                  # Caption title
  description: string            # Technical description
  beforeText: string             # ⚠️ Use camelCase (NOT before_text)
  afterText: string              # ⚠️ Use camelCase (NOT after_text)
  images:
    micro:
      url: string                # Microscopy image path
      alt: string                # Alt text
  quality_metrics:               # ⚠️ snake_case for metrics
    surface_roughness_ra: number
    thermal_conductivity: number
    contamination_removal: number
  laserParams:                   # Optional laser parameters
    wavelength: string
    power: string
    pulseWidth: string
```

### Example:
```yaml
caption:
  material: "Stainless Steel 304"
  title: "Surface Analysis Before and After Laser Cleaning"
  description: "Microscopic analysis showing contamination removal"
  beforeText: "Surface exhibits oxide layer and contaminants with Ra 3.2 μm roughness"
  afterText: "Cleaned surface shows uniform finish with Ra 0.8 μm roughness"
  images:
    micro:
      url: "/images/material/stainless-steel-laser-cleaning-micro.jpg"
      alt: "Microscopic comparison of stainless steel surface"
  quality_metrics:
    surface_roughness_ra: 0.8
    thermal_conductivity: 167
    contamination_removal: 99.5
  laserParams:
    wavelength: "1064 nm"
    power: "100 W"
    pulseWidth: "10 ns"
```

**CRITICAL**: 
- ✅ Use `beforeText` and `afterText` (camelCase)
- ❌ Do NOT use `before_text` and `after_text` (deprecated)

---

## 🔗 Content Cards (Unified Structure)

### **Replaces**: Legacy `callouts` and `workflow` fields

```yaml
contentCards:
  - type: string                 # "info", "warning", "success", "workflow"
    heading: string              # Card title
    text: string                 # Card content
    image:                       # Optional image
      url: string
      alt: string
    link:                        # Optional link
      url: string
      text: string
```

### Example:
```yaml
contentCards:
  - type: "info"
    heading: "Safety Considerations"
    text: "Always wear appropriate laser safety eyewear rated for 1064nm wavelength"
    image:
      url: "/images/icons/safety.svg"
      alt: "Safety icon"
  - type: "workflow"
    heading: "Surface Preparation"
    text: "Clean surface with degreaser to remove oils before laser treatment"
  - type: "success"
    heading: "Expected Results"
    text: "Surface roughness reduced from 3.2 μm to 0.8 μm Ra"
```

---

## ⚠️ Legacy Compatibility Fields

### **Maintain These for Backward Compatibility**:

```yaml
subject: string                  # ⚠️ Legacy: Use 'title' instead for new content
author_object: AuthorInfo        # ⚠️ Legacy: Use 'author' instead
technical_specifications: {}     # ⚠️ Legacy: Use 'machineSettings' instead
callouts: []                     # ⚠️ Legacy: Use 'contentCards' instead
workflow: []                     # ⚠️ Legacy: Use 'contentCards' instead
```

**Note**: These fields are deprecated but still supported. New content should use the modern equivalents.

---

## 📝 Complete Example Template

```yaml
---
# Core Fields (Required)
title: "Laser Cleaning Stainless Steel 304 - Technical Guide"
subtitle: "Industrial surface treatment and contamination removal"
description: "Comprehensive technical guide for laser cleaning stainless steel 304 surfaces using nanosecond pulse lasers"
slug: "stainless-steel-304-laser-cleaning"
category: "material"
tags:
  - stainless-steel
  - laser-cleaning
  - surface-treatment
  - industrial-processing

# Author Information
author:
  name: "Dr. Sarah Chen"
  title: "Senior Materials Scientist"
  expertise:
    - "Laser Surface Treatment"
    - "Materials Engineering"
  bio: "15+ years of experience in advanced laser processing"
  email: "sarah.chen@z-beam.com"

# Image Structure (Nested Objects)
images:
  hero:
    url: "/images/material/stainless-steel-304-laser-cleaning-hero.jpg"
    alt: "Industrial laser cleaning stainless steel surface"
    width: 1920
    height: 1080
  micro:
    url: "/images/material/stainless-steel-304-laser-cleaning-micro.jpg"
    alt: "Microscopic view of cleaned surface"
  social:
    url: "/images/material/stainless-steel-304-laser-cleaning-micro-social.jpg"
    alt: "Stainless steel laser cleaning results"

# Chemical Properties
chemicalProperties:
  symbol: "SS304"
  formula: "Fe-Cr18-Ni8"
  materialType: "metal alloy"
  composition: "Austenitic stainless steel with 18% chromium and 8% nickel"
  density: "7.93 g/cm³"
  meltingPoint: "1400-1450°C"
  thermalConductivity: "16.2 W/(m·K)"

# Material Properties (Nested Objects with Units)
properties:
  density:
    value: 7.93
    unit: "g/cm³"
    min: 7.85
    max: 8.03
  meltingPoint:
    value: 1425
    unit: "°C"
    min: 1400
    max: 1450
  thermalConductivity:
    value: 16.2
    unit: "W/(m·K)"
  tensileStrength:
    value: 505
    unit: "MPa"
    min: 485
    max: 620
  youngsModulus:
    value: 193
    unit: "GPa"

# Machine Settings (Nested Objects)
machineSettings:
  powerRange:
    value: 100
    unit: "W"
    min: 50
    max: 200
  wavelength:
    value: 1064
    unit: "nm"
  pulseWidth:
    value: 10
    unit: "ns"
    min: 5
    max: 50
  repetitionRate:
    value: 20
    unit: "kHz"
    min: 10
    max: 100
  spotSize:
    value: 50
    unit: "μm"
  scanSpeed:
    value: 1000
    unit: "mm/s"
    min: 500
    max: 2000
  fluence:
    value: 2.5
    unit: "J/cm²"
    min: 1.5
    max: 5.0

# Caption Data (Microscopy Analysis)
caption:
  material: "Stainless Steel 304"
  title: "Surface Analysis Before and After Laser Cleaning"
  description: "Microscopic analysis showing oxide layer removal"
  beforeText: "Surface exhibits oxide layer and contaminants with Ra 3.2 μm roughness"
  afterText: "Cleaned surface shows uniform finish with Ra 0.8 μm roughness, improved corrosion resistance"
  images:
    micro:
      url: "/images/material/stainless-steel-304-laser-cleaning-micro.jpg"
      alt: "Microscopic comparison of stainless steel surface before and after laser cleaning"
  quality_metrics:
    surface_roughness_ra: 0.8
    thermal_conductivity: 167
    contamination_removal: 99.5
    oxide_layer_thickness: 0
  laserParams:
    wavelength: "1064 nm"
    power: "100 W"
    pulseWidth: "10 ns"
    repetitionRate: "20 kHz"

# Content Cards (Unified Structure)
contentCards:
  - type: "info"
    heading: "Material Characteristics"
    text: "Stainless steel 304 is a versatile austenitic alloy with excellent corrosion resistance"
  - type: "workflow"
    heading: "Surface Preparation"
    text: "Remove loose contaminants with compressed air before laser treatment"
  - type: "workflow"
    heading: "Laser Processing"
    text: "Apply laser treatment in overlapping passes at 50% overlap ratio"
  - type: "success"
    heading: "Quality Results"
    text: "Surface roughness reduced by 75%, oxide layer completely removed"
  - type: "warning"
    heading: "Safety Requirements"
    text: "Wear laser safety eyewear rated for 1064nm wavelength"

# Additional Metadata
keywords:
  - stainless steel 304
  - laser cleaning
  - surface treatment
  - oxide removal
  - industrial cleaning
applications:
  - "Aerospace component cleaning"
  - "Medical device manufacturing"
  - "Food processing equipment"
  - "Automotive parts restoration"
datePublished: "2024-01-15"
lastModified: "2024-01-20"
---

# Markdown Content Here

Your markdown content goes after the frontmatter section...
```

---

## 🎯 Field Naming Quick Reference

### ✅ USE (Preferred - camelCase):
- `beforeText`, `afterText`
- `machineSettings`
- `powerRange`, `pulseWidth`, `repetitionRate`
- `meltingPoint`, `thermalConductivity`
- `contentCards`
- `chemicalProperties`
- `youngsModulus`

### ⚠️ LEGACY (Backward Compatibility Only - snake_case):
- `author_object` → Use `author` instead
- `technical_specifications` → Use `machineSettings` instead
- `quality_metrics` → OK for caption metrics only
- `subject` → Use `title` instead

### ❌ AVOID (Deprecated):
- `before_text`, `after_text` → Use `beforeText`, `afterText`
- `callouts`, `workflow` → Use `contentCards`

---

## 🔍 Validation Checklist

Before generating frontmatter, verify:

- [ ] All field names use **camelCase** (except legacy/metrics fields)
- [ ] File name uses **kebab-case** (e.g., `material-name.md`)
- [ ] `images` structure uses nested objects (`hero.url`, `micro.url`, `social.url`)
- [ ] Image paths follow pattern: `/images/material/{material-name}-laser-cleaning-{type}.jpg`
- [ ] `properties` and `machineSettings` use nested object format with `value`, `unit`, `min`, `max`
- [ ] `caption` uses `beforeText` and `afterText` (NOT `before_text` / `after_text`)
- [ ] `author` is either string or full AuthorInfo object (not `author_object`)
- [ ] `contentCards` is used instead of `callouts` or `workflow`
- [ ] All numeric values with units are properly structured
- [ ] Required fields are present: `title`, `slug`, `description`, `category`

---

## 🚀 Python Generator Integration

### Post-Processing with YAML Validator:

After generating your frontmatter files, run the YAML post-processor to ensure proper formatting:

```python
#!/usr/bin/env python3
import subprocess
import sys

def run_yaml_postprocessor(content_dir="./content"):
    """Run YAML post-processor on generated content."""
    try:
        result = subprocess.run([
            sys.executable, 
            'yaml-processor/yaml_processor.py', 
            content_dir
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ YAML post-processing completed")
        else:
            print(f"⚠️  YAML post-processor warnings:\n{result.stdout}")
    except Exception as e:
        print(f"❌ Could not run YAML post-processor: {e}")

# Call this after your content generation
if __name__ == "__main__":
    # Your content generation logic here
    generate_frontmatter_files()
    
    # Post-process with YAML validator
    run_yaml_postprocessor("./content")
```

---

## 📚 Reference Documentation

- **Type Definitions**: `types/centralized.ts` (lines 145-222: ArticleMetadata interface)
- **Caption Structure**: `docs/CAPTION_QUICK_START.md`
- **Image Paths**: `scripts/analyze-image-paths.js`
- **Component Usage**: `app/components/Caption/Caption.tsx`, `app/components/MetricsCard/MetricsGrid.tsx`

---

## 🎓 Common Patterns

### Pattern 1: Material Properties with Ranges
```yaml
properties:
  density:
    value: 7.85      # Typical value
    unit: "g/cm³"
    min: 7.75        # Range minimum
    max: 8.05        # Range maximum
```

### Pattern 2: Dual Format Support (Prefer Object)
```yaml
# Preferred (nested object):
author:
  name: "Dr. Sarah Chen"
  title: "Senior Scientist"
  expertise: ["Laser Processing"]

# Also supported (simple string):
author: "Dr. Sarah Chen"
```

### Pattern 3: Image Path Consistency
```yaml
# All material images follow this pattern:
images:
  hero:
    url: "/images/material/{kebab-case-name}-laser-cleaning-hero.jpg"
  micro:
    url: "/images/material/{kebab-case-name}-laser-cleaning-micro.jpg"
  social:
    url: "/images/material/{kebab-case-name}-laser-cleaning-micro-social.jpg"
```

---

## ✨ Summary

**Key Takeaways for Python Generator:**

1. **Use camelCase** for all field names (not snake_case, not kebab-case)
2. **Nest objects** for images, properties, machineSettings
3. **Include units** with all numeric values using `value`/`unit`/`min`/`max` structure
4. **Follow image path patterns** consistently
5. **Use `contentCards`** instead of legacy callouts/workflow
6. **Prefer `author` object** over `author_object`
7. **Caption uses `beforeText`/`afterText`** (camelCase, not snake_case)
8. **File names in kebab-case**, field names in camelCase
9. **Run YAML post-processor** after generation for validation

This standardization ensures seamless integration with the Next.js application's type system and component architecture.
