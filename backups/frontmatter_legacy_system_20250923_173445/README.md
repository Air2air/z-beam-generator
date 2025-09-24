# Frontmatter Management System

## Overview
The frontmatter system provides centralized management of material metadata with robust validation, schema enforcement, and enhanced data integrity. This root-level architecture elevates frontmatter as a first-class citizen in the z-beam-generator ecosystem.

## Architecture

### Directory Structure
```
frontmatter/
├── materials/           # Material frontmatter files (YAML)
├── schemas/            # JSON Schema validation files
└── management/         # Management tools and utilities
    ├── manager.py      # FrontmatterManager (primary interface)
    ├── migrator.py     # Migration tools
    └── enhanced_generator.py  # Enhanced component generators
```

### Core Components

#### FrontmatterManager (`management/manager.py`)
The primary interface for all frontmatter operations:
- **Schema Validation**: Enforces JSON Schema compliance
- **Caching**: LRU cache for optimized performance
- **Integrity Checking**: Validates file consistency and completeness
- **Error Handling**: Fail-fast behavior with specific exception types

#### Migration System (`management/migrator.py`)
Automated migration tools for transitioning from old frontmatter structure:
- **Safe Migration**: Backup creation before any changes
- **Path Updating**: Automatic update of file references across codebase
- **Dry-Run Testing**: Preview changes before execution
- **Comprehensive Reporting**: Detailed migration status and results

#### Enhanced Generators (`management/enhanced_generator.py`)
Base classes for component generators with frontmatter integration:
- **EnhancedComponentGenerator**: Standard enhanced base class
- **FailFastComponentGenerator**: Strict validation with fail-fast behavior
- **Backward Compatibility**: Seamless integration with existing generators

## Usage Guide

### Basic Frontmatter Operations

#### Loading Material Frontmatter
```python
from frontmatter.management.manager import FrontmatterManager

# Initialize manager
manager = FrontmatterManager()

# Load specific material
frontmatter_data = manager.load_material("aluminum-6061")

# Load with validation
validated_data = manager.load_material("steel-304", validate=True)
```

#### Schema Validation
```python
# Validate specific material
is_valid = manager.validate_material("copper-c110")

# Get validation details
try:
    manager.validate_material("brass-360", raise_on_error=True)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

#### Integrity Checking
```python
# Get comprehensive integrity report
report = manager.get_integrity_report()
print(f"Valid files: {report['valid_count']}")
print(f"Invalid files: {report['invalid_count']}")
for error in report['errors']:
    print(f"Error in {error['file']}: {error['error']}")
```

### Component Generator Integration

#### Using Enhanced Generators
```python
from frontmatter.management.enhanced_generator import EnhancedComponentGenerator

class MyComponentGenerator(EnhancedComponentGenerator):
    def __init__(self):
        super().__init__(component_type="my_component")
    
    def generate(self, material_name: str, **kwargs) -> str:
        # Frontmatter automatically loaded and validated
        frontmatter_data = self.get_frontmatter(material_name)
        return self._generate_content(frontmatter_data, **kwargs)
```

#### Fail-Fast Integration
```python
from frontmatter.management.enhanced_generator import FailFastComponentGenerator

class StrictComponentGenerator(FailFastComponentGenerator):
    def generate(self, material_name: str, **kwargs) -> str:
        # Strict validation with immediate failure on errors
        frontmatter_data = self.get_frontmatter(material_name)
        # Generation logic with guaranteed valid data
        return self._generate_content(frontmatter_data, **kwargs)
```

### Migration Operations

#### Running Migration
```python
from frontmatter.management.migrator import FrontmatterMigrator

# Initialize migrator
migrator = FrontmatterMigrator()

# Dry run (preview changes)
dry_run_report = migrator.migrate(dry_run=True)
print(f"Files to migrate: {dry_run_report['files_to_migrate']}")
print(f"Paths to update: {dry_run_report['paths_to_update']}")

# Execute migration
migration_report = migrator.migrate(dry_run=False)
print(f"Migration completed: {migration_report['success']}")
```

## Schema Validation

### Material Frontmatter Schema
The system enforces comprehensive validation through JSON Schema:

#### Required Fields
- `name`: Material display name
- `category`: Material category
- `subcategory`: Material subcategory
- `applications`: List of applications
- `safety_considerations`: Safety information

#### Field Validation Rules
- **Naming**: Alphanumeric with spaces and hyphens
- **Categories**: Must match predefined category list
- **Applications**: Non-empty string array
- **Safety**: Required safety considerations
- **Properties**: Structured property definitions with units

#### Example Valid Frontmatter
```yaml
name: "Aluminum 6061"
category: "Metals"
subcategory: "Aluminum Alloys"
applications:
  - "Aerospace components"
  - "Automotive parts"
safety_considerations: "Use appropriate ventilation and protective equipment"
properties:
  thickness:
    range: "0.5-25mm"
    optimal: "1-10mm"
  surface_finish: "Mill finish to polished"
