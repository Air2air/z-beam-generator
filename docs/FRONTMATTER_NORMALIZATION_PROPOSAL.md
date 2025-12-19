# Frontmatter Key Normalization Proposal

**Date**: December 18, 2025  
**Status**: Architectural Proposal  
**Impact**: All 654 frontmatter files (materials, contaminants, compounds, settings)

---

## Executive Summary

**Problem**: Frontmatter files have many scattered, non-normalized keys at various levels (top-level, nested, inconsistent naming). This creates:
- Difficulty finding related data
- Inconsistent access patterns
- Hard to maintain relationships
- Poor discoverability for generators/consumers

**Solution**: Normalize all relationship, safety, and reference data under a unified `relationships` schema, following the successful pattern already used for `related_materials` and `related_contaminants`.

---

## Current State Analysis

### Well-Normalized (Good Pattern)
```yaml
relationships:
  related_materials:
  - id: aluminum-laser-cleaning
    title: Aluminum
    url: /materials/aluminum-laser-cleaning
    image: /images/materials/aluminum-laser-cleaning.jpg
    frequency: common
    severity: moderate
    typical_context: general
  
  related_contaminants:
  - id: rust-corrosion-contamination
    # ... same structure
```

✅ **Benefits of this pattern**:
- Consistent structure
- Easy to validate
- Clear relationships
- Predictable access

---

### Currently Scattered (Problem Areas)

#### 1. **Safety & Compliance Data**
**Current**: Scattered at top level
```yaml
# Top-level scattered keys
ppe_requirements:
  respiratory: "..."
  skin: "..."
  eye: "..."

regulatory_classification:
  un_number: UN1089
  dot_hazard_class: "..."

regulatory_standards:
- description: "FDA 21 CFR..."
  name: FDA
  url: "..."

exposure_limits:
  osha_pel_ppm: 200
  # ...
```

**Issues**:
- Different structures for similar data
- Hard to discover all safety information
- No consistent linkage pattern
- Mixes atomic values with complex objects

---

#### 2. **Compound/Chemical References**
**Current**: Multiple scattered locations
```yaml
# In compounds - at relationships level
relationships:
  produced_by_contaminants:
  - id: plastic-residue
    title: "..."
    url: "..."

# In contaminants - at top level
prohibited_materials:
- Electronics

valid_materials:
- Steel
- Aluminum
```

**Issues**:
- Same concept (`related_materials`) in different places
- Inconsistent data structures
- String arrays vs object arrays

---

#### 3. **Technical Data**
**Current**: Mixed structures
```yaml
# Contaminants
laser_properties:
  laser_parameters:
    beam_profile: flat_top
    # ...
  optical_properties:
    # ...
  safety_data:
    # ...

# Settings
machine_settings:
  powerRange:
    value: 100
    unit: W
```

**Issues**:
- Deep nesting makes access complex
- No clear relationship to source materials
- Difficult to cross-reference

---

## Proposed Normalized Schema

### Core Principles

1. **Unified Schema**: ALL relationship entries use a single, standardized schema with optional fields
2. **Normalization**: ALL data except page-specific fields lives under the `relationships` key
3. **Consistency**: Same structure regardless of relationship type (materials, contaminants, compounds, standards, etc.)
4. **Extensibility**: Optional fields allow type-specific data without breaking the unified schema

### What Stays at Top-Level (Page-Specific Only)

```yaml
# Identity & Metadata
id: acetaldehyde
name: Acetaldehyde
display_name: Acetaldehyde (C₂H₄O)
slug: acetaldehyde
title: "..." # For materials/contaminants

# Taxonomy
category: irritant
subcategory: aldehyde
content_type: compounds
schema_version: 5.0.0

# Timestamps
datePublished: '2025-12-18T21:23:41.336901Z'
dateModified: '2025-12-18T21:23:41.336901Z'

# Content Fields
description: "..." # Main description
micro: {...}      # Micro content for materials/contaminants
faq: [...]        # FAQ for materials

# Author
author:
  id: 1

# Page Images
images:
  hero: {...}
  micro: {...}

# Navigation
breadcrumb_text: "..."
```

**Everything else goes into `relationships`**

### Proposed Unified Schema

All relationship entries follow this single schema:

```yaml
relationships:
  [relationship_type]:  # e.g., related_materials, regulatory_standards, etc.
  - # ============================================
    # REQUIRED FIELDS (All entries MUST have)
    # ============================================
    id: string                    # Unique identifier
    title: string                 # Display name
    url: string                   # Link to entity
    
    # ============================================
    # CORE OPTIONAL FIELDS (Common across types)
    # ============================================
    image: string                 # Image path
    description: string           # Brief explanation
    notes: string                 # Additional context
    
    # ============================================
    # RELATIONSHIP METADATA (When applicable)
    # ============================================
    frequency: string             # common | uncommon | rare | very_common
    severity: string              # high | moderate | low | critical
    typical_context: string       # When/where this applies
    
    # ============================================
    # TYPE-SPECIFIC OPTIONAL FIELDS
    # ============================================
    # Chemical/Compound specific
    cas_number: string
    hazard_class: string
    concentration_range: string
    chemical_formula: string
    molecular_weight: number
    
    # Regulatory/Standards specific
    authority: string
    compliance_level: string      # mandatory | recommended | optional
    applicability: string
    effective_date: string
    
    # Production/Source specific
    production_mechanism: string
    decomposition_temp: string
    typical_conditions: string
    
    # Compatibility specific
    compatibility: string         # high | moderate | low | incompatible
    reason: string                # Why prohibited/recommended
    
    # Settings/Equipment specific
    success_rate: string          # high | moderate | low
    power_range: string
    recommended_for: string[]
    
    # Safety/PPE specific
    equipment_type: string
    protection_level: string
    standard: string
    condition: string
```

**Key Points**:
- ✅ Every relationship entry has `id`, `title`, `url` (minimum required)
- ✅ All other fields are optional - use only when data exists
- ✅ No need for different schemas per type - one schema fits all
- ✅ Easy to add new optional fields without breaking existing entries

---

### Example: Unified Schema in Practice

All relationship types use the same base schema:

