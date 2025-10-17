# Qualitative Properties Handling Guide

**Last Updated**: October 17, 2025  
**Status**: ✅ Active Rule - Enforced in validation and testing

---

## Overview

This document defines how **qualitative (non-numerical) properties** are handled differently from **quantitative (numerical) properties** in the Z-Beam Generator system.

---

## The Rule

**QUALITATIVE PROPERTIES HANDLING RULE**: Properties with **non-numerical values** (text, enums, ratings) MUST be handled separately from quantitative properties:

1. **No min/max ranges**: Qualitative properties have `min: null, max: null` (always)
2. **Separate storage**: Store in `materialCharacteristics` section (NOT mixed with numerical data)
3. **Zero Null Policy exemption**: Null ranges are ALLOWED for qualitative properties
4. **Legacy migration**: If found in legacy materials.yaml with ranges, remove ranges and move to appropriate section

---

## Property Classification

### Quantitative Properties (Numerical)
**Definition**: Properties with numerical values that can be measured, compared, and have meaningful min/max ranges.

**Characteristics**:
- Value is a number (int or float)
- Has units of measurement
- Can be compared with `<`, `>`, `=`
- Has meaningful statistical ranges across materials

**Examples**:
```yaml
# Quantitative - MUST have min/max ranges
density:
  value: 2.7
  unit: g/cm³
  confidence: 98
  min: 0.53    # ✅ Required
  max: 22.6    # ✅ Required

thermalConductivity:
  value: 237
  unit: W/m·K
  confidence: 95
  min: 6.0     # ✅ Required
  max: 429.0   # ✅ Required
```

### Qualitative Properties (Descriptive)
**Definition**: Properties with descriptive text values that cannot be numerically compared.

**Characteristics**:
- Value is a string (enum, rating, description)
- No units or non-numerical units (e.g., "rating")
- Cannot be mathematically compared
- Represents categories, states, or qualities

**Examples**:
```yaml
# Qualitative - MUST NOT have min/max ranges
crystallineStructure:
  value: FCC
  confidence: 95
  description: Face-centered cubic crystal structure
  min: null    # ✅ Always null for qualitative
  max: null    # ✅ Always null for qualitative

oxidationResistance:
  value: high
  confidence: 85
  description: Resistance to surface oxidation
  min: null    # ✅ Always null for qualitative
  max: null    # ✅ Always null for qualitative

corrosionResistance:
  value: excellent
  unit: rating
  confidence: 90
  min: null    # ✅ Always null for qualitative
  max: null    # ✅ Always null for qualitative
```

---

## Common Qualitative Properties

### Material Properties
- `crystallineStructure` - Crystal lattice type (FCC, BCC, HCP, etc.)
- `oxidationResistance` - Qualitative rating (low, medium, high, excellent)
- `corrosionResistance` - Qualitative rating (poor, fair, good, excellent)
- `biocompatibility` - Compatibility rating (none, low, moderate, high)
- `chemicalStability` - Stability rating (unstable, stable, very stable)
- `flammability` - Fire behavior (non-flammable, low, moderate, high)

### Machine Settings
- `beamProfile` - Beam shape (Gaussian, flat-top, donut)
- `safetyClass` - Laser safety classification (Class 1, 2, 3R, 3B, 4)

### Processing
- `surfaceTreatments` - Array of treatment types
- `incompatibleConditions` - Array of conditions to avoid

---

## Implementation Guidelines

### 1. Adding New Qualitative Properties

**Categories.yaml**:
```yaml
categories:
  metal:
    category_ranges:
      oxidationResistance:
        allowedValues: ['poor', 'fair', 'good', 'excellent']  # ✅ Use allowedValues
        unit: rating
        description: Resistance to surface oxidation
        confidence: 85
        notes: Based on exposure testing at elevated temperatures
        # ❌ NO min/max fields
```

**materials.yaml**:
```yaml
materials:
  Aluminum:
    properties:
      oxidationResistance:
        value: good         # ✅ String value
        confidence: 85
        # ❌ NO min/max fields (ranges only in Categories.yaml)
```

### 2. Generating Frontmatter

**Generator Logic**:
```python
def generate_property(prop_name, prop_value, category_ranges):
    """Generate property with proper min/max handling"""
    
    # Check if qualitative
    if isinstance(prop_value['value'], str):
        # Qualitative property
        return {
            'value': prop_value['value'],
            'unit': prop_value.get('unit', ''),
            'confidence': prop_value.get('confidence', 80),
            'description': prop_value.get('description', ''),
            'min': None,  # ✅ Always null
            'max': None   # ✅ Always null
        }
    else:
        # Quantitative property
        category_range = category_ranges.get(prop_name, {})
        return {
            'value': prop_value['value'],
            'unit': prop_value.get('unit', ''),
            'confidence': prop_value.get('confidence', 80),
            'description': prop_value.get('description', ''),
            'min': category_range.get('min'),  # ✅ From Categories.yaml
            'max': category_range.get('max')   # ✅ From Categories.yaml
        }
```

### 3. Validation Rules

