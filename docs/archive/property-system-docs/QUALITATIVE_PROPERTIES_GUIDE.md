# Qualitative Properties Handling Guide

**Last Updated**: October 17, 2025  
**Status**: ✅ Production Rule (Zero Tolerance for Violations)

---

## Overview

This guide establishes the **mandatory** treatment of qualitative (non-numerical, descriptive) properties in the Z-Beam Generator system. 

**Core Principle**: Qualitative properties **MUST NOT** have numerical `min`/`max` ranges and **MUST** be clearly separated from quantitative properties in all data structures.

---

## The Zero-Null Rule for Qualitative Properties

**ABSOLUTE REQUIREMENT**: Qualitative properties **MUST NEVER** show `min: null` or `max: null` in generated frontmatter.

### Why This Matters

Null values in frontmatter indicate one of two failures:
1. **Missing category ranges** → Properties should have ranges defined in Categories.yaml
2. **Improper property type** → Qualitative properties should not have numerical ranges at all

**Solution**: Qualitative properties must be identified and excluded from range assignment logic.

---

## Property Type Classification

### Quantitative Properties (Numerical)
**Characteristics**:
- Measurable with instruments
- Have numerical values with units
- Can be compared across materials using min/max ranges
- Require category-level ranges for comparison context

**Examples**:
- `density`: 2.7 g/cm³
- `thermalConductivity`: 237 W/m·K
- `hardness`: 150 HV
- `meltingPoint`: 660 °C

**Data Structure**:
```yaml
thermalConductivity:
  value: 237
  unit: W/m·K
  confidence: 95
  description: High thermal conductivity of pure aluminum
  min: 7.0        # From Categories.yaml
  max: 430        # From Categories.yaml
```

---

### Qualitative Properties (Descriptive)
**Characteristics**:
- Descriptive categories or classifications
- Text-based values from defined lists
- Cannot be numerically compared
- Do NOT require min/max ranges

**Examples**:
- `crystallineStructure`: "FCC", "BCC", "HCP", "amorphous"
- `oxidationResistance`: "poor", "moderate", "excellent"
- `surfaceFinish`: "polished", "rough", "textured"
- `corrosionBehavior`: "resistant", "susceptible"

**Data Structure**:
```yaml
crystallineStructure:
  value: "FCC"
  confidence: 99
  description: Face-centered cubic crystal structure
  # NO min/max fields
```

---

### Hybrid Properties (Context-Dependent)
**Characteristics**:
- Can be numerical OR qualitative depending on context
- Require conditional logic for range assignment

**Examples**:

**Porosity (Numerical)**:
```yaml
porosity:
  value: 15.5
  unit: "%"
  confidence: 85
  min: 10.0
  max: 25.0
```

**Porosity (Qualitative)**:
```yaml
porosity:
  value: "moderate"
  confidence: 75
  description: Moderate porosity level
  # NO min/max fields
```

---

## Known Qualitative Properties

### Structural Properties
- `crystallineStructure`: FCC, BCC, HCP, amorphous, cubic, hexagonal, tetragonal, orthorhombic, monoclinic, triclinic
- `grainStructure`: fine, medium, coarse, equiaxed, columnar
- `phase`: single, multi-phase, composite

### Surface Properties
- `surfaceFinish`: polished, rough, textured, smooth, matte, brushed
- `surfaceCondition`: clean, oxidized, contaminated, coated

### Resistance/Behavior Properties
- `oxidationResistance`: poor, fair, moderate, good, excellent
- `corrosionResistance`: poor, fair, moderate, good, excellent, immune
- `wearResistance`: low, moderate, high, exceptional
- `thermalShockBehavior`: brittle, stable, resistant

### Processing Properties
- `machinability`: difficult, fair, good, excellent
- `weldability`: poor, fair, good, excellent
- `formability`: poor, moderate, good, excellent

---

## Data Structure Rules

### In materials.yaml

**✅ CORRECT - Qualitative Property**:
```yaml
materials:
  Aluminum:
    properties:
      crystallineStructure:
        value: "FCC"
        confidence: 99
        description: Face-centered cubic structure at room temperature
        research_basis: X-ray diffraction analysis
```

