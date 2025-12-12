# Contamination Patterns Frontend Integration Guide

**For**: Frontend AI Assistant  
**Purpose**: Generate contamination pattern pages from Contaminants.yaml data  
**Date**: December 11, 2025

---

## Overview

The contamination patterns domain contains **99 contamination patterns** (oxidation, aging, contamination types) with complete laser removal data. Each pattern needs a dedicated frontend page similar to materials and settings pages.

**Example frontmatter**: See `data/contaminants/FRONTMATTER_EXAMPLE.yaml`

---

## Data Source

**Primary file**: `data/contaminants/Contaminants.yaml` (23,353 lines)

**Structure**:
```yaml
contamination_patterns:
  adhesive-residue:
    author: {...}
    micro:
      before: "..."
      after: "..."
    category: contamination
    context_notes: "..."
    description: "..."
    eeat: {...}
    id: adhesive_residue
    laser_properties:
      laser_parameters: {...}
      optical_properties: {...}
      removal_characteristics: {...}
      safety_data: {...}
    visual_characteristics:
      appearance_on_categories:
        ceramic: {...}
        metal: {...}
        # ... 18 categories total
    valid_materials: [list of 100+ materials]
```

---

## Frontmatter Structure

### 1. Basic Metadata
```yaml
name: Adhesive Residue
slug: adhesive-residue
pattern_id: adhesive_residue
category: contamination  # or: oxidation, aging, biodegradation, photodegradation
content_type: contamination_pattern
schema_version: 1.0.0
datePublished: null
dateModified: null
```

**Mapping**:
- `name` = pattern name (title case)
- `slug` = pattern-id with hyphens
- `pattern_id` = Contaminants.yaml key
- `category` = from `category` field
- Dates remain null (set by CMS)

---

### 2. Author Information

**Source**: `contamination_patterns.{pattern}.author`

```yaml
author:
  id: 4
  name: Ikmanda Roswati
  country: Indonesia
  title: Ph.D.
  jobTitle: Junior Research Scientist in Laser Physics
  # ... complete author object
```

**Note**: Author structure identical to materials/settings domains.

---

### 3. Page Content

**Source**: Multiple fields from Contaminants.yaml

```yaml
title: Adhesive Residue Laser Cleaning
meta_description: Complete guide to laser cleaning adhesive residue...

contamination_description: Sticky residue from labels, tapes, or adhesives
context_notes: Common on manufactured items, shipped goods, or items with labels/tape
```

**Mapping**:
- `title` = "{Name} Laser Cleaning"
- `meta_description` = AI-generated SEO description (100-160 chars)
- `contamination_description` = from `description` field
- `context_notes` = from `context_notes` field

---

### 4. Breadcrumb Navigation

```yaml
breadcrumb:
  - label: Home
    href: /
  - label: Contamination Patterns
    href: /contamination
  - label: Contamination Type  # or Oxidation, Aging, etc.
    href: /contamination/contamination
  - label: Adhesive Residue
    href: /contamination/contamination/adhesive-residue
```

**Logic**:
- Level 1: Always "Contamination Patterns"
- Level 2: Based on `category` field (contamination/oxidation/aging/etc.)
- Level 3: Pattern name
- Final href: `/contamination/{category}/{slug}`

---

### 5. Images

**Source**: `contamination_patterns.{pattern}.micro`

```yaml
images:
  hero:
    before:
      url: /images/contamination/adhesive-residue-before.jpg
      alt: Surface shows contamination from adhesive residue
    after:
      url: /images/contamination/adhesive-residue-after.jpg
      alt: Post-cleaning reveals restored surface

micro:
  before: Surface shows contamination from adhesive residue / tape marks...
  after: Post-cleaning reveals restored surface with adhesive residue...
```

**Mapping**:
- Image URLs: Generate from slug (`/images/contamination/{slug}-before.jpg`)
- Alt text: Abbreviated from micro text (first sentence)
- Micro text: Direct copy from `micro.before` and `micro.after`

**Note**: Images need to be generated separately (image generation system handles this).

---

### 6. Visual Characteristics by Category

**Source**: `contamination_patterns.{pattern}.visual_characteristics.appearance_on_categories`

