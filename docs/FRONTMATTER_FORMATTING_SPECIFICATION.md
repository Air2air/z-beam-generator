# Frontmatter Formatting Specification

**Date**: December 18, 2025  
**Status**: Implementation Specification  
**Applies To**: All 654 frontmatter files (materials, contaminants, compounds, settings)

---

## Quick Reference: Parent Keys Organization

```yaml
# TOP-LEVEL (Page Identity & Content Only)
id, name, display_name, title, slug, category, subcategory, content_type, 
schema_version, datePublished, dateModified, description, micro, faq, 
author, images, breadcrumb, breadcrumb_text

# RELATIONSHIPS (Everything Else)
relationships:
  # Cross-References (use unified schema)
  related_materials, related_contaminants, related_compounds, related_settings
  
  # Production & Sources
  produced_by_contaminants, produced_by_materials
  
  # Regulatory & Standards
  regulatory_standards, regulatory_classification
  
  # Compatibility
  compatible_materials, prohibited_materials, recommended_settings
  
  # Technical Data
  laser_properties, machine_settings, material_properties, optical_properties
  
  # Safety & PPE
  ppe_requirements, emergency_response, storage_requirements
  
  # Exposure & Monitoring
  workplace_exposure, exposure_limits, detection_monitoring
  
  # Chemical Data
  physical_properties, chemical_properties, reactivity, environmental_impact
  
  # Identifiers & Metadata
  synonyms_identifiers, health_effects_keywords, sources_in_laser_cleaning
  
  # Applications
  applications, characteristics, challenges
  
  # Composition (Contaminants)
  composition, visual_characteristics
```

---

## 1. Unified Relationship Entry Schema

**ALL relationship entries MUST use this exact structure:**

### Required Fields (Every Entry)
```yaml
- id: string                    # Full unique identifier
  title: string                 # Display name
  url: string                   # Full URL path with ID
```

### Common Optional Fields
```yaml
  image: string                 # Image path
  description: string           # Brief explanation
  notes: string                 # Additional context
  
  # Relationship metadata
  frequency: string             # common | uncommon | rare | very_common
  severity: string              # high | moderate | low | critical
  typical_context: string       # When/where applicable
```

### Type-Specific Optional Fields
```yaml
  # Chemical/Compound
  cas_number: string
  hazard_class: string
  concentration_range: string
  chemical_formula: string
  molecular_weight: number
  
  # Regulatory/Standards
  authority: string
  compliance_level: string      # mandatory | recommended | optional
  applicability: string
  effective_date: string
  
  # Production/Source
  production_mechanism: string
  decomposition_temp: string
  typical_conditions: string
  
  # Compatibility
  compatibility: string         # high | moderate | low | incompatible
  reason: string
  
  # Settings/Equipment
  success_rate: string          # high | moderate | low
  power_range: string
  recommended_for: string[]
  
  # Safety/PPE
  equipment_type: string
  protection_level: string
  standard: string
  condition: string
```

---

## 2. Parent Key Organization by Content Type

### 2.1 Materials Frontmatter

