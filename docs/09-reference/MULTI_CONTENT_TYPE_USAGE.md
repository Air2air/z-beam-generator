# Multi-Content Type Usage Guide

**System Status**: ✅ All 5 Content Types Fully Functional  
**Date**: October 30, 2025  
**Architecture**: Phase 1 Multi-Content Type Complete

---

## Overview

The Z-Beam Generator supports **5 equal-weight content types**, each with discrete generators, data files, and output directories:

1. **Material** - Production-ready (132 materials, 93.5% data complete)
2. **Contaminant** - Data-driven (8 contaminant types)
3. **Region** - Data-driven (6 global regions)
4. **Application** - Data-driven (12 industrial applications)
5. **Thesaurus** - Data-driven (15 technical terms)

All generators read from YAML data files and produce structured frontmatter with author voice integration.

---

## Quick Start

### Basic Usage Pattern

```bash
python3 run.py --content-type <TYPE> --identifier "<NAME>"
```

### Examples

```bash
# Generate material frontmatter (production data)
python3 run.py --content-type material --identifier "Aluminum"
python3 run.py --content-type material --identifier "Steel"

# Generate contaminant frontmatter (data-driven)
python3 run.py --content-type contaminant --identifier "rust"
python3 run.py --content-type contaminant --identifier "paint"

# Generate region frontmatter (data-driven)
python3 run.py --content-type region --identifier "north_america"
python3 run.py --content-type region --identifier "europe"

# Generate application frontmatter (data-driven)
python3 run.py --content-type application --identifier "automotive_manufacturing"
python3 run.py --content-type application --identifier "aerospace_maintenance"

# Generate thesaurus frontmatter (data-driven)
python3 run.py --content-type thesaurus --identifier "ablation"
python3 run.py --content-type thesaurus --identifier "fluence"
```

---

## Content Type Details

### 1. Material (Production)

**Status**: ✅ Production-ready  
**Data Source**: `data/Materials.yaml`  
**Generator**: `MaterialFrontmatterGenerator` (wrapper around `StreamlinedFrontmatterGenerator`)  
**Output**: `frontmatter/{material}-laser-cleaning.yaml`

**Available Materials**: 132 (Aluminum, Steel, Copper, Glass, etc.)

**Example**:
```bash
python3 run.py --content-type material --identifier "Aluminum"
# OR use legacy command:
python3 run.py --material "Aluminum"
```

**Output Structure**:
- Complete material properties with ranges
- Machine settings (laser parameters)
- Applications and industry tags
- Regulatory standards
- Environmental impact
- FAQ, caption, subtitle (generated)
- Author voice integration

---

### 2. Contaminant (Data-Driven)

**Status**: ✅ Fully functional  
**Data Source**: `data/contaminants.yaml`  
**Generator**: `ContaminantFrontmatterGenerator`  
**Output**: `frontmatter/contaminants/{contaminant}-laser-cleaning.yaml`

**Available Contaminants**: 8
- `rust` - Iron oxide corrosion products
- `paint` - Coatings and paint layers
- `oxide_layer` - Metal oxide films
- `grease` - Oils and lubricants
- `biological_growth` - Mold, algae, bacteria
- `carbon_deposits` - Carbon buildup
- `mineral_deposits` - Scale and mineral formations
- `adhesive_residue` - Glue and adhesive remnants

**Example**:
```bash
python3 run.py --content-type contaminant --identifier "rust"
```

**Output Structure**:
- Contaminant description and properties
- Chemical composition (if available)
- Common substrates
- Laser parameters (placeholder + research needed)
- Applications
- Removal difficulty rating

---

### 3. Region (Data-Driven)

**Status**: ✅ Fully functional  
**Data Source**: `data/regions.yaml`  
**Generator**: `RegionFrontmatterGenerator`  
**Output**: `frontmatter/regions/{region}-laser-cleaning.yaml`

