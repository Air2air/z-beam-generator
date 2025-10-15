# Data Architecture: Categories → Materials → Frontmatter

## Overview
This document clarifies the **correct** data flow and range propagation through the Z-Beam Generator system.

**Last Updated**: October 14, 2025  
**Status**: ✅ System working correctly as of this date

---

## Three Types of Ranges

The system uses three distinct types of min/max ranges:

### 1. Category Ranges (Categories.yaml)
**Location**: `data/Categories.yaml → categories.[category_name].category_ranges`

**Purpose**: Provide **comparison context** showing where a specific material falls within its category.

**Scope**: Wide ranges spanning all materials in a category.

**Example**:
```yaml
categories:
  metal:
    category_ranges:
      density:
        min: 0.53      # Lithium (lightest metal)
        max: 22.6      # Osmium (densest metal)
        unit: g/cm³
```

**Properties with category ranges**: 12 properties across 9 categories
- `density`, `hardness`, `laserAbsorption`, `laserReflectivity`
- `specificHeat`, `tensileStrength`, `thermalConductivity`
- `thermalDestructionPoint`, `thermalDestructionType`
- `thermalDiffusivity`, `thermalExpansion`, `youngsModulus`

**Categories**: ceramic, composite, glass, masonry, metal, plastic, semiconductor, stone, wood

---

### 2. Material-Specific Tolerance Ranges (materials.yaml)
**Location**: `data/materials.yaml → materials.[material_name].properties.[property_name]`

**Purpose**: Represent **material variance** due to purity, measurement uncertainty, or grade variations.

**Scope**: Narrow ranges specific to individual materials.

**Example**:
```yaml
materials:
  Copper:
    properties:
      density:
        value: 8.96
        min: 8.89     # -0.07 tolerance (purity variance)
        max: 8.96     # Pure copper upper bound
        unit: g/cm³
```

**Count**: 1,332 material-specific tolerance ranges across 122 materials

**NOT used in frontmatter** - These stay in materials.yaml as reference data.

---

### 3. Category Duplicates (materials.yaml - ERROR)
**Location**: `data/materials.yaml → materials.[material_name].properties.[property_name]`

**Status**: ⚠️ **Data quality issue** - 8 instances found

**Problem**: Some material properties incorrectly duplicate exact category ranges.

**Example of ERROR**:
```yaml
materials:
  Alumina:
    properties:
      hardness:
        value: 9.0
        min: 1.0      # ❌ Exact match to ceramic category min
        max: 10.0     # ❌ Exact match to ceramic category max
```

**Action needed**: These 8 duplicates should be removed or replaced with material-specific tolerances.

**Found in**:
- Alumina (ceramic) - hardness
- Titanium Carbide (ceramic) - hardness
- Tungsten Carbide (ceramic) - hardness
- Fiberglass (composite) - thermalConductivity
- GFRP (composite) - thermalDiffusivity
- Beryllium (metal) - specificHeat
- Iridium (metal) - laserReflectivity
- Silicon Carbide (semiconductor) - youngsModulus

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. Categories.yaml (Authoritative Source for Category Ranges)      │
│    categories.[category].category_ranges                            │
│    • 9 categories × 12 properties = 108 category range definitions  │
│    • Purpose: Comparison context across category                    │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 2. materials.yaml (Material-Specific Data)                          │
│    materials.[material].properties                                   │
│    • 122 materials with properties                                   │
│    • Each property has: value, unit, confidence, description        │
│    • Some have min/max (material-specific tolerances)               │
│    • Category: Links to Categories.yaml category                    │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 3. StreamlinedGenerator (Combines Data)                             │
│    components/frontmatter/core/streamlined_generator.py              │
│    • Loads Categories.yaml → self.category_ranges                   │
│    • Loads materials.yaml → material properties                     │
│    • Calls _get_category_ranges_for_property()                      │
│    • Injects category ranges into property min/max                  │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 4. Frontmatter YAML Output                                          │
│    content/components/frontmatter/[material]-laser-cleaning.yaml    │
│    materialProperties:                                               │
│      physical_structural:                                            │
│        properties:                                                   │
│          density:                                                    │
│            value: 8.96     ← From materials.yaml                    │
│            min: 0.53       ← From Categories.yaml (metal range)     │
│            max: 22.6       ← From Categories.yaml (metal range)     │
│            unit: g/cm³                                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Critical Design Principles

### ✅ CORRECT Behavior

1. **Frontmatter min/max = Category ranges ONLY**
   - Frontmatter shows where material falls within its category
   - Example: Copper (8.96) sits mid-range in metals (0.53-22.6)
   - Provides meaningful comparison context

2. **Material-specific tolerances stay in materials.yaml**
   - These represent measurement uncertainty/purity variance
   - Not propagated to frontmatter
   - Used for internal data validation only

3. **Generator ignores material min/max**
   - `_get_category_ranges_for_property()` reads from Categories.yaml only
   - Lines 1460-1480 in streamlined_generator.py
   - Never reads min/max from materials.yaml properties

4. **Null ranges are correct**
   - If a property has no category range defined, min/max = null
   - Example: `compressiveStrength` not in masonry category_ranges
   - This is **intentional**, not an error

