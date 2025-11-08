# Deep Research Schema for Properties & Settings

**Purpose**: Enable drill-down pages with multiple researched values per property/setting  
**Date**: November 7, 2025  
**Schema Version**: 3.0.0

---

## 🎯 Overview

This schema extends MaterialProperties.yaml and MachineSettings.yaml to support:
- Multiple values per property from different sources
- Context-specific variations (wavelength, power, material condition)
- Rich metadata (research papers, confidence intervals, validation data)
- Drill-down page generation with comparative analysis

---

## 📊 Current Schema (v2.0) - Single Value

```yaml
properties:
  Aluminum:
    material_characteristics:
      density:
        value: 2.70
        unit: g/cm³
        confidence: 100
        source: ai_research
```

**Limitation**: Only one value per property. No way to represent:
- Different measurement methods
- Multiple authoritative sources
- Context-dependent variations
- Historical research data

---

## 🚀 Enhanced Schema (v3.0) - Deep Research

### Structure

```yaml
properties:
  Aluminum:
    material_characteristics:
      density:
        # Primary value (current system - PRESERVED)
        value: 2.70
        unit: g/cm³
        confidence: 100
        source: ai_research
        
        # NEW: Deep research data
        research:
          values:
            - value: 2.70
              unit: g/cm³
              confidence: 100
              source: "ASM Handbook Vol. 2 - Properties of Metals"
              source_type: handbook
              method: "X-ray diffraction"
              temperature: 20°C
              purity: "99.9%"
              notes: "Standard reference value for pure aluminum"
              
            - value: 2.699
              unit: g/cm³
              confidence: 95
              source: "MatWeb Materials Database"
              source_type: database
              url: "https://matweb.com/search/..."
              notes: "Commercial purity (99.5%)"
              
            - value: 2.71
              unit: g/cm³
              confidence: 90
              source: "Aluminum Association Standards"
              source_type: industry_standard
              alloy: "1100-H14"
              notes: "Work-hardened alloy variant"
          
          metadata:
            total_sources: 3
            value_range: {min: 2.699, max: 2.71}
            standard_deviation: 0.006
            consensus_value: 2.70
            last_researched: "2025-11-07"
            research_depth: comprehensive
```

---

## 🔬 Machine Settings Deep Research

### Context-Specific Values

```yaml
settings:
  Aluminum:
    wavelength:
      # Primary value (current system - PRESERVED)
      value: 1064
      unit: nm
      description: "Near-IR wavelength for optimal absorption"
      
      # NEW: Deep research with context variations
      research:
        values:
          # UV wavelength (355nm)
          - value: 355
            unit: nm
            confidence: 85
            source: "Journal of Laser Applications, 2023"
            source_type: academic
            doi: "10.2351/7.0000123"
            context:
              application: precision_cleaning
              material_condition: oxidized_surface
              advantages: ["High precision", "Minimal heat", "Surface selectivity"]
              disadvantages: ["Lower throughput", "Higher cost"]
              optimal_for: ["Thin oxide layers", "Delicate components"]
            performance:
              removal_rate: "0.5 μm/pass"
              surface_roughness: "Ra < 0.2 μm"
              damage_risk: low
          
          # Green wavelength (532nm)
          - value: 532
            unit: nm
            confidence: 80
            source: "Laser Cleaning Handbook, 2024"
            source_type: handbook
            context:
              application: general_cleaning
              material_condition: light_contamination
              advantages: ["Good absorption", "Moderate cost"]
              disadvantages: ["Less penetration than UV"]
            performance:
              removal_rate: "1.2 μm/pass"
              surface_roughness: "Ra < 0.5 μm"
              
          # Near-IR wavelength (1064nm) - PRIMARY
          - value: 1064
            unit: nm
            confidence: 95
            source: "Multiple industry sources"
            source_type: consensus
            context:
              application: industrial_cleaning
              material_condition: heavy_oxidation
              advantages: ["High efficiency", "Deep penetration", "Cost effective"]
              disadvantages: ["More heat generation"]
              optimal_for: ["Thick oxide", "Paint removal", "High throughput"]
              is_primary: true
            performance:
              removal_rate: "3.5 μm/pass"
              surface_roughness: "Ra < 1.0 μm"
              damage_risk: medium
              
          # CO2 wavelength (10640nm)
          - value: 10640
            unit: nm
            confidence: 75
            source: "Industrial Laser Cleaning Guide"
            source_type: manufacturer
            context:
              application: aggressive_cleaning
              material_condition: heavy_contamination
              advantages: ["Very high removal rate", "Strong absorption"]
              disadvantages: ["High thermal damage risk", "Poor precision"]
              not_recommended_for: ["Thin materials", "Precision work"]
            performance:
              removal_rate: "8.0 μm/pass"
              damage_risk: high
              
        metadata:
          available_wavelengths: [355, 532, 1064, 10640]
          primary_wavelength: 1064
          total_research_sources: 4
          last_researched: "2025-11-07"
          context_variations: ["application", "material_condition", "contamination_type"]
```

