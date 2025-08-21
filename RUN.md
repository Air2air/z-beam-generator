# Test API connection
python3 z_beam_generator.py --test-api

# Generate content for a specific material
python3 z_beam_generator.py --material "Steel" --components "caption"

# Generate all components for a material
python3 z_beam_generator.py --material "Aluminum" --all

# List available materials
python3 z_beam_generator.py --list-materials

# See all options
python3 z_beam_generator.py --help