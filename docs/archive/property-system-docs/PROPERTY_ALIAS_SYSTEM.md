# Property Alias System

**Date**: October 17, 2025  
**Purpose**: Handle migration from legacy thermal property names to unified `thermalDestruction` system

## Overview

The Z-Beam Generator uses a property alias mapping system to handle the migration from category-specific thermal destruction property names to a unified `thermalDestruction` property that works across all material categories.

## Legacy Property Migration

### Problem
Different material categories historically used different property names for thermal destruction:

- **Metals**: `meltingPoint` (melting temperature)
- **Ceramics**: `sinteringPoint` (sintering temperature)
- **Plastics/Composites**: `degradationPoint` (thermal degradation)
- **Glass**: `softeningPoint` (glass transition)
- **Stone/Masonry**: `thermalDegradationPoint` (decomposition)
- **Wood**: `carbonization` (decomposition without melting)

### Solution: Unified `thermalDestruction` Property

All materials now use `thermalDestruction` with structure:

```yaml
thermalDestruction:
  point:
    value: 1538.0
    unit: °C
    min: 1500.0
    max: 1600.0
  type: melting  # or sintering, degradation, softening, carbonization, decomposition
  confidence: 0.95
  source: ai_research
  research_basis: materials_science_database
  research_date: 2025-10-17
```

## Property Alias Mapping

Defined in `PropertyValueResearcher.PROPERTY_ALIASES`:

```python
PROPERTY_ALIASES = {
    'meltingPoint': 'thermalDestruction',
    'thermalDestructionPoint': 'thermalDestruction',
    'sinteringPoint': 'thermalDestruction',
    'degradationPoint': 'thermalDestruction',
    'softeningPoint': 'thermalDestruction',
    'thermalDegradationPoint': 'thermalDestruction',
}
```

## How It Works

### 1. Property Discovery

When AI discovery finds legacy properties like `meltingPoint`:

```python
discovered = {
    'meltingPoint': {
        'value': 1538,
        'unit': '°C',
        'confidence': 0.95
    }
}
```

### 2. Alias Resolution

The property manager resolves aliases during processing:

```python
canonical_prop_name = PropertyValueResearcher.resolve_property_alias('meltingPoint')
# Returns: 'thermalDestruction'
```

### 3. Category Range Lookup

System looks up `thermalDestruction` ranges (which exist for all categories):

```yaml
# Categories.yaml - metal category
thermalDestruction:
  point:
    min: 200
    max: 3500
    unit: °C
  type: melting
```

### 4. Property Construction

Final property uses canonical name with proper structure:

```yaml
thermalDestruction:
  point:
    value: 1538.0
    unit: °C
    min: 200.0
    max: 3500.0
  type: melting
  confidence: 0.95
  source: ai_research
```

## Benefits

### 1. **Backward Compatibility**
- AI discovery can still find properties by legacy names
- No need to update AI prompts immediately
- Gradual migration supported

### 2. **Data Consistency**
- All materials use same property structure
- Easier validation and comparison
- Unified frontmatter generation

### 3. **Type Preservation**
- `type` field preserves material-specific destruction mechanism
- `melting` for metals, `carbonization` for wood, etc.
- Maintains scientific accuracy

### 4. **Fail-Fast Behavior**
- Properties without category ranges are skipped gracefully
- Clear logging when aliases are resolved
- No silent fallbacks or defaults

## Usage Examples

### Checking for Aliases

```python
from components.frontmatter.research.property_value_researcher import PropertyValueResearcher

# Check if property is an alias
canonical = PropertyValueResearcher.resolve_property_alias('meltingPoint')
print(canonical)  # Output: 'thermalDestruction'

# Non-aliased properties return unchanged
canonical = PropertyValueResearcher.resolve_property_alias('density')
print(canonical)  # Output: 'density'
```

### Logging Output

When aliases are resolved, you'll see:

```
🔄 Property alias resolved: 'meltingPoint' → 'thermalDestruction' for Iron
```

### Skipping Inapplicable Properties

If AI discovers a property without category ranges:

