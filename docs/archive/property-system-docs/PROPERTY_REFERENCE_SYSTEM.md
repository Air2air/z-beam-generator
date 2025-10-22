# Property Reference System

**Version**: 2.0  
**Last Updated**: October 19, 2025  
**Status**: ✅ IMPLEMENTED

---

## 📋 Overview

The Property Reference System provides a centralized, authoritative source for all material properties across categories. It eliminates property definition duplication and ensures consistency between validation, research, and generation systems.

---

## 🎯 Problem Solved

### Before (Fragmented):
- ❌ Essential properties defined in 5+ different files
- ❌ Validation expects `laserReflectivity`, code uses `reflectivity`
- ❌ Property names inconsistent across components
- ❌ No single source of truth

### After (Centralized):
- ✅ Single property registry: `utils/category_property_cache.py`
- ✅ Property aliases resolved automatically
- ✅ Consistent names across all components
- ✅ Validation, research, and generation use same definitions

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                PROPERTY REFERENCE SYSTEM                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  utils/category_property_cache.py (SINGLE SOURCE)    │  │
│  │  • Loads from Categories.yaml                        │  │
│  │  • Caches valid properties per category              │  │
│  │  • Provides property aliases                         │  │
│  │  • Returns authoritative property sets               │  │
│  └──────────────────────────────────────────────────────┘  │
│                        │                                     │
│            ┌───────────┼───────────┐                        │
│            ▼           ▼           ▼                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │Validation│  │ Research │  │Generation│                 │
│  │  System  │  │  System  │  │  System  │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Property Categories

### Universal Properties (All Materials)
```python
{
    'thermalConductivity',
    'density',
    'hardness',
    'laserReflectivity'  # Note: Not 'reflectivity'
}
```

### Category-Specific Essential Properties

#### Metal
```python
{
    'thermalDestruction',      # Not 'meltingPoint'
    'thermalConductivity',
    'density',
    'hardness',
    'ablationThreshold',
    'absorptionCoefficient',
    'elasticModulus',
    'laserReflectivity'
}
```

#### Ceramic
```python
{
    'thermalDestruction',      # Not 'sinteringPoint'
    'thermalConductivity',
    'density',
    'hardness'
}
```

#### Plastic
```python
{
    'thermalDestruction',      # Not 'degradationPoint'
    'thermalConductivity',
    'density'
}
```

#### Composite
```python
{
    'thermalDestruction',
    'thermalConductivity',
    'density'
}
```

#### Glass
```python
{
    'thermalDestruction',      # Not 'softeningPoint'
    'thermalConductivity',
    'density'
}
```

---

## 🔄 Property Aliases

The system automatically resolves property name variations:

```python
PROPERTY_ALIASES = {
    'reflectivity': 'laserReflectivity',
    'meltingPoint': 'thermalDestruction',
    'sinteringPoint': 'thermalDestruction',
    'degradationPoint': 'thermalDestruction',
    'softeningPoint': 'thermalDestruction',
    'thermalDegradationPoint': 'thermalDestruction',
    'thermalDestructionPoint': 'thermalDestruction'
}
```

**Example**:
```python
# User requests 'reflectivity'
# System automatically translates to 'laserReflectivity'
# Both names work, but internally consistent
```

---

## 🛠️ Usage

### Loading Property Definitions

```python
from utils.category_property_cache import get_category_property_cache

# Get cache instance
cache = get_category_property_cache()

# Load valid properties per category
valid_properties = cache.load()

# Example result:
# {
#     'metal': {'density', 'thermalConductivity', 'hardness', ...},
#     'ceramic': {'density', 'thermalConductivity', 'hardness', ...},
#     'plastic': {'density', 'thermalConductivity', ...}
# }
```

### Validation Example

```python
# Validate property is applicable to category
material_category = 'metal'
property_name = 'ablationThreshold'

valid_props = valid_properties.get(material_category, set())

if property_name not in valid_props:
    print(f"⚠️ {property_name} not applicable to {material_category}")
else:
    print(f"✅ {property_name} is valid for {material_category}")
```

### Research Example

```python
# Only research properties that are valid for material's category
material_name = "Aluminum"
material_category = "metal"

valid_props = valid_properties.get(material_category, set())
existing_props = get_material_properties(material_name)

# Find missing properties (only valid ones)
missing_props = valid_props - set(existing_props.keys())

# Research only valid missing properties
for prop in missing_props:
    research_property(material_name, prop)
```

---

## 📁 File Locations

