# Materials.yaml → Frontmatter Field Mapping Analysis

**Date**: October 25, 2025  
**Status**: Comprehensive Analysis Complete  
**Purpose**: Document current field mapping, identify inconsistencies, propose normalized structure

---

## Executive Summary

### Issues Identified:
1. **Caption Structure Inconsistency**: Materials.yaml uses both `caption.beforeText` (nested) AND `ai_text_fields.caption_beforeText` (underscore)
2. **Incomplete Field Mapping**: Not all Materials.yaml fields are transferred to frontmatter files
3. **Escaped Line Breaks**: YAML contains `\` escape sequences that should be removed
4. **Missing Micro Images**: Only 25/132 materials have micro images in frontmatter

### Current Status:
- ✅ Caption regeneration: 132/132 complete (100%)
- ⏳ Frontmatter needs regeneration to fix image paths
- ⏳ Materials.yaml needs normalization

---

## 1. Current Materials.yaml → Frontmatter Mapping

### Fields CURRENTLY Mapped:

```yaml
# FROM Materials.yaml → TO Frontmatter
materials:
  MaterialName:
    name → name
    title → title  
    subtitle → subtitle (if not skipped)
    category → category
    description → description
    subcategory → subcategory
    
    # Properties
    properties → properties (with min/max ranges from Categories.yaml)
    materialProperties → materialProperties (categorized)
    materialCharacteristics → materialCharacteristics (qualitative)
    
    # Machine Settings
    machineSettings → machineSettings (with ranges)
    
    # Images
    images.hero → images.hero (with enhanced alt text)
    # ⚠️ MISSING: images.micro (only 25/132 have this)
    
    # Environmental & Outcomes
    environmentalImpact → environmentalImpact
    outcomeMetrics → outcomeMetrics
    
    # Regulatory
    regulatoryStandards → regulatoryStandards
    
    # Author
    author → author (all fields)
    
    # Caption - INCONSISTENT STRUCTURE
    caption.beforeText → caption.beforeText
    caption.afterText → caption.afterText
    caption.author → caption.author
    caption.generated → caption.generated
    caption.generation_method → caption.generation_method
    caption.word_count → caption.word_count
    caption.character_count → caption.character_count
    
    # ⚠️ BUT ALSO in ai_text_fields:
    ai_text_fields.caption_beforeText → (converted to caption.beforeText)
    ai_text_fields.caption_afterText → (converted to caption.afterText)
```

### Fields NOT Currently Mapped:

```yaml
# These exist in Materials.yaml but are NOT in frontmatter:
- applications (list of industries)
- material_metadata (if present)
- ai_text_fields (internal, used to populate other fields)
- captions (legacy field on some materials)
```

---

## 2. Caption Structure Normalization Issue

### Problem:
Materials.yaml has **TWO different caption storage patterns**:

#### Pattern A: Nested Structure (Current Standard - 132 materials)
```yaml
materials:
  Brick:
    caption:
      beforeText: "Under microscopy..."
      afterText: "After thorough cleaning..."
      author: "Todd Dunning"
      generated: "2025-10-25T14:02:48.641990Z"
      generation_method: "ai_research"
      word_count:
        before: 25
        after: 33
      character_count:
        before: 199
        after: 245
```

#### Pattern B: Underscore in ai_text_fields (Legacy - 2 materials: Aluminum, Brass)
```yaml
materials:
  Aluminum:
    ai_text_fields:
      caption_beforeText:
        content: "..."
        generated: "..."
        method: "ai_research"
      caption_afterText:
        content: "..."
        generated: "..."
        method: "ai_research"
```

### Solution Required:
**Migrate Pattern B → Pattern A** for all materials. The nested `caption` structure is cleaner and more consistent.

---

## 3. Escaped Line Breaks in YAML

### Problem:
Some YAML text fields contain `\` escape sequences from AI generation:

```yaml
# Example (hypothetical - need to search):
beforeText: "Surface contamination shows\
  significant buildup with\
  particles measuring..."
```

### Solution:
Run cleanup script to find and remove:
- `\` followed by newline (line continuation)
- Unnecessary escape sequences in text content

---

## 4. Proposed Normalized Frontmatter Structure

### Complete Frontmatter YAML (All Fields from Materials.yaml):

```yaml
# Basic Metadata
name: MaterialName
material: MaterialName  # alias
title: "MaterialName Laser Cleaning"
subtitle: "Laser cleaning parameters and specifications for MaterialName"
category: metal  # or wood, stone, etc.
subcategory: ferrous  # category-specific
description: "Laser cleaning parameters for MaterialName"
generated_date: '2025-10-25T14:45:00.000000'
data_completeness: 100%
source: "Materials.yaml (direct export)"