```yaml
---
# ============================================
# PAGE IDENTITY & CONTENT
# ============================================
id: aluminum-laser-cleaning
name: Aluminum
display_name: Aluminum (Al)
slug: aluminum
title: Aluminum Laser Cleaning
category: metal
subcategory: non-ferrous
content_type: materials
schema_version: 5.0.0
datePublished: '2025-12-19T00:00:00Z'
dateModified: '2025-12-19T00:00:00Z'

description: |
  Lightweight metal commonly used in aerospace and automotive applications.
  Excellent thermal conductivity but high reflectivity requires power adjustment.

micro:
  before: |
    At 1000x magnification, contaminated aluminum surface shows rough texture
    with oxide buildup and particulates reducing conductivity.
  after: |
    Laser cleaning removes all contamination, revealing smooth metallic surface
    with restored conductivity and natural sheen.

faq:
- question: What makes aluminum suitable for industrial laser cleaning?
  answer: |
    Lightweight with low density (2.7 g/cm³). Near-zero porosity means surfaces
    stay smooth without hidden contaminants.
    
    Alessandro Moretti, Ph.D.

author:
  id: 1

images:
  hero:
    url: /images/materials/aluminum-laser-cleaning-hero.jpg
    alt: Aluminum surface undergoing laser cleaning
  micro:
    url: /images/materials/aluminum-laser-cleaning-micro.jpg
    alt: Microscopic view of laser-cleaned aluminum

breadcrumb:
- label: Home
  href: /
- label: Materials
  href: /materials
- label: Metal
  href: /materials/metal
- label: Non Ferrous
  href: /materials/metal/non-ferrous
- label: Aluminum
  href: /materials/metal/non-ferrous/aluminum-laser-cleaning

# ============================================
# RELATIONSHIPS (Everything Else)
# ============================================
relationships:
  
  # ------------------------------------------
  # CROSS-REFERENCES
  # ------------------------------------------
  related_contaminants:
  - id: rust-corrosion-contamination
    title: Rust / Iron Oxide Corrosion
    url: /contaminants/rust-corrosion-contamination
    image: /images/contaminants/rust-corrosion-contamination.jpg
    frequency: common
    severity: moderate
    typical_context: Surface oxidation on aluminum alloys
    notes: Aluminum forms protective oxide layer naturally
  
  - id: paint-coatings-contamination
    title: Paint & Coatings
    url: /contaminants/paint-coatings-contamination
    image: /images/contaminants/paint-coatings-contamination.jpg
    frequency: very_common
    severity: low
    typical_context: Industrial finishing removal
  
  related_compounds:
  - id: aluminum-oxide
    title: Aluminum Oxide (Al₂O₃)
    url: /compounds/aluminum-oxide
    image: /images/compounds/aluminum-oxide.jpg
    cas_number: 1344-28-1
    chemical_formula: Al2O3
    concentration_range: 5-50 mg/m³
    frequency: very_common
    severity: low
    typical_context: Natural oxidation and laser ablation byproduct
  
  recommended_settings:
  - id: aluminum-standard-cleaning-settings
    title: Aluminum Standard Cleaning Settings
    url: /settings/aluminum-standard-cleaning-settings
    image: /images/settings/aluminum-standard-cleaning.jpg
    success_rate: high
    power_range: 80-120W
    applicability: General oxide and paint removal
    recommended_for:
    - surface_cleaning
    - oxide_removal
    - paint_stripping
  
  # ------------------------------------------
  # REGULATORY & STANDARDS
  # ------------------------------------------
  regulatory_standards:
  - id: fda-laser-product-performance
    title: FDA 21 CFR 1040.10 - Laser Product Performance Standards
    authority: FDA
    url: https://www.ecfr.gov/current/title-21/chapter-I/subchapter-J/part-1040/section-1040.10
    image: /images/logo/logo-org-fda.png
    compliance_level: mandatory
    applicability: All laser cleaning equipment
  
  - id: ansi-z136-laser-safety
    title: ANSI Z136.1 - Safe Use of Lasers
    authority: ANSI
    url: https://webstore.ansi.org/standards/lia/ansiz1362022
    image: /images/logo/logo-org-ansi.png
    compliance_level: recommended
    applicability: Workplace laser safety programs
  
  # ------------------------------------------
  # TECHNICAL PROPERTIES
  # ------------------------------------------
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
      reflectivity: 0.92
      wavelength: 1064 nm
      thermal_diffusivity: 97 mm²/s
    
    removal_characteristics:
      primary_mechanism: thermal_ablation
      byproducts:
      - aluminum oxide particles
      - metal vapor
      damage_risk_to_substrate: low
      optimal_pulse_energy: 0.5-1.0 mJ
    
    safety_data:
      fire_explosion_risk: low
      fumes_generated:
      - aluminum oxide
      - metal vapor
      particulate_generation:
        size_range: 0.1-10 μm
        concentration: 5-20 mg/m³
        control_required: true
  
  machine_settings:
    power:
      value: 100
      unit: W
      range: 80-120
      description: Optimal average power for oxide removal
    
    wavelength:
      value: 1064
      unit: nm
      description: Near-IR wavelength for optimal metal absorption
    
    pulse_frequency:
      value: 30
      unit: kHz
      range: 20-50
      description: Moderate frequency for controlled cleaning
    
    spot_size:
      value: 0.3
      unit: mm
      range: 0.2-0.5
      description: Standard spot size for general cleaning
    
    scan_speed:
      value: 3000
      unit: mm/s
      range: 2000-5000
      description: Moderate speed for thorough cleaning
  
  material_properties:
    physical:
      density:
        value: 2.7
        unit: g/cm³
        confidence: 98
      porosity:
        value: 0
        unit: '%'
        confidence: 95
      surface_roughness:
        value: 0.8
        unit: μm
        typical_range: 0.4-3.2
    
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
  
  # ------------------------------------------
  # SAFETY & PPE
  # ------------------------------------------
  ppe_requirements:
    respiratory:
      equipment: N95 respirator minimum
      standard: NIOSH 42 CFR 84
      condition: For particle exposure during cleaning
      protection_level: Level D
    
    eye:
      equipment: OD 7+ laser safety glasses at 1064nm
      standard: ANSI Z136.1
      condition: Mandatory during all laser operations
      protection_level: Class 4 laser protection
    
    skin:
      equipment: Heat-resistant gloves
      condition: For handling processed parts
      protection_level: Basic thermal protection
    
    special_notes: |
      Aluminum oxide particulates can cause respiratory irritation with prolonged
      exposure. Ensure adequate ventilation or use respiratory protection.
  
  # ------------------------------------------
  # APPLICATIONS & CHARACTERISTICS
  # ------------------------------------------
  applications:
  - industry: aerospace
    use_cases:
    - Aircraft structural components
    - Engine parts
    - Landing gear
    frequency: very_common
    
  - industry: automotive
    use_cases:
    - Cylinder heads
    - Transmission housings
    - Wheels and rims
    frequency: common
    
  - industry: manufacturing
    use_cases:
    - Molds and dies
    - Extrusion dies
    - Forming tools
    frequency: common
  
  characteristics:
    advantages:
    - Lightweight with excellent strength-to-weight ratio
    - Superior corrosion resistance
    - Excellent thermal and electrical conductivity
    - Easy to machine and form
    - Non-magnetic properties
    
    limitations:
    - Lower strength compared to steel alloys
    - High reflectivity requires laser power adjustment
    - Can be difficult to weld without proper technique
    - Softens at relatively low temperatures
    
    typical_applications:
    - Structural components in aerospace industry
    - Automotive parts requiring light weight
    - Heat sinks and thermal management components
    - Electrical conductors and enclosures
    - Consumer electronics housings

---
```

