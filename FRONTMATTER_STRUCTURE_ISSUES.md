# Frontmatter Structure Issues - Two-Category System

**Date**: October 15, 2025  
**Status**: ⚠️ Needs Cleanup

---

## Summary

After the 2-category consolidation, frontmatter files have structural inconsistencies that need to be addressed:

1. **Excess machineSettings keys** (should be 9, some have 10-12)
2. **Properties with null min/max ranges** (should have category ranges)
3. **Unexpected properties** not in the defined 55-property list

---

## ✅ Correct Structure

### materialProperties (2 categories)

#### laser_material_interaction (26 properties)
- laserAbsorption
- laserReflectivity
- reflectivity
- ablationThreshold
- absorptivity
- emissivity
- refractiveIndex
- laserDamageThreshold
- opticalTransmittance
- thermalConductivity
- specificHeat
- thermalDiffusivity
- thermalExpansion
- thermalDestruction
- boilingPoint
- heatCapacity
- glasTransitionTemperature
- sinteringTemperature
- ignitionTemperature
- autoignitionTemperature
- decompositionTemperature
- sublimationPoint
- thermalStability
- absorptionCoefficient
- thermalDegradationPoint
- photonPenetrationDepth

#### material_characteristics (29 properties)
- density
- viscosity
- porosity
- surfaceRoughness
- permeability
- surfaceEnergy
- wettability
- electricalResistivity
- electricalConductivity
- dielectricConstant
- dielectricStrength
- chemicalStability
- oxidationResistance
- corrosionResistance
- moistureContent
- waterSolubility
- weatherResistance
- crystallineStructure
- celluloseContent
- grainSize
- magneticPermeability
- ligninContent
- degradationPoint
- softeningPoint
- surfaceTension
- hardness
- tensileStrength
- youngsModulus
- yieldStrength
- elasticity
- bulkModulus
- shearModulus
- compressiveStrength
- flexuralStrength
- fractureResistance

### machineSettings (9 parameters)
1. powerRange
2. wavelength
3. spotSize
4. repetitionRate
5. pulseWidth
6. scanSpeed
7. fluence
8. overlapRatio
9. passCount

---

## ❌ Issues Found

### Issue 1: Excess machineSettings Keys

**Found in ~13-20 files**:
- ❌ `fluenceThreshold` (13 files) - Should be removed
- ❌ `energyDensity` (7 files) - Should be removed
- ❌ `dwellTime` (1 file) - Should be removed

**Action**: Remove these keys, keep only the 9 standard parameters.

---

### Issue 2: Properties with NULL min/max Ranges

**Found across multiple files**:
- ❌ `crystallineStructure` - 7+ files with null ranges
- ❌ `chemicalStability` - 2+ files with null ranges
- ❌ `oxidationResistance` - 1+ files with null ranges
- ❌ `waterSolubility` - 1+ files with null ranges
- ❌ `surfaceEnergy` - 1+ files with null ranges
- ❌ `surfaceTension` - 1+ files with null ranges

**Why This Happens**:
- These properties don't have category ranges defined in Categories.yaml
- Generator correctly sets min/max to `null` when no category range exists
- This is actually **correct behavior per design** (see DATA_ARCHITECTURE.md)

**Action**: 
- Option A: Add category ranges for these properties in Categories.yaml
- Option B: Accept null ranges as valid (current design allows this)
- **Recommended**: Option B - null ranges are valid for properties without category context

---

### Issue 3: Unexpected Properties

**Properties found that aren't in the 55-property list**:
- ❌ `vaporizationTemperature` - Found in some files, not in official list

**Action**: Remove or map to correct property name (possibly `boilingPoint` or `sublimationPoint`)

---

## 🔧 Cleanup Actions Required

### Priority 1: Remove Excess machineSettings Keys ✅
```python
# Remove from all files:
- fluenceThreshold
- energyDensity  
- dwellTime
```

