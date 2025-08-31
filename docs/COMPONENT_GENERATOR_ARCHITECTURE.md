# Component Generator Architecture

## Overview

The Z-Beam generator has been refactored to extract component-specific logic from the main `DynamicGenerator` into separate, specialized component generators. This provides better maintainability, testability, and extensibility.

## Architecture

### Base Classes

#### `BaseComponentGenerator`
Abstract base class for all component generators. Provides:
- Component type identification
- Prompt configuration loading
- Result creation utilities

#### `StaticComponentGenerator`
For components that don't require API calls:
- Author information
- Badge symbols  
- Properties tables
- Uses local data and templates

#### `APIComponentGenerator`
For components that require AI-generated content:
- Frontmatter
- Content
- Bullets
- Captions, tables, tags, etc.
- Handles API communication and prompt building

### Component Generator Factory

The `ComponentGeneratorFactory` manages creation of component generators:
- Supports both inline class references and string imports
- Enables lazy loading of specialized generators
- Provides centralized component registry

### File Structure

```
generators/
├── dynamic_generator.py          # Main orchestrator
├── component_generators.py       # Base classes and factory
├── author_generator.py          # Author component specialist
├── frontmatter_generator.py     # Frontmatter with enhancement
├── bullets_generator.py         # Bullets with author rules
└── [future specialized generators]
```

## Specialized Generators

### AuthorComponentGenerator
- **File**: `generators/author_generator.py`
- **Type**: Static
- **Function**: Generates author information using local JSON data
- **Features**: 
  - Uses existing author system (`run.get_author_by_id`)
  - Fallback to default author data
  - No API calls required

### FrontmatterComponentGenerator  
- **File**: `generators/frontmatter_generator.py`
- **Type**: API-based
- **Function**: Generates YAML frontmatter with property enhancement
- **Features**:
  - AI-generated base content
  - Automatic property enhancement with percentiles
  - Min/max context injection
  - Category-specific processing

### BulletsComponentGenerator
- **File**: `generators/bullets_generator.py` 
- **Type**: API-based
- **Function**: Generates bullet points with author-specific formatting
- **Features**:
  - Author-specific bullet counts (Taiwan: 4, Italy: 5, Indonesia: 6, USA: 3)
  - Country-specific industry context
  - Material category awareness
  - Technical standards integration

## Benefits

### 1. **Separation of Concerns**
Each component generator handles only its specific logic:
- Author generators manage author data
- Frontmatter generators handle YAML processing and enhancement
- Bullets generators manage formatting rules

### 2. **Maintainability**
- Easier to modify component-specific behavior
- Clear boundaries between components  
- Isolated testing of individual generators

### 3. **Extensibility**
- Easy to add new component types
- Can create specialized generators for complex components
- Plugin-like architecture for future enhancements

### 4. **Backward Compatibility**
- Main `DynamicGenerator` API remains unchanged
- Existing code continues to work
- Gradual migration path for complex components

## Usage Examples

### Basic Usage (No Changes Required)
```python
from generators.dynamic_generator import DynamicGenerator

generator = DynamicGenerator()
result = generator.generate_component('Steel', 'author')
```

### Direct Component Generator Usage
```python
from generators.author_generator import AuthorComponentGenerator

generator = AuthorComponentGenerator()
result = generator.generate('Steel', material_data, author_info=author)
```

### Creating Custom Generators
```python
from generators.component_generators import APIComponentGenerator

class CustomComponentGenerator(APIComponentGenerator):
    def __init__(self):
        super().__init__("custom")
    
    def _post_process_content(self, content, material_name, material_data):
        # Custom post-processing logic
        return enhanced_content
```

## Migration Guide

### For New Components
1. Create specialized generator file in `generators/`
2. Inherit from appropriate base class
3. Implement required methods
4. Register in `ComponentGeneratorFactory`

### For Existing Components
1. Current components continue to work via fallback
2. Can be gradually migrated to specialized generators
3. Test individually before switching

## Testing

Each component generator can be tested independently:

```python
# Test author generator
from generators.author_generator import AuthorComponentGenerator
generator = AuthorComponentGenerator()
result = generator.generate('TestMaterial', material_data)

# Test with mock API for API-based generators  
from generators.frontmatter_generator import FrontmatterComponentGenerator
generator = FrontmatterComponentGenerator()
result = generator.generate('TestMaterial', material_data, mock_api_client)
```

## Future Enhancements

### Planned Specializations
- **Content Generator**: Advanced content structuring and technical accuracy
- **Tags Generator**: Smart tag generation with category analysis  
- **Table Generator**: Dynamic table structures based on material properties
- **Metatags Generator**: SEO optimization and metadata enhancement

### Plugin System
- External component generators
- Custom business logic injection
- Third-party integrations

This architecture provides a solid foundation for scaling the component generation system while maintaining code quality and developer experience.
