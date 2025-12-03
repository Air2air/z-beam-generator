# Settings Thermal Data Specification for Interactive Components

**Version**: 1.2  
**Date**: December 2, 2025  
**Status**: ✅ IMPLEMENTED & DEPLOYED  
**Purpose**: Enable accurate, material-specific behavior in settings page interactive components

---

## Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| `thermalProperties` extraction | ✅ Complete | Auto-normalizes units to mm²/s |
| `laserMaterialInteraction` extraction | ✅ Complete | Calculates optimalFluenceRange |
| Category defaults fallback | ✅ Complete | 16 category/subcategory combos |
| Unit normalization | ✅ Complete | Handles m²/s, m^2/s, ×10^{-5} m²/s, mm²/s |
| **Tests** | ✅ 17/17 passing | `tests/export/test_thermal_properties_export.py` |
| **Deployment** | ✅ Complete | 153/153 materials exported |

**Implementation File**: `export/core/trivial_exporter.py`
- `_normalize_thermal_diffusivity()` - Unit conversion
- `_extract_thermal_properties()` - Extract thermalProperties block  
- `_extract_laser_interaction()` - Extract laserMaterialInteraction block
- `_get_thermal_defaults()` - Category fallback defaults
- `THERMAL_CATEGORY_DEFAULTS` - 16 category/subcategory defaults

**To regenerate all settings files with thermal data:**
```bash
PYTHONPATH="$PWD" python3 tools/run.py --deploy
```

---

## Overview

The z-beam website has 4 interactive components on settings pages that currently use **hardcoded defaults** because the settings YAML files lack thermal and laser interaction data. This specification defines the exact data structures needed and how to source/calculate them.

### Components Affected

| Component | Current Default | Impact of Missing Data |
|-----------|-----------------|----------------------|
| ThermalAccumulation | `thermalDiffusivity = 97 mm²/s` (aluminum) | Wood shows cooling at 800x faster than reality |
| MaterialSafetyHeatmap | `laserDamageThreshold = 5.0 J/cm²` | Textiles show same danger zones as steel |
| ProcessEffectivenessHeatmap | Generic thresholds | Can't show optimal cleaning zones |
| DiagnosticCenter | Metal-focused advice | Wood/plastic get inappropriate guidance |

---

## Data Specification

### 1. `thermalProperties` Block (CRITICAL)

Add to each `*-settings.yaml` file:

```yaml
thermalProperties:
  thermalDiffusivity:
    value: 97.0           # REQUIRED - mm²/s
    unit: mm²/s
    source: calculated    # or "literature", "measured"
    
  thermalConductivity:
    value: 237.0          # REQUIRED - W/(m·K)
    unit: W/(m·K)
    
  specificHeat:
    value: 897            # OPTIONAL - J/(kg·K)
    unit: J/(kg·K)
    
  thermalDestructionPoint:
    value: 933            # REQUIRED - K (melting point for metals, char point for organics)
    unit: K
    type: melting         # Options: melting, charring, decomposition, softening
    
  density:
    value: 2700           # OPTIONAL - kg/m³ (for heat capacity calculations)
    unit: kg/m³
```

#### Source Data Location
- **Materials.yaml** contains thermal and laser properties under:
  - `materials.[name].materialProperties.laser_material_interaction.thermalDiffusivity`
  - `materials.[name].materialProperties.laser_material_interaction.thermalConductivity`
  - `materials.[name].materialProperties.laser_material_interaction.specificHeat`
  - `materials.[name].materialProperties.laser_material_interaction.ablationThreshold`
  - `materials.[name].materialProperties.laser_material_interaction.laserDamageThreshold`
  - `materials.[name].materialProperties.laser_material_interaction.thermalDestructionPoint`
- Values have varied units - MUST normalize during export

#### Unit Conversion & Normalization

The Materials.yaml data uses inconsistent unit formats. The exporter MUST normalize:

