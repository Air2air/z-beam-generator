#!/usr/bin/env python3
"""
Caption Component Generator

Generates technical image captions for laser cleaning applications.
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


class CaptionComponentGenerator(APIComponentGenerator):
    """Generator for caption components using material data"""

    def __init__(self):
        super().__init__("caption")
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
        """Generate caption component content"""
        try:
            # Validate required data
            if not material_name:
                return self.create_error_result("Material name is required")

            # Generate caption content
            content = self._create_caption_content(material_name, material_data)

            return ComponentResult(
                component_type="caption", content=content, success=True
            )

        except Exception as e:
            return handle_generation_error("caption", e, "content generation")

    def _create_caption_content(self, material_name: str, material_data: Dict) -> str:
        """Create caption content with before/after format"""
        # Get contamination types and laser parameters
        contamination = self._get_random_contamination()
        laser_params = self._get_random_laser_params()

        # Create the two-line caption format
        line1 = f"**{material_name}** surface (left) before cleaning, showing {contamination}."

        line2 = f"**After laser cleaning** (right) at {laser_params['wavelength']} nm, {laser_params['power']} W, {laser_params['pulse_duration']} ns pulse duration, and {laser_params['spot_size']} µm spot size, achieving {self._get_random_result()}."

        return f"{line1}\n\n{line2}"

    def _get_random_contamination(self) -> str:
        """Get random contamination description"""
        contaminations = [
            "organic contaminants and particulate adhesion",
            "oxide layers and surface staining",
            "particulate buildup and corrosion deposits",
            "surface residues and contamination layers",
            "industrial deposits and material buildup",
            "environmental contaminants and surface films",
            "processing residues and impurity accumulation",
            "atmospheric deposits and surface contamination",
        ]
        return random.choice(contaminations)

    def _get_random_laser_params(self) -> Dict[str, Any]:
        """Get random laser parameters"""
        wavelengths = [355, 532, 1064, 266]
        powers = [5, 10, 15, 20, 25]
        pulse_durations = [10, 50, 100, 200]
        spot_sizes = [100, 200, 300, 500, 1000]

        return {
            "wavelength": random.choice(wavelengths),
            "power": random.choice(powers),
            "pulse_duration": random.choice(pulse_durations),
            "spot_size": random.choice(spot_sizes),
        }

    def _get_random_result(self) -> str:
        """Get random result description"""
        results = [
            "complete contaminant removal with minimal substrate modification",
            "precise contamination removal with controlled ablation",
            "effective surface cleaning with maintained material integrity",
            "thorough contaminant elimination with optimized parameters",
            "successful surface restoration with minimal thermal effects",
            "comprehensive cleaning with preserved surface characteristics",
            "efficient contaminant removal with controlled process parameters",
            "complete surface decontamination with optimized laser settings",
        ]
        return random.choice(results)

    def create_error_result(self, error_message: str) -> ComponentResult:
        """Create a ComponentResult for error cases"""
        return ComponentResult(
            component_type="caption",
            content="",
            success=False,
            error_message=error_message,
        )


# Legacy compatibility
class CaptionGenerator:
    """Legacy caption generator for backward compatibility"""

    def __init__(self):
        self.generator = CaptionComponentGenerator()

    def generate(self, material: str, material_data: Dict = None) -> str:
        """Legacy generate method"""
        if material_data is None:
            material_data = {"name": material}

        result = self.generator.generate(material, material_data)

        if result.success:
            return result.content
        else:
            return f"Error generating caption content: {result.error_message}"

    def get_component_info(self) -> Dict[str, Any]:
        """Get component information"""
        return {
            "name": "caption",
            "description": "Technical image caption component",
            "version": "1.0.0",
            "requires_api": False,
            "type": "static",
        }


def generate_caption_content(material: str, material_data: Dict = None) -> str:
    """Legacy function for backward compatibility"""
    generator = CaptionGenerator()
    return generator.generate(material, material_data)


if __name__ == "__main__":
    # Test the generator
    generator = CaptionGenerator()
    test_content = generator.generate("Aluminum")
    print("🧪 Caption Component Test:")
    print("=" * 50)
    print(test_content)
