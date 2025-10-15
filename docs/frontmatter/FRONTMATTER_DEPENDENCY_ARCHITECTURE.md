# Frontmatter Dependency Architecture

## Overview

**CRITICAL DESIGN DECISION**: Component generation depends on frontmatter data for that specified material. Component failures will cascade without it. This is intentional design.

## Architecture Principle

The Z-Beam generator follows a **fail-fast architecture** where:

1. **No Mocks or Fallbacks**: System fails immediately if dependencies are missing
2. **Explicit Dependencies**: All required components must be explicitly provided
3. **Component Architecture**: Uses ComponentGeneratorFactory pattern for all generators
4. **Fail-Fast Design**: Validates configurations and inputs immediately

## Frontmatter Dependency Chain

### Primary Dependency: Frontmatter Data

All component generators require frontmatter data to function properly:

```
┌─────────────────┐
│   Frontmatter   │ ←── REQUIRED for all components
│     Data        │
└─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Text          │    │   Bullets       │    │   Caption       │
│   Component     │    │   Component     │    │   Component     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Properties    │    │   Tags          │    │   Metatags      │
│   Table         │    │   Component     │    │   Component     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Required Frontmatter Fields

Each component requires specific frontmatter fields:

#### Text Component
- `name` - Material name
- `category` - Material category (metal, ceramic, etc.)
- `properties` - Technical properties dictionary
- `applications` - List of applications
- `author` - Author information

#### Bullets Component
- `name` - Material name
- `category` - Material category
- `properties` - Technical properties
- `applications` - Application areas

#### Caption Component
- `name` - Material name
- `category` - Material category
- `properties` - Technical properties

#### Frontmatter Component (Self-Referential)
- `name` - Material name
- `category` - Material category
- `formula` - Chemical formula
- `properties` - Technical properties
- `applications` - Application areas
- `technicalSpecifications` - Detailed specs
- `chemicalProperties` - Chemical characteristics

## Cascading Failure Behavior

### Failure Propagation

When frontmatter data is missing or incomplete:

1. **Frontmatter Generation Fails**
   - Missing required fields (category, formula, properties)
   - Invalid data structure
   - File not found

2. **Component Generation Fails**
   - Text component cannot access material properties
   - Bullets component cannot generate application bullets
   - Caption component cannot create descriptive captions

3. **Complete Material Failure**
   - No content generated for the material
   - User must fix frontmatter before proceeding
   - System maintains data integrity

### Example Failure Cascade

```python
# Step 1: Frontmatter missing critical data
frontmatter_data = {
    'name': 'Aluminum'
    # Missing: category, formula, properties, applications
}

# Step 2: Text component fails
text_result = generate_text_component('Aluminum', frontmatter_data)
# Result: FAILURE - Missing category and properties

# Step 3: Bullets component fails
bullets_result = generate_bullets_component('Aluminum', frontmatter_data)
# Result: FAILURE - Missing applications data

# Step 4: Complete material generation fails
# Result: No content generated, user must fix frontmatter
```

## Validation and Error Handling

### Frontmatter Validation

The system validates frontmatter data before component generation:

```python
def validate_frontmatter_for_generation(frontmatter_data: Dict) -> bool:
    """Validate frontmatter contains sufficient data for generation"""
    required_fields = ['name', 'category', 'properties', 'applications']

    for field in required_fields:
        if field not in frontmatter_data:
            return False

        value = frontmatter_data[field]
        if not value:
            return False

        if field in ['properties', 'applications'] and len(value) == 0:
            return False

    return True
```

### Error Messages

Clear error messages indicate missing dependencies:

- `"Frontmatter generation failed: Missing required fields (category, formula, properties)"`
- `"Text component failed: No frontmatter data available"`
- `"Component generation failed: Insufficient frontmatter data"`

## Testing the Dependency Chain

### Comprehensive Test Suite

The test suite validates the dependency chain:

```bash
# Run frontmatter dependency tests
python3 tests/test_frontmatter_dependency_chain.py

