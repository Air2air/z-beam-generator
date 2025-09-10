#!/usr/bin/env python3
"""
Bullets Component Generator

Generates technical bullet points for laser cleaning applications.
Uses consolidated component base utilities for reduced code duplication.
"""

import random
from pathlib import Path
from typing import Any, Dict, Optional

from generators.component_generators import StaticComponentGenerator
from versioning import stamp_component_output


class BulletsComponentGenerator(StaticComponentGenerator):
    """Generator for bullets components using material data"""

    def __init__(self):
        super().__init__("bullets")
        self.prompt_file = Path(__file__).parent / "prompt.yaml"

    def _generate_static_content(
        self,
        material_name: str,
        material_data: Dict,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> str:
        """Generate bullets component content"""
        try:
            # Validate required data
            if not material_name:
                raise ValueError("Material name is required")

            # Generate bullets content
            content = self._create_bullets_content(material_name, material_data)

            # Apply centralized version stamping
            return stamp_component_output("bullets", content)

        except Exception as e:
            raise Exception(f"Error generating bullets content: {e}")

    def _create_bullets_content(self, material_name: str, material_data: Dict) -> str:
        """Create bullets content with technical details"""
        bullets = []

        # Generate 4 technical bullet points (matching example file count)
        bullets.append(self._generate_wavelength_bullet(material_name))
        bullets.append(self._generate_precision_bullet(material_name))
        bullets.append(self._generate_applications_bullet(material_name))
        bullets.append(self._generate_thermal_bullet(material_name))

        # Apply word count limits similar to example file (100-150 words total)
        content = "\n\n".join(bullets)
        words = content.split()
        if len(words) > 150:  # Max ~150 words total
            # Truncate to approximately 150 words while preserving bullet structure
            truncated_words = words[:150]
            content = " ".join(truncated_words)
            # Ensure we end at a complete bullet if possible
            if not content.endswith("."):
                content = content.rsplit(".", 1)[0] + "."

        return content

    def _generate_wavelength_bullet(self, material_name: str) -> str:
        """Generate wavelength-focused bullet"""
        wavelengths = [355, 532, 1064, 266]
        wavelength = random.choice(wavelengths)

        descriptions = [
            f"exhibits high reflectivity, making the {wavelength}nm wavelength (common in pulsed fiber lasers) ideal for effective laser ablation",
            f"responds well to {wavelength}nm wavelength lasers, providing optimal energy absorption for contaminant removal",
            f"benefits from {wavelength}nm laser systems, which offer excellent coupling efficiency for surface cleaning",
            f"works effectively with {wavelength}nm wavelength, delivering precise ablation while controlling thermal effects",
        ]

        return f"• **Optimal Wavelength for Laser Cleaning**: {material_name} {random.choice(descriptions)} while minimizing thermal damage."

    def _generate_precision_bullet(self, material_name: str) -> str:
        """Generate precision-focused bullet"""
        contaminants = [
            "oxides, oils, coatings",
            "surface contaminants and residues",
            "industrial deposits and films",
            "environmental contaminants and buildup",
        ]

        benefits = [
            "preserving substrate integrity and reducing material waste",
            "maintaining surface quality and dimensional accuracy",
            "ensuring consistent cleaning results without mechanical stress",
            "providing selective removal without affecting base material properties",
        ]

        return f"• **Non-Contact Precision Cleaning**: Laser cleaning removes {random.choice(contaminants)} from {material_name} without mechanical contact, {random.choice(benefits)}."

    def _generate_applications_bullet(self, material_name: str) -> str:
        """Generate applications-focused bullet"""
        industries = [
            "electronics, aerospace, and automotive",
            "semiconductor, medical, and manufacturing",
            "aerospace, marine, and industrial equipment",
            "automotive, electronics, and precision engineering",
        ]

        purposes = [
            f"restoring {material_name} surfaces, enhancing conductivity, and preparing for soldering or bonding",
            f"improving {material_name} surface finish, removing coatings, and preparing for further processing",
            f"cleaning critical {material_name} components, removing residues, and ensuring surface quality",
            f"preparing {material_name} surfaces for coating, improving adhesion, and extending component life",
        ]

        return f"• **Industrial Applications**: Widely used in {random.choice(industries)} industries for {random.choice(purposes)}."

    def _generate_thermal_bullet(self, material_name: str) -> str:
        """Generate thermal considerations bullet"""
        considerations = [
            f"Requires precise pulse duration and energy control to avoid excessive heat buildup in {material_name}",
            f"Demands careful parameter selection to prevent thermal stress and distortion of {material_name}",
            f"Needs optimized laser settings to minimize thermal effects on sensitive {material_name} surfaces",
            f"Benefits from controlled energy delivery to prevent unwanted modification of {material_name}",
        ]

        outcomes = [
            "ensuring efficient contamination removal without melting or warping the substrate",
            "providing effective cleaning while maintaining material integrity and properties",
            "delivering precise ablation without compromising structural characteristics",
            "achieving thorough cleaning with minimal thermal impact on the base material",
        ]

        return f"• **Thermal Processing Considerations**: {random.choice(considerations)}, {random.choice(outcomes)}."




# Legacy compatibility
class BulletsGenerator:
    """Legacy bullets generator for backward compatibility"""

    def __init__(self):
        self.generator = BulletsComponentGenerator()

    def generate(self, material: str, material_data: Dict = None) -> str:
        """Legacy generate method"""
        if material_data is None:
            material_data = {"name": material}

        result = self.generator.generate(material, material_data)

        if result.success:
            return result.content
        else:
            return f"Error generating bullets content: {result.error_message}"

    def get_component_info(self) -> Dict[str, Any]:
        """Get component information"""
        return {
            "name": "bullets",
            "description": "Technical bullet points component",
            "version": "1.0.0",
            "requires_api": False,
            "type": "static",
        }


def generate_bullets_content(material: str, material_data: Dict = None) -> str:
    """Legacy function for backward compatibility"""
    generator = BulletsGenerator()
    return generator.generate(material, material_data)


if __name__ == "__main__":
    # Test the generator
    generator = BulletsGenerator()
    test_content = generator.generate("Aluminum")
    print("🧪 Bullets Component Test:")
    print("=" * 50)
    print(test_content)
