#!/usr/bin/env python3
"""
Settings Component Generator

Generates laser processing machine settings from frontmatter data.
Extracts technical specifications and machine parameters for optimal laser cleaning.
Follows fail-fast architecture with frontmatter dependency.
"""

import logging
import yaml
from typing import Dict, Optional

from generators.component_generators import StaticComponentGenerator

logger = logging.getLogger(__name__)


class SettingsComponentGenerator(StaticComponentGenerator):
    """Generator for laser processing machine settings - FAIL-FAST: Requires frontmatter data"""

    def __init__(self):
        super().__init__("settings")

    def _generate_static_content(
        self,
        material_name: str,
        material_data: Dict,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> str:
        """Generate machine settings from frontmatter - FAIL-FAST: Must have frontmatter data"""
        try:
            # Validate required data - FAIL-FAST: Need frontmatter data
            if not material_name:
                raise Exception("Material name is required - fail-fast architecture requires complete input data")
            
            if not frontmatter_data:
                raise Exception("Frontmatter data is required - fail-fast architecture requires machine settings")

            # Extract machine settings from frontmatter - check multiple possible keys
            machine_settings = (
                frontmatter_data.get('machineSettings', {}) or 
                frontmatter_data.get('technicalSpecifications', {}) or 
                frontmatter_data.get('laser_parameters', {})
            )
            
            if not machine_settings:
                raise Exception(f"No machine settings found in frontmatter for {material_name}. Checked: machineSettings, technicalSpecifications, laser_parameters")

            # Build categorized settings with normalized structure - 4 required sections
            categorized_settings = []

            # 1. Machine Configuration
            laser_props = self._extract_laser_settings(machine_settings)
            categorized_settings.append({
                'header': '## Machine Configuration',
                'rows': laser_props
            })

            # 2. Processing Parameters  
            processing_props = self._extract_processing_settings(machine_settings)
            categorized_settings.append({
                'header': '## Processing Parameters',
                'rows': processing_props
            })

            # 3. Safety Parameters
            safety_props = self._extract_safety_settings(machine_settings)
            categorized_settings.append({
                'header': '## Safety Parameters',
                'rows': safety_props
            })

            # 4. Quality Control Settings
            quality_props = self._extract_quality_settings(machine_settings)
            categorized_settings.append({
                'header': '## Quality Control Settings',
                'rows': quality_props
            })

            # Build final normalized YAML structure (no renderInstructions)
            yaml_data = {
                'machineSettings': {
                    'settings': categorized_settings
                }
            }

            return yaml.dump(yaml_data, default_flow_style=False, sort_keys=False, allow_unicode=True, width=1000)

        except Exception as e:
            raise Exception(f"Error generating settings content: {e}")

    def _extract_laser_settings(self, machine_settings: Dict) -> list:
        """Extract laser system configuration settings"""
        rows = []
        
        # Power Range - check multiple field names
        power_range = (
            machine_settings.get("powerRange") or 
            machine_settings.get("power_range") or
            "20-100W"  # Default fallback
        )
        rows.append(self._create_settings_row(
            'Power Range', 
            power_range,
            self._build_range(machine_settings, "powerRange", "20W - 500W"),
            'Laser Power'
        ))
        
        # Wavelength - check multiple field names  
        wavelength = (
            machine_settings.get("wavelength") or
            machine_settings.get("wavelength_optimal") or
            "1064nm (primary), 532nm (optional)"  # Default fallback
        )
        rows.append(self._create_settings_row(
            'Wavelength',
            wavelength,
            self._build_range(machine_settings, "wavelength", "355nm - 2940nm"),
            'Optical'
        ))
        
        # Pulse Duration - check multiple field names
        pulse_duration = (
            machine_settings.get("pulseDuration") or
            machine_settings.get("pulse_duration") or
            "10-100ns"  # Default fallback
        )
        rows.append(self._create_settings_row(
            'Pulse Duration',
            pulse_duration,
            self._build_range(machine_settings, "pulseDuration", "1ns - 1000ns"),
            'Temporal'
        ))
        
        # Repetition Rate - check multiple field names
        rep_rate = (
            machine_settings.get("repetitionRate") or
            machine_settings.get("repetition_rate") or
            "20-100kHz"  # Default fallback
        )
        rows.append(self._create_settings_row(
            'Repetition Rate',
            rep_rate,
            self._build_range(machine_settings, "repetitionRate", "1kHz - 1000kHz"),
            'Timing'
        ))
        
        return rows

    def _extract_processing_settings(self, machine_settings: Dict) -> list:
        """Extract processing parameter settings"""
        rows = []
        
        # Fluence Range - check multiple field names
        fluence = (
            machine_settings.get("fluenceRange") or
            machine_settings.get("fluence_threshold") or
            "0.5-5.0 J/cm²"  # Default fallback
        )
        rows.append(self._create_settings_row(
            'Fluence Range',
            fluence,
            self._build_range(machine_settings, "fluenceRange", "0.1J/cm² - 50J/cm²"),
            'Energy Density'
        ))
        
        # Spot Size - check multiple field names
        spot_size = (
            machine_settings.get("spotSize") or
            machine_settings.get("spot_size") or
            "0.1-2.0mm"  # Default fallback
        )
        rows.append(self._create_settings_row(
            'Spot Size',
            spot_size,
            self._build_range(machine_settings, "spotSize", "0.01mm - 10mm"),
            'Beam Geometry'
        ))
        
        # Scanning Speed - check multiple field names
        scanning_speed = (
            machine_settings.get("scanningSpeed") or
            machine_settings.get("scanning_speed") or
            "50-200mm/s"  # Default fallback
        )
        rows.append(self._create_settings_row(
            'Scanning Speed',
            scanning_speed,
            self._build_range(machine_settings, "scanningSpeed", "10mm/s - 1000mm/s"),
            'Motion Control'
        ))
        
        # Working Distance
        working_distance = (
            machine_settings.get("workingDistance") or
            "100-300mm"  # Default fallback
        )
        rows.append(self._create_settings_row(
            'Working Distance',
            working_distance,
            self._build_range(machine_settings, "workingDistance", "50mm - 500mm"),
            'Positioning'
        ))
        
        return rows

    def _extract_safety_settings(self, machine_settings: Dict) -> list:
        """Extract safety parameter settings"""
        rows = []
        
        # Safety Class
        safety_class = (
            machine_settings.get("safetyClass") or
            machine_settings.get("safety_class") or
            "Class 4"  # Default fallback
        )
        rows.append(self._create_settings_row(
            'Safety Class',
            safety_class,
            "Class 1 - Class 4",
            'Laser Safety'
        ))
        
        # Beam Enclosure
        rows.append(self._create_settings_row(
            'Beam Enclosure',
            "Required",
            "Required - Optional",
            'Safety Equipment'
        ))
        
        # Ventilation Rate
        ventilation = (
            machine_settings.get("ventilationRate") or
            "200-500 CFM"  # Default fallback
        )
        rows.append(self._create_settings_row(
            'Ventilation Rate',
            ventilation,
            "100CFM - 1000CFM",
            'Environmental Safety'
        ))
        
        # Emergency Stop
        rows.append(self._create_settings_row(
            'Emergency Stop',
            "Required",
            "Required - Required",
            'Safety Controls'
        ))
        
        return rows

    def _extract_quality_settings(self, machine_settings: Dict) -> list:
        """Extract quality control settings"""
        rows = []
        
        # Surface Roughness Target
        surface_roughness = (
            machine_settings.get("surfaceRoughness") or
            "Ra 0.1-0.5μm"  # Default fallback
        )
        rows.append(self._create_settings_row(
            'Surface Roughness Target',
            surface_roughness,
            "Ra 0.05μm - Ra 2.0μm",
            'Surface Quality'
        ))
        
        # Cleaning Depth Control
        cleaning_depth = (
            machine_settings.get("cleaningDepth") or
            "1-10μm"  # Default fallback
        )
        rows.append(self._create_settings_row(
            'Cleaning Depth Control',
            cleaning_depth,
            self._build_range(machine_settings, "cleaningDepth", "0.1μm - 50μm"),
            'Material Removal'
        ))
        
        # Process Monitoring
        monitoring = (
            machine_settings.get("processMonitoring") or
            "Real-time optical"  # Default fallback
        )
        rows.append(self._create_settings_row(
            'Process Monitoring',
            monitoring,
            "Manual - Real-time",
            'Quality Assurance'
        ))
        
        # Repeatability
        repeatability = (
            machine_settings.get("repeatability") or
            "±5%"  # Default fallback
        )
        rows.append(self._create_settings_row(
            'Repeatability',
            repeatability,
            "±1% - ±10%",
            'Process Control'
        ))
        
        return rows

    def _build_range(self, machine_settings: Dict, base_key: str, default_range: str) -> str:
        """Build range string from min/max values or use default"""
        min_key = f"{base_key}Min"
        max_key = f"{base_key}Max"
        
        min_val = machine_settings.get(min_key, "")
        max_val = machine_settings.get(max_key, "")
        
        if min_val and max_val:
            return f"{min_val} - {max_val}"
        elif min_val:
            return f"{min_val} - TBD"
        elif max_val:
            return f"TBD - {max_val}"
        else:
            return default_range

    def _create_settings_row(self, parameter: str, value: str, range_info: str, category: str) -> Dict:
        """Create a standardized settings row (like table component)"""
        return {
            'parameter': parameter,
            'value': value,
            'range': range_info if range_info != ' - ' else '-',
            'category': category
        }


# Standalone function for compatibility
def generate_settings_content(material: str, material_data: Dict = None) -> str:
    """Generate settings content for the given material"""
    generator = SettingsComponentGenerator()
    
    # Create a wrapper generator for compatibility
    class SettingsWrapper:
        def __init__(self):
            self.generator = generator
        
        def generate(self, material: str, material_data: Dict = None) -> str:
            if material_data is None:
                material_data = {"name": material}
            
            try:
                content = self.generator._generate_static_content(
                    material, material_data
                )
                return content
            except Exception as e:
                return f"Error generating settings content: {e}"
    
    wrapper = SettingsWrapper()
    return wrapper.generate(material, material_data)
