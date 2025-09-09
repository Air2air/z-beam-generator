# Frontmatter Component

## Overview
The frontmatter component generates comprehensive YAML frontmatter for laser cleaning articles with full author object integration, property enhancement, and fail-fast validation architecture.

## 🆕 **RECENT FIXES - September 8, 2025**

### ✅ **Template Variable Replacement Fix**

**Issue:** Steel and Copper frontmatter files contained generic placeholders instead of material-specific values.

**Root Cause:** Material data wasn't being loaded correctly from `materials.yaml` due to incorrect data structure access.

**Solution:** Fixed `DynamicGenerator` to properly access the nested materials structure:
```yaml
materials:
  metal:
    items:
    - name: Steel
      formula: Fe-C
      symbol: Fe
```

**Before Fix:**
```yaml
name: "Advanced Material"
chemical_formula: "Unknown"
material_symbol: "Unk"
```

**After Fix:**
```yaml
name: "Steel"
chemical_formula: "Fe-C"
material_symbol: "Fe"
```

**Status:** ✅ Template variable replacement is working correctly. Material data loads properly and populates template variables with correct values.

### ✅ **Author Object Resolution Fix**

**Issue:** Frontmatter was using placeholder author information instead of resolved author objects.

**Root Cause:** Author resolution logic wasn't properly integrated with the template variable system.

**Solution:** Enhanced `_create_template_vars()` method to resolve `author_id` from materials data to full author objects from `authors.json`.

**Before Fix:**
```yaml
author: "Dr. Sarah Chen"
author_object:
  id: 1
  name: "Dr. Sarah Chen"
  sex: "unknown"
  title: "Materials Science Expert"
  country: "China"
```

**After Fix:**
```yaml
author: "Ikmanda Roswati"
author_object:
  id: 3
  name: "Ikmanda Roswati"
  sex: "m"
  title: "Ph.D."
  country: "Indonesia"
  expertise: "Ultrafast Laser Physics and Material Interactions"
  image: "/images/author/ikmanda-roswati.jpg"
```

**Status:** ✅ Author object resolution is working correctly. All author fields are properly populated from the authors database.

## Architecture

### Fail-Fast Design Principles
- **No Mocks or Fallbacks**: System fails immediately if dependencies are missing
- **Explicit Dependencies**: All required components must be explicitly provided
- **Component Architecture**: Uses ComponentGeneratorFactory pattern for all generators
- **Fail-Fast Validation**: Validates configurations and inputs immediately

### Core Components

#### 1. FrontmatterComponentGenerator
Main generator class that extends `APIComponentGenerator`:
- Loads optimized prompt configuration from `prompt.yaml`
- Creates template variables with material and author data
- Builds API prompts with variable substitution
- Post-processes content with property enhancement

#### 2. Template Variable System
Comprehensive variable substitution system:
```python
template_vars = {
    "subject": material_name,                    # "Steel"
    "subject_lowercase": subject_lowercase,     # "steel"
    "subject_slug": subject_slug,               # "steel"
    "material_formula": formula,                # "Fe-C"
    "material_symbol": symbol,                  # "Fe"
    "material_type": material_type,             # "ferrous alloy"
    "category": category,                       # "metal"
    "author_name": author_name,                 # "Ikmanda Roswati"
    "author_object_sex": sex,                   # "m"
    "author_object_title": title,               # "Ph.D."
    "author_object_country": country,           # "Indonesia"
    "author_object_expertise": expertise,       # "Ultrafast Laser Physics..."
    "author_object_image": image,               # "/images/author/ikmanda-roswati.jpg"
    "persona_country": country,                 # "Indonesia"
    "author_id": author_id,                     # 3
    "timestamp": timestamp,                     # "2025-09-08T10:30:00Z"
}
```

#### 3. Author Resolution System
Automatic author resolution from materials data:
1. Extracts `author_id` from material data
2. Resolves to full author object using `get_author_by_id()`
3. Validates all required author fields
4. Fails fast if author data is incomplete

#### 4. Property Enhancement System
Post-processing enhancement with percentile calculations:
- Loads category ranges from `data/category_ranges.yaml`
- Calculates min/max values and percentiles for properties
- Enhances frontmatter with contextual property data

## Features

