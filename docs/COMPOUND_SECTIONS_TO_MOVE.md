# Compound Frontmatter: Sections to Move to Relationships

**Date**: December 18, 2025  
**Last Updated**: December 18, 2025 (23:45 - Post-Evaluation)  
**Purpose**: Quick reference for generator - which sections move from top-level to relationships  
**Scope**: All 50 compound frontmatter files  
**Status**: 🔴 **NOT YET MIGRATED** - Files regenerated Dec 18 @ 23:19 with old structure

---

## ⚠️ Current State (Dec 18, 2025)

**Evaluation Complete**: All compounds still have WRONG structure

- ❌ All 15 sections still at top-level (not moved to relationships)
- ❌ Relationships still using reference arrays (not actual data)
- ❌ No cross-references to materials/contaminants
- 🔴 **Priority**: HIGH - Needs immediate migration

---

## 📦 15 Sections to Move from Top-Level → Relationships

### 1. `exposure_limits` → `relationships.exposure_limits`
**Current location**: Top-level  
**New location**: `relationships.exposure_limits`  
**Data**:
```yaml
osha_pel_ppm: 200
osha_pel_mg_m3: 360
niosh_rel_ppm: null
niosh_rel_mg_m3: null
acgih_tlv_ppm: 25
acgih_tlv_mg_m3: 45
```

---

### 2. `health_effects_keywords` → `relationships.health_hazards.keywords`
**Current location**: Top-level  
**New location**: `relationships.health_hazards.keywords`  
**Data**:
```yaml
- respiratory_irritation
- eye_irritation
- suspected_carcinogen
- narcotic_effects
```

---

### 3. `monitoring_required` → `relationships.exposure_limits.monitoring_required`
**Current location**: Top-level  
**New location**: `relationships.exposure_limits.monitoring_required`  
**Data**:
```yaml
true
```

---

### 4. `typical_concentration_range` → `relationships.exposure_limits.typical_concentration_range`
**Current location**: Top-level  
**New location**: `relationships.exposure_limits.typical_concentration_range`  
**Data**:
```yaml
5-25 mg/m³
```

---

### 5. `sources_in_laser_cleaning` → `relationships.production_sources.laser_cleaning_processes`
**Current location**: Top-level  
**New location**: `relationships.production_sources.laser_cleaning_processes`  
**Transform**: Convert from simple array to structured objects  
**Current**:
```yaml
- alcohol_oxidation
- polymer_decomposition
- organic_solvent_breakdown
```
**Target**:
```yaml
- process: alcohol_oxidation
  description: Oxidation of alcohol-based contaminants during laser ablation
- process: polymer_decomposition
  description: Thermal decomposition of polymeric materials
- process: organic_solvent_breakdown
  description: Breakdown of organic solvents under laser energy
```

---

### 6. `ppe_requirements` → `relationships.ppe_requirements`
**Current location**: Top-level  
**New location**: `relationships.ppe_requirements`  
**Data**:
```yaml
respiratory: NIOSH-approved organic vapor respirator for <25 ppm. SCBA for >25 ppm or unknown concentrations.
skin: Nitrile or butyl rubber gloves. Chemical-resistant clothing for liquid contact.
eye: Chemical safety goggles, face shield for splash hazard.
minimum_level: Level C for <25 ppm, Level B for >25 ppm
special_notes: Probable human carcinogen (IARC Group 2B). Extremely flammable. Irritating vapor. May polymerize explosively.
```

---

### 7. `physical_properties` → `relationships.chemical_properties`
**Current location**: Top-level  
**New location**: `relationships.chemical_properties`  
**Data**:
```yaml
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
```

---

### 8. `emergency_response` → `relationships.emergency_response`
**Current location**: Top-level  
**New location**: `relationships.emergency_response`  
**Data**:
```yaml
fire_hazard: EXTREMELY FLAMMABLE. Wide explosive range. Vapors heavier than air - travel to ignition sources. May polymerize explosively in fire.
fire_suppression: EVACUATE - explosion hazard. Stop flow if safe. Use dry chemical, CO2, alcohol-resistant foam. Water spray to cool containers. Do not use water jet directly on liquid.
spill_procedures: EVACUATE. Eliminate ignition sources. Ventilate area. SCBA for large spills. Contain with dry sand or earth. Neutralize with sodium bisulfite. Absorb with vermiculite.
exposure_immediate_actions: 'Remove to fresh air immediately. Eyes: flush with water for 15 minutes. Remove contaminated clothing. Wash skin with soap and water. Seek medical attention - irritation and carcinogen exposure concern.'
environmental_hazards: Toxic to aquatic life. Rapidly volatilizes from water. Biodegrades quickly. Report spills.
special_hazards: PROBABLE HUMAN CARCINOGEN (IARC 2B). Respiratory tract carcinogen in animals. Extremely flammable. May polymerize violently when contaminated. Narcotic at high concentrations. Irritating to eyes and respiratory tract.
```