### ❌ INCORRECT Behavior (Previously Fixed)

1. **Reading ranges from materials.yaml** - WRONG
   - Would give material-specific tolerances instead of category context
   - Fixed on Oct 14, 2025

2. **Assuming null ranges are errors** - WRONG
   - Not all properties have category ranges (by design)
   - Only 12 properties out of 55+ total have category ranges

3. **Copying category ranges to materials.yaml** - WRONG
   - Creates data duplication and confusion
   - 8 instances found and marked for cleanup

---

## Code Implementation

### Generator Loading (Lines 279-334)

```python
# Load Categories.yaml
with open(categories_file, 'r', encoding='utf-8') as f:
    cat_data = yaml.safe_load(f)
    if 'categories' in cat_data:
        for category_name, category_info in cat_data['categories'].items():
            # Store category_ranges for later use
            if 'category_ranges' in category_info:
                self.category_ranges[category_name] = category_info['category_ranges']
```

### Range Injection (Lines 657-677)

```python
# Create property with value from materials.yaml
properties[prop_name] = {
    'value': yaml_prop.get('value'),      # Material-specific value
    'unit': yaml_prop.get('unit', ''),
    'confidence': int(confidence * 100),
    'description': yaml_prop.get('description'),
    'min': None,                           # Will be populated from category ranges
    'max': None                            # Will be populated from category ranges
}

# Get category ranges from Categories.yaml (NOT materials.yaml)
category_ranges = self._get_category_ranges_for_property(
    material_data.get('category'), 
    prop_name
)
if category_ranges:
    properties[prop_name]['min'] = category_ranges.get('min')
    properties[prop_name]['max'] = category_ranges.get('max')
```

### Category Range Lookup (Lines 1460-1480)

```python
def _get_category_ranges_for_property(self, category: str, property_name: str) -> Optional[Dict]:
    """Get min/max ranges for a property from Categories.yaml category_ranges"""
    try:
        if not category or category not in self.category_ranges:
            return None
            
        category_ranges = self.category_ranges[category]
        
        if property_name in category_ranges:
            ranges = category_ranges[property_name]
            if 'min' in ranges and 'max' in ranges:
                if 'unit' not in ranges:
                    self.logger.warning(f"Unit missing for {category}.{property_name}")
                    return None  # Fail-fast
                return {
                    'min': ranges['min'],
                    'max': ranges['max'],
                    'unit': ranges['unit']
                }
        
        return None
    except Exception as e:
        self.logger.error(f"Error getting category ranges: {e}")
        return None
```

**Key Points**:
- Reads from `self.category_ranges[category]` (loaded from Categories.yaml)
- **Never** accesses `materials.yaml` property min/max
- Returns `None` if no category range exists (correct behavior)
- Fail-fast if unit missing (no fallback defaults)

---

## Examples

### Example 1: Copper Density (Correct)

**Categories.yaml (metal category)**:
```yaml
category_ranges:
  density:
    min: 0.53      # Lithium
    max: 22.6      # Osmium
    unit: g/cm³
```

**materials.yaml**:
```yaml
Copper:
  category: metal
  properties:
    density:
      value: 8.96                    # Pure copper value
      min: 8.89                      # Material-specific tolerance (NOT used in frontmatter)
      max: 8.96                      # Material-specific tolerance (NOT used in frontmatter)
      unit: g/cm³
```

**Frontmatter Output** (copper-laser-cleaning.yaml):
```yaml
materialProperties:
  physical_structural:
    properties:
      density:
        value: 8.96    # From materials.yaml
        min: 0.53      # From Categories.yaml (metal range)
        max: 22.6      # From Categories.yaml (metal range)
        unit: g/cm³
```

**Interpretation**: Copper's density (8.96) falls mid-range among all metals (0.53-22.6), providing meaningful comparison context.

---

### Example 2: Stucco Compressive Strength (Null Range Correct)

**Categories.yaml (masonry category)**:
```yaml
category_ranges:
  density: { min: 0.6, max: 2.8, unit: g/cm³ }
  hardness: { min: 1.0, max: 7.0, unit: Mohs }
  # Note: compressiveStrength NOT in category_ranges
```

**materials.yaml**:
```yaml
Stucco:
  category: masonry
  properties:
    compressiveStrength:
      value: 15.0
      unit: MPa
      # No min/max in materials.yaml either
```

**Frontmatter Output**:
```yaml
materialProperties:
  mechanical:
    properties:
      compressiveStrength:
        value: 15.0
        min: null      # Correct - no category range defined
        max: null      # Correct - no category range defined
        unit: MPa
```

**Why null is correct**: Not all properties have category ranges defined. This is by design, not an error.

---

## Testing Strategy

### Test 1: Verify Category Ranges Load Correctly
```python
def test_category_ranges_loading():
    """Ensure Categories.yaml category_ranges load into generator"""
    generator = StreamlinedGenerator()
    
    # Check all 9 categories loaded
    assert len(generator.category_ranges) == 9
    
    # Check metal category has all 12 properties
    assert 'metal' in generator.category_ranges
    assert len(generator.category_ranges['metal']) == 12
    
    # Verify density range structure
    density = generator.category_ranges['metal']['density']
    assert 'min' in density and density['min'] == 0.53
    assert 'max' in density and density['max'] == 22.6
    assert 'unit' in density and density['unit'] == 'g/cm³'
```