# Applications (NEW - from Materials.yaml)
applications:
  - Industry 1
  - Industry 2
  - Industry 3

# Properties (Quantitative with Min/Max Ranges)
properties:
  ablationThreshold:
    value: 1.8
    unit: "J/cm²"
    min: 0.5
    max: 2.0
    confidence: 92
    source: ai_research
    research_date: '2025-10-23T11:20:35.380261'
    description: "Ablation threshold description"
  # ... more properties

# Material Properties (Categorized by System)
materialProperties:
  laser_material_interaction:
    description: "Optical, thermal, and surface properties"
    label: "Laser-Material Interaction"
    percentage: 40.0
    properties:
      laserAbsorption:
        value: 8.2
        unit: '%'
        min: 5.0
        max: 15.0
        confidence: 92
        # ... full property structure
  material_characteristics:
    # ... organized by category
  other:
    # ... additional properties

# Material Characteristics (Qualitative - NO min/max)
materialCharacteristics:
  crystallineStructure:
    value: "FCC"
    allowedValues: ["FCC", "BCC", "HCP", ...]
    confidence: 0.95
    description: "Face-centered cubic crystal structure"
    # NOTE: NO min/max fields for qualitative properties

# Category Information
category_info:
  description: "Category description from Categories.yaml"
  properties_count: 13
  category_ranges:
    density:
      min: 6.1
      max: 9.8
      unit: "g/cm³"
      research_basis: "Lanthanides range from La..."
      confidence: 98

# Machine Settings (With Ranges)
machineSettings:
  wavelength:
    value: 1064
    unit: nm
    min: 532
    max: 10600
    confidence: 88
    description: "Near-infrared wavelength for optimal absorption"
  powerRange:
    value: 100
    unit: W
    min: 80
    max: 120
    confidence: 92
    description: "Optimal average power"
  # ... more settings

# Images (Hero + Micro with Enhanced Alt Text)
images:
  hero:
    url: "/images/material/material-laser-cleaning-hero.jpg"
    alt: "Material surface during precision laser cleaning process removing contamination layer at microscopic scale"
  micro:
    url: "/images/material/material-microscopic-before-after.jpg"
    alt: "Material surface at 500x magnification comparing contaminated state with cleaned substrate showing complete restoration"

# Caption (Microscopic Analysis)
caption:
  description: "Microscopic analysis of Material surface before and after laser cleaning treatment"
  beforeText: "Under microscopy, the material surface reveals..."
  afterText: "After laser cleaning, the surface shows..."
  author: "Author Name"
  generated: '2025-10-25T14:02:48.641990Z'
  generation_method: "ai_research"
  word_count:
    before: 25
    after: 33
  character_count:
    before: 199
    after: 245

# Environmental Impact
environmentalImpact:
  - applicableIndustries:
      - Semiconductor
      - Electronics
    benefit: "Chemical Waste Elimination"
    description: "Eliminates hazardous chemical waste streams"
    quantifiedBenefits: "Up to 100% reduction in chemical cleaning agents"
  # ... more impacts

# Outcome Metrics
outcomeMetrics:
  - metric: "Contaminant Removal Efficiency"
    description: "Percentage of target contaminants successfully removed"
    measurementMethods:
      - "Before/after microscopy"
      - "Chemical analysis"
    factorsAffecting:
      - "Contamination type"
      - "Adhesion strength"
    units: []
  # ... more metrics

# Regulatory Standards
regulatoryStandards:
  - "FDA 21 CFR 1040.10 - Laser Product Performance Standards"
  - "ANSI Z136.1 - Safe Use of Lasers"
  - "IEC 60825 - Safety of Laser Products"
  - "OSHA 29 CFR 1926.95 - Personal Protective Equipment"

# Author Information
author:
  country: "Taiwan"
  expertise: "Laser Materials Processing"
  id: 1
  image: "/images/author/yi-chun-lin.jpg"
  name: "Yi-Chun Lin"
  sex: "f"
  title: "Ph.D."