**❌ WRONG - Qualitative Property with Ranges**:
```yaml
materials:
  Aluminum:
    properties:
      crystallineStructure:
        value: "FCC"
        min: "BCC"          # ❌ NO! Qualitative properties don't have min/max
        max: "HCP"          # ❌ NO! This makes no sense
```

---

### In Categories.yaml

**✅ CORRECT - Qualitative Property Definition**:
```yaml
categories:
  metal:
    category_ranges:
      crystallineStructure:
        allowedValues:
          - FCC
          - BCC
          - HCP
          - amorphous
        description: Crystal lattice structure classification
        validation: Must be one of the allowed values
```

**❌ WRONG - Qualitative Property with Numerical Ranges**:
```yaml
categories:
  metal:
    category_ranges:
      crystallineStructure:
        min: "FCC"          # ❌ NO! Qualitative properties don't have numerical ranges
        max: "HCP"          # ❌ NO! This is nonsensical
        unit: ""            # ❌ NO! No units for text classifications
```

---

### In Generated Frontmatter

**✅ CORRECT - Placed in materialCharacteristics**:
```yaml
materialProperties:
  material_characteristics:
    label: Material Characteristics
    properties:
      crystallineStructure:
        value: "FCC"
        confidence: 99
        description: Face-centered cubic crystal structure
        # NO min/max fields
      
      surfaceRoughness:
        value: 0.8
        unit: μm Ra
        confidence: 82
        min: 0.4
        max: 150
```

**❌ WRONG - Has Null Min/Max**:
```yaml
materialProperties:
  material_characteristics:
    properties:
      crystallineStructure:
        value: "FCC"
        confidence: 99
        min: null           # ❌ NO! Qualitative properties should not have min/max at all
        max: null           # ❌ NO! This violates zero-null rule
```

---

## Generator Implementation

### Property Type Detection

```python
QUALITATIVE_PROPERTIES = {
    'crystallineStructure',
    'oxidationResistance',
    'corrosionResistance',
    'surfaceFinish',
    'grainStructure',
    # ... add more as needed
}

def is_qualitative_property(property_name: str, property_value: Any) -> bool:
    """Determine if property is qualitative (non-numerical)"""
    
    # Check against known qualitative list
    if property_name in QUALITATIVE_PROPERTIES:
        return True
    
    # Check if value is string (not numerical)
    if isinstance(property_value, str):
        return True
    
    # Check if property has allowedValues instead of min/max
    if isinstance(property_value, dict):
        if 'allowedValues' in property_value:
            return True
    
    return False
```

### Range Assignment Logic

```python
def assign_category_ranges(property_name: str, property_data: dict, 
                          category_ranges: dict) -> dict:
    """Assign min/max ranges only to quantitative properties"""
    
    # Skip range assignment for qualitative properties
    if is_qualitative_property(property_name, property_data.get('value')):
        # Do NOT add min/max fields
        return property_data
    
    # Assign ranges for quantitative properties
    if property_name in category_ranges:
        range_data = category_ranges[property_name]
        property_data['min'] = range_data.get('min')
        property_data['max'] = range_data.get('max')
    
    return property_data
```

---

## Migration Strategy

### Step 1: Identify Qualitative Properties

Run detection script to find properties with:
- Non-numerical values
- `allowedValues` instead of `min`/`max`
- Text-based classifications

### Step 2: Update Data Files

**materials.yaml**:
- Remove any `min`/`max` fields from qualitative properties
- Ensure `value` field contains appropriate text classification
- Add `allowedValues` validation if needed

**Categories.yaml**:
- Replace `min`/`max` with `allowedValues` list
- Add `validation` field describing allowed values
- Document classification system in `notes`

### Step 3: Update Generator Logic

- Add qualitative property detection
- Skip range assignment for qualitative properties
- Place qualitative properties in `materialCharacteristics` section
- Validate values against `allowedValues` list

### Step 4: Validate Output

Run test suite to ensure:
- No qualitative properties have `min: null` or `max: null`
- All qualitative properties in correct section
- Values match allowed classifications
- No numerical ranges on text properties

---

## Testing Requirements

