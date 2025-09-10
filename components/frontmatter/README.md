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

### Hybrid Data Integration
The frontmatter component uses a **hybrid approach** that combines data from multiple sources:

#### 1. Material Data Source (`data/materials.yaml`)
- **Primary Data:** Material properties, formulas, symbols, categories
- **Author References:** `author_id` links to complete author profiles
- **Laser Parameters:** Wavelength, power ranges, fluence thresholds
- **Application Data:** Industry uses and surface treatment methods

#### 2. Prompt Template (`components/frontmatter/prompt.yaml`)
- **Template Structure:** Pre-defined YAML frontmatter format
- **Variable Substitution:** Dynamic replacement with material-specific data
- **Property Placeholders:** Template variables for density, melting point, etc.
- **Author Integration:** Complete author object embedding

#### 3. Author Database (`authors.json`)
- **Complete Profiles:** Full author information with expertise, country, etc.
- **Dynamic Resolution:** `author_id` to complete author object conversion
- **Cultural Adaptation:** Country-specific writing styles and perspectives

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

## Version Information Integration

### Architecture
The frontmatter component integrates with the centralized versioning system (`versioning/generator.py`) to provide consistent version tracking across all components.

### Version Information Structure
Generated frontmatter files contain three distinct sections:

1. **YAML Frontmatter Section**
   ```yaml
   ---
   name: "Material Name"
   # ... frontmatter content ...
   ---
   ```

2. **Version Information Comments**
   ```markdown
   # Version Information
   # Generated: 2025-09-10T13:23:40.671545
   # Material: Alumina
   # Component: frontmatter
   # Generator: Z-Beam v1.0.0
   # Platform: Darwin (3.12.4)
   ```

3. **Version Log Section**
   ```yaml
   ---
   Version Log - Generated: 2025-09-10T13:23:40.671714
   Material: Alumina
   Component: frontmatter
   Generator: Z-Beam v2.1.0
   Author: AI Assistant
   Platform: Darwin (3.12.4)
   File: content/components/frontmatter/alumina-laser-cleaning.md
   ---
   ```

### Versioning Integration
- Version information is **automatically appended** by `versioning/generator.py`
- **No manual version handling** required in frontmatter component
- **Consistent format** across all Z-Beam components
- **Fail-fast architecture** ensures version information is always present

### Post-Processing
The post-processor ensures:
- ✅ Clean YAML frontmatter with proper boundaries
- ✅ Preservation of version information sections
- ✅ Proper formatting and structure validation
- ✅ No duplication or conflicts with versioning system

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

### ✅ **Formula as Symbol Fallback**
- **FIXED**: When `symbol` field is missing, the system now uses `formula` as fallback
- **Example**: Quartzite with `formula: SiO2` will use `SiO2` for both formula and symbol fields
- **Logging**: System logs when formula is used as symbol fallback for transparency

### ✅ **Fail-Fast Architecture**
- Validates all required configurations and data before generation
- No fallback values or mock data in production
- Clear error messages for missing dependencies

## Data Flow

### Hybrid Integration Process

#### 1. Material Data Loading
```yaml
# From data/materials.yaml
materials:
  metal:
    items:
    - name: Steel
      author_id: 3
      formula: Fe-C
      symbol: Fe
      category: metal
      laser_parameters:
        fluence_threshold: "1.0–10 J/cm²"
        wavelength_optimal: 1064nm
        power_range: 50-200W
```

#### 2. Author Resolution
```json
// From authors.json (resolved via author_id: 3)
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

#### 3. Template Integration
```yaml
# From components/frontmatter/prompt.yaml
template: |
  ---
  name: "{subject}"
  applications:
  - industry: "Electronics Manufacturing"
    detail: "Removal of surface oxides and contaminants from {subject} substrates"
  author: "{author_name}"
  author_object:
    id: {author_id}
    name: "{author_name}"
    country: "{author_object_country}"
    expertise: "{author_object_expertise}"
  category: "{category}"
  chemicalProperties:
    symbol: "{material_symbol}"
    formula: "{material_formula}"
  ---
```

#### 4. Variable Substitution
The system performs comprehensive variable replacement:
- **Material Variables:** `{subject}`, `{material_formula}`, `{material_symbol}`
- **Author Variables:** `{author_name}`, `{author_object_country}`, `{author_object_expertise}`
- **Category Variables:** `{category}` for material classification
- **Dynamic Properties:** Material-specific property values from materials.yaml

#### 5. Property Enhancement
Post-processing adds contextual property data:
```yaml
properties:
  density: "7.85 g/cm³"  # From materials.yaml
  densityMin: "7.0 g/cm³"  # Calculated from category ranges
  densityMax: "8.0 g/cm³"  # Calculated from category ranges
  densityPercentile: 75.5  # Statistical ranking
