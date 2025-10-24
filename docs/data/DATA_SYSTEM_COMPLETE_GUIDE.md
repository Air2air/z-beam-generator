# Z-Beam Data System - Complete Guide

**Complete reference for working with Materials.yaml and Categories.yaml**  
**Last Updated**: October 15, 2025

---

## 📖 Quick Navigation

- [Architecture Overview](#architecture-overview) - High-level design
- [Property Patterns](#property-patterns) - 4 patterns supported
- [Using Helpers](#using-helpers) - Convenience methods
- [Category System](#category-system) - Range validation
- [Research & Validation](#research--validation) - Data quality tools
- [Examples](#examples) - Code samples
- [Troubleshooting](#troubleshooting) - Common issues

---

## Architecture Overview

### Design Principles

**Separation of Concerns**:
- `Categories.yaml`: Reference ranges for material types (metals, ceramics, plastics, etc.)
- `Materials.yaml`: Specific values for individual materials (Copper, Steel, etc.)

**Benefits**:
- ✅ Category ranges provide context for validating material values
- ✅ Easy to spot outliers and errors
- ✅ Materials inherit categorical understanding
- ✅ Research-backed data with confidence scoring

### File Structure

```
data/
├── Materials.yaml    # 244 materials with properties
└── Categories.yaml   # 9 categories with ranges

utils/
└── property_helpers.py  # Convenience helpers (NEW!)

scripts/
├── research_range_violations.py  # AI research tool
└── fix_range_violations.py       # Automatic fixer

tests/
└── test_category_range_compliance.py  # Validation suite
```

### Data Flow

```
Category Ranges → Validate → Material Values → Generate Content
     ↓                           ↓
  Context for              Specific laser
  comparison               cleaning data
```

---

## Property Patterns

The system supports **4 property patterns** to handle different types of laser-material interaction data:

### Pattern 1: Simple Value

**Use**: Standard material properties (density, hardness, etc.)

**Structure**:
```yaml
density:
  value: 8.96
  unit: "g/cm³"
  confidence: 0.95
  source: "CRC Handbook"
```

**Access**:
```python
from utils.property_helpers import PropertyAccessor

value = PropertyAccessor.get_value(material['properties']['density'])
# Returns: 8.96
```

### Pattern 2: Nested Structure

**Use**: Complex properties with sub-fields (thermal destruction)

**Structure**:
```yaml
thermalDestruction:
  point:
    value: 1357.77
    unit: "K"
    confidence: 0.95
    source: "CRC Handbook"
  type: "melting"
```

**Why Nested?**:
- Semantically correct: destruction has both point and mechanism
- Preserves scientific accuracy
- Allows multiple destruction modes (melting, decomposition, etc.)

**Access**:
```python
# Using helper (recommended)
temp = PropertyAccessor.get_thermal_destruction_point(material)
dtype = PropertyAccessor.get_thermal_destruction_type(material)

# Manual access
temp = material['properties']['thermalDestruction']['point']['value']
```

### Pattern 3: Pulse-Specific

**Use**: Properties varying by laser pulse duration (ablation threshold)

**Structure**:
```yaml
ablationThreshold:
  nanosecond:
    min: 2.0
    max: 8.0
    unit: "J/cm²"
  picosecond:
    min: 0.1
    max: 2.0
    unit: "J/cm²"
  femtosecond:
    min: 0.14
    max: 1.7
    unit: "J/cm²"
  confidence: 0.90
  source: "Journal of Laser Applications"
```

**Why Pulse-Specific?**:
- Ablation threshold varies dramatically with pulse duration
- Critical for laser parameter selection
- Cannot collapse to single value without losing information

**Access**:
```python
# Get average for specific pulse type
ns_threshold = PropertyAccessor.get_ablation_threshold(material, 'nanosecond')
# Returns: 5.0 (average of 2.0-8.0)

# Get as range
ns_range = PropertyAccessor.get_ablation_threshold(
    material, 'nanosecond', return_range=True
)
# Returns: (2.0, 8.0)
```

### Pattern 4: Wavelength-Specific

**Use**: Properties varying by laser wavelength (reflectivity)

**Structure**:
```yaml
reflectivity:
  at_1064nm:  # Nd:YAG / Fiber laser
    min: 85
    max: 98
    unit: "%"
  at_532nm:   # Green doubled Nd:YAG
    min: 70
    max: 95
    unit: "%"
  at_355nm:   # UV tripled Nd:YAG
    min: 55
    max: 85
    unit: "%"
  at_10640nm: # CO2 laser
    min: 2
    max: 8
    unit: "%"
  confidence: 0.88
  source: "Palik Handbook of Optical Constants"
```

**Why Wavelength-Specific?**:
- Reflectivity changes dramatically with wavelength
- Copper reflects 98% at 1064nm but only 2% at 10640nm
- Critical for laser selection and process design

**Access**:
```python
# Get average for specific wavelength
refl_1064 = PropertyAccessor.get_reflectivity(material, '1064nm')
# Returns: 91.5 (average of 85-98)

# Get as range
refl_range = PropertyAccessor.get_reflectivity(
    material, '1064nm', return_range=True
)
# Returns: (85.0, 98.0)
```

### Pattern Detection

```python
pattern = PropertyAccessor.detect_property_pattern(prop_data)
# Returns: 'simple', 'nested', 'pulse-specific', 'wavelength-specific', or 'unknown'
```

---

## Using Helpers

**NEW!** The `PropertyAccessor` class simplifies property access while preserving all advanced features.

### Basic Usage

```python
from utils.property_helpers import PropertyAccessor

# Load data
import yaml
with open('data/Materials.yaml', 'r') as f:
    materials_data = yaml.safe_load(f)

materials = materials_data['materials']
copper = materials['Copper']

# Get any property value
density = PropertyAccessor.get_value(copper['properties']['density'])
temp = PropertyAccessor.get_thermal_destruction_point(copper)
threshold = PropertyAccessor.get_ablation_threshold(copper, 'femtosecond')
```

### All PropertyAccessor Methods

#### `get_value(prop_data, pulse_type='nanosecond', wavelength='1064nm', return_range=False)`
Universal property getter with automatic pattern detection.

```python
# Simple value
value = PropertyAccessor.get_value({'value': 8.96})

# Nested structure
value = PropertyAccessor.get_value({
    'point': {'value': 1357.77}, 
    'type': 'melting'
})

# Pulse-specific
value = PropertyAccessor.get_value(
    {'nanosecond': {'min': 2.0, 'max': 8.0}},
    pulse_type='nanosecond'
)

# With range
range_tuple = PropertyAccessor.get_value(
    {'nanosecond': {'min': 2.0, 'max': 8.0}},
    return_range=True
)  # Returns: (2.0, 8.0)
```

#### `get_thermal_destruction_point(material)`
Get thermalDestruction.point.value safely.

```python
temp = PropertyAccessor.get_thermal_destruction_point(copper)
# Returns: 1357.77 (in K)
```

#### `get_thermal_destruction_type(material)`
Get thermalDestruction.type safely.

```python
dtype = PropertyAccessor.get_thermal_destruction_type(copper)
# Returns: "melting"
```

#### `get_ablation_threshold(material, pulse_type='nanosecond', return_range=False)`
Get ablation threshold for specific pulse duration.

```python
# Average value
threshold = PropertyAccessor.get_ablation_threshold(steel, 'femtosecond')

# As range
threshold_range = PropertyAccessor.get_ablation_threshold(
    steel, 'femtosecond', return_range=True
)
```

#### `get_reflectivity(material, wavelength='1064nm', return_range=False)`
Get reflectivity for specific wavelength.

```python
# Average value
refl = PropertyAccessor.get_reflectivity(aluminum, '532nm')

# As range
refl_range = PropertyAccessor.get_reflectivity(
    aluminum, '532nm', return_range=True
)
```

#### `get_property_safely(material, property_name, **kwargs)`
Get any property with automatic pattern detection.

```python
density = PropertyAccessor.get_property_safely(copper, 'density')
temp = PropertyAccessor.get_property_safely(copper, 'thermalDestruction')
threshold = PropertyAccessor.get_property_safely(
    copper, 'ablationThreshold', pulse_type='femtosecond'
)
```

#### `get_all_property_values(material, pulse_type='nanosecond', wavelength='1064nm')`
Get all properties as flat dictionary.

```python
values = PropertyAccessor.get_all_property_values(copper)
# Returns: {'density': 8.96, 'hardness': 369.0, ...}
```

#### `get_category_range(categories, category, property_name)`
Get category range with nested support.

```python
with open('data/Categories.yaml', 'r') as f:
    categories = yaml.safe_load(f)

range_data = PropertyAccessor.get_category_range(
    categories, 'metal', 'density'
)
# Returns: {'min': 0.53, 'max': 22.6, 'unit': 'g/cm³'}
```

#### `detect_property_pattern(prop_data)`
Detect which pattern is used.

```python
pattern = PropertyAccessor.detect_property_pattern(prop_data)
# Returns: 'simple', 'nested', 'pulse-specific', 'wavelength-specific', or 'unknown'
```

### CategoryHelper Methods

```python
from utils.property_helpers import CategoryHelper

# Get all categories
categories_list = CategoryHelper.get_all_categories(categories_data)
# Returns: ['metal', 'ceramic', 'plastic', ...]

# Get category info
info = CategoryHelper.get_category_info(categories_data, 'metal')

# Get all properties in category
props = CategoryHelper.get_all_properties_in_category(categories_data, 'metal')
# Returns: ['density', 'hardness', 'thermalConductivity', ...]

# Validate value in range
is_valid = CategoryHelper.is_value_in_range(8.96, 0.53, 22.6)
# Returns: True
```

### Convenience Shortcuts

```python
from utils.property_helpers import (
    get_material_property,
    get_category_range,
    is_in_range
)

# Quick property access
value = get_material_property(material, 'density')

# Quick range access
range_data = get_category_range(categories, 'metal', 'density')

# Quick validation
valid = is_in_range(8.96, 0.53, 22.6)
```

---

## Category System

### Category Structure

```yaml
categories:
  metal:
    name: "Metallic Materials"
    description: "Pure metals and metal alloys"
    category_ranges:
      density:
        min: 0.53      # Lithium
        max: 22.6      # Osmium
        unit: "g/cm³"
      thermalDestruction:  # Nested range
        point:
          min: -38.8   # Mercury (melting)
          max: 3422    # Tungsten (melting)
          unit: "°C"
```

### Validation Logic

```python
# Check if material value is in category range
copper_density = 8.96  # g/cm³
metal_range = {'min': 0.53, 'max': 22.6}

if metal_range['min'] <= copper_density <= metal_range['max']:
    print("✅ Valid")
else:
    print("❌ Out of range")

# Or using helper
is_valid = CategoryHelper.is_value_in_range(
    copper_density, 
    metal_range['min'], 
    metal_range['max']
)
```

### All 9 Categories

1. **metal**: Pure metals and alloys (Copper, Steel, Aluminum, etc.)
2. **ceramic**: Ceramic materials (Alumina, Silicon Carbide, etc.)
3. **plastic**: Polymers and plastics (HDPE, PTFE, etc.)
4. **composite**: Composite materials (Carbon Fiber, Fiberglass, etc.)
5. **glass**: Glass materials (Borosilicate, Soda-Lime, etc.)
6. **semiconductor**: Semiconductor materials (Silicon, Gallium Arsenide, etc.)
7. **wood**: Wood materials (Oak, Pine, Bamboo, etc.)
8. **stone**: Stone materials (Granite, Marble, etc.)
9. **masonry**: Masonry materials (Concrete, Brick, etc.)

---

## Research & Validation

### Data Quality Status

**Current State** (as of October 15, 2025):
- ✅ **Priority 1**: 0 violations (18 fixed with 90-95% confidence)
- ⏳ **Priority 2**: 31 violations (10-50% deviation, moderate priority)
- ⏳ **Priority 3**: 7 violations (<5% deviation, low priority)
- 📊 **Total Materials**: 244
- 📊 **Total Categories**: 9
- 📊 **Total Properties**: ~2,750

### Research Tools

#### AI-Powered Research
```bash
python3 scripts/research_range_violations.py \
  --research-all \
  --confidence 0.85 \
  --report RESEARCH_REPORT.md \
  --max-violations 50
```

Features:
- Uses DeepSeek AI for literature research
- Provides confidence scores (0-1)
- Cites authoritative sources (CRC, ASM, NIST, etc.)
- Recommends range expansions or value corrections

#### Automatic Fixes
```bash
python3 scripts/fix_range_violations.py \
  --apply-fixes \
  --backup \
  --report FIX_REPORT.md
```

Features:
- 8 fix rules for common errors
- Decimal corrections (1.23 → 123)
- Unit conversions (mm²/s ↔ m²/s)
- Backup before modifications

#### Validation Tests
```bash
python3 -m pytest tests/test_category_range_compliance.py -v
```

Features:
- Validates all 244 materials
- Checks all property patterns
- Reports violations with details

### Priority System

**Priority 1**: High confidence issues (>50% deviation)
- Fixed with AI research + literature citations
- 90-95% confidence in corrections
- Example: Beryllium thermalDiffusivity 0.07 m²/s → 70 mm²/s (unit error)

**Priority 2**: Moderate deviation (10-50%)
- Requires AI research
- 85-90% confidence target
- Example: Brass oxidationResistance 85°C → 300°C (literature-backed)

**Priority 3**: Minor deviation (<5%)
- Simple range adjustments
- High confidence edges cases
- Example: Expand ranges by 5-10%

---

## Examples

### Example 1: Basic Property Access

```python
import yaml
from utils.property_helpers import PropertyAccessor

# Load data
with open('data/Materials.yaml', 'r') as f:
    materials_data = yaml.safe_load(f)

materials = materials_data['materials']
copper = materials['Copper']

# Simple property
density = PropertyAccessor.get_value(copper['properties']['density'])
print(f"Copper density: {density} g/cm³")

# Nested property
temp = PropertyAccessor.get_thermal_destruction_point(copper)
dtype = PropertyAccessor.get_thermal_destruction_type(copper)
print(f"Copper {dtype}: {temp} K")
```

### Example 2: Validation Against Category Ranges

```python
from utils.property_helpers import PropertyAccessor, CategoryHelper

# Load both files
with open('data/Materials.yaml', 'r') as f:
    materials_data = yaml.safe_load(f)
with open('data/Categories.yaml', 'r') as f:
    categories_data = yaml.safe_load(f)

# Get copper density
copper = materials_data['materials']['Copper']
copper_density = PropertyAccessor.get_value(copper['properties']['density'])

# Get metal category range
density_range = PropertyAccessor.get_category_range(
    categories_data, 'metal', 'density'
)

# Validate
is_valid = CategoryHelper.is_value_in_range(
    copper_density,
    density_range['min'],
    density_range['max']
)

print(f"Copper density: {copper_density} g/cm³")
print(f"Metal range: {density_range['min']}-{density_range['max']} g/cm³")
print(f"Valid: {'✅' if is_valid else '❌'}")
```

### Example 3: Pulse-Specific Access

```python
# Find material with pulse-specific ablation
for material_name, material_data in materials.items():
    ablation = material_data.get('properties', {}).get('ablationThreshold')
    if ablation and 'nanosecond' in ablation:
        # Get for each pulse type
        for pulse_type in ['nanosecond', 'picosecond', 'femtosecond']:
            threshold = PropertyAccessor.get_ablation_threshold(
                material_data,
                pulse_type=pulse_type
            )
            if threshold:
                print(f"{material_name} {pulse_type}: {threshold:.2f} J/cm²")
        break
```

### Example 4: Get All Properties

```python
# Get all properties as flat dict
copper = materials['Copper']
all_values = PropertyAccessor.get_all_property_values(copper)

print(f"All Copper properties:")
for prop_name, value in sorted(all_values.items()):
    print(f"  {prop_name:25} = {value}")
```

### Example 5: Category Exploration

```python
from utils.property_helpers import CategoryHelper

# List all categories
categories = CategoryHelper.get_all_categories(categories_data)
print(f"Categories: {', '.join(categories)}")

# List all properties in metal category
metal_props = CategoryHelper.get_all_properties_in_category(
    categories_data, 'metal'
)
print(f"Metal properties: {', '.join(sorted(metal_props))}")
```

**More Examples**: See `examples/property_access_examples.py` for 9 complete examples.

---

## Troubleshooting

### Issue: "Can't access nested thermalDestruction"

**Problem**: Direct access to nested structure fails
```python
temp = material['properties']['thermalDestruction']['point']['value']
# KeyError if structure missing
```

**Solution**: Use helper method
```python
temp = PropertyAccessor.get_thermal_destruction_point(material)
# Returns None if missing, no exception
```

### Issue: "Don't know which pulse type to use"

**Problem**: Need to handle all pulse types
```python
ablation = material['properties']['ablationThreshold']
# Which key? nanosecond? picosecond? femtosecond?
```

**Solution**: Loop or specify
```python
for pulse_type in ['nanosecond', 'picosecond', 'femtosecond']:
    threshold = PropertyAccessor.get_ablation_threshold(
        material, pulse_type=pulse_type
    )
    if threshold:
        print(f"{pulse_type}: {threshold}")
```

### Issue: "Not sure what pattern a property uses"

**Problem**: Need to detect pattern before processing

**Solution**: Use pattern detection
```python
pattern = PropertyAccessor.detect_property_pattern(prop_data)
if pattern == 'pulse-specific':
    # Handle pulse types
elif pattern == 'wavelength-specific':
    # Handle wavelengths
else:
    # Simple access
    value = PropertyAccessor.get_value(prop_data)
```

### Issue: "Range validation fails unexpectedly"

**Problem**: Not handling nested category ranges

**Solution**: Use get_category_range helper
```python
# Handles nested thermalDestruction automatically
thermal_range = PropertyAccessor.get_category_range(
    categories, 'metal', 'thermalDestruction'
)
# Returns: {'min': -38.8, 'max': 3422, 'unit': '°C'}
```

### Issue: "Want to validate all materials programmatically"

**Solution**: Use validation test suite
```python
# Run existing tests
python3 -m pytest tests/test_category_range_compliance.py -v

# Or write custom validation
for material_name, material_data in materials.items():
    for prop_name, prop_data in material_data['properties'].items():
        value = PropertyAccessor.get_value(prop_data)
        range_data = PropertyAccessor.get_category_range(
            categories, material_category, prop_name
        )
        if range_data:
            is_valid = CategoryHelper.is_value_in_range(
                value, range_data['min'], range_data['max']
            )
            if not is_valid:
                print(f"❌ {material_name}.{prop_name}: {value}")
```

---

## Architecture Decision Record

**Date**: October 15, 2025  
**Decision**: Hybrid Approach - Add convenience helpers while preserving powerful architecture  
**Status**: ✅ Implemented

### Context
After achieving zero Priority 1 violations (18 research-backed fixes), we evaluated whether to simplify the data architecture for ease of use.

### Options Considered
1. **Keep as-is**: Maintain current architecture
2. **Flatten nested**: Simplify nested structures
3. **Unify patterns**: Single pattern for all properties
4. **Hybrid**: Add helpers, keep architecture ✅ CHOSEN

### Decision
Implemented Option 4 (Hybrid Approach):
- ✅ Created `utils/property_helpers.py` with `PropertyAccessor` and `CategoryHelper`
- ✅ Created `examples/property_access_examples.py` with 9 complete examples
- ✅ Created `tests/test_property_helpers.py` with 23 passing tests
- ✅ Consolidated documentation into this guide
- ✅ Zero breaking changes
- ✅ Preserves all advanced features

### Benefits
- **Convenience**: Simple access via helpers
- **Power**: All 4 patterns still supported
- **Safety**: Graceful handling of missing data
- **Documentation**: Complete guide with examples
- **Testing**: 23 tests validate all patterns
- **Backward Compatible**: Existing code works unchanged

### Implementation Time
**3.5 hours** (within estimated 3-4 hours)

---

## Related Documentation

- `DATA_ARCHITECTURE.md` - Original architecture design (now superseded by this guide)
- `DATA_ACCURACY_RESEARCH_PLAN.md` - Research methodology and priorities
- `PRIORITY1_RESEARCH_REPORT.md` - AI research results for 18 Priority 1 violations
- `PRIORITY1_FIXES_COMPLETE.md` - Documentation of all Priority 1 fixes
- `DATA_ARCHITECTURE_EVALUATION.md` - Evaluation that led to this implementation
- `docs/QUICK_REFERENCE.md` - Quick reference for common operations

---

## Next Steps

**Option A: Continue with Priority 2 Violations**
```bash
python3 scripts/research_range_violations.py \
  --research-all \
  --confidence 0.85 \
  --report PRIORITY2_RESEARCH_REPORT.md \
  --max-violations 31
```

**Option B: Enhance Helpers Further**
- Add batch validation methods
- Create migration tools for old code
- Add property comparison utilities

**Option C: Documentation Polish**
- Add architecture diagrams
- Create interactive Jupyter notebooks
- Record video tutorials

---

**Questions?** See `docs/QUICK_REFERENCE.md` or run `python3 examples/property_access_examples.py`
