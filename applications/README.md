# Applications Content Type

Industry-specific use case frontmatter for laser cleaning applications.

## Structure

- `generator.py` - ApplicationFrontmatterGenerator class
- `data.yaml` - 12 application definitions
- `output/` - Generated frontmatter files

## Usage

```bash
# Generate application frontmatter
python3 run.py --content-type application --identifier "automotive_manufacturing"
python3 run.py --content-type application --identifier "aerospace_maintenance"
```

## Data Structure

Each application in `data.yaml` includes:
- Use cases
- Common materials processed
- Common contaminants removed
- Process requirements
- Benefits and challenges

## Available Applications

- `automotive_manufacturing`
- `aerospace_maintenance`
- `marine_hull_cleaning`
- `industrial_equipment_maintenance`
- `semiconductor_manufacturing`
- `medical_device_cleaning`
- `cultural_heritage_restoration`
- `food_processing_equipment`
- `power_generation`
- `railroad_maintenance`
- `construction_equipment`
- `electronics_manufacturing`
