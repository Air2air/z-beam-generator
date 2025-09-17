# Author Component Documentation

## Overview

The Author component generates author information in YAML format using **frontmatter-only data**. This is a **frontmatter-dependent component** that extracts author information from existing frontmatter files without making any API calls.

## Architecture

### Frontmatter-Only Component (No API Calls)
- **Type**: Frontmatter-dependent component
- **API Provider**: `none` (no API calls)
- **Data Source**: Frontmatter `author_object` field
- **Dependencies**: Frontmatter data must be available
- **Output Format**: Clean YAML (no delimiters or versioning)

### Data Flow
```
Frontmatter Available → Extract author_object → Generate YAML → Save as {material}-laser-cleaning.yaml
```

## Dependencies

### Required Dependencies
1. **Frontmatter Data**: Must contain `author_object` field with complete author information
2. **Material Name**: Used for content personalization and output file naming

### Frontmatter Structure
The Author component expects frontmatter to contain an `author_object` with these fields:
```yaml
author_object:
  id: 1
  name: "Yi-Chun Lin"
  title: "Ph.D."
  expertise: "Laser Materials Processing" 
  country: "Taiwan"
  sex: "f"
  image: "/images/author/yi-chun-lin.jpg"
```

## Configuration

### Component Configuration
```yaml
author:
  enabled: true
  api_provider: "none"  # No API calls
  type: "frontmatter_dependent"
  output_format: "yaml"
  file_naming: "{material}-laser-cleaning.yaml"
```

## Usage Examples

### Basic Usage with Frontmatter Data
```python
from components.author.generator import AuthorComponentGenerator

generator = AuthorComponentGenerator()

# Frontmatter data must include author_object
frontmatter_data = {
    "author_object": {
        "id": 1,
        "name": "Yi-Chun Lin",
        "title": "Ph.D.",
        "expertise": "Laser Materials Processing",
        "country": "Taiwan",
        "sex": "f",
        "image": "/images/author/yi-chun-lin.jpg"
    }
}

result = generator.generate(
    material_name="Aluminum",
    material_data={"name": "Aluminum"},
    frontmatter_data=frontmatter_data
)
```

### Integration with run.py
```bash
# Generate author component for specific material
python3 run.py --material "Aluminum" --components "author"

# Frontmatter data is automatically loaded from:
# content/components/frontmatter/aluminum-laser-cleaning.md
```

## Output Format

### YAML Structure
```yaml
authorInfo:
  id: 1
  name: Yi-Chun Lin
  title: Ph.D.
  expertise: Laser Materials Processing
  country: Taiwan
  sex: f
  image: /images/author/yi-chun-lin.jpg
  profile:
    description: "Yi-Chun Lin is a laser materials processing based in Taiwan..."
    expertiseAreas:
    - Laser cleaning systems and applications
    - Material science and processing
    - Industrial automation and safety protocols
    - Technical consultation and process optimization
    contactNote: "Contact Yi-Chun for expert consultation..."
materialContext:
  specialization: "Aluminum laser cleaning applications"
```

### File Naming Convention
- **Output Directory**: `content/components/author/`
- **File Name**: `{material}-laser-cleaning.yaml` (lowercase, kebab-case)
- **Examples**: 
  - `aluminum-laser-cleaning.yaml`
  - `stainless-steel-laser-cleaning.yaml`

## Testing

### Test Categories
- **Unit Tests**: Frontmatter data extraction and YAML generation
- **Integration Tests**: End-to-end generation with real frontmatter files
- **Validation Tests**: YAML structure and content accuracy

### Key Test Cases
- Content generation with valid frontmatter data
- Error handling for missing `author_object`
- YAML output format validation
- File naming convention verification

## Error Handling

### Common Errors
- **Missing Frontmatter Data**: No frontmatter_data parameter provided
- **Missing author_object**: Frontmatter doesn't contain author_object field
- **Invalid Author Data**: author_object missing required fields

### Error Messages
- `"Frontmatter data is required - fail-fast architecture requires frontmatter author information"`
- `"No author_object found in frontmatter data"`
- `"Material name is required"`

## Performance

### Generation Time
- **Typical**: < 5ms per author (no API calls)
- **Batch Generation**: ~107 materials in under 30 seconds

### Memory Usage
- **Per Generation**: Minimal memory footprint
- **No Caching**: Fresh extraction from frontmatter each time

## Best Practices

### 1. Ensure Frontmatter is Available
```python
# Verify frontmatter exists before author generation
frontmatter_path = f"content/components/frontmatter/{material.lower()}-laser-cleaning.md"
if not os.path.exists(frontmatter_path):
    print(f"❌ No frontmatter found for {material}")
    return
```

### 2. Validate author_object Structure
```python
# Check for required author_object fields
required_fields = ['id', 'name', 'title', 'expertise', 'country', 'sex', 'image']
author_obj = frontmatter_data.get('author_object', {})
for field in required_fields:
    if field not in author_obj:
        print(f"❌ Missing {field} in author_object")
```

### 3. Handle Generation Errors Gracefully
```python
result = generator.generate(material_name, material_data, frontmatter_data=frontmatter_data)
if not result.success:
    logger.error(f"Author generation failed: {result.error_message}")
```

## Troubleshooting

### Frontmatter Not Available
**Symptom**: "Frontmatter data is required" error
**Solution**: Generate frontmatter component first or verify frontmatter file exists

### Missing author_object
**Symptom**: "No author_object found in frontmatter data"
**Solution**: Verify frontmatter contains complete author_object with all required fields

### File Naming Issues
**Symptom**: Output files have wrong names
**Solution**: Ensure run.py uses correct naming convention: `{material}-laser-cleaning.yaml`

## Recent Changes

### Architecture Update (September 2025)
- ✅ **Removed API dependencies**: Now purely frontmatter-based
- ✅ **Implemented clean YAML output**: No HTML delimiters or versioning stamps
- ✅ **Fixed naming convention**: Changed from `{material}-author.yaml` to `{material}-laser-cleaning.yaml`
- ✅ **Simplified architecture**: No backward compatibility, frontmatter-only data source
- ✅ **Batch generation support**: Successfully generated 107/109 materials

### Breaking Changes
- **No longer uses `authors.json`**: All author data comes from frontmatter
- **Parameter change**: `author_info` replaced with `frontmatter_data`
- **Output format**: Pure YAML instead of versioned/delimited content
- **File naming**: Consistent with other components using `-laser-cleaning.yaml`