```python
def normalize_thermal_diffusivity(value, unit):
    """
    Normalize thermalDiffusivity to mm²/s for frontend.
    
    Input formats from Materials.yaml:
    - value=9.7, unit='×10^{-5} m²/s' → 97.0 mm²/s
    - value=1.25e-07, unit='m²/s' → 0.125 mm²/s  
    - value=6.2e-07, unit='m^2/s' → 0.62 mm²/s
    - value=0.12, unit='mm²/s' → 0.12 mm²/s (already correct)
    """
    if value is None:
        return None
        
    # Handle multiplier format: ×10^{-5} m²/s
    if '×10^{-5}' in unit:
        # value is in 10^-5 m²/s, convert to mm²/s
        # 1 m²/s = 1,000,000 mm²/s
        # 10^-5 m²/s = 10 mm²/s
        return value * 10
        
    # Handle standard m²/s or m^2/s
    if 'm²/s' in unit or 'm^2/s' in unit:
        # Scientific notation: 1.25e-07 m²/s = 0.125 mm²/s
        return value * 1_000_000
        
    # Already in mm²/s
    if 'mm²/s' in unit or 'mm^2/s' in unit:
        return value
        
    # Unknown format - return as-is with warning
    logger.warning(f"Unknown thermal diffusivity unit: {unit}")
    return value
```

**Coverage Status**: 153/153 materials (100%) have `thermalDiffusivity` data

#### Category Defaults (if per-material data missing)

Use these fallbacks based on category/subcategory:

```yaml
# metal/precious
thermalDiffusivity: 150.0  # mm²/s (silver=175, gold=127)
thermalConductivity: 350.0  # W/(m·K)
thermalDestructionPoint: 1337  # K (gold melting)

# metal/non-ferrous  
thermalDiffusivity: 70.0   # mm²/s (aluminum=97, copper=111, brass=34)
thermalConductivity: 200.0  # W/(m·K)
thermalDestructionPoint: 1000  # K (varies widely)

# metal/ferrous
thermalDiffusivity: 8.0    # mm²/s (steel=4-12)
thermalConductivity: 50.0   # W/(m·K)
thermalDestructionPoint: 1800  # K

# wood/hardwood
thermalDiffusivity: 0.12   # mm²/s (800x slower than aluminum!)
thermalConductivity: 0.17   # W/(m·K)
thermalDestructionPoint: 523  # K (250°C char point)
type: charring

# wood/softwood
thermalDiffusivity: 0.10   # mm²/s
thermalConductivity: 0.12   # W/(m·K)
thermalDestructionPoint: 513  # K (240°C char point)
type: charring

# plastic/thermoplastic
thermalDiffusivity: 0.12   # mm²/s
thermalConductivity: 0.20   # W/(m·K)
thermalDestructionPoint: 473  # K (200°C softening)
type: softening

# plastic/thermoset
thermalDiffusivity: 0.15   # mm²/s
thermalConductivity: 0.30   # W/(m·K)
thermalDestructionPoint: 573  # K (300°C decomposition)
type: decomposition

# composite/carbon-fiber
thermalDiffusivity: 15.0   # mm²/s (anisotropic, varies)
thermalConductivity: 50.0   # W/(m·K)
thermalDestructionPoint: 673  # K (matrix decomposition)
type: decomposition

# composite/fiberglass
thermalDiffusivity: 0.22   # mm²/s
thermalConductivity: 0.40   # W/(m·K)
thermalDestructionPoint: 573  # K
type: decomposition

# stone/natural
thermalDiffusivity: 1.2    # mm²/s
thermalConductivity: 2.5    # W/(m·K)
thermalDestructionPoint: 1400  # K (varies by type)

# stone/engineered
thermalDiffusivity: 0.8    # mm²/s
thermalConductivity: 1.5    # W/(m·K)
thermalDestructionPoint: 1000  # K

# ceramic/traditional
thermalDiffusivity: 1.0    # mm²/s
thermalConductivity: 2.0    # W/(m·K)
thermalDestructionPoint: 1500  # K

# ceramic/advanced
thermalDiffusivity: 12.0   # mm²/s (SiC, Al2O3)
thermalConductivity: 70.0   # W/(m·K)
thermalDestructionPoint: 2700  # K

# glass/standard
thermalDiffusivity: 0.5    # mm²/s
thermalConductivity: 1.0    # W/(m·K)
thermalDestructionPoint: 1000  # K (softening)
type: softening

# glass/specialty
thermalDiffusivity: 5.0    # mm²/s (sapphire)
thermalConductivity: 20.0   # W/(m·K)
thermalDestructionPoint: 2100  # K

# rubber
thermalDiffusivity: 0.12   # mm²/s
thermalConductivity: 0.16   # W/(m·K)
thermalDestructionPoint: 523  # K (250°C decomposition)
type: decomposition

# textile/natural
thermalDiffusivity: 0.07   # mm²/s
thermalConductivity: 0.07   # W/(m·K)
thermalDestructionPoint: 503  # K (230°C - cotton chars easily!)
type: charring

# textile/synthetic
thermalDiffusivity: 0.10   # mm²/s
thermalConductivity: 0.15   # W/(m·K)
thermalDestructionPoint: 523  # K
type: melting
```