```yaml
relationships:
  # ================================================
  # MATERIALS (Uses: id, title, url, image, frequency, severity, typical_context)
  # ================================================
  related_materials:
  - id: aluminum-laser-cleaning
    title: Aluminum
    url: /materials/aluminum-laser-cleaning
    image: /images/materials/aluminum-laser-cleaning.jpg
    frequency: common
    severity: moderate
    typical_context: general
    notes: High reflectivity requires power adjustment
  
  # ================================================
  # CONTAMINANTS (Uses: id, title, url, image, frequency, severity, typical_context)
  # ================================================
  related_contaminants:
  - id: rust-corrosion-contamination
    title: Rust / Iron Oxide Corrosion
    url: /contaminants/rust-corrosion-contamination
    image: /images/contaminants/rust-corrosion-contamination.jpg
    frequency: common
    severity: high
    typical_context: general
    description: Common oxide contamination on ferrous metals
  
  # ================================================
  # COMPOUNDS (Uses: id, title, url, image, cas_number, hazard_class, 
  #            concentration_range, frequency, severity, typical_context)
  # ================================================
  related_compounds:
  - id: acetaldehyde
    title: Acetaldehyde (C₂H₄O)
    url: /compounds/acetaldehyde
    image: /images/compounds/acetaldehyde.jpg
    cas_number: 75-07-0
    hazard_class: irritant
    concentration_range: 5-25 mg/m³
    frequency: common
    severity: moderate
    typical_context: Decomposition of vinyl and acrylic adhesives
    chemical_formula: C2H4O
    molecular_weight: 44.05
  
  # ================================================
  # PRODUCTION SOURCES (Uses: id, title, url, image, production_mechanism,
  #                     frequency, severity, typical_context)
  # ================================================
  produced_by_contaminants:
  - id: plastic-residue-contamination
    title: Degraded Polymer Deposits
    url: /contaminants/plastic-residue-contamination
    image: /images/contaminants/plastic-residue-contamination.jpg
    production_mechanism: Thermal degradation of polyethylene
    frequency: common
    severity: moderate
    typical_context: High-power laser cleaning of polymers
    decomposition_temp: 300-400°C
  
  # ================================================
  # REGULATORY STANDARDS (Uses: id, title, url, image, authority, 
  #                       compliance_level, applicability)
  # ================================================
  regulatory_standards:
  - id: fda-laser-product-performance
    title: FDA 21 CFR 1040.10 - Laser Product Performance Standards
    authority: FDA
    url: https://www.ecfr.gov/current/title-21/chapter-I/subchapter-J/part-1040/section-1040.10
    image: /images/logo/logo-org-fda.png
    applicability: All laser cleaning equipment
    compliance_level: mandatory
    effective_date: '1976-08-02'
  
  # ================================================
  # MATERIAL COMPATIBILITY (Uses: id, title, url, compatibility, notes)
  # ================================================
  compatible_materials:
  - id: steel-laser-cleaning
    title: Steel
    url: /materials/steel-laser-cleaning
    image: /images/materials/steel-laser-cleaning.jpg
    compatibility: high
    notes: Excellent absorption at 1064nm
    recommended_for: [rust_removal, oxide_cleaning, paint_stripping]
  
  # ================================================
  # PROHIBITED MATERIALS (Uses: id, title, reason, severity)
  # ================================================
  prohibited_materials:
  - id: electronics-pcb
    title: Electronics (PCB)
    url: /materials/electronics-pcb
    reason: Component damage risk from thermal shock
    severity: critical
    notes: Use low-power alternatives or mechanical cleaning only
  
  # ================================================
  # RECOMMENDED SETTINGS (Uses: id, title, url, image, success_rate,
  #                       applicability, power_range)
  # ================================================
  recommended_settings:
  - id: aluminum-bronze-settings
    title: Aluminum Bronze Settings
    url: /settings/aluminum-bronze-settings
    image: /images/settings/aluminum-bronze-settings.jpg
    applicability: Oxide removal on aluminum alloys
    success_rate: high
    power_range: 80-120W
    recommended_for: [surface_cleaning, oxide_removal]
```

**Benefits of Unified Schema**:
- ✅ Same fields available to all relationship types
- ✅ Only populate fields with actual data
- ✅ Easy to add new fields - just make them optional
- ✅ Consistent validation and TypeScript interfaces
- ✅ Predictable access patterns in code

---

