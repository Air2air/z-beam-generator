# Frontmatter Component

The frontmatter component generates YAML frontmatter for laser cleaning materials with a **hierarchical structure** and clean unit separation.

## 🏗️ Hierarchical Architecture

### Core Principle
Frontmatter uses a **hierarchical structure** with `materialProperties` and `laserProcessing` instead of flat `properties`/`machineSettings`.

### Format Example
```yaml
# Modern Hierarchical Structure
materialProperties:
  chemical:
    formula: "Al"                    # Chemical composition
    symbol: "Al"                     # Chemical symbol
    chemicalFormula: "Al"            # Alternative notation
  physical:
    density: 2.7                     # Pure numeric (float)
    densityUnit: "g/cm³"            # Unit in separate field
    densityMin: 0.53                # Min range numeric
    densityMax: 22.59               # Max range numeric
  mechanical:
    tensileStrength: 310            # Pure numeric (int)
    tensileStrengthUnit: "MPa"      # Unit in separate field
    tensileStrengthMin: 70          # Min range numeric
    tensileStrengthMax: 2000        # Max range numeric
  thermal:
    thermalConductivity: 237        # Pure numeric (int)
    thermalConductivityUnit: "W/m·K" # Unit in separate field

laserProcessing:
  recommended:
    powerRange: 150.0               # Pure numeric (float)
    powerRangeUnit: "W"             # Unit in separate field
    powerRangeMin: 20.0             # Min range numeric
    powerRangeMax: 500.0            # Max range numeric
    wavelength: 1064.0              # Pure numeric (float)
    wavelengthUnit: "nm"            # Unit in separate field
    beamProfile: "Gaussian TEM00"   # Standard settings
    beamProfileOptions: 
      - "Gaussian TEM00"
      - "Top-hat"
      - "Donut"
      - "Multi-mode"
    safetyClass: "Class 4 (requires full enclosure)"
```

## 🏗️ Key Components

### StreamlinedFrontmatterGenerator

**Shared Generation Architecture**: Both `materialProperties` and `machineSettings` are generated using reusable, shared methods. The key distinction is their respective data categories:

- **materialProperties**: Uses material-specific category (e.g., 'metal', 'ceramic', 'polymer') for **fully dynamic property research** - no fallbacks or defaults allowed
- **machineSettings**: Uses 'machine' category for **AI-calculated laser parameter research** based on material properties - no fallbacks or defaults allowed

### Core Generation Methods

1. **`_generate_properties_with_ranges(material_data)`** → materialProperties
   - Calls shared `_create_datametrics_property()` with material category
   - Uses PropertyValueResearcher for AI-researched values
   - **100% Dynamic Property Discovery**: AI-powered MaterialPropertyResearchSystem determines which properties to research
   - **No Fallbacks**: System fails fast if property research is unavailable - no defaults or hardcoded lists
   - **Material Category Validation**: Properties validated against category-specific ranges from materials.yaml

2. **`_generate_machine_settings_with_ranges(material_data)`** → machineSettings  
   - Calls shared `_create_datametrics_property()` with 'machine' category
   - **Material-Based Calculations**: Uses researched material properties to calculate optimal laser parameters
   - **No Fallbacks**: System fails fast if material properties unavailable - no defaults or estimations
   - **Physics-Based Research**: AI calculates powerRange, wavelength based on material density, thermal properties
   - Settings optimized for specific material properties

3. **`_create_datametrics_property(value, prop_key, category)`** → Shared DataMetrics structure
   - **Reusable core method** used by both property types
   - Creates consistent structure: `{value, unit, confidence, min, max, description}`
   - Category parameter determines research methodology and ranges
Core generator with hierarchical structure and numeric extraction:

```python
from components.frontmatter.core.streamlined_generator import StreamlinedFrontmatterGenerator

generator = StreamlinedFrontmatterGenerator()
result = generator.generate("Aluminum")
```

**Key Methods:**
- `_extract_property_data()`: Unified extraction for values, ranges, and units
- `_generate_from_materials_data()`: Creates hierarchical materialProperties/laserProcessing structure
- `generate()`: Main entry point returning ComponentResult with YAML content

### Hierarchical Structure Benefits
- **Organized**: Properties grouped by category (chemical, physical, mechanical, thermal)
- **Extensible**: Easy to add new property categories or laser processing sections
- **Clear**: Logical separation between material properties and processing parameters
- **Schema-compliant**: Matches modern frontmatter.json schema requirements

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
        thermalConductivity: 401
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
properties = frontmatter_data.get('materialProperties', {})
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