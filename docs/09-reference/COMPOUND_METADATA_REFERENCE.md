# Compounds Domain - Metadata Field Reference

**Last Updated**: December 15, 2025  
**Version**: 2.0.0  
**Status**: Enhanced with 10 new metadata categories (1,140 additional data points)

## Overview

The Compounds domain contains comprehensive hazardous chemical data for 20 compounds generated during laser cleaning operations. Each compound now includes **25+ metadata fields** across 10 categories, providing complete safety, regulatory, and operational information.

---

## Original Metadata Fields (15 fields)

### Core Identification
- **id**: Unique compound identifier (slug format)
- **name**: Full compound name
- **display_name**: Display name with chemical formula
- **slug**: URL-friendly identifier
- **chemical_formula**: Molecular formula
- **cas_number**: Chemical Abstracts Service registry number
- **molecular_weight**: Molecular weight in g/mol

### Classification
- **category**: Primary hazard category (carcinogen, toxic_gas, corrosive, etc.)
- **subcategory**: Specific subcategory
- **hazard_class**: Regulatory hazard classification
- **author**: Assigned author ID for content generation

### Exposure & Monitoring
- **exposure_limits**: OSHA PEL, NIOSH REL, ACGIH TLV values (ppm and mg/m³)
- **monitoring_required**: Boolean flag for monitoring requirements
- **typical_concentration_range**: Expected concentration in laser cleaning
- **sources_in_laser_cleaning**: Material sources generating this compound

### Content Fields (To Be Generated)
- **description**: Compound description (null until generated)
- **health_effects**: Health effects description (null until generated)
- **exposure_guidelines**: Exposure guidelines (null until generated)
- **detection_methods**: Detection methods (null until generated)
- **first_aid**: First aid procedures (null until generated)

---

## Enhanced Metadata Categories (10 new categories, 60+ fields per compound)

### 1. PPE Requirements

Personal protective equipment guidance for safe handling.

**Fields**:
- `respiratory`: Respiratory protection requirements by concentration
- `skin`: Skin protection (gloves, suits, breakthrough times)
- `eye`: Eye protection (goggles, face shields)
- `minimum_level`: OSHA protection level (A, B, C, D)
- `special_notes`: Critical safety information (carcinogenicity, skin absorption, special hazards)

**Example** (Formaldehyde):
```yaml
ppe_requirements:
  respiratory: "Full-face NIOSH-approved respirator with formaldehyde cartridges for <0.75 ppm. SCBA >0.75 ppm."
  skin: "Nitrile or butyl rubber gloves (>8hr breakthrough). Chemical-resistant suit for high exposure."
  eye: "Chemical safety goggles or full-face respirator. Face shield for splash."
  minimum_level: "Level C for <0.75 ppm, Level B for unknown concentrations"
  special_notes: "IARC Group 1 carcinogen. Strong sensitizer. Formaldehyde-specific cartridges required."
```

---

### 2. Physical Properties

Complete physical and chemical property data.

**Fields**:
- `boiling_point`: Boiling point (°C and °F)
- `melting_point`: Melting point (°C and °F)
- `vapor_pressure`: Vapor pressure at 20°C
- `vapor_density`: Vapor density (Air=1)
- `specific_gravity`: Specific gravity
- `flash_point`: Flash point (°C and °F)
- `autoignition_temp`: Autoignition temperature
- `explosive_limits`: LEL and UEL percentages
- `appearance`: Physical appearance
- `odor`: Odor description and threshold

**Example** (Styrene):
```yaml
physical_properties:
  boiling_point: "145°C (293°F)"
  flash_point: "31°C (88°F)"
  explosive_limits: "LEL: 1.1%, UEL: 6.1%"
  vapor_density: "3.6 (Air=1)"
  odor: "Sweet floral odor @ 0.05-0.5 ppm BUT olfactory fatigue occurs - cannot rely on odor"
```

---

### 3. Emergency Response

Comprehensive emergency procedures and hazard information.

**Fields**:
- `fire_hazard`: Flammability and combustion hazards
- `fire_suppression`: Appropriate fire suppression methods
- `spill_procedures`: Spill containment and cleanup procedures
- `exposure_immediate_actions`: First response to exposure (eyes, skin, inhalation)
- `environmental_hazards`: Environmental impact of releases
- `special_hazards`: Critical warnings (carcinogenicity, delayed effects, unique hazards)

