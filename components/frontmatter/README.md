# Frontmatter Component

## Overview
The frontmatter component generates comprehensive YAML frontmatter for laser cleaning articles with full author object integration.

## Features
- **Author Resolution**: Automatically resolves author_id from materials.yaml to full author objects from authors.json
- **Complete Author Information**: Includes all author fields (name, sex, title, country, expertise, image)
- **Fail-Fast Architecture**: Validates all required configurations and data before generation
- **Property Enhancement**: Integrates material property data with percentile calculations

## Author Object Structure
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

## Data Flow
1. **Material Data**: materials.yaml provides `author_id` for each material
2. **Author Lookup**: Component resolves author_id to full author object from authors.json
3. **Template Integration**: All author fields are included in the frontmatter template
4. **Validation**: Fail-fast validation ensures all required data is present

## Configuration Files
- `prompt.yaml`: Template with author object placeholders
- `authors.json`: Author database with complete profiles
- `materials.yaml`: Material data with author_id references

## Usage
The component automatically handles author resolution when generating frontmatter:

```python
result = generator.generate(
    material_name="Alumina",
    material_data=material_data,  # Contains author_id
    api_client=api_client,
    author_info=None  # Will be resolved from material_data
)
```

## Error Handling
- **Missing author_id**: Raises ConfigurationError if author_id not found in material data
- **Invalid author_id**: Raises GenerationError if author not found in authors.json
- **Missing author fields**: Uses defaults for optional fields, fails on required fields

## Testing
Run tests to verify author object integration:
```bash
python3 -m pytest components/frontmatter/tests/
```
