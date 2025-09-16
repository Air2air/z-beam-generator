# Frontmatter Technical Data Accuracy Guide

## Overview

This guide ensures that the frontmatter generator produces scientifically accurate, material-specific technical data rather than generic placeholder values. The system must deeply research each material's unique properties and generate appropriate laser processing parameters.

## Critical Requirements

### 1. Material-Specific Research

**REQUIRED**: Each material must have unique, researched technical specifications:
- ✅ Density values specific to the actual material
- ✅ Melting points accurate for the material type  
- ✅ Laser parameters appropriate for material properties
- ✅ Chemical formulas scientifically correct
- ❌ NO generic values used across multiple materials
- ❌ NO placeholder data like "steel density for ceramics"

### 2. API Configuration for Research Quality

**Token Limits**: High enough for comprehensive research
```python
# Current Configuration (VERIFIED)
frontmatter_config = {
    "max_tokens": 4000,  # Sufficient for complete technical content
    "temperature": 0.5,  # Balanced creativity for research
    "top_p": 0.9,        # Allows diverse research approaches
}
```

**Temperature Settings**: Balanced for research creativity
- `0.4-0.6`: Optimal for technical research
- Too low (0.1): Overly deterministic, generic results
- Too high (0.8+): Random, potentially inaccurate

### 3. Prompt Engineering for Accuracy

The prompt template must include:
- `[RESEARCH: material-specific values]` placeholders
- Requirements for scientific accuracy
- Instructions to avoid generic data
- Material type awareness

## Material-Specific Validation Criteria

### Ceramics (Silicon Nitride, Titanium Dioxide, etc.)
```yaml
# Example: Silicon Nitride (Si3N4)
properties:
  density: "3.17 g/cm³"           # SPECIFIC to Si3N4
  meltingPoint: "1900°C"          # Decomposition temp
  thermalConductivity: "30 W/m·K" # Actual Si3N4 value
technicalSpecifications:
  wavelength: "1064 nm, 532 nm"   # Appropriate for ceramics
  fluenceRange: "0.5-2.5 J/cm²"   # Safe for ceramic processing
```

### Metals (Aluminum, Steel, etc.)
```yaml
# Example: Aluminum 6061
properties:
  density: "2.70 g/cm³"           # SPECIFIC to Al 6061
  meltingPoint: "615-655°C"       # Actual alloy range
  thermalConductivity: "167 W/m·K" # Al 6061 specific
technicalSpecifications:
  wavelength: "1064 nm"           # Fiber laser for metals
  fluenceRange: "2-10 J/cm²"      # Higher for metal ablation
```

### Polymers (PTFE, etc.)
```yaml
# Example: PTFE
properties:
  density: "2.16 g/cm³"           # SPECIFIC to PTFE
  meltingPoint: "327°C"           # PTFE crystalline melting
  thermalConductivity: "0.25 W/m·K" # Low polymer conductivity
technicalSpecifications:
  wavelength: "10.6 μm"           # CO2 laser for polymers
  fluenceRange: "0.1-1.0 J/cm²"   # Lower for polymer processing
```

## Validation Tests

### 1. Technical Accuracy Tests
```python
def test_density_material_specific():
    """Ensure different materials have different density values"""
    materials = ["Silicon Nitride", "Aluminum 6061", "PTFE"]
    densities = []
    
    for material in materials:
        frontmatter = generate_frontmatter(material)
        density = extract_density(frontmatter)
        densities.append(density)
    
    # All densities must be different and realistic
    assert len(set(densities)) == len(densities)  # No duplicates
    assert all(0.5 < d < 25 for d in densities)   # Realistic range
```

### 2. Research Quality Indicators
- Specific numerical values (not round numbers)
- Multiple properties per material
- Material-appropriate applications
- Scientifically valid combinations

### 3. Anti-Generic Validation
```python
def test_no_generic_values():
    """Ensure no generic placeholder values are used"""
    forbidden_generic_values = [
        "7.85 g/cm³",      # Generic steel density
        "1500°C",          # Generic melting point
        "1064 nm only",    # Generic laser wavelength
    ]
    
    for material in test_materials:
        frontmatter = generate_frontmatter(material)
        for forbidden in forbidden_generic_values:
            assert forbidden not in frontmatter
```

## Implementation Checklist

### ✅ Completed Improvements
- [x] API token limits increased to 4000
- [x] Temperature optimized to 0.5 for balanced research
- [x] Prompt rewritten with research requirements
- [x] Base configuration updated for high-quality generation

### 🔄 Testing Requirements
- [ ] Run comprehensive technical accuracy tests
- [ ] Validate multiple materials generate unique data
- [ ] Verify research quality indicators
- [ ] Confirm API configuration effectiveness

### 📝 Documentation Updates
- [x] Technical accuracy test suite created
- [x] Material-specific validation criteria documented
- [x] API configuration requirements specified
- [x] Research quality guidelines established

## Common Issues and Solutions

### Issue: Generic Values Across Materials
**Problem**: Same density/melting point for different materials
**Solution**: Enhanced prompt with `[RESEARCH: specific values]` requirements

### Issue: API Truncation
**Problem**: Incomplete technical data generation
**Solution**: Increased max_tokens to 4000, optimized temperature

### Issue: Unrealistic Property Combinations
**Problem**: Metal properties on ceramics, etc.
**Solution**: Material-type awareness in prompt template

### Issue: Round Number Bias
**Problem**: Properties like "1500°C" instead of "1547°C"
**Solution**: Research-driven prompts requiring specific literature values

## Testing Commands

### Run Technical Accuracy Tests
```bash
# Full test suite
python -m pytest tests/test_frontmatter_technical_accuracy.py -v

# Specific test categories
python -m pytest tests/test_frontmatter_technical_accuracy.py::TestTechnicalDataAccuracy -v
python -m pytest tests/test_frontmatter_technical_accuracy.py::TestAPIConfigurationValidation -v
```

### Generate Test Samples
```bash
# Test multiple materials for comparison
python3 run.py --material "Silicon Nitride" --components frontmatter
python3 run.py --material "Aluminum 6061" --components frontmatter  
python3 run.py --material "PTFE" --components frontmatter
```

### Validate Generated Content
```bash
# Check for research quality
python3 scripts/validate_technical_accuracy.py content/components/frontmatter/
```

## Quality Assurance Process

1. **Pre-Generation**: Validate API configuration
2. **Generation**: Use research-driven prompts
3. **Post-Generation**: Run technical accuracy tests
4. **Validation**: Compare materials for uniqueness
5. **Documentation**: Update any identified issues

## Research Sources for Validation

- **Material Properties**: ASM International, NIST databases
- **Laser Parameters**: Laser processing literature, industrial standards
- **Chemical Formulas**: CAS Registry, chemical databases
- **Physical Properties**: Engineering handbooks, scientific literature

This guide ensures that every generated frontmatter meets professional scientific standards with material-specific, researched technical data.
