# JSON-LD Component Documentation

## Overview
The JSON-LD component generates comprehensive structured data in schema.org format for material laser cleaning pages. It provides rich machine-readable metadata for search engines and enhances SEO performance with multiple interconnected schema types.

**Latest Update (September 24, 2025)**: ✅ **ENHANCED COMPREHENSIVE JSON-LD SYSTEM** - Completely replaced simple Article-only schema with comprehensive multi-schema system including Article, Product, HowTo, BreadcrumbList, WebPage, Website, and FAQPage. Implemented dynamic placeholder substitution with real frontmatter data values.

## Key Features

### Multi-Schema Architecture (NEW)
- **Article Schema**: Main content with headlines, descriptions, author info
- **Product Schema**: Material properties and specifications
- **HowTo Schema**: Step-by-step laser cleaning instructions  
- **BreadcrumbList Schema**: SEO navigation hierarchy
- **WebPage Schema**: Page-level metadata and relationships
- **Website Schema**: Organization and search functionality
- **FAQPage Schema**: Material-specific questions and answers

### Dynamic Value Substitution
- **No Static Placeholders**: All `{{MATERIAL_NAME}}`, `{{LASER_WAVELENGTH}}` etc. replaced with real data
- **Frontmatter Integration**: Uses camelCase fields like `machineSettings`, `thermalConductivity`
- **10,500+ Characters**: Comprehensive content vs. ~800 characters in old system

## Key Files

### Core Implementation
- **`enhanced_generator.py`** - New comprehensive generator with dynamic substitution
- **`generator.py`** - Main component entry point (uses EnhancedJsonldGenerator)
- **`simple_generator.py`** - Legacy simple generator (deprecated)
- **`schemas/json-ld.json`** - Comprehensive schema template with placeholders
- **`validator.py`** - Updated validation supporting @graph structure
- **`prompt.yaml`** - Legacy template (Version 5.0.0)

## Usage

The component generates comprehensive JSON-LD structured data using frontmatter data:

```python
from components.jsonld.generator import JsonldComponentGenerator

# Create enhanced generator
generator = JsonldComponentGenerator()  # Uses EnhancedJsonldGenerator

# Generate comprehensive JSON-LD
result = generator.generate(
    material_name="Aluminum",
    material_data=material_data,
    frontmatter_data=frontmatter_data  # Required for dynamic substitution
)

# Access comprehensive result (10,500+ characters)
jsonld_content = result.content  # Contains all 7 schema types
```

## Implementation Details

### Enhanced Generator Class
The `EnhancedJsonldGenerator` class implements:

- **Dynamic Substitution**: Replaces all placeholders with real frontmatter values
- **Multi-Schema Generation**: Creates 7 interconnected schema.org types
- **Fallback Handling**: Graceful degradation if comprehensive schema fails
- **CamelCase Integration**: Uses `machineSettings`, `thermalConductivity`, etc.

### Schema Template System
The `schemas/json-ld.json` provides comprehensive template with:
- **Dynamic Placeholders**: `{{MATERIAL_NAME}}`, `{{LASER_WAVELENGTH}}`, etc.
- **Interconnected References**: Proper @id linking between schema types
- **SEO Optimization**: Rich metadata for search engines
- **Technical Specifications**: Material properties with proper units

### Validation
The `validator.py` file provides three main validation functions:
- **validate_jsonld_structure**: Supports both single entity and @graph structures
- **validate_jsonld_content**: Checks for actual placeholders (not JSON syntax)
- **validate_jsonld_schema**: Validates schema.org compliance and SEO best practices

## JSON-LD Schema Implementation

The component implements several schema.org types:
- **Article**: Main content type with headlines, description, etc.
- **Material**: Structured material properties and specifications
- **Process**: Laser cleaning process details
- **HowTo**: Step-by-step instructions for laser cleaning
- **ImageObject**: Enhanced image metadata
- **BreadcrumbList**: SEO navigation hierarchy

## SEO Benefits

- **Rich Results**: Enhanced visibility in search results
- **Knowledge Graph**: Integration with Google Knowledge Graph
- **Structured Data**: Machine-readable technical information
- **Navigation Enhancement**: Breadcrumb display in search results

## Best Practices

1. **Use Title Case for Material Names**: Ensure material names are properly capitalized
2. **Include Essential Fields**: headline, description, author, datePublished
3. **Provide Technical Properties**: Include detailed material properties with units
4. **Optimize Keywords**: Generate relevant keywords from material properties
5. **Add HowTo Steps**: Include detailed procedural steps for material processing
6. **Include Image Metadata**: Enhance images with detailed descriptions and captions
7. **Implement Clean Structure**: Focus on essential data without unnecessary publisher or alternative name arrays

## Performance Optimization

- **Extract Real Values**: Use actual frontmatter data instead of placeholders
- **Reuse Common Structures**: Template repeated structures like PropertyValue
- **Generate Technical Content**: Algorithmically create content from specifications
- **Fail-Fast Validation**: Validate inputs early to avoid processing invalid data

## Example Output

**New Comprehensive JSON-LD Format (September 24, 2025)**:
```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Article",
      "@id": "https://z-beam.com/aluminum#article",
      "headline": "Aluminum Laser Cleaning Guide",
      "description": "Technical overview of Aluminum laser cleaning applications and parameters",
      "author": {
        "@type": "Person",
        "name": "Ikmanda Roswati"
      },
      "keywords": "laser cleaning, aluminum, aluminum laser cleaning, laser ablation...",
      "datePublished": "2025-09-24"
    },
    {
      "@type": "Product", 
      "@id": "https://z-beam.com/aluminum#material",
      "name": "Aluminum",
      "additionalProperty": [
        {
          "@type": "PropertyValue",
          "name": "Thermal Conductivity",
          "value": "237 W/m·K",
          "unitCode": "WMK"
        }
      ]
    },
    {
      "@type": "HowTo",
      "@id": "https://z-beam.com/aluminum#howto", 
      "name": "How to Clean Aluminum with Laser Technology",
      "step": [
        {
          "@type": "HowToStep",
          "name": "Parameter Configuration",
          "text": "Set laser parameters: 1064nm wavelength, 100W power, optimized for Aluminum"
        }
      ]
    },
    {
      "@type": "FAQPage",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "What laser parameters are optimal for Aluminum?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "For Aluminum, we recommend 1064nm wavelength at 100W power..."
          }
        }
      ]
    }
  ]
}
```

**Legacy Simple Format** (deprecated):
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Laser Cleaning of Aluminum Materials",
  "description": "Comprehensive technical guide..."
}
```