---

### 2. `laserMaterialInteraction` Block (HIGH PRIORITY)

Add to each `*-settings.yaml` file:

```yaml
laserMaterialInteraction:
  laserDamageThreshold:
    value: 5.0            # REQUIRED - J/cm² (substrate damage begins)
    unit: J/cm²
    wavelength: 1064      # nm (threshold varies by wavelength)
    pulseWidth: 10        # ns (threshold varies by pulse duration)
    
  ablationThreshold:
    value: 1.5            # REQUIRED - J/cm² (minimum for cleaning)
    unit: J/cm²
    
  optimalFluenceRange:
    min: 2.0              # OPTIONAL - J/cm² (effective cleaning starts)
    max: 4.0              # OPTIONAL - J/cm² (before damage risk)
    unit: J/cm²
    
  thermalShockResistance:
    value: 200            # OPTIONAL - K (max temperature differential)
    unit: K
    
  reflectivity:
    value: 0.85           # OPTIONAL - dimensionless (0-1)
    wavelength: 1064      # nm
    surfaceCondition: polished  # Options: polished, oxidized, rough
```

#### Category Defaults

```yaml
# metal/precious
laserDamageThreshold: 12.0   # J/cm² (high threshold)
ablationThreshold: 3.0        # J/cm²
optimalFluenceRange: [4.0, 10.0]
reflectivity: 0.95           # Very high

# metal/non-ferrous
laserDamageThreshold: 8.0    # J/cm²
ablationThreshold: 2.0        # J/cm²
optimalFluenceRange: [3.0, 6.0]
reflectivity: 0.90           # High (aluminum)

# metal/ferrous
laserDamageThreshold: 12.0   # J/cm² (robust)
ablationThreshold: 4.0        # J/cm²
optimalFluenceRange: [5.0, 10.0]
reflectivity: 0.70           # Lower (oxidized)

# wood/hardwood
laserDamageThreshold: 3.5    # J/cm² (chars easily!)
ablationThreshold: 1.0        # J/cm²
optimalFluenceRange: [1.5, 3.0]
reflectivity: 0.08           # Very low

# wood/softwood
laserDamageThreshold: 2.5    # J/cm² (more delicate)
ablationThreshold: 0.8        # J/cm²
optimalFluenceRange: [1.0, 2.0]
reflectivity: 0.06           # Very low

# plastic/thermoplastic
laserDamageThreshold: 2.0    # J/cm² (melts easily)
ablationThreshold: 0.8        # J/cm²
optimalFluenceRange: [1.0, 1.8]
reflectivity: 0.10

# plastic/thermoset
laserDamageThreshold: 4.0    # J/cm² (more robust)
ablationThreshold: 1.5        # J/cm²
optimalFluenceRange: [2.0, 3.5]
reflectivity: 0.12

# composite/carbon-fiber
laserDamageThreshold: 5.0    # J/cm²
ablationThreshold: 2.0        # J/cm²
optimalFluenceRange: [2.5, 4.5]
reflectivity: 0.30           # Carbon absorbs well

# composite/fiberglass
laserDamageThreshold: 3.5    # J/cm²
ablationThreshold: 1.5        # J/cm²
optimalFluenceRange: [2.0, 3.0]
reflectivity: 0.50           # Glass reflects IR

# stone/natural
laserDamageThreshold: 15.0   # J/cm² (robust)
ablationThreshold: 5.0        # J/cm²
optimalFluenceRange: [6.0, 12.0]
reflectivity: 0.20

# stone/engineered
laserDamageThreshold: 12.0   # J/cm²
ablationThreshold: 4.0        # J/cm²
optimalFluenceRange: [5.0, 10.0]
reflectivity: 0.25

# ceramic/traditional
laserDamageThreshold: 20.0   # J/cm² (very robust)
ablationThreshold: 6.0        # J/cm²
optimalFluenceRange: [8.0, 18.0]
reflectivity: 0.30

# ceramic/advanced
laserDamageThreshold: 35.0   # J/cm² (extremely robust)
ablationThreshold: 12.0       # J/cm²
optimalFluenceRange: [15.0, 30.0]
reflectivity: 0.40

# glass/standard
laserDamageThreshold: 8.0    # J/cm² (thermal shock risk)
ablationThreshold: 3.0        # J/cm²
optimalFluenceRange: [4.0, 7.0]
reflectivity: 0.04           # Transparent at 1064nm
thermalShockResistance: 80   # K (very sensitive!)

# glass/specialty
laserDamageThreshold: 40.0   # J/cm² (sapphire very robust)
ablationThreshold: 15.0       # J/cm²
optimalFluenceRange: [18.0, 35.0]
reflectivity: 0.08
thermalShockResistance: 1000  # K (quartz excellent)

# rubber
laserDamageThreshold: 2.5    # J/cm² (burns easily)
ablationThreshold: 1.0        # J/cm²
optimalFluenceRange: [1.2, 2.2]
reflectivity: 0.05

# textile/natural
laserDamageThreshold: 2.0    # J/cm² (burns very easily!)
ablationThreshold: 0.5        # J/cm²
optimalFluenceRange: [0.6, 1.5]
reflectivity: 0.15

# textile/synthetic
laserDamageThreshold: 3.0    # J/cm²
ablationThreshold: 1.0        # J/cm²
optimalFluenceRange: [1.2, 2.5]
reflectivity: 0.12
```