---

## 📐 Schema Fields Reference

### Research Value Object

```yaml
value:
  value: <number>              # The measured/researched value
  unit: <string>               # Unit of measurement
  confidence: <0-100>          # Confidence level (%)
  source: <string>             # Citation/source name
  source_type: <enum>          # Type of source
  
  # Optional metadata
  method?: <string>            # Measurement/research method
  temperature?: <string>       # Temperature conditions
  pressure?: <string>          # Pressure conditions
  purity?: <string>            # Material purity level
  alloy?: <string>             # Alloy designation
  doi?: <string>               # DOI for academic papers
  url?: <string>               # URL for online resources
  isbn?: <string>              # ISBN for books/handbooks
  date?: <string>              # Publication/measurement date
  notes?: <string>             # Additional notes
  
  # Context for settings
  context?:
    application: <string>      # Use case (precision, industrial, aggressive)
    material_condition: <string> # Material state (polished, oxidized, coated)
    contamination_type?: <string> # Type of contamination
    advantages?: <string[]>    # Benefits of this value
    disadvantages?: <string[]> # Drawbacks of this value
    optimal_for?: <string[]>   # Best use cases
    not_recommended_for?: <string[]> # Avoid for these cases
    is_primary?: <boolean>     # Is this the primary/recommended value?
    
  # Performance metrics
  performance?:
    removal_rate?: <string>    # Material removal rate
    surface_roughness?: <string> # Resulting surface quality
    damage_risk?: <enum>       # low/medium/high
    energy_efficiency?: <string>
    throughput?: <string>
```

### Research Metadata Object

```yaml
metadata:
  total_sources: <number>      # Number of research sources
  value_range?:                # Min/max across all values
    min: <number>
    max: <number>
  standard_deviation?: <number> # Statistical variation
  consensus_value?: <number>   # Most agreed-upon value
  last_researched: <date>      # Last research date
  research_depth: <enum>       # minimal/standard/comprehensive/exhaustive
  context_variations?: <string[]> # Types of context variations available
  available_wavelengths?: <number[]> # For wavelength-specific data
  available_power_levels?: <string[]> # For power-specific data
  primary_wavelength?: <number> # Primary/recommended wavelength
  primary_power?: <string>     # Primary/recommended power
```

### Source Types Enum

- `handbook` - Reference handbooks (ASM, CRC, etc.)
- `database` - Materials databases (MatWeb, NIST, etc.)
- `academic` - Peer-reviewed papers
- `industry_standard` - Standards organizations (ISO, ASTM, ANSI)
- `manufacturer` - Manufacturer specifications
- `consensus` - Multiple sources agreeing
- `experimental` - Lab measurements
- `simulation` - Computational models
- `ai_research` - AI-generated research (current system)

---

## 🎨 Use Cases

### 1. Property Drill-Down Page

**URL**: `/properties/density`

**Content**:
- Overview of density property
- Why it matters for laser cleaning
- Comparison table across materials
- Multiple research values per material
- Source citations and confidence levels
- Variation by purity/alloy/condition

### 2. Setting Drill-Down Page

**URL**: `/settings/wavelength`

**Content**:
- Overview of wavelength parameter
- How wavelength affects cleaning
- Material-specific wavelength recommendations
- Context-based selection guide (UV for precision, NIR for industrial, CO2 for aggressive)
- Performance comparison charts
- Research citations

### 3. Material-Property Deep Dive

**URL**: `/materials/aluminum/properties/thermal-conductivity`

**Content**:
- Aluminum thermal conductivity research
- Multiple values from different sources
- Variation by alloy (1100, 2024, 6061, 7075)
- Temperature dependence
- Impact on laser cleaning parameters
- Related properties correlation

### 4. Material-Setting Deep Dive

**URL**: `/materials/aluminum/settings/wavelength`

**Content**:
- Wavelength selection for aluminum
- Performance comparison (355nm vs 532nm vs 1064nm vs 10640nm)
- Application-specific recommendations
- Case studies and research
- Safety considerations
- Cost-effectiveness analysis

---

## 🔄 Migration Strategy

