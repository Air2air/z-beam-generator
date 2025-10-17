# Data Architecture: Complete Pipeline Normalization

## Overview
This document describes the **fully normalized** data flow through the Z-Beam Generator system after October 2025 restructuring with 2-category materialProperties taxonomy.

**Last Updated**: October 15, 2025  
**Status**: ✅ Complete normalization achieved with 2-category system (laser_material_interaction + material_characteristics)

---

## Architecture Principle: Single Source of Truth

The system follows a strict **separation of concerns**:

- **Categories.yaml**: Category-wide min/max ranges (comparison context)
- **materials.yaml**: Material-specific values (individual material data)
- **Generator**: Combines both sources
- **Frontmatter**: Displays complete property data

**Critical Rule**: Min/max ranges exist ONLY in Categories.yaml, NEVER in materials.yaml.

---

## Data Structure

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
      thermalDestruction:   # Nested structure
        point:
          min: -38.8    # Mercury
          max: 3422     # Tungsten
          unit: K
        type: melting
```

**Properties with category ranges**: 12 properties across 9 categories
- `density`, `hardness`, `laserAbsorption`, `laserReflectivity`
- `specificHeat`, `tensileStrength`, `thermalConductivity`
- `thermalDestruction` (nested: point + type)
- `thermalDiffusivity`, `thermalExpansion`, `youngsModulus`

**Categories**: ceramic, composite, glass, masonry, metal, plastic, semiconductor, stone, wood (all lowercase)

---

### 2. Material Values (materials.yaml)
**Location**: `data/materials.yaml → materials.[material_name].properties`

**Purpose**: Store **material-specific values** with confidence and metadata.

**Scope**: Individual material data with NO min/max ranges.

**Example**:
```yaml
materials:
  Copper:
    category: metal
    subcategory: non_ferrous
    properties:
      density:
        value: 8.96
        unit: g/cm³
        confidence: 98
        description: Pure copper density at room temperature
        # ✅ NO min/max - these come from Categories.yaml
      thermalDestruction:   # Nested structure
        point:
          value: 1357.77
          unit: K
          confidence: 98
          # ✅ NO min/max - these come from Categories.yaml
        type: melting
```

**Count**: 122 materials with properties

**Key Point**: Properties contain value, unit, confidence, description, source - but **NEVER min/max**.

---

## Data Flow Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│ 1. Categories.yaml (Source of Truth for Ranges)                     │
│    categories.[category].category_ranges                             │
│    • 9 categories × 12 properties = 108 category range definitions   │
│    • Purpose: Comparison context across category                     │
│    • Contains: min, max, unit (and nested structures)                │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ↓
┌──────────────────────────────────────────────────────────────────────┐
│ 2. materials.yaml (Source of Truth for Values)                       │
│    materials.[material].properties                                    │
│    • 122 materials with properties                                    │
│    • Each property: value, unit, confidence, description, source      │
│    • NO min/max anywhere - values only                                │
│    • Category: Links to Categories.yaml category (lowercase)          │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ↓
┌──────────────────────────────────────────────────────────────────────┐
│ 3. StreamlinedGenerator (Combines Data)                              │
│    components/frontmatter/core/streamlined_generator.py               │
│    • Loads Categories.yaml → self.category_ranges                    │
│    • Loads materials.yaml → material properties                      │
│    • Calls _get_category_ranges_for_property()                       │
│    • Injects category ranges into property min/max                   │
│    • Special handling for nested thermalDestruction                  │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ↓
┌──────────────────────────────────────────────────────────────────────┐
│ 4. Frontmatter YAML Output (2-Category Structure)                    │
│    content/components/frontmatter/[material]-laser-cleaning.yaml     │
│    materialProperties:                                                │
│      laser_material_interaction:                                      │
│        label: Laser-Material Interaction                              │
│        percentage: 47.3                                               │
│        properties:                                                    │
│          laserAbsorption:                                             │
│            value: 47.5     ← From materials.yaml                     │
│            min: 0.02       ← From Categories.yaml (metal range)      │
│            max: 100        ← From Categories.yaml (metal range)      │
│            unit: %                                                    │
│          thermalConductivity:                                         │
│            value: 401      ← From materials.yaml                     │
│            min: 15         ← From Categories.yaml (metal range)      │
│            max: 400        ← From Categories.yaml (metal range)      │
│            unit: W/(m·K)                                              │
│      material_characteristics:                                        │
│        label: Material Characteristics                                │
│        percentage: 52.7                                               │
│        properties:                                                    │
│          density:                                                     │
│            value: 8.96     ← From materials.yaml                     │
│            min: 0.53       ← From Categories.yaml (metal range)      │
│            max: 22.6       ← From Categories.yaml (metal range)      │
│            unit: g/cm³                                                │
│          hardness:                                                    │
│            value: 369      ← From materials.yaml                     │
│            min: 2.5        ← From Categories.yaml (metal range)      │
│            max: 3500       ← From Categories.yaml (metal range)      │
│            unit: MPa                                                  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Two-Category materialProperties System

### Overview (as of October 15, 2025)
The frontmatter uses a **2-category taxonomy** for organizing material properties:

1. **`laser_material_interaction`** (26 properties, 47.3%)
   - Optical and thermal properties governing laser energy absorption, reflection, propagation, and ablation thresholds
   - Includes: laserAbsorption, laserReflectivity, thermalConductivity, specificHeat, ablationThreshold, etc.

2. **`material_characteristics`** (29 properties, 52.7%)
   - Intrinsic physical, mechanical, chemical, and structural properties affecting cleaning outcomes
   - Includes: density, hardness, tensileStrength, youngsModulus, corrosionResistance, etc.

### Scientific Rationale
This structure aligns with:
- **Materials Science**: Mechanical properties (hardness, strength, modulus) are material properties, not separate
- **Laser Processing Physics**: Clear distinction between laser-material interaction and material nature
- **Industry Standards**: Matches standard materials databases (ASM, MatWeb, NIST)

### Migration from 3-Category System
Previous system (DEPRECATED v4.0.0):
- `energy_coupling` → Renamed to `laser_material_interaction`
- `structural_response` + `material_properties` → Merged into `material_characteristics`

See `docs/TWO_CATEGORY_SYSTEM.md` for complete details.

---

## Nested thermalDestruction Structure

### Background
Prior to October 2025, thermal destruction data was stored as separate flat properties:
- `thermalDestructionPoint`: Temperature value
- `thermalDestructionType`: Mechanism type (melting, thermal_shock, etc.)
- `meltingPoint`: Redundant metal-specific property

### New Structure
These have been **combined into a nested object** for better semantic organization:

#### Categories.yaml:
```yaml
categories:
  metal:
    category_ranges:
      thermalDestruction:
        point:
          min: -38.8
          max: 3422
          unit: K
        type: melting