---

### 2.2 Contaminants Frontmatter

```yaml
---
# ============================================
# PAGE IDENTITY & CONTENT
# ============================================
id: adhesive-residue-contamination
name: Adhesive Residue / Tape Marks
slug: adhesive-residue-tape-marks
category: organic-residue
subcategory: adhesive
content_type: contaminants
schema_version: 5.0.0
datePublished: '2025-12-19T00:00:00Z'
dateModified: '2025-12-19T00:00:00Z'

description: |
  Adhesive residue appears as sticky organic films on surfaces after removal
  of tapes or labels. Strong adhesion occurs on metals, with re-adhesion
  challenges during mechanical removal attempts. Laser cleaning vaporizes
  organics selectively while leaving substrates undamaged.

micro:
  before: |
    Adhesive residue exhibits sticky viscoelastic bonds, trapping micro-particles
    in polymeric matrix and resisting shear forces. Surface appears irregular with
    layered buildup that clings tightly.
  after: |
    After laser treatment, contamination is ablated completely, revealing clean
    surface with uniform texture and no remnants.

author:
  id: 1

images:
  hero:
    url: /images/contaminants/adhesive-residue-hero.jpg
    alt: Adhesive residue contamination on metal surface
  micro:
    url: /images/contaminants/adhesive-residue-micro.jpg
    alt: Microscopic view of adhesive residue buildup

breadcrumb_text: Adhesive Residue / Tape Marks

# ============================================
# RELATIONSHIPS
# ============================================
relationships:
  
  # ------------------------------------------
  # CROSS-REFERENCES
  # ------------------------------------------
  related_materials:
  - id: steel-laser-cleaning
    title: Steel
    url: /materials/steel-laser-cleaning
    image: /images/materials/steel-laser-cleaning.jpg
    frequency: very_common
    severity: moderate
    typical_context: Adhesive residue on steel manufacturing parts
    notes: Strong adhesion to ferrous metals
  
  - id: aluminum-laser-cleaning
    title: Aluminum
    url: /materials/aluminum-laser-cleaning
    image: /images/materials/aluminum-laser-cleaning.jpg
    frequency: common
    severity: moderate
    typical_context: Tape marks on aluminum components
  
  - id: acrylic-pmma-laser-cleaning
    title: Acrylic (PMMA)
    url: /materials/acrylic-pmma-laser-cleaning
    image: /images/materials/acrylic-pmma-laser-cleaning.jpg
    frequency: common
    severity: low
    typical_context: Label residue on plastic products
    notes: Lower power required for plastics
  
  related_compounds:
  - id: acrylic-adhesive-polymer
    title: Acrylic Adhesive Polymer
    url: /compounds/acrylic-adhesive-polymer
    cas_number: 25085-34-1
    frequency: very_common
    severity: low
    typical_context: Primary component of pressure-sensitive adhesives
  
  recommended_settings:
  - id: adhesive-removal-standard-settings
    title: Adhesive Removal Standard Settings
    url: /settings/adhesive-removal-standard-settings
    success_rate: high
    power_range: 50-100W
    applicability: General adhesive and tape residue removal
  
  # ------------------------------------------
  # COMPOSITION
  # ------------------------------------------
  composition:
  - compound: Acrylic polymer
    percentage: 40-60%
    role: Primary adhesive matrix
    
  - compound: Tackifier resin
    percentage: 20-40%
    role: Enhances adhesion properties
    
  - compound: Plasticizer
    percentage: 5-15%
    role: Improves flexibility
    
  - compound: Filler particles
    percentage: 5-10%
    role: Bulk and cost reduction
  
  # ------------------------------------------
  # VISUAL CHARACTERISTICS
  # ------------------------------------------
  visual_characteristics:
    appearance_on_categories:
      metal:
        appearance: Transparent to amber sticky film
        coverage: Irregular patches with defined edges
        pattern: Follows tape or label outline
        thickness: 0.1-0.5 mm typical
        
      plastic:
        appearance: Semi-transparent residue with trapped particles
        coverage: Uniform to irregular depending on adhesive type
        pattern: Rectangular or custom label shapes
        thickness: 0.05-0.3 mm typical
        
      wood:
        appearance: Sticky residue penetrating surface grain
        coverage: Irregular with fiber absorption
        pattern: Variable, often darker than surrounding wood
        thickness: Surface to 1mm penetration
    
    identification_markers:
    - Sticky or tacky texture to touch
    - Transparent to amber coloration
    - Traps dust and particles on surface
    - Fluorescence under UV light
    - Irregular edges following tape removal pattern
  
  # ------------------------------------------
  # TECHNICAL PROPERTIES
  # ------------------------------------------
  laser_properties:
    removal_characteristics:
      primary_mechanism: photo_thermal_ablation
      optimal_wavelength: 1064 nm
      power_density: 10-30 MW/cm²
      pulse_duration: 100-200 ns
      passes_required: 1-3
      
    effectiveness_by_substrate:
      metal:
        removal_rate: high
        damage_risk: very_low
        power_adjustment: standard
        
      plastic:
        removal_rate: medium
        damage_risk: medium
        power_adjustment: reduce_by_30_percent
        
      wood:
        removal_rate: medium
        damage_risk: low
        power_adjustment: reduce_by_20_percent

---
```