**Example** (Phosgene):
```yaml
emergency_response:
  special_hazards: "CHEMICAL WARFARE AGENT (WWI). DELAYED PULMONARY EDEMA 2-48 hours post-exposure. Odor threshold >0.4 ppm ABOVE IDLH - do not rely on odor. Asymp-tomatic period before sudden respiratory failure. Keep exposed persons at absolute rest for 48 hours."
```

---

### 4. Storage Requirements

Safe storage conditions and incompatibilities.

**Fields**:
- `temperature_range`: Required storage temperature
- `ventilation`: Ventilation requirements
- `incompatibilities`: List of incompatible materials
- `container_material`: Suitable container materials
- `segregation`: Segregation requirements from other materials
- `quantity_limits`: Storage quantity limits (NFPA, OSHA)
- `special_requirements`: Critical storage notes (stabilizers, monitoring, labeling)

**Example** (Acetaldehyde):
```yaml
storage_requirements:
  temperature_range: "Below 20°C refrigerated"
  special_requirements: "MUST be stabilized. Inert gas blanketing (nitrogen) required. Check stabilizer level regularly. Forms explosive peroxides with air."
```

---

### 5. Regulatory Classification

Complete regulatory and hazard classification data.

**Fields**:
- `un_number`: United Nations identification number
- `dot_hazard_class`: Department of Transportation hazard class
- `dot_label`: DOT hazard label
- `nfpa_codes`: NFPA 704 diamond ratings (health, flammability, reactivity, special)
- `epa_hazard_categories`: EPA hazard categories
- `sara_title_iii`: SARA Title III listing (boolean)
- `cercla_rq`: CERCLA Reportable Quantity
- `rcra_code`: RCRA hazardous waste code

**Example** (Benzene):
```yaml
regulatory_classification:
  un_number: "UN1114"
  dot_hazard_class: "3 (Flammable liquid)"
  nfpa_codes: {health: 2, flammability: 3, reactivity: 0}
  cercla_rq: "10 pounds (4.54 kg)"
  rcra_code: "U019"
```

---

### 6. Workplace Exposure (Enhanced)

Comprehensive exposure limits and biological monitoring.

**Fields**:
- `osha_pel`: OSHA Permissible Exposure Limit (TWA, STEL, Ceiling)
- `niosh_rel`: NIOSH Recommended Exposure Limit (TWA, STEL, Ceiling, IDLH)
- `acgih_tlv`: ACGIH Threshold Limit Value (TWA, STEL, Ceiling)
- `biological_exposure_indices`: Array of BEI values with:
  - `metabolite`: Metabolite name
  - `specimen`: Sample type (urine, blood, exhaled air)
  - `timing`: Sample timing (end of shift, pre-shift, etc.)
  - `bei_value`: Threshold value

**Example** (Toluene):
```yaml
workplace_exposure:
  osha_pel: {twa_8hr: "200 ppm", stel_15min: "300 ppm", ceiling: "500 ppm (peak)"}
  niosh_rel: {twa_8hr: "100 ppm", stel_15min: "150 ppm", idlh: "500 ppm"}
  acgih_tlv: {twa_8hr: "20 ppm"}  # Much stricter due to neurotoxicity
  biological_exposure_indices:
    - metabolite: "o-Cresol"
      specimen: "Urine"
      timing: "End of shift"
      bei_value: "0.5 mg/L"
```

---

### 7. Synonyms & Identifiers

Alternative names and database identifiers.

**Fields**:
- `synonyms`: Array of chemical synonyms
- `common_trade_names`: Commercial product names
- `other_identifiers`:
  - `rtecs_number`: Registry of Toxic Effects of Chemical Substances
  - `ec_number`: European Community number
  - `pubchem_cid`: PubChem Compound ID

**Example** (Carbon Monoxide):
```yaml
synonyms_identifiers:
  synonyms: ["CO", "Carbon oxide", "Carbonic oxide", "Flue gas", "Exhaust gas"]
  rtecs_number: "FG3500000"
  ec_number: "211-128-3"
  pubchem_cid: "281"
```

---

### 8. Reactivity

Chemical stability and incompatibility information.