```

#### materials.yaml:
```yaml
materials:
  Copper:
    properties:
      thermalDestruction:
        point:
          value: 1357.77
          unit: K
          confidence: 98
        type: melting
```

#### Generated Frontmatter:
```yaml
materialProperties:
  laser_material_interaction:
    label: Laser-Material Interaction
    properties:
      thermalDegradationPoint:
        value: 1357.77    # From material
        unit: °C
        confidence: 98
        min: -38.8        # From category
        max: 3422         # From category
```

### Destruction Types by Category:
- **ceramic**: thermal_shock
- **composite**: decomposition
- **glass**: melting
- **masonry**: spalling
- **metal**: melting
- **plastic**: decomposition
- **semiconductor**: melting
- **stone**: thermal_shock
- **wood**: carbonization

### Generator Implementation
The generator has special handling for nested structures in `_populate_property()` (lines 661-689):
1. Detects nested property format
2. Reads value from materials.yaml
3. Gets min/max from Categories.yaml via `_get_category_ranges_for_property()`
4. Builds nested structure in frontmatter

---

## Critical Design Principles

### ✅ CORRECT Behavior

1. **Frontmatter min/max = Category ranges ONLY**
   - Always pull from Categories.yaml
   - Never from materials.yaml (which has no min/max)
   - Provides comparison context

2. **Material values stay pure**
   - materials.yaml contains only: value, unit, confidence, description, source
   - NO min/max anywhere in materials.yaml
   - Preserves single source of truth

3. **Generator combines both**
   - Reads value from materials.yaml
   - Reads ranges from Categories.yaml
   - Outputs complete property data to frontmatter

4. **Category capitalization: lowercase everywhere**
   - Categories.yaml: `category: metal` ✅
   - materials.yaml: `category: metal` ✅
   - Frontmatter: `category: Metal` ✅ (note: frontmatter capitalizes for display)

### ❌ INCORRECT Behavior (What We Avoid)

1. **DO NOT add min/max to materials.yaml**
   - Would create redundancy
   - Would violate single source of truth
   - Would confuse category ranges with material variance

2. **DO NOT use material min/max in frontmatter**
   - System used to have material-specific ranges (pre-Oct 2025)
   - These were removed during normalization
   - All ranges now come from categories

3. **DO NOT duplicate category ranges in materials**
   - Some materials previously had exact category range duplicates
   - These have been removed
   - Category ranges live ONLY in Categories.yaml

---

## Example: Complete Property Flow

### Source Data

**Categories.yaml** (metal category):
```yaml
categories:
  metal:
    category_ranges:
      density:
        min: 0.53    # Lithium
        max: 22.6    # Osmium
        unit: g/cm³
