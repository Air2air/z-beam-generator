# Compound ID Mapping Guide

**Purpose**: Map byproduct compound names in Contaminants.yaml to compound IDs in Compounds.yaml

## Recommended Mappings

| Contaminants Byproduct | Compounds.yaml ID | Status |
|------------------------|-------------------|--------|
| `Al vapor` | `TBD` | ⚠️ Needs review |
| `Al2O3 nanoparticles` | `aluminum-oxide` | ✅ Ready to update |
| `Aluminum vapor` | `TBD` | ⚠️ Needs review |
| `Al₂O₃ nanoparticles` | `aluminum-oxide` | ✅ Ready to update |
| `CO` | `carbon-monoxide` | ✅ Ready to update |
| `CO/CO2` | `carbon-monoxide` | ✅ Ready to update |
| `CO2` | `carbon-dioxide` | ✅ Ready to update |
| `CO₂` | `carbon-dioxide` | ✅ Ready to update |
| `Fe2O3/Fe3O4 nanoparticles` | `iron-oxide` | ✅ Ready to update |
| `H2O` | `N/A` | ℹ️ Non-hazardous (no entry needed) |
| `H₂O` | `TBD` | ⚠️ Needs review |
| `NO_x` | `nitrogen-oxides` | ✅ Ready to update |
| `NO₂` | `nitrogen-oxides` | ✅ Ready to update |
| `O2` | `N/A` | ℹ️ Non-hazardous (no entry needed) |
| `O₂` | `TBD` | ⚠️ Needs review |
| `VOC` | `vocs` | ✅ Ready to update |
| `carbon_ash` | `TBD` | ⚠️ Needs review |
| `carbon_particulates` | `TBD` | ⚠️ Needs review |
| `metal vapor plasma` | `TBD` | ⚠️ Needs review |
| `volatile_organic_compounds` | `vocs` | ✅ Ready to update |

## Usage

Update contaminants byproducts from:
```yaml
byproducts:
  - compound: CO2  # OLD
    hazard_level: low
```

To:
```yaml
byproducts:
  - compound: carbon-dioxide  # UPDATED - matches Compounds.yaml ID
    hazard_level: low
```