## Detailed Structure by Content Type
  # ================================================
  # CROSS-REFERENCES (Existing Pattern)
  # ================================================
  related_materials:
  - id: aluminum-laser-cleaning
    title: Aluminum
    url: /materials/aluminum-laser-cleaning
    image: /images/materials/aluminum-laser-cleaning.jpg
    frequency: common
    severity: moderate
    typical_context: general
  
  related_contaminants:
  - id: rust-corrosion-contamination
    title: Rust / Iron Oxide Corrosion
    url: /contaminants/rust-corrosion-contamination
    image: /images/contaminants/rust-corrosion-contamination.jpg
    frequency: common
    severity: high
    typical_context: general
  
  related_compounds:
  - id: acetaldehyde
    title: Acetaldehyde (C₂H₄O)
    url: /compounds/acetaldehyde
    image: /images/compounds/acetaldehyde.jpg
    cas_number: 75-07-0
    hazard_class: irritant
    concentration_range: 5-25 mg/m³
    frequency: common
    severity: moderate
    typical_context: Decomposition of vinyl and acrylic adhesives
  
  produced_by_contaminants:
  - id: plastic-residue-contamination
    title: Degraded Polymer Deposits
    url: /contaminants/plastic-residue-contamination
    image: /images/contaminants/plastic-residue-contamination.jpg
    production_mechanism: Thermal degradation of polyethylene
    frequency: common
    severity: moderate
    typical_context: High-power laser cleaning of polymers
  
  # ================================================
  # REGULATORY & STANDARDS
  # ================================================
  regulatory_standards:
  - id: fda-laser-product-performance
    title: FDA 21 CFR 1040.10 - Laser Product Performance Standards
    authority: FDA
    url: https://www.ecfr.gov/current/title-21/chapter-I/subchapter-J/part-1040/section-1040.10
    image: /images/logo/logo-org-fda.png
    applicability: All laser cleaning equipment
    compliance_level: mandatory
  
  regulatory_classification:
    un_number: UN1089
    dot_hazard_class: 3 (Flammable liquid)
    dot_label: Flammable Liquid
    nfpa_codes:
      health: 2
      flammability: 4
      reactivity: 2
      special: null
    epa_hazard_categories:
    - Flammability
    - Acute toxicity
    - Carcinogenicity (probable)
    sara_title_iii: true
    cercla_rq: 1000 pounds (454 kg)
    rcra_code: U001
  
  # ================================================
  # SAFETY & PPE
  # ================================================
  ppe_requirements:
    respiratory: NIOSH-approved organic vapor respirator for <25 ppm
    skin: Nitrile or butyl rubber gloves
    eye: Chemical safety goggles, face shield for splash hazard
    minimum_level: Level C for <25 ppm, Level B for >25 ppm
    special_notes: Probable human carcinogen (IARC Group 2B)
  
  emergency_response:
    fire_hazard: EXTREMELY FLAMMABLE. Wide explosive range.
    fire_suppression: EVACUATE - explosion hazard. Stop flow if safe.
    spill_procedures: EVACUATE. Eliminate ignition sources. Ventilate area.
    exposure_immediate_actions: Remove to fresh air immediately.
    environmental_hazards: Toxic to aquatic life. Report spills.
    special_hazards: PROBABLE HUMAN CARCINOGEN (IARC 2B).
  
  # ================================================
  # MATERIAL COMPATIBILITY
  # ================================================
  compatible_materials:
  - id: steel-laser-cleaning
    title: Steel
    url: /materials/steel-laser-cleaning
    compatibility: high
    notes: Excellent absorption at 1064nm
  
  prohibited_materials:
  - id: electronics-pcb
    title: Electronics (PCB)
    reason: Component damage risk
    severity: critical
  
  # ================================================
  # TECHNICAL PROPERTIES
  # ================================================
  physical_properties:
    boiling_point: 20.2°C (68.4°F)
    melting_point: -123.5°C (-190.3°F)
    vapor_pressure: 740 mmHg @ 20°C
    vapor_density: 1.52 (Air=1)
    specific_gravity: 0.788 @ 20°C
    flash_point: -39°C (-38°F)
    autoignition_temp: 175°C (347°F)
    explosive_limits: 'LEL: 4%, UEL: 60%'
    appearance: Colorless liquid, colorless gas >20°C
    odor: Pungent, fruity odor @ 0.05-1 ppm
  
  laser_properties:
    laser_parameters:
      beam_profile: flat_top
      fluence_range:
        max_j_cm2: 1.2
        min_j_cm2: 0.3
        recommended_j_cm2: 0.7
      overlap_percentage: 50
      # ... full structure
    optical_properties:
      absorption_coefficient: {...}
      reflectivity: {...}
    removal_characteristics:
      byproducts: [...]
      damage_risk_to_substrate: low
      primary_mechanism: thermal_ablation
    safety_data:
      fire_explosion_risk: low
      fumes_generated: [...]
      particulate_generation: {...}
  
  machine_settings:
    powerRange:
      value: 100
      unit: W
      description: Optimal average power for metal oxide removal
    wavelength:
      value: 1064
      unit: nm
      description: Near-IR wavelength for optimal metal absorption
    # ... full settings
  
  # ================================================
  # EXPOSURE & MONITORING
  # ================================================
  exposure_limits:
    osha_pel_ppm: 200
    osha_pel_mg_m3: 360
    niosh_rel_ppm: null
    acgih_tlv_ppm: 25
    acgih_tlv_mg_m3: 45
  
  workplace_exposure:
    osha_pel:
      twa_8hr: 200 ppm (360 mg/m³)
      stel_15min: null
      ceiling: null
    niosh_rel:
      ceiling: 10 ppm (18 mg/m³) - based on carcinogenicity
      idlh: 2000 ppm
    acgih_tlv:
      ceiling: 25 ppm
    biological_exposure_indices: []
  
  detection_monitoring:
    sensor_types:
    - Photoionization detector (PID)
    - Electrochemical
    detection_range: 0-100 ppm typical
    alarm_setpoints:
      low: 10 ppm (NIOSH ceiling)
      high: 25 ppm (ACGIH ceiling)
      evacuate: 2000 ppm (NIOSH IDLH)
    analytical_methods:
    - method: NIOSH 2538
      technique: GC-FID
      detection_limit: 0.01 ppm
  
  # ================================================
  # CHEMICAL DATA
  # ================================================
  chemical_properties:
    chemical_formula: C2H4O
    cas_number: 75-07-0
    molecular_weight: 44.05
    hazard_class: irritant
  
  reactivity:
    stability: UNSTABLE. Polymerizes readily.
    polymerization: Violent exothermic polymerization
    incompatible_materials:
    - Strong acids
    - Strong bases
    - Oxidizers
    hazardous_decomposition:
    - Carbon monoxide
    - Carbon dioxide
    conditions_to_avoid:
    - Heat
    - Sparks
    - Flames
    reactivity_hazard: EXTREMELY REACTIVE.
  
  environmental_impact:
    aquatic_toxicity: 'Toxic to aquatic life. LC50 (fish, 96h): 50-150 mg/L.'
    biodegradability: Readily biodegradable (>70% in 28 days)
    bioaccumulation: 'Does not bioaccumulate. Log Kow: -0.34.'
    soil_mobility: High mobility
    atmospheric_fate: 'Photolyzes rapidly. Half-life: 9 hours.'
    reportable_releases:
      water: 1000 lbs to navigable waters
      air: 1000 lbs/day (CERCLA RQ)
  
  storage_requirements:
    temperature_range: Store below 20°C, refrigerate
    ventilation: Explosion-proof ventilation required
    incompatibilities:
    - Acids
    - Bases
    - Oxidizers
    container_material: Stainless steel or aluminum
    segregation: Separate from oxidizers by 20 feet
    quantity_limits: Many facilities limit to <10 gallons
    special_requirements: Store with stabilizer. Refrigerated storage required.
  
  # ================================================
  # IDENTIFIERS & METADATA
  # ================================================
  synonyms_identifiers:
    synonyms:
    - Acetic aldehyde
    - Ethanal
    - Ethyl aldehyde
    common_trade_names: []
    other_identifiers:
      rtecs_number: AB1925000
      ec_number: 200-836-8
      pubchem_cid: '177'
  
  health_effects_keywords:
  - respiratory_irritation
  - eye_irritation
  - suspected_carcinogen
  - narcotic_effects
  
  sources_in_laser_cleaning:
  - alcohol_oxidation
  - polymer_decomposition
  - organic_solvent_breakdown
  
  # ================================================
  # MATERIAL-SPECIFIC
  # ================================================
  material_properties:
    mechanical:
      tensile_strength: {...}
      hardness: {...}
    thermal:
      thermal_conductivity: {...}
      thermal_expansion: {...}
    optical:
      reflectivity: {...}
      absorption: {...}
  
  applications:
  - industry: aerospace
    use_cases: [...]
  - industry: automotive
    use_cases: [...]
  
  characteristics:
    advantages: [...]
    limitations: [...]
    typical_applications: [...]
  
  # ================================================
  # CONTAMINANT-SPECIFIC
  # ================================================
  composition:
  - compound: "..."
    percentage: "..."
  
  visual_characteristics:
    appearance_on_categories:
      metal:
        appearance: "..."
        coverage: "..."
        pattern: "..."
  
  # ================================================
  # SETTINGS-SPECIFIC
  # ================================================
  challenges:
  - "Requires careful power calibration"
  - "Monitor surface temperature during processing"
  
  recommended_settings:
  - id: aluminum-bronze-settings
    title: Aluminum Bronze Settings
    url: /settings/aluminum-bronze-settings
    applicability: Oxide removal
    success_rate: high