---

### 9. `storage_requirements` → `relationships.storage_requirements`
**Current location**: Top-level  
**New location**: `relationships.storage_requirements`  
**Data**:
```yaml
temperature_range: Store below 20°C, refrigerate. Keep away from heat.
ventilation: 'Outdoor storage strongly preferred. Indoor: explosion-proof ventilation. Gas detection mandatory.'
incompatibilities:
- Acids
- Bases
- Alcohols
- Ammonia
- Halogens
- Oxidizers
- Phenols
- Hydrogen cyanide
container_material: Stainless steel or aluminum. Must be stabilized. Never use copper or iron containers.
segregation: Separate from oxidizers and incompatibles by 20 feet. Flammable liquid storage cabinet.
quantity_limits: Minimize quantities. Many facilities limit to <10 gallons.
special_requirements: 'CRITICAL: Store with stabilizer. Check stabilizer regularly. Refrigerated storage required. Inert gas blanketing (nitrogen). Post "EXTREMELY FLAMMABLE" and "CANCER HAZARD" signs.'
```

---

### 10. `regulatory_classification` → `relationships.regulatory_classification`
**Current location**: Top-level  
**New location**: `relationships.regulatory_classification`  
**Data**:
```yaml
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
- Eye irritation
sara_title_iii: true
cercla_rq: 1000 pounds (454 kg)
rcra_code: U001
```

---

### 11. `workplace_exposure` → `relationships.workplace_exposure`
**Current location**: Top-level  
**New location**: `relationships.workplace_exposure`  
**Data**:
```yaml
osha_pel:
  twa_8hr: 200 ppm (360 mg/m³)
  stel_15min: null
  ceiling: null
niosh_rel:
  twa_8hr: null
  stel_15min: null
  ceiling: 10 ppm (18 mg/m³) - based on carcinogenicity
  idlh: 2000 ppm
acgih_tlv:
  twa_8hr: null
  stel_15min: null
  ceiling: 25 ppm (confirmed animal carcinogen with unknown relevance to humans)
biological_exposure_indices: []
```

---

### 12. `synonyms_identifiers` → `relationships.synonyms_identifiers`
**Current location**: Top-level  
**New location**: `relationships.synonyms_identifiers`  
**Data**:
```yaml
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
```

---

### 13. `reactivity` → `relationships.reactivity`
**Current location**: Top-level  
**New location**: `relationships.reactivity`  
**Data**:
```yaml
stability: UNSTABLE. Polymerizes readily. Must be stabilized. Oxidizes in air.
polymerization: Violent exothermic polymerization with acids, bases, or contaminants. Stabilizer required.
incompatible_materials:
- Strong acids
- Strong bases
- Oxidizers
- Halogens
- Alcohols
- Ammonia
- Hydrogen cyanide
- Phenols
- Hydrogen sulfide
hazardous_decomposition:
- Carbon monoxide
- Carbon dioxide
- Acetic acid
- Acetaldehyde vapors
conditions_to_avoid:
- Heat
- Light
- Air
- Acids
- Bases
- Sparks
- Flames
- Contamination
reactivity_hazard: EXTREMELY REACTIVE. Polymerizes violently. Reacts violently with oxidizers. Forms explosive peroxides with air. May self-heat and ignite.
```

---

### 14. `environmental_impact` → `relationships.environmental_impact`
**Current location**: Top-level  
**New location**: `relationships.environmental_impact`  
**Data**:
```yaml
aquatic_toxicity: 'Toxic to aquatic life. LC50 (fish, 96h): 50-150 mg/L.'
biodegradability: Readily biodegradable (>70% in 28 days). Oxidizes to acetic acid.
bioaccumulation: 'Does not bioaccumulate. Log Kow: -0.34.'
soil_mobility: High mobility. Volatilizes rapidly from soil.
atmospheric_fate: 'Photolyzes rapidly. Forms peroxyacetyl nitrate (PAN). Atmospheric half-life: 9 hours.'
ozone_depletion: false
global_warming_potential: null
reportable_releases:
  water: 1000 lbs to navigable waters
  air: 1000 lbs/day (CERCLA RQ)
```

