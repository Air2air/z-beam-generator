# Frontmatter Unit/Value Separation Update

## Overview
Updated the frontmatter generation system to separate numeric values from units, as requested.

## Changes Made

### 1. Generator Updates (streamlined_generator.py)
- **Added `_extract_numeric_only()` method**: Extracts pure numeric values from mixed strings
- **Updated `_generate_properties_with_ranges()`**: Now outputs numeric-only values 
- **Updated `_add_property_ranges()`**: Min/Max ranges are now numeric
- **Updated `_generate_machine_settings_with_ranges()`**: Machine settings use numeric values
- **Updated `_add_machine_setting_ranges()`**: Min/Max ranges are numeric

### 2. Schema Updates (frontmatter.json)
- **Main values**: Changed from `oneOf: [string, number]` to `type: "number"`
- **Min/Max fields**: Changed from `type: "string"` to `type: "number"`
- **Unit fields**: Remain as `type: "string"` (unchanged)

### 3. Output Format Changes
**Before:**
```yaml
properties:
  density: "2.7 g/cm³"
  densityMin: "0.53 g/cm³"
  densityMax: "22.59 g/cm³"
```

**After:**
```yaml
properties:
  density: 2.7
  densityUnit: "g/cm³"
  densityMin: 0.53
  densityMax: 22.59
```

## Benefits
- ✅ Clean separation of numeric values and units
- ✅ Better data processing capabilities (no string parsing needed)
- ✅ Consistent integer/float types throughout
- ✅ Maintains backward compatibility for unit information
- ✅ Schema validation ensures type correctness

## Validation
- All properties and machineSettings sections validate correctly
- Numeric values are properly typed as int/float
- Unit information preserved in separate *Unit fields
- Min/Max ranges are consistently numeric

## Files Modified
1. `components/frontmatter/core/streamlined_generator.py`
2. `schemas/frontmatter.json`

## Testing
Validated with Aluminum material generation:
- All numeric values properly extracted and typed
- Units correctly separated into *Unit fields
- Schema validation passes for both Properties and MachineSettings sections