```

---

## Migration Strategy

### Phase 1: Analysis (Week 1)
1. **Inventory all scattered keys** across all content types
2. **Map current usage patterns** (who reads what keys)
3. **Identify breaking changes** for existing consumers
4. **Design backward compatibility layer**

### Phase 2: Schema Design (Week 1-2)
1. **Define normalized structures** for each relationship type
2. **Create TypeScript interfaces** for validation
3. **Document migration patterns** for each scattered key
4. **Build validation tools**

### Phase 3: Generator Updates (Week 2-3)
1. **Update frontmatter generators** to output new schema
2. **Add backward compatibility** (write both old and new formats temporarily)
3. **Test with sample files**
4. **Validate against TypeScript schemas**

### Phase 4: Consumer Updates (Week 3-4)
1. **Update all components** reading frontmatter
2. **Update GraphQL schemas** (if applicable)
3. **Update API endpoints**
4. **Test all pages render correctly**

### Phase 5: Migration (Week 4-5)
1. **Regenerate all 654 frontmatter files** with new schema
2. **Validate all files** against schema
3. **Test all pages** still work
4. **Remove backward compatibility code**

### Phase 6: Cleanup (Week 5)
1. **Remove old scattered keys**
2. **Update all documentation**
3. **Remove compatibility layer**
4. **Final validation**

---

## Benefits

### 1. **Consistency**
- All relationship data follows same pattern
- Easy to understand and maintain
- Predictable for new developers

### 2. **Discoverability**
- All related data in one place
- Clear relationship types
- Easy to explore connections

### 3. **Maintainability**
- Single validation schema
- Consistent access patterns
- Easy to add new relationship types

### 4. **Extensibility**
- New relationship types follow same pattern
- No need to scatter new keys
- Clear upgrade path

### 5. **Type Safety**
- TypeScript interfaces for all relationship types
- Compile-time validation
- Better IDE support

---

## Key Mapping Table

| Current Location | Current Key | New Location | New Key |
|-----------------|-------------|--------------|---------|
| Top-level | `regulatory_standards` | `relationships` | `regulatory_standards` |
| Top-level | `ppe_requirements` | `relationships` | `ppe_recommendations` |
| Top-level | `prohibited_materials` | `relationships` | `prohibited_materials` |
| Top-level | `valid_materials` | `relationships` | `compatible_materials` |
| `relationships` | `produced_by_contaminants` | `relationships` | `produced_by_contaminants` |
| Top-level | `exposure_limits` | Keep top-level | `exposure_limits` (atomic data) |
| Top-level | `physical_properties` | Keep top-level | `physical_properties` (atomic data) |
| Top-level | `laser_properties` | Keep top-level | `laser_properties` (atomic data) |
| Top-level | `machine_settings` | Keep top-level | `machine_settings` (atomic data) |

### Decision Rules

**MOVE to `relationships`:**
- ✅ References other entities (materials, contaminants, compounds, standards)
- ✅ Has ID/URL/title pattern
- ✅ Represents a relationship between entities

**KEEP at top-level:**
- ✅ Atomic property values (numbers, strings, simple objects)
- ✅ Intrinsic properties (molecular weight, boiling point)
- ✅ Technical specifications (laser parameters, machine settings)
- ✅ Does NOT reference other entities

---

## Example: Before & After

### BEFORE (Scattered)

```yaml
id: acetaldehyde
name: Acetaldehyde
# ... basic fields ...

# Scattered at top level
ppe_requirements:
  respiratory: NIOSH-approved organic vapor respirator
  skin: Nitrile gloves
  eye: Safety goggles

regulatory_classification:
  un_number: UN1089
  dot_hazard_class: 3

# In relationships
relationships:
  produced_by_contaminants:
  - id: plastic-residue
    title: "..."
```

### AFTER (Normalized)

```yaml
id: acetaldehyde
name: Acetaldehyde
# ... basic fields ...

# Atomic properties stay at top-level
exposure_limits:
  osha_pel_ppm: 200

physical_properties:
  boiling_point: 20.2°C

# All relationships consolidated
relationships:
  produced_by_contaminants:
  - id: plastic-residue-contamination
    title: Degraded Polymer Deposits
    url: /contaminants/plastic-residue-contamination
    image: /images/contaminants/plastic-residue-contamination.jpg
    production_mechanism: Thermal degradation
    frequency: common
    severity: moderate
    typical_context: High-power polymer cleaning
  
  regulatory_standards:
  - id: dot-un1089
    title: UN1089 - Flammable Liquid Classification
    authority: DOT
    url: https://...
    compliance_level: mandatory
  
  ppe_recommendations:
  - equipment_type: respiratory
    level: NIOSH-approved organic vapor respirator
    condition: For concentrations <25 ppm
    standard: NIOSH 42 CFR 84
```

---

## 5. Complete Before/After Examples

### Example 1: Compound Frontmatter (acetaldehyde-compound.yaml)

#### ❌ BEFORE (Current - Scattered Keys Everywhere)
```yaml
---
# Page-specific fields
id: acetaldehyde-compound
name: Acetaldehyde
schema_version: 5.0.0
category: compounds
datePublished: '2024-11-15'
dateModified: '2024-11-15'
description: Colorless, flammable gas with pungent odor...
author: Dr. Sophia Chen

# ⚠️ PROBLEM: Safety data scattered at top-level
ppe_requirements:
  respiratory: NIOSH-approved organic vapor respirator for <25 ppm
  skin: Nitrile or butyl rubber gloves
  eye: Chemical safety goggles, face shield for splash hazard
  minimum_level: Level C for <25 ppm, Level B for >25 ppm

emergency_response:
  fire_hazard: EXTREMELY FLAMMABLE. Wide explosive range.
  fire_suppression: EVACUATE - explosion hazard.
  spill_procedures: EVACUATE. Eliminate ignition sources.
  exposure_immediate_actions: Remove to fresh air immediately.

