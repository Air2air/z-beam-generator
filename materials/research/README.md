# Property Research System

## Overview

The Property Research System provides **uniform property research** for all frontmatter keys using a single, generic `PropertyResearcher` class. All properties (powerRange, density, wavelength, thermalConductivity, etc.) are treated identically without artificial distinctions.

## Architecture

```
PropertyResearcher
├── Multi-strategy research (AI → Web API → Database → Estimation)
├── PropertyDataMetric output format  
├── Confidence scoring and range handling
└── Fail-fast validation
```

## Core Component

### PropertyResearcher (`property_researcher.py`)

**Purpose**: Research individual material property values using multiple fallback strategies

**Key Methods**:
- `research_property_value(material, property_name)` → PropertyDataMetric
- Multi-strategy execution with confidence scoring
- Range-aware output (min/max when appropriate)

**Usage Example**:
```python
researcher = PropertyResearcher()
result = researcher.research_property_value("Zirconia", "powerRange")
# Returns: PropertyDataMetric(value=120, unit="W", confidence=85, min=120.0, max=420.0)
```

## Key Principles

1. **No Special Cases**: powerRange, density, wavelength all handled uniformly
2. **Multi-Strategy Fallback**: AI → Web API → Database → Estimation
3. **Confidence-Driven**: Every result includes confidence percentage
4. **Range-Aware**: Min/max ranges when property varies with conditions
5. **Fail-Fast**: Invalid inputs cause immediate failure with clear errors

## Integration

The PropertyResearcher integrates directly with the frontmatter generation process:
1. ComponentGeneratorFactory creates frontmatter generator
2. Frontmatter generator identifies missing properties
3. PropertyResearcher researches each missing property individually
4. Results formatted as PropertyDataMetric and added to YAML frontmatter

## Test Coverage

Comprehensive testing ensures:
- ✅ **Exact Zirconia matches**: density (5.68 g/cm³), melting point (2715°C) 
- ✅ **powerRange calculation**: Handles machine settings uniformly
- ✅ **Multi-strategy fallback**: AI → Web API → Database → Estimation
- ✅ **Error handling**: Proper exception management and logging
- ✅ **PropertyDataMetric format**: Consistent structured output

Run tests with: `python3 components/frontmatter/tests/test_property_researcher.py`