---

### 2.3 Compounds Frontmatter

```yaml
---
# ============================================
# PAGE IDENTITY & CONTENT
# ============================================
id: acetaldehyde
name: Acetaldehyde
display_name: Acetaldehyde (C₂H₄O)
slug: acetaldehyde
category: irritant
subcategory: aldehyde
content_type: compounds
schema_version: 5.0.0
datePublished: '2025-12-19T00:00:00Z'
dateModified: '2025-12-19T00:00:00Z'

description: |
  Colorless, flammable gas with pungent fruity odor. Produced during laser
  cleaning of polymers and organic materials. Probable human carcinogen
  (IARC Group 2B) requiring strict exposure controls.

author:
  id: 1

images:
  hero:
    url: /images/compounds/acetaldehyde-hero.jpg
    alt: Acetaldehyde molecular structure and hazard information
  micro:
    url: /images/compounds/acetaldehyde-micro.jpg
    alt: Gas chromatography detection of acetaldehyde

breadcrumb_text: Acetaldehyde (C₂H₄O)

# ============================================
# RELATIONSHIPS
# ============================================
relationships:
  
  # ------------------------------------------
  # CROSS-REFERENCES
  # ------------------------------------------
  produced_by_contaminants:
  - id: plastic-residue-contamination
    title: Degraded Polymer Deposits
    url: /contaminants/plastic-residue-contamination
    image: /images/contaminants/plastic-residue-contamination.jpg
    production_mechanism: Thermal degradation of polyethylene
    decomposition_temp: 300-400°C
    frequency: common
    severity: moderate
    typical_context: High-power laser cleaning of polymers
  
  - id: paint-coatings-contamination
    title: Paint & Coatings
    url: /contaminants/paint-coatings-contamination
    image: /images/contaminants/paint-coatings-contamination.jpg
    production_mechanism: Decomposition of acrylic binders
    decomposition_temp: 250-350°C
    frequency: uncommon
    severity: moderate
  
  related_materials:
  - id: polyethylene-laser-cleaning
    title: Polyethylene (PE)
    url: /materials/polyethylene-laser-cleaning
    image: /images/materials/polyethylene-laser-cleaning.jpg
    frequency: common
    severity: moderate
    typical_context: Polymer processing generates acetaldehyde
    notes: Primary source material during thermal decomposition
  
  # ------------------------------------------
  # CHEMICAL PROPERTIES
  # ------------------------------------------
  chemical_properties:
    chemical_formula: C2H4O
    cas_number: 75-07-0
    molecular_weight: 44.05
    hazard_class: irritant
    state_at_room_temp: gas
    
  physical_properties:
    boiling_point:
      value: 20.2
      unit: °C
      fahrenheit: 68.4
    
    melting_point:
      value: -123.5
      unit: °C
      fahrenheit: -190.3
    
    vapor_pressure:
      value: 740
      unit: mmHg
      temperature: 20°C
    
    vapor_density:
      value: 1.52
      reference: Air=1
    
    specific_gravity:
      value: 0.788
      temperature: 20°C
    
    flash_point:
      value: -39
      unit: °C
      fahrenheit: -38
    
    autoignition_temp:
      value: 175
      unit: °C
      fahrenheit: 347
    
    explosive_limits:
      lel: 4
      uel: 60
      unit: '%'
    
    appearance: Colorless liquid, colorless gas >20°C
    odor: Pungent, fruity odor
    odor_threshold: 0.05-1 ppm
  
  reactivity:
    stability: UNSTABLE - Polymerizes readily
    polymerization: Violent exothermic polymerization with acids, bases, contaminants
    
    incompatible_materials:
    - Strong acids
    - Strong bases
    - Oxidizers
    - Halogens
    - Alcohols
    - Ammonia
    - Hydrogen cyanide
    - Phenols
    
    hazardous_decomposition:
    - Carbon monoxide
    - Carbon dioxide
    - Acetic acid
    
    conditions_to_avoid:
    - Heat
    - Light
    - Air exposure
    - Sparks and flames
    - Contamination
    
    reactivity_hazard: |
      EXTREMELY REACTIVE. Polymerizes violently. Reacts violently with
      oxidizers. Forms explosive peroxides with air. May self-heat and ignite.
  
  environmental_impact:
    aquatic_toxicity:
      description: Toxic to aquatic life
      lc50_fish_96h: 50-150 mg/L
    
    biodegradability:
      rating: readily_biodegradable
      percentage: '>70% in 28 days'
      pathway: Oxidizes to acetic acid
    
    bioaccumulation:
      potential: low
      log_kow: -0.34
      description: Does not bioaccumulate
    
    soil_mobility: high
    soil_behavior: Volatilizes rapidly from soil
    
    atmospheric_fate:
      degradation: photolyzes_rapidly
      products: Forms peroxyacetyl nitrate (PAN)
      half_life: 9 hours
    
    ozone_depletion: false
    global_warming_potential: null
    
    reportable_releases:
      water: 1000 lbs to navigable waters
      air: 1000 lbs/day (CERCLA RQ)
  
  # ------------------------------------------
  # REGULATORY & STANDARDS
  # ------------------------------------------
  regulatory_classification:
    un_number: UN1089
    dot_hazard_class: 3
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
    - Eye irritation
    
    sara_title_iii: true
    cercla_rq: 1000 pounds (454 kg)
    rcra_code: U001
  
  # ------------------------------------------
  # EXPOSURE & MONITORING
  # ------------------------------------------
  exposure_limits:
    osha_pel_ppm: 200
    osha_pel_mg_m3: 360
    niosh_rel_ppm: null
    niosh_rel_mg_m3: null
    acgih_tlv_ppm: 25
    acgih_tlv_mg_m3: 45
  
  workplace_exposure:
    osha_pel:
      twa_8hr: 200 ppm (360 mg/m³)
      stel_15min: null
      ceiling: null
    
    niosh_rel:
      twa_8hr: null
      stel_15min: null
      ceiling: 10 ppm (18 mg/m³)
      ceiling_basis: Based on carcinogenicity
      idlh: 2000 ppm
    
    acgih_tlv:
      twa_8hr: null
      stel_15min: null
      ceiling: 25 ppm
      classification: Confirmed animal carcinogen with unknown relevance to humans
    
    biological_exposure_indices: []
  
  detection_monitoring:
    sensor_types:
    - Photoionization detector (PID)
    - Electrochemical sensors
    - Gas chromatography
    
    detection_range: 0-100 ppm typical
    
    alarm_setpoints:
      low: 10 ppm (NIOSH ceiling)
      high: 25 ppm (ACGIH ceiling)
      evacuate: 2000 ppm (NIOSH IDLH)
    
    analytical_methods:
    - method: NIOSH 2538
      technique: GC-FID
      detection_limit: 0.01 ppm
      sample_type: Air
    
    - method: EPA TO-15
      technique: GC-MS
      detection_limit: 0.5 ppb
      sample_type: Air
  
  # ------------------------------------------
  # SAFETY & PPE
  # ------------------------------------------
  ppe_requirements:
    respiratory:
      equipment: NIOSH-approved organic vapor respirator for <25 ppm
      upgraded_equipment: SCBA for >25 ppm or unknown concentrations
      standard: NIOSH 42 CFR 84
      protection_level: Level C for <25 ppm, Level B for >25 ppm
    
    skin:
      equipment: Nitrile or butyl rubber gloves
      additional: Chemical-resistant clothing for liquid contact
      standard: ANSI/ISEA 105
    
    eye:
      equipment: Chemical safety goggles
      additional: Face shield for splash hazard
      standard: ANSI Z87.1
    
    special_notes: |
      PROBABLE HUMAN CARCINOGEN (IARC Group 2B). Extremely flammable.
      Irritating vapor. May polymerize explosively. Minimize exposure duration.
  
  emergency_response:
    fire_hazard: |
      EXTREMELY FLAMMABLE. Wide explosive range (4-60%). Vapors heavier
      than air travel to ignition sources. May polymerize explosively in fire.
    
    fire_suppression: |
      EVACUATE - explosion hazard. Stop flow if safe. Use dry chemical, CO2,
      alcohol-resistant foam. Water spray to cool containers. Do not use
      water jet directly on liquid.
    
    spill_procedures: |
      EVACUATE area. Eliminate all ignition sources. Ventilate thoroughly.
      SCBA for large spills. Contain with dry sand or earth. Neutralize with
      sodium bisulfite solution. Absorb with vermiculite or other inert material.
    
    exposure_immediate_actions: |
      Remove to fresh air immediately. Eyes: flush with water for 15 minutes.
      Remove contaminated clothing. Wash skin with soap and water.
      Seek medical attention - irritation and carcinogen exposure concern.
    
    environmental_hazards: |
      Toxic to aquatic life. Rapidly volatilizes from water. Biodegrades quickly
      in environment. Report all spills per regulatory requirements.
    
    special_hazards: |
      PROBABLE HUMAN CARCINOGEN (IARC 2B). Respiratory tract carcinogen in
      animals. Extremely flammable. May polymerize violently when contaminated.
      Narcotic effects at high concentrations. Severe eye and respiratory irritant.
  
  storage_requirements:
    temperature_range: Store below 20°C, refrigerate preferred
    
    ventilation: |
      Outdoor storage strongly preferred. Indoor: explosion-proof ventilation
      required. Gas detection systems mandatory.
    
    incompatibilities:
    - Acids
    - Bases
    - Alcohols
    - Ammonia
    - Halogens
    - Oxidizers
    
    container_material: |
      Stainless steel or aluminum only. Must contain stabilizer. Never use
      copper or iron containers.
    
    segregation: |
      Separate from oxidizers and incompatibles by minimum 20 feet.
      Store in approved flammable liquid storage cabinet.
    
    quantity_limits: |
      Minimize quantities stored. Many facilities limit to <10 gallons
      due to extreme fire hazard.
    
    special_requirements: |
      CRITICAL: Store with stabilizer. Check stabilizer concentration regularly.
      Refrigerated storage required. Inert gas blanketing (nitrogen) recommended.
      Post "EXTREMELY FLAMMABLE" and "CANCER HAZARD" warning signs.
  
  # ------------------------------------------
  # IDENTIFIERS & METADATA
  # ------------------------------------------
  synonyms_identifiers:
    synonyms:
    - Acetic aldehyde
    - Ethanal
    - Ethyl aldehyde
    - CH3CHO
    
    common_trade_names: []
    
    other_identifiers:
      rtecs_number: AB1925000
      ec_number: 200-836-8
      pubchem_cid: '177'
      einecs: 200-836-8
  
  health_effects_keywords:
  - respiratory_irritation
  - eye_irritation
  - suspected_carcinogen
  - narcotic_effects
  - skin_sensitization
  
  sources_in_laser_cleaning:
  - alcohol_oxidation
  - polymer_decomposition
  - organic_solvent_breakdown
  - acrylic_degradation
  - polyethylene_thermal_breakdown

---
```

