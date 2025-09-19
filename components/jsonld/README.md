# JSON-LD Component Documentation

## Overview
The JSON-LD component generates structured data in schema.org format for material laser cleaning pages. It provides machine-readable metadata for search engines and enhances SEO performance.

**Latest Update (September 18, 2025)**: ✅ **STREAMLINED JSON-LD STRUCTURE** - Removed `publisher` and `alternateName` fields to create cleaner, more focused structured data. Enhanced hybrid mode for comprehensive frontmatter data integration while maintaining essential schema.org compliance.

## Key Files

### Core Implementation
- **`generator.py`** - Main component generator using HybridComponentGenerator pattern
- **`example_jsonld.md`** - Complete schema.org implementation example
- **`validator.py`** - JSON-LD validation logic
- **`prompt.yaml`** - Enhanced template (Version 5.0.0)

## Usage

The component can be used in two modes:
1. **Frontmatter-only mode**: Generates JSON-LD using only frontmatter data
2. **Hybrid mode**: Uses both frontmatter and API enhancement

```python
from components.jsonld.generator import JsonldComponentGenerator

# Create generator
generator = JsonldComponentGenerator()

# Generate JSON-LD
result = generator.generate(
    material_name="Aluminum",
    material_data=material_data,
    api_client=api_client,  # Optional for hybrid mode
    author_info=author_info,  # Optional
    frontmatter_data=frontmatter_data
)

# Access result
jsonld_content = result.content
```

## Implementation Details

### Generator Class
The `JsonldComponentGenerator` class extends `HybridComponentGenerator` and implements:

- **_extract_from_frontmatter**: Builds JSON-LD from frontmatter data
- **_build_from_example**: Uses example_jsonld.md as a template
- **_build_from_schema**: Fallback builder using schema structure
- **_build_nested_structure**: Constructs nested JSON objects
- **_build_properties_array**: Generates PropertyValue arrays

### Validation
The `validator.py` file provides three main validation functions:
- **validate_jsonld_structure**: Ensures JSON-LD syntax and required fields
- **validate_jsonld_content**: Checks for placeholder content
- **validate_jsonld_schema**: Validates schema.org compliance

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

**New YAML Format (September 16, 2025)**:
```yaml
---
jsonld:
  '@context': https://schema.org
  '@type': Article
  headline: Aluminum Laser Cleaning
  description: Comprehensive technical guide covering laser cleaning methodologies...
  author:
    '@type': Person
    name: Dr. Emily Chen
  datePublished: '2025-09-16T15:30:00Z'
  image:
  - '@type': ImageObject
    url: /images/aluminum-laser-cleaning-hero.jpg
    name: Aluminum Laser Cleaning Before/After Comparison
  about:
  - '@type': Material
    name: Aluminum
    category: metal
---
```

**Previous JSON Format** (deprecated):
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Laser Cleaning of Aluminum Materials",
  "description": "Comprehensive technical guide covering laser cleaning methodologies...",
  "author": {
    "@type": "Person",
    "name": "Dr. Emily Chen"
  },
  "datePublished": "2025-01-27T15:30:00Z",
  "image": [
    {
      "@type": "ImageObject",
      "url": "/images/aluminum-laser-cleaning-hero.jpg",
      "name": "Aluminum Laser Cleaning Before/After Comparison"
    }
  ],
  "about": [
    {
      "@type": "Material",
      "name": "Aluminum",
      "category": "metal",
      "additionalProperty": [
        {
          "@type": "PropertyValue",
          "name": "Density",
          "value": "2.7",
          "unitCode": "KGM"
        }
      ]
    }
  ]
}
```
