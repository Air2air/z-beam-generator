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

**Why it matters**: Thermal expansion creates mechanical stress - these determine whether material ablates cleanly or damages structurally.

---

### 4. **Material Characteristics** (40.0% - 22 properties)

**Physics Stage**: Supporting Properties  
**ID**: `material_characteristics`

**What it governs**: Intrinsic characteristics affecting secondary outcomes like surface finish and process efficiency.

**Properties**:
- density, viscosity, porosity, surfaceRoughness, permeability, surfaceEnergy, wettability, electricalResistivity, electricalConductivity, dielectricConstant, dielectricStrength, chemicalStability, oxidationResistance, corrosionResistance, moistureContent, waterSolubility, weatherResistance, crystallineStructure, celluloseContent, grainSize, magneticPermeability, photonPenetrationDepth

**Why it matters**: While not directly driving the laser-thermal-mechanical cascade, these affect cleaning quality and process efficiency.

---

## 🔧 Usage Examples

```python
from utils.core.property_categorizer import get_property_categorizer

categorizer = get_property_categorizer()

# Get category by physics stage
category = categorizer.get_category('laserAbsorption')
# Returns: 'laser_interaction'

category = categorizer.get_category('thermalConductivity')
# Returns: 'thermal_response'

category = categorizer.get_category('hardness')
# Returns: 'mechanical_response'

category = categorizer.get_category('density')
# Returns: 'material_characteristics'

# Get all categories (physics-based)
categories = categorizer.get_all_categories()
# Returns: ['laser_interaction', 'thermal_response', 'mechanical_response', 'material_characteristics']
```

---

## 📊 Statistics

- **Total Properties**: 55 unique
- **Total Materials**: 122 with complete property data
- **Categories**: 4 physics-based groupings
- **Physics Flow**: Energy Absorption → Dissipation → Material Response → Supporting Properties

---

## 🚀 Quick Start

```python
from utils.core.property_categorizer import get_property_categorizer

categorizer = get_property_categorizer()

# Understand the physics flow
for cat in categorizer.get_all_categories():
    info = categorizer.get_category_info(cat)
    print(f"{info['physics_stage']}: {info['label']}")

# Output:
# Energy Absorption: Laser Interaction Properties
# Energy Dissipation: Thermal Response Properties
# Material Response: Mechanical Response Properties
# Supporting Properties: Material Characteristics
```

---

**Status**: ✅ Implemented (Physics-Based Structure v3.0.0)  
**Version**: 3.0.0 (Categories.yaml v3.0.0)  
**GROK Compliance**: ✅ Full compliance  
**Code Impact**: Zero - taxonomy-driven via Categories.yaml  
**Physics-Based**: 4 categories following laser cleaning process (Oct 14, 2025)
