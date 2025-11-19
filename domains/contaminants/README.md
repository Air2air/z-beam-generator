# Contaminants Content Type

Contaminant removal frontmatter for laser cleaning applications.

## Structure

- `generator.py` - ContaminantFrontmatterGenerator class
- `data.yaml` - 8 contaminant type definitions
- `output/` - Generated frontmatter files

## Usage

```bash
# Generate contaminant frontmatter
python3 run.py --content-type contaminant --identifier "rust"
python3 run.py --content-type contaminant --identifier "paint"
```

## Data Structure

Each contaminant in `data.yaml` includes:
- Description and types
- Compatible materials
- Removal guidelines
- Laser parameters
- Safety considerations

## Available Contaminants

- `rust` - Iron oxide corrosion
- `paint` - Coatings and finishes
- `oil_grease` - Hydrocarbon residues
- `scale` - Mineral deposits
- `carbon_deposits` - Carbonaceous buildup
- `adhesives` - Bonding agents
- `biological_growth` - Organic contamination
- `oxidation` - Surface degradation
