#!/usr/bin/env python3
"""
Mock Properties Table Component Generator for Testing - Fail-Fast Architecture
"""

from typing import Any, Dict, Optional

from generators.component_generators import ComponentResult


class MockPropertiesTableComponentGenerator:
    """Mock generator for properties table component testing - follows fail-fast pattern."""

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
        """Generate mock properties table component content - FAIL FAST."""
        self.call_count += 1

        # FAIL FAST: Require frontmatter data
        if not frontmatter_data:
            return ComponentResult(
                component_type="propertiestable",
                content="",
                success=False,
                error_message="Frontmatter data is required for propertiestable generation"
            )

        # Generate deterministic mock content based on material
        mock_content = self._generate_mock_table(material_name, frontmatter_data)

        return ComponentResult(
            component_type="propertiestable",
            content=mock_content,
            success=True,
        )

    def _generate_mock_table(self, material_name: str, frontmatter_data: Dict) -> str:
        """Generate deterministic mock table content."""
        # Extract available properties from frontmatter
        properties = frontmatter_data.get("properties", {})
        chem_props = frontmatter_data.get("chemicalProperties", {})
        category = frontmatter_data.get("category", "Material")

        # Build table with available data
        table_lines = ["| Property | Value |", "|----------|-------|"]

        # Chemical formula
        formula = chem_props.get("formula", f"{material_name[:2].upper()}")
        table_lines.append(f"| Formula | {formula} |")

        # Material symbol
        symbol = chem_props.get("symbol", material_name[:3].upper())
        table_lines.append(f"| Symbol | {symbol} |")

        # Category
        table_lines.append(f"| Category | {category.title()} |")

        # Density
        density = properties.get("density", "N/A")
        if density != "N/A":
            table_lines.append(f"| Density | {density} |")

        # Thermal conductivity
        thermal = properties.get("thermalConductivity", None)
        if thermal:
            table_lines.append(f"| Thermal | {thermal} |")

        # Tensile strength
        tensile = properties.get("tensileStrength", None)
        if tensile:
            table_lines.append(f"| Tensile | {tensile} |")

        return "\n".join(table_lines)
