# Categories.yaml Data Generator Documentation

## Overview
The Categories.yaml generator is a **standalone data generation tool** that creates and periodically refreshes a comprehensive database of researched material property ranges organized by material categories and subcategories. This tool uses AI research to validate and update property ranges, creating an authoritative reference database.

## Purpose
1. **Standalone Database Creation**: Generate Categories.yaml as a standalone reference database
2. **AI-Powered Research**: Use AI to research and validate material property ranges for each category/subcategory
3. **Periodic Updates**: Refresh the database occasionally with latest research and validation
4. **Data Quality Assurance**: Ensure all property ranges are scientifically accurate and properly sourced
5. **No Integration Required**: Operates independently - other components can reference the generated Categories.yaml file

## Current State Analysis
The system already has a `category_ranges` section in `data/Materials.yaml` that provides:
- **Categories Covered**: ceramic, composite, glass, metal, organic, polymer, stone
- **Properties Per Category**: density, hardness, laserAbsorption, laserReflectivity, specificHeat, tensileStrength, thermalConductivity, thermalDestructionPoint, thermalDiffusivity, thermalExpansion, youngsModulus
- **Range Structure**: min/max values with proper units

## Proposed Enhancement: Subcategory-Specific Data

### Data Structure Design
```yaml
categories:
  metal:
    # Category-level defaults (current system)
    category_ranges:
      density:
        min: 0.53 g/cm³  # lithium
        max: 22.59 g/cm³ # osmium
        confidence: 98
      # ... other properties
    
    # NEW: Subcategory-specific refinements
    subcategories:
      ferrous:
        density:
          min: 7.2 g/cm³   # cast iron
          max: 8.0 g/cm³   # steel alloys
          typical: 7.85 g/cm³
          confidence: 99
        laserAbsorption:
          min: 0.8 10⁶/m
          max: 2.5 10⁶/m
          typical: 1.2 10⁶/m
          wavelength_optimized: 1064 nm
      
      non-ferrous:
        density:
          min: 0.53 g/cm³  # lithium
          max: 19.32 g/cm³ # gold
          typical: 8.96 g/cm³  # copper baseline
        laserAbsorption:
          min: 0.5 10⁶/m
          max: 1.8 10⁶/m
          typical: 0.85 10⁶/m
      
      reactive:
        density:
          min: 0.53 g/cm³  # lithium  
          max: 6.11 g/cm³  # europium
          typical: 1.74 g/cm³  # magnesium baseline
        specialConsiderations:
          - oxidation_sensitive
          - low_power_recommended
          - inert_atmosphere_required
```

## Implementation Requirements

### 1. Data Research Methodology
- **Primary Sources**: Scientific literature, materials handbooks, NIST databases
- **Validation**: Cross-reference multiple authoritative sources
- **Confidence Scoring**: Assign confidence levels (0-100) based on source quality
- **Range Justification**: Document the reasoning behind min/max boundaries

### 2. Property Coverage
Extract and research all properties currently used in frontmatter generation:

#### MaterialProperties DataMetrics:
- `density` (g/cm³)
- `meltingPoint` (°C) 
- `thermalConductivity` (W/m·K)
- `tensileStrength` (MPa)
- `hardness` (HV, HRC, Shore, Mohs)
- `youngsModulus` (GPa)
- `thermalExpansion` (10⁻⁶/°C)
- `specificHeat` (J/kg·K)
- `thermalDiffusivity` (mm²/s)
- `reflectivity` (%)
- `absorptionCoefficient` (10⁶/m)
- `ablationThreshold` (J/cm²)
- `oxidationResistance` (qualitative)
- `crystallineStructure` (crystal system)

#### MachineSettings DataMetrics:
- `powerRange` (W)
- `wavelength` (nm)
- `spotSize` (μm)
- `repetitionRate` (kHz)
- `fluenceThreshold` (J/cm²)
- `pulseWidth` (ns)
- `scanSpeed` (mm/s)
- `overlapRatio` (%)
- `passCount` (passes)

### 3. Subcategory Analysis from Materials.yaml
Current subcategories found in the data:
- **ceramic**: carbide, fired, oxide
- **composite**: composite, fiber-reinforced  
- **glass**: borosilicate
- **metal**: ferrous, non-ferrous, reactive
- **organic**: grass, hardwood, softwood
- **polymer**: thermoplastic, thermoset
- **stone**: architectural, concrete, igneous, sedimentary

