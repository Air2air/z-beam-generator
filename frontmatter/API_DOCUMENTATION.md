# Frontmatter Management API Documentation

## Overview
The Frontmatter Management API provides centralized access to material metadata with comprehensive validation, caching, and error handling. This API serves as the single source of truth for all frontmatter operations in the z-beam-generator ecosystem.

## Core Classes

### FrontmatterManager

#### Purpose
Central manager for all frontmatter operations with built-in validation, caching, and integrity checking.

#### Constructor
```python
FrontmatterManager(root_path: Optional[Path] = None)
```

**Parameters:**
- `root_path` (Optional[Path]): Custom root path for frontmatter directory. Defaults to current working directory.

**Example:**
```python
from frontmatter.management.manager import FrontmatterManager

# Use default path (current working directory)
manager = FrontmatterManager()

# Use custom path
manager = FrontmatterManager(root_path=Path("/custom/project/path"))
```

#### Methods

##### `load_material(material_name: str, validate: bool = False) -> Dict[str, Any]`

Load material frontmatter data with optional validation.

**Parameters:**
- `material_name` (str): Name of the material (without .yaml extension)
- `validate` (bool): Whether to perform schema validation (default: False)

**Returns:**
- `Dict[str, Any]`: Parsed frontmatter data

**Raises:**
- `FrontmatterNotFoundError`: When material file doesn't exist
- `FrontmatterCorruptedError`: When YAML parsing fails
- `FrontmatterValidationError`: When validation is enabled and fails

**Example:**
```python
# Load without validation
data = manager.load_material("aluminum-6061")

# Load with validation
data = manager.load_material("aluminum-6061", validate=True)
```

##### `validate_material(material_name: str, raise_on_error: bool = False) -> bool`

Validate material frontmatter against JSON Schema.

**Parameters:**
- `material_name` (str): Name of the material to validate
- `raise_on_error` (bool): Whether to raise exception on validation failure

**Returns:**
- `bool`: True if validation passes, False otherwise

**Raises:**
- `FrontmatterValidationError`: When raise_on_error=True and validation fails

**Example:**
```python
# Check validation status
is_valid = manager.validate_material("aluminum-6061")

# Validate with exception on failure
try:
    manager.validate_material("aluminum-6061", raise_on_error=True)
    print("Material is valid")
except FrontmatterValidationError as e:
    print(f"Validation failed: {e}")
```

##### `list_materials() -> List[str]`

Get list of all available material names.

**Returns:**
- `List[str]`: List of material names (without .yaml extension)

**Example:**
```python
materials = manager.list_materials()
print(f"Available materials: {materials}")
```

##### `get_integrity_report() -> Dict[str, Any]`

Generate comprehensive integrity report for all frontmatter files.

**Returns:**
- `Dict[str, Any]`: Report containing:
  - `total_files` (int): Total number of frontmatter files
  - `valid_count` (int): Number of valid files
  - `invalid_count` (int): Number of invalid files
  - `errors` (List[Dict]): Detailed error information

**Example:**
```python
report = manager.get_integrity_report()
print(f"Integrity: {report['valid_count']}/{report['total_files']} files valid")

for error in report['errors']:
    print(f"Error in {error['file']}: {error['error']}")
```

##### `material_exists(material_name: str) -> bool`

Check if a material frontmatter file exists.

**Parameters:**
- `material_name` (str): Name of the material to check

**Returns:**
- `bool`: True if material exists, False otherwise

**Example:**
```python
if manager.material_exists("aluminum-6061"):
    data = manager.load_material("aluminum-6061")
```

##### `get_material_path(material_name: str) -> Path`

Get the full path to a material frontmatter file.

**Parameters:**
- `material_name` (str): Name of the material

**Returns:**
- `Path`: Full path to the material file

**Example:**
```python
path = manager.get_material_path("aluminum-6061")
print(f"Material file: {path}")
```

##### `clear_cache() -> None`

Clear the internal LRU cache.

**Example:**
```python
manager.clear_cache()
```

#### Properties

##### `materials_dir: Path`
Path to the materials directory (frontmatter/materials).

##### `schema_path: Path`
Path to the JSON schema file.

### Enhanced Component Generators

#### EnhancedComponentGenerator

Base class for component generators with automatic frontmatter integration.