```yaml
appearance_by_category:
  ceramic:
    appearance: Adhesive residue manifests as a sticky, often translucent layer...
    coverage: Coverage ranges from small, isolated spots to larger sections...
    pattern: It usually forms defined patches or streaks...
  metal:
    appearance: ...
    coverage: ...
    pattern: ...
  # ... 18 categories total
```

**Key Points**:
- **100% coverage**: All 99 patterns have appearance data for all material categories
- Categories: ceramic, composite, concrete, fabric, glass, metal, plastic, stone, wood, etc.
- Each category has 3 fields: appearance, coverage, pattern
- Direct copy from YAML (no transformation needed)

---

### 7. Affected Materials

**Source**: `contamination_patterns.{pattern}.valid_materials`

```yaml
affected_materials:
  categories:
    - ceramic
    - composite
    - concrete
    - fabric
    - glass
    - metal
    - plastic
    - stone
    - wood
  specific_materials:
    - Aluminum
    - Steel
    - Glass
    # ... 100+ materials
```

**Logic**:
- Extract unique categories from `appearance_on_categories` keys
- `specific_materials` = direct copy of `valid_materials` list
- Used for "Materials affected by this contamination" section

---

### 8. Laser Parameters

**Source**: `contamination_patterns.{pattern}.laser_properties.laser_parameters`

```yaml
laser_parameters:
  beam_profile: flat_top
  fluence_range:
    min_j_cm2: 0.3
    max_j_cm2: 1.2
    recommended_j_cm2: 0.8
  pulse_duration_range:
    min_ns: 10
    max_ns: 100
    recommended_ns: 30
  repetition_rate_khz:
    min: 20
    max: 200
    recommended: 50
  wavelength_preference:
    - 1064
    - 532
  scan_speed_mm_s:
    min: 500
    max: 2000
    recommended: 1000
  spot_size_mm:
    min: 0.02
    max: 0.1
    recommended: 0.05
  overlap_percentage: 50
  safety_margin_factor: 0.7
  polarization: circular
```

**Display**: Render as technical specifications table with min/max/recommended values.

---

### 9. Optical Properties

**Source**: `contamination_patterns.{pattern}.laser_properties.optical_properties`

```yaml
optical_properties:
  absorption_coefficient:
    wavelength_1064nm: 850
    wavelength_532nm: 4200
    wavelength_355nm: 18500
  reflectivity:
    wavelength_1064nm: 0.15
    wavelength_532nm: 0.08
    wavelength_355nm: 0.04
  refractive_index:
    real_part: 1.52
    imaginary_part: 0.023
  transmission_depth: 11.8
```

**Display**: Technical table showing wavelength-dependent properties.

---

### 10. Removal Characteristics

**Source**: `contamination_patterns.{pattern}.laser_properties.removal_characteristics`

```yaml
removal_characteristics:
  primary_mechanism: thermal_ablation
  secondary_mechanisms:
    - photochemical
    - mechanical_spallation
  removal_efficiency:
    single_pass: 0.7
    optimal_passes: 3
    diminishing_returns_after: 5
  process_speed:
    typical_scan_speed_mm_s: 800
    area_coverage_rate_cm2_min: 240
  damage_risk_to_substrate: low
  surface_quality_after_removal:
    roughness_increase: minimal
    color_change: no
    residual_stress: compressive
  byproducts:
    - compound: CO2
      phase: gas
      hazard_level: low
    - compound: carbon_particulates
      phase: solid
      hazard_level: moderate
```

**Key Info**:
- Shows how effectively the laser removes this contamination
- Process speeds for ROI calculations
- Byproducts and hazards

---

### 11. Safety Data

**Source**: `contamination_patterns.{pattern}.laser_properties.safety_data`

```yaml
safety_data:
  toxic_gas_risk: moderate
  fire_explosion_risk: low
  particulate_generation:
    size_range_um: [0.1, 10]
    respirable_fraction: 0.7
  fumes_generated:
    - compound: Formaldehyde
      concentration_mg_m3: "1-10"
      exposure_limit_mg_m3: 0.3
      hazard_class: carcinogenic
    - compound: Benzene
      concentration_mg_m3: "0.5-5"
      exposure_limit_mg_m3: 0.5
      hazard_class: carcinogenic
  ppe_requirements:
    eye_protection: goggles
    respiratory: full_face
    skin_protection: gloves
  ventilation_requirements:
    minimum_air_changes_per_hour: 12
    exhaust_velocity_m_s: 0.5
    filtration_type: carbon
  substrate_compatibility_warnings:
    - May cause surface discoloration on painted surfaces
    - Can damage thin coatings or plated surfaces
```