storage_requirements:
  temperature_range: Store below 20°C, refrigerate
  ventilation: Explosion-proof ventilation required
  incompatibilities: [Acids, Bases, Oxidizers]

# ⚠️ PROBLEM: Regulatory data scattered at top-level
regulatory_classification:
  un_number: UN1089
  dot_hazard_class: 3 (Flammable liquid)
  nfpa_codes:
    health: 2
    flammability: 4
    reactivity: 2

# ⚠️ PROBLEM: Chemical properties scattered at top-level
physical_properties:
  boiling_point: 20.2°C (68.4°F)
  melting_point: -123.5°C (-190.3°F)
  vapor_pressure: 740 mmHg @ 20°C
  vapor_density: 1.52 (Air=1)
  specific_gravity: 0.788 @ 20°C
  flash_point: -39°C (-38°F)
  autoignition_temp: 175°C (347°F)
  explosive_limits: 'LEL: 4%, UEL: 60%'

reactivity:
  stability: UNSTABLE. Polymerizes readily.
  polymerization: Violent exothermic polymerization
  incompatible_materials: [Strong acids, Strong bases, Oxidizers]

environmental_impact:
  aquatic_toxicity: 'Toxic to aquatic life. LC50 (fish, 96h): 50-150 mg/L.'
  biodegradability: Readily biodegradable (>70% in 28 days)
  bioaccumulation: 'Does not bioaccumulate. Log Kow: -0.34.'
  soil_mobility: High mobility

# ⚠️ PROBLEM: Exposure/monitoring data scattered at top-level
workplace_exposure:
  osha_pel:
    twa_8hr: 200 ppm (360 mg/m³)
  niosh_rel:
    ceiling: 10 ppm (18 mg/m³)
  acgih_tlv:
    ceiling: 25 ppm

exposure_limits:
  osha_pel_ppm: 200
  osha_pel_mg_m3: 360
  acgih_tlv_ppm: 25

detection_monitoring:
  sensor_types: [Photoionization detector (PID), Electrochemical]
  detection_range: 0-100 ppm typical
  alarm_setpoints:
    low: 10 ppm
    high: 25 ppm

# ⚠️ PROBLEM: Identifiers scattered at top-level
synonyms_identifiers:
  synonyms: [Acetic aldehyde, Ethanal, Ethyl aldehyde]
  other_identifiers:
    rtecs_number: AB1925000
    ec_number: 200-836-8

health_effects_keywords:
- respiratory_irritation
- eye_irritation
- suspected_carcinogen

sources_in_laser_cleaning:
- alcohol_oxidation
- polymer_decomposition

# ✅ GOOD: Only part properly structured
relationships:
  produced_by_contaminants:
  - id: plastic-residue-contamination
    title: Degraded Polymer Deposits
    url: /contaminants/plastic-residue-contamination
---
```

#### ✅ AFTER (Proposed - Everything Under relationships)
```yaml
---
# ================================================
# PAGE-SPECIFIC FIELDS ONLY (Top-Level)
# ================================================
id: acetaldehyde-compound
name: Acetaldehyde
schema_version: 5.0.0
category: compounds
content_type: compound
datePublished: '2024-11-15'
dateModified: '2024-11-15'
description: Colorless, flammable gas with pungent odor...
micro: Probable carcinogen. Extremely flammable gas...
author: Dr. Sophia Chen
images:
  hero: /images/compounds/acetaldehyde-hero.jpg
  thumbnail: /images/compounds/acetaldehyde-thumb.jpg
breadcrumb_text: Acetaldehyde