```python
from frontmatter.management.enhanced_generator import EnhancedComponentGenerator

class MyComponentGenerator(EnhancedComponentGenerator):
    def __init__(self):
        super().__init__(component_type="my_component")
    
    def generate(self, material_name: str, **kwargs) -> str:
        # Frontmatter automatically loaded and cached
        frontmatter_data = self.get_frontmatter(material_name)
        return self._generate_content(frontmatter_data, **kwargs)
```

#### FailFastComponentGenerator

Strict validation version of EnhancedComponentGenerator with fail-fast behavior.

```python
from frontmatter.management.enhanced_generator import FailFastComponentGenerator

class StrictComponentGenerator(FailFastComponentGenerator):
    def generate(self, material_name: str, **kwargs) -> str:
        # Strict validation with immediate failure on errors
        frontmatter_data = self.get_frontmatter(material_name)
        # Generation logic with guaranteed valid data
        return self._generate_content(frontmatter_data, **kwargs)
```

## Exception Classes

### FrontmatterNotFoundError
Raised when a requested material frontmatter file cannot be found.

```python
try:
    data = manager.load_material("nonexistent-material")
except FrontmatterNotFoundError as e:
    print(f"Material not found: {e}")
```

### FrontmatterValidationError
Raised when frontmatter data fails schema validation.

```python
try:
    manager.validate_material("invalid-material", raise_on_error=True)
except FrontmatterValidationError as e:
    print(f"Validation failed: {e}")
```

### FrontmatterCorruptedError
Raised when frontmatter file cannot be parsed (corrupted YAML).

```python
try:
    data = manager.load_material("corrupted-material")
except FrontmatterCorruptedError as e:
    print(f"File corrupted: {e}")
```

### MigrationError
Raised when migration operations fail.

```python
from frontmatter.management.migrator import FrontmatterMigrator

try:
    migrator = FrontmatterMigrator()
    report = migrator.migrate(dry_run=False)
except MigrationError as e:
    print(f"Migration failed: {e}")
```

## Migration API

### FrontmatterMigrator

Handles migration from old frontmatter structure to new system.

#### Methods

##### `migrate(dry_run: bool = True) -> Dict[str, Any]`

Execute frontmatter migration with optional dry-run mode.

**Parameters:**
- `dry_run` (bool): If True, preview changes without making them

**Returns:**
- `Dict[str, Any]`: Migration report with status and details

**Example:**
```python
from frontmatter.management.migrator import FrontmatterMigrator

migrator = FrontmatterMigrator()

# Preview migration
dry_run_report = migrator.migrate(dry_run=True)
print(f"Will migrate {dry_run_report['files_to_migrate']} files")

# Execute migration
if input("Proceed? (y/n): ").lower() == 'y':
    migration_report = migrator.migrate(dry_run=False)
    print(f"Migration {'succeeded' if migration_report['success'] else 'failed'}")
```

## Schema Validation

### JSON Schema Structure

The frontmatter system uses JSON Schema for validation:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["name", "category", "subcategory", "applications", "safety_considerations"],
  "properties": {
    "name": {
      "type": "string",
      "pattern": "^[A-Za-z0-9\\s\\-]+$",
      "minLength": 1,
      "maxLength": 100
    },
    "category": {
      "type": "string",
      "enum": ["Metals", "Ceramics", "Polymers", "Composites", "Glass", "Wood", "Stone", "Other"]
    },
    "applications": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 1
    }
  }
}
```

### Custom Validation

For custom validation beyond schema:

```python
def validate_custom_requirements(data: Dict[str, Any]) -> bool:
    """Custom validation logic."""
    # Check custom business rules
    if data.get('category') == 'Metals':
        required_properties = ['density', 'melting_point']
        for prop in required_properties:
            if prop not in data.get('properties', {}):
                return False
    return True

# Use with FrontmatterManager
data = manager.load_material("aluminum-6061")
if manager.validate_material("aluminum-6061") and validate_custom_requirements(data):
    print("Material passes all validation checks")
```

## Performance Considerations

### Caching Strategy

The FrontmatterManager uses LRU caching for optimal performance:

- **Cache Size**: 128 materials (configurable)
- **Cache Key**: Material name
- **Cache Invalidation**: Manual via `clear_cache()`

### Cache Monitoring

```python
# Check cache performance
cache_info = manager.load_material.cache_info()
print(f"Cache hits: {cache_info.hits}")
print(f"Cache misses: {cache_info.misses}")
print(f"Hit ratio: {cache_info.hits / (cache_info.hits + cache_info.misses):.2%}")
```

### Optimization Tips

1. **Batch Operations**: Load multiple materials together when possible
2. **Cache Warmup**: Pre-load frequently used materials
3. **Validation Strategy**: Use validation judiciously for performance-critical paths

```python
# Efficient batch loading
materials_to_load = ["aluminum-6061", "steel-304", "copper-c110"]
material_data = {}

