#!/usr/bin/env python3
"""
Table Component Generator

Generates technical tables for laser cleaning applications.
Uses consolidated component base utilities for reduced code duplication.
"""

import random
from pathlib import Path
from typing import Any, Dict, Optional

from generators.component_generators import APIComponentGenerator
from utils.core.component_base import (
    ComponentResult,
    handle_generation_error,
    validate_required_fields,
)


class TableComponentGenerator(APIComponentGenerator):
    """Generator for table components using material data"""

    def __init__(self):
        super().__init__("table")
        self.prompt_file = Path(__file__).parent / "prompt.yaml"

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate table component content"""
        try:
            # Validate required data
            if not material_name:
                return self.create_error_result("Material name is required")

            # Generate table content
            content = self._create_table_content(material_name, material_data)

            return ComponentResult(
                component_type="table", content=content, success=True
            )

        except Exception as e:
            return handle_generation_error("table", e, "content generation")

    def _create_table_content(self, material_name: str, material_data: Dict) -> str:
        """Create table content with multiple technical tables"""
        tables = []

        # Generate 5 different tables
        tables.append(self._create_material_properties_table(material_name))
        tables.append(self._create_grades_table(material_name))
        tables.append(self._create_performance_table(material_name))
        tables.append(self._create_standards_table())
        tables.append(self._create_laser_parameters_table())

        return "\n\n".join(tables)

    def _create_material_properties_table(self, material_name: str) -> str:
        """Create material properties table"""
        properties = [
            ("Atomic Number", "29", "-"),
            ("Density", "8.96", "g/cm³"),
            ("Melting Point", "1085", "°C"),
            ("Boiling Point", "2562", "°C"),
            ("Thermal Conductivity", "401", "W/(m·K)"),
            ("Electrical Conductivity", "5.96×10⁷", "S/m"),
            ("Tensile Strength", "210-350", "MPa"),
            ("Young's Modulus", "110-128", "GPa"),
        ]

        # Randomly select 5-7 properties
        selected_props = random.sample(properties, random.randint(5, 7))

        table = "## Material Properties\n"
        table += "| Property | Value | Unit |\n"
        table += "| --- | --- | --- |\n"

        for prop, value, unit in selected_props:
            table += f"| {prop} | {value} | {unit} |\n"

        return table

    def _create_grades_table(self, material_name: str) -> str:
        """Create material grades table"""
        grades = [
            ("C10100 (OFHC)", "≥99.99", "O₂ ≤ 0.0005"),
            ("C11000 (ETP)", "≥99.90", "O₂ ≤ 0.04"),
            ("C12200 (Phosphorized)", "≥99.90", "P 0.015-0.040"),
            ("C19400 (Alloy)", "97.0-98.5", "Fe 2.1-2.6"),
        ]

        # Randomly select 3-4 grades
        selected_grades = random.sample(grades, random.randint(3, 4))

        table = "## Material Grades and Purity\n"
        table += "| Grade | Purity (%) | Common Impurities |\n"
        table += "| --- | --- | --- |\n"

        for grade, purity, impurities in selected_grades:
            table += f"| {grade} | {purity} | {impurities} |\n"

        return table

    def _create_performance_table(self, material_name: str) -> str:
        """Create performance metrics table"""
        metrics = [
            ("Corrosion Rate (Seawater)", "0.05-0.2", "mm/year (25°C)"),
            ("Fatigue Strength", "70-100", "MPa (10⁷ cycles)"),
            ("Hardness (Brinell)", "35-150", "HB (annealed)"),
            ("Reflectivity (IR)", "≥98%", "λ = 1064nm"),
            ("Surface Roughness (Ra)", "0.1-0.5", "µm"),
            ("Thermal Expansion", "16.5", "µm/(m·K)"),
        ]

        # Randomly select 4-5 metrics
        selected_metrics = random.sample(metrics, random.randint(4, 5))

        table = "## Performance Metrics\n"
        table += "| Metric | Value | Condition |\n"
        table += "| --- | --- | --- |\n"

        for metric, value, condition in selected_metrics:
            table += f"| {metric} | {value} | {condition} |\n"

        return table

    def _create_standards_table(self) -> str:
        """Create standards and compliance table"""
        standards = [
            ("ASTM B152/B152M", "Sheet/strip/plate"),
            ("ISO 431", "High-conductivity copper"),
            ("EN 1172", "Copper for roofing"),
            ("IEC 60028", "International resistivity std"),
            ("ASTM B170", "Oxygen-free copper"),
            ("JIS H3100", "Copper and copper alloys"),
        ]

        # Randomly select 4-5 standards
        selected_standards = random.sample(standards, random.randint(4, 5))

        table = "## Standards and Compliance\n"
        table += "| Standard | Scope |\n"
        table += "| --- | --- |\n"

        for standard, scope in selected_standards:
            table += f"| {standard} | {scope} |\n"

        return table

    def _create_laser_parameters_table(self) -> str:
        """Create laser cleaning parameters table"""
        parameters = [
            ("Wavelength", "1064nm (primary), 532nm (optional)", "-"),
            ("Power", "20-100", "W"),
            ("Pulse Duration", "10-100", "ns"),
            ("Spot Size", "0.1-2.0", "mm"),
            ("Repetition Rate", "10-50", "kHz"),
            ("Fluence", "0.5-5", "J/cm²"),
        ]

        # Randomly select 4-5 parameters
        selected_params = random.sample(parameters, random.randint(4, 5))

        table = "## Laser Cleaning Parameters\n"
        table += "| Parameter | Range | Unit |\n"
        table += "| --- | --- | --- |\n"

        for param, range_val, unit in selected_params:
            table += f"| {param} | {range_val} | {unit} |\n"

        return table

    def create_error_result(self, error_message: str) -> ComponentResult:
        """Create a ComponentResult for error cases"""
        return ComponentResult(
            component_type="table",
            content="",
            success=False,
            error_message=error_message,
        )


# Legacy compatibility
class TableGenerator:
    """Legacy table generator for backward compatibility"""

    def __init__(self):
        self.generator = TableComponentGenerator()

    def generate(self, material: str, material_data: Dict = None) -> str:
        """Legacy generate method"""
        if material_data is None:
            material_data = {"name": material}

        result = self.generator.generate(material, material_data)

        if result.success:
            return result.content
        else:
            return f"Error generating table content: {result.error_message}"

    def get_component_info(self) -> Dict[str, Any]:
        """Get component information"""
        return {
            "name": "table",
            "description": "Technical tables component",
            "version": "1.0.0",
            "requires_api": False,
            "type": "static",
        }


def generate_table_content(material: str, material_data: Dict = None) -> str:
    """Legacy function for backward compatibility"""
    generator = TableGenerator()
    return generator.generate(material, material_data)


if __name__ == "__main__":
    # Test the generator
    generator = TableGenerator()
    test_content = generator.generate("Copper")
    print("🧪 Table Component Test:")
    print("=" * 50)
    print(test_content)
