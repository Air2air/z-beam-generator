# Z-Beam Dynamic Generation System Documentation

## Overview

The Z-Beam Dynamic Generation System is a comprehensive, schema-driven content generation platform that creates high-quality technical documentation for laser cleaning applications. The system uses dynamic field mapping from JSON schemas and provides flexible component selection for customized content generation.

## Key Features

### 🚀 Dynamic Schema-Driven Generation
- **Fully Dynamic Fields**: Content generation driven by JSON schema field mappings
- **Component-Specific Generation**: Each component type has optimized generation parameters
- **Material-Specific Adaptation**: Content automatically adapts based on material properties
- **Real-time Schema Integration**: Dynamic field extraction and content customization

### 🔧 Flexible Component Selection
- **Interactive Selection**: Users can choose specific components to generate
- **Batch Generation**: Generate all components or selected subsets
- **Component Validation**: Automatic validation of component availability
- **Progress Tracking**: Real-time generation progress and statistics

### ⚡ Standardized DeepSeek API Integration
- **Robust Error Handling**: Comprehensive retry logic and timeout management
- **Optimized Parameters**: Component-specific API parameters for optimal results
- **Statistics Tracking**: Detailed usage statistics and performance metrics
- **Mock Client Support**: Full testing capability without API keys

### 📊 Comprehensive Validation
- **Schema Compliance**: Automatic validation against JSON schema requirements
- **YAML Processing**: Post-processing and error correction for generated content
- **Real-time Feedback**: Immediate error detection and correction suggestions

## System Architecture

```
Z-Beam Dynamic Generation System
├── run.py                          # Main CLI interface
├── generators/
│   └── dynamic_generator.py        # Core dynamic generation engine
├── api/
│   ├── client.py                   # Standardized API client base
│   ├── deepseek.py                 # DeepSeek-specific optimizations
│   └── config.py                   # Configuration management
├── validators/
│   └── centralized_validator.py    # YAML validation and post-processing
├── schemas/                        # JSON schemas for dynamic field mapping
│   ├── material.json               # Material profile schema
│   ├── base.json                   # Base content schema
│   └── *.json                      # Additional schemas
└── components/                     # Component prompt templates
    ├── frontmatter/prompt.yaml     # Frontmatter generation prompts
    ├── content/prompt.yaml         # Article content prompts
    └── */prompt.yaml               # Other component prompts
```

## Usage Examples

### 1. Interactive Generation Mode
```bash
python3 run.py --interactive
```
- Guides users through material and component selection
- Real-time progress feedback and statistics
- Flexible generation workflow

### 2. Specific Material Generation
```bash
python3 run.py --material "Aluminum" --components "frontmatter,content"
```
- Generate specific components for a chosen material
- Supports comma-separated component lists
- Automatic validation and error reporting

### 3. Batch Generation
```bash
python3 run.py --material "Steel" --components all
```
- Generate all available components for a material
- Efficient batch processing with progress tracking

### 4. System Information
```bash
python3 run.py --list-materials     # List all available materials
python3 run.py --list-components    # List all available components
python3 run.py --test-api          # Test API connection
```

### 5. YAML Validation
```bash
python3 run.py --yaml
```
- Validate and fix YAML formatting issues
- Comprehensive error reporting and correction

## Component Types

The system supports 9 component types with specialized generation:

| Component | Description | Optimization |
|-----------|-------------|--------------|
| **frontmatter** | YAML metadata and properties | Low temperature (0.3) for structured data |
| **content** | Main article content | Balanced creativity (0.7) |
| **jsonld** | JSON-LD structured data | Very low temperature (0.2) for JSON |
| **table** | Technical specification tables | Structured output (0.3) |
| **metatags** | SEO meta tags and OpenGraph | Creative for SEO (0.4) |
| **tags** | Categorization tags | Moderate creativity (0.5) |
| **bullets** | Key feature bullet points | Good creativity (0.6) |
| **caption** | Image captions | Good creativity (0.6) |
| **propertiestable** | Material properties table | Structured output (0.3) |

## Schema-Driven Field Mapping

### Dynamic Field Configuration
The system extracts dynamic fields from JSON schemas:

```json
{
  "generatorConfig": {
    "contentGeneration": {
      "fieldContentMapping": {
        "properties": "Detail the physical and chemical properties of {subject} relevant to laser cleaning",
        "laserParameters": "Explain the optimal laser parameters for cleaning {subject}",
        "applications": "Describe the key applications where {subject} is processed"
      }
    }
  }
}
```

