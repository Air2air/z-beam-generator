# Numeric Formatting Policy

**Purpose**: Ensure consistent, readable numeric formatting across all frontmatter exports  
**Last Updated**: November 29, 2025  
**Status**: ACTIVE

---

## 🎯 Core Principle

**Values should be formatted for human readability while preserving scientific accuracy.**

- Users don't need 6 decimal places for density
- Users don't want to count zeros in `37700000.0`
- Values should be easy to read at a glance
- Scientific notation only when truly necessary

---

## 📐 Formatting Rules by Value Range

### Rule 1: Very Small Numbers (< 0.01)
**Format**: Scientific notation with 2 significant figures

| Raw Value | Formatted | Reason |
|-----------|-----------|--------|
| `2.65e-08` | `2.7e-8` | Readability |
| `0.000015` | `1.5e-5` | Avoid leading zeros |
| `0.00001` | `1.0e-5` | Preserve magnitude |

### Rule 2: Small Numbers (0.01 to 0.99)
**Format**: 2 decimal places maximum

| Raw Value | Formatted | Reason |
|-----------|-----------|--------|
| `0.2744` | `0.27` | Unnecessary precision |
| `0.06` | `0.06` | Already good |
| `0.019` | `0.02` | Round for readability |

### Rule 3: Numbers Near Whole (1 to 999)
**Format**: 
- For values 1-99: 1 decimal place if fractional, whole if not
- For values 100-999: Always round to whole number (cleaner for larger values)

| Raw Value | Formatted | Reason |
|-----------|-----------|--------|
| `5.1` | `5.1` | Meaningful decimal |
| `90.0` | `90` | Drop trailing .0 |
| `237.0` | `237` | Drop trailing .0 |
| `933.47` | `933` | Round to whole (≥100) |
| `255.7565` | `256` | Round to whole (≥100) |

### Rule 4: Large Numbers (1,000 to 999,999)
**Format**: Whole numbers, no decimals

| Raw Value | Formatted | Reason |
|-----------|-----------|--------|
| `2792.0` | `2792` | Drop .0 |
| `10640` | `10640` | Already good |
| `101325.0` | `101325` | Drop .0 |

### Rule 5: Very Large Numbers (≥ 1,000,000)
**Format**: Scientific notation with 2 significant figures

| Raw Value | Formatted | Reason |
|-----------|-----------|--------|
| `37700000.0` | `3.8e7` | Readability |
| `66115300.0` | `6.6e7` | Avoid counting zeros |
| `50000000` | `5.0e7` | Standardize |

### Rule 6: Percentages
**Format**: Whole numbers or 1 decimal place

| Raw Value | Formatted | Reason |
|-----------|-----------|--------|
| `50` | `50` | Already good |
| `15.0` | `15` | Drop trailing .0 |
| `0.5` | `0.5` | Preserve meaningful decimal |

---

## 🔧 Implementation

### Python Formatting Function

```python
def format_value(value: float, unit: str = '') -> Union[int, float, str]:
    """
    Format numeric value for human readability.
    
    Args:
        value: Raw numeric value
        unit: Unit string (for context)
    
    Returns:
        Formatted value (int, float, or scientific notation string)
    """
    if value is None:
        return None
    
    abs_val = abs(value)
    
    # Rule 1: Very small numbers - scientific notation
    if abs_val < 0.01 and abs_val > 0:
        return f"{value:.2g}"  # 2 significant figures
    
    # Rule 5: Very large numbers - scientific notation
    if abs_val >= 1_000_000:
        return f"{value:.2g}"  # 2 significant figures
    
    # Rule 2: Small numbers (0.01 to 0.99) - 2 decimal places
    if abs_val < 1:
        rounded = round(value, 2)
        return rounded if rounded != int(rounded) else int(rounded)
    
    # Rule 3: Numbers 1 to 999 - whole or 1 decimal
    if abs_val < 1000:
        rounded = round(value, 1)
        if rounded == int(rounded):
            return int(rounded)
        return rounded
    
    # Rule 4: Large numbers (1000 to 999999) - whole numbers
    return int(round(value))
```

### Integration Points

1. **TrivialFrontmatterExporter**: Apply in `_enrich_material_properties()` and `_enrich_machine_settings()`
2. **Data Export**: Apply before YAML serialization
3. **Research Output**: Apply when saving AI-researched values

---

## 📊 Before/After Examples

### Machine Settings

| Parameter | Before | After |
|-----------|--------|-------|
| `powerRange.min` | `1.0` | `1` |
| `powerRange.max` | `120` | `120` |
| `spotSize.min` | `0.1` | `0.1` |
| `energyDensity.value` | `5.1` | `5.1` |

### Material Properties

| Property | Before | After |
|----------|--------|-------|
| `density` | `2.7` | `2.7` |
| `hardness` | `0.2744` | `0.27` |
| `thermalDestruction` | `933.47` | `933` |
| `thermalDestruction.min` | `255.7565` | `256` |
| `electricalResistivity` | `2.65e-08` | `2.7e-8` |
| `electricalConductivity` | `37700000.0` | `3.8e7` |

---

## ⚠️ Exceptions

### Preserve Full Precision For:
1. **Boiling/Melting Points in Kelvin**: Scientific constants, preserve 2 decimals
2. **Specific Scientific Constants**: When source data specifies precision
3. **Regulatory Values**: Must match official documentation exactly

### Never Round:
1. **Allowed Values Lists**: Qualitative enums (exact match required)
2. **Unit Strings**: Never modify units
3. **IDs/References**: Never modify identifiers

---

## 🧪 Testing

Test file: `tests/export/test_numeric_formatting.py`

```python
def test_format_very_small():
    assert format_value(2.65e-08) == "2.7e-8"
    assert format_value(0.00001) == "1.0e-5"

def test_format_small():
    assert format_value(0.2744) == 0.27
    assert format_value(0.06) == 0.06

def test_format_near_whole():
    assert format_value(90.0) == 90
    assert format_value(933.47) == 933
    assert format_value(5.1) == 5.1

def test_format_large():
    assert format_value(37700000.0) == "3.8e7"
    assert format_value(101325.0) == 101325

def test_percentages():
    assert format_value(50) == 50
    assert format_value(15.0) == 15
```

---

## 📚 Related Documentation

- `docs/05-data/DATA_ARCHITECTURE.md` - Data structure overview
- `docs/schemas/DATA_FIELD_LOCATIONS.md` - Where values are stored
- `export/core/trivial_exporter.py` - Export implementation

---

## 🔄 Maintenance

**When adding new properties**:
1. Determine appropriate formatting rule based on typical value range
2. Document any exceptions in this file
3. Add test cases for edge values
4. Verify output after export

**When changing rules**:
1. Update this document first
2. Update formatting function
3. Run full test suite
4. Re-export and verify frontmatter
