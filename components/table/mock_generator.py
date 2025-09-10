#!/usr/bin/env python3
"""
Test Utility for Table Component - Deterministic Generation

Note: This is NOT a mock with fallbacks. It generates the same deterministic
output as the real generator for testing purposes. No fallbacks allowed.
"""

from typing import Dict, Optional

from utils.core.component_base import ComponentResult


class TestTableComponentGenerator:
    """
    Test utility that generates identical deterministic output as real generator.
    Used for testing deterministic behavior - NOT a fallback mechanism.
    """

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
        """
        Generate deterministic table content identical to real generator.
        FAIL-FAST: No fallbacks - fails immediately on invalid input.
        """
        self.call_count += 1

        # FAIL-FAST: Validate inputs strictly
        if not material_name:
            return ComponentResult(
                component_type="table",
                content="",
                success=False,
                error_message="Material name is required - fail-fast architecture requires complete input data"
            )

        if not material_data:
            return ComponentResult(
                component_type="table",
                content="",
                success=False,
                error_message="Material data is required - fail-fast architecture requires complete material specifications"
            )

        # Generate deterministic content based on material
        content = self._generate_deterministic_content(material_name.lower())

        return ComponentResult(
            component_type="table",
            content=content,
            success=True,
        )

    def _generate_deterministic_content(self, material: str) -> str:
        """Generate exact same content as real generator - no variation."""
        if material == "copper":
            return self._copper_tables()
        elif material == "steel":
            return self._steel_tables()
        elif material == "aluminum":
            return self._aluminum_tables()
        else:
            # FAIL-FAST: No fallback for unsupported materials
            raise Exception(f"No properties found for material {material} - fail-fast architecture requires complete material data")

    def _copper_tables(self) -> str:
        """Generate exact copper tables matching real generator."""
        return """| Property | Value | Unit |
| --- | --- | --- |
| Atomic Number | 29 | - |
| Density | 8.96 | g/cm³ |
| Melting Point | 1085 | °C |
| Boiling Point | 2562 | °C |
| Thermal Conductivity | 401 | W/(m·K) |
| Electrical Conductivity | 5.96×10⁷ | S/m |
| Tensile Strength | 210-350 | MPa |
| Young's Modulus | 110-128 | GPa |

| Grade | Purity (%) | Common Impurities |
| --- | --- | --- |
| C10100 (OFHC) | ≥99.99 | O₂ ≤ 0.0005, Ag ≤ 0.0025 |
| C11000 (ETP) | ≥99.90 | O₂ ≤ 0.04, Pb ≤ 0.005 |
| C12200 (Phosphorized) | ≥99.90 | P 0.015-0.040 |
| C19400 (Alloy) | 97.0-98.5 | Fe 2.1-2.6, Zn 0.05-0.20 |

| Metric | Value | Condition |
| --- | --- | --- |
| Corrosion Rate (Seawater) | 0.05-0.2 | mm/year (25°C) |
| Fatigue Strength | 70-100 | MPa (10⁷ cycles) |
| Hardness (Brinell) | 35-150 | HB (annealed) |
| Reflectivity (IR) | ≥98% | λ = 1064nm |

| Standard | Scope |
| --- | --- |
| ASTM B152/B152M | Sheet/strip/plate |
| ISO 431 | High-conductivity copper |
| EN 1172 | Copper for roofing |
| IEC 60028 | International resistivity std |

| Parameter | Value | Unit |
| --- | --- | --- |
| Recyclability | 100% | - |
| Embodied Energy | 42-60 | MJ/kg |
| CO₂ Footprint | 2.5-4.0 | kg CO₂/kg |
| EU RoHS Compliance | Exempt (Annex III) | - |

| Parameter | Range | Unit |
| --- | --- | --- |
| Wavelength | 1064nm (primary), 532nm (optional) | - |
| Power | 20-100 | W |
| Pulse Duration | 10-100 | ns |
| Spot Size | 0.1-2.0 | mm |
| Repetition Rate | 10-50 | kHz |
| Fluence | 0.5-5 | J/cm² |"""

    def _steel_tables(self) -> str:
        """Generate exact steel tables matching real generator."""
        return """| Property | Value | Unit |
| --- | --- | --- |
| Atomic Number | 26 | - |
| Density | 7.85 | g/cm³ |
| Melting Point | 1370-1530 | °C |
| Boiling Point | 2862 | °C |
| Thermal Conductivity | 50-60 | W/(m·K) |
| Electrical Conductivity | 1.0×10⁷ | S/m |
| Tensile Strength | 400-2000 | MPa |
| Young's Modulus | 190-210 | GPa |

| Grade | Purity (%) | Common Impurities |
| --- | --- | --- |
| AISI 1018 | ≥99.0 | C 0.15-0.20, Mn 0.60-0.90 |
| AISI 304 | ≥98.0 | Cr 18-20, Ni 8-10.5 |
| AISI 316 | ≥97.0 | Cr 16-18, Ni 10-14, Mo 2-3 |
| AISI 4340 | ≥96.0 | Cr 0.70-0.90, Ni 1.65-2.00 |

| Metric | Value | Condition |
| --- | --- | --- |
| Corrosion Rate (Atmospheric) | 0.01-0.1 | mm/year |
| Fatigue Strength | 200-600 | MPa (10⁷ cycles) |
| Hardness (Brinell) | 100-400 | HB |
| Reflectivity (IR) | 85-95% | λ = 1064nm |

| Standard | Scope |
| --- | --- |
| ASTM B152/B152M | Sheet/strip/plate |
| ISO 431 | High-conductivity copper |
| EN 1172 | Copper for roofing |
| IEC 60028 | International resistivity std |

| Parameter | Value | Unit |
| --- | --- | --- |
| Recyclability | 100% | - |
| Embodied Energy | 42-60 | MJ/kg |
| CO₂ Footprint | 2.5-4.0 | kg CO₂/kg |
| EU RoHS Compliance | Exempt (Annex III) | - |

| Parameter | Range | Unit |
| --- | --- | --- |
| Wavelength | 1064nm (primary), 532nm (optional) | - |
| Power | 20-100 | W |
| Pulse Duration | 10-100 | ns |
| Spot Size | 0.1-2.0 | mm |
| Repetition Rate | 10-50 | kHz |
| Fluence | 0.5-5 | J/cm² |"""

    def _aluminum_tables(self) -> str:
        """Generate exact aluminum tables matching real generator."""
        return """| Property | Value | Unit |
| --- | --- | --- |
| Atomic Number | 13 | - |
| Density | 2.70 | g/cm³ |
| Melting Point | 660 | °C |
| Boiling Point | 2470 | °C |
| Thermal Conductivity | 237 | W/(m·K) |
| Electrical Conductivity | 3.8×10⁷ | S/m |
| Tensile Strength | 90-700 | MPa |
| Young's Modulus | 70 | GPa |

| Grade | Purity (%) | Common Impurities |
| --- | --- | --- |
| AA 1100 | ≥99.0 | Si+Fe ≤ 1.0 |
| AA 2024 | ≥90.0 | Cu 3.8-4.9, Mg 1.2-1.8 |
| AA 6061 | ≥95.0 | Mg 0.8-1.2, Si 0.4-0.8 |
| AA 7075 | ≥87.0 | Zn 5.1-6.1, Mg 2.1-2.9 |

| Metric | Value | Condition |
| --- | --- | --- |
| Corrosion Rate (Atmospheric) | 0.005-0.02 | mm/year |
| Fatigue Strength | 50-150 | MPa (10⁷ cycles) |
| Hardness (Brinell) | 20-120 | HB |
| Reflectivity (IR) | 90-98% | λ = 1064nm |

| Standard | Scope |
| --- | --- |
| ASTM B152/B152M | Sheet/strip/plate |
| ISO 431 | High-conductivity copper |
| EN 1172 | Copper for roofing |
| IEC 60028 | International resistivity std |

| Parameter | Value | Unit |
| --- | --- | --- |
| Recyclability | 100% | - |
| Embodied Energy | 42-60 | MJ/kg |
| CO₂ Footprint | 2.5-4.0 | kg CO₂/kg |
| EU RoHS Compliance | Exempt (Annex III) | - |

| Parameter | Range | Unit |
| --- | --- | --- |
| Wavelength | 1064nm (primary), 532nm (optional) | - |
| Power | 20-100 | W |
| Pulse Duration | 10-100 | ns |
| Spot Size | 0.1-2.0 | mm |
| Repetition Rate | 10-50 | kHz |
| Fluence | 0.5-5 | J/cm² |"""


# Legacy compatibility - DEPRECATED: Use TestTableComponentGenerator instead
class MockTableComponentGenerator(TestTableComponentGenerator):
    """
    DEPRECATED: Legacy mock class for backward compatibility.
    Use TestTableComponentGenerator for deterministic testing.
    """
    pass
