"""
Materials data loader for Z-Beam generator.
"""

import yaml
from pathlib import Path


def load_materials():
    """Load materials data from YAML file."""
    materials_file = Path(__file__).parent / "materials.yaml"
    
    try:
        with open(materials_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data.get('materials', {})  # Return the materials section
    except Exception as e:
        print(f"Error loading materials data: {e}")
        return {}
