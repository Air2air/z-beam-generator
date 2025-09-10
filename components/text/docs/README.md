# Text Component Documentation

This directory contains documentation for the core Z-Beam text generation component, focusing on basic content generation using the base content prompt system.

## Documentation Files

### 🏗️ [CONTENT_GENERATION_ARCHITECTURE.md](./CONTENT_GENERATION_ARCHITECTURE.md)
Core text generation architecture including:
- Component structure and relationships
- Basic generation process flow
- Simple prompt system details
- Error handling and validation
- Configuration management

### 📚 [API_REFERENCE.md](./API_REFERENCE.md)
Developer API reference including:
- Quick start examples
- Complete method documentation
- Data structure specifications
- Error handling patterns
- Best practices and integration examples

### 📖 [CASE_STUDIES.md](./CASE_STUDIES.md)
Basic generation examples and case studies including:
- Simple content generation examples
- Configuration validation testing
- Basic error handling demonstrations
- Performance benchmarking

## Quick Navigation

### For Developers
- **Getting Started:** See [API_REFERENCE.md](./API_REFERENCE.md) Quick Start section
- **Integration:** See [CONTENT_GENERATION_ARCHITECTURE.md](./CONTENT_GENERATION_ARCHITECTURE.md) Integration Points
- **Error Handling:** See [API_REFERENCE.md](./API_REFERENCE.md) Error Handling section

### For Content Creators
- **Basic Generation:** See [API_REFERENCE.md](./API_REFERENCE.md) for simple usage examples
- **Configuration:** See [CONTENT_GENERATION_ARCHITECTURE.md](./CONTENT_GENERATION_ARCHITECTURE.md) Configuration section
- **Examples:** See [CASE_STUDIES.md](./CASE_STUDIES.md) for generation examples

## System Overview

The text component is the core of the Z-Beam laser cleaning content generation system. It produces basic technical articles about laser cleaning using a **hybrid data integration approach** that combines material data from `data/materials.yaml` with template guidance from `components/text/prompts/base_content_prompt.yaml`.

### 🔧 **Core Technologies**
- **Hybrid Data Integration:** Combines materials.yaml data with prompt templates
- **Template Variable Substitution:** Dynamic content generation using material properties
- **Fail-Fast Architecture:** Immediate validation, no fallbacks
- **Single API Call:** Efficient generation per content piece
- **Configuration Validation:** Startup health checks

### 📊 **Key Features**
- **Material Data Integration:** Uses complete material properties from materials.yaml
- **Template-Driven Generation:** Structured prompts with variable substitution
- **Author Context:** Includes author information in generation context
- **Frontmatter Integration:** Incorporates frontmatter data for consistency
- **Error Handling:** Comprehensive error management with retry logic

### 🎯 **Generation Process**
1. **Validation Phase** - Fail-fast dependency checking (API client, material data, author info)
2. **Data Loading** - Load material properties from materials.yaml and prompt template
3. **Hybrid Integration** - Combine material data with template variables
4. **Context Building** - Include author information and frontmatter data
5. **Prompt Construction** - Build complete prompt with variable substitution
6. **API Generation** - Single API call with validation
7. **Content Formatting** - Return structured ComponentResult

## Usage Examples

### Basic Generation
```python
from components.text.generator import TextComponentGenerator

generator = TextComponentGenerator()
result = generator.generate(
    material_name="alabaster",
    material_data=material_data,
    api_client=api_client,
    author_info={'id': 2}
)

if result.success:
    print(result.content)
else:
    print(f"Error: {result.error_message}")
```

### With Quality Validation
```python
from components.text.generators.fail_fast_generator import create_fail_fast_generator

generator = create_fail_fast_generator(enable_scoring=False)  # Basic generation only
result = generator.generate(material_name, material_data, api_client)
```

## Hybrid Data Integration

### Data Sources

#### 1. Material Data (`data/materials.yaml`)
```yaml
materials:
  mineral:
    items:
    - name: alabaster
      author_id: 2
      formula: CaSO₄·2H₂O
      symbol: CaSO4
      category: mineral
      laser_parameters:
        fluence_threshold: "0.5–2.0 J/cm²"
        wavelength_optimal: 355nm
        power_range: 10-50W
```

#### 2. Template System (`components/text/prompts/base_content_prompt.yaml`)
```yaml
overall_subject: |
  A detailed technical analysis of the {material}, emphasizing its physicochemical properties, engineering applications, and the intricate mechanisms involved in laser cleaning processes...
```

#### 3. Author Information
```json
{
  "id": 2,
  "name": "Dr. Maria Santos",
  "country": "Brazil",
  "expertise": "Mineral Processing and Surface Engineering"
}
```

### Integration Process

#### Variable Substitution
The system performs dynamic variable replacement in the prompt template:
- **Material Variables:** `{material}` → actual material name (e.g., "alabaster")
- **Context Variables:** Material properties, author information, frontmatter data

#### Prompt Construction
```python
# Example of how variables are integrated
sections = [
    f"AUTHOR: {author_name}",
    f"COUNTRY: {author_country}",
    f"MATERIAL: {material_name}",
    f"MATERIAL DATA: {json.dumps(material_data)}",
    f"TASK: Write about laser cleaning of {material_name}...",
    formatted_template_content
]
```

#### Data Flow
1. **Material Resolution:** Extract material properties from materials.yaml
2. **Author Resolution:** Get author details using author_id
3. **Template Loading:** Load base_content_prompt.yaml
4. **Variable Substitution:** Replace {material} and other variables
5. **Context Integration:** Include author info and frontmatter data
6. **Prompt Assembly:** Combine all components into final prompt

## Quality Standards

### ✅ **Core Principles**
- **Fail-Fast:** System fails immediately if dependencies missing
- **No Fallbacks:** All dependencies must be explicitly provided
- **Simple Generation:** Basic content generation without optimization
- **Configuration Validation:** Required files must exist and be valid

### 📈 **Basic Metrics**
- **Generation Time:** <5 seconds per article
- **Success Rate:** >95% for valid configurations
- **Error Handling:** Comprehensive error reporting
- **Content Validity:** Basic structure validation

## Integration Points

### ComponentGeneratorFactory Integration
```python
# Factory discovery
ComponentGeneratorFactory.create_generator("text")

# Returns TextComponentGenerator instance
# Integrates with broader component system
```

### Basic Generation Flow
```python
# Simple generation without optimization
generator = TextComponentGenerator()
result = generator.generate(material_name, material_data, api_client)
```

## Support and Maintenance

### Common Issues
1. **Configuration Errors:** Missing base_content_prompt.yaml
2. **API Failures:** Network timeouts or API limits
3. **Validation Errors:** Invalid material data or author info

### Monitoring
- **Generation Success:** Track successful content generation
- **Error Rates:** Monitor error types and frequencies
- **Performance:** Generation time and API call metrics
- **Configuration Health:** Startup validation status

### Updates
- **Prompt Refinement:** Updates to base content guidance
- **Error Handling:** Enhanced error reporting and recovery
- **Performance:** Generation speed optimizations
- **Validation:** Improved input validation

---

For specific implementation details, see the individual documentation files above.

**Note:** For advanced optimization features including AI detection, persona management, and quality enhancement, see the optimizer documentation at `optimizer/text_optimization/docs/`.
