# Range Functions in Frontmatter Generator

## Overview
The range functions in `StreamlinedFrontmatterGenerator` provide **materials science research-based** Min/Max ranges for DataMetrics schema compliance. Instead of generic calculations, they use actual material property data from `materials.yaml`.

## Architecture

### Materials Science Research Approach
Range functions now use comprehensive materials research data:
- **Material Category Ranges**: Extracted from `materials.yaml` `category_ranges` section
- **Machine Settings Ranges**: Based on laser equipment specifications in `machineSettingsRanges`
- **Property-Specific**: Each material category (metal, ceramic, glass, etc.) has scientifically researched ranges
- **Equipment-Based**: Machine settings use actual laser equipment operational limits

### DataMetrics Schema Requirements
Every property must include:
- `value`: Numeric value (required)
- `unit`: Unit string (required) 
- `confidence`: Confidence level 0.0-1.0 (required)
- `min`: Research-based minimum range value (required)
- `max`: Research-based maximum range value (required)
- `description`: Property description (required)

### Research-Based Implementation

#### _generate_properties_with_ranges()
- **Purpose**: Generate material properties with research-based Min/Max ranges
- **Data Source**: `materials.yaml` `category_ranges` section
- **Range Logic**: Uses actual material science data for each category
- **Material Categories**: metal, ceramic, glass, composite, plastic, etc.
- **Properties Handled**: 
  - density (e.g., metals: 0.53-22.59 g/cm³)
  - thermalConductivity (e.g., metals: 6.3-429 W/m·K)
  - tensileStrength (e.g., metals: 70-2000 MPa)
  - youngsModulus, hardness, electricalConductivity

#### _generate_machine_settings_with_ranges() 
- **Purpose**: Generate machine settings with equipment-based Min/Max ranges
- **Data Source**: `materials.yaml` `machineSettingsRanges` section
- **Range Logic**: Based on actual laser equipment specifications
- **Settings Handled**:
  - powerRange (1W - 10,000W)
  - pulseDuration (1fs - 1,000,000,000ns)
  - wavelength (157nm - 10,600nm)
  - spotSize (0.01mm - 50mm)

#### _get_research_based_range()
- **Purpose**: Core research data lookup for accurate ranges
- **Material Properties**: Maps to category_ranges by material type
- **Machine Settings**: Maps to machineSettingsRanges
- **Fallback Protection**: Uses calculated ranges only if research data missing

### Integration with AI Generation

#### Research-Enhanced Approach
1. **AI Generation**: Create content via `_generate_from_api()`
2. **Research Enhancement**: Apply `_get_research_based_range()` for accurate Min/Max
3. **Schema Compliance**: Guarantee all required fields present with real data

#### _merge_with_ranges()
- **Purpose**: Merge AI content with research-based Min/Max
- **Research Priority**: Always use materials science data for ranges
- **AI Preservation**: Keep AI-generated descriptions and confidence when superior

### Materials Science Data Structure
```
category_ranges:
  metal:
    density: {min: 0.53 g/cm³, max: 22.59 g/cm³}
    thermalConductivity: {min: 6.3 W/m·K, max: 429 W/m·K}
  ceramic:
    density: {min: 1.8 g/cm³, max: 15.7 g/cm³}
    
machineSettingsRanges:
  powerRange: {min: 1 W, max: 10000 W}
  wavelength: {min: 157 nm, max: 10600 nm}
```

## Usage Examples

### Research-Based Material Properties
```python
# Input: Aluminum (metal category)
material_data = {
    'category': 'metal',
    'density': '2.7 g/cm³',
    'thermal_conductivity': '237 W/m·K'
}

# Research-based range processing
properties = generator._generate_properties_with_ranges(material_data)
```

### Output Structure with Research Data
```yaml
density:
  value: 2.7
  unit: 'g/cm³' 
  confidence: 0.85
  min: 0.53     # Metal category research minimum
  max: 22.59    # Metal category research maximum
  description: 'density property'

thermalConductivity:
  value: 237
  unit: 'W/m·K'
  confidence: 0.85
  min: 6.3      # Metal category research minimum
  max: 429      # Metal category research maximum
  description: 'thermalConductivity property'
```

### Machine Settings Example
```yaml
powerRange:
  value: 150.0
  unit: 'W'
  confidence: 0.85
  min: 1.0      # Laser equipment minimum from research
  max: 10000.0  # Laser equipment maximum from research
  description: 'powerRange property'
```

## Research Data Sources

### Material Property Ranges
- **Density**: Comprehensive material density database
- **Thermal Properties**: Heat conduction and thermal research
- **Mechanical Properties**: Strength and elasticity data
- **Electrical Properties**: Conductivity measurements

### Machine Settings Ranges  
- **Power Range**: Laser equipment specifications (1W-10kW)
- **Wavelength**: Available laser wavelengths (UV to IR)
- **Pulse Duration**: Femtosecond to continuous operation
- **Spot Size**: Micro-machining to large area processing

## Error Handling
- **Missing Research Data**: Falls back to calculated ranges with warning
- **Invalid Categories**: Uses 'metal' as default category
- **Data Loading Failure**: Fail-fast approach - system requires research data
- **Type Safety**: Validates all numeric extractions before processing

## Testing with Research Data
Range functions tested against actual materials science data:
```python
generator = StreamlinedFrontmatterGenerator(api_client, config)

# Test with aluminum (metal category)
aluminum_data = {'category': 'metal', 'density': '2.7 g/cm³'}
properties = generator._generate_properties_with_ranges(aluminum_data)

# Verify research-based ranges
assert properties['density']['min'] == 0.53   # Metal category minimum
assert properties['density']['max'] == 22.59  # Metal category maximum
```

## Architecture Evolution
1. **Legacy**: Generic ±20% percentage calculations
2. **Transition**: Mixed approach with some research data
3. **Current**: Full materials science research-based ranges
4. **Future**: Enhanced confidence scoring based on research quality and data sources