# ================================================
# ALL OTHER DATA UNDER RELATIONSHIPS
# ================================================
relationships:
  # ========================================
  # SAFETY & PPE DATA
  # ========================================
  ppe_requirements:
    respiratory: NIOSH-approved organic vapor respirator for <25 ppm
    skin: Nitrile or butyl rubber gloves
    eye: Chemical safety goggles, face shield for splash hazard
    minimum_level: Level C for <25 ppm, Level B for >25 ppm
    special_notes: Probable human carcinogen (IARC Group 2B)
  
  emergency_response:
    fire_hazard: EXTREMELY FLAMMABLE. Wide explosive range.
    fire_suppression: EVACUATE - explosion hazard. Stop flow if safe.
    spill_procedures: EVACUATE. Eliminate ignition sources. Ventilate area.
    exposure_immediate_actions: Remove to fresh air immediately.
    environmental_hazards: Toxic to aquatic life. Report spills.
    special_hazards: PROBABLE HUMAN CARCINOGEN (IARC 2B).
  
  storage_requirements:
    temperature_range: Store below 20°C, refrigerate
    ventilation: Explosion-proof ventilation required
    incompatibilities: [Acids, Bases, Oxidizers]
    container_material: Stainless steel or aluminum
    segregation: Separate from oxidizers by 20 feet
    quantity_limits: Many facilities limit to <10 gallons
    special_requirements: Store with stabilizer. Refrigerated storage required.
  
  # ========================================
  # REGULATORY & COMPLIANCE DATA
  # ========================================
  regulatory_classification:
    un_number: UN1089
    dot_hazard_class: 3 (Flammable liquid)
    dot_label: Flammable Liquid
    nfpa_codes:
      health: 2
      flammability: 4
      reactivity: 2
      special: null
    epa_hazard_categories:
    - Flammability
    - Acute toxicity
    - Carcinogenicity (probable)
    sara_title_iii: true
    cercla_rq: 1000 pounds (454 kg)
    rcra_code: U001
  
  regulatory_standards:
  - id: osha-1910-1000
    title: OSHA 1910.1000 - Air Contaminants
    authority: OSHA
    url: https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.1000
    image: /images/logo/logo-org-osha.png
    applicability: Workplace exposure limits
    compliance_level: mandatory
  
  # ========================================
  # EXPOSURE & MONITORING DATA
  # ========================================
  workplace_exposure:
    osha_pel:
      twa_8hr: 200 ppm (360 mg/m³)
      stel_15min: null
      ceiling: null
    niosh_rel:
      ceiling: 10 ppm (18 mg/m³) - based on carcinogenicity
      idlh: 2000 ppm
    acgih_tlv:
      ceiling: 25 ppm
    biological_exposure_indices: []
  
  exposure_limits:
    osha_pel_ppm: 200
    osha_pel_mg_m3: 360
    niosh_rel_ppm: null
    acgih_tlv_ppm: 25
    acgih_tlv_mg_m3: 45
  
  detection_monitoring:
    sensor_types:
    - Photoionization detector (PID)
    - Electrochemical
    detection_range: 0-100 ppm typical
    alarm_setpoints:
      low: 10 ppm (NIOSH ceiling)
      high: 25 ppm (ACGIH ceiling)
      evacuate: 2000 ppm (NIOSH IDLH)
    analytical_methods:
    - method: NIOSH 2538
      technique: GC-FID
      detection_limit: 0.01 ppm
  
  # ========================================
  # CHEMICAL PROPERTIES
  # ========================================
  physical_properties:
    boiling_point: 20.2°C (68.4°F)
    melting_point: -123.5°C (-190.3°F)
    vapor_pressure: 740 mmHg @ 20°C
    vapor_density: 1.52 (Air=1)
    specific_gravity: 0.788 @ 20°C
    flash_point: -39°C (-38°F)
    autoignition_temp: 175°C (347°F)
    explosive_limits: 'LEL: 4%, UEL: 60%'
    appearance: Colorless liquid, colorless gas >20°C
    odor: Pungent, fruity odor @ 0.05-1 ppm
  
  chemical_properties:
    chemical_formula: C2H4O
    cas_number: 75-07-0
    molecular_weight: 44.05
    hazard_class: irritant
  
  reactivity:
    stability: UNSTABLE. Polymerizes readily.
    polymerization: Violent exothermic polymerization
    incompatible_materials: [Strong acids, Strong bases, Oxidizers]
    hazardous_decomposition: [Carbon monoxide, Carbon dioxide]
    conditions_to_avoid: [Heat, Sparks, Flames]
    reactivity_hazard: EXTREMELY REACTIVE.
  
  environmental_impact:
    aquatic_toxicity: 'Toxic to aquatic life. LC50 (fish, 96h): 50-150 mg/L.'
    biodegradability: Readily biodegradable (>70% in 28 days)
    bioaccumulation: 'Does not bioaccumulate. Log Kow: -0.34.'
    soil_mobility: High mobility
    atmospheric_fate: 'Photolyzes rapidly. Half-life: 9 hours.'
    reportable_releases:
      water: 1000 lbs to navigable waters
      air: 1000 lbs/day (CERCLA RQ)
  
  # ========================================
  # IDENTIFIERS & METADATA
  # ========================================
  synonyms_identifiers:
    synonyms: [Acetic aldehyde, Ethanal, Ethyl aldehyde]
    common_trade_names: []
    other_identifiers:
      rtecs_number: AB1925000
      ec_number: 200-836-8
      pubchem_cid: '177'
  
  health_effects_keywords:
  - respiratory_irritation
  - eye_irritation
  - suspected_carcinogen
  - narcotic_effects
  
  sources_in_laser_cleaning:
  - alcohol_oxidation
  - polymer_decomposition
  - organic_solvent_breakdown
  
  # ========================================
  # CROSS-REFERENCES
  # ========================================
  produced_by_contaminants:
  - id: plastic-residue-contamination
    title: Degraded Polymer Deposits
    url: /contaminants/plastic-residue-contamination
    image: /images/contaminants/plastic-residue-contamination.jpg
    production_mechanism: Thermal degradation of polyethylene
    frequency: common
    severity: moderate
    typical_context: High-power laser cleaning of polymers
  
  related_materials:
  - id: polyethylene-laser-cleaning
    title: Polyethylene (PE)
    url: /materials/polyethylene-laser-cleaning
    image: /images/materials/polyethylene-laser-cleaning.jpg
    frequency: common
    severity: moderate
    typical_context: Polymer processing
---
```

### Example 2: Material Frontmatter (aluminum-laser-cleaning.yaml)

#### ❌ BEFORE (Current - Technical Data Scattered)
```yaml
---
# Page-specific fields
id: aluminum-laser-cleaning
name: Aluminum
display_name: Aluminum (Al)
category: materials
subcategory: metals
schema_version: 5.0.0
datePublished: '2024-01-15'
dateModified: '2024-11-20'
description: Lightweight metal commonly used in aerospace...
author: Dr. James Mitchell

# ⚠️ PROBLEM: Technical properties scattered at top-level
laser_properties:
  laser_parameters:
    beam_profile: flat_top
    fluence_range:
      min_j_cm2: 0.3
      max_j_cm2: 1.2
      recommended_j_cm2: 0.7
    overlap_percentage: 50
    pulse_duration: 100-200 ns
  optical_properties:
    absorption_coefficient: 0.045
    reflectivity: 0.92 @ 1064nm
  removal_characteristics:
    byproducts: [aluminum oxide particles, metal vapor]
    damage_risk_to_substrate: low
    primary_mechanism: thermal_ablation

machine_settings:
  powerRange:
    value: 100
    unit: W
  wavelength:
    value: 1064
    unit: nm
  pulseFrequency:
    value: 30
    unit: kHz

# ⚠️ PROBLEM: Material properties scattered at top-level
material_properties:
  mechanical:
    tensile_strength: 90 MPa
    hardness: 28 HB
  thermal:
    thermal_conductivity: 237 W/m·K
    melting_point: 660°C

# ⚠️ PROBLEM: Safety data scattered at top-level
ppe_requirements:
  respiratory: N95 respirator minimum
  eye: OD 7+ laser safety glasses at 1064nm
  skin: Heat-resistant gloves

# ⚠️ PROBLEM: Application data scattered at top-level
applications:
- industry: aerospace
  use_cases: [Aircraft parts, Engine components]
- industry: automotive
  use_cases: [Cylinder heads, Transmission housings]

characteristics:
  advantages:
  - Lightweight with good strength-to-weight ratio
  - Excellent corrosion resistance
  limitations:
  - Lower strength compared to steel
  - High reflectivity requires power adjustment

# ✅ GOOD: Only part properly structured
relationships:
  related_contaminants:
  - id: rust-corrosion-contamination
    title: Rust / Iron Oxide Corrosion
    url: /contaminants/rust-corrosion-contamination
---
```

#### ✅ AFTER (Proposed - Everything Under relationships)
```yaml
---
# ================================================
# PAGE-SPECIFIC FIELDS ONLY (Top-Level)
# ================================================
id: aluminum-laser-cleaning
name: Aluminum
display_name: Aluminum (Al)
category: materials
subcategory: metals
content_type: material
schema_version: 5.0.0
datePublished: '2024-01-15'
dateModified: '2024-11-20'
description: Lightweight metal commonly used in aerospace...
micro: Soft, lightweight metal requiring moderate laser power...
faq:
  - question: What laser power is best for aluminum?
    answer: 100W at 1064nm wavelength...
