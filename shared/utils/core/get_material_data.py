"""
Helper functions for getting material data and extracting author information
"""

from typing import Dict, Optional, Any


def get_material_data_from_materials(materials_data, material_name: str) -> Optional[Dict]:
    """Get material data for a specific material name"""
    try:
        if not materials_data or "materials" not in materials_data:
            print(f"⚠️ No materials data available or incorrect format")
            return None

        material_data = None
        materials_section = materials_data["materials"]
        for category, category_data in materials_section.items():
            if isinstance(category_data, dict) and "items" in category_data:
                for item in category_data["items"]:
                    if "name" in item and item["name"].lower() == material_name.lower():
                        material_data = item
                        print(f"✅ Found material data for {material_name} in category {category}")
                        break
                if material_data:
                    break

        if not material_data:
            # Try once more with an exact match for compatibility with old tests
            for category, category_data in materials_section.items():
                if isinstance(category_data, dict) and "items" in category_data:
                    for item in category_data["items"]:
                        if "name" in item and item["name"] == material_name:
                            material_data = item
                            print(f"✅ Found material data with exact match for {material_name} in category {category}")
                            break
                    if material_data:
                        break

        if not material_data:
            print(f"⚠️ Material '{material_name}' not found in any category")
            
        return material_data
    except Exception as e:
        print(f"⚠️ Error retrieving material data for {material_name}: {e}")
        return None