**Fields**:
- `stability`: Stability under normal conditions
- `polymerization`: Polymerization hazard
- `incompatible_materials`: List of incompatible substances
- `hazardous_decomposition`: Decomposition products
- `conditions_to_avoid`: Conditions causing decomposition or reaction
- `reactivity_hazard`: Specific reactivity warnings

**Example** (Formaldehyde):
```yaml
reactivity:
  stability: "Pure formaldehyde unstable. Solutions polymerize without stabilizer."
  polymerization: "Polymerizes to paraformaldehyde with impurities, acids, bases, or cooling. Exothermic."
  incompatible_materials: ["Strong oxidizers", "Strong acids", "Phenols", "Nitrogen dioxide"]
  reactivity_hazard: "Reacts with phenols forming heat-sensitive explosives. Reacts with nitrogen dioxide forming explosive nitro compounds."
```

---

### 9. Environmental Impact

Environmental fate and ecological effects.

**Fields**:
- `aquatic_toxicity`: LC50 values for aquatic organisms
- `biodegradability`: Biodegradation rate and percentage
- `bioaccumulation`: BCF (bioconcentration factor) and Log Kow
- `soil_mobility`: Soil adsorption and mobility
- `atmospheric_fate`: Atmospheric half-life and degradation pathways
- `ozone_depletion`: Ozone depletion potential (boolean)
- `global_warming_potential`: GWP value or None
- `reportable_releases`:
  - `water`: Reportable quantity to water
  - `air`: Reportable quantity to air

**Example** (Styrene):
```yaml
environmental_impact:
  aquatic_toxicity: "LC50 (fish, 96h): 4-10 mg/L"
  biodegradability: "Readily biodegradable (>60% in 28 days)"
  bioaccumulation: "Moderate potential. BCF: 25-150. Log Kow: 2.95"
  atmospheric_fate: "Atmospheric half-life: 1-2 days. Photolyzes via hydroxyl radicals. Forms ozone."
```

---

### 10. Detection & Monitoring

Monitoring equipment and analytical methods.

**Fields**:
- `sensor_types`: Array of sensor technologies (PID, FID, electrochemical, IR, etc.)
- `detection_range`: Typical detection range in ppm
- `alarm_setpoints`:
  - `low`: Low-level alarm (typically TLV)
  - `high`: High-level alarm (typically PEL or STEL)
  - `evacuate`: Evacuation level (typically IDLH)
- `colorimetric_tubes`: Available detector tube brands/models
- `analytical_methods`: Array of NIOSH/OSHA/EPA methods:
  - `method`: Method number
  - `technique`: Analytical technique (GC-FID, HPLC, etc.)
  - `detection_limit`: Method detection limit
- `odor_threshold`: Odor detection threshold with reliability notes

**Example** (Formaldehyde):
```yaml
detection_monitoring:
  sensor_types: ["Electrochemical", "Photoionization detector (PID)", "Colorimetric"]
  detection_range: "0-10 ppm typical"
  alarm_setpoints:
    low: "0.3 ppm (ACGIH ceiling)"
    high: "0.75 ppm (OSHA PEL)"
    evacuate: "20 ppm (NIOSH IDLH)"
  analytical_methods:
    - method: "NIOSH 2541"
      technique: "HPLC (2,4-DNPH derivatization)"
      detection_limit: "0.006 ppm"
  odor_threshold: "0.05-1 ppm - early warning but olfactory fatigue occurs. Do not rely on odor alone."
```

---

## Critical Safety Warnings by Compound

### IARC Group 1 Carcinogens (Known Human Carcinogens)
1. **Formaldehyde**: Nasopharyngeal cancer, leukemia
2. **Benzene**: Leukemia, bone marrow damage
3. **Benzo[a]pyrene**: Lung cancer, skin cancer

### IARC Group 2B (Probable Human Carcinogens)
1. **Acetaldehyde**: Respiratory tract carcinogen (animal)
2. **Styrene**: Neurotoxin + carcinogen
3. **Chromium VI**: Lung cancer (hexavalent form)

### Extremely Toxic Gases (IDLH <50 ppm)
1. **Phosgene**: IDLH 2 ppm, delayed pulmonary edema 2-48 hours
2. **Hydrogen Cyanide**: IDLH 50 ppm, cellular respiration inhibitor

