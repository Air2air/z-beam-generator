# Frontmatter Generator Documentation

## Strategic Role
**The frontmatter component is the core component of the Z-Beam system and will eventually serve as the single source of truth for all material data generation.**

> 📋 **Architectural Direction**: Over time, the system will transition to using only the frontmatter component, with other components being derived from or integrated into frontmatter output.

## Overview

The Frontmatter Component Generator creates YAML metadata for material articles based on structured material data. 
It strictly adheres to the system's fail-fast architecture while allowing certain fields to be optional.

## Usage

The frontmatter generator should be used through the established component factory system:

```python
from generators.component_generators import ComponentGeneratorFactory

factory = ComponentGeneratorFactory()
generator = factory.create_generator("frontmatter")

result = generator.generate(
    material_name="Aluminum",
    material_data=material_data,
    api_client=api_client,
    author_info=author_info
)
```

## Required vs Optional Fields

As of the latest update, the frontmatter generator has the following field requirements:

### Required Fields:
- Material name
- Material category
- Material symbol (chemical symbol)
- Author information (via author object with id, name, expertise, etc.)
- Machine settings and laser parameters
- Environmental impact data
- Application types and industry classifications
- Regulatory standards and safety information

> 💡 **Future Enhancement**: The frontmatter component will be enhanced to include derivation methods for generating all other component outputs (JSON-LD, metatags, tables, etc.) from the core frontmatter data.

### Optional Fields:
- Formula (chemical formula) - Warning logged if missing, generation continues

## API Dependency

The frontmatter generator requires a valid API client for content generation. The client must support the `generate_simple()` method. Always use the cached API client:

```python
from api.client_cache import get_cached_api_client

api_client = get_cached_api_client("deepseek")
```

## Error Handling

The generator follows strict fail-fast principles for required fields but gracefully handles optional fields.
For missing required fields, it will throw an exception immediately. For missing optional fields, it will log
a warning and continue with generation.

## Testing

When testing the frontmatter generator, use the established component creation patterns and testing frameworks.
There is no need to modify material data directly as the system is designed to work with standardized data from `data/Materials.yaml`.

## Configuration

The generator uses a comprehensive prompt configuration file at `components/frontmatter/prompt.yaml`.
This configuration defines the template variables, API prompt structure, and other generation parameters.