---

## 3. Formatting Rules

### 3.1 Field Naming Conventions

- **Snake_case**: All keys use lowercase with underscores
  - ✅ `ppe_requirements`, `regulatory_standards`, `chemical_formula`
  - ❌ `ppeRequirements`, `RegulatoryStandards`, `chemicalFormula`

- **Descriptive names**: Clear, unambiguous field names
  - ✅ `compliance_level`, `production_mechanism`, `typical_context`
  - ❌ `level`, `mechanism`, `context`

### 3.2 Value Formatting

- **Strings**: Use plain strings or multi-line with `|` for paragraphs
  ```yaml
  description: Short single-line description
  
  description: |
    Multi-line description with
    proper paragraph formatting
    and line breaks preserved.
  ```

- **Numbers**: No quotes for numeric values
  ```yaml
  ✅ value: 2.7
  ❌ value: "2.7"
  ```

- **Booleans**: Lowercase true/false
  ```yaml
  ✅ monitoring_required: true
  ❌ monitoring_required: True
  ```

- **Nulls**: Use `null` not empty strings
  ```yaml
  ✅ ceiling: null
  ❌ ceiling: ""
  ❌ ceiling: ~
  ```

### 3.3 Array Formatting

- **Single-line for short lists**:
  ```yaml
  synonyms: [Acetic aldehyde, Ethanal, Ethyl aldehyde]
  ```

