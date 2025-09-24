# Frontmatter API Reference

## StreamlinedFrontmatterGenerator

Main class for frontmatter generation with consolidated architecture.

### Constructor
```python
StreamlinedFrontmatterGenerator()
```
No configuration required - uses embedded services and validation.

### Methods

#### `generate_from_material_name(material_name: str, api_client=None) -> ComponentResult`
Generates complete frontmatter for a material by name.

**Parameters:**
- `material_name` (str): Name of the material to generate frontmatter for
- `api_client` (optional): API client for content generation

**Returns:**
- `ComponentResult`: Object containing generated frontmatter content and metadata

**Example:**
```python
generator = StreamlinedFrontmatterGenerator()
result = generator.generate_from_material_name("Titanium")
print(result.content)  # YAML frontmatter content
```

#### `_generate_from_materials_data(material_data: dict, material_name: str) -> dict`
Internal method for generating frontmatter from materials.yaml data.

**Parameters:**
- `material_data` (dict): Material data from materials.yaml
- `material_name` (str): Name of the material

**Returns:**
- `dict`: Frontmatter data dictionary

#### `_generate_content_metadata(material_data: dict, material_name: str) -> dict`
Generates content metadata section (title, headline, description, keywords).

#### `_generate_properties_with_ranges(material_data: dict) -> dict`
Generates properties section with min/max ranges from category data.

#### `_generate_machine_settings_with_ranges(material_data: dict) -> dict`
Generates machine settings section with parameter ranges.

#### `_generate_author_object(material_data: dict) -> dict`
Resolves author information from author_id to complete author object.

#### `_generate_images_section(material_name: str) -> dict`
Generates images section with hero and micro images for the material.

**Parameters:**
- `material_name` (str): Name of the material

**Returns:**
- `dict`: Images section with 'hero' and 'micro' objects containing 'alt' and 'url'

**Example:**
```python
images = generator._generate_images_section("Aluminum")
# Returns:
# {
#   'hero': {
#     'alt': 'Aluminum surface undergoing laser cleaning showing precise contamination removal',
#     'url': '/images/aluminum-laser-cleaning-hero.jpg'
#   },
#   'micro': {
#     'alt': 'Microscopic view of Aluminum surface after laser cleaning showing detailed surface structure', 
#     'url': '/images/aluminum-laser-cleaning-micro.jpg'
#   }
# }
```

**Image URL Patterns:**
- Hero images: `/images/{material-name}-laser-cleaning-hero.jpg`
- Micro images: `/images/{material-name}-laser-cleaning-micro.jpg`
- Material names are converted to lowercase and spaces become hyphens

**Alt Text Patterns:**
- Hero: `"{Material Name} surface undergoing laser cleaning showing precise contamination removal"`
- Micro: `"Microscopic view of {Material Name} surface after laser cleaning showing detailed surface structure"`

#### `_format_as_yaml(frontmatter_data: dict) -> str`
Formats frontmatter data as proper YAML with frontmatter delimiters.

---

## UnifiedPropertyEnhancementService

Consolidated service for property and machine settings enhancement.

### Static Methods

#### `add_properties(frontmatter_data: dict, preserve_min_max: bool = True) -> None`
Enhances frontmatter with property data.

**Parameters:**
- `frontmatter_data` (dict): Frontmatter data to enhance
- `preserve_min_max` (bool): Whether to preserve existing min/max values

**Example:**
```python
UnifiedPropertyEnhancementService.add_properties(frontmatter, preserve_min_max=True)
```

#### `add_machine_settings(machine_settings: dict, use_optimized: bool = True) -> None`
Enhances machine settings with parameter data.

**Parameters:**
- `machine_settings` (dict): Machine settings data to enhance
- `use_optimized` (bool): Whether to use optimized format

#### `apply_full_optimization(frontmatter: dict, use_optimized: bool = True) -> dict`
Applies complete optimization to frontmatter data.

**Parameters:**
- `frontmatter` (dict): Complete frontmatter data
- `use_optimized` (bool): Whether to use optimized format

**Returns:**
- `dict`: Statistics about optimization applied

#### `remove_redundant_sections(frontmatter: dict) -> dict`
Removes redundant or duplicate sections from frontmatter.

#### `**Returns:**
- `tuple[float, str]`: Numeric value and unit string