author: Dr. James Mitchell
images:
  hero: /images/materials/aluminum-hero.jpg
  thumbnail: /images/materials/aluminum-thumb.jpg
breadcrumb_text: Aluminum

# ================================================
# ALL OTHER DATA UNDER RELATIONSHIPS
# ================================================
relationships:
  # ========================================
  # TECHNICAL PROPERTIES
  # ========================================
  laser_properties:
    laser_parameters:
      beam_profile: flat_top
      fluence_range:
        min_j_cm2: 0.3
        max_j_cm2: 1.2
        recommended_j_cm2: 0.7
      overlap_percentage: 50
      pulse_duration: 100-200 ns
      scan_speed: 2-5 m/s
    optical_properties:
      absorption_coefficient: 0.045
      reflectivity: 0.92 @ 1064nm
      thermal_diffusivity: 97 mm²/s
    removal_characteristics:
      byproducts: [aluminum oxide particles, metal vapor]
      damage_risk_to_substrate: low
      primary_mechanism: thermal_ablation
    safety_data:
      fire_explosion_risk: low
      fumes_generated: [aluminum oxide, metal vapor]
      particulate_generation:
        size_range: 0.1-10 μm
        concentration: 5-20 mg/m³ typical
  
  machine_settings:
    powerRange:
      value: 100
      unit: W
      description: Optimal average power for oxide removal
    wavelength:
      value: 1064
      unit: nm
      description: Near-IR wavelength for optimal metal absorption
    pulseFrequency:
      value: 30
      unit: kHz
      description: Moderate frequency for controlled cleaning
    spotSize:
      value: 0.3
      unit: mm
      description: Standard spot size for general cleaning
    scanSpeed:
      value: 3000
      unit: mm/s
      description: Moderate speed for thorough cleaning
  
  # ========================================
  # MATERIAL PROPERTIES
  # ========================================
  material_properties:
    mechanical:
      tensile_strength:
        value: 90
        unit: MPa
        condition: Annealed
      hardness:
        value: 28
        scale: HB
        condition: Annealed
      yield_strength:
        value: 35
        unit: MPa
    thermal:
      thermal_conductivity:
        value: 237
        unit: W/m·K
        temperature: 20°C
      melting_point:
        value: 660
        unit: °C
      thermal_expansion:
        value: 23.1
        unit: μm/m·K
    optical:
      reflectivity:
        value: 92
        unit: '%'
        wavelength: 1064 nm
      absorption:
        value: 8
        unit: '%'
        wavelength: 1064 nm
  
  # ========================================
  # SAFETY & PPE
  # ========================================
  ppe_requirements:
    respiratory: N95 respirator minimum for particle exposure
    skin: Heat-resistant gloves for handling processed parts
    eye: OD 7+ laser safety glasses at 1064nm
    minimum_level: Level D with respiratory and eye protection
    special_notes: Aluminum oxide particulates can cause respiratory irritation
  
  # ========================================
  # APPLICATIONS & CHARACTERISTICS
  # ========================================
  applications:
  - industry: aerospace
    use_cases:
    - Aircraft structural components
    - Engine parts
    - Landing gear
  - industry: automotive
    use_cases:
    - Cylinder heads
    - Transmission housings
    - Wheels
  - industry: manufacturing
    use_cases:
    - Molds and dies
    - Extrusion dies
    - Forming tools
  
  characteristics:
    advantages:
    - Lightweight with good strength-to-weight ratio
    - Excellent corrosion resistance
    - Good thermal conductivity
    - Easy to machine and form
    limitations:
    - Lower strength compared to steel
    - High reflectivity requires power adjustment
    - Can be difficult to weld
    typical_applications:
    - Structural components in aerospace
    - Automotive parts requiring light weight
    - Heat sinks and thermal management
  
  # ========================================
  # CROSS-REFERENCES
  # ========================================
  related_contaminants:
  - id: rust-corrosion-contamination
    title: Rust / Iron Oxide Corrosion
    url: /contaminants/rust-corrosion-contamination
    image: /images/contaminants/rust-corrosion-contamination.jpg
    frequency: common
    severity: moderate
    typical_context: Surface oxidation
  
  - id: paint-coatings-contamination
    title: Paint & Coatings
    url: /contaminants/paint-coatings-contamination
    image: /images/contaminants/paint-coatings-contamination.jpg
    frequency: very_common
    severity: low
    typical_context: Industrial finishing removal
  
  related_materials:
  - id: steel-laser-cleaning
    title: Steel
    url: /materials/steel-laser-cleaning
    image: /images/materials/steel-laser-cleaning.jpg
    frequency: common
    severity: moderate
    typical_context: Similar industrial applications
  
  recommended_settings:
  - id: aluminum-bronze-settings
    title: Aluminum Bronze Settings
    url: /settings/aluminum-bronze-settings
    image: /images/settings/aluminum-bronze-settings.jpg
    applicability: Oxide removal
    success_rate: high
---
```

### Key Changes Summary

#### What Stays at Top-Level (Page-Specific Only)
- `id`, `name`, `display_name`, `title`
- `slug` (if needed for URLs)
- `category`, `subcategory`
- `content_type`
- `schema_version`
- `datePublished`, `dateModified`
- `description`, `micro`, `faq` (content fields)
- `author`
- `images` (hero, thumbnail)
- `breadcrumb_text`

#### What Moves to relationships (Everything Else)
- **Safety**: `ppe_requirements`, `emergency_response`, `storage_requirements`
- **Regulatory**: `regulatory_classification`, `regulatory_standards`
- **Exposure**: `workplace_exposure`, `exposure_limits`, `detection_monitoring`
- **Chemical**: `physical_properties`, `chemical_properties`, `reactivity`, `environmental_impact`
- **Technical**: `laser_properties`, `machine_settings`, `removal_characteristics`
- **Material**: `material_properties`, `applications`, `characteristics`
- **Identifiers**: `synonyms_identifiers`, `health_effects_keywords`, `sources_in_laser_cleaning`
- **Cross-References**: `related_materials`, `related_contaminants`, `produced_by_contaminants`, `compatible_materials`, `prohibited_materials`, `recommended_settings`

---

## TypeScript Schema (Unified)

```typescript
/**
 * Unified Relationship Entry Schema
 * All relationship types use this single interface with optional fields
 */
interface RelationshipEntry {
  // ============================================
  // REQUIRED FIELDS
  // ============================================
  id: string;                           // Unique identifier
  title: string;                        // Display name
  url: string;                          // Link to entity
  