### Automatic Field Injection
- Fields are automatically injected into generation prompts
- Material-specific substitutions (`{subject}`, `{category}`)
- Dynamic instruction generation based on schema definitions

## API Client Features

### Standardized Configuration
```bash
export DEEPSEEK_API_KEY="your-api-key"
export DEEPSEEK_BASE_URL="https://api.deepseek.com"  # Optional
export DEEPSEEK_MODEL="deepseek-chat"                # Optional
export DEEPSEEK_MAX_TOKENS="4000"                   # Optional
export DEEPSEEK_TEMPERATURE="0.7"                   # Optional
```

### Advanced Features
- **Retry Logic**: Automatic retry with exponential backoff
- **Timeout Management**: Configurable connection and read timeouts
- **Statistics Tracking**: Comprehensive usage metrics
- **Error Handling**: Detailed error reporting and recovery
- **Mock Testing**: Full functionality testing without API calls

## Material Database

The system includes 122+ materials across 9 categories:

- **Metal**: Aluminum, Steel, Copper, etc.
- **Ceramic**: Porcelain, Zirconia, etc.
- **Composite**: Carbon Fiber, Fiberglass, etc.
- **Glass**: Borosilicate, Pyrex, etc.
- **Masonry**: Brick, Concrete, etc.
- **Plastic**: Various polymers
- **Semiconductor**: Silicon-based materials
- **Stone**: Natural stone materials
- **Wood**: Various wood types

## Performance Characteristics

### Generation Speed
- **Single Component**: 2-5 seconds per component
- **Full Material Set**: 20-60 seconds for all 9 components
- **Batch Processing**: Efficient parallel processing for multiple materials

### Quality Metrics
- **Schema Compliance**: 100% validation against JSON schemas
- **Content Quality**: Technical accuracy with industry-standard terminology
- **Consistency**: Standardized formatting across all components

## Testing and Validation

### Automated Testing
```bash
python3 test_dynamic_system.py
```
- Comprehensive system testing without API requirements
- Validation of all core functionality
- Performance and integration testing

### Manual Testing
```bash
# Test with mock client
python3 run.py --material "Aluminum" --components "frontmatter" --mock

# Test API connection
python3 run.py --test-api

# Interactive testing
python3 run.py --interactive
```

## Troubleshooting

### Common Issues

1. **API Key Not Set**
   ```
   Error: DEEPSEEK_API_KEY environment variable not set
   ```
   Solution: Set your DeepSeek API key in environment variables

2. **Component Not Found**
   ```
   Error: Invalid components: invalid_component
   ```
   Solution: Use `--list-components` to see available components

3. **Material Not Found**
   ```
   Error: Material MaterialName not found
   ```
   Solution: Use `--list-materials` to see available materials

### Debug Mode
```bash
python3 run.py --verbose --material "Aluminum" --components "frontmatter"
```
- Enables detailed logging
- Shows API request/response details
- Provides generation statistics

## Extension and Customization

### Adding New Components
1. Create `components/newcomponent/prompt.yaml`
2. Define component-specific prompts and parameters
3. Add component to available list (automatic detection)

### Adding New Materials
1. Edit `lists/materials.yaml`
2. Add material to appropriate category
3. System automatically detects new materials

### Custom Schemas
1. Create new JSON schema in `schemas/`
2. Define dynamic field mappings
3. Schema automatically loaded and integrated

## Best Practices

### For Content Generation
- Use specific, descriptive material names
- Select relevant components for your use case
- Review generated content for technical accuracy
- Post-process with YAML validation

### For API Usage
- Set appropriate timeout values for your connection
- Monitor API usage statistics
- Use mock client for development and testing
- Implement proper error handling in production

### For Schema Development
- Define clear, specific field mapping instructions
- Use material-specific placeholders (`{subject}`, `{category}`)
- Include comprehensive validation rules
- Test schema changes with mock generation

## Support and Maintenance

### Log Files
- Generation logs: Console output with timestamps
- Error logs: Detailed error information
- Statistics: API usage and performance metrics

### Updates and Maintenance
- Regular schema updates for new materials
- Component prompt optimization
- API client enhancements
- Performance monitoring and optimization

---

*Generated: August 21, 2025*
*Version: 2.0.0*
*Status: Production Ready ✅*
