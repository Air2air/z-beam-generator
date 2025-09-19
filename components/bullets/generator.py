#!/usr/bin/env python3
"""
Bullets Component Generator

Generates technical bullet points for laser cleaning applications using frontmatter data.
FAIL-FAST: Requires all laser parameters from frontmatter - no defaults or random generation.
"""

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
        """Generate bullets component content using frontmatter data"""
        try:
            # FAIL-FAST: Validate required inputs
            if not material_name:
                raise ValueError("Material name is required for bullets generation")
            if not frontmatter_data:
                raise ValueError("Frontmatter data is required for bullets generation - no fallbacks allowed")

            # Generate bullets content using frontmatter data
            content = self._create_bullets_content(material_name, frontmatter_data)

            # Apply centralized version stamping
            return stamp_component_output("bullets", content)

        except Exception as e:
            raise Exception(f"Error generating bullets content: {e}")

    def _create_bullets_content(self, material_name: str, frontmatter_data: Dict) -> str:
        """Create bullets content using frontmatter machine settings and properties"""
        # Extract machine settings from frontmatter
        machine_settings = frontmatter_data.get("machineSettings", {})
        if not machine_settings:
            raise ValueError(f"Machine settings not found in frontmatter for {material_name} - fail-fast requires complete data")

        # Extract properties from frontmatter
        properties = frontmatter_data.get("properties", {})
        if not properties:
            raise ValueError(f"Properties not found in frontmatter for {material_name} - fail-fast requires complete data")

        bullets = []

        # Generate 4 technical bullet points using actual frontmatter data
        bullets.append(self._generate_wavelength_bullet(material_name, machine_settings))
        bullets.append(self._generate_precision_bullet(material_name, machine_settings))
        bullets.append(self._generate_applications_bullet(material_name, properties))
        bullets.append(self._generate_thermal_bullet(material_name, machine_settings))

        return "\n\n".join(bullets)

    def _generate_wavelength_bullet(self, material_name: str, machine_settings: Dict) -> str:
        """Generate wavelength-focused bullet using frontmatter data"""
        wavelength = machine_settings.get("wavelength")
        if not wavelength:
            raise ValueError(f"Wavelength not found in machine settings for {material_name}")
        
        power_range = machine_settings.get("powerRange", "")
        fluence_range = machine_settings.get("fluenceRange", "")
        
        # Build description with available parameters
        power_desc = f" with {power_range} power output" if power_range else ""
        fluence_desc = f" at {fluence_range} fluence levels" if fluence_range else ""
        
        return f"• **Optimal Wavelength for Laser Cleaning**: {material_name} exhibits optimal response to {wavelength} laser systems{power_desc}{fluence_desc}, providing precise energy absorption for effective contaminant removal while minimizing thermal damage."

    def _generate_precision_bullet(self, material_name: str, machine_settings: Dict) -> str:
        """Generate precision-focused bullet using machine settings"""
        pulse_duration = machine_settings.get("pulseDuration")
        spot_size = machine_settings.get("spotSize")
        
        if not pulse_duration:
            raise ValueError(f"Pulse duration not found in machine settings for {material_name}")
        if not spot_size:
            raise ValueError(f"Spot size not found in machine settings for {material_name}")

        return f"• **Non-Contact Precision Cleaning**: Laser cleaning removes surface contaminants from {material_name} using {pulse_duration} pulse duration and {spot_size} spot size, ensuring selective material removal without mechanical contact or substrate damage."

    def _generate_applications_bullet(self, material_name: str, properties: Dict) -> str:
        """Generate applications-focused bullet using material properties"""
        category = properties.get("category")
        if not category:
            raise ValueError(f"Category not found in properties for {material_name}")
        
        # Map categories to relevant applications
        industry_map = {
            "Metal": "aerospace, automotive, and electronics industries",
            "Alloy": "aerospace, marine, and manufacturing industries", 
            "Wood": "furniture, construction, and restoration industries",
            "Stone": "construction, architectural, and restoration industries",
            "Glass": "electronics, optical, and semiconductor industries",
            "Composite": "aerospace, automotive, and marine industries",
            "Ceramic": "semiconductor, medical, and precision engineering industries"
        }
        
        industries = industry_map.get(category, "industrial and manufacturing applications")
        
        return f"• **Industrial Applications**: Widely used in {industries} for {material_name} surface preparation, contamination removal, and restoration processes requiring precise material handling."

    def _generate_thermal_bullet(self, material_name: str, machine_settings: Dict) -> str:
        """Generate thermal considerations bullet using machine settings"""
        repetition_rate = machine_settings.get("repetitionRate")
        scanning_speed = machine_settings.get("scanningSpeed")
        
        if not repetition_rate:
            raise ValueError(f"Repetition rate not found in machine settings for {material_name}")
        if not scanning_speed:
            raise ValueError(f"Scanning speed not found in machine settings for {material_name}")

        return f"• **Thermal Processing Considerations**: Optimized {repetition_rate} repetition rate and {scanning_speed} scanning speed ensure precise energy delivery to {material_name}, minimizing heat accumulation while achieving effective surface processing without thermal stress or distortion."




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
