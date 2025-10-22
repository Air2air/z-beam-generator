# Frontmatter Structure Reference

**Version**: 5.0.0  
**Date**: October 15, 2025  
**Status**: Production Standard

---

## materialProperties (2 Categories)

### Category 1: laser_material_interaction
**Count**: 26 properties  
**Percentage**: 47.3%

1. laserAbsorption
2. laserReflectivity
3. reflectivity
4. ablationThreshold
5. absorptivity
6. emissivity
7. refractiveIndex
8. laserDamageThreshold
9. opticalTransmittance
10. thermalConductivity
11. specificHeat
12. thermalDiffusivity
13. thermalExpansion
14. thermalDestruction
15. boilingPoint
16. heatCapacity
17. glasTransitionTemperature
18. sinteringTemperature
19. ignitionTemperature
20. autoignitionTemperature
21. decompositionTemperature
22. sublimationPoint
23. thermalStability
24. absorptionCoefficient
25. thermalDegradationPoint
26. photonPenetrationDepth

### Category 2: material_characteristics
**Count**: 29 properties  
**Percentage**: 52.7%

**Physical Properties (15)**:
1. density
2. viscosity
3. porosity
4. surfaceRoughness
5. permeability
6. surfaceEnergy
7. wettability
8. crystallineStructure
9. grainSize
10. moistureContent
11. waterSolubility
12. celluloseContent
13. ligninContent
14. degradationPoint
15. softeningPoint
16. surfaceTension

**Mechanical Properties (10)**:
17. hardness
18. tensileStrength
19. youngsModulus
20. yieldStrength
21. elasticity
22. bulkModulus
23. shearModulus
24. compressiveStrength
25. flexuralStrength
26. fractureResistance

**Electrical Properties (4)**:
27. electricalResistivity
28. electricalConductivity
29. dielectricConstant
30. dielectricStrength

**Chemical Properties (4)**:
31. chemicalStability
32. oxidationResistance
33. corrosionResistance
34. weatherResistance

**Other (1)**:
35. magneticPermeability

---

## machineSettings (9 Parameters)

**EXACTLY 9 keys** - no more, no less:

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

## Property Structure

Each property should have:
```yaml
propertyName:
  value: <number or string>
  unit: <string>
  confidence: <integer 0-100>
  description: <string>
  min: <number or null>
  max: <number or null>
  source: <string> (optional)
  notes: <string> (optional)
  metadata: <dict> (optional)
```

---

## Category Structure

```yaml
materialProperties:
  laser_material_interaction:
    label: Laser-Material Interaction
    description: Optical and thermal properties governing laser energy absorption, reflection, propagation, and ablation thresholds
    percentage: 47.3
    properties:
      <26 properties>
  
  material_characteristics:
    label: Material Characteristics
    description: Intrinsic physical, mechanical, chemical, and structural properties affecting cleaning outcomes and material integrity
    percentage: 52.7
    properties:
      <29 properties>
```

---

## ❌ INVALID Keys (DO NOT USE)

### In machineSettings:
- ❌ fluenceThreshold (REMOVED)
- ❌ energyDensity (REMOVED)
- ❌ dwellTime (REMOVED)
- ❌ Any other keys not in the 9-parameter list

### In materialProperties:
- ❌ vaporizationTemperature (use boilingPoint or sublimationPoint)
- ❌ meltingPoint (use thermalDegradationPoint)
- ❌ energy_coupling (OLD - renamed to laser_material_interaction)
- ❌ structural_response (OLD - merged into material_characteristics)
- ❌ material_properties (OLD - merged into material_characteristics)

---

## NULL Ranges

Some properties may have `null` for min/max if they don't have category-wide ranges in Categories.yaml. This is **acceptable and by design**.

**Common properties with null ranges**:
- crystallineStructure
- chemicalStability
- oxidationResistance
- surfaceEnergy
- waterSolubility
- grainSize

---

## Validation Checklist

✅ **materialProperties** has exactly 2 top-level keys  
✅ **machineSettings** has exactly 9 top-level keys  
✅ No excess or invalid keys present  
✅ All properties have value, unit, confidence, description  
✅ Properties may have null min/max (acceptable)  
✅ Structure matches production standard

---

**Reference**: See `docs/TWO_CATEGORY_SYSTEM.md` for complete documentation