```

#### 6. Validation
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
- **Prompt Length**: Current template generates ~4100 characters (above optimal 2000-3000 range)
- **Token Usage**: ~2,008 tokens for comprehensive generation
- **Response Time**: Mock API: ~0.022s, Live API: Expected 10-1000x slower
- **Reliability Issue**: Prompts >4000 chars may cause live API failures

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

#### 1.5. Symbol Field Missing (AUTO-FIXED)
```
Error: Material data missing required 'symbol' field
```
**Solution**: System automatically uses `formula` as fallback for missing `symbol` field

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

### API Troubleshooting

#### Why Mock Works But Live API Fails

**Root Cause:** Prompt complexity and connection reliability differences

**Mock Scenario:**
- Uses simple `Mock()` objects with instant responses
- No network latency or connection issues
- Always returns success with predefined content
- No token limits or rate limiting

**Live API Scenario:**
- Uses complex prompts (3000+ characters)
- Network latency and connection reliability issues
- Token limits and rate limiting
- API service availability and timeouts

**Evidence from Testing:**
```python
# This works (Mock)
mock_client = Mock()
mock_client.generate_simple.return_value = Mock(success=True, content='response')

# This fails (Live API with complex prompts)
# Connection error after 2 attempts
```

#### API Connection Failure Solutions

**1. Prompt Optimization:**
- Keep prompts under 2000 characters for reliability
- Test with simple prompts first
- Monitor token usage and response times
- Use optimized prompt templates

**2. Connection Reliability:**
- Implement retry logic with exponential backoff
- Handle network timeouts gracefully
- Monitor API service status
- Use connection pooling for multiple requests

**3. Error Handling:**
```python
try:
    response = api_client.generate_simple(prompt)
    if not response.success:
        # Log detailed error information
        logger.error(f"API call failed: {response.error}")
        # Implement fallback or retry logic
except Exception as e:
    logger.error(f"API connection error: {e}")
    # Handle connection failures
```

**4. Testing Strategy:**
- Test with mock clients for unit tests
- Test with live API for integration tests
- Monitor API performance metrics
- Implement circuit breaker pattern for reliability

#### Performance Comparison: Mock vs Live API

| Aspect | Mock API | Live API |
|--------|----------|----------|
| **Response Time** | ~0.022s per request | Expected 0.2-20s per request |
| **Reliability** | 100% | 95-99% (depends on prompt size) |
| **Token Usage** | 0 | 1000-2000 |
| **Network Dependency** | None | Required |
| **Cost** | Free | Per token |
| **Prompt Size Limit** | Unlimited | ~4000 chars (current: 4118) |
| **Performance Ratio** | 1x (baseline) | 10-1000x slower |

#### Debug Mode
Enable debug logging for detailed troubleshooting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## API Integration Testing

### Missing Test Coverage (FIXED)

**Previously Missing Tests:**
```python
# These critical tests were missing from the original test suite
@patch('api.client_factory.APIClientFactory.create_client')
def test_api_client_factory_mock_integration(self, mock_create_client):
    """Test factory method with use_mock=True"""

@patch('api.client_factory.APIClientFactory.create_client')  
def test_api_client_factory_live_integration(self, mock_create_client):
    """Test factory method with use_mock=False"""
```

**Now Available:**
- ✅ API client factory integration tests
- ✅ Mock vs live API scenario comparisons
- ✅ Prompt size optimization validation
- ✅ Connection failure simulation tests

### Running API Integration Tests
```bash
# Run all frontmatter tests including new API integration tests
python3 -m pytest components/frontmatter/tests.py components/frontmatter/api_integration_tests.py -v

# Run only API integration tests
python3 -m pytest components/frontmatter/api_integration_tests.py -v
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

### v4.1.1 (September 10, 2025)
- ✅ **ENHANCED**: Version information integration with centralized versioning system
- ✅ **IMPROVED**: Post-processor handling of version sections and YAML formatting
- ✅ **ADDED**: Comprehensive test coverage for version information workflows
- ✅ **FIXED**: Clean separation between YAML frontmatter and version metadata
- ✅ **DOCUMENTED**: Version information architecture and integration patterns

### v4.1.0 (September 9, 2025)
- ✅ **FIXED**: Formula fallback for missing symbol field
- ✅ **ENHANCED**: Automatic symbol resolution using formula when symbol is unavailable
- ✅ **IMPROVED**: Better error handling and logging for symbol/formula resolution

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