**Critical Section**: Safety data must be prominently displayed with hazard warnings.

---

### 12. Regulatory Standards

**Source**: `contamination_patterns.{pattern}.eeat.citations`

```yaml
regulatoryStandards:
  - name: IEC
    longName: International Electrotechnical Commission
    description: IEC 60825 - Safety of Laser Products
    url: https://webstore.iec.ch/publication/3587
    image: /images/logo/logo-org-iec.png
  - name: OSHA
    longName: Occupational Safety and Health Administration
    description: OSHA 29 CFR 1926.95 - Personal Protective Equipment
    url: https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.102
    image: /images/logo/logo-org-osha.png
```

**Logic**:
- Parse `eeat.citations` list
- Map to standard regulatory body info (IEC, OSHA, ANSI, FDA, etc.)
- Include logo images from `/images/logo/`

---

### 13. E-E-A-T

**Source**: `contamination_patterns.{pattern}.eeat`

```yaml
eeat:
  isBasedOn:
    name: IEC 60825 - Safety of Laser Products
    url: https://webstore.iec.ch/publication/3587
  citations:
    - IEC 60825 - Safety of Laser Products
    - OSHA 29 CFR 1926.95 - Personal Protective Equipment
  reviewedBy: Z-Beam Quality Assurance Team
```

**Purpose**: SEO structured data for expertise/authority/trust signals.

---

### 14. FAQ Section

**Status**: **NOT YET GENERATED** - Needs AI generation

**Format** (same as materials/settings):
```yaml
faq:
  - question: What types of surfaces can adhesive residue contamination affect?
    answer: |-
      **Affects most material categories**. Adhesive residue commonly appears on...
      
      Ikmanda Roswati, Ph.D.
  
  - question: How does laser cleaning remove adhesive residue safely?
    answer: |-
      **Thermal ablation breaks down adhesive bonds**. The laser uses 0.8 J/cm²...
      
      Ikmanda Roswati, Ph.D.
```

