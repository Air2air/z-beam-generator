# Research Pipeline Architecture

## Overview

The Z-Beam Generator's Research Pipeline Architecture represents a fundamental enhancement to the material prompting system, transforming static property generation into a dynamic, research-driven process that automatically discovers, validates, and populates material properties and machine settings through online research and AI-powered analysis.

## Core Architecture Principles

### 1. Research-Driven Property Discovery
- **Systematic Discovery**: Automatically identifies applicable material properties based on material category (ceramic, metal, plastic)
- **Online Research Integration**: Leverages web APIs and AI systems to research actual property values from authoritative sources
- **Dynamic Property Lists**: Creates working lists of properties in memory for processing and validation

### 2. Structured Data Format (PropertyDataMetric)
```yaml
# Legacy Format (Deprecated)
density: 5.68
densityUnit: "g/cm³"
densityMin: 5.0
densityMax: 6.0

# New Structured Format
density:
  value: 5.68
  unit: "g/cm³"
  min: 5.0
  max: 6.0
  confidence: 95
```

### 3. Multi-Phase Pipeline Processing
1. **Discovery Phase**: Identify applicable properties for material type
2. **Research Phase**: Online research for each property value
3. **Validation Phase**: Verify and score property data quality
4. **Population Phase**: Structure and save validated properties
5. **Machine Settings Phase**: Repeat process for laser parameters

## System Components

### ResearchPipelineManager
**Location**: `components/frontmatter/research/research_pipeline.py`

The central orchestrator that manages the complete research workflow.

#### Key Methods:
- `execute_complete_pipeline(material_name, category)`: Main entry point for full pipeline execution
- `research_material_properties(material_name, applicable_properties)`: Research material property values
- `research_machine_settings(material_name, material_properties)`: Research laser parameter settings

#### Pipeline Flow:
```python
# Complete pipeline execution
results = pipeline_manager.execute_complete_pipeline("Zirconia", "ceramic")

# Pipeline phases:
# 1. Discover applicable properties for ceramic materials
# 2. Research each property online with AI assistance
# 3. Validate property values and assign confidence scores
# 4. Structure data using PropertyDataMetric format
# 5. Research corresponding machine settings
# 6. Return complete structured dataset
```

### MaterialPropertyDiscoverer
**Purpose**: Discovers applicable properties based on material category and characteristics.

#### Discovery Logic:
```python
# Category-based property discovery
ceramic_properties = [
    "density", "meltingPoint", "thermalConductivity", 
    "hardness", "thermalShockResistance", "compressiveStrength"
]

metal_properties = [
    "density", "meltingPoint", "thermalConductivity",
    "yieldStrength", "ultimateTensileStrength", "elasticModulus"
]

plastic_properties = [
    "density", "glassTradition", "thermalConductivity",
    "tensileStrength", "flexuralModulus", "impactStrength"
]
```

### PropertyResearcher
**Purpose**: Handles individual property research using multiple data sources and validation methods.

#### Research Sources:
- **Primary**: AI-powered research with context-aware prompting
- **Secondary**: Web API integration for materials databases
- **Fallback**: Estimated values with lower confidence scores

#### Validation Framework:
```python
confidence_scoring = {
    "authoritative_source": 95,      # Peer-reviewed publications, standards
    "manufacturer_data": 85,         # Technical datasheets, specifications
    "database_lookup": 75,           # Materials property databases
    "ai_research": 65,              # AI-generated with source verification
    "estimated_value": 45           # Calculated or interpolated values
}
```

## Integration Architecture

### DynamicPropertyGenerator Integration
**Location**: `components/frontmatter/core/dynamic_property_generator.py`

The research pipeline integrates seamlessly with existing generators through a layered approach:

```python
def generate_properties_for_material(self, material_name: str, existing_data: Dict = None) -> Dict:
    """
    Three-tier generation strategy:
    1. Research Pipeline (Primary) - Comprehensive online research
    2. Legacy Research System (Fallback) - Existing research integration
    3. Basic Properties (Final Fallback) - Static property extraction
    """
    
    # Tier 1: Research Pipeline
    if self.pipeline_manager:
        results = self.pipeline_manager.execute_complete_pipeline(material_name, material_category)
        if results and results.get("materialProperties"):
            return results["materialProperties"]
    
    # Tier 2 & 3: Fallback systems
    return self._generate_legacy_research_properties(material_name, existing_data)
```

### Schema Integration
**Location**: `schemas/active/frontmatter.json`

The PropertyDataMetric schema definition supports the structured property format:

```json
{
  "PropertyDataMetric": {
    "type": "object",
    "properties": {
      "value": {"type": ["number", "string"], "description": "The primary property value"},
      "unit": {"type": "string", "description": "Unit of measurement"},
      "min": {"type": "number", "description": "Minimum range value"},
      "max": {"type": "number", "description": "Maximum range value"},
      "confidence": {"type": "integer", "minimum": 0, "maximum": 100}
    },
    "required": ["value"],
    "additionalProperties": false
  }
}
```

## Workflow Documentation

### Complete Research Pipeline Workflow

#### Phase 1: Material Analysis
```python
material_name = "Zirconia"
material_category = determine_material_category(material_name)  # "ceramic"
```

