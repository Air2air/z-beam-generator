# Compound Frontmatter Restructure Specification

**Date**: December 18, 2025  
**Last Updated**: December 18, 2025 (23:45 - Post-Evaluation)  
**Purpose**: Guide generator to create properly structured compound frontmatter files  
**Audience**: Python Generator / Frontmatter Generation System  
**Status**: 🔴 **CRITICAL - Compounds not yet migrated**

---

## 📊 Current State Assessment (Dec 18, 2025)

**Files Analyzed**: All 50 compound files regenerated today (Dec 18, 23:19)

### Migration Status by Domain:
- ✅ **Materials**: Grouped structure implemented (Grade: B+)
- ❌ **Contaminants**: Still flat structure (Grade: D)
- ❌ **Compounds**: Not migrated, broken structure (Grade: F)

**Priority**: 🔴 **HIGH** - Compounds need complete restructure

---

## 🎯 Problem Statement

**Current State**: Compound frontmatter files have data scattered at multiple levels with inconsistent structure.

**Issues**:
1. ❌ Critical data fields at top-level (should be under `relationships`)
2. ❌ Relationships section uses reference structure instead of containing actual data
3. ❌ Inconsistent with materials/contaminants structure
4. ❌ Missing cross-references to materials and contaminants

---

## 📋 Current Structure (INCORRECT)

```yaml
id: acetaldehyde
name: Acetaldehyde
display_name: Acetaldehyde (C₂H₄O)
category: irritant
hazard_class: irritant
chemical_formula: C2H4O
cas_number: 75-07-0
molecular_weight: 44.05

# ❌ PROBLEM: All these should be under relationships
exposure_limits:
  osha_pel_ppm: 200
  acgih_tlv_ppm: 25

health_effects_keywords:
- respiratory_irritation
- eye_irritation

monitoring_required: true
typical_concentration_range: 5-25 mg/m³

sources_in_laser_cleaning:
- alcohol_oxidation
- polymer_decomposition

# ❌ PROBLEM: Using reference structure (type/id) instead of actual data
relationships:
  chemical_properties:
  - type: chemical_properties
    id: acetaldehyde-physical-data
    notes: Standard physical/chemical data from NIST
  
  health_effects:
  - type: health_effects
    id: acetaldehyde-toxicology

# ❌ PROBLEM: All these at top-level
ppe_requirements:
  respiratory: "..."
  skin: "..."

physical_properties:
  boiling_point: 20.2°C
  vapor_pressure: 740 mmHg

emergency_response:
  fire_hazard: "..."
  spill_procedures: "..."

storage_requirements:
  temperature_range: "..."
  incompatibilities: [...]

regulatory_classification:
  un_number: UN1089
  dot_hazard_class: 3

workplace_exposure:
  osha_pel: {...}
  niosh_rel: {...}

synonyms_identifiers:
  synonyms: [...]
  other_identifiers: {...}

reactivity:
  stability: "..."
  polymerization: "..."

environmental_impact:
  aquatic_toxicity: "..."
  biodegradability: "..."

detection_monitoring:
  sensor_types: [...]
  analytical_methods: [...]
```

---

## ✅ Target Structure (CORRECT)