---

## Image Generation

The frontmatter generator automatically creates image sections for all materials following consistent patterns.

### Image Structure
Each material gets two images with standardized naming and alt text:

```yaml
images:
  hero:
    alt: "{Material} surface undergoing laser cleaning showing precise contamination removal"
    url: "/images/{material-name}-laser-cleaning-hero.jpg"
  micro:
    alt: "Microscopic view of {Material} surface after laser cleaning showing detailed surface structure"
    url: "/images/{material-name}-laser-cleaning-micro.jpg"
```

### URL Naming Conventions
- **Base Pattern**: `/images/{material-name}-laser-cleaning-{type}.jpg`
- **Material Name Processing**:
  - Convert to lowercase
  - Replace spaces with hyphens
  - Preserve alphanumeric characters and hyphens
  - Remove special characters

**Examples:**
- "Aluminum" → `/images/aluminum-laser-cleaning-hero.jpg`
- "Stainless Steel" → `/images/stainless-steel-laser-cleaning-hero.jpg`
- "Ti-6Al-4V" → `/images/ti-6al-4v-laser-cleaning-hero.jpg`

### Alt Text Templates
**Hero Image Alt Text:**
- Template: `"{Material Name} surface undergoing laser cleaning showing precise contamination removal"`
- Example: `"Titanium surface undergoing laser cleaning showing precise contamination removal"`

**Micro Image Alt Text:**
- Template: `"Microscopic view of {Material Name} surface after laser cleaning showing detailed surface structure"`
- Example: `"Microscopic view of Titanium surface after laser cleaning showing detailed surface structure"`

### N/A Fallback Handling
When image generation fails, the N/A field normalizer provides fallback structure:

```yaml
images:
  hero:
    alt: "{Material Name} surface laser cleaning (N/A)"
    url: "/images/placeholder-hero.jpg"
  micro:
    alt: "Microscopic view of {Material Name} surface (N/A)"
    url: "/images/placeholder-micro.jpg"
```

---

## ValidationHelpers`
Extracts numeric value and unit from a string.

**Parameters:**
- `value_str` (str): String containing numeric value with unit (e.g., "7.85 g/cm³")

**Returns:**
- `tuple`: (numeric_value, unit_string)

**Example:**
```python
value, unit = UnifiedPropertyEnhancementService._extract_numeric_and_unit("7.85 g/cm³")
# Returns: (7.85, "g/cm³")
```

---

## FieldOrderingService

Service for consistent field ordering in frontmatter.

### Static Methods

#### `apply_field_ordering(frontmatter_data: dict) -> dict`
Applies standardized field ordering to frontmatter data.

**Parameters:**
- `frontmatter_data` (dict): Frontmatter data to order

**Returns:**
- `dict`: Frontmatter data with standardized field ordering

**Field Order:**
1. Basic Identification (name, category)
2. Content Metadata (title, headline, description, keywords)
3. Chemical Properties (chemicalProperties)
4. Physical Properties (properties)
5. Composition & Applications (composition, applications)
6. Machine Settings (machineSettings)
7. Standards & Compatibility (compatibility, regulatoryStandards)
8. Author & Visual Assets (author_object)
9. Impact Metrics (environmentalImpact)

#### `_create_clean_properties_structure(properties: dict) -> dict`
Creates clean, organized structure for properties section.

#### `_create_clean_machine_settings_structure(machine_settings: dict) -> dict`
Creates clean, organized structure for machine settings section.

---

## ValidationHelpers

GROK-compliant validation helpers for content validation.

### Static Methods

#### `validate_and_enhance_content(content: str, material_data: dict, api_client) -> tuple[str, dict]`
Validates and enhances frontmatter content.

**Parameters:**
- `content` (str): Raw frontmatter content
- `material_data` (dict): Material data for validation
- `api_client`: API client for enhancement

**Returns:**
- `tuple`: (validated_content, validation_report)

#### `extract_yaml_from_content(content: str) -> dict`
Extracts YAML frontmatter from content string.

#### `validate_required_fields(frontmatter_data: dict) -> list`
Validates presence of required frontmatter fields.

---

## ComponentResult

Result object returned by generation methods.

