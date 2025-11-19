# Thesaurus Content Type

Technical terminology and knowledge base for laser cleaning concepts.

## Structure

- `generator.py` - ThesaurusFrontmatterGenerator class
- `data.yaml` - 15 technical term definitions
- `output/` - Generated frontmatter files

## Usage

```bash
# Generate term definition frontmatter
python3 run.py --content-type thesaurus --identifier "ablation"
python3 run.py --content-type thesaurus --identifier "fluence"
```

## Data Structure

Each term in `data.yaml` includes:
- Term name
- Definition
- Category
- Related terms
- Technical details
- Applications

## Available Terms

- `ablation` - Material removal process
- `fluence` - Energy density
- `pulse_duration` - Temporal characteristics
- `wavelength` - Spectral characteristics
- `beam_quality` - Spatial beam properties
- `repetition_rate` - Pulse frequency
- `average_power` - Energy delivery
- `peak_power` - Maximum intensity
- `spot_size` - Beam diameter
- `depth_of_focus` - Focal range
- `threshold_fluence` - Minimum ablation energy
- `heat_affected_zone` - Thermal influence
- `plasma_plume` - Ionized ejection
- `selective_absorption` - Wavelength-dependent removal
- `surface_roughness` - Finish quality