### Test 2: Verify Frontmatter Uses Category Ranges
```python
def test_frontmatter_uses_category_ranges():
    """Verify frontmatter min/max come from Categories.yaml, not materials.yaml"""
    # Generate Copper frontmatter
    generator = StreamlinedGenerator()
    result = generator.generate_frontmatter('Copper')
    
    # Get density from frontmatter
    density = result['materialProperties']['physical_structural']['properties']['density']
    
    # Should match category ranges (metal)
    assert density['min'] == 0.53   # Metal category min
    assert density['max'] == 22.6   # Metal category max
    
    # Should NOT match material tolerance ranges
    assert density['min'] != 8.89   # Copper material min (ignored)
    assert density['max'] != 8.96   # Copper material max (ignored)
```

### Test 3: Verify Null Ranges When No Category Range
```python
def test_null_ranges_when_no_category_range():
    """Properties without category ranges should have null min/max"""
    generator = StreamlinedGenerator()
    result = generator.generate_frontmatter('Stucco')
    
    # compressiveStrength not in masonry category_ranges
    comp = result['materialProperties']['mechanical']['properties']['compressiveStrength']
    
    assert comp['value'] == 15.0    # Has value
    assert comp['min'] is None      # No category range
    assert comp['max'] is None      # No category range
```

### Test 4: Verify All Categories Have Ranges
```python
def test_all_categories_have_ranges():
    """All 9 categories should have category_ranges defined"""
    with open('data/Categories.yaml', 'r') as f:
        cat_data = yaml.safe_load(f)
    
    categories = ['ceramic', 'composite', 'glass', 'masonry', 'metal', 
                  'plastic', 'semiconductor', 'stone', 'wood']
    
    for category in categories:
        assert category in cat_data['categories']
        assert 'category_ranges' in cat_data['categories'][category]
        assert len(cat_data['categories'][category]['category_ranges']) == 12
```

---

## Maintenance Guidelines

### When Adding New Materials
1. Add to `materials.yaml` with category and properties
2. Include material-specific values ONLY
3. **Do NOT** add min/max unless material-specific tolerance ranges
4. Category ranges will auto-populate in frontmatter

### When Adding New Properties
1. If property should have category context, add to `Categories.yaml` category_ranges
2. Add to all 9 categories for consistency
3. Generator will automatically pick up new category ranges
4. Existing frontmatter needs regeneration to get new ranges

### When Fixing Data Quality
1. Check for category duplicate ranges in materials.yaml (currently 8 found)
2. Remove or replace with material-specific tolerance ranges
3. Verify generator still uses Categories.yaml only

### When Modifying Generator
1. **NEVER** read min/max from materials.yaml properties
2. **ALWAYS** use `_get_category_ranges_for_property()`
3. Maintain fail-fast behavior (no fallback defaults)
4. Preserve null ranges when no category range exists

---

## Common Mistakes to Avoid

### ❌ Mistake 1: "Null ranges are missing data"
**Reality**: Null ranges are correct when no category range is defined. Not all properties have category ranges.

### ❌ Mistake 2: "Material min/max should be in frontmatter"
**Reality**: Material-specific tolerances (e.g., Copper 8.89-8.96) don't provide comparison context. Category ranges (0.53-22.6) do.

### ❌ Mistake 3: "Generator should read from materials.yaml min/max"
**Reality**: Generator must ignore materials.yaml min/max and use Categories.yaml only.

### ❌ Mistake 4: "Add ranges to materials.yaml for completeness"
**Reality**: Only add material-specific tolerance ranges (narrow). Never duplicate category ranges.

### ❌ Mistake 5: "All properties should have ranges"
**Reality**: Only 12 properties out of 55+ have category ranges (by design).

---

## Statistics (Current System)

- **Categories**: 9 (ceramic, composite, glass, masonry, metal, plastic, semiconductor, stone, wood)
- **Category Range Properties**: 12 per category (108 total definitions)
- **Materials**: 122
- **Material Properties**: ~6,700 total property instances
- **Material-Specific Tolerance Ranges**: 1,332
- **Category Range Duplicates**: 8 (data quality issue)
- **Frontmatter Files**: 122
- **Properties in Frontmatter with Category Ranges**: Varies by material category

---

## Related Documentation

- **Setup**: `setup/API_CONFIGURATION.md`
- **Quick Reference**: `docs/QUICK_REFERENCE.md`
- **Index**: `docs/INDEX.md`
- **Component Architecture**: `components/frontmatter/docs/README.md`
- **Recent Fix**: `MISSING_RANGE_VALUES_FIXED.md`

---

## Version History

- **v1.0** (Oct 14, 2025): Initial comprehensive documentation
  - Clarified three types of ranges
  - Documented correct data flow
  - Added testing strategy
  - Identified 8 category duplicate issues
