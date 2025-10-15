# Materials Loading System

## Overview

The `data/materials.py` module provides the `load_materials()` function that serves as the central interface for loading material data from `data/Materials.yaml`. This system was enhanced to support bulk material processing via the `--all` flag.

## Key Functions

### `load_materials()`

Loads and processes material data from `Materials.yaml` with automatic compatibility enhancements.

**Features:**
- Automatic detection of optimized vs. standard YAML format
- Enhanced name field population for --all flag compatibility  
- Support for both legacy and current material data structures
- Lazy loading with error handling

**Returns:**
```python
{
    "materials": {
        "category_name": {
            "items": [
                {"name": "Material Name", ...other_fields},
                ...
            ]
        },
        ...
    },
    "metadata": {...}
}
```

### `add_material_names_to_items(materials_data)`

Internal function that enhances material items with name fields using the material_index lookup.

**Purpose:**
- Enables --all flag functionality by ensuring all material items have name fields
- Maintains compatibility between different YAML data structures
- Creates reverse lookup from material_index to populate missing name fields

**Process:**
1. Checks if materials already have name fields populated
2. Uses material_index section to create name → category mapping  
3. Populates name field in each material item
4. Preserves all existing material data

## Usage Examples

### Basic Loading
```python
from data.materials import load_materials

# Load all materials
materials_data = load_materials()

# Access materials by category
steel_materials = materials_data['materials']['metal']['items']
```

### --all Flag Compatibility
```python
# This pattern is used internally by run.py --all flag
materials_data = load_materials()
all_materials = []

for category, category_data in materials_data['materials'].items():
    items = category_data.get('items', [])
    for item in items:
        material_name = item.get('name')  # Now guaranteed to exist
        if material_name:
            all_materials.append(material_name)

print(f"Found {len(all_materials)} materials for bulk processing")
```

## Data Structure Requirements

### Input (Materials.yaml)
The system supports materials with either structure:

**With material_index (current format):**
```yaml
material_index:
  Aluminum: metal
  Steel: metal
  Alumina: ceramic

materials:
  metal:
    items:
      - formula: "Al"
        # name field added automatically
      - formula: "Fe" 
        # name field added automatically
  ceramic:
    items:
      - formula: "Al2O3"
        # name field added automatically
```

**Pre-populated names (legacy format):**
```yaml
materials:
  metal:
    items:
      - name: "Aluminum"
        formula: "Al"
      - name: "Steel" 
        formula: "Fe"
```

### Output Structure
All loaded materials will have consistent structure with name fields:

```python
{
    "materials": {
        "metal": {
            "items": [
                {"name": "Aluminum", "formula": "Al", ...},
                {"name": "Steel", "formula": "Fe", ...}
            ]
        },
        "ceramic": {
            "items": [
                {"name": "Alumina", "formula": "Al2O3", ...}
            ]
        }
    }
}
```

## Integration Points

### CLI Integration (run.py)
- **--material**: Uses individual material lookup
- **--all**: Requires name fields in all items (enhanced by load_materials)

### Component Generators  
- **frontmatter**: Uses material data for rich field population
- **other components**: Access standardized material structure

### Testing
- **Unit tests**: Verify name field population and --all compatibility
- **Mock data**: Maintains same structure as real data loader

## Performance Considerations

- **LRU Caching**: Material data is cached to avoid repeated file reads
- **Lazy Loading**: Name field enhancement only runs when needed
- **Memory Efficient**: Modifies existing data structures in-place

## Error Handling

```python
try:
    materials_data = load_materials()
except FileNotFoundError:
    print("Materials.yaml not found")
except yaml.YAMLError:
    print("Invalid YAML syntax")
except Exception as e:
    print(f"Materials loading error: {e}")
```

## Compatibility Notes

### Before Enhancement
- --all flag failed with "No materials found in database"
- Individual material lookups worked correctly
- Name fields were stored separately in material_index

### After Enhancement  
- --all flag finds all 123 materials successfully
- Individual lookups continue to work unchanged
- Name fields automatically populated in all material items
- Full backward compatibility maintained

## Development Guidelines

### Adding New Materials
1. Add material name to material_index section
2. Add material data to appropriate category items array
3. Name field will be populated automatically by load_materials()

### Modifying Data Structure
- Maintain material_index → category mapping for name population
- Ensure all items arrays contain material data dictionaries
- Test both individual (--material) and bulk (--all) access patterns

### Testing Changes
```python
# Test name field population
materials_data = load_materials()
for category, cat_data in materials_data['materials'].items():
    for item in cat_data['items']:
        assert 'name' in item, f"Missing name in {category} item: {item}"

# Test --all flag compatibility  
all_materials = []
for category, cat_data in materials_data['materials'].items():
    for item in cat_data['items']:
        if item.get('name'):
            all_materials.append(item['name'])
assert len(all_materials) > 100, "Insufficient materials for bulk processing"
```

This enhancement ensures the materials loading system provides robust support for both individual material access and bulk processing operations.