```

**materials.yaml** (Copper):
```yaml
materials:
  Copper:
    category: metal
    properties:
      density:
        value: 8.96
        unit: g/cm³
        confidence: 98
        description: Pure copper density at room temperature
        source: ai_research
```

### Generator Process

1. Load Copper material data
2. Find property: `density = {value: 8.96, unit: g/cm³, confidence: 98, ...}`
3. Detect category: `metal`
4. Call `_get_category_ranges_for_property('metal', 'density')`
5. Return: `{min: 0.53, max: 22.6, unit: g/cm³}`
6. Inject ranges into property
7. Output to frontmatter

### Frontmatter Output

```yaml
materialProperties:
  physical_structural:
    label: Physical/Structural Properties
    properties:
      density:
        value: 8.96          # From materials.yaml
        unit: g/cm³          # From materials.yaml
        confidence: 98       # From materials.yaml
        description: Pure copper density at room temperature
        min: 0.53            # From Categories.yaml (metal range)
        max: 22.6            # From Categories.yaml (metal range)
```

---

## Statistics

### Current System (October 2025)
- **Categories**: 9 (all lowercase)
- **Materials**: 122
- **Category Range Definitions**: 108 (9 categories × 12 properties)
- **Material Properties with Values**: ~1,220
- **Material Properties with Min/Max**: **0** (complete normalization achieved)
- **Frontmatter Files**: 115 generated, 7 skipped (not in materials.yaml)

### Normalization Achievement
- ✅ **Categories.yaml**: Single source of truth for ranges
- ✅ **materials.yaml**: Single source of truth for values (NO min/max)
- ✅ **Generator**: Combines both correctly
- ✅ **Frontmatter**: Displays complete data (value + ranges)
- ✅ **Nested structures**: thermalDestruction properly integrated
- ✅ **Category capitalization**: Lowercase system-wide

---

## For Developers

### Adding New Properties

When adding a new property to the system:

1. **Add to Categories.yaml** (if category-wide ranges apply):
```yaml
categories:
  metal:
    category_ranges:
      newProperty:
        min: 0.0
        max: 100.0
        unit: unit_name
```

2. **Add to materials.yaml** (value only, NO min/max):
```yaml
materials:
  Copper:
    properties:
      newProperty:
        value: 42.5
        unit: unit_name
        confidence: 95
        description: Description of property
        source: ai_research
```

3. **Generator automatically handles it** - no code changes needed for standard properties

4. **For nested structures** (like thermalDestruction):
   - Follow the nested pattern in both files
   - Update `_populate_property()` if special handling needed
   - Update `_get_category_ranges_for_property()` to handle nesting

### Common Pitfalls to Avoid

❌ **DON'T**: Add min/max to materials.yaml properties
```yaml
# WRONG - violates normalization
properties:
  density:
    value: 8.96
    min: 0.53    # ❌ NO! This belongs in Categories.yaml only
    max: 22.6    # ❌ NO! This belongs in Categories.yaml only
```

✅ **DO**: Add only value data to materials.yaml
```yaml
# CORRECT - normalized structure
properties:
  density:
    value: 8.96
    unit: g/cm³
    confidence: 98
```

---

## Property Data Patterns (as of Oct 2025)

### Pattern Evolution

The system supports **4 property data patterns**, reflecting the evolution from AI-generated to research-backed authoritative data:

#### 1. Legacy Format (Original - 70-85% confidence)
```yaml
ablationThreshold:
  value: 0.8
  unit: "J/cm²"
  confidence: 80
  description: "Laser ablation threshold"
  min: null
  max: null
```
- **Used by**: ~800 properties across 122 materials
- **Source**: Original AI generation
- **Status**: Still valid, maintained for backward compatibility

#### 2. Pulse-Specific Format (Priority 2 Authoritative - 90% confidence)
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
  source: "Marks et al. 2022, Precision Engineering"
  confidence: 90
  measurement_context: "Varies by pulse duration (ns/ps/fs)"
```
- **Used by**: 45 properties (36 metals, 7 ceramics, 2 glasses)
- **Source**: Peer-reviewed research (Priority 2 automation)
- **Properties**: ablationThreshold
- **Impact**: Enables pulse-duration-specific laser parameter optimization

#### 3. Wavelength-Specific Format (Priority 2 Authoritative - 85% confidence)
```yaml
reflectivity:
  at_1064nm:    # Nd:YAG, Fiber lasers
    min: 85
    max: 98
    unit: "%"
  at_532nm:     # Green doubled Nd:YAG
    min: 70
    max: 95
    unit: "%"
  at_355nm:     # UV tripled Nd:YAG
    min: 55
    max: 85
    unit: "%"
  at_10640nm:   # CO2 lasers
    min: 95
    max: 99
    unit: "%"
  source: "Handbook of Optical Constants (Palik)"
  confidence: 85
  measurement_context: "Varies by laser wavelength"
```
- **Used by**: 35 properties (metals only)
- **Source**: Handbook of Optical Constants (Palik)
- **Properties**: reflectivity
- **Impact**: Enables wavelength-specific laser selection and parameter optimization