**Requirements**:
- 3 questions per pattern (like materials/settings)
- Author signature at end (from pattern's author field)
- **Bold first sentence** pattern
- Technical accuracy (reference laser_parameters, safety_data)

**Generation Needed**:
- Similar to materials domain FAQ generation
- Use pattern-specific data (laser parameters, safety warnings, visual characteristics)
- Maintain author voice consistency

---

## Key Differences from Materials/Settings

### Contamination vs Materials/Settings

| Aspect | Materials | Settings | **Contamination** |
|--------|-----------|----------|-------------------|
| **Primary focus** | Material properties | Machine parameters | Contamination removal |
| **Visual data** | N/A | N/A | **Appearance by category** |
| **Technical specs** | Material properties | Laser settings | **Removal characteristics** |
| **Safety** | Material hazards | Operation safety | **Fume/byproduct hazards** |
| **Breadcrumb** | Materials/{category} | Materials/{material}/settings | **Contamination/{type}/{pattern}** |
| **Images** | Material surface | N/A (settings reuse material images) | **Before/after contamination** |

---

## Data Coverage Status

### Current Status (Dec 11, 2025)

- **Total patterns**: 99
- **With visual_characteristics**: 99/99 (100%)
- **With appearance_on_categories**: 99/99 (100%)
- **With laser_properties**: 99/99 (100%)
- **With safety_data**: 99/99 (100%)

**All data needed for frontmatter generation is complete.**

### Missing: FAQ Content

- **Current**: 0/99 patterns have FAQs
- **Needed**: Generate 3 FAQs per pattern (297 FAQs total)
- **Method**: Similar to materials/settings FAQ generation
- **Priority**: Medium (pages can launch without FAQs, add later)

---

## URL Structure

**Pattern**: `/contamination/{category}/{slug}`

**Examples**:
- `/contamination/contamination/adhesive-residue`
- `/contamination/oxidation/rust-oxidation`
- `/contamination/aging/weathering`
- `/contamination/biodegradation/mold-growth`

**Category values**:
- `contamination` (6 patterns)
- `oxidation` (2 patterns)
- `aging` (1 pattern)
- `biodegradation` (1 pattern)
- `photodegradation` (1 pattern)
- `unknown` (88 patterns) - **Note**: These need category assignment

---

## Frontend Page Components

### Recommended Sections (in order)

1. **Hero Section**
   - Title: "{Name} Laser Cleaning"
   - Before/after images
   - Micro text

2. **Overview**
   - Contamination description
   - Context notes
   - Affected materials summary

3. **Visual Characteristics**
   - Tabs or accordion for each material category
   - Show appearance, coverage, pattern for each

4. **Laser Removal Parameters**
   - Technical specifications table
   - Recommended settings highlighted

5. **Removal Process**
   - Primary/secondary mechanisms
   - Removal efficiency chart
   - Process speeds

6. **Safety Information** ⚠️
   - Hazard warnings (prominent display)
   - Fumes/byproducts list
   - PPE requirements
   - Ventilation requirements
   - Substrate compatibility warnings

7. **Optical Properties**
   - Absorption coefficients by wavelength
   - Reflectivity data
   - Refractive index

8. **FAQ Section**
   - 3 questions per pattern
   - Author attribution

9. **Related Content**
   - Links to affected materials pages
   - Links to similar contamination patterns
   - Links to category overview page

10. **Regulatory/E-E-A-T**
    - Standards badges/logos
    - Citations
    - Reviewed by statement

---

## Implementation Steps

### Phase 1: Frontmatter Generation

1. **Parse Contaminants.yaml**
   - Read all 99 patterns
   - Extract data for frontmatter fields

2. **Generate frontmatter files**
   - Create YAML files in `frontmatter/contaminants/`
   - Naming: `{slug}-laser-cleaning.yaml`
   - Example: `adhesive-residue-laser-cleaning.yaml`

3. **Handle special cases**
   - Patterns with category="unknown" (88 patterns) - assign appropriate categories
   - Missing data fields (should be none, but validate)

### Phase 2: FAQ Generation

1. **Setup generation system**
   - Similar to materials/settings FAQ generation
   - Use pattern-specific prompts

2. **Generate 3 FAQs per pattern**
   - Question 1: What types of surfaces / When is this contamination found?
   - Question 2: How does laser cleaning remove this contamination?
   - Question 3: What safety precautions are needed?

3. **Add author signatures**
   - Use pattern's author from `author` field
   - Format: "{Author Name}, {Title}"

### Phase 3: Image Generation

1. **Generate before/after images**
   - 99 patterns × 2 images = 198 images
   - Use existing image generation system
   - Save to `/images/contamination/{slug}-before.jpg` and `-after.jpg`

2. **Image requirements**
   - Show contamination clearly (before)
   - Show clean surface (after)
   - Realistic lighting and context

---

## Validation Checklist

Before generating pages, verify:

- [ ] All 99 patterns have complete data
- [ ] All patterns have assigned category (not "unknown")
- [ ] All appearance_on_categories have 3 fields (appearance, coverage, pattern)
- [ ] All laser_parameters have min/max/recommended values
- [ ] All safety_data includes fumes_generated list
- [ ] All author information is complete
- [ ] Breadcrumb logic handles all category types
- [ ] URL slugs are valid (no special characters)

---

## Questions for Backend Team

1. **Category Assignment**: 88 patterns have category="unknown". Should these be researched and assigned proper categories?

2. **FAQ Generation**: Should we use the existing materials/settings FAQ generation system, or create contamination-specific prompts?

3. **Image Generation**: Should before/after images be AI-generated or use stock photography?

4. **URL Structure**: Confirm `/contamination/{category}/{slug}` structure is acceptable.

5. **Missing Fields**: Are there any additional frontmatter fields needed beyond what's in materials/settings examples?

---

## Contact

For questions about this integration, refer to:
- **Example file**: `data/contaminants/FRONTMATTER_EXAMPLE.yaml`
- **Source data**: `data/contaminants/Contaminants.yaml`
- **Materials example**: `frontmatter/materials/aluminum-laser-cleaning.yaml`
- **Settings example**: `frontmatter/settings/aluminum-settings.yaml`

---

**Last Updated**: December 11, 2025  
**Status**: Ready for frontend implementation  
**Data Completeness**: 100% (visual characteristics, laser properties, safety data)  
**Missing**: FAQ content (297 FAQs needed)