**Available Regions**: 6
- `north_america` - USA, Canada, Mexico
- `europe` - EU member states + UK
- `asia_pacific` - China, Japan, Korea, Southeast Asia
- `middle_east` - Gulf states + MENA region
- `south_america` - Brazil, Argentina, Chile, etc.
- `africa` - Sub-Saharan + North Africa

**Example**:
```bash
python3 run.py --content-type region --identifier "north_america"
```

**Output Structure**:
- Region name and countries
- Market characteristics (size, growth rate, maturity)
- Regulatory framework (agencies, standards)
- Common applications by region
- Key industries
- Primary language

---

### 4. Application (Data-Driven)

**Status**: ✅ Fully functional  
**Data Source**: `data/applications.yaml`  
**Generator**: `ApplicationFrontmatterGenerator`  
**Output**: `frontmatter/applications/{application}-laser-cleaning.yaml`

**Available Applications**: 12
- `automotive_manufacturing` - Vehicle production
- `aerospace_maintenance` - Aircraft cleaning/repair
- `historical_restoration` - Cultural heritage
- `marine_maintenance` - Ship/vessel cleaning
- `electronics_manufacturing` - PCB/component prep
- `oil_gas_industry` - Pipeline/equipment maintenance
- `medical_device_cleaning` - Healthcare equipment
- `mold_cleaning` - Injection mold maintenance
- `nuclear_decontamination` - Nuclear facility cleaning
- `solar_panel_maintenance` - PV panel cleaning
- `shipbuilding` - Shipyard operations
- `rail_transport` - Train/rail maintenance

**Example**:
```bash
python3 run.py --content-type application --identifier "automotive_manufacturing"
```

**Output Structure**:
- Application name and industry sector
- Use cases (6-8 specific scenarios)
- Common materials cleaned
- Common contaminants removed
- Process requirements (automation, throughput, precision)
- Benefits (efficiency, quality, cost)
- Challenges and considerations
- Typical laser parameters

---

### 5. Thesaurus (Data-Driven)

**Status**: ✅ Fully functional  
**Data Source**: `data/thesaurus.yaml`  
**Generator**: `ThesaurusFrontmatterGenerator`  
**Output**: `frontmatter/thesaurus/{term}-laser-cleaning.yaml`

**Available Terms**: 15
- `ablation` - Material removal process
- `fluence` - Energy per unit area
- `pulse_width` - Duration of laser pulse
- `repetition_rate` - Pulse frequency
- `wavelength` - Laser light wavelength
- `spot_size` - Beam diameter
- `heat_affected_zone` - Thermal damage area
- `q_switching` - Pulse generation technique
- `scanning_speed` - Beam travel rate
- `line_overlap` - Pass overlap percentage
- `ablation_threshold` - Minimum energy threshold
- `selectivity` - Material preference
- `beam_quality` - Beam profile metric
- `plume` - Ablated material cloud
- `pulse_overlap` - Pulse spacing metric

**Example**:
```bash
python3 run.py --content-type thesaurus --identifier "ablation"
```

**Output Structure**:
- Term and definition
- Category (process, parameter, characteristic)
- Synonyms and related terms
- Technical details (mechanism, units, ranges)
- Applications
- Usage context

---

## Output Locations

All generated frontmatter files follow a consistent naming pattern:

```
frontmatter/
├── {material}-laser-cleaning.yaml              # Materials (root)
├── contaminants/
│   └── {contaminant}-laser-cleaning.yaml
├── regions/
│   └── {region}-laser-cleaning.yaml
├── applications/
│   └── {application}-laser-cleaning.yaml
└── thesaurus/
    └── {term}-laser-cleaning.yaml
```

---

## Architecture Features

### 1. Equal-Weight Content Types
All 5 content types have:
- Discrete generator classes
- Dedicated YAML data files
- Separate output directories
- Author voice integration
- Validation and error handling

### 2. Data-Driven Generation
Non-material types use **data files as source of truth**:
- Properties, specifications, and metadata from YAML
- Placeholder laser parameters (marked for research)
- Structured frontmatter output
- Extensible schema

