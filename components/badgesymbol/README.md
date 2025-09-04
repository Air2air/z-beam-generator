# BadgeSymbol Component Documentation

## Overview

The BadgeSymbol component generates standardized material symbol badges by extracting data from frontmatter. It is a **static component** that does not make API calls but has a **critical dependency** on frontmatter being generated first.

## Architecture

### Static Component (No API Calls)
- **Type**: Static component
- **API Provider**: `none`
- **Data Source**: Frontmatter data extraction
- **Dependencies**: Frontmatter must be generated first (critical)

### Data Flow
```
Frontmatter Generation → BadgeSymbol Extraction → YAML Badge Generation
```

## Dependencies

### Critical Dependencies
1. **Frontmatter Component**: **MUST** be generated first - no fallback available
2. **Material Schema**: Schema files must exist for field mapping
3. **Example Files**: Example badge files for format reference

### Frontmatter Dependency (Critical)
The BadgeSymbol component **cannot function** without frontmatter data because:
- It extracts chemical symbols, material types, and properties from frontmatter
- No fallback mechanism exists - system uses fail-fast architecture
- Missing frontmatter results in generation failure

## Configuration

### Component Configuration
```yaml
badgesymbol:
  enabled: true
  api_provider: "none"  # Static component
  type: "static"
```

### Required Files
- `schemas/material.json`: Material schema for field mapping
- `components/badgesymbol/example_badgesymbol.md`: Format reference
- Frontmatter data from previous generation step

## Usage Examples

### Basic Usage (Requires Frontmatter)
```python
from components.badgesymbol.generator import BadgeSymbolGenerator

generator = BadgeSymbolGenerator()

# Frontmatter MUST be available
frontmatter_data = {
    "name": "Aluminum",
    "chemicalProperties": {
        "symbol": "Al",
        "materialType": "Pure Metal"
    }
}

content = generator.generate_content("Aluminum", frontmatter_data)
```

### Integration with Dynamic Generator
```python
from generators.dynamic_generator import DynamicGenerator

generator = DynamicGenerator()

# CRITICAL: Generate frontmatter FIRST
frontmatter_result = generator.generate_component("Aluminum", "frontmatter")
if not frontmatter_result.success:
    raise Exception("Frontmatter generation failed - BadgeSymbol cannot proceed")

# Now BadgeSymbol can use the frontmatter data
badgesymbol_result = generator.generate_component("Aluminum", "badgesymbol")
```

## Data Extraction

### Field Mapping
The component extracts data using this priority:

1. **Example Fields**: From `example_badgesymbol.md`
2. **Schema Fields**: From `schemas/material.json`
3. **Fallback Values**: Generated from material name

### Extraction Paths
```python
field_paths = {
    'symbol': ['chemicalProperties.symbol', 'symbol', 'chemicalFormula'],
    'materialType': ['chemicalProperties.materialType', 'materialType', 'category']
}
```

### Fallback Logic
- **Symbol**: First two letters of material name (uppercase)
- **Material Type**: Default to "material"

## Testing

### Test Categories
- **Unit Tests**: Field extraction and YAML generation
- **Integration Tests**: Frontmatter dependency validation
- **Error Tests**: Behavior when frontmatter is missing
- **Performance Tests**: Extraction speed and memory usage

### Key Test Cases
- Content generation with complete frontmatter
- Content generation with partial frontmatter
- **Failure case**: No frontmatter available (should fail)
- Field extraction from nested data structures
- YAML format validation

### Critical Test: Frontmatter Dependency
```python
def test_frontmatter_dependency_critical(self):
    """Test that BadgeSymbol fails without frontmatter (fail-fast)"""
    with self.assertRaises(Exception):
        # This MUST fail - no frontmatter means no generation
        result = self.generator.generate_content("Steel")
```

## Error Handling

### Critical Errors (Fail-Fast)
- **Missing Frontmatter**: Component cannot generate without frontmatter data
- **Missing Schema**: No schema file for field mapping
- **Invalid Frontmatter**: Frontmatter data doesn't match expected structure

### Error Messages
- `"No schema or example provided for badge symbol generation"`
- `"Frontmatter data required for BadgeSymbol generation"`
- `"Failed to extract required fields from frontmatter"`

## Performance

### Generation Time
- **Typical**: < 5ms per badge
- **With Dependencies**: < 20ms including frontmatter processing

### Memory Usage
- **Static Data**: Minimal (schema and example files)
- **Per Generation**: ~1KB for YAML output

## Best Practices

### 1. Always Generate Frontmatter First
```python
# REQUIRED ORDER: Frontmatter → BadgeSymbol
components_order = ["frontmatter", "badgesymbol", "author", ...]
```

### 2. Validate Frontmatter Before Generation
```python
# Check frontmatter exists and has required fields
if not has_frontmatter(material):
    logger.error(f"Frontmatter required for BadgeSymbol generation of {material}")
    return None

badgesymbol = generator.generate_content(material, frontmatter_data)
```

### 3. Handle Dependency Failures
```python
try:
    # Ensure frontmatter is generated first
    frontmatter = generate_frontmatter(material)
    if not frontmatter.success:
        raise Exception("BadgeSymbol dependency failed: frontmatter not available")

    badgesymbol = generate_badgesymbol(material, frontmatter.content)
except Exception as e:
    logger.error(f"BadgeSymbol generation failed due to dependency: {e}")
```

## Troubleshooting

### Frontmatter Not Available
**Symptom**: BadgeSymbol generation fails immediately
**Solution**: Ensure frontmatter component is generated first in the pipeline

### Schema File Missing
**Symptom**: "No schema or example provided" error
**Solution**: Verify `schemas/material.json` exists and is valid

### Invalid Frontmatter Structure
**Symptom**: Field extraction fails
**Solution**: Check frontmatter format matches expected schema

### Example File Missing
**Symptom**: Format reference not available
**Solution**: Ensure `components/badgesymbol/example_badgesymbol.md` exists

## Architecture Notes

### Fail-Fast Design
The BadgeSymbol component follows the system's fail-fast architecture:
- **No Fallbacks**: If dependencies are missing, generation fails
- **Explicit Dependencies**: All requirements must be met
- **Clear Error Messages**: Specific errors for different failure modes

### Static Component Benefits
- **Fast Generation**: No API calls required
- **Reliable**: No external service dependencies
- **Predictable**: Consistent output format
- **Low Cost**: No API usage costs

## Future Improvements

### Planned Enhancements
- **Enhanced Field Extraction**: Support for more complex data structures
- **Multiple Symbol Formats**: Support for different badge formats
- **Validation Integration**: Automatic validation of extracted data
- **Caching**: Cache extracted values for performance
- **Custom Symbol Mapping**: Override default symbol generation logic
