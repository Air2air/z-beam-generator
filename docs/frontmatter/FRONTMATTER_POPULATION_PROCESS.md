# Frontmatter Population Process

## Overview

The Z-Beam Generator uses a **two-stage component-based architecture** to dynamically populate YAML frontmatter for laser cleaning content. This process combines material-specific property discovery with dynamic property research to create comprehensive, technically accurate metadata.

## Two-Stage Architecture

### Stage 1: Property Discovery (Material-Aware)
```
MaterialPropertyResearchSystem.get_recommended_properties_for_material()
├── Material category detection (ceramic, wood, metal, etc.)  
├── Category-specific property mapping
└── Returns filtered list of relevant properties
```

**Key Principle**: Different material types have completely different relevant properties:
- **Ceramic**: density, meltingPoint, thermalShockResistance, hardness
- **Wood**: density, moistureContent, grainDensity, ligninContent  
- **Metal**: density, meltingPoint, tensileStrength, thermalConductivity

### Stage 2: Property Value Research (Generic)
```
PropertyResearcher.research_property_value()
├── Multi-strategy research (AI → Web API → Database → Estimation)
├── PropertyResult with confidence scoring
└── Uniform treatment of all property types
```

**Key Principle**: powerRange, density, wavelength all researched identically using the same methods.

## Complete Frontmatter Generation Flow

```
Material Input → Property Discovery → Property Research → Schema Validation → YAML Output
     ↓                    ↓                    ↓                    ↓              ↓
"Zirconia"    →    [density, melting    →    Research each    →    Validate    →    YAML
ceramic             Point, thermal           property value        structure        frontmatter
                   ShockResistance]          individually
```

### Detailed Process:

1. **Material Identification**: Extract material name and category from user input
2. **Stage 1 - Property Discovery**: `MaterialPropertyResearchSystem` determines relevant properties based on material category
3. **Stage 2 - Property Research**: `PropertyResearcher` researches actual values for each discovered property  
4. **Schema Validation**: Ensure all generated data matches expected frontmatter structure
5. **YAML Generation**: Output structured frontmatter with confidence scores

## Dynamic materialProperties Structure

The **materialProperties** section is completely dynamic based on material relevance:

```yaml
# Zirconia (ceramic) - ceramic-relevant properties only:
materialProperties:
  density:
    value: 5.68
    unit: g/cm³
    confidence: 95
  meltingPoint:
    value: 2715
    unit: °C  
    confidence: 90
  thermalShockResistance:  # ceramic-specific
    value: 525.0
    unit: °C
    confidence: 70

# Wood material would have completely different properties:
materialProperties:
  density:
    value: 0.65
    unit: g/cm³
    confidence: 85
  moistureContent:         # wood-specific
    value: 12
    unit: '%'
    confidence: 80
  grainDensity:           # wood-specific
    value: 0.45
    unit: g/cm³
    confidence: 75
```

## PropertyResearcher Integration

The **PropertyResearcher** handles Stage 2 uniformly:

```python
# Stage 1: Property Discovery (material-aware)
recommended_properties = research_system.get_recommended_properties_for_material("Zirconia")
# Returns: ["density", "meltingPoint", "thermalShockResistance", ...]

# Stage 2: Property Research (uniform)
for property_name in recommended_properties:
    result = property_researcher.research_property_value("Zirconia", property_name)
    # Each property researched identically regardless of type
```

## Key Architectural Principles

1. **Two-Stage Separation**: Property discovery (material-aware) vs property research (generic)
2. **Dynamic Structure**: materialProperties completely different per material type
3. **No Special Cases**: All properties in Stage 2 treated identically (powerRange = density = wavelength)
4. **Material-Category Mapping**: Ceramic gets ceramic properties, wood gets wood properties
5. **Confidence-Driven**: Every property includes confidence score and research strategy used
6. **Fail-Fast Validation**: Missing critical properties cause immediate generation failure

This architecture ensures that Zirconia gets ceramic-relevant properties like thermalShockResistance, while wood materials get wood-relevant properties like moistureContent - but all property values are researched using the same uniform PropertyResearcher system.