- **Multi-line for complex objects**:
  ```yaml
  related_materials:
  - id: steel-laser-cleaning
    title: Steel
    url: /materials/steel-laser-cleaning
  ```

### 3.4 Indentation

- **2 spaces per level** (not tabs)
- **Consistent alignment** for nested structures

### 3.5 Comments

- Use comments to separate major sections:
  ```yaml
  # ------------------------------------------
  # CROSS-REFERENCES
  # ------------------------------------------
  ```

- Use inline comments sparingly for clarification:
  ```yaml
  frequency: common             # common | uncommon | rare | very_common
  ```

---

## 4. Validation Checklist

Before committing any frontmatter file:

### Required Fields Check
- [ ] `id` present and matches filename
- [ ] `name` present
- [ ] `category` and `subcategory` present
- [ ] `content_type` matches folder (materials/contaminants/compounds/settings)
- [ ] `schema_version` is `5.0.0`
- [ ] `datePublished` and `dateModified` in ISO format
- [ ] `description` present and descriptive
- [ ] `author` present

### Relationships Check
- [ ] All relationship entries have `id`, `title`, `url`
- [ ] No `slug` field in relationship entries
- [ ] No `category`/`subcategory` in relationship entries
- [ ] URLs use full ID (e.g., `/materials/aluminum-laser-cleaning`)
- [ ] Optional fields only populated when data exists
- [ ] All arrays follow unified schema structure

