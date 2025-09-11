# Material Data Customization Guide

## Overview

This document explains how to work with modified material data in the Z-Beam Generator system, particularly when testing or extending components that need to handle optional fields.

## Understanding the Material Data Flow

There are two primary ways to use material data in the system:

1. **Standard Workflow via `run_dynamic_generation`**:
   - Materials are loaded from `data/materials.yaml` via the `load_materials()` function
   - The `DynamicGenerator` looks up materials by name
   - Not suitable for testing with modified material data

2. **Direct Component Generation**:
   - Components are instantiated directly (e.g., `FrontmatterComponentGenerator()`)
   - Modified material data is passed directly to the `generate()` method
   - Allows complete control over the material data structure

## Example: Testing with Modified Material Data

When testing components with modified material data (such as removing optional fields like `formula`), use the direct component generation approach:

```python
# Import necessary components
from components.frontmatter.generator import FrontmatterComponentGenerator
from api.client_cache import get_cached_api_client
from utils.core.author_manager import get_author_info_for_material

# Create modified material data
material_data = {...}  # Start with existing material data
if "formula" in material_data:
    del material_data["formula"]  # Remove the formula field

# Get author info and API client
author_info = get_author_info_for_material(material_data)
api_client = get_cached_api_client("deepseek")

# Generate component with modified data
generator = FrontmatterComponentGenerator()
result = generator.generate(
    material_name="Aluminum",
    material_data=material_data,  # Pass modified data here
    api_client=api_client,
    author_info=author_info
)
```

## Best Practices for Material Data Customization

1. Always use `get_cached_api_client()` rather than creating new clients directly
2. Use `get_author_info_for_material()` to properly resolve author information
3. Make a deep copy of material data before modifying it: `material_data = copy.deepcopy(original_data)`
4. Check the component's documentation for required vs. optional fields
5. Examine logs for warnings about missing fields

## Related Tests

- `test_formula_direct.py`: Tests the frontmatter generator directly with missing formula field
- `test_formula_optional.py`: Similar test with different material structure
- `test_override_material.py`: Complete example of modifying material data and using it directly

## Implementing Support for Optional Fields

When implementing support for optional fields in your own components:

1. Use defensive programming (check if fields exist before accessing them)
2. Log warnings for missing optional fields rather than throwing errors
3. Provide reasonable defaults when appropriate
4. Document which fields are required vs. optional