for material in materials_to_load:
    material_data[material] = manager.load_material(material)

# Cache warmup for frequently used materials
common_materials = manager.list_materials()[:10]  # Top 10 materials
for material in common_materials:
    manager.load_material(material)  # Populate cache
```

## Integration Examples

### Component Factory Integration

```python
from frontmatter.management.manager import FrontmatterManager
from components import ComponentGeneratorFactory

class EnhancedComponentFactory:
    def __init__(self):
        self.frontmatter_manager = FrontmatterManager()
    
    def create_generator(self, component_type: str):
        generator = ComponentGeneratorFactory.create_generator(component_type)
        
        # Inject frontmatter manager if generator supports it
        if hasattr(generator, 'set_frontmatter_manager'):
            generator.set_frontmatter_manager(self.frontmatter_manager)
        
        return generator
```

### Validation Pipeline

```python
def validate_all_materials():
    """Validate all materials and generate report."""
    manager = FrontmatterManager()
    report = manager.get_integrity_report()
    
    if report['invalid_count'] > 0:
        print(f"⚠️ {report['invalid_count']} materials failed validation:")
        for error in report['errors']:
            print(f"  - {error['file']}: {error['error']}")
        return False
    
    print(f"✅ All {report['valid_count']} materials passed validation")
    return True

# Use in CI/CD pipeline
if not validate_all_materials():
    sys.exit(1)
```

### Testing Integration

```python
import tempfile
from pathlib import Path
from frontmatter.management.manager import FrontmatterManager

def test_with_temp_frontmatter():
    """Test with temporary frontmatter setup."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test frontmatter structure
        materials_dir = Path(temp_dir) / "frontmatter" / "materials"
        materials_dir.mkdir(parents=True)
        
        # Create test material
        test_material = {
            "name": "Test Material",
            "category": "Metals",
            "subcategory": "Test Alloys",
            "applications": ["Testing"],
            "safety_considerations": "Use appropriate safety equipment"
        }
        
        test_file = materials_dir / "test-material.yaml"
        with open(test_file, 'w') as f:
            yaml.dump(test_material, f)
        
        # Test with custom manager
        manager = FrontmatterManager(root_path=Path(temp_dir))
        data = manager.load_material("test-material")
        
        assert data["name"] == "Test Material"
```

## Best Practices

### Error Handling

```python
# Comprehensive error handling
def safe_load_material(manager: FrontmatterManager, material_name: str) -> Optional[Dict]:
    """Safely load material with proper error handling."""
    try:
        return manager.load_material(material_name, validate=True)
    except FrontmatterNotFoundError:
        logger.error(f"Material '{material_name}' not found")
        return None
    except FrontmatterValidationError as e:
        logger.error(f"Material '{material_name}' failed validation: {e}")
        return None
    except FrontmatterCorruptedError as e:
        logger.error(f"Material '{material_name}' file corrupted: {e}")
        return None
```

### Configuration Management

```python
# Environment-specific configuration
class FrontmatterConfig:
    def __init__(self, environment: str = "production"):
        if environment == "test":
            self.root_path = Path("tests/fixtures/frontmatter")
        elif environment == "development":
            self.root_path = Path(".")
        else:
            self.root_path = Path("/opt/zbeam/frontmatter")
    
    def create_manager(self) -> FrontmatterManager:
        return FrontmatterManager(root_path=self.root_path)
```

### Logging and Monitoring

```python
import logging
from functools import wraps

def log_frontmatter_operations(func):
    """Decorator to log frontmatter operations."""
    @wraps(func)
    def wrapper(self, material_name: str, *args, **kwargs):
        logger = logging.getLogger(__name__)
        logger.info(f"Loading material: {material_name}")
        
        start_time = time.time()
        try:
            result = func(self, material_name, *args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"Loaded {material_name} in {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to load {material_name} after {duration:.3f}s: {e}")
            raise
    
    return wrapper

# Apply to custom manager
class LoggedFrontmatterManager(FrontmatterManager):
    @log_frontmatter_operations
    def load_material(self, material_name: str, validate: bool = False):
        return super().load_material(material_name, validate)
```