### Data Placement Check
- [ ] Only page-specific fields at top-level
- [ ] All technical/safety/chemical data under `relationships`
- [ ] Parent keys used for organization (e.g., `ppe_requirements`, not flat structure)

### Formatting Check
- [ ] Consistent 2-space indentation
- [ ] Snake_case for all keys
- [ ] No trailing whitespace
- [ ] Proper YAML syntax (quotes, colons, dashes)
- [ ] Multi-line strings use `|` for readability

---

## 5. Migration Priority

### Phase 1: Structure (All Files)
1. Remove `slug` from relationship entries
2. Fix URLs to use full IDs
3. Remove `category`/`subcategory` from relationships

### Phase 2: Reorganization (By Content Type)
1. **Compounds** (~50 files): Move scattered keys under relationships
2. **Materials** (153 files): Move regulatory_standards, properties under relationships
3. **Contaminants** (196 files): Verify structure, add missing cross-references
4. **Settings** (255 files): Similar to contaminants

### Phase 3: Enhancement
1. Add missing optional fields where valuable
2. Populate cross-references between content types
3. Add notes/descriptions to relationship entries
4. Verify all data accurately reflects unified schema

---

## 6. Tools & Scripts

### Validation Script
```bash
# Run YAML validation
python3 scripts/validate_frontmatter.py frontmatter/

# Check specific content type
python3 scripts/validate_frontmatter.py frontmatter/compounds/

# Generate compliance report
python3 scripts/frontmatter_compliance_report.py
```

