# PropertyDataMetric Format Documentation

## Overview

The PropertyDataMetric format represents a fundamental shift from flat property representation to structured, confidence-scored property data. This format enables comprehensive property management with built-in quality assessment, range specifications, and measurement units.

## Format Evolution

### Legacy Flat Format (Deprecated)
```yaml
# Old approach - multiple fields per property
density: 5.68
densityUnit: "g/cm³"
densityMin: 5.0
densityMax: 6.0
densityConfidence: 95

meltingPoint: 2715
meltingPointUnit: "°C"
meltingPointMin: 2700
meltingPointMax: 2730
```

**Problems with Legacy Format:**
- Field explosion (4-5 fields per property)
- Inconsistent naming patterns
- No standardized confidence scoring
- Difficult to validate and maintain
- Poor schema enforcement

### New Structured Format (PropertyDataMetric)
```yaml
# New approach - nested structure per property
density:
  value: 5.68
  unit: "g/cm³"
  min: 5.0
  max: 6.0
  confidence: 95

meltingPoint:
  value: 2715
  unit: "°C"
  min: 2700
  max: 2730
  confidence: 90
```

**Benefits of Structured Format:**
- Single nested object per property
- Consistent structure across all properties
- Built-in confidence scoring
- Easier validation and schema enforcement
- Cleaner property management

## PropertyDataMetric Schema Definition

### Core Structure
```json
{
  "PropertyDataMetric": {
    "type": "object",
    "properties": {
      "value": {
        "type": ["number", "string"],
        "description": "The primary property value (required)"
      },
      "unit": {
        "type": "string", 
        "description": "Unit of measurement (optional)"
      },
      "min": {
        "type": "number",
        "description": "Minimum range value (optional)"
      },
      "max": {
        "type": "number", 
        "description": "Maximum range value (optional)"
      },
      "confidence": {
        "type": "integer",
        "minimum": 0,
        "maximum": 100,
        "description": "Confidence score 0-100 (optional)"
      }
    },
    "required": ["value"],
    "additionalProperties": false
  }
}
```

### Field Specifications

#### `value` (Required)
- **Type**: `number` or `string`
- **Purpose**: The primary property measurement or specification
- **Examples**: `5.68`, `"Diode-pumped solid-state laser"`, `2715`

#### `unit` (Optional)
- **Type**: `string`
- **Purpose**: Measurement unit for the value
- **Examples**: `"g/cm³"`, `"°C"`, `"W/m·K"`, `"Mohs"`, `"kHz"`
- **Standards**: Use standard SI units where possible

#### `min` (Optional)
- **Type**: `number`
- **Purpose**: Minimum value in the acceptable/typical range
- **Use Cases**: Processing parameters, material property ranges
- **Example**: For laser power range, minimum effective power

#### `max` (Optional)
- **Type**: `number`
- **Purpose**: Maximum value in the acceptable/typical range
- **Use Cases**: Safe operating limits, material property ranges
- **Example**: For laser power range, maximum safe power

#### `confidence` (Optional)
- **Type**: `integer` (0-100)
- **Purpose**: Data quality and reliability indicator
- **Scoring System**:
  - `90-100`: Authoritative sources (peer-reviewed, standards)
  - `80-89`: Manufacturer specifications, technical datasheets
  - `70-79`: Established databases, multiple source correlation
  - `60-69`: AI research with source verification
  - `40-59`: Estimated or interpolated values
  - `0-39`: Uncertain or placeholder values

## Real-World Examples

### Material Properties

#### High-Confidence Property (Authoritative Source)
```yaml
density:
  value: 5.68
  unit: "g/cm³"
  confidence: 95
```

#### Property with Range (Processing Parameter)
```yaml
thermalConductivity:
  value: 200.05
  unit: "W/m·K"
  min: 0.1
  max: 400
  confidence: 75
```

#### Complex Property (Multiple Characteristics)
```yaml
hardness:
  value: 8.5
  unit: "Mohs"
  min: 8.0
  max: 9.0
  confidence: 85
```

### Machine Settings

#### Laser Power Range
```yaml
powerRange:
  value: 120
  unit: "W"
  min: 120.0
  max: 420.0
  confidence: 85
```

#### Processing Speed Range
```yaml
processingSpeed:
  value: "15-70"
  unit: "mm/min"
  confidence: 75
```

#### String-Based Setting
```yaml
laserType:
  value: "Diode-pumped solid-state laser"
  confidence: 90
```

## Implementation Patterns

### Property Generation
```python
def create_structured_property(value, unit=None, min_val=None, max_val=None, confidence=None):
    """Create a PropertyDataMetric-compliant property"""
    property_data = {"value": value}
    
    if unit:
        property_data["unit"] = unit
    if min_val is not None:
        property_data["min"] = min_val
    if max_val is not None:
        property_data["max"] = max_val
    if confidence is not None:
        property_data["confidence"] = confidence
    
    return property_data

# Usage
density_property = create_structured_property(
    value=5.68,
    unit="g/cm³",
    confidence=95
)
```

### Property Validation
```python
def validate_property_data_metric(property_data):
    """Validate PropertyDataMetric compliance"""
    if not isinstance(property_data, dict):
        raise ValueError("Property must be a dictionary")
    
    if "value" not in property_data:
        raise ValueError("Property must have a 'value' field")
    
    # Validate confidence score
    if "confidence" in property_data:
        confidence = property_data["confidence"]
        if not isinstance(confidence, int) or not (0 <= confidence <= 100):
            raise ValueError("Confidence must be an integer between 0 and 100")
    
    return True
```

