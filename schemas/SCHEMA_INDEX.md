# Z-Beam Generator Schema Index

Generated: 2025-09-24T22:48:05.149794

## Schema Hierarchy (Validation Priority)

The UnifiedSchemaValidator uses this fallback hierarchy:

1. **enhanced_unified_frontmatter.json** (PRIMARY)
   - Location: `schemas/active/`
   - Purpose: Complete frontmatter validation with DataMetric pattern
   - Features: Reusable data structures, confidence scoring, research validation
   - Use Case: Production content generation with quality metrics

2. **enhanced_frontmatter.json** (ENHANCED FALLBACK)
   - Location: `schemas/active/`
   - Purpose: Enhanced validation without DataMetric complexity
   - Features: Extended validation rules, quality checks
   - Use Case: Enhanced validation when unified schema unavailable

3. **frontmatter.json** (LEGACY FALLBACK)
   - Location: `schemas/active/`
   - Purpose: Basic validation for backward compatibility
   - Features: Core required fields only
   - Use Case: Emergency fallback when modern schemas fail

## Active Schemas

### Primary Validation Schemas

#### enhanced_unified_frontmatter.json
- **Title**: Enhanced Frontmatter Schema with Reusable Data Metrics  
- **Description**: Primary schema with DataMetric pattern
- **Usage**: 4 references in codebase
- **Status**: ✅ Active
- **Used By**: /Users/todddunning/Desktop/Z-Beam/z-beam-generator/scripts/organize_schemas.py, /Users/todddunning/Desktop/Z-Beam/z-beam-generator/validation/unified_schema_validator.py, /Users/todddunning/Desktop/Z-Beam/z-beam-generator/components/frontmatter/core/streamlined_generator.py (and 1 more)

#### enhanced_frontmatter.json
- **Title**: Enhanced Frontmatter Schema  
- **Description**: Enhanced validation features
- **Usage**: 11 references in codebase
- **Status**: ✅ Active
- **Used By**: /Users/todddunning/Desktop/Z-Beam/z-beam-generator/examples/enhanced_frontmatter_demo.py, /Users/todddunning/Desktop/Z-Beam/z-beam-generator/examples/yaml_output_sample.py, /Users/todddunning/Desktop/Z-Beam/z-beam-generator/examples/complete_sample_output.py (and 8 more)

#### frontmatter.json
- **Title**: Frontmatter Schema  
- **Description**: Legacy compatibility fallback
- **Usage**: 185 references in codebase
- **Status**: ✅ Active
- **Used By**: /Users/todddunning/Desktop/Z-Beam/z-beam-generator/fix_titanium_frontmatter.py, /Users/todddunning/Desktop/Z-Beam/z-beam-generator/run.py, /Users/todddunning/Desktop/Z-Beam/z-beam-generator/verify_materials_database.py (and 182 more)

## Component Schemas

Specialized schemas for individual components:

### author.json
- **Purpose**: Author component schema
- **Usage**: 117 references
- **Status**: 🔧 Component-specific

### application.json
- **Purpose**: Application component schema
- **Usage**: 68 references
- **Status**: 🔧 Component-specific

### region.json
- **Purpose**: Region component schema
- **Usage**: 1 references
- **Status**: 🔧 Component-specific

### json-ld.json
- **Purpose**: JSON-LD structured data schema
- **Usage**: 3 references
- **Status**: 🔧 Component-specific

### thesaurus.json
- **Purpose**: Thesaurus/terminology schema
- **Usage**: 1 references
- **Status**: 🔧 Component-specific

### base.json
- **Purpose**: Base component schema
- **Usage**: 116 references
- **Status**: 🔧 Component-specific

## Archived Schemas

Specialized schemas moved to archive for organization:

### metricsproperties.json
- **Purpose**: Properties component schema
- **Usage**: 20 references
- **Status**: 📦 Archived (still accessible)

### metricsmachinesettings.json
- **Purpose**: Machine settings component schema
- **Usage**: 14 references
- **Status**: 📦 Archived (still accessible)

### Materials_yaml.json
- **Purpose**: Materials.yaml validation schema
- **Usage**: 29 references
- **Status**: 📦 Archived (still accessible)

### material.json
- **Purpose**: Single material structure schema
- **Usage**: 218 references
- **Status**: 📦 Archived (still accessible)


## Usage Guidelines

### For Validation
Use UnifiedSchemaValidator which automatically selects the best available schema:
```python
from validation.unified_schema_validator import UnifiedSchemaValidator

# Automatic schema selection with fallback
validator = UnifiedSchemaValidator(validation_mode="enhanced")
result = validator.validate(frontmatter_data, material_name)
```

### For Specific Schema
```python
# Use specific schema
validator = UnifiedSchemaValidator("schemas/active/enhanced_unified_frontmatter.json")
```

### Schema Path Resolution
The validator searches in this order:
1. `schemas/active/enhanced_unified_frontmatter.json`
2. `schemas/enhanced_unified_frontmatter.json` (legacy location)
3. `schemas/active/enhanced_frontmatter.json`
4. `schemas/enhanced_frontmatter.json` (legacy location)
5. `schemas/active/frontmatter.json`
6. `schemas/frontmatter.json` (legacy location)
7. Emergency minimal schema (built-in)

## Maintenance

- **Adding New Schemas**: Place in appropriate directory (active/, components/, archive/)
- **Updating Schemas**: Update in-place, increment version in schema metadata
- **Deprecating Schemas**: Move to archive/, update this index
- **Schema Testing**: Use `python scripts/verify_unified_validator.py --test schema`

## Migration Notes

- Legacy code may reference old schema locations
- UnifiedSchemaValidator handles path resolution automatically
- Component schemas remain accessible for specialized validation
- Archive schemas are preserved for specialized use cases