### ✅ **Author Resolution**
- Automatically resolves author_id from materials.yaml to full author objects from authors.json
- Includes all author fields (name, sex, title, country, expertise, image)
- Fail-fast validation ensures complete author information

### ✅ **Complete Author Information**
The frontmatter now includes a complete `author_object` with all fields from the authors database:

```yaml
author: "Alessandro Moretti"
author_object:
  id: 2
  name: "Alessandro Moretti"
  sex: "m"
  title: "Ph.D."
  country: "Italy"
  expertise: "Laser-Based Additive Manufacturing"
  image: "/images/author/alessandro-moretti.jpg"
```

### ✅ **Property Enhancement**
- Integrates material property data with percentile calculations
- Adds min/max context for all properties
- Calculates percentile rankings within material categories

### ✅ **Template Variable Replacement**
- ✅ FIXED - Properly replaces placeholders with material-specific data
- Supports comprehensive variable substitution
- Fail-fast validation for missing template variables

### ✅ **Fail-Fast Architecture**
- Validates all required configurations and data before generation
- No fallback values or mock data in production
- Clear error messages for missing dependencies

## Data Flow

### 1. Material Data Loading
```python
# From materials.yaml
materials:
  metal:
    items:
    - name: Steel
      author_id: 3
      formula: Fe-C
      symbol: Fe
      category: metal
```

### 2. Author Resolution
```python
# From authors.json
{
  "authors": [
    {
      "id": 3,
      "name": "Ikmanda Roswati",
      "sex": "m",
      "title": "Ph.D.",
      "country": "Indonesia",
      "expertise": "Ultrafast Laser Physics and Material Interactions",
      "image": "/images/author/ikmanda-roswati.jpg"
    }
  ]
}
```

### 3. Template Integration
All author fields are included in the frontmatter template with proper variable substitution.

### 4. Property Enhancement
Post-processing adds contextual property data:
```yaml
properties:
  density: "7.85 g/cm³"
  densityMin: "7.0 g/cm³"
  densityMax: "8.0 g/cm³"
  densityPercentile: 75.5
```

### 5. Validation
Fail-fast validation ensures all required data is present and properly formatted.

## Configuration Files

### prompt.yaml
Optimized template with comprehensive variable substitution:
- Pre-filled YAML structure with specific values
- Template variables for material-specific customization
- Optimized length (692 characters) for API compatibility

### authors.json
Author database with complete profiles:
```json
{
  "id": 3,
  "name": "Ikmanda Roswati",
  "sex": "m",
  "title": "Ph.D.",
  "country": "Indonesia",
  "expertise": "Ultrafast Laser Physics and Material Interactions",
  "image": "/images/author/ikmanda-roswati.jpg"
}
```

### materials.yaml
Material data with author_id references:
```yaml
- name: Steel
  author_id: 3
  formula: Fe-C
  symbol: Fe
  category: metal
```

## Usage Examples

### Basic Generation
```python
from components.frontmatter.generator import FrontmatterComponentGenerator

generator = FrontmatterComponentGenerator()
result = generator.generate(
    material_name="Steel",
    material_data={
        "name": "Steel",
        "author_id": 3,
        "formula": "Fe-C",
        "symbol": "Fe",
        "category": "metal"
    },
    api_client=api_client
)
```

### With Author Info Override
```python
result = generator.generate(
    material_name="Steel",
    material_data=material_data,
    api_client=api_client,
    author_info={
        "name": "Custom Author",
        "country": "Custom Country",
        "id": 999
    }
)
```

### Dynamic Generation
```python
from generators.workflow_manager import run_dynamic_generation

result = run_dynamic_generation(
    generator=generator,
    material="Steel",
    component_types=["frontmatter"],
    author_info={"name": "Ikmanda Roswati", "country": "Indonesia", "id": 3}
)
```

## Error Handling

### Configuration Errors
- **Missing prompt configuration**: Raises ConfigurationError
- **Invalid template variables**: Raises ValidationError with specific field details
- **Missing material data**: Raises Exception with fail-fast message

### Author Resolution Errors
- **Missing author_id**: Raises Exception requiring complete author information
- **Invalid author_id**: Raises Exception with resolution failure details
- **Incomplete author data**: Raises Exception for missing required fields