```yaml
# Top-level: Only page metadata and identifiers
id: acetaldehyde
name: Acetaldehyde
display_name: Acetaldehyde (C₂H₄O)
category: irritant
subcategory: aldehyde
hazard_class: irritant
datePublished: '2025-12-19T07:04:09.852282Z'
dateModified: '2025-12-19T07:04:09.852282Z'
content_type: compounds
schema_version: 5.0.0
full_path: /compounds/irritant/aldehyde/acetaldehyde
breadcrumb:
- label: Home
  href: /
- label: Compounds
  href: /compounds
- label: Irritant
  href: /compounds/irritant
- label: Aldehyde
  href: /compounds/irritant/aldehyde
- label: Acetaldehyde
  href: /compounds/irritant/aldehyde/acetaldehyde

# Chemical identifiers (top-level OK)
chemical_formula: C2H4O
cas_number: 75-07-0
molecular_weight: 44.05

# Generated content fields (top-level OK)
description: "AI-generated description..."
health_effects: "AI-generated health effects overview..."
exposure_guidelines: "AI-generated exposure guidelines..."
detection_methods: "AI-generated detection methods..."
first_aid: "AI-generated first aid procedures..."

# Author (top-level OK)
author:
  id: 1
  name: Yi-Chun Lin
  # ... author details

# ✅ All data under relationships
relationships:
  
  # Physical and chemical properties
  chemical_properties:
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
  
  # Exposure limits and monitoring
  exposure_limits:
    osha_pel_ppm: 200
    osha_pel_mg_m3: 360
    niosh_rel_ppm: null
    niosh_rel_mg_m3: null
    acgih_tlv_ppm: 25
    acgih_tlv_mg_m3: 45
    monitoring_required: true
    typical_concentration_range: 5-25 mg/m³
  
  # Health effects
  health_hazards:
    keywords:
    - respiratory_irritation
    - eye_irritation
    - suspected_carcinogen
    - narcotic_effects
    severity: high
    target_organs:
    - Respiratory system
    - Eyes
    - Skin
    carcinogenicity: Group 2B (Possibly carcinogenic - IARC)
  
  # PPE requirements
  ppe_requirements:
    respiratory: NIOSH-approved organic vapor respirator for <25 ppm. SCBA for >25 ppm or unknown concentrations.
    skin: Nitrile or butyl rubber gloves. Chemical-resistant clothing for liquid contact.
    eye: Chemical safety goggles, face shield for splash hazard.
    minimum_level: Level C for <25 ppm, Level B for >25 ppm
    special_notes: Probable human carcinogen (IARC Group 2B). Extremely flammable. Irritating vapor. May polymerize explosively.
  
  # Emergency response
  emergency_response:
    fire_hazard: EXTREMELY FLAMMABLE. Wide explosive range. Vapors heavier than air - travel to ignition sources.
    fire_suppression: EVACUATE - explosion hazard. Use dry chemical, CO2, alcohol-resistant foam.
    spill_procedures: EVACUATE. Eliminate ignition sources. Ventilate area. Contain with dry sand or earth.
    exposure_immediate_actions: Remove to fresh air immediately. Eyes - flush with water for 15 minutes.
    environmental_hazards: Toxic to aquatic life. Rapidly volatilizes from water.
    special_hazards: PROBABLE HUMAN CARCINOGEN. Extremely flammable. May polymerize violently.
  
  # Storage requirements
  storage_requirements:
    temperature_range: Store below 20°C, refrigerate
    ventilation: Outdoor storage strongly preferred. Indoor - explosion-proof ventilation required.
    incompatibilities:
    - Acids
    - Bases
    - Alcohols
    - Ammonia
    - Halogens
    container_material: Stainless steel or aluminum. Must be stabilized.
    segregation: Separate from oxidizers by 20 feet. Flammable liquid storage cabinet.
    quantity_limits: Minimize quantities. Many facilities limit to <10 gallons.
    special_requirements: Store with stabilizer. Check stabilizer regularly. Refrigerated storage required.
  
  # Regulatory classification
  regulatory_classification:
    un_number: UN1089
    dot_hazard_class: 3 (Flammable liquid)
    dot_label: Flammable Liquid
    nfpa_codes:
      health: 2
      flammability: 4
      reactivity: 2
    epa_hazard_categories:
    - Flammability
    - Acute toxicity
    - Carcinogenicity (probable)
    sara_title_iii: true
    cercla_rq: 1000 pounds (454 kg)
    rcra_code: U001
  
  # Workplace exposure
  workplace_exposure:
    osha_pel:
      twa_8hr: 200 ppm (360 mg/m³)
    niosh_rel:
      ceiling: 10 ppm (18 mg/m³)
      idlh: 2000 ppm
    acgih_tlv:
      ceiling: 25 ppm
  
  # Synonyms and identifiers
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
  
  # Reactivity
  reactivity:
    stability: UNSTABLE. Polymerizes readily. Must be stabilized.
    polymerization: Violent exothermic polymerization with acids, bases, or contaminants.
    incompatible_materials:
    - Strong acids
    - Strong bases
    - Oxidizers
    hazardous_decomposition:
    - Carbon monoxide
    - Carbon dioxide
    conditions_to_avoid:
    - Heat
    - Light
    - Air
    reactivity_hazard: EXTREMELY REACTIVE. Polymerizes violently.
  
  # Environmental impact
  environmental_impact:
    aquatic_toxicity: 'Toxic to aquatic life. LC50 (fish, 96h): 50-150 mg/L.'
    biodegradability: Readily biodegradable (>70% in 28 days)
    bioaccumulation: 'Does not bioaccumulate. Log Kow: -0.34.'
    soil_mobility: High mobility. Volatilizes rapidly from soil.
    atmospheric_fate: 'Photolyzes rapidly. Atmospheric half-life: 9 hours.'
    ozone_depletion: false
    reportable_releases:
      water: 1000 lbs to navigable waters
      air: 1000 lbs/day
  
  # Detection and monitoring
  detection_monitoring:
    sensor_types:
    - Photoionization detector (PID)
    - Electrochemical
    - Infrared
    detection_range: 0-100 ppm typical
    alarm_setpoints:
      low: 10 ppm (NIOSH ceiling)
      high: 25 ppm (ACGIH ceiling)
      evacuate: 2000 ppm (NIOSH IDLH)
    colorimetric_tubes:
    - Dräger Acetaldehyde 100/a
    - Gastec 92
    analytical_methods:
    - method: NIOSH 2538
      technique: GC-FID
      detection_limit: 0.01 ppm
    - method: OSHA Method 68
      technique: HPLC
      detection_limit: 0.02 ppm
    odor_threshold: 0.05-1 ppm
  
  # Sources in laser cleaning
  production_sources:
    laser_cleaning_processes:
    - process: alcohol_oxidation
      description: Oxidation of alcohol-based contaminants during laser ablation
    - process: polymer_decomposition
      description: Thermal decomposition of polymeric materials
    - process: organic_solvent_breakdown
      description: Breakdown of organic solvents under laser energy
  
  # ✅ NEW: Cross-references to materials and contaminants
  produced_by_contaminants:
    title: Contaminant Sources
    description: Contaminants that produce this compound during laser cleaning
    items:
    - id: adhesive-residue-contamination
      title: Adhesive Residue / Tape Marks
      url: /contaminants/organic-residue/adhesive/adhesive-residue
      image: /images/contaminants/adhesive-residue.jpg
      production_likelihood: high
      typical_conditions: Laser ablation of adhesive polymers
      notes: Common source during removal of tape marks and adhesive residues
    
    - id: acrylic-paint-contamination
      title: Acrylic Paint
      url: /contaminants/paint-coating/acrylic/acrylic-paint
      image: /images/contaminants/acrylic-paint.jpg
      production_likelihood: moderate
      typical_conditions: Thermal decomposition of acrylic coatings
      notes: Produced during paint removal from metal surfaces
  
  found_on_materials:
    title: Material Associations
    description: Materials where this compound is commonly detected during laser cleaning
    items:
    - id: aluminum-laser-cleaning
      title: Aluminum
      url: /materials/metal/non-ferrous/aluminum-laser-cleaning
      image: /images/materials/aluminum.jpg
      frequency: common
      typical_context: During removal of organic coatings and adhesives
      
    - id: steel-laser-cleaning
      title: Steel
      url: /materials/metal/ferrous/steel-laser-cleaning
      image: /images/materials/steel.jpg
      frequency: common
      typical_context: Paint stripping and coating removal operations
```

