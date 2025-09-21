#!/usr/bin/env python3
"""
Table Component Generator

Generates deterministic YAML tables from frontmatter data.
No API requests needed - processes frontmatter directly.
Follows fail-fast architecture with no fallbacks.
"""

import logging
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union

from generators.component_generators import StaticComponentGenerator
from utils.core.component_base import (
    handle_generation_error,
)

logger = logging.getLogger(__name__)


class TableComponentGenerator(StaticComponentGenerator):
    """Generator for table components using frontmatter data - FAIL-FAST: No API calls needed"""

    def __init__(self):
        super().__init__("table")

    def _generate_static_content(
        self,
        material_name: str,
        material_data: Dict,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> str:
        """Generate table component content from frontmatter - FAIL-FAST: Must have frontmatter data"""
        try:
            # Validate required data - FAIL-FAST: Need frontmatter data
            if not material_name:
                raise Exception("Material name is required - fail-fast architecture requires complete input data")
            
            if not frontmatter_data:
                raise Exception("Frontmatter data is required - fail-fast architecture requires frontmatter properties")

            # Check if frontmatter has any extractable data sections
            has_data = any([
                frontmatter_data.get('chemicalProperties'),
                frontmatter_data.get('properties') and isinstance(frontmatter_data.get('properties'), dict) and frontmatter_data.get('properties'),
                frontmatter_data.get('machineSettings'),
                frontmatter_data.get('applications'),
                frontmatter_data.get('outcomes'),
                frontmatter_data.get('environmentalImpact'),
                frontmatter_data.get('compatibility'),
                frontmatter_data.get('regulatoryStandards')
            ])
            
            if not has_data:
                raise Exception(f"No extractable data found in frontmatter for {material_name} - need at least one data section (chemical properties, machine settings, applications, etc.)")

            # Generate deterministic YAML table content
            table_yaml = self._generate_yaml_tables(material_name, frontmatter_data)

            # Return YAML content without version stamping for now
            return table_yaml

        except Exception as e:
            raise Exception(f"Table generation failed for {material_name}: {str(e)}")

    def _generate_yaml_tables(self, material_name: str, frontmatter_data: Dict) -> str:
        """Generate YAML tables from frontmatter data following available data structure"""
        
        # Group available frontmatter data into meaningful categories
        categorized_tables = []
        
        # Chemical Properties & Composition
        chemical_props = self._extract_chemical_properties(frontmatter_data)
        if chemical_props:
            categorized_tables.append({
                'header': '## Chemical Properties',
                'rows': chemical_props
            })
        
        # Physical & Mechanical Properties (from properties section)
        physical_props = self._extract_physical_properties(frontmatter_data)
        if physical_props:
            categorized_tables.append({
                'header': '## Physical & Mechanical Properties',
                'rows': physical_props
            })
        
        # Laser Processing Parameters (from machineSettings)
        laser_props = self._extract_machine_settings_properties(frontmatter_data)
        if laser_props:
            categorized_tables.append({
                'header': '## Laser Processing Parameters',
                'rows': laser_props
            })
        
        # Applications & Industries
        application_props = self._extract_application_properties(frontmatter_data)
        if application_props:
            categorized_tables.append({
                'header': '## Applications & Industries',
                'rows': application_props
            })
        
        # Performance Metrics (from outcomes)
        performance_props = self._extract_performance_properties(frontmatter_data)
        if performance_props:
            categorized_tables.append({
                'header': '## Performance Metrics',
                'rows': performance_props
            })
        
        # Environmental Impact
        environmental_props = self._extract_environmental_properties(frontmatter_data)
        if environmental_props:
            categorized_tables.append({
                'header': '## Environmental Impact',
                'rows': environmental_props
            })
        
        # Compatibility & Standards
        compliance_props = self._extract_compliance_properties(frontmatter_data)
        if compliance_props:
            categorized_tables.append({
                'header': '## Compatibility & Standards',
                'rows': compliance_props
            })
        
        # Build final YAML structure
        yaml_data = {
            'materialTables': {
                'tables': categorized_tables
            },
            'renderInstructions': (
                "In Next.js, loop over tables[].rows and render as <table> with "
                "<tr><td>{property}</td><td>{value} ({unit})</td><td>{min}-{max}</td>"
                "<td>{percentile ? percentile + '%' : 'N/A'}</td>"
                "<td>{category}</td></tr>. "
                "Use MDX for headers. Pure data structure optimized for performance."
            )
        }
        
        return yaml.dump(yaml_data, default_flow_style=False, sort_keys=False, allow_unicode=True, width=1000)

    def _extract_chemical_properties(self, frontmatter_data: Dict) -> list:
        """Extract chemical properties from frontmatter data"""
        rows = []
        
        # Chemical Properties
        chemical_props = frontmatter_data.get("chemicalProperties", {})
        if chemical_props.get("formula"):
            rows.append(self._create_simple_property_row(
                'Chemical Formula', 
                chemical_props["formula"],
                '-',
                'Chemical'
            ))
        
        if chemical_props.get("symbol"):
            rows.append(self._create_simple_property_row(
                'Chemical Symbol',
                chemical_props["symbol"],
                '-',
                'Chemical'
            ))
        
        if chemical_props.get("materialType"):
            rows.append(self._create_simple_property_row(
                'Material Type',
                chemical_props["materialType"].title(),
                '-',
                'Classification'
            ))
        
        # Composition
        composition = frontmatter_data.get("composition", [])
        if composition:
            composition_text = ", ".join(composition)
            rows.append(self._create_simple_property_row(
                'Composition',
                composition_text,
                '-',
                'Composition'
            ))
        
        return rows

    def _extract_physical_properties(self, frontmatter_data: Dict) -> list:
        """Extract physical and mechanical properties from the properties section"""
        rows = []
        
        properties = frontmatter_data.get("properties", {})
        if not properties or not isinstance(properties, dict):
            return rows  # Return empty if no properties or if properties is empty dict
        
        # Density
        if properties.get("density"):
            rows.append(self._create_property_row(
                'Density',
                properties["density"],
                properties.get("densityMinNumeric"),
                properties.get("densityMaxNumeric"),
                properties.get("densityNumeric"),
                properties.get("densityPercentile"),
                properties.get("densityUnit", "g/cm³")
            ))
        
        # Melting Point
        if properties.get("meltingPoint"):
            rows.append(self._create_property_row(
                'Melting Point',
                properties["meltingPoint"],
                None,  # No min/max for melting point typically
                None,
                properties.get("meltingPointNumeric"),
                properties.get("meltingPercentile"),
                properties.get("meltingPointUnit", "°C")
            ))
        
        # Thermal Conductivity
        if properties.get("thermalConductivity"):
            rows.append(self._create_property_row(
                'Thermal Conductivity',
                properties["thermalConductivity"],
                None,
                None,
                properties.get("thermalConductivityNumeric"),
                properties.get("thermalPercentile"),
                properties.get("thermalConductivityUnit", "W/m·K")
            ))
        
        # Tensile Strength
        if properties.get("tensileStrength"):
            rows.append(self._create_property_row(
                'Tensile Strength',
                properties["tensileStrength"],
                None,
                None,
                properties.get("tensileStrengthNumeric"),
                properties.get("tensilePercentile"),
                properties.get("tensileStrengthUnit", "MPa")
            ))
        
        # Hardness
        if properties.get("hardness"):
            rows.append(self._create_property_row(
                'Hardness',
                properties["hardness"],
                properties.get("hardnessMinNumeric"),
                properties.get("hardnessMaxNumeric"),
                properties.get("hardnessNumeric"),
                properties.get("hardnessPercentile"),
                properties.get("hardnessUnit", "HRB")
            ))
        
        # Young's Modulus
        if properties.get("youngsModulus"):
            rows.append(self._create_property_row(
                "Young's Modulus",
                properties["youngsModulus"],
                properties.get("modulusMinNumeric"),
                properties.get("modulusMaxNumeric"),
                properties.get("youngsModulusNumeric"),
                properties.get("modulusPercentile"),
                properties.get("youngsModulusUnit", "GPa")
            ))
        
        return rows

    def _extract_machine_settings_properties(self, frontmatter_data: Dict) -> list:
        """Extract laser processing parameters from machineSettings"""
        rows = []
        
        machine_settings = frontmatter_data.get("machineSettings", {})
        
        # Power Range with numeric values
        if machine_settings.get("powerRange"):
            value = machine_settings["powerRange"]
            min_val = machine_settings.get("powerRangeMinNumeric")
            max_val = machine_settings.get("powerRangeMaxNumeric")
            numeric_val = machine_settings.get("powerRangeNumeric")
            unit = machine_settings.get("powerRangeUnit", "W")
            
            rows.append(self._create_property_row(
                'Power Range', 
                value,
                min_val,
                max_val,
                numeric_val,
                None,
                unit
            ))
        
        # Pulse Duration with numeric values
        if machine_settings.get("pulseDuration"):
            value = machine_settings["pulseDuration"]
            min_val = machine_settings.get("pulseDurationMinNumeric")
            max_val = machine_settings.get("pulseDurationMaxNumeric")
            numeric_val = machine_settings.get("pulseDurationNumeric")
            unit = machine_settings.get("pulseDurationUnit", "ns")
            
            if min_val and max_val and numeric_val:
                rows.append(self._create_property_row(
                    'Pulse Duration',
                    value,
                    min_val,
                    max_val,
                    numeric_val,
                    None,
                    unit
                ))
            else:
                rows.append(self._create_simple_property_row(
                    'Pulse Duration',
                    value,
                    unit,
                    'Standard'
                ))
        
        # Wavelength with numeric values
        if machine_settings.get("wavelength"):
            value = machine_settings["wavelength"]
            min_val = machine_settings.get("wavelengthMinNumeric")
            max_val = machine_settings.get("wavelengthMaxNumeric")
            numeric_val = machine_settings.get("wavelengthNumeric")
            unit = machine_settings.get("wavelengthUnit", "nm")
            
            if min_val and max_val and numeric_val:
                rows.append(self._create_property_row(
                    'Wavelength',
                    value,
                    min_val,
                    max_val,
                    numeric_val,
                    None,
                    unit
                ))
            else:
                rows.append(self._create_simple_property_row(
                    'Wavelength',
                    value,
                    unit,
                    'Optimal'
                ))
        
        # Spot Size with numeric values
        if machine_settings.get("spotSize"):
            value = machine_settings["spotSize"]
            min_val = machine_settings.get("spotSizeMinNumeric")
            max_val = machine_settings.get("spotSizeMaxNumeric")
            numeric_val = machine_settings.get("spotSizeNumeric")
            unit = machine_settings.get("spotSizeUnit", "mm")
            
            if min_val and max_val and numeric_val:
                rows.append(self._create_property_row(
                    'Spot Size',
                    value,
                    min_val,
                    max_val,
                    numeric_val,
                    None,
                    unit
                ))
            else:
                rows.append(self._create_simple_property_row(
                    'Spot Size',
                    value,
                    unit,
                    'Configurable'
                ))
        
        # Repetition Rate with numeric values
        if machine_settings.get("repetitionRate"):
            value = machine_settings["repetitionRate"]
            min_val = machine_settings.get("repetitionRateMinNumeric")
            max_val = machine_settings.get("repetitionRateMaxNumeric")
            numeric_val = machine_settings.get("repetitionRateNumeric")
            unit = machine_settings.get("repetitionRateUnit", "kHz")
            
            if min_val and max_val and numeric_val:
                rows.append(self._create_property_row(
                    'Repetition Rate',
                    value,
                    min_val,
                    max_val,
                    numeric_val,
                    None,
                    unit
                ))
            else:
                rows.append(self._create_simple_property_row(
                    'Repetition Rate',
                    value,
                    unit,
                    'Variable'
                ))
        
        # Fluence Range with numeric values
        if machine_settings.get("fluenceRange"):
            value = machine_settings["fluenceRange"]
            min_val = machine_settings.get("fluenceRangeMinNumeric")
            max_val = machine_settings.get("fluenceRangeMaxNumeric")
            numeric_val = machine_settings.get("fluenceRangeNumeric")
            unit = machine_settings.get("fluenceRangeUnit", "J/cm²")
            
            if min_val and max_val and numeric_val:
                rows.append(self._create_property_row(
                    'Fluence Range',
                    value,
                    min_val,
                    max_val,
                    numeric_val,
                    None,
                    unit
                ))
            else:
                rows.append(self._create_simple_property_row(
                    'Fluence Range',
                    value,
                    unit,
                    'Range'
                ))
        
        # Scanning Speed with numeric values (new field in comprehensive frontmatter)
        if machine_settings.get("scanningSpeed"):
            value = machine_settings["scanningSpeed"]
            min_val = machine_settings.get("scanningSpeedMinNumeric")
            max_val = machine_settings.get("scanningSpeedMaxNumeric")
            numeric_val = machine_settings.get("scanningSpeedNumeric")
            unit = machine_settings.get("scanningSpeedUnit", "mm/s")
            
            rows.append(self._create_property_row(
                'Scanning Speed',
                value,
                min_val,
                max_val,
                numeric_val,
                None,
                unit
            ))
        
        # Laser Type
        if machine_settings.get("laserType"):
            rows.append(self._create_simple_property_row(
                'Laser Type',
                machine_settings["laserType"],
                '-',
                'System'
            ))
        
        # Beam Profile
        if machine_settings.get("beamProfile"):
            rows.append(self._create_simple_property_row(
                'Beam Profile',
                machine_settings["beamProfile"],
                '-',
                'System'
            ))
        
        # Safety Class
        if machine_settings.get("safetyClass"):
            rows.append(self._create_simple_property_row(
                'Safety Class',
                machine_settings["safetyClass"],
                '-',
                'Safety'
            ))
        
        return rows

    def _extract_application_properties(self, frontmatter_data: Dict) -> list:
        """Extract application and industry information"""
        rows = []
        
        applications = frontmatter_data.get("applications", [])
        for i, app in enumerate(applications):
            # Handle new string format: "Industry: Detail"
            if isinstance(app, str):
                # Parse "Industry: Detail" format
                if ':' in app:
                    industry, detail = app.split(':', 1)
                    industry = industry.strip()
                    detail = detail.strip()
                    rows.append(self._create_simple_property_row(
                        industry,
                        detail,
                        '-',
                        'Application'
                    ))
                else:
                    # Handle single-part applications
                    rows.append(self._create_simple_property_row(
                        f"Application {i+1}",
                        app,
                        '-',
                        'Application'
                    ))
            elif isinstance(app, dict) and app.get("industry") and app.get("detail"):
                # Handle legacy object format
                rows.append(self._create_simple_property_row(
                    app["industry"],
                    app["detail"],
                    '-',
                    'Application'
                ))
        
        return rows

    def _extract_performance_properties(self, frontmatter_data: Dict) -> list:
        """Extract performance metrics from outcomes"""
        rows = []
        
        outcomes = frontmatter_data.get("outcomes", [])
        for outcome in outcomes:
            if isinstance(outcome, dict) and outcome.get("result") and outcome.get("metric"):
                rows.append(self._create_simple_property_row(
                    outcome["result"],
                    outcome["metric"],
                    '-',
                    'Performance'
                ))
        
        return rows

    def _extract_environmental_properties(self, frontmatter_data: Dict) -> list:
        """Extract environmental impact information"""
        rows = []
        
        environmental_impact = frontmatter_data.get("environmentalImpact", [])
        for impact in environmental_impact:
            if isinstance(impact, dict) and impact.get("benefit") and impact.get("description"):
                rows.append(self._create_simple_property_row(
                    impact["benefit"],
                    impact["description"],
                    '-',
                    'Environmental'
                ))
        
        return rows

    def _extract_compliance_properties(self, frontmatter_data: Dict) -> list:
        """Extract compatibility and regulatory standards"""
        rows = []
        
        # Compatibility
        compatibility = frontmatter_data.get("compatibility", [])
        if compatibility:
            compatibility_text = ", ".join(compatibility)
            rows.append(self._create_simple_property_row(
                'Material Compatibility',
                compatibility_text,
                '-',
                'Compatibility'
            ))
        
        # Regulatory Standards
        regulatory = frontmatter_data.get("regulatoryStandards")
        if regulatory:
            rows.append(self._create_simple_property_row(
                'Regulatory Standards',
                regulatory,
                '-',
                'Compliance'
            ))
        
        return rows

    def _create_simple_property_row(self, property_name: str, value: str, unit: str, category: str) -> Dict:
        """Create a simplified property row without min/max ranges"""
        row = {
            'property': property_name,
            'value': str(value),
            'unit': unit,
            'category': category
        }
        
        return row

    def _create_property_row(self, property_name: str, value: str, min_val: Optional[str], 
                           max_val: Optional[str], numeric_val: Optional[float], percentile: Optional[float], unit: str) -> Dict:
        """Create a standardized property row"""
        row = {
            'property': property_name,
            'value': str(value),
            'unit': unit
        }
        
        # Add min/max if available
        if min_val is not None:
            row['min'] = str(min_val)
        if max_val is not None:
            row['max'] = str(max_val)
        if percentile is not None:
            row['percentile'] = float(percentile)
        
        # Add numeric value if available for calculations
        if numeric_val is not None:
            row['numeric'] = float(numeric_val)
        
        return row

    def _calculate_percentage(self, value: Union[str, float], min_val: Union[str, float], max_val: Union[str, float]) -> int:
        """Calculate percentage position within min-max range using clean frontmatter data"""
        try:
            # Convert all values to numeric - frontmatter provides clean data
            numeric_value = float(value)
            min_numeric = float(min_val)
            max_numeric = float(max_val)
            
            # Avoid division by zero
            if max_numeric <= min_numeric:
                return 50
                
            # Calculate percentage
            percentage = ((numeric_value - min_numeric) / (max_numeric - min_numeric)) * 100
            return max(0, min(100, int(percentage)))
            
        except Exception as e:
            logger.warning(f"Percentage calculation failed for value '{value}' in range '{min_val}'-'{max_val}': {e}")
            return 50  # Default to middle

    def _extract_table_categories(self, frontmatter_data: Dict) -> list:
        """Get list of categories that would be generated from available frontmatter data"""
        categories = []
        
        # Check each category based on available frontmatter sections
        if frontmatter_data.get('chemicalProperties') or frontmatter_data.get('composition'):
            categories.append('Chemical Properties')
        
        if frontmatter_data.get('machineSettings'):
            categories.append('Laser Processing Parameters')
        
        if frontmatter_data.get('applications'):
            categories.append('Applications & Industries')
        
        if frontmatter_data.get('outcomes'):
            categories.append('Performance Metrics')
        
        if frontmatter_data.get('environmentalImpact'):
            categories.append('Environmental Impact')
        
        if frontmatter_data.get('compatibility') or frontmatter_data.get('regulatoryStandards'):
            categories.append('Compatibility & Standards')
        
        return categories

# Legacy compatibility
class TableGenerator:
    """Legacy table generator for backward compatibility"""

    def __init__(self):
        self.generator = TableComponentGenerator()

    def generate(self, material: str, material_data: Dict = None, frontmatter_data: Dict = None) -> str:
        """Legacy generate method"""
        if material_data is None:
            material_data = {"name": material}

        result = self.generator.generate(
            material_name=material,
            material_data=material_data,
            frontmatter_data=frontmatter_data
        )

        if result.success:
            return result.content
        else:
            return f"Error generating table content: {result.error_message}"

    def get_component_info(self) -> Dict[str, Any]:
        """Get component information"""
        return {
            "name": "table",
            "description": "YAML tables from frontmatter data",
            "version": "3.0.0",
            "requires_api": False,
            "type": "frontmatter-based",
        }


def generate_table_content(material: str, material_data: Dict = None, frontmatter_data: Dict = None) -> str:
    """Legacy function for backward compatibility"""
    generator = TableGenerator()
    return generator.generate(material, material_data, frontmatter_data)


if __name__ == "__main__":
    # Test the generator with mock frontmatter data
    generator = TableGenerator()
    mock_frontmatter = {
        'properties': {
            'density': '8.96 g/cm³',
            'densityMin': '0.9 g/cm³', 
            'densityMax': '22 g/cm³',
            'densityPercentile': 85.0,
            'meltingPoint': '1085°C',
            'thermalConductivity': '401 W/m·K',
            'tensileStrength': '210 MPa',
            'laserType': 'Pulsed Fiber Laser',
            'wavelength': '1064nm',
            'fluenceRange': '0.5-5 J/cm²'
        },
        'chemicalProperties': {
            'formula': 'Cu'
        }
    }
    
    test_content = generator.generate("Copper", frontmatter_data=mock_frontmatter)
    print("🧪 Table Component Test:")
    print("=" * 50)
    print(test_content)
