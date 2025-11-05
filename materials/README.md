# Materials Content Type

Material frontmatter generation for laser cleaning applications.

## Architecture Overview

The materials module has TWO generation systems:

### 1. **Frontmatter Generation** (`generator.py`)
- **Purpose**: Complete material frontmatter generation
- **Entry Point**: MaterialFrontmatterGenerator class
- **Used By**: components/frontmatter/core/orchestrator.py
- **Function**: Wraps StreamlinedFrontmatterGenerator, generates full YAML files
- **Size**: 246 lines

### 2. **Text Content Generation** (Dual System)

**A. NEW System** (`unified_generator.py` - 391 lines)
- **Purpose**: Caption, FAQ, and Subtitle generation
- **Used By**: shared/commands/generation.py (--caption, --subtitle, --faq flags)
- **Approach**: Single generator with prompt templates
- **Status**: ✅ Active, modern approach

**B. OLD System** (Component generators in subdirectories)
- **Caption**: `caption/generators/generator.py` (388 lines)
- **Subtitle**: `subtitle/core/subtitle_generator.py` (333 lines)
- **FAQ**: `faq/generators/faq_generator.py` (493 lines)
- **Used By**: Tests, ComponentGeneratorFactory, batch scripts
- **Status**: ⚠️ Legacy, maintained for backward compatibility

## Structure

- `generator.py` - Main frontmatter generator (orchestrator entry point)
- `unified_generator.py` - Text content generator (caption/FAQ/subtitle)
- `data/materials.yaml` - 132 material definitions with properties
- `caption/`, `subtitle/`, `faq/` - Legacy component generators
- `modules/` - 6 active modules for frontmatter assembly
- `services/` - Property management and validation
- `research/` - AI-powered property research tools
- `utils/` - Property taxonomy and helpers
- `validation/` - Completeness validator

## Usage

```bash
# Generate material frontmatter
python3 run.py --content-type material --identifier "Aluminum"
python3 run.py --material "Steel"  # Shortcut flag

# Data-only mode (no AI)
python3 run.py --material "Copper" --data-only
```

## Data Structure

Each material in `data.yaml` follows the GROUPED structure defined in `data/frontmatter_template.yaml`:

### Core Fields
- **Identification**: name, category, subcategory, title, subtitle
- **Content**: author, caption
- **Assets**: images (hero, micro)
- **Standards**: regulatoryStandards
- **FAQ**: Frequently asked questions

### Material Properties (GROUPED Structure)

Properties are organized into two category groups:

**1. material_characteristics**
- Physical properties: density, porosity, crystalline structure
- Mechanical properties: hardness, tensile strength, elasticity
- Chemical properties: composition, reactivity
- Surface properties: roughness, finish

**2. laser_material_interaction**  
- Thermal properties: thermal conductivity, melting point
- Optical properties: reflectivity, absorption coefficient
- Laser-specific: ablation threshold, heat-affected zone depth

Each group contains:
```yaml
materialProperties:
  material_characteristics:
    label: "Material Characteristics"
    description: "Physical, mechanical, and chemical properties"
    properties:
      density: { value: "2.7", unit: "g/cm³", range: {...} }
  laser_material_interaction:
    label: "Laser-Material Interaction"  
    description: "Thermal and optical properties"
    properties:
      thermalConductivity: { value: "205", unit: "W/m·K", range: {...} }
```

### Machine Settings
- Recommended laser parameters per application
- Power, speed, frequency ranges
- Safety considerations

## Dependencies

Inherits from `components/frontmatter/core/base_generator.py` and uses shared infrastructure from:
- `shared/voice/` - Author voice processing
- `shared/validation/` - Schema validation
- `shared/api/` - AI client management
- `components/frontmatter/research/` - Property research tools