### Primary Source
- **`data/Categories.yaml`** - Authoritative property definitions per category

### Property Cache
- **`utils/category_property_cache.py`** - Loads and caches property definitions
- **`.category_property_cache.json`** - Generated cache file (auto-created)

### Essential Properties (Deprecated - Use Cache)
- ~~`components/frontmatter/services/property_manager.py`~~ - Now uses cache
- ~~`components/frontmatter/validation/completeness_validator.py`~~ - Now uses cache
- ~~`components/frontmatter/services/property_discovery_service.py`~~ - Now uses cache

---

## 🧪 Testing

### Unit Tests
```bash
# Test property cache loading
python3 -m pytest tests/test_category_property_cache.py

# Test property validation
python3 -m pytest tests/test_property_validation.py

# Test property aliases
python3 -m pytest tests/test_property_aliases.py
```

### Integration Tests
```bash
# Test full validation pipeline
python3 run.py --test

# Test with specific material
python3 run.py --material "Aluminum"
```

---

## 🔧 Maintenance

### Adding a New Property

1. **Update Categories.yaml**:
```yaml
categories:
  metal:
    category_ranges:
      newProperty:
        min: 0
        max: 100
        unit: "unit"
```

2. **Clear cache** (auto-regenerates):
```bash
rm .category_property_cache.json
```

3. **Verify**:
```python
from utils.category_property_cache import get_category_property_cache
cache = get_category_property_cache()
props = cache.load()
assert 'newProperty' in props['metal']
```

### Adding a Property Alias

Update `PROPERTY_ALIASES` in `utils/category_property_cache.py`:
```python
PROPERTY_ALIASES = {
    'oldName': 'newName',
    # Add new alias here
}
```

---

## 🚨 Common Issues & Solutions

### Issue 1: "Property not found in Materials.yaml"
**Cause**: Property exists but validator doesn't recognize it  
**Solution**: Check if property name is in category's valid properties set

```python
valid_props = cache.load()
category = 'metal'
print(f"Valid properties for {category}: {valid_props[category]}")
```

### Issue 2: "Empty materialProperties section"
**Cause**: Property structure doesn't match expected format  
**Solution**: Ensure Materials.yaml uses correct structure:

```yaml
Aluminum:
  category: metal
  properties:  # Not 'materialProperties'
    density:
      value: 2.7
      unit: "g/cm³"
```

### Issue 3: "Missing essential property X"
**Cause**: Property name mismatch (e.g., `reflectivity` vs `laserReflectivity`)  
**Solution**: Use property aliases or update to canonical name

```python
# Check alias
from utils.category_property_cache import PROPERTY_ALIASES
canonical_name = PROPERTY_ALIASES.get('reflectivity', 'reflectivity')
print(f"Canonical name: {canonical_name}")  # → 'laserReflectivity'
```

---

## 📊 Statistics

Current system coverage (October 19, 2025):

| Category      | Properties Defined | Essential Properties | Total Materials |
|---------------|-------------------|---------------------|-----------------|
| metal         | 42                | 8                   | 45              |
| ceramic       | 38                | 4                   | 12              |
| plastic       | 28                | 3                   | 18              |
| composite     | 35                | 3                   | 10              |
| glass         | 32                | 3                   | 9               |
| wood          | 25                | 2                   | 6               |
| stone         | 30                | 3                   | 8               |
| semiconductor | 40                | 4                   | 5               |
| masonry       | 28                | 3                   | 4               |

---

## 🔗 Related Documentation

- **[UNIT_CONVERSION.md](./UNIT_CONVERSION.md)** - Unit normalization system
- **[DATA_ARCHITECTURE.md](./DATA_ARCHITECTURE.md)** - Overall data structure
- **[PROPERTY_ALIAS_SYSTEM.md](./PROPERTY_ALIAS_SYSTEM.md)** - Alias resolution details
- **[VALIDATION_ARCHITECTURE.md](./VALIDATION_ARCHITECTURE.md)** - Validation system

---

## ✅ Best Practices

1. **Always use category property cache** - Don't hardcode property lists
2. **Check property aliases** - Support both old and new names
3. **Validate category applicability** - Don't assume all properties apply to all categories
4. **Use canonical names** - Store using `laserReflectivity`, not `reflectivity`
5. **Test with real data** - Verify against actual Materials.yaml entries

---

**Last Updated**: October 19, 2025  
**Maintainer**: Z-Beam Generator Team  
**Status**: ✅ Production Ready
