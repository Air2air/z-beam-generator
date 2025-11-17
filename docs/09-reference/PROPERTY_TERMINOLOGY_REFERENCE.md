# Property Terminology Reference

**Date**: October 22, 2025  
**Purpose**: Define system-specific property terminology and research guidance  
**Audience**: AI research systems, developers, and content generators

---

## 🎯 Executive Summary

The Z-Beam Generator uses **standardized property terminology** that may differ from common scientific literature. This document provides the mapping between our system terms and standard research terms to ensure accurate AI research and data consistency.

---

## 🔄 Property Terminology Mappings

### Thermal Properties

#### `thermalDestruction` ↔ `meltingPoint`
- **System Term**: `thermalDestruction`
- **Research Term**: `meltingPoint` or "melting point"
- **Definition**: Temperature at which a material transitions from solid to liquid state
- **Units**: °C (Celsius)
- **AI Research Guidance**: 
  - Search literature for "melting point" data
  - Include related terms: "fusion point", "liquidus temperature"
  - Store results under `thermalDestruction` property name

#### `thermalDestructionPoint` ↔ `meltingPoint`
- **System Term**: `thermalDestructionPoint` 
- **Research Term**: `meltingPoint` or "melting point"
- **Legacy**: Newer standardized form of `thermalDestruction`
- **Migration**: System automatically migrates `meltingPoint` → `thermalDestructionPoint`

#### `thermalDestructionType`
- **System Term**: `thermalDestructionType`
- **Research Term**: "primary thermal failure mechanism"
- **Values**: melting, decomposition, carbonization, oxidation, sublimation, thermal_shock, softening, spalling, calcination, delamination, pyrolysis, sintering, degradation
- **AI Research Guidance**: Determine the dominant mechanism when material reaches thermal limits

### Material-Specific Thermal Terms

#### Wood Materials: `thermalDestructionPoint`
- **Research Term**: "charring temperature", "pyrolysis temperature", "ignition point"
- **Typical Values**: 200-300°C
- **Note**: Wood doesn't melt; it decomposes/carbonizes

#### Ceramic Materials: `sinteringPoint`
- **Research Term**: "sintering temperature", "densification temperature"
- **Definition**: Temperature where particle fusion occurs
- **Typical Values**: 1000-1800°C

#### Glass Materials: `softeningPoint`
- **Research Term**: "glass transition temperature", "softening point", "Tg"
- **Definition**: Temperature where glass transitions from rigid to pliable
- **Typical Values**: 400-600°C

#### Plastic/Composite Materials: `degradationPoint`
- **Research Term**: "thermal decomposition temperature", "degradation temperature"
- **Definition**: Temperature where polymer breakdown begins
- **Typical Values**: 200-400°C

#### Stone/Masonry Materials: `thermalDegradationPoint`
- **Research Term**: "thermal shock temperature", "spalling temperature"
- **Definition**: Temperature where structural breakdown begins
- **Typical Values**: 500-800°C

---

## 🔬 AI Research Guidelines

### General Research Strategy

1. **Use Standard Terms**: Search literature using common scientific terminology
2. **Store System Terms**: Save data using our standardized property names
3. **Include Confidence**: Always provide confidence levels (0-100%)
4. **Reference Sources**: Include DOI or publication reference when possible

### Research Query Examples

#### For thermalDestruction Research:
```
"aluminum melting point" OR "aluminum fusion temperature"
"steel melting point" OR "steel liquidus temperature"
"copper melting point" OR "copper thermal properties"
```

#### For thermalDestructionType Research:
```
"aluminum thermal failure mechanism"
"wood thermal decomposition mechanism"
"glass thermal transition behavior"
```

### Expected Data Format

```yaml
thermalDestruction:
  value: 660.3
  unit: "°C"
  confidence: 95
  description: "Melting point of pure aluminum"
  source: "ASM Handbook"
  research_date: "2025-10-22T10:30:00Z"
```

---

## 📊 Property Coverage by Category

### Metal Materials
- **thermalDestruction**: ✅ Use melting point data
- **thermalDestructionType**: ✅ Usually "melting"

### Wood Materials  
- **thermalDestruction**: ✅ Use charring/pyrolysis temperature
- **thermalDestructionType**: ✅ Usually "carbonization" or "pyrolysis"

### Ceramic Materials
- **thermalDestruction**: ✅ Use sintering temperature  
- **thermalDestructionType**: ✅ Usually "sintering"

### Glass Materials
- **thermalDestruction**: ✅ Use glass transition temperature
- **thermalDestructionType**: ✅ Usually "softening"

### Plastic/Composite Materials
- **thermalDestruction**: ✅ Use decomposition temperature
- **thermalDestructionType**: ✅ Usually "degradation" or "delamination"

---

## 🚨 Common Research Pitfalls

### ❌ Avoid These Mistakes

1. **Wrong Temperature Scale**: Always convert to Celsius
2. **Impure Material Data**: Use pure material properties, not alloys (unless specified)
3. **Pressure Dependencies**: Use standard atmospheric pressure values
4. **Conflicting Sources**: Choose peer-reviewed sources over general websites

### ✅ Best Practices

1. **Cross-Reference**: Verify values across multiple authoritative sources
2. **Material Purity**: Specify material purity level (e.g., 99.9% pure aluminum)
3. **Standard Conditions**: Use STP (Standard Temperature and Pressure) values
4. **Confidence Scoring**: Lower confidence for conflicting or limited sources

---

## 🔄 Legacy Property Migration

### Automatic Migration Rules

The system automatically handles these migrations:

```yaml
# Old → New
meltingPoint → thermalDestructionPoint
boilingPoint → vaporPressure  # (if used)
```

### Migration Logic in Validation

```python
# Stage 3 validation handles migration automatically
if 'thermalDestructionPoint' in updated_properties and 'meltingPoint' in current_properties:
    # Migrate old to new format
    thermal_destruction_migration['thermalDestructionPoint'] = updated_properties['thermalDestructionPoint']
    thermal_destruction_migration['_remove_meltingPoint'] = True
```

---

## 📝 Usage in System Components

### AI Research Service
```python
# When researching thermalDestruction:
search_terms = ["melting point", "fusion temperature", "liquidus temperature"]
property_name = "thermalDestruction"  # Store under system name
```

### Validation System
```python
# Property validation recognizes both terms:
valid_thermal_props = ["thermalDestruction", "thermalDestructionPoint", "meltingPoint"]
```

### Content Generation
```python
# Content uses system terminology:
description = f"Material reaches thermal destruction at {temp}°C"
```

---

## 📚 Reference Materials

### Authoritative Sources for Thermal Data
- **ASM Handbook**: Comprehensive materials database
- **CRC Handbook**: Standard reference for physical constants
- **NIST WebBook**: Government database for chemical properties
- **Materials Project**: Computational materials database

### Research Databases
- **Google Scholar**: Peer-reviewed academic papers
- **ScienceDirect**: Scientific journal articles
- **Springer Materials**: Professional materials database
- **MatWeb**: Engineering materials database

---

## ✅ Quick Reference Summary

| System Term | Research Term | Category | Example Value |
|-------------|---------------|----------|---------------|
| `thermalDestruction` | melting point | Metal | 1538°C (iron) |
| `thermalDestruction` | charring temp | Wood | 280°C (oak) |
| `thermalDestruction` | sintering temp | Ceramic | 1600°C (alumina) |
| `thermalDestruction` | glass transition | Glass | 560°C (soda-lime) |
| `thermalDestruction` | degradation temp | Plastic | 300°C (PEEK) |

**Key Principle**: Research with standard scientific terms, store with system terminology, maintain data consistency across all components.