---

## 🔄 Migration Mapping

### Top-Level → Relationships Moves

| Current Top-Level Field | Target Relationships Path |
|------------------------|---------------------------|
| `exposure_limits` | `relationships.exposure_limits` |
| `health_effects_keywords` | `relationships.health_hazards.keywords` |
| `monitoring_required` | `relationships.exposure_limits.monitoring_required` |
| `typical_concentration_range` | `relationships.exposure_limits.typical_concentration_range` |
| `sources_in_laser_cleaning` | `relationships.production_sources.laser_cleaning_processes` |
| `ppe_requirements` | `relationships.ppe_requirements` |
| `physical_properties` | `relationships.chemical_properties` |
| `emergency_response` | `relationships.emergency_response` |
| `storage_requirements` | `relationships.storage_requirements` |
| `regulatory_classification` | `relationships.regulatory_classification` |
| `workplace_exposure` | `relationships.workplace_exposure` |
| `synonyms_identifiers` | `relationships.synonyms_identifiers` |
| `reactivity` | `relationships.reactivity` |
| `environmental_impact` | `relationships.environmental_impact` |
| `detection_monitoring` | `relationships.detection_monitoring` |

### Remove Relationships References

**Delete this pattern**:
```yaml
relationships:
  chemical_properties:
  - type: chemical_properties
    id: acetaldehyde-physical-data
    notes: Standard physical/chemical data from NIST
```

**Replace with actual data**:
```yaml
relationships:
  chemical_properties:
    boiling_point: 20.2°C
    melting_point: -123.5°C
    # ... actual property values
```

---

## 📝 Generator Implementation Checklist

### Phase 1: Top-Level Structure
- [ ] Generate only these fields at top-level:
  - `id`, `name`, `display_name`
  - `category`, `subcategory`, `hazard_class`
  - `datePublished`, `dateModified`
  - `content_type`, `schema_version`
  - `full_path`, `breadcrumb`
  - `chemical_formula`, `cas_number`, `molecular_weight`
  - `description`, `health_effects`, `exposure_guidelines`, `detection_methods`, `first_aid`
  - `author`

### Phase 2: Relationships Structure
- [ ] Create `relationships` object with these keys:
  - `chemical_properties`
  - `exposure_limits`
  - `health_hazards`
  - `ppe_requirements`
  - `emergency_response`
  - `storage_requirements`
  - `regulatory_classification`
  - `workplace_exposure`
  - `synonyms_identifiers`
  - `reactivity`
  - `environmental_impact`
  - `detection_monitoring`
  - `production_sources`