```

## Error Handling

### Exception Types
- **`FrontmatterNotFoundError`**: Material frontmatter file not found
- **`FrontmatterValidationError`**: Schema validation failure
- **`FrontmatterCorruptedError`**: YAML parsing or file corruption
- **`MigrationError`**: Migration process failure

### Error Recovery
```python
try:
    frontmatter_data = manager.load_material("unknown-material")
except FrontmatterNotFoundError as e:
    # Handle missing material
    logger.error(f"Material not found: {e}")
except FrontmatterValidationError as e:
    # Handle validation failure
    logger.error(f"Validation failed: {e}")
```

## Performance Considerations

### Caching Strategy
- **LRU Cache**: 128 material limit for memory efficiency
- **Lazy Loading**: Files loaded only when requested
- **Cache Invalidation**: Automatic cache refresh on file changes

### Optimization Tips
- Use `load_material()` for cached access
- Batch operations where possible
- Monitor cache hit rates for performance tuning

## Testing and Validation

### Running Frontmatter Tests
```bash
# Test frontmatter system
python -m pytest tests/test_frontmatter/ -v

# Test migration
python -m pytest tests/test_frontmatter_migration.py -v

# Test schema validation
python -m pytest tests/test_frontmatter_validation.py -v
```

### Validation Commands
```bash
# Validate all frontmatter files
python -c "from frontmatter.management.manager import FrontmatterManager; print(FrontmatterManager().get_integrity_report())"

# Check migration readiness
python frontmatter/management/migrator.py --dry-run
```

## Integration with Component System

### Component Generator Factory
The enhanced frontmatter system integrates seamlessly with the ComponentGeneratorFactory:

```python
from components import ComponentGeneratorFactory

# Factory automatically uses enhanced generators
generator = ComponentGeneratorFactory.create_generator("text")
# Generator now has access to validated frontmatter data
```

### Fail-Fast Architecture
- **Configuration Validation**: All required frontmatter files validated on startup
- **Schema Enforcement**: Invalid frontmatter files cause immediate failure
- **Dependency Checking**: Missing materials detected before generation begins

## Migration from Old System

### Pre-Migration Checklist
1. **Backup Creation**: Ensure backups of existing frontmatter files
2. **Dependency Review**: Identify all code referencing old frontmatter paths
3. **Testing**: Run comprehensive tests before migration
4. **Documentation**: Review migration report for any required manual updates

### Migration Process
1. **Dry Run**: Execute migration in dry-run mode to preview changes
2. **Backup**: Create backup of current frontmatter files
3. **Migrate Files**: Move frontmatter files to new structure
4. **Update Paths**: Automatically update file references in codebase
5. **Validate**: Run integrity checks on migrated files
6. **Test**: Execute full test suite to ensure functionality

### Post-Migration Validation
```bash
# Validate migration success
python -c "from frontmatter.management.manager import FrontmatterManager; manager = FrontmatterManager(); report = manager.get_integrity_report(); print(f'Valid: {report[\"valid_count\"]}, Invalid: {report[\"invalid_count\"]}')"
```

## Troubleshooting

### Common Issues

#### Schema Validation Errors
```
Error: Material 'material-name' failed schema validation
Solution: Check frontmatter file against schema requirements
Command: python frontmatter/management/manager.py --validate material-name
```

#### Missing Material Files
```
Error: FrontmatterNotFoundError for material 'material-name'
Solution: Ensure material file exists in frontmatter/materials/
Command: ls frontmatter/materials/ | grep material-name
```

#### Migration Path Conflicts
```
Error: Migration failed due to path conflicts
Solution: Review and resolve conflicting file paths
Command: python frontmatter/management/migrator.py --check-conflicts
```

### Diagnostic Commands
```bash
# Check frontmatter system health
python frontmatter/management/manager.py --health-check

# Validate specific material
python frontmatter/management/manager.py --validate aluminum-6061

# Migration status check
python frontmatter/management/migrator.py --status
```

## Best Practices

### Frontmatter File Management
1. **Consistent Naming**: Use lowercase with hyphens for material files
2. **Complete Data**: Ensure all required fields are populated
3. **Regular Validation**: Run periodic integrity checks
4. **Version Control**: Track changes to frontmatter files

### Component Integration
1. **Use Enhanced Generators**: Leverage EnhancedComponentGenerator base class
2. **Validate Early**: Use fail-fast generators for critical components
3. **Cache Wisely**: Rely on FrontmatterManager caching for performance
4. **Handle Errors**: Implement proper error handling for missing materials

### Development Workflow
1. **Test First**: Run frontmatter tests before code changes
2. **Validate Schema**: Check schema compliance for new materials
3. **Update Documentation**: Keep component docs synchronized with frontmatter changes
4. **Performance Monitor**: Track cache performance and file access patterns

## API Reference

See `frontmatter/management/manager.py` for detailed API documentation of the FrontmatterManager class and its methods.