### Attributes
- `content` (str): Generated frontmatter content
- `success` (bool): Whether generation was successful
- `error` (str, optional): Error message if generation failed
- `metadata` (dict, optional): Additional metadata about generation

### Methods

#### `is_success() -> bool`
Returns whether the generation was successful.

#### `get_content() -> str`
Returns the generated content.

#### `get_error() -> str`
Returns error message if generation failed.

---

## Usage Examples

### Basic Frontmatter Generation
```python
from components.frontmatter.core.streamlined_generator import StreamlinedFrontmatterGenerator

# Initialize generator
generator = StreamlinedFrontmatterGenerator()

# Generate frontmatter for a material
result = generator.generate_from_material_name("Steel")

if result.is_success():
    print("Generated frontmatter:")
    print(result.get_content())
else:
    print(f"Generation failed: {result.get_error()}")
```

### Advanced Property Enhancement
```python
from components.frontmatter.enhancement.unified_property_enhancement_service import UnifiedPropertyEnhancementService

# Create frontmatter data
frontmatter = {
    "name": "Steel",
    "properties": {
        "density": "7.85 g/cm³",
        "melting_point": "1370°C"
    }
}

# Enhance with full property breakdown
UnifiedPropertyEnhancementService.add_properties(frontmatter, preserve_min_max=False)

# Result includes numeric values, units, and ranges
print(frontmatter["properties"])
# {
#   "density": "7.85 g/cm³",
#   "densityNumeric": 7.85,
#   "densityUnit": "g/cm³",
#   "densityMin": "0.53 g/cm³",
#   "densityMax": "22.59 g/cm³"
# }
```

### Custom Field Ordering
```python
from components.frontmatter.ordering.field_ordering_service import FieldOrderingService

# Unordered frontmatter data
data = {
    "applications": ["aerospace", "automotive"],
    "name": "Aluminum", 
    "chemicalProperties": {"formula": "Al", "symbol": "Al"},
    "category": "metal"
}

# Apply standard field ordering
ordered_data = FieldOrderingService.apply_field_ordering(data)

# Result follows standard order: name, category, chemicalProperties, applications
print(list(ordered_data.keys()))
# ['name', 'category', 'chemicalProperties', 'applications']
```

### Error Handling
```python
from components.frontmatter.core.streamlined_generator import StreamlinedFrontmatterGenerator

generator = StreamlinedFrontmatterGenerator()

try:
    result = generator.generate_from_material_name("InvalidMaterial")
    if not result.is_success():
        print(f"Generation failed: {result.get_error()}")
except ValueError as e:
    print(f"Validation error: {e}")
except KeyError as e:
    print(f"Missing required data: {e}")
```

---

## Configuration

### Environment Variables
- `MATERIALS_YAML_PATH`: Path to materials.yaml file (default: `data/materials.yaml`)
- `AUTHORS_JSON_PATH`: Path to authors.json file (default: `authors.json`)

### Default Paths
```python
# Materials data
materials_path = "data/materials.yaml"

# Authors data  
authors_path = "authors.json"

# Schema validation
schema_path = "schemas/frontmatter.json"
```

### Logging Configuration
```python
import logging

# Enable debug logging for detailed output
logging.basicConfig(level=logging.DEBUG)

# Component-specific logger
logger = logging.getLogger('components.frontmatter')
logger.setLevel(logging.INFO)
```

---

## Error Reference

### Common Exceptions

#### `ValueError`
- Missing required material data
- Invalid material name format
- Missing required fields in materials.yaml

#### `KeyError`
- Missing required keys in material data
- Missing author_id in material data
- Missing required frontmatter fields

#### `FileNotFoundError`
- materials.yaml file not found
- authors.json file not found
- Schema file not found

#### `yaml.YAMLError`
- Invalid YAML syntax in materials.yaml
- Malformed frontmatter content

### Error Handling Best Practices
```python
# Always check result success
result = generator.generate_from_material_name("Material")
if result.is_success():
    # Process successful result
    content = result.get_content()
else:
    # Handle failure
    error = result.get_error()
    logger.error(f"Generation failed: {error}")

# Use try-catch for validation errors
try:
    result = generator.generate_from_material_name("Material")
except ValueError as e:
    logger.error(f"Validation error: {e}")
except KeyError as e:
    logger.error(f"Missing data: {e}")
```
