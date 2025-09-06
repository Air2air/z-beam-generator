#!/usr/bin/env python3
"""
Mock Table Component Generator for Testing
"""

from typing import Any, Dict, Optional

from utils.component_base import ComponentResult


class MockTableComponentGenerator:
    """Mock generator for table component testing."""

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
        """Generate mock table component content."""
        self.call_count += 1

        mock_content = f"""| Property | Value | Unit |
|----------|-------|------|
| Material | {material_name} | - |
| Thermal Conductivity | 50-400 | W/m·K |
| Melting Point | 100-2500 | °C |
| Surface Reflectivity | 4-95 | % |"""

        return ComponentResult(
            component_type="table",
            content=mock_content,
            success=True,
        )