### Priority 2: Handle Unexpected Properties ✅
```python
# Check and remove/map:
- vaporizationTemperature → needs mapping or removal
```

### Priority 3: Verify NULL Ranges (Low Priority)
```python
# Properties with null ranges are OK per design
# Only act if category ranges should exist but are missing
```

---

## 📋 Verification Checklist

After cleanup, verify:
- [ ] All files have exactly 2 materialProperties categories
- [ ] All files have exactly 9 machineSettings keys
- [ ] No unexpected properties exist
- [ ] NULL ranges only appear for non-core properties (acceptable)
- [ ] All 122 files pass structure validation

---

## 🛠️ Recommended Fix Script

Create `scripts/tools/cleanup_frontmatter_structure.py`:

```python
#!/usr/bin/env python3
"""
Clean up frontmatter structure after 2-category consolidation.

Actions:
1. Remove excess machineSettings keys (fluenceThreshold, energyDensity, dwellTime)
2. Remove unexpected properties (vaporizationTemperature, etc.)
3. Verify 2-category structure
4. Report null range properties (informational only)
"""

import yaml
from pathlib import Path

VALID_MACHINE_KEYS = {
    'powerRange', 'wavelength', 'spotSize', 'repetitionRate',
    'pulseWidth', 'scanSpeed', 'fluence', 'overlapRatio', 'passCount'
}

VALID_MATERIAL_CATEGORIES = {
    'laser_material_interaction', 'material_characteristics'
}

UNEXPECTED_PROPERTIES = {
    'vaporizationTemperature', # Map to boilingPoint or remove
}

def cleanup_file(file_path):
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    
    changes = []
    
    # Clean machineSettings
    if 'machineSettings' in data:
        excess_keys = set(data['machineSettings'].keys()) - VALID_MACHINE_KEYS
        for key in excess_keys:
            del data['machineSettings'][key]
            changes.append(f"Removed machineSettings.{key}")
    
    # Clean materialProperties
    if 'materialProperties' in data:
        for cat_name, cat_data in data['materialProperties'].items():
            if 'properties' in cat_data:
                for prop in UNEXPECTED_PROPERTIES:
                    if prop in cat_data['properties']:
                        del cat_data['properties'][prop]
                        changes.append(f"Removed {cat_name}.{prop}")
    
    if changes:
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    return changes

# Run on all files...
```

---

## 📊 Current State

**Analyzed**: 20 sample files  
**Total Files**: 122

**Issues Found**:
- ✅ 2-category structure: 100% correct
- ⚠️ machineSettings keys: 13+ files have excess keys
- ⚠️ NULL ranges: 6 properties affected (acceptable by design)
- ⚠️ Unexpected properties: Need full scan to quantify

---

## 🎯 Expected Final State

### materialProperties
```yaml
materialProperties:
  laser_material_interaction:
    label: Laser-Material Interaction
    percentage: 47.3
    properties:
      # 26 properties max, each with value/unit/confidence/description/min/max
  material_characteristics:
    label: Material Characteristics
    percentage: 52.7
    properties:
      # 29 properties max, each with value/unit/confidence/description/min/max
      # Some may have null min/max if no category range exists
```

### machineSettings
```yaml
machineSettings:
  powerRange: {...}
  wavelength: {...}
  spotSize: {...}
  repetitionRate: {...}
  pulseWidth: {...}
  scanSpeed: {...}
  fluence: {...}
  overlapRatio: {...}
  passCount: {...}
  # EXACTLY 9 keys, no more, no less
```

---

## 🚀 Next Steps

1. **Create cleanup script** - `scripts/tools/cleanup_frontmatter_structure.py`
2. **Run dry-run** - Test on sample files
3. **Execute cleanup** - Process all 122 files
4. **Verify structure** - Run validation tests
5. **Deploy** - Push clean files to production

---

**Status**: Ready for cleanup script creation  
**Priority**: Medium (functionality works, but structure should be clean)  
**Impact**: Cosmetic + test compliance