### Phase 1: Schema Extension (Non-Breaking)
1. Add `research` field to existing properties/settings
2. Keep current `value` field as primary (backward compatible)
3. New fields are optional - existing system works unchanged

### Phase 2: Research Population
1. Start with high-priority properties (density, thermalConductivity, hardness)
2. Start with high-priority settings (wavelength, powerRange, fluenceThreshold)
3. Gradually add multi-source research data
4. Use AI to research multiple sources per property/setting

### Phase 3: UI/Page Generation
1. Create drill-down page templates
2. Generate comparative visualizations
3. Add source citation system
4. Create context-based recommendation engine

---

## 📊 Example: Complete Property with Deep Research

```yaml
properties:
  Aluminum:
    material_characteristics:
      thermalConductivity:
        # Primary value (preserved)
        value: 237
        unit: W/(m·K)
        confidence: 95
        source: ai_research
        
        # Deep research
        research:
          values:
            - value: 237
              unit: W/(m·K)
              confidence: 100
              source: "ASM Handbook Vol. 2"
              source_type: handbook
              isbn: "978-1-62708-163-7"
              temperature: 25°C
              purity: "99.99% pure aluminum"
              method: "Laser flash method"
              
            - value: 247
              unit: W/(m·K)
              confidence: 95
              source: "NIST Materials Database"
              source_type: database
              url: "https://materialsdata.nist.gov"
              temperature: 20°C
              notes: "High purity specimen"
              
            - value: 180
              unit: W/(m·K)
              confidence: 90
              source: "Aluminum Association"
              source_type: industry_standard
              alloy: "6061-T6"
              notes: "Common structural alloy - lower due to alloying elements"
              
            - value: 130
              unit: W/(m·K)
              confidence: 90
              source: "Materials Science Journal"
              source_type: academic
              doi: "10.1016/j.matdes.2024.112234"
              alloy: "2024-T3"
              notes: "Aircraft alloy - copper addition reduces conductivity"
              
            - value: 160
              unit: W/(m·K)
              confidence: 85
              source: "Aerospace Materials Handbook"
              source_type: handbook
              alloy: "7075-T6"
              notes: "High-strength alloy - zinc addition reduces conductivity"
              
          metadata:
            total_sources: 5
            value_range: {min: 130, max: 247}
            standard_deviation: 47.8
            consensus_value: 237
            last_researched: "2025-11-07"
            research_depth: comprehensive
            alloy_variations: ["pure", "1100", "2024", "6061", "7075"]
            temperature_dependent: true
```

---

## 🛠️ Implementation Files

### New Files to Create

1. **`materials/data/PropertyResearch.yaml`**
   - Deep research for material properties
   - Multiple values per property per material
   - Rich metadata and citations

2. **`materials/data/SettingResearch.yaml`**
   - Deep research for machine settings
   - Context-specific variations
   - Performance metrics

3. **`materials/research/`** (directory)
   - Individual research files per property/setting
   - `density_research.yaml`
   - `wavelength_research.yaml`
   - etc.

### Loader Extensions

Add to `materials/data/loader.py`:
```python
def get_property_research(material_name: str, property_name: str) -> Dict[str, Any]:
    """Get deep research data for a specific property."""
    
def get_setting_research(material_name: str, setting_name: str) -> Dict[str, Any]:
    """Get deep research data for a specific setting."""
    
def get_all_research_for_property(property_name: str) -> Dict[str, Any]:
    """Get research across all materials for a property."""
    
def get_all_research_for_setting(setting_name: str) -> Dict[str, Any]:
    """Get research across all materials for a setting."""
```

---

## 🎯 Next Steps

1. **Approve schema design** - Review and approve the enhanced schema
2. **Create PropertyResearch.yaml** - New file for deep property research
3. **Create SettingResearch.yaml** - New file for deep setting research
4. **Extend loader** - Add new accessor functions
5. **Research population** - Start with high-priority properties/settings
6. **Page generation** - Create drill-down page templates
7. **Visualization** - Add comparison charts and tables

---

## 💡 Benefits

✅ **Rich Research Data**: Multiple sources per property/setting  
✅ **Context Awareness**: Different values for different use cases  
✅ **Source Attribution**: Proper academic/industry citations  
✅ **Comparative Analysis**: Easy comparison across materials/contexts  
✅ **Backward Compatible**: Existing system works unchanged  
✅ **Extensible**: Easy to add more research over time  
✅ **SEO Friendly**: Detailed pages rank better for specific queries  
✅ **User Education**: Helps users understand variations and trade-offs  

---

**Status**: Schema design complete, ready for implementation
