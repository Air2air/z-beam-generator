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

Each material in `data.yaml` includes:
- Properties (thermal, optical, mechanical)
- Category classification
- Laser parameters and guidelines
- Safety requirements
- Applications and use cases

## Dependencies

Inherits from `components/frontmatter/core/base_generator.py` and uses shared infrastructure from:
- `shared/voice/` - Author voice processing
- `shared/validation/` - Schema validation
- `shared/api/` - AI client management
- `components/frontmatter/research/` - Property research tools