---

### 3. Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GENERATOR DATA SOURCES                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Materials.yaml                    PropertyDefinitions.yaml          │
│  ├─ thermalDiffusivity (m²/s)     ├─ ablationThreshold ranges       │
│  ├─ thermalConductivity            ├─ category typical values        │
│  ├─ specificHeat                   └─ laser cleaning impact          │
│  └─ laserAbsorption                                                  │
│                                                                      │
│  Categories.yaml                   ParameterDefinitions.yaml         │
│  ├─ category hierarchy             ├─ parameter ranges               │
│  └─ subcategory mappings           └─ formulas (thermal_accumulation)│
│                                                                      │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     GENERATOR PROCESSING                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. Load material from Materials.yaml                                │
│  2. Convert units:                                                   │
│     - thermalDiffusivity: m²/s → mm²/s (× 1,000,000)                │
│  3. Look up category defaults for missing values                     │
│  4. Calculate derived values:                                        │
│     - optimalFluenceRange from ablation/damage thresholds           │
│  5. Validate all required fields present                             │
│                                                                      │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    OUTPUT: *-settings.yaml                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  name: Aluminum                                                      │
│  slug: aluminum                                                      │
│  category: metal                                                     │
│  subcategory: non-ferrous                                           │
│                                                                      │
│  machineSettings:                                                    │
│    powerRange: { value: 100, unit: W, min: 1, max: 120 }            │
│    wavelength: { value: 1064, unit: nm }                            │
│    # ... existing parameters ...                                     │
│                                                                      │
│  thermalProperties:                    # ◄── NEW BLOCK               │
│    thermalDiffusivity:                                               │
│      value: 97.0                                                     │
│      unit: mm²/s                                                     │
│    thermalConductivity:                                              │
│      value: 237.0                                                    │
│      unit: W/(m·K)                                                   │
│    thermalDestructionPoint:                                          │
│      value: 933                                                      │
│      unit: K                                                         │
│      type: melting                                                   │
│                                                                      │
│  laserMaterialInteraction:             # ◄── NEW BLOCK               │
│    laserDamageThreshold:                                             │
│      value: 8.0                                                      │
│      unit: J/cm²                                                     │
│    ablationThreshold:                                                │
│      value: 2.0                                                      │
│      unit: J/cm²                                                     │
│    optimalFluenceRange:                                              │
│      min: 3.0                                                        │
│      max: 6.0                                                        │
│      unit: J/cm²                                                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 4. Implementation Steps