### Test Coverage

1. **Property Type Identification**
   - Verify known qualitative properties detected correctly
   - Confirm numerical properties NOT marked as qualitative
   - Validate hybrid property conditional logic

2. **materials.yaml Validation**
   - No qualitative properties have min/max fields
   - All qualitative values from allowed lists
   - Proper confidence and description fields

3. **Categories.yaml Validation**
   - Qualitative properties have allowedValues, not min/max
   - Allowed values lists are complete
   - Validation rules documented

4. **Frontmatter Validation**
   - No null min/max values for any properties
   - Qualitative properties in materialCharacteristics
   - Proper separation from quantitative properties

### Test Execution

```bash
# Run qualitative properties test suite
pytest tests/test_qualitative_properties.py -v

# Run full validation
pytest tests/ -k qualitative
```

---

## Common Pitfalls

### Pitfall 1: Treating Qualitative as Quantitative

**❌ WRONG**:
```yaml
oxidationResistance:
  value: "excellent"
  min: "poor"      # ❌ Can't numerically compare text values
  max: "excellent"
```

**✅ CORRECT**:
```yaml
oxidationResistance:
  value: "excellent"
  allowedValues: [poor, fair, moderate, good, excellent]
  description: Resistance to oxidation at elevated temperatures
```

---

### Pitfall 2: Missing AllowedValues

**❌ WRONG**:
```yaml
crystallineStructure:
  min: null        # ❌ Qualitative properties don't have ranges
  max: null
  unit: ""
```

**✅ CORRECT**:
```yaml
crystallineStructure:
  allowedValues: [FCC, BCC, HCP, amorphous, cubic]
  description: Crystal lattice structure classification
  validation: Must be one of the defined crystal systems
```

---

### Pitfall 3: Mixing Numerical and Text Values

**❌ WRONG**:
```yaml
# Trying to use both numerical and qualitative
porosity:
  value: 15.5
  qualitative: "moderate"  # ❌ Choose one approach
  min: 10.0
  max: 25.0
```

**✅ CORRECT (Pick One)**:
```yaml
# Option A: Numerical
porosity:
  value: 15.5
  unit: "%"
  min: 10.0
  max: 25.0

# Option B: Qualitative
porosity:
  value: "moderate"
  allowedValues: [low, moderate, high]
```

---

## Enforcement

### Validation Gates

1. **Pre-Generation**: Validate materials.yaml for qualitative property structure
2. **During Generation**: Skip range assignment for qualitative properties
3. **Post-Generation**: Validate frontmatter has no null values
4. **CI/CD**: Automated tests prevent commits with violations

### Error Messages

```
❌ VALIDATION ERROR: Qualitative property 'crystallineStructure' has min/max fields
   Material: Aluminum
   Fix: Remove min/max fields - qualitative properties don't have numerical ranges

❌ VALIDATION ERROR: Property 'crystallineStructure' has null min/max in frontmatter
   File: aluminum-laser-cleaning.yaml
   Fix: Property should be in materialCharacteristics without min/max fields

❌ VALIDATION ERROR: Invalid value 'cubic-hexagonal' for 'crystallineStructure'
   Material: Titanium
   Allowed: [FCC, BCC, HCP, amorphous, cubic, hexagonal]
   Fix: Use one of the allowed crystal structure classifications
```

---

## Summary Checklist

**For Each Qualitative Property**:
- [ ] Listed in QUALITATIVE_PROPERTIES constant
- [ ] Has `allowedValues` in Categories.yaml (not `min`/`max`)
- [ ] No `min`/`max` fields in materials.yaml
- [ ] Placed in `materialCharacteristics` section in frontmatter
- [ ] Never shows `min: null` or `max: null` in output
- [ ] Value validated against allowed list
- [ ] Test coverage for type detection and validation

---

## References

- **DATA_ARCHITECTURE.md**: QUALITATIVE PROPERTIES HANDLING RULE section
- **Test Suite**: `tests/test_qualitative_properties.py`
- **Schema Definition**: `schemas/frontmatter_schema.yaml`
- **Generator Code**: `components/frontmatter/generators/streamlined_generator.py`
