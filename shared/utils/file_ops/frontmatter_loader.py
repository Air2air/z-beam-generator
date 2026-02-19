#!/usr/bin/env python3
"""
Frontmatter Loader

Utility for loading and parsing frontmatter data from saved files.
"""

import logging
from pathlib import Path
from typing import Dict

import yaml

logger = logging.getLogger(__name__)

def load_frontmatter_data(material_name: str) -> Dict:
    """
    Load frontmatter data from saved file for dependent components.
    
    Args:
        material_name: Name of the material
        
    Returns:
        Dictionary containing parsed frontmatter data

    Raises:
        FileNotFoundError: If frontmatter file does not exist
        ValueError: If frontmatter content is empty or invalid
        RuntimeError: If YAML parsing fails
    """
    # Create safe filename from material name
    safe_material = material_name.lower().replace(" ", "-").replace("/", "-")

    # Canonical frontmatter system (YAML format)
    yaml_filename = f"{safe_material}.yaml"
    frontmatter_dir = Path("frontmatter") / "materials"
    yaml_filepath = frontmatter_dir / yaml_filename

    if not yaml_filepath.exists():
        raise FileNotFoundError(f"Frontmatter file not found for {material_name}: {yaml_filepath}")

    try:
        with open(yaml_filepath, "r", encoding="utf-8") as f:
            frontmatter_data = yaml.safe_load(f)

        if frontmatter_data is None:
            raise ValueError(f"Frontmatter file is empty: {yaml_filepath}")
        if not isinstance(frontmatter_data, dict):
            raise ValueError(f"Frontmatter YAML root must be a dictionary: {yaml_filepath}")

        logger.info(f"Successfully loaded frontmatter data for {material_name} (YAML)")
        return frontmatter_data
    except yaml.YAMLError as e:
        raise RuntimeError(f"Failed to parse frontmatter YAML for {material_name}: {e}") from e
