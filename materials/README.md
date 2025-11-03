# Materials Content Type

Material frontmatter generation for laser cleaning applications.

## Structure

- `generator.py` - MaterialFrontmatterGenerator class
- `data.yaml` - 132 material definitions with properties
- `output/` - Generated frontmatter files

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
