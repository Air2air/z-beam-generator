#!/usr/bin/env python3
"""
Material data utility functions.

This module provides utilities to extract material data for specific materials.
"""

import logging
from typing import Dict, List, Optional


def find_material_data(materials_data: Dict, material_name: str) -> Optional[Dict]:
    """
    Find material data for a specific material by name.
    
    Args:
        materials_data: The loaded materials data dictionary
        material_name: Name of the material to find
        
    Returns:
        Material data dictionary or None if not found
    """
    if not materials_data or "materials" not in materials_data:
        logging.warning(f"No materials data available or incorrect format")
        return None

    material_data = None
    materials_section = materials_data["materials"]
    
    # Case-insensitive search first
    for category, category_data in materials_section.items():
        if isinstance(category_data, dict) and "items" in category_data:
            for item in category_data["items"]:
                if "name" in item and item["name"].lower() == material_name.lower():
                    logging.debug(f"Found material data for {material_name} in category {category}")
                    material_data = item
                    break
            if material_data:
                break

    # If not found, try exact match for backward compatibility
    if not material_data:
        for category, category_data in materials_section.items():
            if isinstance(category_data, dict) and "items" in category_data:
                for item in category_data["items"]:
                    if "name" in item and item["name"] == material_name:
                        logging.debug(f"Found material data with exact match for {material_name} in category {category}")
                        material_data = item
                        break
                if material_data:
                    break

    if not material_data:
        logging.warning(f"Material '{material_name}' not found in any category")
    
    return material_data


def extract_author_id_from_material_data(material_data: Dict) -> Optional[int]:
    """
    Extract author ID from material data.
    
    Args:
        material_data: Material data dictionary
        
    Returns:
        Author ID or None if not found
    """
    if not material_data:
        return None
        
    # Check for author_id directly in material data
    if "author_id" in material_data:
        author_id = material_data["author_id"]
        logging.info(f"Extracted author_id {author_id} from material data")
        return author_id
    
    # Check for author_id in nested data structure
    if "data" in material_data and "author_id" in material_data["data"]:
        author_id = material_data["data"]["author_id"]
        logging.info(f"Extracted author_id {author_id} from nested data")
        return author_id
    
    logging.warning("No author_id found in material data")
    return None
