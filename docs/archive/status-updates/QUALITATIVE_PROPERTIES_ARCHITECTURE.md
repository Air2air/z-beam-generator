# Qualitative Properties Architecture

**Date:** October 17, 2025  
**Status:** 🚧 Implementation in Progress

---

## 🎯 Objective

Create a dedicated categorization system for qualitative (non-numeric) properties that currently exist alongside quantitative properties in `materialProperties`. These should be elevated to a new top-level category for clarity and proper handling.

---

## 📊 Current State Analysis

### Identified Qualitative Properties
1. **thermalDestructionType**: Categorical values like "melting", "decomposition", "sublimation", "vaporization"
2. **toxicity**: Rating values like "Low", "Medium", "High", "None"
3. **Future qualitative properties**: color, texture, appearance, classification types, etc.

### Current Structure Problems
❌ Qualitative properties mixed with quantitative in `materialProperties`  
❌ min/max validation incorrectly applied to qualitative properties  
❌ No clear semantic distinction between property types  
❌ Confusing for users and difficult to process  

---

## 🏗️ New Architecture

### Top-Level Categories

```yaml
name: Cast Iron
category: Metal
subcategory: ferrous
title: Cast Iron Laser Cleaning
description: Laser cleaning parameters for Cast Iron

# Quantitative numeric properties
materialProperties:
  material_characteristics:
    properties:
      density: {...}
      hardness: {...}
  laser_material_interaction:
    properties:
      laserAbsorption: {...}
      reflectivity: {...}

# Qualitative categorical properties  
materialCharacteristics:
  thermal_behavior:
    label: Thermal Behavior
    description: Qualitative thermal response characteristics
    properties:
      thermalDestructionType:
        value: melting
        confidence: 99
        description: Primary mechanism of thermal destruction
        allowedValues: [melting, decomposition, sublimation, vaporization, oxidation]
  
  safety_handling:
    label: Safety & Handling
    description: Qualitative safety and handling characteristics
    properties:
      toxicity:
        value: Low
        confidence: 95
        description: Toxicity rating for handling and disposal
        allowedValues: [None, Low, Medium, High, Extreme]

# Machine configuration
machineSettings:
  power_settings: {...}
  scanning_parameters: {...}
```

### Property Type Classification

**Quantitative Properties** (materialProperties):
- Have numeric values
- Require min/max ranges
- Support statistical analysis
- Examples: density, temperature, wavelength

**Qualitative Properties** (materialCharacteristics):
- Have categorical/text values
- Use allowedValues enumeration
- Support classification/categorization
- Examples: destructionType, toxicity, color

**Machine Settings** (machineSettings):
- Configuration parameters
- Can be quantitative or qualitative
- Device-specific

---

## 🔧 Implementation Components

### 1. Schema Updates
- **File**: `schemas/active/frontmatter.json`
- Add `materialCharacteristics` as top-level property
- Define subcategories: thermal_behavior, safety_handling, physical_appearance
- Add `allowedValues` field for enumerations
- Remove min/max requirements for qualitative properties

### 2. Property Classification Logic
- **File**: `components/frontmatter/core/streamlined_generator.py`
- Add `_classify_property_type()` method
- Route qualitative properties to materialCharacteristics
- Route quantitative properties to materialProperties
- Skip min/max validation for qualitative

### 3. Property Research Service
- **File**: `components/frontmatter/services/property_research_service.py`
- Update `research_material_properties()` to classify and route
- Add `research_material_characteristics()` for qualitative
- Define allowed values for each qualitative property

### 4. Template Updates
- **File**: `components/frontmatter/templates/`
- Update templates to handle materialCharacteristics
- Add rendering logic for qualitative properties

### 5. Validation Updates
- **File**: `validation/`
- Add QualitativePropertyValidator
- Validate against allowedValues
- Skip numeric range validation

---

## 📋 Property Categorization Matrix

### materialCharacteristics Subcategories

#### thermal_behavior
- thermalDestructionType: [melting, decomposition, sublimation, vaporization, oxidation, charring]
- thermalStability: [poor, fair, good, excellent]
- heatTreatmentResponse: [hardenable, non-hardenable, age-hardenable]