### Property Access Patterns
```python
def get_property_value(property_data, default=None):
    """Safely extract property value"""
    if isinstance(property_data, dict) and "value" in property_data:
        return property_data["value"]
    return default

def get_property_confidence(property_data, default=0):
    """Safely extract confidence score"""
    if isinstance(property_data, dict) and "confidence" in property_data:
        return property_data["confidence"]
    return default

def has_range_data(property_data):
    """Check if property has min/max range data"""
    if not isinstance(property_data, dict):
        return False
    return "min" in property_data and "max" in property_data
```

## Migration Strategies

### Automated Migration
```python
def migrate_flat_to_structured(flat_properties):
    """Convert legacy flat format to structured format"""
    structured_properties = {}
    processed_props = set()
    
    for key, value in flat_properties.items():
        # Skip if already processed as part of a property group
        if key in processed_props:
            continue
            
        # Find base property name
        base_prop = None
        if key.endswith("Unit"):
            base_prop = key[:-4]  # Remove "Unit" suffix
        elif key.endswith("Min"):
            base_prop = key[:-3]  # Remove "Min" suffix
        elif key.endswith("Max"):
            base_prop = key[:-3]  # Remove "Max" suffix
        else:
            base_prop = key
            
        # Build structured property
        structured_prop = {"value": flat_properties[base_prop]}
        
        # Add unit if exists
        unit_key = f"{base_prop}Unit"
        if unit_key in flat_properties:
            structured_prop["unit"] = flat_properties[unit_key]
            processed_props.add(unit_key)
            
        # Add min/max if exists
        min_key = f"{base_prop}Min"
        max_key = f"{base_prop}Max"
        if min_key in flat_properties:
            structured_prop["min"] = flat_properties[min_key]
            processed_props.add(min_key)
        if max_key in flat_properties:
            structured_prop["max"] = flat_properties[max_key]
            processed_props.add(max_key)
            
        structured_properties[base_prop] = structured_prop
        processed_props.add(base_prop)
    
    return structured_properties
```

### Backward Compatibility Support
```python
def get_property_with_fallback(properties, prop_name):
    """Get property value with fallback to legacy format"""
    # Try structured format first
    if prop_name in properties:
        prop_data = properties[prop_name]
        if isinstance(prop_data, dict) and "value" in prop_data:
            return prop_data["value"]
        else:
            return prop_data  # Legacy direct value
    
    # Fallback to legacy flat format
    return properties.get(prop_name)
```

## Quality Assurance

### Confidence Score Guidelines

#### 90-100: Authoritative Sources
- Peer-reviewed scientific publications
- Industry standards (ASTM, ISO, etc.)
- Official material specifications
- Manufacturer certified data

#### 80-89: Manufacturer Data
- Technical datasheets
- Product specifications
- Engineering documentation
- Certified test results

#### 70-79: Database Sources
- Materials property databases
- Multiple source correlation
- Industry reference materials
- Cross-validated measurements

#### 60-69: AI Research
- AI-generated with source verification
- Literature synthesis
- Calculated from related properties
- Expert system recommendations

#### 40-59: Estimated Values
- Interpolated from similar materials
- Rule-of-thumb calculations
- Approximate ranges
- Preliminary measurements

#### 0-39: Uncertain Data
- Placeholder values
- Unverified sources
- Conflicting information
- Requires further research

### Data Validation Rules

#### Value Validation
```python
def validate_property_value(property_data, prop_name):
    """Validate property value makes sense"""
    value = property_data.get("value")
    unit = property_data.get("unit", "")
    
    # Physical property validation
    if prop_name == "density" and isinstance(value, (int, float)):
        if value <= 0:
            raise ValueError("Density must be positive")
        if unit == "g/cm³" and value > 25:  # Osmium is ~22.6
            raise ValueError("Density seems too high")
    
    if prop_name == "meltingPoint" and isinstance(value, (int, float)):
        if unit == "°C" and value < -273:
            raise ValueError("Temperature below absolute zero")
```

#### Range Validation
```python
def validate_property_ranges(property_data):
    """Validate min/max ranges are logical"""
    if "min" in property_data and "max" in property_data:
        min_val = property_data["min"]
        max_val = property_data["max"]
        
        if min_val >= max_val:
            raise ValueError("Minimum value must be less than maximum")
        
        # Check if main value is within range
        value = property_data.get("value")
        if isinstance(value, (int, float)):
            if value < min_val or value > max_val:
                raise ValueError("Value outside specified range")
```

## Best Practices

### Property Naming
- Use camelCase for property names: `meltingPoint`, `thermalConductivity`
- Use descriptive, unambiguous names
- Follow established materials science terminology
- Maintain consistency across similar properties

### Unit Specifications
- Use standard SI units where possible
- Include proper unit symbols: `"W/m·K"`, `"g/cm³"`, `"J/cm²"`
- Be consistent with unit formatting
- Document non-standard units clearly

### Confidence Scoring
- Always provide confidence scores when available
- Be conservative with confidence assignments
- Document confidence reasoning in comments
- Update confidence when new data becomes available

### Range Usage
- Use ranges for processing parameters
- Include safety margins in max values
- Provide typical operating ranges
- Distinguish between theoretical and practical limits

## Conclusion

The PropertyDataMetric format provides a robust foundation for structured property management in the Z-Beam Generator system. By standardizing property representation and including confidence scoring, this format enables better data quality assessment, easier validation, and more reliable property management across the entire laser cleaning parameter generation system.