"""
Data Finder Module

Utilities for finding material data and other content-related data
from the project's data sources.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def find_material_data(material_name: str, materials_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Find material data from the materials database."""
    try:
        # Normalize the search material name
        search_name = material_name.lower().replace(" ", "-").replace("_", "-")
        
        for category_data in materials_data.values():
            for item in category_data.get("items", []):
                if "name" in item:
                    # Normalize the item name for comparison
                    item_name = item["name"].lower().replace(" ", "-").replace("_", "-")
                    if item_name == search_name:
                        logger.info(f"Found material data for {material_name}: {item['name']}")
                        return item
        
        logger.warning(f"Material data not found for {material_name} (searched for: {search_name})")
        # Debug: show available materials
        all_materials = []
        for category_data in materials_data.values():
            for item in category_data.get("items", []):
                if "name" in item:
                    all_materials.append(item["name"])
        logger.debug(f"Available materials: {', '.join(all_materials[:5])}{'...' if len(all_materials) > 5 else ''}")
        
    except Exception as e:
        logger.error(f"Error finding material data for {material_name}: {e}")

    return None