  // ============================================
  // CORE OPTIONAL FIELDS (Common)
  // ============================================
  image?: string;                       // Image path
  description?: string;                 // Brief explanation
  notes?: string;                       // Additional context
  
  // ============================================
  // RELATIONSHIP METADATA
  // ============================================
  frequency?: 'common' | 'uncommon' | 'rare' | 'very_common';
  severity?: 'high' | 'moderate' | 'low' | 'critical';
  typical_context?: string;             // When/where this applies
  
  // ============================================
  // TYPE-SPECIFIC OPTIONAL FIELDS
  // ============================================
  
  // Chemical/Compound specific
  cas_number?: string;
  hazard_class?: string;
  concentration_range?: string;
  chemical_formula?: string;
  molecular_weight?: number;
  
  // Regulatory/Standards specific
  authority?: string;
  compliance_level?: 'mandatory' | 'recommended' | 'optional';
  applicability?: string;
  effective_date?: string;
  
  // Production/Source specific
  production_mechanism?: string;
  decomposition_temp?: string;
  typical_conditions?: string;
  
  // Compatibility specific
  compatibility?: 'high' | 'moderate' | 'low' | 'incompatible';
  reason?: string;                      // Why prohibited/recommended
  
  // Settings/Equipment specific
  success_rate?: 'high' | 'moderate' | 'low';
  power_range?: string;
  recommended_for?: string[];
  
  // Safety/PPE specific
  equipment_type?: 'respiratory' | 'eye_protection' | 'skin_protection' | 'hearing';
  protection_level?: string;
  standard?: string;
  condition?: string;
}

/**
 * Frontmatter Relationships Container
 * All relationship types use the same entry schema
 */
interface FrontmatterRelationships {
  // Cross-references
  related_materials?: RelationshipEntry[];
  related_contaminants?: RelationshipEntry[];
  related_compounds?: RelationshipEntry[];
  related_settings?: RelationshipEntry[];
  
  // Production sources
  produced_by_contaminants?: RelationshipEntry[];
  
  // Regulatory & Standards
  regulatory_standards?: RelationshipEntry[];
  
  // Compatibility
  compatible_materials?: RelationshipEntry[];
  prohibited_materials?: RelationshipEntry[];
  
  // Recommendations
  recommended_settings?: RelationshipEntry[];
  
  // Any future relationship types also use RelationshipEntry[]
  [key: string]: RelationshipEntry[] | undefined;
}

/**
 * Complete Frontmatter Schema
 */
interface Frontmatter {
  // ============================================
  // PAGE-SPECIFIC FIELDS (Top-Level Only)
  // ============================================
  id: string;
  name: string;
  display_name?: string;
  slug?: string;
  title?: string;
  category: string;
  subcategory?: string;
  content_type: 'material' | 'contaminant' | 'compound' | 'setting';
  schema_version: string;
  datePublished: string;
  dateModified: string;
  description: string;
  micro?: string;
  faq?: Array<{ question: string; answer: string }>;
  author: string | { id: number };
  images?: {
    hero?: string;
    thumbnail?: string;
    [key: string]: string | undefined;
  };
  breadcrumb_text?: string;
  
  // ============================================
  // ALL OTHER DATA UNDER RELATIONSHIPS
  // ============================================
  relationships: FrontmatterRelationships & {
    // Technical properties (non-reference data)
    laser_properties?: Record<string, any>;
    machine_settings?: Record<string, any>;
    material_properties?: Record<string, any>;
    
    // Safety data (non-reference)
    ppe_requirements?: Record<string, any>;
    emergency_response?: Record<string, any>;
    storage_requirements?: Record<string, any>;
    
    // Regulatory data (non-reference)
    regulatory_classification?: Record<string, any>;
    
    // Exposure data (non-reference)
    workplace_exposure?: Record<string, any>;
    exposure_limits?: Record<string, any>;
    detection_monitoring?: Record<string, any>;
    
    // Chemical data (non-reference)
    physical_properties?: Record<string, any>;
    chemical_properties?: Record<string, any>;
    reactivity?: Record<string, any>;
    environmental_impact?: Record<string, any>;
    
    // Identifiers (non-reference)
    synonyms_identifiers?: Record<string, any>;
    health_effects_keywords?: string[];
    sources_in_laser_cleaning?: string[];
    
    // Applications (non-reference)
    applications?: Array<Record<string, any>>;
    characteristics?: Record<string, any>;
    
    // Contaminant-specific (non-reference)
    composition?: Array<Record<string, any>>;
    visual_characteristics?: Record<string, any>;
    
    // Settings-specific (non-reference)
    challenges?: string[];
  };
}

/**
 * Validation Helper
 */
function validateRelationshipEntry(entry: RelationshipEntry): boolean {
  // Required fields
  if (!entry.id || !entry.title || !entry.url) {
    return false;
  }
  
  // Optional field validation
  if (entry.frequency && !['common', 'uncommon', 'rare', 'very_common'].includes(entry.frequency)) {
    return false;
  }
  
  if (entry.severity && !['high', 'moderate', 'low', 'critical'].includes(entry.severity)) {
    return false;
  }
  
  if (entry.compliance_level && !['mandatory', 'recommended', 'optional'].includes(entry.compliance_level)) {
    return false;
  }
  
  return true;
}
```

**Key Advantages**:
- ✅ Single `RelationshipEntry` interface for ALL relationship types
- ✅ Type safety with optional fields
- ✅ Easy to extend - just add optional fields to base interface
- ✅ Consistent validation across all relationship types
- ✅ Better IDE autocomplete - all fields available everywhere

---

## Rollback Plan

If issues arise during migration:

1. **Immediate**: Keep old keys for 1 release cycle (dual-write)
2. **Components**: Check for both old and new keys with fallback
3. **Validation**: Don't enforce new schema until all files migrated
4. **Deployment**: Blue-green deployment with instant rollback capability

---

## Success Metrics

- ✅ 100% of frontmatter files follow new schema
- ✅ Zero scattered relationship keys at top-level
- ✅ All TypeScript interfaces validate correctly
- ✅ All pages render correctly with new schema
- ✅ No breaking changes for external consumers
- ✅ Documentation updated and comprehensive

---

## Recommendation

**PROCEED with normalization** using phased approach:
1. Start with compounds (smallest dataset, ~50 files)
2. Validate pattern works
3. Roll out to contaminants, materials, settings
4. Remove compatibility layer after 1 release cycle

**Estimated Timeline**: 5-6 weeks for complete migration

**Risk Level**: Medium (manageable with phased approach and compatibility layer)

**Value**: High (long-term maintainability, consistency, extensibility)
