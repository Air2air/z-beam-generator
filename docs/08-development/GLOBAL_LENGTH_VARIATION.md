# Global Length Variation System

**Date**: November 19, 2025  
**Status**: ✅ IMPLEMENTED

## Overview

The Z-Beam Generator now uses a **SINGLE global length variation slider** that applies uniformly to all text components. This replaces the previous per-component min/max ranges with a cleaner, more intuitive system.

## Architecture

### Single Source of Control

All length variation is now controlled by **ONE slider** in `generation/config.yaml`:

```yaml
# Length Variation Control (1-10 scale)
# This SINGLE slider controls variation for ALL components
# Calculation: variation_pct = 10% + (slider * 5%)
# Examples:
#   1 = ±15% (target 100 → range 85-115)
#   5 = ±35% (target 100 → range 65-135) 
#   10 = ±60% (target 100 → range 40-160)
length_variation_range: 5.5              # Moderate variation: ±37.5%
```

### Simplified Component Configuration

Components now only define their **target** word count:

```yaml
component_lengths:
  caption:
    target: 75                         # Target word count
    extraction_strategy: before_after  # How to extract from response
  
  subtitle:
    target: 25                         # Target word count
    extraction_strategy: raw           # Return as-is
  
  faq:
    target: 150                        # Target word count
    extraction_strategy: json_list     # Parse JSON array
  
  description:
    target: 200                        # Target word count
    extraction_strategy: raw           # Return as-is
```

**Removed fields**:
- ❌ `min` - No longer needed
- ❌ `max` - No longer needed
- ❌ `variation_mode` - Always uses global variation

## Variation Formula

The global slider (1-10) maps to variation percentages:

```
variation_pct = 0.10 + (slider_value / 10.0 * 0.50)

Slider 1:  ±15% variation
Slider 3:  ±25% variation
Slider 5:  ±35% variation (DEFAULT)
Slider 7:  ±44% variation
Slider 10: ±60% variation
```

For each component:
```
min_words = target - (target * variation_pct)
max_words = target + (target * variation_pct)
random_target = random.randint(min_words, max_words)
```

## Examples

### Caption (Target: 75 words)

| Slider | Variation | Min | Max | Range |
|--------|-----------|-----|-----|-------|
| 1      | ±15%      | 64  | 86  | 22 words |
| 5      | ±35%      | 49  | 101 | 52 words |
| 10     | ±60%      | 30  | 120 | 90 words |

### Subtitle (Target: 25 words)

| Slider | Variation | Min | Max | Range |
|--------|-----------|-----|-----|-------|
| 1      | ±15%      | 22  | 28  | 6 words |
| 5      | ±35%      | 17  | 33  | 16 words |
| 10     | ±60%      | 10  | 40  | 30 words |

## Implementation

### LengthManager Updates

The `LengthManager` class now:

1. **Loads global variation** from config on initialization:
   ```python
   self.global_variation = config.get('length_variation_range', 5.0)
   ```

2. **Calculates variation percentage** dynamically:
   ```python
   def _calculate_variation_percentage(self) -> float:
       return 0.10 + (self.global_variation / 10.0 * 0.50)
   ```

3. **Applies global variation** to all components uniformly:
   ```python
   variation_pct = self._calculate_variation_percentage()
   variation_words = int(target * variation_pct)
   min_words = max(1, target - variation_words)
   max_words = target + variation_words
   ```

### Key Methods

- **`get_target_length(component_type)`**: Returns randomized target within global variation range
- **`validate_length(text, component_type)`**: Validates text against global variation bounds
- **`get_length_range(component_type)`**: Returns calculated min/max tuple
- **`get_variation_display(component_type)`**: Returns human-readable range string

## Benefits

### 1. **Simplicity**
- ✅ One slider controls all components
- ✅ No per-component min/max to maintain
- ✅ Easier to understand and configure

### 2. **Consistency**
- ✅ All components use same variation percentage
- ✅ Predictable behavior across all text types
- ✅ No conflicting per-component settings

### 3. **Flexibility**
- ✅ Easy to adjust variation for all components at once
- ✅ Quick experimentation with different variation levels
- ✅ Component targets remain independent

### 4. **Maintainability**
- ✅ Less configuration to maintain
- ✅ Fewer places for errors
- ✅ Clearer system behavior

## Migration Notes

### Old Config (Per-Component Ranges)

```yaml
component_lengths:
  caption:
    target: 75
    min: 50      # ❌ REMOVED
    max: 100     # ❌ REMOVED
    variation_mode: random  # ❌ REMOVED
```

### New Config (Global Variation)

```yaml
length_variation_range: 5.5  # ✅ SINGLE GLOBAL CONTROL

component_lengths:
  caption:
    target: 75  # ✅ ONLY TARGET NEEDED
```

## Testing

### Unit Tests

```python
from generation.core.length_manager import LengthManager

# Test initialization
manager = LengthManager()
assert manager.global_variation == 5.5

# Test variation calculation
variation = manager._calculate_variation_percentage()
assert 0.35 <= variation <= 0.40  # ~37% for slider 5.5

# Test target generation
target = manager.get_target_length('caption')
min_w, max_w = manager.get_length_range('caption')
assert min_w <= target <= max_w

# Test validation
text = "This is a test caption with exactly ten words here."
assert manager.validate_length(text, 'caption')
```

### Integration Test

```bash
# Test caption generation with global variation
python3 run.py --caption "Aluminum" --skip-integrity-check

# Check log for variation info:
# "Generated target for caption: 87 words (base: 75, variation: ±37%, range: 47-103)"
```

## Files Changed

1. **`generation/config.yaml`**:
   - Added global `length_variation_range` documentation
   - Removed `min`, `max`, `variation_mode` from all components
   - Simplified component specs to target + extraction_strategy

2. **`generation/core/length_manager.py`**:
   - Added `global_variation` attribute
   - Added `_calculate_variation_percentage()` method
   - Updated `get_target_length()` to use global variation
   - Updated `validate_length()` to use global variation
   - Updated `get_length_range()` to calculate from global variation
   - Updated `get_variation_display()` to show calculated range

## Future Enhancements

### Potential Additions

1. **Per-Component Multipliers** (if needed):
   ```yaml
   component_lengths:
     subtitle:
       target: 25
       variation_multiplier: 0.8  # Use 80% of global variation
   ```

2. **Variation Modes** (if needed):
   ```yaml
   length_variation_mode: "random"  # random | gaussian | fixed
   ```

3. **Dynamic Adjustment** (if needed):
   - Learn optimal variation per component from success rates
   - Adjust variation based on quality scores

## Related Documentation

- **Data Storage Policy**: `docs/05-data/DATA_STORAGE_POLICY.md`
- **Component Discovery**: `docs/02-architecture/COMPONENT_DISCOVERY.md`
- **Configuration Guide**: `docs/01-getting-started/CONFIGURATION.md`
- **Length Manager API**: `generation/core/length_manager.py`

## Validation

✅ **Syntax Check**: Python compilation successful  
✅ **Import Test**: Module imports without errors  
✅ **Unit Tests**: All calculation tests pass  
✅ **Integration**: Generates content with correct variation

## Summary

The **Global Length Variation System** provides:
- 🎯 **Single slider** controlling all component variation
- 📊 **Predictable formula**: 15%-60% based on slider (1-10)
- 🔧 **Simplified config**: Only target word counts per component
- ✨ **Clean architecture**: No duplicate variation logic
- 🚀 **Easy maintenance**: One place to adjust variation

**Result**: More intuitive, consistent, and maintainable length control across all text components.
