# Materials.yaml Field Analysis Report

## Overview

Comprehensive analysis of all fields in Materials.yaml to identify category/subcategory-applicable fields beyond materialProperties and machineSettings.

### Analysis Summary
- **Total Categories Found**: 9
- **Total Subcategories Found**: 0 
- **Total Materials Analyzed**: 123
- **Unique Fields Found**: 58

## Categories and Subcategories Found

### Categories (9)
- ceramic
- composite
- glass
- masonry
- metal
- plastic
- semiconductor
- stone
- wood

### Subcategories (0)
None found

## Field Categorization for Categories.yaml

### 🔧 Material Properties Candidates (16)
*Fields suitable for materialProperties section*
- `chemical_resistance` (used 1x)
- `compressive_strength` (used 30x)
- `density` (used 9x)
- `firing_temperature` (used 1x)
- `flexural_strength` (used 5x)
- `fracture_toughness` (used 2x)
- `hardness` (used 69x)
- `ionic_conductivity` (used 1x)
- `melting_point` (used 13x)
- `porosity` (used 27x)
- `specificHeat` (used 9x)
- `tensileStrength` (used 63x)
- `thermalConductivity` (used 108x)
- `thermalDiffusivity` (used 9x)
- `thermalExpansion` (used 74x)
- `youngsModulus` (used 63x)

### ⚙️ Machine Settings Candidates (2)
*Fields suitable for machineSettings section*
- `laserAbsorption` (used 9x)
- `laserReflectivity` (used 9x)

### 🏭 Industry & Regulatory Fields (2)
*Fields for industry tags and regulatory standards*
- `industryTags` (used 123x)
- `regulatoryStandards` (used 123x)

### ⚡ Electrical Properties (2)
*Fields for electrical characteristics*
- `dielectric_constant` (used 3x)
- `electricalResistivity` (used 38x)

### 💡 Optical Properties (0)
*Fields for optical/laser interaction properties*
None found

### 🔥 Processing Fields (4)
*Fields for processing conditions and thermal properties*
- `curie_temperature` (used 2x)
- `operating_temperature` (used 13x)
- `thermalDestructionPoint` (used 9x)
- `thermalDestructionType` (used 9x)

### 🧪 Physical Test Fields (2)
*Fields for mechanical testing results*
- `strength` (used 1x)
- `yield_strength` (used 3x)

### 📋 Metadata Fields (1)
*Fields for content management and organization*
- `author` (used 123x)

### 🏷️ Taxonomic Fields (1)
*Fields for material classification*
- `category` (used 123x)

### ❓ Uncategorized Fields (23)
*Fields requiring further analysis*
- `antimicrobial_properties` (used 1x)
- `bandgap` (used 4x)
- `chromium_content` (used 1x)
- `color` (used 1x)
- `common_alloys` (used 2x)
- `composition` (used 2x)
- `corrosion_resistance` (used 3x)
- `crystal_structure` (used 7x)
- `documentation_status` (used 1x)
- `grades` (used 1x)
- `grain_pattern` (used 1x)
- `grain_structure_type` (used 11x)
- `growth_type` (used 1x)
- `machinability` (used 1x)
- `magnetic_properties` (used 3x)
- `mineral_composition` (used 18x)
- `moisture_content` (used 12x)
- `natural_oils` (used 2x)
- `nickel_content` (used 1x)
- `resin_content` (used 12x)
- `specific_heat` (used 11x)
- `tannin_content` (used 11x)
- `water_absorption` (used 7x)

## Recommended Categories.yaml Extensions

Based on this analysis, the Categories.yaml structure should be extended to include:

### 1. Industry & Applications Section
```yaml
categories:
  metal:
    industry_applications:
      common_industries: [Automotive, Aerospace, Medical, Electronics]
      regulatory_standards: 
        - OSHA 29 CFR 1926.95
        - FDA 21 CFR 1040.10
        - ANSI Z136.1
```

### 2. Electrical Properties Section  
```yaml
categories:
  ceramic:
    electricalProperties:
      dielectric_constant:
        min: 2.0
        max: 25.0
        unit: unitless
      electricalResistivity:
        min: 1e10
        max: 1e16
        unit: Ω·cm
```

### 3. Processing Parameters Section
```yaml  
categories:
  ceramic:
    processingParameters:
      firing_temperature:
        min: 1000
        max: 1700
        unit: °C
      porosity:
        min: 0
        max: 15
        unit: '%'
```

## Most Frequent Fields by Category

| Category | Unique Fields | Most Common Fields |
|----------|---------------|--------------------|
| ceramic | 17 | author (123), category (123), chemical_resistance (1) |
| composite | 8 | author (123), category (123), industryTags (123) |
| glass | 9 | author (123), category (123), hardness (69) |
| masonry | 8 | author (123), category (123), compressive_strength (30) |
| metal | 25 | antimicrobial_properties (1), author (123), category (123) |
| plastic | 5 | author_id (123), category (123), hardness (69) |
| semiconductor | 12 | author_id (123), bandgap (4), category (123) |
| stone | 10 | author_id (123), category (123), compressive_strength (30) |
| wood | 14 | author_id (123), category (123), grain_pattern (1) |


## Field Type Distribution

| Field | Types Found | Examples |
|-------|-------------|----------|
| antimicrobial_properties | bool | Used 1x |
| article_type | str | Used 9x |
| author_id | int | Used 123x |
| bandgap | str | Used 4x |
| category | str | Used 123x |
| chemical_resistance | str | Used 1x |
| chromium_content | str | Used 1x |
| color | str | Used 1x |
| common_alloys | str | Used 2x |
| composition | str | Used 2x |


## Recommendations

1. **Extend Categories.yaml Schema**: Add sections for industry applications, electrical properties, and processing parameters
2. **Standardize Units**: Many fields have inconsistent unit formats that should be normalized
3. **Add Validation**: Implement validation for field ranges and data types
4. **Consider Subcategory Specificity**: Some fields may benefit from subcategory-specific ranges
5. **Include Regulatory Data**: Industry tags and regulatory standards are valuable for practical applications

## Next Steps

1. Update Categories.yaml schema to include new field categories
2. Research appropriate ranges for electrical and processing properties
3. Create validation rules for new field types
4. Consider AI research for subcategory-specific property refinements