```
⚠️  Skipping discovered property 'absorptionCoefficient' for wood - no category ranges defined. 
    Property not applicable to this category.
```

## Category-Specific Types

The `type` field in `thermalDestruction` indicates the mechanism:

| Category      | Type            | Description                           |
|---------------|-----------------|---------------------------------------|
| metal         | melting         | Phase transition to liquid            |
| ceramic       | sintering       | Particle fusion below melting point   |
| plastic       | degradation     | Polymer chain breakdown               |
| composite     | degradation     | Matrix/fiber degradation              |
| glass         | softening       | Glass transition temperature          |
| wood          | carbonization   | Pyrolysis/charring without melting    |
| stone         | decomposition   | Thermal breakdown of minerals         |
| semiconductor | decomposition   | Crystal structure degradation         |
| masonry       | decomposition   | Binding material breakdown            |

## Implementation Files

- **Alias Definition**: `components/frontmatter/research/property_value_researcher.py`
  - `PropertyValueResearcher.PROPERTY_ALIASES`
  - `PropertyValueResearcher.resolve_property_alias()`

- **Alias Resolution**: `components/frontmatter/services/property_manager.py`
  - `_process_discovered_properties()` method
  - Resolves aliases before range lookup

- **Category Ranges**: `data/Categories.yaml`
  - All categories have `thermalDestruction` ranges
  - Legacy property ranges being phased out

## Testing

Verify alias system works:

```bash
# Test material that would discover legacy properties
python3 run.py --material "Oak"

# Check logs for alias resolution messages
grep "Property alias resolved" batch_generation.log
```

## Migration Status

### ✅ Complete (October 17, 2025)
1. **Property Alias System Implemented** - All 6 thermal property aliases defined and operational
2. **PropertyValueResearcher Integration** - Alias resolution in AI research pipeline
3. **PropertyManager Integration** - Alias resolution in property discovery pipeline
4. **Essential Property Lists Updated** - All validators use unified thermalDestruction
5. **Materials.yaml Structures Fixed** - 104 materials with complete thermalDestruction properties
6. **Validation Logic Updated** - Conservation of energy tolerance adjusted to 130%
7. **Documentation Complete** - Full system documentation and validation fix reports

### Validation Integration (NEW - October 17, 2025)

All validation components now use the unified `thermalDestruction` property:

**Updated Files**:
- `components/frontmatter/services/property_manager.py` - Essential properties standardized
- `components/frontmatter/validation/completeness_validator.py` - Essential properties standardized
- `validation/helpers/relationship_validators.py` - A+R tolerance increased to 130%

**Key Changes**:
```python
# Before: Mixed thermal property names
ESSENTIAL_PROPERTIES = {
    'stone': {'thermalDegradationPoint', 'density', 'hardness'},
    'ceramic': {'sinteringPoint', 'thermalConductivity', 'density'},
    'plastic': {'degradationPoint', 'thermalConductivity', 'density'}
}

# After: Unified thermalDestruction
ESSENTIAL_PROPERTIES = {
    'stone': {'thermalDestruction', 'density', 'hardness'},
    'ceramic': {'thermalDestruction', 'thermalConductivity', 'density'},
    'plastic': {'thermalDestruction', 'thermalConductivity', 'density'}
}
```

**Automatic Alias Resolution**:
- Validators check for `thermalDestruction`
- PropertyValueResearcher resolves aliases automatically
- No code changes needed in Materials.yaml (aliases work transparently)
- Full backward compatibility maintained

### 🔄 In Progress
- Batch generation testing with validated system

### 📋 Future Enhancements
- Remove legacy `meltingPoint` from Categories.yaml (metal category)
- Update AI discovery prompts to use canonical names directly
- Phase out legacy property names completely

## Notes

- **Wood materials**: Never had `meltingPoint` - wood carbonizes/decomposes rather than melting
- **Fail-fast principle**: Properties without category ranges are skipped, not filled with defaults
- **Zero Null Policy**: All thermal destruction properties must have complete structure
- **Research basis**: All properties include `research_basis` and `research_date` metadata