**Qualitative Property Checks**:
```python
def validate_qualitative_property(prop_name, prop_data):
    """Validate qualitative property structure"""
    errors = []
    
    # Check value type
    if not isinstance(prop_data.get('value'), str):
        errors.append(f"{prop_name}: Qualitative property must have string value")
    
    # Check min/max are null
    if prop_data.get('min') is not None:
        errors.append(f"{prop_name}: Qualitative property must have min=null")
    
    if prop_data.get('max') is not None:
        errors.append(f"{prop_name}: Qualitative property must have max=null")
    
    return errors
```

**Quantitative Property Checks (Zero Null Policy)**:
```python
def validate_quantitative_property(prop_name, prop_data):
    """Validate quantitative property structure"""
    errors = []
    
    # Check value type
    if not isinstance(prop_data.get('value'), (int, float)):
        errors.append(f"{prop_name}: Quantitative property must have numerical value")
    
    # Check min/max are NOT null (Zero Null Policy)
    if prop_data.get('min') is None:
        errors.append(f"{prop_name}: Quantitative property must have min value (Zero Null Policy)")
    
    if prop_data.get('max') is None:
        errors.append(f"{prop_name}: Quantitative property must have max value (Zero Null Policy)")
    
    return errors
```

---

## Migration from Legacy Data

### Identifying Legacy Violations

**❌ Legacy Violation Example**:
```yaml
# OLD materials.yaml (WRONG)
materials:
  Steel:
    properties:
      crystallineStructure:
        value: BCC
        min: 0        # ❌ Qualitative property with numerical range
        max: 10       # ❌ Makes no sense for descriptive value
```

**✅ Corrected Structure**:
```yaml
# NEW materials.yaml (CORRECT)
materials:
  Steel:
    properties:
      crystallineStructure:
        value: BCC
        confidence: 95
        # ✅ No min/max in materials.yaml
```

```yaml
# Categories.yaml
categories:
  metal:
    category_ranges:
      crystallineStructure:
        allowedValues: ['FCC', 'BCC', 'HCP']  # ✅ Use allowedValues
        description: Crystal lattice structure
        # ✅ No numerical min/max
```

### Migration Script Template

```python
def migrate_qualitative_properties(materials_data, qualitative_props):
    """Remove min/max from qualitative properties in materials.yaml"""
    
    for material_name, material_data in materials_data['materials'].items():
        properties = material_data.get('properties', {})
        
        for prop_name in qualitative_props:
            if prop_name in properties:
                prop_data = properties[prop_name]
                
                # Remove min/max if present
                if 'min' in prop_data:
                    del prop_data['min']
                    print(f"Removed min from {material_name}.{prop_name}")
                
                if 'max' in prop_data:
                    del prop_data['max']
                    print(f"Removed max from {material_name}.{prop_name}")
    
    return materials_data
```

---

## Testing

### Test Coverage Required

1. **Detection Tests**:
   - Identify qualitative vs quantitative properties correctly
   - Classify based on value type

2. **Frontmatter Tests**:
   - Qualitative properties have null min/max
   - Quantitative properties have non-null min/max (Zero Null Policy)
   - No mixed categorization

3. **Categories.yaml Tests**:
   - Qualitative properties use `allowedValues` not numerical ranges
   - No qualitative properties with numerical min/max

4. **materials.yaml Tests**:
   - No qualitative properties with min/max fields (VITAL RULE)
   - All ranges live in Categories.yaml only

### Running Tests

```bash
# Run qualitative properties tests
pytest tests/test_qualitative_properties.py -v

# Run specific test class
pytest tests/test_qualitative_properties.py::TestQualitativePropertiesInFrontmatter -v

# Run with coverage
pytest tests/test_qualitative_properties.py --cov=components.frontmatter --cov=generators
```

---

## Exceptions

### Machine Settings
Machine settings properties (wavelength, fluenceRange, etc.) follow **different rules**:
- May have null min/max even if numerical
- Ranges are material-specific, not category-wide
- Stored in `machineSettings` section, not `materialProperties`

**Example**:
```yaml
machineSettings:
  wavelength:
    value: 1064
    unit: nm
    confidence: 88
    min: null    # ✅ Allowed for machine settings
    max: null    # ✅ No category-wide wavelength ranges
```

---

## Summary Checklist

**For Qualitative Properties**:
- [x] Value is descriptive text/enum
- [x] `min: null` and `max: null` in frontmatter
- [x] Use `allowedValues` in Categories.yaml (not numerical ranges)
- [x] No min/max fields in materials.yaml
- [x] Stored in `materialCharacteristics` section

**For Quantitative Properties**:
- [x] Value is numerical (int/float)
- [x] Has units of measurement
- [x] `min` and `max` are NON-NULL in frontmatter (Zero Null Policy)
- [x] Ranges defined in Categories.yaml category_ranges
- [x] No min/max fields in materials.yaml (VITAL RULE)
- [x] Stored in appropriate materialProperties category

---

## References

- **Data Architecture**: `docs/DATA_ARCHITECTURE.md`
- **Zero Null Policy**: `docs/ZERO_NULL_POLICY.md`
- **Test Suite**: `tests/test_qualitative_properties.py`
- **Categories Schema**: `schemas/categories_schema.yaml`
- **Materials Schema**: `schemas/materials_schema.yaml`