#### Phase 1: Thermal Properties (Week 1)
**Impact**: ThermalAccumulation component shows accurate cooling curves

1. **Add unit conversion to settings exporter**
   ```python
   def convert_thermal_diffusivity(value_m2_s):
       """Convert m²/s to mm²/s for frontend component"""
       if value_m2_s is None:
           return None
       return value_m2_s * 1_000_000
   ```

2. **Add category defaults lookup**
   ```python
   THERMAL_DEFAULTS = {
       ('metal', 'non-ferrous'): {
           'thermalDiffusivity': 70.0,
           'thermalConductivity': 200.0,
           'thermalDestructionPoint': 1000,
           'destructionType': 'melting'
       },
       ('wood', 'hardwood'): {
           'thermalDiffusivity': 0.12,
           'thermalConductivity': 0.17,
           'thermalDestructionPoint': 523,
           'destructionType': 'charring'
       },
       # ... etc
   }
   ```

3. **Export thermalProperties block**
   - Read from Materials.yaml
   - Convert units
   - Fall back to category defaults if missing
   - Add to settings YAML output

#### Phase 2: Laser Interaction Data (Week 2)
**Impact**: Safety & Effectiveness heatmaps show accurate zones

1. **Add laserMaterialInteraction block**
   - Source from PropertyDefinitions.yaml where available
   - Use category defaults otherwise

2. **Calculate optimalFluenceRange**
   ```python
   def calculate_optimal_range(ablation_threshold, damage_threshold):
       """Calculate optimal fluence range for cleaning"""
       # Optimal starts 20% above ablation threshold
       min_optimal = ablation_threshold * 1.2
       # Optimal ends 20% below damage threshold  
       max_optimal = damage_threshold * 0.8
       return {'min': min_optimal, 'max': max_optimal}
   ```

#### Phase 3: Validation & Testing (Week 3)
**Impact**: Ensure all 140+ materials have complete data

1. **Add schema validation**
   ```yaml
   # settings_schema.yaml
   thermalProperties:
     required: true
     properties:
       thermalDiffusivity:
         required: true
         type: number
         min: 0.01   # Textiles
         max: 200    # Silver
       thermalDestructionPoint:
         required: true
         type: number
         min: 400    # Low-temp plastics
         max: 3500   # Tungsten
   ```

2. **Generate coverage report**
   - List materials with per-material data vs category defaults
   - Prioritize research for high-traffic materials

---

### 5. Frontend Component Updates Needed

After generator implements this spec, the z-beam frontend components need minor updates:

