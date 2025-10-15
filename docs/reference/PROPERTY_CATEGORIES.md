# Property Categories System

**Version**: 3.0.0  
**Last Updated**: October 14, 2025  
**Architecture**: Physics-Based 4-Category Structure (GROK Compliant)

## 🎯 Overview

The Property Categories system provides a **lightweight, read-only taxonomy** for organizing the 55 material properties across 122 materials into 4 physics-based categories that follow the **laser cleaning process flow**.

**Physics-Driven Organization**: Categories mirror the actual laser cleaning process stages:
1. **Laser Interaction** → Photon coupling (absorption vs. reflection)
2. **Thermal Response** → Heat propagation and phase transitions
3. **Mechanical Response** → Physical reaction to thermal stress
4. **Material Characteristics** → Supporting properties affecting outcomes

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
┌────────────────────────────────────────────┐
│  1. LASER INTERACTION (Photon Coupling)    │
│     - Absorption vs. Reflection            │
│     - Energy enters material               │
└────────────────────────────────────────────┘
    ↓
┌────────────────────────────────────────────┐
│  2. THERMAL RESPONSE (Heat Propagation)    │
│     - Heat distributes through material    │
│     - Phase transitions occur              │
│     - Melting/vaporization                 │
└────────────────────────────────────────────┘
    ↓
┌────────────────────────────────────────────┐
│  3. MECHANICAL RESPONSE (Stress/Strain)    │
│     - Thermal expansion                    │
│     - Material ablation                    │
│     - Contaminant ejection                 │
└────────────────────────────────────────────┘
    ↓
┌────────────────────────────────────────────┐
│  4. MATERIAL CHARACTERISTICS (Outcomes)    │
│     - Surface finish quality               │
│     - Contamination removal efficiency     │
│     - Process optimization factors         │
└────────────────────────────────────────────┘
```

---

## 📊 The 4 Physics-Based Categories

### 1. **Laser Interaction Properties** (16.4% - 9 properties)

**Physics Stage**: Energy Absorption  
**ID**: `laser_interaction`

**What it governs**: First-order photon coupling - how much laser energy actually enters the material vs. reflects away.

**Properties**:
- laserAbsorption, laserReflectivity, reflectivity, ablationThreshold, absorptivity, emissivity, refractiveIndex, laserDamageThreshold, opticalTransmittance

**Why it matters**: If absorption is too low or reflectivity too high, laser energy never enters the material and cleaning fails at step 1.

---

### 2. **Thermal Response Properties** (25.5% - 14 properties)

**Physics Stage**: Energy Dissipation  
**ID**: `thermal_response`

**What it governs**: How absorbed laser energy distributes through material and when critical phase transitions occur.

**Properties**:
- thermalConductivity, specificHeat, thermalDiffusivity, thermalExpansion, thermalDestruction, boilingPoint, heatCapacity, glasTransitionTemperature, sinteringTemperature, ignitionTemperature, autoignitionTemperature, decompositionTemperature, sublimationPoint, thermalStability

**Why it matters**: Determines how fast heat spreads (substrate damage risk) and when material ablates (cleaning effectiveness).

---

### 3. **Mechanical Response Properties** (18.2% - 10 properties)

**Physics Stage**: Material Response  
**ID**: `mechanical_response`

**What it governs**: How material physically reacts to rapid thermal stress.

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