### Special Hazards
1. **Styrene**: Olfactory fatigue - cannot rely on odor
2. **Hydrogen Cyanide**: Wide olfactory variation (genetic)
3. **Nitrogen Oxides**: Delayed pulmonary edema 6-72 hours
4. **Acrolein**: Lachrymator, delayed pulmonary edema
5. **Acetaldehyde**: Widest explosive range (4-60%)
6. **Carbon Dioxide**: Odorless simple asphyxiant

---

## Usage in Content Generation

These enhanced metadata fields provide rich source material for generating:

1. **Material Descriptions**: Physical properties, appearance, odor
2. **Health Effects**: Special hazards, exposure symptoms, chronic effects
3. **Exposure Guidelines**: OSHA/NIOSH/ACGIH limits, BEI values, alarm setpoints
4. **Detection Methods**: Sensors, analytical methods, colorimetric tubes
5. **First Aid**: Emergency response procedures, exposure actions

### Example Prompt Enhancement

**Before** (15 basic fields):
```
Generate description for Styrene.
Available data: molecular_weight: 104.15, category: VOC, exposure_limits: 100 ppm
```

**After** (25+ enhanced fields):
```
Generate description for Styrene.
Available data:
- Physical: BP 145°C, sweet floral odor @ 0.05-0.5 ppm
- Special hazard: OLFACTORY FATIGUE OCCURS - cannot rely on odor
- Health: IARC 2B carcinogen, neurotoxin (CNS depression, peripheral neuropathy)
- Exposure: ACGIH 20 ppm (much stricter than OSHA 100 ppm)
- BEI: Mandelic + phenylglyoxylic acid 400 mg/g creatinine
- Storage: Polymerization inhibitor required (10-15 ppm tert-butylcatechol)
- Detection: PID/FID/IR sensors, NIOSH 1501 GC-FID
```

Result: **Much richer, more accurate, professionally detailed content**.

---

## Data Sources

All metadata researched from authoritative sources:
- **NIOSH** - Occupational safety data, analytical methods
- **OSHA** - Regulatory exposure limits, PELs
- **ACGIH** - Threshold Limit Values, BEIs
- **EPA** - Environmental data, reportable quantities
- **DOT** - Transportation classification, UN numbers
- **NFPA** - Fire diamond ratings
- **NIST** - Physical property data
- **PubChem** - Chemical identifiers, properties
- **IARC** - Carcinogenicity classifications

---

## Metadata Completeness

**Status**: 20/20 compounds (100% complete)

All compounds include:
- ✅ 15 original fields
- ✅ 10 new metadata categories
- ✅ ~60 individual data points per compound
- ✅ 1,140 total new data points added
- ✅ Quality verified against SDS cross-checks

**Total Dataset**: 1,440+ individual data points across 20 compounds

---

## Field Glossary

**ACGIH TLV**: American Conference of Governmental Industrial Hygienists Threshold Limit Value  
**BEI**: Biological Exposure Index - metabolite levels indicating exposure  
**BCF**: Bioconcentration Factor - bioaccumulation in organisms  
**CERCLA RQ**: Comprehensive Environmental Response, Compensation, and Liability Act Reportable Quantity  
**DOT**: Department of Transportation  
**GWP**: Global Warming Potential  
**IARC**: International Agency for Research on Cancer  
**IDLH**: Immediately Dangerous to Life or Health  
**LEL/UEL**: Lower/Upper Explosive Limit  
**Log Kow**: Octanol-water partition coefficient (lipophilicity)  
**NFPA**: National Fire Protection Association  
**NIOSH REL**: National Institute for Occupational Safety and Health Recommended Exposure Limit  
**OSHA PEL**: Occupational Safety and Health Administration Permissible Exposure Limit  
**PID/FID**: Photoionization Detector / Flame Ionization Detector  
**RCRA**: Resource Conservation and Recovery Act  
**RTECS**: Registry of Toxic Effects of Chemical Substances  
**SARA**: Superfund Amendments and Reauthorization Act  
**SCBA**: Self-Contained Breathing Apparatus  
**STEL**: Short-Term Exposure Limit (15 minutes)  
**TWA**: Time-Weighted Average (8 hours)  

---

## Version History

**Version 2.0.0** (December 15, 2025)
- ✅ Added 10 new metadata categories
- ✅ 1,140 additional data points researched
- ✅ All 20 compounds enhanced
- ✅ Quality verified against SDS sources

**Version 1.0.0** (Initial)
- 15 basic metadata fields
- 20 compounds identified