#### ThermalAccumulation.tsx
```typescript
// Current (hardcoded default):
thermalDiffusivity = 97, // Aluminum default

// Updated (from settings data):
interface ThermalAccumulationProps {
  thermalProperties?: {
    thermalDiffusivity: { value: number; unit: string };
    thermalDestructionPoint: { value: number; unit: string; type: string };
  };
}

// Use:
const diffusivity = thermalProperties?.thermalDiffusivity?.value ?? 97;
const maxSafeTemp = thermalProperties?.thermalDestructionPoint?.value 
  ? (thermalProperties.thermalDestructionPoint.value - 273) * 0.6  // 60% of char/melt in °C
  : 150;
```

#### MaterialSafetyHeatmap.tsx
```typescript
// Current: Uses prop with fallback
laserDamageThreshold = 5.0

// Updated: Read from laserMaterialInteraction
interface HeatmapProps {
  laserMaterialInteraction?: {
    laserDamageThreshold: { value: number };
    ablationThreshold: { value: number };
  };
}
```

---

### 6. Quick Reference: Thermal Diffusivity by Category

Visual representation of why defaults matter:

```
Category              Thermal Diffusivity (mm²/s)    
─────────────────────────────────────────────────────
Precious metals       ████████████████████ 120-175
Non-ferrous metals    █████████████ 40-100  
Advanced ceramics     ████ 5-20
Ferrous metals        ███ 4-12
Stone                 █ 0.8-2
Glass (standard)      ▌ 0.4-0.6
Composites            ▌ 0.15-0.3
Plastics              ▎ 0.08-0.2
Wood                  ▎ 0.08-0.15
Textiles              ▏ 0.05-0.10

3500x difference between silver (175) and cotton (0.05)!
```

---

### 7. Testing Checklist

Before deploying settings YAML changes:

- [ ] All materials have `thermalProperties.thermalDiffusivity` (value > 0)
- [ ] All materials have `thermalProperties.thermalDestructionPoint`
- [ ] All materials have `laserMaterialInteraction.laserDamageThreshold`
- [ ] All materials have `laserMaterialInteraction.ablationThreshold`
- [ ] Unit conversions verified: `thermalDiffusivity` in mm²/s (not m²/s)
- [ ] Wood materials show char point (~250°C), not melting point
- [ ] Textiles show low damage threshold (<3 J/cm²)
- [ ] Metals show high damage threshold (>5 J/cm²)

---

### 8. Files to Modify in Generator

1. **`processing/exporters/settings_exporter.py`** (or equivalent)
   - Add `_export_thermal_properties()` method
   - Add `_export_laser_interaction()` method
   - Add unit conversion utilities

2. **`data/materials/CategoryDefaults.yaml`** (NEW FILE)
   - Store category-level default thermal properties
   - Store category-level default laser thresholds

3. **`processing/validation/settings_schema.yaml`** (or equivalent)
   - Add schema for new blocks
   - Add range validation

4. **`tests/test_settings_thermal_data.py`** (NEW FILE)
   - Test unit conversions
   - Test category defaults applied correctly
   - Test all materials have required fields

---

## Summary

| Data Block | Purpose | Source Path | Coverage | Priority |
|------------|---------|-------------|----------|----------|
| `thermalProperties.thermalDiffusivity` | ThermalAccumulation cooling rates | `materialProperties.laser_material_interaction.thermalDiffusivity` | 153/153 (100%) | CRITICAL |
| `thermalProperties.thermalDestructionPoint` | Safe temperature limits | `materialProperties.laser_material_interaction.thermalDestructionPoint` | 129/153 (84%) | CRITICAL |
| `laserMaterialInteraction.laserDamageThreshold` | Safety heatmap red zones | `materialProperties.laser_material_interaction.laserDamageThreshold` | 153/153 (100%) | HIGH |
| `laserMaterialInteraction.ablationThreshold` | Effectiveness heatmap | `materialProperties.laser_material_interaction.ablationThreshold` | 153/153 (100%) | HIGH |
| `laserMaterialInteraction.optimalFluenceRange` | Optimal cleaning zones | Calculated from above | Derived | MEDIUM |

**Expected Outcome**: All 4 interactive components on settings pages will show accurate, material-specific behavior instead of generic aluminum/metal defaults.