#### Phase 2: Property Discovery
```python
discoverer = MaterialPropertyDiscoverer()
applicable_properties = discoverer.discover_applicable_properties(
    material_name="Zirconia",
    material_category="ceramic"
)
# Returns: ["density", "meltingPoint", "thermalConductivity", "hardness", ...]
```

#### Phase 3: Property Research
```python
researcher = PropertyResearcher()
property_results = {}

for property_name in applicable_properties:
    result = researcher.research_property(
        material_name="Zirconia",
        property_name=property_name
    )
    property_results[property_name] = {
        "value": result.value,
        "unit": result.unit,
        "min": result.min_range,
        "max": result.max_range,
        "confidence": result.confidence_score
    }
```

#### Phase 4: Machine Settings Research
```python
machine_settings = researcher.research_machine_settings(
    material_name="Zirconia",
    material_properties=property_results
)
```

#### Phase 5: Result Compilation
```python
complete_results = {
    "materialProperties": property_results,
    "machineSettings": machine_settings
}
```

## Implementation Examples

### Real-World Example: Zirconia Processing
```yaml
materialProperties:
  density:
    value: 5.68
    unit: g/cm³
    confidence: 95
  meltingPoint:
    value: 2715
    unit: °C
    confidence: 90
  thermalConductivity:
    value: 200.05
    unit: W/m·K
    min: 0.1
    max: 400
    confidence: 75

machineSettings:
  powerRange:
    value: 120
    unit: W
    min: 120.0
    max: 420.0
    confidence: 85
  wavelength:
    value: 1064
    unit: nm
    confidence: 95
```

### API Integration Pattern
```python
# Research pipeline with API fallback
class PropertyResearcher:
    def research_property(self, material_name: str, property_name: str):
        # Primary: AI-powered research
        ai_result = self._research_with_ai(material_name, property_name)
        if ai_result.confidence >= 65:
            return ai_result
        
        # Secondary: Web API research
        api_result = self._research_with_web_api(material_name, property_name)
        if api_result.confidence >= 45:
            return api_result
        
        # Fallback: Estimated values
        return self._generate_estimated_value(material_name, property_name)
```

## Performance and Reliability

### Caching Strategy
- **Property Results Caching**: Cache research results to avoid duplicate API calls
- **Material Category Caching**: Cache material categorization for repeated materials
- **API Response Caching**: Cache web API responses with TTL expiration

### Error Handling
```python
class ResearchPipelineError(Exception):
    """Base exception for research pipeline failures"""
    pass

class PropertyResearchError(ResearchPipelineError):
    """Individual property research failure"""
    pass

class PipelineConfigurationError(ResearchPipelineError):
    """Pipeline configuration or setup failure"""
    pass
```

### Fail-Fast Architecture
- **Configuration Validation**: Validate all required dependencies on initialization
- **API Key Validation**: Ensure API keys are available before research begins
- **Data Source Validation**: Verify research sources are accessible
- **Result Validation**: Validate structured format compliance before return

## Migration Path

### From Legacy to Research Pipeline

#### Legacy Generator Usage:
```python
# Old approach - static property extraction
properties = generator.generate_basic_properties(existing_data)
```

#### New Research Pipeline Usage:
```python
# New approach - dynamic research-driven generation
pipeline = ResearchPipelineManager()
results = pipeline.execute_complete_pipeline(material_name, category)
properties = results["materialProperties"]
```

### Backward Compatibility
- Legacy generators remain functional during transition
- Gradual migration path with fallback mechanisms
- Support for both flat and structured property formats during transition period

## Benefits and Impact

### Enhanced Data Quality
- **Authoritative Sources**: Properties sourced from peer-reviewed publications and technical standards
- **Confidence Scoring**: Transparent quality assessment for each property value
- **Range Data**: Comprehensive min/max ranges for processing parameter optimization

### Improved Automation
- **Dynamic Discovery**: Automatically identifies relevant properties for any material
- **Reduced Manual Work**: Eliminates need for manual property research and entry
- **Scalable Processing**: Can process hundreds of materials systematically

### Better User Experience
- **Comprehensive Data**: Complete property profiles with confidence indicators
- **Consistent Format**: Standardized structured format across all materials
- **Transparency**: Clear indication of data sources and reliability

## Future Enhancements

### Planned Improvements
1. **Machine Learning Integration**: Property prediction models based on material composition
2. **Expert System Integration**: Rule-based validation using materials science knowledge
3. **Real-time Updates**: Automatic property updates when new research becomes available
4. **Custom Property Discovery**: User-defined property sets for specialized applications

### Extensibility Points
- **Custom Research Sources**: Plugin architecture for additional data sources
- **Property Validators**: Custom validation rules for specific material categories
- **Export Formats**: Multiple output formats for different use cases

## Conclusion

The Research Pipeline Architecture represents a paradigm shift from static to dynamic property generation, enabling the Z-Beam Generator to automatically research, validate, and populate comprehensive material properties and machine settings. This enhancement provides the foundation for scalable, high-quality laser cleaning parameter generation while maintaining system reliability and user trust through transparent confidence scoring and robust fallback mechanisms.