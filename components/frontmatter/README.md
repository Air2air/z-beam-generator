# Frontmatter Component

The frontmatter component generates YAML frontmatter for laser cleaning materials with a **numeric-only value format** and clean unit separation.

## 🔢 Unit/Value Separation Architecture

### Core Principle
All property and machine setting values are **pure numeric types** (int/float), with units stored in separate `*Unit` fields.

### Format Example
```yaml
properties:
  density: 8.9                    # Pure numeric (float)
  densityUnit: "g/cm³"           # Unit in separate field
  densityMin: 0.53               # Min range numeric
  densityMax: 22.59              # Max range numeric
  meltingPoint: 1025             # Pure numeric (int)
  meltingPointUnit: "°C"         # Unit in separate field

machineSettings:
  powerRange: 150.0              # Pure numeric (float)
  powerRangeUnit: "W"            # Unit in separate field
  powerRangeMin: 20.0            # Min range numeric
  powerRangeMax: 500.0           # Max range numeric
  wavelength: 1064.0             # Pure numeric (float)
  wavelengthUnit: "nm"           # Unit in separate field
```

## 🏗️ Key Components

### StreamlinedFrontmatterGenerator
Core generator with numeric extraction capabilities:

```python
from components.frontmatter.core.streamlined_generator import StreamlinedFrontmatterGenerator

generator = StreamlinedFrontmatterGenerator()
result = generator.generate("Copper", use_api=False)
```

**Key Methods:**
- `_extract_numeric_only()`: Extracts numeric values from strings with units
- `_generate_properties_with_ranges()`: Creates properties with Min/Max/Unit structure
- `_generate_machine_settings_with_ranges()`: Creates machine settings with ranges

### UnifiedPropertyEnhancementService
Processes and enhances properties while preserving numeric format:

```python
from components.frontmatter.enhancement.unified_property_enhancement_service import UnifiedPropertyEnhancementService

# Apply enhancement while preserving Min/Max/Unit structure
UnifiedPropertyEnhancementService.add_properties(frontmatter, preserve_min_max=True)
```

**Key Features:**
- Processes Min/Max fields containing units
- Preserves existing numeric values
- Extracts units into separate fields
- Maintains schema compliance

## 📋 Supported Fields

### Properties
- **Main Values**: `density`, `meltingPoint`, `thermalConductivity`, `tensileStrength`, `hardness`, `youngsModulus`
- **Min/Max Ranges**: All main values have corresponding `*Min` and `*Max` fields
- **Units**: All main values have corresponding `*Unit` fields

### Machine Settings
- **Main Values**: `powerRange`, `wavelength`, `pulseDuration`, `spotSize`, `repetitionRate`, `fluenceRange`
- **Min/Max Ranges**: All main values have corresponding `*Min` and `*Max` fields
- **Units**: All main values have corresponding `*Unit` fields

## 🧪 Testing

### Unit Value Separation Tests
```bash
python -m pytest components/frontmatter/tests/test_unit_value_separation.py -v
```

**Test Coverage:**
- Numeric value generation
- Min/Max field processing
- Schema validation
- Enhancement service behavior

### Schema Validation Tests
```bash
python -m pytest tests/validation/test_schema_validation.py -v
```

**Test Coverage:**
- Schema enforcement of numeric types
- Validation of generated content
- Rejection of invalid string values
- Unit field type validation

## 🔧 Configuration

### Materials Data
The component uses `data/materials.yaml` as the primary data source:

```yaml
materials:
  metal:
    items:
      - name: "Copper"
        density: 8.96
        melting_point: 1085
        thermal_conductivity: 401
        # ... more properties
```

### Category Ranges
Min/Max ranges are defined in materials configuration:
```yaml
category_ranges:
  metal:
    density:
      min: 0.53
      max: 22.59
      unit: "g/cm³"
```

## 🚀 Usage Examples

### Basic Generation
```python
from components.frontmatter.core.streamlined_generator import StreamlinedFrontmatterGenerator

generator = StreamlinedFrontmatterGenerator()
result = generator.generate("Bronze", use_api=False)

if result.success:
    print(f"Generated {len(result.content)} characters")
    # Save to file
    with open("bronze-frontmatter.md", "w") as f:
        f.write(result.content)
```

### Validation
```python
import yaml
import json
import jsonschema

# Parse generated content
content = result.content.strip()
yaml_content = content.split('---', 2)[1]
frontmatter_data = yaml.safe_load(yaml_content)

# Load and validate against schema
with open("schemas/frontmatter.json", "r") as f:
    schema = json.load(f)

jsonschema.validate(frontmatter_data, schema)
print("✅ Schema validation passed!")
```

### Check Numeric Format
```python
properties = frontmatter_data.get('properties', {})
machine_settings = frontmatter_data.get('machineSettings', {})

# Count numeric values
numeric_props = [k for k, v in properties.items() 
                 if isinstance(v, (int, float)) and not k.endswith('Unit')]
numeric_machine = [k for k, v in machine_settings.items() 
                   if isinstance(v, (int, float)) and not k.endswith('Unit')]

print(f"Properties: {len(numeric_props)} numeric values")
print(f"Machine Settings: {len(numeric_machine)} numeric values")
```

## 🔄 Migration from Old Format

If you have frontmatter files with the old format (units in values), they can be regenerated:

```bash
# Regenerate all materials with new format
python run.py --material "Copper" --regenerate
python run.py --material "Bronze" --regenerate
```

## 📊 Benefits

### For Developers
- **Type Safety**: Numeric values enable direct mathematical operations
- **Consistency**: All files follow the same numeric-only format
- **Validation**: Schema ensures data integrity
- **Processing**: No need to parse units from values

### For Data Processing
- **Direct Calculations**: `density * volume` works immediately
- **Range Validation**: `value >= densityMin and value <= densityMax`
- **Unit Conversion**: Units accessible for conversion logic
- **Database Storage**: Clean numeric types for database fields

### For Maintenance
- **Clear Separation**: Values vs units are obviously separated
- **Schema Enforcement**: Invalid formats are rejected
- **Test Coverage**: Comprehensive validation ensures reliability
- **Documentation**: Clear examples and usage patterns

## 🐛 Troubleshooting

### Common Issues

**Issue**: Min/Max fields contain strings with units
```yaml
# Wrong
meltingMax: "2800°C"

# Right  
meltingMax: 2800
meltingPointUnit: "°C"
```

**Solution**: Regenerate the material with the updated generator.

**Issue**: Schema validation fails
```
ValidationError: 'string value' is not of type 'number'
```

**Solution**: Check that all value fields are numeric, not strings.

**Issue**: Units missing from generated content
```yaml
density: 8.9
# Missing densityUnit
```

**Solution**: Verify that the material data includes unit information or ranges are properly configured.

## 📈 Version History

- **v6.1.0**: Unit/value separation implementation
  - Added numeric-only value format
  - Enhanced UnifiedPropertyEnhancementService
  - Updated schema validation
  - Comprehensive test coverage
  
- **v6.0.0**: Pure AI research system
- **v3.0.0**: Root-level frontmatter architecture
- **v2.0.0**: Streamlined generator implementation