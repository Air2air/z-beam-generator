# AI Prompt Exception Handling - Integration Guide

## Overview
This system provides material-specific exception handling for AI prompts,
ensuring that generated content respects the unique characteristics of different
material categories (wood, ceramic, metal, plastic, composite, etc.).

## Metricsproperties Integration
**File:** `components/metricsproperties/generator.py`

### Integration Points:
**Generate Method:**
- Replace base prompt with material-aware prompt
```python
# BEFORE (existing code):
prompt = self.prompt_template.format(
    material_name=material_name,
    properties_summary=properties_summary
)

# AFTER (with exception handling):
from ai_research.prompt_exceptions.material_aware_generator import generate_material_specific_prompt

material_category = material_data.get('category', 'unknown')
prompt = generate_material_specific_prompt(
    component_type='metricsproperties',
    material_name=material_name,
    material_category=material_category,
    material_data=material_data,
    properties_summary=properties_summary
)
```

**Validation Method:**
- Add material-specific validation
```python
# Add after content generation:
from ai_research.prompt_exceptions.material_aware_generator import validate_component_content

is_valid, errors = validate_component_content(
    component_type='metricsproperties',
    material_category=material_category,
    generated_content=generated_content
)

if not is_valid:
    logger.warning(f"Material validation errors for {material_name}: {errors}")
    # Handle validation errors (retry, fallback, etc.)
```

### Benefits:
- Wood materials get decomposition temperature instead of melting point
- Ceramic materials use appropriate hardness scales (Mohs)
- Metal materials get validated thermal conductivity ranges
- Proper unit handling for different material types

## Metricsmachinesettings Integration
**File:** `components/metricsmachinesettings/generator.py`

### Integration Points:
**Generate Method:**
- Material-aware laser parameter generation
```python
# Enhanced prompt generation:
material_category = material_data.get('category', 'unknown')
prompt = generate_material_specific_prompt(
    component_type='metricsmachinesettings',
    material_name=material_name, 
    material_category=material_category,
    material_data=material_data,
    machine_settings_summary=machine_settings_summary
)
```

### Benefits:
- Metal materials get high-reflectance considerations
- Wood materials get moisture content warnings
- Ceramic materials get thermal shock considerations
- Appropriate power ranges for material categories

## Text Integration
**File:** `components/text/generators/fail_fast_generator.py`

### Integration Points:
**Prompt Construction:**
- Material-specific content guidance
```python
# In prompt construction phase:
material_category = material_data.get('category', 'unknown')
material_aware_prompt = generate_material_specific_prompt(
    component_type='text',
    material_name=material_name,
    material_category=material_category,
    material_data=material_data,
    content_requirements=content_requirements
)

# Combine with existing localization prompts:
final_prompt = localization_prompt + "\n\n" + material_aware_prompt
```

### Benefits:
- Wood content focuses on decomposition and grain properties
- Ceramic content emphasizes brittleness and thermal shock
- Metal content highlights conductivity and reflectance
- Appropriate technical terminology for each material type

## Frontmatter Integration
**File:** `components/frontmatter/core/streamlined_generator.py`

### Integration Points:
**Property Enhancement:**
- Material-aware property validation
```python
# During property enhancement:
from ai_research.prompt_exceptions.material_exception_handler import validate_property_for_material_type

for prop_name, prop_value in properties.items():
    is_valid, message = validate_property_for_material_type(
        material_category, prop_name, prop_value
    )
    
    if not is_valid:
        logger.warning(f"Property validation issue: {message}")
        # Apply correction or use fallback
```

### Benefits:
- Prevents invalid property combinations
- Ensures appropriate units for material types
- Validates property ranges against material categories
- Provides material-specific property descriptions

## Material-Specific Exception Rules

### Wood Materials
- `meltingPoint` → `decompositionTemperature`
- Density range: 0.16-1.4 g/cm³
- Hardness units: kN (Janka scale)
- Thermal conductivity: 0.04-0.4 W/m·K
- Considerations: Grain direction, moisture content

### Ceramic Materials
- Hardness units: Mohs scale preferred
- Emphasis on compressive over tensile strength
- Thermal shock resistance considerations
- Wide thermal conductivity range: 0.5-200 W/m·K

### Metal Materials
- High thermal conductivity expected: 1-500 W/m·K
- High reflectance considerations: 60-98%
- Surface oxidation effects on laser processing
- Electrical conductivity properties

### Plastic Materials
- Distinguish thermoplastic vs thermoset behavior
- Glass transition temperature considerations
- Temperature-dependent properties
- Low thermal conductivity: 0.1-2.0 W/m·K

### Composite Materials
- Anisotropic properties (direction-dependent)
- Fiber orientation effects
- Matrix and fiber property contributions
- Delamination considerations

## Implementation Checklist

### For Each Component:
- [ ] Import material-aware prompt generator
- [ ] Replace base prompts with material-aware versions
- [ ] Add material category detection
- [ ] Implement content validation
- [ ] Add error handling for validation failures
- [ ] Test with different material categories

### System-Wide:
- [ ] Update materials.yaml to ensure category consistency
- [ ] Add material category validation to input processing
- [ ] Create material-specific test cases
- [ ] Update documentation and examples
- [ ] Monitor validation errors and improve rules
