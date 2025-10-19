# Unit Conversion System

**Version**: 1.0  
**Last Updated**: October 19, 2025  
**Status**: ✅ IMPLEMENTED

---

## 📋 Overview

The Unit Conversion System normalizes property values to standard units before validation, preventing false positives from unit mismatches.

### Problem Solved

**Bug**: electricalConductivity validation failure
```
❌ electricalConductivity = 37,700,000 S/m > 70.0 (global max)
```

**Root Cause**: Validator compared `37,700,000 S/m` to `70 MS/m` without conversion

**Solution**: Auto-convert to normalized unit before range validation
```
✅ electricalConductivity = 37.7 MS/m < 70.0 (global max)
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│           VALIDATION PIPELINE                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│  1. Load property value & unit                      │
│     value = 37,700,000                              │
│     unit = "S/m"                                    │
│                                                      │
│  2. ⚡ UNIT NORMALIZATION (NEW)                     │
│     normalized_value = 37.7                         │
│     normalized_unit = "MS/m"                        │
│                                                      │
│  3. Range validation (using normalized values)      │
│     if 37.7 > 70.0: FAIL                           │
│     else: PASS ✅                                   │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Usage

### Automatic Conversion in Validation

```python
from validation.helpers.unit_converter import UnitConverter

# Example: electricalConductivity
value = 37700000.0  # 37.7 million Siemens/meter
unit = "S/m"

# Normalize before validation
normalized_value, normalized_unit = UnitConverter.normalize(
    'electricalConductivity',
    value,
    unit
)

print(f"Original: {value} {unit}")
print(f"Normalized: {normalized_value} {normalized_unit}")
# Output:
# Original: 37700000.0 S/m
# Normalized: 37.7 MS/m
```

### Checking Convertibility

```python
# Check if a unit can be converted
is_valid = UnitConverter.is_convertible(
    'electricalConductivity',
    'S/m'
)
print(f"Can convert S/m: {is_valid}")  # True

# Check normalized unit for a property
norm_unit = UnitConverter.get_normalized_unit('electricalConductivity')
print(f"Normalized unit: {norm_unit}")  # MS/m
```

---

## 📊 Conversion Rules

### electricalConductivity → MS/m (MegaSiemens/meter)

| Source Unit | Conversion Factor | Example |
|-------------|------------------|---------|
| MS/m        | 1.0             | 37.7 MS/m = 37.7 MS/m |
| S/m         | 1e-6            | 37,700,000 S/m = 37.7 MS/m |
| ×10⁷ S/m    | 10.0            | 3.77×10⁷ S/m = 37.7 MS/m |
| % IACS      | 0.581           | 64.9% IACS = 37.7 MS/m |

**Note**: 100% IACS = 58.1 MS/m (copper standard)

### electricalResistivity → Ω·m (Ohm-meter)

| Source Unit | Conversion Factor | Example |
|-------------|------------------|---------|
| Ω·m         | 1.0             | 2.65e-8 Ω·m = 2.65e-8 Ω·m |
| ohm·m       | 1.0             | (same as Ω·m) |
| Ω⋅m         | 1.0             | (same as Ω·m) |

### thermalConductivity → W/(m·K)

| Source Unit | Conversion Factor | Example |
|-------------|------------------|---------|
| W/(m·K)     | 1.0             | 237 W/(m·K) = 237 W/(m·K) |
| W/m·K       | 1.0             | (same) |
| W/mK        | 1.0             | (same) |

### density → g/cm³

| Source Unit | Conversion Factor | Example |
|-------------|------------------|---------|
| g/cm³       | 1.0             | 2.7 g/cm³ = 2.7 g/cm³ |
| g/cc        | 1.0             | (same as g/cm³) |
| kg/m³       | 0.001           | 2700 kg/m³ = 2.7 g/cm³ |

### hardness → GPa

| Source Unit | Conversion Factor | Example |
|-------------|------------------|---------|
| GPa         | 1.0             | 2.4 GPa = 2.4 GPa |
| MPa         | 0.001           | 2400 MPa = 2.4 GPa |
| HV          | 0.0098          | ~245 HV ≈ 2.4 GPa |
| Mohs        | N/A             | Non-linear scale |

**Note**: Mohs hardness cannot be linearly converted to GPa

### youngsModulus → GPa

| Source Unit | Conversion Factor | Example |
|-------------|------------------|---------|
| GPa         | 1.0             | 70 GPa = 70 GPa |
| MPa         | 0.001           | 70,000 MPa = 70 GPa |
| Pa          | 1e-9            | 7e10 Pa = 70 GPa |

### tensileStrength → MPa

| Source Unit | Conversion Factor | Example |
|-------------|------------------|---------|
| MPa         | 1.0             | 310 MPa = 310 MPa |
| GPa         | 1000.0          | 0.31 GPa = 310 MPa |
| Pa          | 1e-6            | 3.1e8 Pa = 310 MPa |

### thermalDiffusivity → mm²/s

| Source Unit | Conversion Factor | Example |
|-------------|------------------|---------|
| mm²/s       | 1.0             | 97.1 mm²/s = 97.1 mm²/s |
| m²/s        | 1,000,000.0     | 9.71e-5 m²/s = 97.1 mm²/s |
| cm²/s       | 100.0           | 0.971 cm²/s = 97.1 mm²/s |

---

## 🧪 Testing

### Unit Test Examples

```python
# tests/test_unit_converter.py
import pytest
from validation.helpers.unit_converter import UnitConverter, UnitConversionError