### Migration Script
```bash
# Dry run (show changes without applying)
python3 scripts/migrate_frontmatter.py --dry-run

# Migrate specific content type
python3 scripts/migrate_frontmatter.py --type compounds

# Migrate all files
python3 scripts/migrate_frontmatter.py --all
```

---

## 7. Examples by Issue Type

### Issue: Slug in relationships
```yaml
# ❌ Before
related_materials:
- id: aluminum-laser-cleaning
  slug: aluminum
  title: Aluminum

# ✅ After
related_materials:
- id: aluminum-laser-cleaning
  title: Aluminum
  url: /materials/aluminum-laser-cleaning
```

### Issue: Scattered data (compounds)
```yaml
# ❌ Before (top-level)
ppe_requirements:
  respiratory: "..."
physical_properties:
  boiling_point: 20.2°C

# ✅ After (under relationships)
relationships:
  ppe_requirements:
    respiratory: "..."
  physical_properties:
    boiling_point: 20.2°C
```

### Issue: Wrong regulatory structure
```yaml
# ❌ Before
regulatory_standards:
- name: FDA
  description: FDA 21 CFR 1040.10

# ✅ After
relationships:
  regulatory_standards:
  - id: fda-laser-product-performance
    title: FDA 21 CFR 1040.10 - Laser Product Performance Standards
    authority: FDA
    url: https://...
    compliance_level: mandatory
```

---

## Summary

This specification provides:
- ✅ Clear parent key organization
- ✅ Unified relationship entry schema
- ✅ Consistent formatting rules
- ✅ Complete examples for each content type
- ✅ Validation checklist
- ✅ Migration guidance

All 654 frontmatter files should follow these specifications for consistency, maintainability, and extensibility.
