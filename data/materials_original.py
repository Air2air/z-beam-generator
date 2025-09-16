"""
Materials data loader for Z-Beam generator.
"""

from pathlib import Path

import yaml


def load_materials():
    """Load materials data from YAML file."""
    materials_file = Path(__file__).parent / "materials.yaml"

    try:
        with open(materials_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        # Return the complete structure, not just the materials section
        # This makes it compatible with both DynamicGenerator and other components
        return data
    except Exception as e:
        print(f"Error loading materials data: {e}")
        return {"materials": {}}  # Return an empty but valid structure