### 3. Author Voice Integration
All generators support author voice processing:
- Country-specific linguistic patterns
- Writing style adaptation
- Voice metadata in output

### 4. Fail-Fast Validation
- Validates content type support
- Validates identifier exists in data file
- Clear error messages with available options
- No silent failures or fallbacks

---

## Common Commands

### List Available Content Types
```bash
# System supports: material, contaminant, region, application, thesaurus
python3 run.py --content-type unknown --identifier "test"
# Error message shows supported types
```

### Check Available Identifiers
```bash
# Try invalid identifier to see available options
python3 run.py --content-type contaminant --identifier "invalid"
# Error: "Contaminant 'invalid' not found. Available: rust, paint, oxide_layer, ..."
```

### Data-Only Mode (No API)
```bash
# Generate without API calls (uses data files only)
python3 run.py --content-type contaminant --identifier "rust" --data-only
```

---

## Extending the System

### Adding New Content Types
1. Create data file: `data/{type}.yaml`
2. Create generator: `components/frontmatter/types/{type}/generator.py`
3. Extend `BaseFrontmatterGenerator`
4. Implement required methods:
   - `_load_type_data()`
   - `_validate_identifier()`
   - `_build_frontmatter_data()`
   - `_get_schema_name()`
   - `_get_output_filename()`
5. Register with `FrontmatterOrchestrator`

### Adding New Identifiers
Edit the appropriate data file:
- `data/Materials.yaml` - Add material
- `data/contaminants.yaml` - Add contaminant type
- `data/regions.yaml` - Add region
- `data/applications.yaml` - Add application
- `data/thesaurus.yaml` - Add term

---

## Data File Locations

```
data/
├── Materials.yaml      # 132 materials (48,120 lines)
├── contaminants.yaml   # 8 types (400+ lines)
├── regions.yaml        # 6 regions (300+ lines)
├── applications.yaml   # 12 applications (600+ lines)
└── thesaurus.yaml      # 15 terms (400+ lines)
```

---

## Status Summary

| Content Type | Status | Data Source | Count | Output Quality |
|--------------|--------|-------------|-------|----------------|
| Material | ✅ Production | `Materials.yaml` | 132 | Complete (93.5% data) |
| Contaminant | ✅ Data-Driven | `contaminants.yaml` | 8 | Structured placeholder |
| Region | ✅ Data-Driven | `regions.yaml` | 6 | Structured placeholder |
| Application | ✅ Data-Driven | `applications.yaml` | 12 | Structured placeholder |
| Thesaurus | ✅ Data-Driven | `thesaurus.yaml` | 15 | Structured placeholder |

**Total Available Content**: 173 discrete content items across 5 types

---

## Future Enhancements

### Phase 2 (Content Research)
- AI-powered research for non-material types
- Property discovery and validation
- Range calculation and verification
- Completeness scoring

### Phase 3 (Component Generation)
- FAQ generation for all content types
- Caption and subtitle generation
- Related content linking
- Cross-reference validation

---

## Troubleshooting

### Issue: "Content type not supported"
**Solution**: Check spelling and use lowercase: `material`, `contaminant`, `region`, `application`, `thesaurus`

### Issue: "Identifier not found"
**Solution**: Check available identifiers in data file or use invalid identifier to see list

### Issue: "Generator failed"
**Solution**: Check data file exists and is valid YAML format

### Issue: Output file not created
**Solution**: Check write permissions in `frontmatter/` directory

---

## Additional Resources

- **Architecture**: `docs/architecture/PHASE1_IMPLEMENTATION_COMPLETE.md`
- **Data Files**: `data/` directory
- **Generators**: `components/frontmatter/types/` directory
- **Orchestrator**: `components/frontmatter/core/orchestrator.py`

---

**System Version**: 2.0.0  
**Last Updated**: October 30, 2025  
**Status**: ✅ All 5 Content Types Fully Functional