#### 4. Authoritative Format (Priority 2 Enhanced Legacy - 75-90% confidence)
```yaml
thermalConductivity:
  value: 401
  unit: "W/(m·K)"
  confidence: 85
  description: "Thermal conductivity of pure copper at 20°C"
  min: 15
  max: 400
  source: "MatWeb Materials Database"
  notes: "Typical range for metal materials at room temperature"
```
- **Used by**: ~144 properties across ~60 materials
- **Source**: Research databases (NIST, ASM Handbook, MatWeb, Engineering ToolBox, etc.)
- **Properties**: thermalConductivity, porosity, oxidationResistance, surfaceRoughness
- **Enhancement**: Legacy format + source attribution + contextual notes

### Pattern Detection & Value Extraction

**Generators use pattern-aware methods**:
- `_detect_property_pattern(prop_data)` → Returns: `'pulse-specific'`, `'wavelength-specific'`, `'authoritative'`, `'legacy-sourced'`, or `'legacy'`
- `_extract_property_value(prop_data, prefer_wavelength='1064nm', prefer_pulse='nanosecond')` → Returns numeric value

**Detection Logic**:
1. Check for `nanosecond/picosecond/femtosecond` keys → pulse-specific
2. Check for `at_1064nm/at_532nm/at_355nm/at_10640nm` keys → wavelength-specific
3. Check for `source` + confidence > 85% → authoritative
4. Check for `source` or `notes` → legacy-sourced
5. Default → legacy

**Value Extraction**:
- Pulse-specific: Returns average of preferred pulse duration (default: nanosecond)
- Wavelength-specific: Returns average of preferred wavelength (default: 1064nm for Nd:YAG)
- Legacy/Authoritative: Returns `value` field or min/max average
- Fallback: Returns 0

### Generator Compatibility

**Updated Generators** (Oct 2025):
- ✅ `streamlined_generator.py` - Pattern-aware value extraction
- ✅ Preserves pulse-specific and wavelength-specific structures during operations
- ✅ Handles all 4 patterns transparently for tag generation and property access
- ✅ Comprehensive test coverage (15 tests in `test_property_pattern_detection.py`)

**Critical Preservation Rule**:
Generators must NOT overwrite pulse-specific or wavelength-specific patterns during regeneration. Always check pattern type before regenerating any property with confidence > 85% and source attribution.

### Data Distribution

| Pattern | Properties | Files | Confidence | Status |
|---------|-----------|-------|------------|--------|
| Legacy | ~800 | 122 | 70-85% | ✅ Maintained |
| Pulse-specific | 45 | 45 | 90% | ✅ Priority 2 |
| Wavelength-specific | 35 | 35 | 85% | ✅ Priority 2 |
| Authoritative | 144 | ~60 | 75-90% | ✅ Priority 2 |

**Total Priority 2 Updates**: 224 authoritative properties across 91 materials

### Related Documentation

- **Normalization Analysis**: `FRONTMATTER_NORMALIZATION_REPORT.md`
- **Generator Updates**: `GENERATOR_PATTERN_AWARENESS_UPDATE.md`
- **Priority 2 Research**: `docs/PRIORITY2_COMPLETE.md`
- **Test Suite**: `tests/test_property_pattern_detection.py`

---

## Migration Notes

### Pre-October 2025 System
- Had material-specific min/max in materials.yaml (~1,332 instances)
- Used flat `thermalDestructionPoint` and `thermalDestructionType`
- Had `meltingPoint` as separate property
- Mixed category capitalization (Capitalized in frontmatter, lowercase elsewhere)

### October 2025 Normalization
- ✅ Removed ALL material min/max from materials.yaml
- ✅ Restructured to nested `thermalDestruction` object
- ✅ Removed `meltingPoint` from all files
- ✅ Normalized categories to lowercase system-wide
- ✅ Updated 115 frontmatter files via scripting
- ✅ Updated generator to handle nested structures
- ✅ Updated JSON schema to reflect new structure

### Result
Complete pipeline normalization - all properties follow the same pattern with zero exceptions.

---

## References

- **Implementation Details**: `COMPLETE_PIPELINE_NORMALIZATION.md`
- **Generator Code**: `components/frontmatter/core/streamlined_generator.py`
- **Schema Definition**: `schemas/frontmatter.json`
- **Test Suite**: `tests/test_range_propagation.py`
- **Quick Reference**: `docs/QUICK_REFERENCE.md`

---

**Last Verified**: October 14, 2025  
**System Status**: ✅ Fully Normalized - All Properties Follow Same Pattern
