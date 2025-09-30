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

            # Build final normalized YAML structure
            yaml_data = {
                'machineSettings': {
                    'settings': categorized_settings
                },
                'renderInstructions': (
                    "In Next.js, loop over settings[].rows and render as structured sections with "
                    "<h2>{header}</h2><table><tr><th>Category</th><th>Parameter</th><th>Value</th><th>Range</th></tr>"
                    "<tr><td>{category}</td><td>{parameter}</td><td>{value}</td><td>{range}</td></tr>. "
                    "Use MDX for headers. Pure data structure optimized for performance and standardized machine settings display."
                )
            }

            return yaml.dump(yaml_data, default_flow_style=False, sort_keys=False, allow_unicode=True, width=1000)

        except Exception as e:
            raise Exception(f"Error generating settings content: {e}")

    def _extract_laser_settings(self, machine_settings: Dict) -> list:
        """Extract laser system configuration settings"""
        rows = []
        
        # Power Range - explicit configuration required
        if not machine_settings.get("powerRange") and not machine_settings.get("power_range"):
            raise ValueError("Machine settings must provide powerRange or power_range - no defaults allowed")
        power_range = machine_settings.get("powerRange") or machine_settings.get("power_range")
        rows.append(self._create_settings_row(
            'Power Range', 
            power_range,
            self._build_range(machine_settings, "powerRange", "20W - 500W"),
            'Laser Power'
        ))
        
        # Wavelength - explicit configuration required
        if not machine_settings.get("wavelength") and not machine_settings.get("wavelength_optimal"):
            raise ValueError("Machine settings must provide wavelength or wavelength_optimal - no defaults allowed")
        wavelength = machine_settings.get("wavelength") or machine_settings.get("wavelength_optimal")
        rows.append(self._create_settings_row(
            'Wavelength',
            wavelength,
            self._build_range(machine_settings, "wavelength", "355nm - 2940nm"),
            'Optical'
        ))
        
        # Pulse Duration - explicit configuration required
        if not machine_settings.get("pulseDuration") and not machine_settings.get("pulse_duration"):
            raise ValueError("Machine settings must provide pulseDuration or pulse_duration - no defaults allowed")
        pulse_duration = machine_settings.get("pulseDuration") or machine_settings.get("pulse_duration")
        rows.append(self._create_settings_row(
            'Pulse Duration',
            pulse_duration,
            self._build_range(machine_settings, "pulseDuration", "1ns - 1000ns"),
            'Temporal'
        ))
        
        # Repetition Rate - explicit configuration required
        if not machine_settings.get("repetitionRate") and not machine_settings.get("repetition_rate"):
            raise ValueError("Machine settings must provide repetitionRate or repetition_rate - no defaults allowed")
        rep_rate = machine_settings.get("repetitionRate") or machine_settings.get("repetition_rate")
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
        
        # Fluence Range - explicit configuration required
        if not machine_settings.get("fluenceRange") and not machine_settings.get("fluence_threshold"):
            raise ValueError("Machine settings must provide fluenceRange or fluence_threshold - no defaults allowed")
        fluence = machine_settings.get("fluenceRange") or machine_settings.get("fluence_threshold")
        rows.append(self._create_settings_row(
            'Fluence Range',
            fluence,
            self._build_range(machine_settings, "fluenceRange", "0.1J/cm² - 50J/cm²"),
            'Energy Density'
        ))
        
        # Spot Size - explicit configuration required
        if not machine_settings.get("spotSize") and not machine_settings.get("spot_size"):
            raise ValueError("Machine settings must provide spotSize or spot_size - no defaults allowed")
        spot_size = machine_settings.get("spotSize") or machine_settings.get("spot_size")
        rows.append(self._create_settings_row(
            'Spot Size',
            spot_size,
            self._build_range(machine_settings, "spotSize", "0.01mm - 10mm"),
            'Beam Geometry'
        ))
        
        # Scanning Speed - explicit configuration required
        if not machine_settings.get("scanningSpeed") and not machine_settings.get("scanning_speed"):
            raise ValueError("Machine settings must provide scanningSpeed or scanning_speed - no defaults allowed")
        scanning_speed = machine_settings.get("scanningSpeed") or machine_settings.get("scanning_speed")
        rows.append(self._create_settings_row(
            'Scanning Speed',
            scanning_speed,
            self._build_range(machine_settings, "scanningSpeed", "10mm/s - 1000mm/s"),
            'Motion Control'
        ))
        
        # Working Distance - explicit configuration required
        if not machine_settings.get("workingDistance"):
            raise ValueError("Machine settings must provide workingDistance - no defaults allowed")
        working_distance = machine_settings.get("workingDistance")
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
        
        # Safety Class - explicit configuration required
        if not machine_settings.get("safetyClass") and not machine_settings.get("safety_class"):
            raise ValueError("Machine settings must provide safetyClass or safety_class - no defaults allowed")
        safety_class = machine_settings.get("safetyClass") or machine_settings.get("safety_class")
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
        
        # Ventilation Rate - explicit configuration required
        if not machine_settings.get("ventilationRate"):
            raise ValueError("Machine settings must provide ventilationRate - no defaults allowed")
        ventilation = machine_settings.get("ventilationRate")
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
        
        # Surface Roughness Target - explicit configuration required
        if not machine_settings.get("surfaceRoughness"):
            raise ValueError("Machine settings must provide surfaceRoughness - no defaults allowed")
        surface_roughness = machine_settings.get("surfaceRoughness")
        rows.append(self._create_settings_row(
            'Surface Roughness Target',
            surface_roughness,
            "Ra 0.05μm - Ra 2.0μm",
            'Surface Quality'
        ))
        
        # Cleaning Depth Control - explicit configuration required
        if not machine_settings.get("cleaningDepth"):
            raise ValueError("Machine settings must provide cleaningDepth - no defaults allowed")
        cleaning_depth = machine_settings.get("cleaningDepth")
        rows.append(self._create_settings_row(
            'Cleaning Depth Control',
            cleaning_depth,
            self._build_range(machine_settings, "cleaningDepth", "0.1μm - 50μm"),
            'Material Removal'
        ))
        
        # Process Monitoring - explicit configuration required
        if not machine_settings.get("processMonitoring"):
            raise ValueError("Machine settings must provide processMonitoring - no defaults allowed")
        monitoring = machine_settings.get("processMonitoring")
        rows.append(self._create_settings_row(
            'Process Monitoring',
            monitoring,
            "Manual - Real-time",
            'Quality Assurance'
        ))
        
        # Repeatability - explicit configuration required
        if not machine_settings.get("repeatability"):
            raise ValueError("Machine settings must provide repeatability - no defaults allowed")
        repeatability = machine_settings.get("repeatability")
        rows.append(self._create_settings_row(
            'Repeatability',
            repeatability,
            "±1% - ±10%",
            'Process Control'
        ))
        
        return rows

    def _extract_beam_settings(self, machine_settings: Dict) -> list:
        """Extract beam configuration settings"""
        rows = []
        
        # Beam Profile - explicit configuration required
        if not machine_settings.get('beamProfile') and not machine_settings.get('beam_profile'):
            raise ValueError("Machine settings must provide beamProfile or beam_profile - no defaults allowed")
        beam_profile = machine_settings.get('beamProfile') or machine_settings.get('beam_profile')
        rows.append(self._create_settings_row(
            'Beam Profile',
            beam_profile,
            "Gaussian - Top-hat",
            'Beam Geometry'
        ))
        
        # Laser Type - explicit configuration required
        if (not machine_settings.get('laserType') and not machine_settings.get('laser_type') and 
            not machine_settings.get('wavelengthOptimal')):
            raise ValueError("Machine settings must provide laserType, laser_type, or wavelengthOptimal - no defaults allowed")
        laser_type = (machine_settings.get('laserType') or machine_settings.get('laser_type') or 
                     machine_settings.get('wavelengthOptimal'))
        rows.append(self._create_settings_row(
            'Laser Type',
            laser_type,
            "Fiber - Nd:YAG - CO2",
            'Laser Configuration'
        ))
        
        # Beam Quality
        beam_quality = (
            machine_settings.get('beamQuality', '') or
            machine_settings.get('beam_quality', '') or
            "M² < 1.3"  # Default beam quality
        )
        rows.append(self._create_settings_row(
            'Beam Quality',
            beam_quality,
            "M² 1.1 - M² 2.0",
            'Beam Performance'
        ))
        
        # Polarization
        polarization = (
            machine_settings.get('polarization', '') or
            "Linear"  # Default polarization
        )
        rows.append(self._create_settings_row(
            'Polarization',
            polarization,
            "Linear - Circular - Random",
            'Beam Characteristics'
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
