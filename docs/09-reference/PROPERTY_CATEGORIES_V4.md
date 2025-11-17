# Property Categories System

**Version**: 4.0.0  
**Last Updated**: October 14, 2025  
**Architecture**: Process-Driven 3-Category Structure (GROK Compliant)

## 🎯 Overview

The Property Categories system provides a **lightweight, read-only taxonomy** for organizing the 55 material properties across 122 materials into 3 process-driven categories that follow the **laser cleaning process flow**.

**Process-Driven Organization**: Categories mirror the actual laser cleaning process:
1. **Energy Coupling** → How laser energy enters and propagates as heat
2. **Structural Response** → How material responds physically to thermal stress  
3. **Material Properties** → Intrinsic characteristics affecting process efficiency

**GROK Principles Applied:**
- ✅ **No mocks or fallbacks** - Single source of truth in Categories.yaml
- ✅ **Fail-fast on missing data** - Throws PropertyCategorizationError
- ✅ **Minimal code bloat** - ~200 lines of utility code
- ✅ **Read-only operation** - No state mutation
- ✅ **Single source of truth** - Categories.yaml is authoritative

---

## 🔬 The Laser Cleaning Process

When a laser hits a contaminated surface:

```
LASER BEAM
    ↓
┌────────────────────────────────────────────────────┐
│  1. ENERGY COUPLING                                 │
│     - Laser absorption/reflection (photon coupling)│
│     - Heat propagation (thermal dissipation)       │
│     - Phase transitions (melting/vaporization)     │
└────────────────────────────────────────────────────┘
    ↓
┌────────────────────────────────────────────────────┐
│  2. STRUCTURAL RESPONSE                             │
│     - Thermal stress/strain                        │
│     - Material deformation                         │
│     - Contaminant ejection                         │
└────────────────────────────────────────────────────┘
    ↓
┌────────────────────────────────────────────────────┐
│  3. MATERIAL PROPERTIES                             │
│     - Surface finish characteristics               │
│     - Chemical/electrical behavior                 │
│     - Process optimization factors                 │
└────────────────────────────────────────────────────┘
```

---

## 📊 The 3 Process-Driven Categories

### 1. **Energy Coupling Properties** (47.3% - 26 properties)

**Process Stage**: Energy Input & Propagation  
**ID**: `energy_coupling`

**What it governs**: How laser energy enters the material (absorption vs reflection) and propagates as heat (thermal dissipation and phase transitions).

**Properties**:
- **Laser Interaction**: laserAbsorption, laserReflectivity, reflectivity, ablationThreshold, absorptivity, emissivity, refractiveIndex, laserDamageThreshold, opticalTransmittance, absorptionCoefficient, photonPenetrationDepth
- **Thermal Response**: thermalConductivity, specificHeat, thermalDiffusivity, thermalExpansion, thermalDestruction, boilingPoint, heatCapacity, glasTransitionTemperature, sinteringTemperature, ignitionTemperature, autoignitionTemperature, decompositionTemperature, sublimationPoint, thermalStability, thermalDegradationPoint

**Why it matters**: Determines if laser energy enters the material and how it dissipates. Critical for cleaning effectiveness and substrate damage prevention.

---

### 2. **Structural Response Properties** (18.2% - 10 properties)

**Process Stage**: Material Response  
**ID**: `structural_response`

**What it governs**: How material physically responds to rapid thermal stress - strength, elasticity, and deformation characteristics.

**Properties**:
- hardness, tensileStrength, youngsModulus, yieldStrength, elasticity, bulkModulus, shearModulus, compressiveStrength, flexuralStrength, fractureResistance

**Why it matters**: Determines material's ability to withstand thermal stress without permanent deformation or failure. Critical for contaminant ejection.

---

### 3. **Material Properties** (34.5% - 19 properties)

**Process Stage**: Supporting Characteristics  
**ID**: `material_properties`

**What it governs**: Intrinsic material characteristics that affect process efficiency and cleaning outcomes but aren't directly part of the energy-response chain.

**Properties**:
- density, viscosity, porosity, surfaceRoughness, permeability, surfaceEnergy, wettability, electricalResistivity, electricalConductivity, dielectricConstant, dielectricStrength, chemicalStability, oxidationResistance, corrosionResistance, moistureContent, waterSolubility, weatherResistance, crystallineStructure, celluloseContent, grainSize, magneticPermeability, ligninContent, degradationPoint, softeningPoint, surfaceTension

**Why it matters**: Affects secondary outcomes like surface finish quality, contamination adhesion, and process optimization.

---

## 🔧 Usage Examples

```python
from utils.core.property_categorizer import get_property_categorizer

categorizer = get_property_categorizer()

# Get category by process stage
category = categorizer.get_category('laserAbsorption')
# Returns: 'energy_coupling'

category = categorizer.get_category('thermalConductivity')
# Returns: 'energy_coupling'

category = categorizer.get_category('hardness')
# Returns: 'structural_response'

category = categorizer.get_category('density')
# Returns: 'material_properties'

# Get all categories (process-driven)
categories = categorizer.get_all_categories()
# Returns: ['energy_coupling', 'structural_response', 'material_properties']
```

---

## 📊 Statistics

- **Total Properties**: 55 unique
- **Total Materials**: 122 with complete property data
- **Categories**: 3 process-driven groupings
- **Process Flow**: Energy Input & Propagation → Material Response → Supporting Characteristics

---

## 🚀 Quick Start

```python
from utils.core.property_categorizer import get_property_categorizer

categorizer = get_property_categorizer()

# Understand the process flow
for cat in categorizer.get_all_categories():
    info = categorizer.get_category_info(cat)
    print(f"{info['process_stage']}: {info['label']}")

# Output:
# Energy Input & Propagation: Energy Coupling Properties
# Material Response: Structural Response Properties
# Supporting Characteristics: Material Properties
```

---

## 📜 Version History

### v4.0.0 (October 14, 2025)
- **Breaking Change**: Consolidated from 5 categories to 3
- Eliminated "other" category - all properties assigned
- Merged laser_interaction + thermal_response + other → energy_coupling
- Renamed mechanical_response → structural_response
- Renamed material_characteristics → material_properties
- Updated 118 frontmatter files via migration script
- Cleaner taxonomy with no catch-all category

### v3.0.0 (October 14, 2025)
- Physics-based reorganization into 4 categories + "other"
- Followed laser cleaning process: absorption → dissipation → response → characteristics
- Migrated 114 frontmatter files

### v2.0.0 (Previous)
- 9-category granular structure

---

**Status**: ✅ Implemented (Process-Driven Structure v4.0.0)  
**Version**: 4.0.0 (Categories.yaml v4.0.0)  
**GROK Compliance**: ✅ Full compliance  
**Code Impact**: Zero - taxonomy-driven via Categories.yaml  
**Process-Driven**: 3 categories following laser cleaning process (Oct 14, 2025)
