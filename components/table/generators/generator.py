#!/usr/bin/env python3
"""
Table Component Generator

Generates deterministic YAML tables from frontmatter data.
No API requests needed - processes frontmatter directly.
Follows fail-fast architecture with no fallbacks.
"""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional

from generators.component_generators import StaticComponentGenerator
from utils.core.component_base import (
    handle_generation_error,
    validate_required_fields,
)


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

            # Extract properties from frontmatter - FAIL-FAST if insufficient data
            properties = frontmatter_data.get('properties', {})
            if not properties:
                raise Exception(f"ERROR: No table-appropriate data in frontmatter for {material_name}")

            # Generate deterministic YAML table content
            table_yaml = self._generate_yaml_tables(material_name, frontmatter_data)

            # Return YAML content without version stamping for now
            return table_yaml

        except Exception as e:
            raise Exception(f"Table generation failed for {material_name}: {str(e)}")

    def _generate_yaml_tables(self, material_name: str, frontmatter_data: Dict) -> str:
        """Generate YAML tables from frontmatter data following prompt.yaml specification"""
        properties = frontmatter_data.get('properties', {})
        
        # Group properties into categories based on materials science standards
        categorized_tables = []
        
        # Physical Properties
        physical_props = self._extract_physical_properties(properties)
        if physical_props:
            categorized_tables.append({
                'header': '## Physical Properties',
                'rows': physical_props
            })
        
        # Thermal Properties
        thermal_props = self._extract_thermal_properties(properties)
        if thermal_props:
            categorized_tables.append({
                'header': '## Thermal Properties', 
                'rows': thermal_props
            })
        
        # Mechanical Properties
        mechanical_props = self._extract_mechanical_properties(properties)
        if mechanical_props:
            categorized_tables.append({
                'header': '## Mechanical Properties',
                'rows': mechanical_props
            })
        
        # Optical Properties
        optical_props = self._extract_optical_properties(properties)
        if optical_props:
            categorized_tables.append({
                'header': '## Optical Properties',
                'rows': optical_props
            })
        
        # Laser Processing Parameters
        laser_props = self._extract_laser_properties(properties, frontmatter_data)
        if laser_props:
            categorized_tables.append({
                'header': '## Laser Processing Parameters',
                'rows': laser_props
            })
        
        # Composition (if chemical formula present)
        composition_props = self._extract_composition_properties(frontmatter_data)
        if composition_props:
            categorized_tables.append({
                'header': '## Composition',
                'rows': composition_props
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
                "<td dangerouslySetInnerHTML={{__html: htmlVisualization}} /></tr>. "
                "Use MDX for headers."
            )
        }
        
        return yaml.dump(yaml_data, default_flow_style=False, sort_keys=False)

    def _extract_physical_properties(self, properties: Dict) -> list:
        """Extract physical properties (density, melting point)"""
        rows = []
        
        # Density
        if 'density' in properties:
            rows.append(self._create_property_row(
                'Density', 
                properties['density'],
                properties.get('densityMin'),
                properties.get('densityMax'), 
                properties.get('densityPercentile'),
                'g/cm³'
            ))
        
        # Melting Point
        if 'meltingPoint' in properties:
            rows.append(self._create_property_row(
                'Melting Point',
                properties['meltingPoint'],
                properties.get('meltingMin'),
                properties.get('meltingMax'),
                properties.get('meltingPercentile'),
                '°C'
            ))
        
        return rows

    def _extract_thermal_properties(self, properties: Dict) -> list:
        """Extract thermal properties"""
        rows = []
        
        # Thermal Conductivity
        if 'thermalConductivity' in properties:
            rows.append(self._create_property_row(
                'Thermal Conductivity',
                properties['thermalConductivity'],
                properties.get('thermalMin'),
                properties.get('thermalMax'),
                properties.get('thermalPercentile'),
                'W/m·K'
            ))
        
        # Thermal Diffusivity (range only)
        if 'thermalDiffusivityMin' in properties and 'thermalDiffusivityMax' in properties:
            value_range = f"{properties['thermalDiffusivityMin']}-{properties['thermalDiffusivityMax']} mm²/s"
            rows.append(self._create_property_row(
                'Thermal Diffusivity',
                value_range,
                properties['thermalDiffusivityMin'],
                properties['thermalDiffusivityMax'],
                None,
                'mm²/s'
            ))
        
        # Thermal Expansion (range only)
        if 'thermalExpansionMin' in properties and 'thermalExpansionMax' in properties:
            value_range = f"{properties['thermalExpansionMin']}-{properties['thermalExpansionMax']} µm/m·K"
            rows.append(self._create_property_row(
                'Thermal Expansion',
                value_range,
                properties['thermalExpansionMin'],
                properties['thermalExpansionMax'],
                None,
                'µm/m·K'
            ))
        
        # Specific Heat (range only)
        if 'specificHeatMin' in properties and 'specificHeatMax' in properties:
            value_range = f"{properties['specificHeatMin']}-{properties['specificHeatMax']} J/g·K"
            rows.append(self._create_property_row(
                'Specific Heat',
                value_range,
                properties['specificHeatMin'],
                properties['specificHeatMax'],
                None,
                'J/g·K'
            ))
        
        return rows

    def _extract_mechanical_properties(self, properties: Dict) -> list:
        """Extract mechanical properties"""
        rows = []
        
        # Tensile Strength
        if 'tensileStrength' in properties:
            rows.append(self._create_property_row(
                'Tensile Strength',
                properties['tensileStrength'],
                properties.get('tensileMin'),
                properties.get('tensileMax'),
                properties.get('tensilePercentile'),
                'MPa'
            ))
        
        # Hardness
        if 'hardness' in properties:
            rows.append(self._create_property_row(
                'Hardness',
                properties['hardness'],
                properties.get('hardnessMin'),
                properties.get('hardnessMax'),
                properties.get('hardnessPercentile'),
                'HV'
            ))
        
        # Young's Modulus
        if 'youngsModulus' in properties:
            rows.append(self._create_property_row(
                "Young's Modulus",
                properties['youngsModulus'],
                properties.get('modulusMin'),
                properties.get('modulusMax'),
                properties.get('modulusPercentile'),
                'GPa'
            ))
        
        return rows

    def _extract_optical_properties(self, properties: Dict) -> list:
        """Extract optical properties"""
        rows = []
        
        # Laser Absorption (range only)
        if 'laserAbsorptionMin' in properties and 'laserAbsorptionMax' in properties:
            value_range = f"{properties['laserAbsorptionMin']}-{properties['laserAbsorptionMax']} cm⁻¹"
            rows.append(self._create_property_row(
                'Laser Absorption',
                value_range,
                properties['laserAbsorptionMin'],
                properties['laserAbsorptionMax'],
                None,
                'cm⁻¹'
            ))
        
        # Laser Reflectivity (range only)
        if 'laserReflectivityMin' in properties and 'laserReflectivityMax' in properties:
            value_range = f"{properties['laserReflectivityMin']}-{properties['laserReflectivityMax']}%"
            rows.append(self._create_property_row(
                'Laser Reflectivity',
                value_range,
                properties['laserReflectivityMin'],
                properties['laserReflectivityMax'],
                None,
                '%'
            ))
        
        return rows

    def _extract_laser_properties(self, properties: Dict, frontmatter_data: Dict) -> list:
        """Extract laser processing parameters"""
        rows = []
        
        # Laser Type
        if 'laserType' in properties:
            rows.append({
                'property': 'Laser Type',
                'value': properties['laserType'],
                'unit': '-',
                'htmlVisualization': '<span class="px-2 py-1 bg-blue-100 text-blue-800 rounded">Standard</span>'
            })
        
        # Wavelength
        if 'wavelength' in properties:
            rows.append({
                'property': 'Wavelength',
                'value': properties['wavelength'],
                'unit': 'nm',
                'htmlVisualization': '<span class="px-2 py-1 bg-green-100 text-green-800 rounded">Optimal</span>'
            })
        
        # Fluence Range
        if 'fluenceRange' in properties:
            rows.append({
                'property': 'Fluence Range',
                'value': properties['fluenceRange'],
                'unit': 'J/cm²',
                'htmlVisualization': '<div class="w-full bg-gray-200 rounded-full h-2"><div class="bg-orange-600 h-2 rounded-full" style="width: 75%"></div></div>'
            })
        
        return rows

    def _extract_composition_properties(self, frontmatter_data: Dict) -> list:
        """Extract composition properties if present"""
        rows = []
        
        chemical_props = frontmatter_data.get('chemicalProperties', {})
        if 'formula' in chemical_props:
            rows.append({
                'property': 'Chemical Formula',
                'value': chemical_props['formula'],
                'unit': '-',
                'htmlVisualization': '<span class="font-mono text-sm bg-gray-100 px-2 py-1 rounded">Chemical</span>'
            })
        
        return rows

    def _create_property_row(self, property_name: str, value: str, min_val: Optional[str], 
                           max_val: Optional[str], percentile: Optional[float], unit: str) -> Dict:
        """Create a standardized property row with visualization"""
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
        
        # Generate HTML visualization
        if min_val and max_val and value:
            percentage = self._calculate_percentage(value, min_val, max_val)
            row['htmlVisualization'] = (
                f'<div class="w-full bg-gray-200 rounded-full h-2">'
                f'<div class="bg-blue-600 h-2 rounded-full" style="width: {percentage}%"></div></div>'
                f'<p class="text-xs text-center">Value at {percentage}% of range</p>'
            )
        else:
            row['htmlVisualization'] = '<span class="text-gray-500">-</span>'
        
        return row

    def _calculate_percentage(self, value: str, min_val: str, max_val: str) -> int:
        """Calculate percentage position within min-max range"""
        try:
            # Extract numeric value (handle ranges like "2.7-3.0")
            if '-' in str(value) and '°C' not in str(value):
                # Handle ranges by taking midpoint
                parts = str(value).split('-')
                if len(parts) == 2:
                    val1 = float(''.join(c for c in parts[0] if c.replace('.', '').isdigit()))
                    val2 = float(''.join(c for c in parts[1] if c.replace('.', '').isdigit()))
                    numeric_value = (val1 + val2) / 2
                else:
                    numeric_value = float(''.join(c for c in str(value) if c.replace('.', '').isdigit()))
            else:
                numeric_value = float(''.join(c for c in str(value) if c.replace('.', '').isdigit()))
            
            min_numeric = float(''.join(c for c in str(min_val) if c.replace('.', '').isdigit()))
            max_numeric = float(''.join(c for c in str(max_val) if c.replace('.', '').isdigit()))
            
            if max_numeric <= min_numeric:
                return 50
            
            percentage = ((numeric_value - min_numeric) / (max_numeric - min_numeric)) * 100
            return max(0, min(100, int(percentage)))
        except:
            return 50  # Default to middle if calculation fails

    def _extract_table_categories(self, properties: Dict) -> list:
        """Get list of categories that would be generated"""
        categories = []
        
        # Check each category
        if any(key in properties for key in ['density', 'meltingPoint']):
            categories.append('Physical Properties')
        
        if any(key in properties for key in ['thermalConductivity', 'thermalDiffusivityMin', 'thermalExpansionMin', 'specificHeatMin']):
            categories.append('Thermal Properties')
        
        if any(key in properties for key in ['tensileStrength', 'hardness', 'youngsModulus']):
            categories.append('Mechanical Properties')
        
        if any(key in properties for key in ['laserAbsorptionMin', 'laserReflectivityMin']):
            categories.append('Optical Properties')
        
        if any(key in properties for key in ['laserType', 'wavelength', 'fluenceRange']):
            categories.append('Laser Processing Parameters')
        
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
