# Data Structure Documentation

Complete guide to the Z-Beam Generator data organization, focusing on the flattened materials.yaml structure.

## Overview

**Version**: 2.0 (Flattened Architecture)  
**Migration Date**: October 2, 2025  
**Total Materials**: 121 across 9 categories

## Quick Navigation

- [Flattened Structure](#flattened-structure) - Current data organization
- [Migration Guide](#migration-guide) - How we got here
- [Access Patterns](#access-patterns) - How to use the data
- [Category System](#category-system) - Material categorization
- [Data Validation](#data-validation) - Quality assurance

## Flattened Structure

### Overview

Materials are now organized as a flat dictionary with direct O(1) access instead of nested navigation.

**Key Change**: `materials['Aluminum']` instead of `materials[category]['items'][index]`

### File Location

`data/materials.yaml`

### Top-Level Structure

```yaml
metadata:
  version: "2.0"
  lastUpdated: "2025-10-02"
  totalMaterials: 121

category_metadata:
  metal:
    article_type: material
    description: Metal materials for laser cleaning applications
  wood:
    article_type: material
    description: Wood materials for laser cleaning applications
  # ... 7 more categories

machineSettingsRanges:
  powerRange:
    min: 1.0
    max: 120
    unit: W
  wavelength:
    min: 355
    max: 10640
    unit: nm
  # ... more ranges

property_groups:
  # Shared property definitions

materials:
  # FLAT DICTIONARY - Direct material access
  Aluminum:
    name: Aluminum
    category: metal  # Category embedded in material
    properties: {...}
    mechanicalProperties: {...}
    thermalProperties: {...}
    electricalProperties: {...}
    material_metadata: {...}
    author: {...}
  
  Copper:
    name: Copper
    category: metal
    properties: {...}
    # ... full material data
  
  # ... 121 materials total

material_index:
  # Kept for backward compatibility and quick category lookup
  Aluminum: metal
  Copper: metal
  Oak: wood
  Granite: stone
  # ... all 121 materials
```

### Material Object Structure

Each material has this structure:

```yaml
MaterialName:
  name: "MaterialName"
  category: "metal"  # Category embedded directly
  
  properties:
    density: 2.7
    hardness: 2.75
    corrosionResistance: "high"
    # ... more properties
  
  mechanicalProperties:
    tensileStrength: 310
    yieldStrength: 276
    elongation: 12
    # ... more mechanical properties
  
  thermalProperties:
    meltingPoint: 660
    thermalConductivity: 205
    thermalExpansion: 23.1
    # ... more thermal properties
  
  electricalProperties:
    conductivity: 37.7
    resistivity: 2.65e-8
    # ... more electrical properties
  
  material_metadata:
    common_name: "Aluminum"
    alternative_names: ["Aluminium"]
    category: "metal"
    subcategory: "light-metal"
    cas_number: "7429-90-5"
  
  author:
    id: 1
    name: "author-name"
```

## Migration Guide

### What Changed

**Before (Nested Structure)**:
```yaml
materials:
  metal:
    items:
      - name: Aluminum
        category: metal
        properties: {...}
      - name: Copper
        category: metal
        properties: {...}
  wood:
    items:
      - name: Oak
        properties: {...}
```

**After (Flat Structure)**:
```yaml
materials:
  Aluminum:
    name: Aluminum
    category: metal  # Embedded
    properties: {...}
  Copper:
    name: Copper
    category: metal
    properties: {...}
  Oak:
    name: Oak
    category: wood
    properties: {...}
```

### Migration Process

**Automated Script**: `scripts/tools/flatten_materials_structure.py`

```bash
# Flatten with automatic backup
python3 scripts/tools/flatten_materials_structure.py

# Show before/after comparison
python3 scripts/tools/flatten_materials_structure.py --show-comparison

# Flatten to different file
python3 scripts/tools/flatten_materials_structure.py -o materials_flat.yaml
```

**Backup Created**: `data/materials.yaml.backup.20251002_141324`

### Code Changes Required

**Old Code** (nested access):
```python
# Two-step lookup
category = material_index['Aluminum']  # Step 1
items = materials[category]['items']   # Step 2
material = next(item for item in items if item['name'] == 'Aluminum')  # Step 3
```

**New Code** (direct access):
```python
# Single-step lookup
material = materials['Aluminum']
category = material['category']
```

### Files Updated

1. **data/materials.py** - Simplified by 129 lines
   - `load_materials()` - Now returns flat structure
   - `get_material_by_name()` - Direct dict lookup
   - `find_material_case_insensitive()` - Simplified iteration

2. **All component generators** - Updated to use flat access
   - Frontmatter generator
   - Text generator
   - Caption generator
   - Tags generator

## Access Patterns

### Basic Lookup

```python
from data.materials import load_materials

# Load materials
data = load_materials()

# Direct access by name
aluminum = data['materials']['Aluminum']
print(aluminum['category'])  # 'metal'
print(aluminum['properties']['density'])  # 2.7

# Get all materials
all_materials = data['materials'].keys()  # dict_keys(['Aluminum', 'Copper', ...])
```

### Case-Insensitive Lookup

**ALL material lookups are case-insensitive throughout the system.**

```python
from data.materials import get_material_by_name

# All case variations work identically
material = get_material_by_name('aluminum')   # ✅ lowercase
material = get_material_by_name('ALUMINUM')   # ✅ uppercase
material = get_material_by_name('Aluminum')   # ✅ proper case
material = get_material_by_name('AlUmInUm')   # ✅ mixed case

# Command-line is also case-insensitive
# python3 run.py --material "steel"     ✅
# python3 run.py --material "Steel"     ✅
# python3 run.py --material "STEEL"     ✅
```

### Find by Category

```python
from data.materials import load_materials

data = load_materials()
materials = data['materials']

# Get all metals
metals = [
    name for name, mat_data in materials.items()
    if mat_data['category'] == 'metal'
]

# Count materials per category
from collections import Counter
categories = Counter(mat['category'] for mat in materials.values())
print(categories)  # {'metal': 35, 'wood': 20, 'stone': 18, ...}
```

### Iterate All Materials

```python
from data.materials import load_materials

data = load_materials()

# Iterate all materials
for name, material_data in data['materials'].items():
    print(f"{name}: {material_data['category']}")
    print(f"  Density: {material_data['properties']['density']}")
```

## Category System

### Available Categories

| Category | Count | Examples |
|----------|-------|----------|
| metal | 35 | Aluminum, Copper, Steel, Titanium |
| wood | 20 | Oak, Pine, Mahogany, Bamboo |
| stone | 18 | Granite, Marble, Limestone, Slate |
| composite | 13 | Carbon Fiber, Fiberglass, Kevlar |
| glass | 11 | Borosilicate, Tempered, Crown |
| ceramic | 9 | Alumina, Zirconia, Silicon Nitride |
| masonry | 7 | Brick, Concrete, Stucco |
| plastic | 6 | HDPE, PVC, Polystyrene |
| semiconductor | 4 | Silicon, GaAs, Silicon Carbide |

### Category Metadata

```yaml
category_metadata:
  metal:
    article_type: material
    description: Metal materials for laser cleaning applications
    typical_properties:
      - High thermal conductivity
      - Electrically conductive
      - High density
  
  wood:
    article_type: material
    description: Wood materials for laser cleaning applications
    typical_properties:
      - Organic composition
      - Variable density
      - Anisotropic properties
  
  # ... 7 more categories
```

## Data Validation

### Validation Rules

**Enforced by**: `scripts/validation/fail_fast_materials_validator.py`

1. **Structural Requirements**
   - Materials must be flat dictionary
   - Each material must have `name` and `category`
   - Categories must match `material_index`

2. **Property Requirements**
   - Flexible property count based on material complexity
   - All property values must be explicit (no defaults)
   - All values must have sources (ai_research)

3. **Uniqueness Requirements**
   - Material names must be unique
   - Each property set should be unique (no copy-paste)

4. **Quality Requirements**
   - No forbidden default values
   - No mock data or placeholders
   - All sources must be "ai_research"

### Running Validation

```bash
# Validate materials database
python3 scripts/validation/validate_materials.py

# Check for forbidden defaults
python3 scripts/validation/fail_fast_materials_validator.py

# Validate specific material
python3 -c "
from data.materials import get_material_by_name
mat = get_material_by_name('Aluminum')
print('Valid:', 'properties' in mat and len(mat['properties']) >= 5)
"
```

## Material Properties

### Standard Properties

Every material has these property groups:

```yaml
properties:
  density: number  # g/cm³
  hardness: number  # Mohs or similar
  corrosionResistance: string  # low/medium/high
  surfaceTexture: string  # rough/smooth/polished
  # ... more properties

mechanicalProperties:
  tensileStrength: number  # MPa
  yieldStrength: number  # MPa
  elongation: number  # %
  modulusOfElasticity: number  # GPa
  # ... more properties

thermalProperties:
  meltingPoint: number  # °C
  thermalConductivity: number  # W/m·K
  thermalExpansion: number  # 10⁻⁶/K
  specificHeat: number  # J/kg·K
  # ... more properties

electricalProperties:
  conductivity: number  # MS/m
  resistivity: number  # Ω·m
  dielectricConstant: number  # unitless
  # ... more properties (if applicable)
```

### Property Sources

All properties are AI-researched and validated:

```yaml
properties:
  density:
    value: 2.7
    unit: "g/cm³"
    source: "ai_research"
    confidence: "high"
```

## Best Practices

### DO ✅

1. **Use `get_material_by_name()`** for lookups (handles case)
2. **Check category** before assuming properties
3. **Validate material exists** before accessing
4. **Use embedded category** instead of index lookup
5. **Iterate materials.items()** for all materials

### DON'T ❌

1. **Don't assume nested structure** (old format)
2. **Don't modify material_index** (auto-generated)
3. **Don't hardcode material names** (iterate instead)
4. **Don't skip validation** before accessing properties
5. **Don't create duplicate materials** (check first)

## Example Code

### Complete Material Access

```python
from data.materials import load_materials, get_material_by_name

# Method 1: Direct access
data = load_materials()
aluminum = data['materials']['Aluminum']

# Method 2: Case-insensitive lookup (recommended)
aluminum = get_material_by_name('aluminum')

# Access properties
print(f"Name: {aluminum['name']}")
print(f"Category: {aluminum['category']}")
print(f"Density: {aluminum['properties']['density']} g/cm³")
print(f"Melting Point: {aluminum['thermalProperties']['meltingPoint']}°C")

# Check if property exists
if 'electricalProperties' in aluminum:
    conductivity = aluminum['electricalProperties']['conductivity']
    print(f"Conductivity: {conductivity} MS/m")
```

### Filter Materials by Criteria

```python
from data.materials import load_materials

data = load_materials()
materials = data['materials']

# Find high-conductivity materials
high_conductivity = [
    name for name, mat in materials.items()
    if 'electricalProperties' in mat
    and mat['electricalProperties'].get('conductivity', 0) > 30
]

print(f"High conductivity materials: {high_conductivity}")
```

## Troubleshooting

### Common Issues

**1. KeyError: 'items'**
```python
# OLD CODE (broken)
materials['metal']['items']  # ❌ No 'items' in flat structure

# NEW CODE (correct)
[m for m in materials.values() if m['category'] == 'metal']  # ✅
```

**2. Material Not Found**
```python
# Check if material exists
from data.materials import get_material_by_name

try:
    material = get_material_by_name('NonExistent')
except ValueError as e:
    print(f"Material not found: {e}")
```

**3. Category Mismatch**
```python
# Verify category matches
material = get_material_by_name('Aluminum')
index_category = data['material_index']['Aluminum']
embedded_category = material['category']
assert index_category == embedded_category  # Should always be true
```

## See Also

- [System Architecture](SYSTEM_ARCHITECTURE.md) - Overall system design
- [Materials.py Reference](../../data/materials.py) - Python access layer
- [Migration Script](../../scripts/tools/flatten_materials_structure.py) - Flattening tool
- [Validation Guide](../operations/VALIDATION.md) - Quality assurance