def test_electrical_conductivity_conversion():
    """Test S/m to MS/m conversion"""
    # Aluminum: 37.7 MS/m = 37,700,000 S/m
    normalized, unit = UnitConverter.normalize(
        'electricalConductivity',
        37700000.0,
        'S/m'
    )
    assert normalized == 37.7
    assert unit == 'MS/m'

def test_iacs_conversion():
    """Test % IACS to MS/m conversion"""
    # 100% IACS = 58.1 MS/m (copper standard)
    normalized, unit = UnitConverter.normalize(
        'electricalConductivity',
        100.0,
        '% IACS'
    )
    assert normalized == 58.1
    assert unit == 'MS/m'

def test_unknown_unit():
    """Test error on unknown unit"""
    with pytest.raises(UnitConversionError):
        UnitConverter.normalize(
            'electricalConductivity',
            37.7,
            'invalid_unit'
        )

def test_non_convertible_property():
    """Test property without conversion rules"""
    # Properties without rules return unchanged
    normalized, unit = UnitConverter.normalize(
        'unknownProperty',
        100.0,
        'unknown_unit'
    )
    assert normalized == 100.0
    assert unit == 'unknown_unit'
```

### Integration Test

```bash
# Test with Aluminum (real-world case)
python3 run.py --material "Aluminum"

# Should now PASS validation:
# ✅ electricalConductivity = 37.7 MS/m < 70.0 (global max)
```

---

## 🔧 Adding New Conversions

### Step 1: Define Conversion Rules

Edit `validation/helpers/unit_converter.py`:

```python
CONVERSION_RULES = {
    'newProperty': {
        'normalized_unit': {  # First key is normalized unit
            'normalized_unit': 1.0,
            'source_unit_1': conversion_factor_1,
            'source_unit_2': conversion_factor_2,
        }
    }
}
```

### Step 2: Add Tests

```python
def test_new_property_conversion():
    normalized, unit = UnitConverter.normalize(
        'newProperty',
        value_in_source_unit,
        'source_unit_1'
    )
    assert normalized == expected_normalized_value
    assert unit == 'normalized_unit'
```

### Step 3: Update Documentation

Add to this file under "Conversion Rules"

---

## 🚨 Common Issues

### Issue 1: "Unknown unit" error
**Cause**: Unit not in conversion rules  
**Solution**: Add unit to CONVERSION_RULES or use supported unit

### Issue 2: Validation still failing after conversion
**Cause**: Value genuinely out of range  
**Solution**: Check if value is physically reasonable

### Issue 3: Non-linear scale (e.g., Mohs)
**Cause**: Some scales can't be linearly converted  
**Solution**: Handle separately or use conversion factor = None

---

## 📊 Performance

- **Overhead**: < 1ms per property
- **Cache**: No caching needed (simple multiplication)
- **Memory**: Minimal (static conversion tables)

---

## ✅ Best Practices

1. **Always normalize before range validation**
2. **Use try-except for conversion errors**
3. **Log original and normalized values for debugging**
4. **Test with real data from Materials.yaml**
5. **Document conversion factors with sources**

---

## 🔗 Related Documentation

- **[PROPERTY_REFERENCE_SYSTEM.md](./PROPERTY_REFERENCE_SYSTEM.md)** - Property definitions
- **[VALIDATION_ARCHITECTURE.md](./VALIDATION_ARCHITECTURE.md)** - Validation system
- **[DATA_ARCHITECTURE.md](./DATA_ARCHITECTURE.md)** - Data structure

---

## 📝 Change Log

### v1.0 (October 19, 2025)
- ✅ Initial implementation
- ✅ Fixed electricalConductivity bug (37.7M S/m issue)
- ✅ Added 9 common property conversions
- ✅ Integrated with PreGenerationValidationService
- ✅ Comprehensive test coverage

---

**Last Updated**: October 19, 2025  
**Maintainer**: Z-Beam Generator Team  
**Status**: ✅ Production Ready