#### safety_handling
- toxicity: [None, Low, Medium, High, Extreme]
- flammability: [non-flammable, low, moderate, high, extremely-flammable]
- reactivity: [stable, low, moderate, high, explosive]
- corrosivityLevel: [non-corrosive, mildly-corrosive, corrosive, highly-corrosive]

#### physical_appearance
- color: [silver, gray, black, bronze, copper, gold, etc.]
- surfaceFinish: [polished, brushed, matte, rough, oxidized]
- transparency: [opaque, translucent, transparent]

#### material_classification
- crystalStructure: [FCC, BCC, HCP, amorphous, etc.]
- microstructure: [single-phase, multi-phase, composite]
- processingMethod: [cast, forged, machined, sintered, additive]

---

## 🔄 Migration Strategy

### Phase 1: Schema & Infrastructure ✅
1. Update frontmatter.json schema
2. Add materialCharacteristics definition
3. Update validation to handle both types

### Phase 2: Classification Logic ✅
1. Implement property type detection
2. Add routing logic in generator
3. Update property research service

### Phase 3: Extraction & Population ⏳
1. Extract existing qualitative properties
2. Migrate to materialCharacteristics
3. Remove from materialProperties

### Phase 4: Regeneration 📋
1. Regenerate all frontmatter files
2. Validate new structure
3. Update documentation

### Phase 5: Enhancement 🎯
1. Add more qualitative properties
2. Expand allowed values
3. Add semantic relationships

---

## 🎨 Allowed Values Definitions

```python
QUALITATIVE_PROPERTY_DEFINITIONS = {
    'thermalDestructionType': {
        'category': 'thermal_behavior',
        'allowedValues': ['melting', 'decomposition', 'sublimation', 'vaporization', 'oxidation', 'charring'],
        'description': 'Primary mechanism by which material thermally degrades',
        'unit': 'type'
    },
    'toxicity': {
        'category': 'safety_handling',
        'allowedValues': ['None', 'Low', 'Medium', 'High', 'Extreme'],
        'description': 'Toxicity level for safety and handling considerations',
        'unit': 'rating'
    },
    'flammability': {
        'category': 'safety_handling',
        'allowedValues': ['non-flammable', 'low', 'moderate', 'high', 'extremely-flammable'],
        'description': 'Flammability classification',
        'unit': 'rating'
    },
    'color': {
        'category': 'physical_appearance',
        'allowedValues': ['silver', 'gray', 'black', 'bronze', 'copper', 'gold', 'white', 'red', 'blue', 'green', 'yellow', 'brown'],
        'description': 'Primary visual color of material',
        'unit': 'color'
    },
    'crystalStructure': {
        'category': 'material_classification',
        'allowedValues': ['FCC', 'BCC', 'HCP', 'amorphous', 'cubic', 'hexagonal', 'tetragonal', 'orthorhombic'],
        'description': 'Crystal lattice structure type',
        'unit': 'structure'
    }
}
```

---

## ✅ Success Criteria

- [ ] Schema updated with materialCharacteristics
- [ ] Classification logic implemented
- [ ] Qualitative properties properly routed
- [ ] No min/max validation on qualitative properties
- [ ] AllowedValues validation working
- [ ] All frontmatter regenerated with new structure
- [ ] Zero null values for qualitative properties
- [ ] Clear semantic separation of property types

---

## 📈 Benefits

1. **Clarity**: Clear distinction between quantitative and qualitative data
2. **Validation**: Proper validation (enumeration vs ranges)
3. **Semantics**: Better semantic meaning and searchability
4. **Extensibility**: Easy to add new qualitative properties
5. **User Experience**: Clearer documentation and understanding
6. **Data Quality**: Prevent invalid values through allowedValues

---

## 🚀 Next Steps

1. Implement schema changes
2. Update classification logic
3. Migrate existing qualitative properties
4. Regenerate frontmatter
5. Validate and test
6. Document new structure