### 4. Standalone Generator Architecture

#### File Structure
```
scripts/generators/
├── categories_generator.py        # Standalone generator script
├── research_validator.py          # AI research validation module
└── categories_updater.py          # Database refresh utility

data/
├── Categories.yaml               # Generated database (output)
└── Materials.yaml               # Source data (input)

schemas/
└── categories_schema.json       # Validation schema
```

#### Usage Pattern
```bash
# Generate initial Categories.yaml
python3 scripts/generators/categories_generator.py --generate

# Refresh with latest research
python3 scripts/generators/categories_generator.py --refresh

# Validate existing Categories.yaml
python3 scripts/generators/categories_generator.py --validate
```

#### No Integration Dependencies
- **Standalone Operation**: Runs independently of main generation system
- **File-Based Output**: Produces Categories.yaml for other tools to reference
- **Self-Contained Research**: Uses AI APIs directly for property validation
- **Optional Usage**: Other components can use Categories.yaml if available, but don't require it

### 5. Fail-Fast Architecture Compliance
- **No Fallbacks**: Fail immediately if research sources are unavailable
- **Explicit Dependencies**: Require validated research data for all properties
- **Configuration Validation**: Verify Categories.yaml structure on startup
- **Error Handling**: Use specific exception types (CategoryResearchError, SubcategoryValidationError)

## Implementation Steps

### Phase 1: Standalone Generator Setup
1. Create standalone script in `scripts/generators/`
2. Parse `data/Materials.yaml` to extract categories/subcategories
3. Set up AI research pipeline using existing API infrastructure

### Phase 2: AI Research & Validation
1. Use AI to research property ranges for each category/subcategory
2. Validate findings against multiple sources
3. Assign confidence scores based on research quality

### Phase 3: Database Generation
1. Generate Categories.yaml with researched data
2. Validate against schema
3. Include metadata and research provenance

### Phase 4: Refresh Mechanism
1. Create update utility for periodic refreshes
2. Track changes and improvements over time
3. Maintain version history

## Quality Assurance

### Data Validation Rules
- All ranges must have scientific justification
- Min/max values must reflect real-world material boundaries
- Confidence scores must be based on source quality
- Units must be consistent and properly specified

### Testing Requirements
- Unit tests for all property lookups
- Integration tests with frontmatter generation
- Validation against known material databases
- Performance tests for large-scale generation

## Benefits

### For Frontmatter Generation
- **Accuracy**: Property values within realistic ranges for each material type
- **Consistency**: Uniform property definitions within categories
- **Completeness**: Comprehensive coverage of all required DataMetric fields
- **Scientific Validity**: Research-backed property ranges

### For System Architecture
- **Maintainability**: Centralized property database
- **Scalability**: Easy addition of new categories/subcategories
- **Quality Control**: Systematic validation of all property data
- **Documentation**: Clear provenance for all property values

## Your Original Instructions - Analysis

Your proposed instructions are **conceptually sound** but need enhancement:

### ✅ Strong Points:
1. "Research data for category and subcategory-specific values" - Good focus on both levels
2. "From Materials.yaml, collect all fields applicable to categories" - Leverages existing data
3. "Database will be used to populate material frontmatter fields" - Clear purpose
4. "Categories.yaml" - Good naming convention

### 📋 Areas for Enhancement:
1. **Scope Definition**: Specify which properties need research (all DataMetric fields)
2. **Research Methodology**: How will data be validated and sourced?
3. **Integration Strategy**: How does this connect to existing frontmatter generation?
4. **Quality Standards**: What confidence levels and validation criteria?
5. **Architecture Compliance**: How does this follow fail-fast principles?

### 🎯 Recommended Final Instructions:
"Create a standalone Categories.yaml generator that researches and validates material property ranges by category and subcategory using AI, extracting category/subcategory combinations from Materials.yaml, implementing comprehensive research validation with confidence scoring, and generating a reference database that can be refreshed periodically for the latest scientific data."

This approach provides:
- ✅ **Standalone Operation**: No integration dependencies
- ✅ **AI-Powered Research**: Uses existing API infrastructure for validation
- ✅ **Periodic Refresh**: Can be run occasionally to update data
- ✅ **Scientific Validation**: Ensures accuracy through AI research
- ✅ **Reference Database**: Other tools can optionally use Categories.yaml