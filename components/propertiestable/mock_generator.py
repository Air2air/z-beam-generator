#!/usr/bin/env python3
"""
Mock Properties Table Component Generator for Testing
"""

from typing import Any, Dict, Optional

from utils.component_base import ComponentResult


class MockPropertiesTableComponentGenerator:
    """Mock generator for properties table component testing."""

    def __init__(self):
        self.call_count = 0

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate mock properties table component content."""
        self.call_count += 1

        mock_content = f"""Thermal Conductivity|50-400|W/m·K|Material-dependent heat transfer rate
Melting Point|100-2500|°C|Temperature threshold for material damage
Surface Reflectivity|4-95|%|Laser energy absorption efficiency
Optimal Wavelength|532-1064|nm|Laser wavelength for best cleaning efficiency
Pulse Energy|0.3-5.0|mJ|Energy delivered per laser pulse
Material|{material_name}|-|Test material for laser cleaning"""

        return ComponentResult(
            component_type="propertiestable",
            content=mock_content,
            success=True,
        )