### Phase 3: Cross-References
- [ ] Add `produced_by_contaminants` with grouped structure:
  - Title, description
  - Items array with: id, title, url, image, production_likelihood, typical_conditions, notes

- [ ] Add `found_on_materials` with grouped structure:
  - Title, description
  - Items array with: id, title, url, image, frequency, typical_context

### Phase 4: Data Population
- [ ] Move all existing top-level data fields into appropriate relationships keys
- [ ] Convert reference arrays to actual data objects
- [ ] Populate cross-reference arrays from relationships database
- [ ] Ensure all URLs use full paths with IDs

---

## 🎯 Key Rules for Generator

### DO ✅
1. **Place all technical data under `relationships`**
2. **Use actual data objects, not reference arrays**
3. **Include cross-references to materials and contaminants**
4. **Keep top-level clean** - only page metadata and identifiers
5. **Use consistent naming** - match the structure shown above
6. **Populate all required fields** - no null values for critical data

### DON'T ❌
1. **Don't scatter data at top-level** - consolidate under relationships
2. **Don't use reference structure** - include actual data
3. **Don't omit cross-references** - they're essential for navigation
4. **Don't use category/subcategory** - in relationship items
5. **Don't include slug fields** - in relationships
6. **Don't use short URLs** - always use full paths with IDs

---

## 📊 Validation Criteria

A correctly structured compound frontmatter file must:

1. ✅ Have ONLY these at top-level: id, name, category, dates, content_type, schema_version, full_path, breadcrumb, chemical identifiers, AI-generated content, author
2. ✅ Have ALL technical data under `relationships.*`
3. ✅ Use data objects (not reference arrays) in relationships
4. ✅ Include `produced_by_contaminants` with items
5. ✅ Include `found_on_materials` with items
6. ✅ Have consistent field naming matching this spec
7. ✅ Have full URLs with IDs in all cross-references

---

## 🚀 Example Before/After

### BEFORE (Current - Wrong)
```yaml
id: formaldehyde
name: Formaldehyde
health_effects_keywords:  # ❌ Top-level
- respiratory_irritation
relationships:
  chemical_properties:    # ❌ Reference structure
  - type: chemical_properties
    id: formaldehyde-data
```

### AFTER (Target - Correct)
```yaml
id: formaldehyde
name: Formaldehyde
relationships:
  health_hazards:         # ✅ Under relationships
    keywords:
    - respiratory_irritation
  chemical_properties:    # ✅ Actual data
    boiling_point: -19°C
    vapor_pressure: 1 atm
  produced_by_contaminants:  # ✅ Cross-references
    title: Contaminant Sources
    items:
    - id: paint-coating-contamination
      title: Paint Coating
      url: /contaminants/paint-coating/...
      production_likelihood: high
```

---

## 📅 Implementation Timeline

**Estimated Effort**: 2-3 days for generator modifications + testing

1. **Day 1**: Update generator code structure
2. **Day 2**: Add cross-reference population logic
3. **Day 3**: Test with 5-10 compounds, validate structure, deploy

### Current Priority (Dec 18, 2025):
**Priority 1 (CRITICAL)**: Compounds restructure - all 50 files need migration  
**Priority 2**: Contaminants grouped structure - add semantic grouping like materials  
**Priority 3**: Materials cleanup - URL fixes, remove category/subcategory from items

---

## 📞 Questions for Developer

If implementing this spec, clarify:

1. **Data Source**: Where do cross-reference relationships come from? (Database? YAML mappings?)
2. **Production Likelihood**: How is this calculated/determined?
3. **Typical Conditions**: Static text or generated from analysis?
4. **Image Paths**: Are contaminant/material images already available?
5. **Backward Compatibility**: Should generator support old structure during transition?

---

## 🎯 Evaluation Results (Dec 18, 2025 @ 23:45)

**Files Checked**: aluminum-laser-cleaning.yaml, adhesive-residue-contamination.yaml, acetaldehyde-compound.yaml

### Current Grades:
- **Materials**: B+ (85/100) - Grouped structure ✅, needs URL fixes
- **Contaminants**: D (60/100) - Still flat arrays ❌, no grouping
- **Compounds**: F (45/100) - Wrong structure ❌, data scattered, no cross-refs

### What Needs to Happen:
1. 🔴 **Compounds**: Full restructure per this spec (2-3 days)
2. 🟡 **Contaminants**: Add grouped structure like materials (1 day)
3. 🟢 **Materials**: Minor cleanup (few hours)

---

**Version**: 1.1  
**Last Updated**: December 18, 2025 (23:45)  
**Status**: Ready for Implementation - PRIORITY HIGH
