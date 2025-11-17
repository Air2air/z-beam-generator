# Materials.yaml Structure - CANONICAL REFERENCE

**Date:** November 3, 2025  
**Authority:** `materials/data/frontmatter_template.yaml`  
**Status:** Enforced via validation and migration scripts

---

## ⚠️ CRITICAL: No 'properties' Wrapper!

Properties are stored **DIRECTLY** under category groups, NOT nested under a `properties` key.

### ❌ WRONG (causes bugs):
```yaml
materialProperties:
  material_characteristics:
    label: "Material Characteristics"
    properties:  # ❌ NO! This wrapper should NOT exist
      density:
        value: 8.8
        unit: "g/cm³"
```

### ✅ CORRECT (canonical structure):
```yaml
materialProperties:
  material_characteristics:
    label: "Material Characteristics"
    density:  # ✅ Properties are DIRECTLY here
      value: 8.8
      unit: "g/cm³"
    porosity:
      value: 0.5
      unit: "%"
  
  laser_material_interaction:
    label: "Laser-Material Interaction"
    thermalConductivity:  # ✅ Properties are DIRECTLY here
      value: 109.0
      unit: "W/(m·K)"
```

---

## Structure Hierarchy

```
materials:
  MaterialName:
    materialProperties:
      material_characteristics:
        label: "..."              # Metadata
        <propertyName>:           # ← Property DIRECTLY here
          value: <number>
          unit: "<string>"
          min: <number>
          max: <number>
          research_basis: "ai_research"
      
      laser_material_interaction:
        label: "..."              # Metadata
        <propertyName>:           # ← Property DIRECTLY here
          value: <number>
          unit: "<string>"
          min: <number>
          max: <number>
          research_basis: "ai_research"
```

---

## Accessing Properties in Code

### ✅ CORRECT:
```python
mat_props = material_data['materialProperties']
mc = mat_props['material_characteristics']

# Get property directly from category group
density = mc.get('density')  # ✅ CORRECT
if density:
    value = density.get('value')
```

### ❌ WRONG (old nested structure):
```python
mc = mat_props['material_characteristics']

# Do NOT look for 'properties' wrapper
mc_props = mc.get('properties', {})  # ❌ WRONG!
density = mc_props.get('density')     # ❌ WRONG!
```

---

## Metadata Keys (Not Properties)

These keys exist alongside properties but are NOT property data:

- `label` - Display name for the category group
- `description` - Category description (optional)
- `percentage` - Legacy field (being removed)

### Filtering Metadata:
```python
# Get only actual property keys
property_keys = [
    k for k in mc.keys() 
    if k not in ['label', 'description', 'percentage']
]
```

---

## Property Schema

Each property follows this structure:

```yaml
propertyName:
  value: <number>           # Required: actual value
  unit: "<string>"          # Required: unit of measurement
  min: <number>             # Optional: min value from category ranges
  max: <number>             # Optional: max value from category ranges
  research_basis: "ai_research"  # Required: source
  confidence: <0-100>       # Optional: confidence score
```

---

## Validation Rules

1. **No 'properties' wrapper** - Properties must be directly under category groups
2. **Metadata keys excluded** - `label`, `description`, `percentage` are not properties
3. **Required structure** - Both category groups must exist (can be empty)
4. **Property format** - Each property must have `value` and `unit` keys

---

## Migration

If you find materials with the nested `properties` structure:

```bash
python3 scripts/tools/flatten_properties_structure.py
```

This script:
- Finds all materials with `properties` wrapper
- Moves properties up one level (flattens)
- Removes the `properties` key
- Creates backup before modifying

---

## Testing

Validate structure compliance:

```bash
# Check specific material
python3 -c "
import yaml
with open('materials/data/materials.yaml') as f:
    data = yaml.safe_load(f)
    
bronze = data['materials']['Bronze']
mc = bronze['materialProperties']['material_characteristics']

# Should NOT have 'properties' key
assert 'properties' not in mc, 'ERROR: Has properties wrapper!'

# Should have properties directly
assert 'density' in mc, 'ERROR: Missing density property!'
print('✅ Structure valid')
"
```

---

## References

- **Template:** `materials/data/frontmatter_template.yaml` (lines 63-97)
- **Migration:** `scripts/tools/flatten_properties_structure.py`
- **Validation:** `materials/validation/completeness_validator.py`
- **Research:** `shared/commands/research.py` (lines 310-327)
- **Tests:** `tests/test_materials_validation.py`

---

## Change History

- **2025-11-03:** Created canonical documentation, fixed research.py and tests
- **2025-11-03:** Created migration script to flatten 5 materials with nested structure
- **2025-11-02:** Attempted normalization (incorrectly used nested structure)

---

## For AI Assistants

When working with Materials.yaml:

1. **ALWAYS** check this document first
2. **NEVER** assume properties are nested under a `properties` key
3. **ALWAYS** access properties directly: `mc.get('density')`
4. **NEVER** use: `mc.get('properties', {}).get('density')`
5. **ALWAYS** exclude metadata keys when counting properties
6. **Reference** `frontmatter_template.yaml` as the single source of truth