```

---

## 5. Text Fields Candidates for Author Voice

### Current Text Fields Using Author Voice:
1. ✅ **caption.beforeText** - Microscopic "before" description
2. ✅ **caption.afterText** - Microscopic "after" description

### Potential Future Text Fields for Author Voice:
3. ⏳ **description** - Material description (currently template)
4. ⏳ **environmentalImpact[].description** - Environmental benefit descriptions
5. ⏳ **outcomeMetrics[].description** - Outcome metric descriptions
6. ⏳ **FAQ answers** - Future FAQ component (NEW)

### NOT Candidates (Data/Technical Fields):
- properties.*.description - Technical spec descriptions
- machineSettings.*.description - Technical parameter descriptions
- category_info.description - Category definitions

### Recommendation:
**Phase 1** (Current): Caption text only (beforeText, afterText)  
**Phase 2** (Future): Environmental impact & outcome metric descriptions  
**Phase 3** (Future): FAQ component with full voice integration

---

## 6. FAQ Component Requirement (Preliminary)

### Purpose:
Generate material-specific FAQs with absolute material specificity

### Data Structure (Proposed):
```yaml
faq:
  - question: "What makes [Material] suitable for laser cleaning?"
    answer: "[Material-specific answer with technical details about absorption, thermal properties, etc.]"
    category: "Material Properties"
    
  - question: "What laser wavelength works best for [Material]?"
    answer: "[Specific wavelength from machineSettings with scientific rationale]"
    category: "Laser Parameters"
    
  - question: "What contaminants can be removed from [Material]?"
    answer: "[Material-specific contaminants based on applications and properties]"
    category: "Applications"
    
  - question: "Is laser cleaning safe for [Material]?"
    answer: "[Material-specific safety considerations based on thermal properties]"
    category: "Safety"
    
  - question: "What industries use laser cleaning for [Material]?"
    answer: "[List from applications field with use case details]"
    category: "Industries"
```

### Requirements:
1. **Absolute Material Specificity**: Every answer must reference actual material data
2. **Author Voice**: All answers written in assigned author's voice/country style
3. **Technical Accuracy**: Pull from machineSettings, properties, outcomeMetrics
4. **5-7 FAQs per material**: Cover properties, parameters, applications, safety, industries
5. **Dynamic Generation**: Create from Materials.yaml data, not templates

### Data Sources:
- `machineSettings` → Laser parameter questions
- `properties` → Material property questions
- `applications` → Industry/use case questions
- `author` → Voice styling for answers
- `outcomeMetrics` → Performance questions
- `environmentalImpact` → Environmental benefit questions

---

## 7. Action Items

### Immediate (Required Before Frontmatter Regeneration):

1. **Normalize Caption Structure in Materials.yaml**
   - Find materials with `ai_text_fields.caption_*` structure (Aluminum, Brass)
   - Migrate to nested `caption.beforeText/afterText` structure
   - Remove `ai_text_fields.caption_*` fields after migration
   
2. **Remove Escaped Line Breaks**
   - Search Materials.yaml for `\` escape sequences in text fields
   - Remove unnecessary escapes, preserve intentional formatting
   
3. **Add Applications to Frontmatter Mapping**
   - Update `streamlined_generator.py` to include `applications` field
   - Applications list from Materials.yaml → frontmatter.applications

### Next (Frontmatter Regeneration):

4. **Regenerate All 132 Frontmatter Files**
   - Include micro images with enhanced alt text
   - Include applications field
   - Verify caption structure consistency
   - Estimated time: 20-30 minutes

### Future (FAQ Component):

5. **Design FAQ Component Architecture**
   - Create `components/faq/` directory structure
   - Implement FAQ generator following caption component pattern
   - Integrate with voice transformation system
   - Add FAQ field mapping to frontmatter generator

---

## 8. File Location Reference

- **Materials.yaml**: `/Users/todddunning/Desktop/Z-Beam/z-beam-generator/data/materials.yaml`
- **Frontmatter Generator**: `/Users/todddunning/Desktop/Z-Beam/z-beam-generator/components/frontmatter/core/streamlined_generator.py`
- **Frontmatter Files**: `/Users/todddunning/Desktop/Z-Beam/z-beam-generator/content/frontmatter/*.yaml`
- **Caption Generator**: `/Users/todddunning/Desktop/Z-Beam/z-beam-generator/components/caption/`
- **Voice Profiles**: `/Users/todddunning/Desktop/Z-Beam/z-beam-generator/voice/profiles/`

---

## Appendix: Caption Structure Comparison

### Good Structure (132 materials):
```yaml
caption:
  beforeText: "Text..."
  afterText: "Text..."
  author: "Name"
  generated: "2025-10-25T14:02:48Z"
  generation_method: "ai_research"
  word_count:
    before: 25
    after: 33
  character_count:
    before: 199
    after: 245
```

### Legacy Structure (2 materials - needs migration):
```yaml
ai_text_fields:
  caption_beforeText:
    content: "Text..."
    generated: "..."
    method: "ai_research"
  caption_afterText:
    content: "Text..."
    generated: "..."
    method: "ai_research"
```

**Migration Rule**: Extract `content` → `caption.beforeText/afterText`, preserve metadata