# Run cascading failure tests
python3 tests/test_cascading_failure.py

# Run validation tests
python3 tests/test_frontmatter_validation.py
```

### Test Coverage

Tests cover:

1. **Complete Frontmatter Success**
   - All components generate successfully
   - Content quality meets requirements

2. **Incomplete Frontmatter Failure**
   - Components fail gracefully
   - Clear error messages provided

3. **Cascading Failure Demonstration**
   - Shows how one failure affects all components
   - Validates fail-fast behavior

4. **Validation Testing**
   - Frontmatter validation functions
   - Required field checking
   - Data structure validation

## Best Practices

### For Developers

1. **Always Validate Frontmatter First**
   ```python
   if not validate_frontmatter_for_generation(frontmatter_data):
       raise ValueError("Insufficient frontmatter data for generation")
   ```

2. **Fail Fast on Missing Dependencies**
   ```python
   if not frontmatter_data:
       return ComponentResult(component_type, "", False, "No frontmatter data available")
   ```

3. **Provide Clear Error Messages**
   ```python
   error_msg = f"Missing required frontmatter fields: {missing_fields}"
   ```

### For Users

1. **Ensure Frontmatter Exists**
   - Create frontmatter files before generation
   - Validate all required fields are present

2. **Check Frontmatter Completeness**
   - Run validation tests before generation
   - Fix missing fields before proceeding

3. **Understand Failure Causes**
   - Frontmatter issues cause component failures
   - Fix root cause (frontmatter) before retrying

## Configuration

### Frontmatter File Structure

Frontmatter files must be located at:
```
content/components/frontmatter/{material}-laser-cleaning.yaml
```

### Required Frontmatter Structure

```yaml
---
name: "Aluminum"
category: "metal"
formula: "Al"
symbol: "Al"
properties:
  density: "2.7 g/cm³"
  melting_point: "660°C"
  thermal_conductivity: "237 W/m·K"
applications:
  - "Aerospace components"
  - "Automotive parts"
  - "Building construction"
technicalSpecifications:
  purity: "99.9%"
  grain_size: "ASTM 5-7"
  surface_finish: "Ra 0.8 μm"
chemicalProperties:
  reactivity: "Low"
  corrosion_resistance: "High"
  oxidation_behavior: "Forms protective layer"
keywords:
  - "aluminum laser cleaning"
  - "metal surface preparation"
  - "industrial cleaning"
title: "Aluminum Laser Cleaning Guide"
headline: "Professional Aluminum Surface Preparation"
author: "Dr. Sarah Chen"
article_type: "material"
---
```

## Troubleshooting

### Common Issues

1. **"No frontmatter data available"**
   - Check if frontmatter file exists
   - Verify file path and naming convention

2. **"Missing required frontmatter fields"**
   - Add missing fields to frontmatter file
   - Validate YAML structure

3. **"Component generation failed"**
   - Check frontmatter data completeness
   - Run validation tests

### Debugging Steps

1. Run frontmatter validation:
   ```bash
   python3 -c "from tests.test_frontmatter_dependency_chain import validate_frontmatter_for_generation; print(validate_frontmatter_for_generation(your_data))"
   ```

2. Check frontmatter file:
   ```bash
   cat content/components/frontmatter/aluminum-laser-cleaning.yaml
   ```

3. Run dependency tests:
   ```bash
   python3 tests/test_frontmatter_dependency_chain.py
   ```

## Conclusion

The frontmatter dependency architecture ensures:

- **Data Integrity**: All components have required information
- **Fail-Fast Behavior**: Issues identified immediately
- **Clear Error Messages**: Users understand failure causes
- **No Silent Failures**: System fails explicitly rather than generating incorrect content
- **Maintainable Code**: Clear dependency chain and validation

This design prioritizes correctness over convenience, ensuring that generated content is always based on complete and accurate material data.
