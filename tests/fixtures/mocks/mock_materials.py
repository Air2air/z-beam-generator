#!/usr/bin/env python3
"""
Mock materials data for testing.

This module provides mock materials data for tests to avoid dependency on real data files.
"""


def mock_load_materials():
    """Mock implementation that returns test materials data."""
    return {
        "materials": {
            "metal": {
                "items": [
                    {"name": "Steel", "formula": "Fe", "symbol": "Fe"},
                    {"name": "Aluminum", "formula": "Al", "symbol": "Al"},
                    {"name": "Copper", "formula": "Cu", "symbol": "Cu"},
                    {"name": "Titanium", "formula": "Ti", "symbol": "Ti"}
                ]
            },
            "ceramic": {
                "items": [
                    {"name": "Alumina", "formula": "Al2O3", "symbol": "Al2O3"}
                ]
            },
            "composite": {
                "items": [
                    {"name": "Carbon Fiber Reinforced Polymer", "symbol": "CFRP"}
                ]
            },
            "glass": {
                "items": [
                    {"name": "Borosilicate Glass", "formula": "B2O3-SiO2"}
                ]
            }
        }
    }


def get_mock_materials_list():
    """Get a list of all mock material names."""
    materials_data = mock_load_materials()
    material_names = []

    for category, category_data in materials_data["materials"].items():
        for item in category_data["items"]:
            material_names.append(item["name"])

    return material_names