---

### 15. `detection_monitoring` → `relationships.detection_monitoring`
**Current location**: Top-level  
**New location**: `relationships.detection_monitoring`  
**Data**:
```yaml
sensor_types:
- Photoionization detector (PID)
- Electrochemical
- Infrared
- Metal oxide
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
odor_threshold: 0.05-1 ppm - provides early warning
```

---

## ✅ Fields That STAY at Top-Level

**Do NOT move these**:

### Page Metadata
- `id`
- `name`
- `display_name`
- `category`
- `subcategory`
- `hazard_class`
- `datePublished`
- `dateModified`
- `content_type`
- `schema_version`
- `full_path`
- `breadcrumb`

### Chemical Identifiers
- `chemical_formula`
- `cas_number`
- `molecular_weight`

### AI-Generated Content Fields
- `description`
- `health_effects`
- `exposure_guidelines`
- `detection_methods`
- `first_aid`

### Author Information
- `author` (entire object)

---

## 🗑️ Also DELETE from relationships

**Current relationships section uses wrong structure** - delete these reference arrays:

```yaml
relationships:
  chemical_properties:  # ❌ DELETE - will be replaced with actual data
  - type: chemical_properties
    id: acetaldehyde-physical-data
    notes: Standard physical/chemical data from NIST
  
  health_effects:  # ❌ DELETE - merged into health_hazards
  - type: health_effects
    id: acetaldehyde-toxicology
    notes: Toxicology data from IARC, NTP, NIOSH
  
  environmental_impact:  # ❌ DELETE - will be replaced with actual data
  - type: environmental_impact
    id: acetaldehyde-environmental-data
    notes: Environmental fate from EPA databases
  
  detection_monitoring:  # ❌ DELETE - will be replaced with actual data
  - type: detection_monitoring
    id: acetaldehyde-monitoring-methods
    notes: NIOSH Method 2538, EPA TO-15
  
  ppe_requirements:  # ❌ DELETE - will be replaced with actual data
  - type: ppe_requirements
    id: irritant-gas-high-concentration
    notes: Level B protection for >25 ppm or unknown concentrations
    overrides:
      specific_compound: acetaldehyde
      ceiling_limit_ppm: 25
  
  emergency_response:  # ❌ DELETE - will be replaced with actual data
  - type: emergency_response
    id: flammable-gas-extremely
    notes: Flash point -39°C, LEL 4%, UEL 60%
    overrides:
      specific_compound: acetaldehyde
      reportable_quantity: 1000 lbs
      iarc_classification: Group 2B (Possibly carcinogenic)
```

---

## 🎯 Quick Summary

**MOVE 15 sections** from top-level into `relationships.*`

**DELETE 6 reference arrays** from current relationships section

**ADD 2 new sections** to relationships:
- `produced_by_contaminants` (cross-references)
- `found_on_materials` (cross-references)

**Result**: Clean, organized structure matching materials/contaminants pattern

---

## 📋 Generator Action Items

1. ✅ Move 15 top-level sections into relationships
2. ✅ Delete 6 reference arrays from relationships
3. ✅ Transform `sources_in_laser_cleaning` from array to structured objects
4. ✅ Add `produced_by_contaminants` with proper items structure
5. ✅ Add `found_on_materials` with proper items structure
6. ✅ Keep top-level clean (metadata + identifiers + AI content + author only)

---

## 📊 Implementation Status

### By Domain (Dec 18, 2025):

| Domain | Structured? | Grouped? | Cross-refs? | Grade | Priority |
|--------|-------------|----------|-------------|-------|----------|
| **Materials** | ✅ Yes | ✅ Yes | ⚠️ Partial | B+ (85%) | 🟢 LOW |
| **Contaminants** | ⚠️ Partial | ❌ No | ⚠️ Partial | D (60%) | 🟡 MEDIUM |
| **Compounds** | ❌ No | N/A | ❌ No | F (45%) | 🔴 HIGH |

### Next Steps:
1. 🔴 **Fix compounds first** - Use this doc + full spec
2. 🟡 **Add contaminant grouping** - Follow materials pattern
3. 🟢 **Clean up materials** - Remove category/subcategory, fix URLs

---

**Version**: 1.1  
**Last Updated**: December 18, 2025 (23:45)  
**See Also**: `COMPOUND_FRONTMATTER_RESTRUCTURE_SPEC.md` (full specification)  
**Status**: Ready for immediate implementation