### API Errors
- **API client not provided**: Raises DependencyError
- **API call failures**: Raises APIError with retry information
- **Token limit exceeded**: Raises ValidationError for prompt length

## Testing

### Running Tests
```bash
# Run all frontmatter tests
python3 -m pytest components/frontmatter/tests.py -v

# Run specific test categories
python3 -m pytest components/frontmatter/tests.py::TestFrontmatterGenerator::test_author_resolution -v
python3 -m pytest components/frontmatter/tests.py::TestFrontmatterValidator::test_yaml_validation -v
```

### Test Coverage
- ✅ Author resolution and validation
- ✅ Template variable substitution
- ✅ YAML format validation
- ✅ Property enhancement
- ✅ Error handling scenarios
- ✅ API integration testing
- ✅ Fail-fast validation

## File Structure

```
components/frontmatter/
├── README.md              # This documentation
├── __init__.py           # Package initialization
├── generator.py          # Main generator class
├── mock_generator.py     # Mock implementation for testing
├── post_processor.py     # Content post-processing utilities
├── prompt.yaml           # Optimized prompt template
├── prompt_simple.yaml    # Legacy simple prompt
├── tests.py              # Comprehensive test suite
├── utils.py              # Utility functions
├── validator.py          # Validation logic
└── example_frontmatter.md # Example output
```

## Dependencies

### Required
- `generators.component_generators.APIComponentGenerator`
- `utils.get_author_by_id`
- `utils.property_enhancer`
- `utils.validation`
- `utils.percentile_calculator`
- `pathlib.Path`
- `yaml`
- `logging`

### Optional
- `utils.loud_errors` (for enhanced error reporting)

## Performance Characteristics

### API Optimization
- **Prompt Length**: Optimized from 5,285 to 692 characters (87% reduction)
- **Token Usage**: ~2,008 tokens for comprehensive generation
- **Response Time**: 35-45 seconds for complete frontmatter generation

### Memory Usage
- **Template Variables**: Minimal memory footprint
- **Property Enhancement**: Loads category ranges on demand
- **Author Resolution**: Cached author lookups

### Scalability
- **Concurrent Generation**: Supports parallel processing
- **Batch Processing**: Efficient for multiple materials
- **Resource Cleanup**: Automatic cleanup of temporary data

## Troubleshooting

### Common Issues

#### 1. Template Variable Errors
```
Error: Missing template variable: material_formula
```
**Solution**: Ensure material data includes `formula` field in materials.yaml

#### 2. Author Resolution Failures
```
Error: Failed to resolve author_id 3
```
**Solution**: Verify author exists in authors.json with all required fields

#### 3. YAML Validation Errors
```
Error: Invalid YAML syntax
```
**Solution**: Check for proper indentation and quote escaping in template

#### 4. API Token Limit Exceeded
```
Error: Token limit exceeded
```
**Solution**: Use optimized prompt.yaml instead of prompt_simple.yaml

### Debug Mode
Enable debug logging for detailed troubleshooting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

### Planned Features
- **Dynamic Property Ranges**: Real-time calculation of property percentiles
- **Multi-language Support**: Localized author information
- **Template Versioning**: Support for multiple prompt versions
- **Performance Monitoring**: Built-in metrics and profiling

### Architecture Improvements
- **Plugin System**: Extensible validation and enhancement plugins
- **Caching Layer**: Redis-based caching for author and material data
- **Async Processing**: Non-blocking generation for high-throughput scenarios

## Contributing

### Code Standards
- Follow fail-fast architecture principles
- Include comprehensive error handling
- Add unit tests for all new features
- Update documentation for API changes

### Testing Guidelines
- Test all error conditions
- Validate YAML output format
- Test with real API clients (no mocks)
- Include performance benchmarks

## Version History

### v4.0.0 (September 8, 2025)
- ✅ Fixed template variable replacement
- ✅ Enhanced author object resolution
- ✅ Optimized prompt length (87% reduction)
- ✅ Added comprehensive property enhancement
- ✅ Implemented fail-fast validation architecture

### v3.0.0
- Added author object integration
- Implemented property enhancement system
- Enhanced error handling and validation

### v2.0.0
- Initial comprehensive frontmatter generation
- Basic template variable system
- YAML validation and formatting

### v1.0.0
- Basic frontmatter generation
- Simple template system
- Initial validation framework
