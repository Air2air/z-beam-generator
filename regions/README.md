# Regions Content Type

Geographic and regulatory frontmatter generation for laser cleaning markets.

## Structure

- `generator.py` - RegionFrontmatterGenerator class
- `data.yaml` - 6 region definitions
- `output/` - Generated frontmatter files

## Usage

```bash
# Generate region frontmatter
python3 run.py --content-type region --identifier "north_america"
python3 run.py --content-type region --identifier "europe"
```

## Data Structure

Each region in `data.yaml` includes:
- Countries covered
- Market size and growth rate
- Regulatory framework
- Common applications
- Key agencies

## Available Regions

- `north_america` - USA, Canada, Mexico
- `europe` - EU member states
- `asia_pacific` - China, Japan, South Korea, etc.
- `middle_east` - UAE, Saudi Arabia, etc.
- `latin_america` - Brazil, Argentina, Chile, etc.
- `africa` - South Africa, Nigeria, etc.
