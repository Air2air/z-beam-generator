#!/usr/bin/env python3
"""
Materials.yaml Enhanced Frontmatter Mapper

Additive enhancement to leverage rich materials.yaml data for frontmatter generation
while reducing AI dependency and preserving existing functionality.

APPROACH: Additive enhancement - no destructive changes to existing system.
"""

import logging
from typing import Dict, Optional, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


class MaterialsYamlFrontmatterMapper:
    """
    Enhanced mapper to leverage rich materials.yaml data for comprehensive frontmatter generation.
    
    DESIGN PRINCIPLES:
    1. Additive only - preserves existing functionality
    2. Rich data prioritization - uses materials.yaml comprehensive data first
    3. AI supplemental - AI only for gaps materials.yaml can't fill
    4. Zero breaking changes - existing code continues to work
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def map_materials_to_comprehensive_frontmatter(self, material_data: Dict, material_name: str) -> Dict:
        """
        Create comprehensive frontmatter from rich materials.yaml data with PROPER ORGANIZATION.
        
        Fixed to extract ALL available properties and organize sections logically:
        1. Core identification (name, category, title, etc.)
        2. Content metadata (description, keywords, etc.)  
        3. Technical properties (ALL physical/mechanical properties)
        4. Machine settings (ALL 11+ parameters)
        5. Chemical properties
        6. Applications & compatibility
        7. Regulatory & safety
        8. Derived laser interaction properties
        """
        self.logger.info(f"🏗️ Mapping comprehensive frontmatter from materials.yaml for {material_name}")
        
        # Build frontmatter in LOGICAL ORDER
        ordered_frontmatter = {}
        
        # 1. CORE IDENTIFICATION - Always first
        core_data = self._map_core_identification(material_data, material_name)
        ordered_frontmatter.update(core_data)
        
        # 2. CONTENT METADATA - Description, keywords, etc.
        content_data = self._generate_content_metadata(material_data, material_name)
        ordered_frontmatter.update(content_data)
        
        # 3. TECHNICAL PROPERTIES - All physical/mechanical properties
        tech_properties = self._map_technical_properties(material_data)
        if tech_properties:
            ordered_frontmatter['technicalProperties'] = tech_properties
        
        # 4. MACHINE SETTINGS - All laser parameters
        machine_settings = self._map_enhanced_machine_settings(material_data)
        if machine_settings:
            ordered_frontmatter['machineSettings'] = machine_settings
        
        # 5. CHEMICAL PROPERTIES - Formula, composition, etc.
        if self._has_chemical_data(material_data):
            ordered_frontmatter['chemicalProperties'] = self._map_chemical_properties(material_data)
        
        # 6. APPLICATIONS & INDUSTRY
        apps_data = self._map_applications_and_industry(material_data)
        ordered_frontmatter.update(apps_data)
        
        # 7. COMPATIBILITY & REGULATORY
        compat_data = self._map_compatibility_regulatory(material_data)
        ordered_frontmatter.update(compat_data)
        
        # 8. LASER INTERACTION - Derived properties
        laser_interaction = self._derive_laser_interaction_properties(material_data)
        if laser_interaction:
            ordered_frontmatter['laserInteraction'] = laser_interaction
        
        self.logger.info(f"✅ Generated comprehensive frontmatter with {len(ordered_frontmatter)} sections from materials.yaml")
        return ordered_frontmatter
    
    def _map_core_identification(self, material_data: Dict, material_name: str) -> Dict:
        """Map core identification fields."""
        return {
            'name': material_data.get('name', material_name),
            'category': material_data.get('category', 'unknown'),
            'complexity': material_data.get('complexity', 'medium'),
            'difficulty_score': material_data.get('difficulty_score', 3),
            'author_id': material_data.get('author_id', 1)
        }
    
    def _generate_content_metadata(self, material_data: Dict, material_name: str) -> Dict:
        """
        Generate content metadata using materials.yaml data with minimal AI dependency.
        Uses structured templates based on material category and properties.
        """
        category = material_data.get('category', 'material')
        formula = material_data.get('formula', '')
        
        # Generate structured title and description from materials data
        title = f"Laser Cleaning {material_name}"
        
        # Create headline from category and key properties
        key_properties = []
        if 'density' in material_data:
            key_properties.append(f"density {material_data['density']}")
        if 'machine_settings' in material_data:
            wavelength = material_data['machine_settings'].get('wavelength_optimal', '')
            if wavelength:
                key_properties.append(f"optimized for {wavelength}")
        
        headline = f"Comprehensive laser cleaning guide for {category} {material_name.lower()}"
        if key_properties:
            headline += f" featuring {', '.join(key_properties[:2])}"
        
        # Generate description from available technical data
        description_parts = [
            f"Technical overview of {material_name}",
            f"({formula})" if formula else "",
            f"for laser cleaning applications"
        ]
        
        # Add key technical highlights
        if 'machine_settings' in material_data:
            ms = material_data['machine_settings']
            if 'wavelength_optimal' in ms:
                description_parts.append(f"including optimal {ms['wavelength_optimal']} wavelength interaction")
        
        # Add application context
        applications = material_data.get('applications', [])
        if applications and len(applications) > 0:
            primary_industry = applications[0].split(':')[0] if ':' in applications[0] else 'industrial'
            description_parts.append(f"and {primary_industry.lower()} applications")
        
        description = ", ".join([part for part in description_parts if part])
        
        # Generate keywords from structured data
        keywords = self._generate_keywords_from_data(material_data, material_name)
        
        return {
            'title': title,
            'headline': headline,
            'description': description,
            'keywords': keywords
        }
    
    def _map_technical_properties(self, material_data: Dict) -> Dict:
        """
        Map comprehensive technical properties from materials.yaml rich data.
        Fixed to match actual materials.yaml field names and extract ALL available properties.
        """
        properties = {}
        
        # CORRECTED: Physical properties with exact materials.yaml field names
        physical_mappings = {
            # Core physical properties
            'density': {'key': 'density', 'default_unit': 'g/cm³'},
            'thermal_conductivity': {'key': 'thermalConductivity', 'default_unit': 'W/m·K'},  # Fixed field name
            'thermal_expansion': {'key': 'thermalExpansion', 'default_unit': '/°C'},
            'hardness': {'key': 'hardness', 'default_unit': 'various'},
            'tensile_strength': {'key': 'tensileStrength', 'default_unit': 'MPa'},  # Fixed field name
            'youngs_modulus': {'key': 'youngsModulus', 'default_unit': 'GPa'},  # Fixed field name
            'compressive_strength': {'key': 'compressiveStrength', 'default_unit': 'MPa'},
            'flexural_strength': {'key': 'flexuralStrength', 'default_unit': 'MPa'},
            'specific_heat': {'key': 'specificHeat', 'default_unit': 'J/g·K'},
            'electrical_resistivity': {'key': 'electricalResistivity', 'default_unit': 'Ω·m'},  # Fixed field name
            'melting_point': {'key': 'meltingPoint', 'default_unit': '°C'},
            'operating_temperature': {'key': 'operatingTemperature', 'default_unit': '°C'},
            # Additional thermal properties
            'thermal_diffusivity': {'key': 'thermalDiffusivity', 'default_unit': 'm²/s'},
            'thermal_shock_resistance': {'key': 'thermalShockResistance', 'default_unit': 'various'},
            # Mechanical properties
            'elastic_modulus': {'key': 'elasticModulus', 'default_unit': 'GPa'},
            'poisson_ratio': {'key': 'poissonRatio', 'default_unit': 'dimensionless'},
            'yield_strength': {'key': 'yieldStrength', 'default_unit': 'MPa'},
            'ultimate_strength': {'key': 'ultimateStrength', 'default_unit': 'MPa'},
            'fatigue_strength': {'key': 'fatigueStrength', 'default_unit': 'MPa'},
            'fracture_toughness': {'key': 'fractureToughness', 'default_unit': 'MPa·m^0.5'}
        }
        
        for yaml_key, config in physical_mappings.items():
            if yaml_key in material_data:
                value = material_data[yaml_key]
                properties[config['key']] = self._format_property_value(value, config['default_unit'])
        
        # Specialized properties
        specialized_mappings = {
            'porosity': 'porosity',
            'moisture_content': 'moistureContent', 
            'resin_content': 'resinContent',
            'tannin_content': 'tanninContent',
            'water_absorption': 'waterAbsorption',
            'crystal_structure': 'crystalStructure',
            'grain_structure_type': 'grainStructure',
            'bandgap': 'bandgap',
            'dielectric_constant': 'dielectricConstant',
            'magnetic_properties': 'magneticProperties',
            'corrosion_resistance': 'corrosionResistance',
            'biocompatibility': 'biocompatibility'
        }
        
        for yaml_key, prop_key in specialized_mappings.items():
            if yaml_key in material_data:
                properties[prop_key] = material_data[yaml_key]
        
        return properties
    
    def _map_enhanced_machine_settings(self, material_data: Dict) -> Dict:
        """
        Map comprehensive machine settings from materials.yaml machine_settings section.
        Provides all 11 laser parameters with proper formatting.
        """
        if 'machine_settings' not in material_data:
            return {}
        
        ms = material_data['machine_settings']
        machine_settings = {}
        
        # Direct mappings with enhanced formatting
        setting_mappings = {
            'fluence_threshold': 'fluenceThreshold',
            'pulse_duration': 'pulseDuration', 
            'wavelength_optimal': 'wavelengthOptimal',
            'power_range': 'powerRange',
            'repetition_rate': 'repetitionRate',
            'spot_size': 'spotSize',
            'laser_type': 'laserType',
            'ablation_threshold': 'ablationThreshold',
            'thermal_damage_threshold': 'thermalDamageThreshold',
            'processing_speed': 'processingSpeed',
            'surface_roughness_change': 'surfaceRoughnessChange'
        }
        
        for yaml_key, setting_key in setting_mappings.items():
            if yaml_key in ms:
                value = ms[yaml_key]
                machine_settings[setting_key] = value
                
                # Add numeric extraction for computational use
                if self._contains_numeric_range(value):
                    numeric_info = self._extract_numeric_info(value)
                    machine_settings[f"{setting_key}Numeric"] = numeric_info
        
        # Add derived settings
        if 'power_range' in ms:
            power_value = ms['power_range']
            if '–' in power_value or '-' in power_value:
                try:
                    # Extract min and max power
                    power_clean = power_value.replace('W', '').replace(' ', '')
                    if '–' in power_clean:
                        min_power, max_power = power_clean.split('–')
                    else:
                        min_power, max_power = power_clean.split('-')
                    
                    machine_settings['powerRangeMin'] = f"{min_power}W"
                    machine_settings['powerRangeMax'] = f"{max_power}W"
                    machine_settings['powerRangeMinNumeric'] = float(min_power)
                    machine_settings['powerRangeMaxNumeric'] = float(max_power)
                except:
                    pass
        
        return machine_settings
    
    def _map_chemical_properties(self, material_data: Dict) -> Dict:
        """Map chemical properties section from materials.yaml chemical data."""
        chemical_props = {}
        
        # Basic chemical identifiers
        if 'formula' in material_data:
            chemical_props['formula'] = material_data['formula']
            chemical_props['chemicalFormula'] = material_data['formula']
        
        if 'symbol' in material_data:
            chemical_props['symbol'] = material_data['symbol']
        
        if 'composition' in material_data:
            chemical_props['composition'] = material_data['composition']
        
        # Specialized chemical properties
        chemical_mappings = {
            'chemical_resistance': 'chemicalResistance',
            'ionic_conductivity': 'ionicConductivity',
            'antimicrobial_properties': 'antimicrobialProperties',
            'common_alloys': 'commonAlloys',
            'chromium_content': 'chromiumContent',
            'nickel_content': 'nickelContent',
            'natural_oils': 'naturalOils'
        }
        
        for yaml_key, prop_key in chemical_mappings.items():
            if yaml_key in material_data:
                chemical_props[prop_key] = material_data[yaml_key]
        
        return chemical_props
    
    def _map_applications_and_industry(self, material_data: Dict) -> Dict:
        """Map applications and industry data from structured materials.yaml data."""
        result = {}
        
        # Applications from structured list
        if 'applications' in material_data:
            applications = material_data['applications']
            result['applications'] = applications
            
            # Extract primary industries from applications
            industries = []
            for app in applications:
                if ':' in app:
                    industry = app.split(':')[0].strip()
                    if industry not in industries:
                        industries.append(industry)
            
            if industries:
                result['primaryIndustries'] = industries
        
        # Industry tags
        if 'industry_tags' in material_data:
            result['industryTags'] = material_data['industry_tags']
        
        return result
    
    def _map_compatibility_regulatory(self, material_data: Dict) -> Dict:
        """Map compatibility and regulatory data from materials.yaml standards."""
        result = {}
        
        # Regulatory standards
        if 'regulatory_standards' in material_data:
            result['regulatoryStandards'] = material_data['regulatory_standards']
        
        # Compatibility information
        if 'compatibility' in material_data:
            compatibility = material_data['compatibility']
            result['compatibility'] = compatibility
            
            # Extract laser types for easy access
            if 'laser_types' in compatibility:
                result['compatibleLaserTypes'] = compatibility['laser_types']
        
        return result
    
    def _derive_laser_interaction_properties(self, material_data: Dict) -> Dict:
        """
        Derive laser interaction properties from machine_settings and physical properties.
        This reduces AI dependency by calculating laser-material interactions from data.
        """
        interaction = {}
        
        if 'machine_settings' not in material_data:
            return interaction
        
        ms = material_data['machine_settings']
        
        # Absorption characteristics from wavelength and material properties
        if 'wavelength_optimal' in ms:
            wavelength = ms['wavelength_optimal']
            interaction['optimalWavelength'] = wavelength
            
            # Derive absorption characteristics based on wavelength and material category
            category = material_data.get('category', '')
            if wavelength == '1064nm':
                if category in ['metal', 'semiconductor']:
                    interaction['absorptionCharacteristic'] = 'High absorption, excellent for conductive materials'
                elif category in ['ceramic', 'glass']:
                    interaction['absorptionCharacteristic'] = 'Moderate absorption, suitable for precise cleaning'
                else:
                    interaction['absorptionCharacteristic'] = 'Material-dependent absorption'
        
        # Thermal characteristics from thermal properties
        if 'thermal_conductivity' in material_data:
            tc = material_data['thermal_conductivity']
            interaction['thermalConductivity'] = tc
            
            # Derive thermal response characteristics
            if 'W/m·K' in str(tc):
                try:
                    # Extract numeric value for analysis
                    tc_numeric = float(str(tc).split('W/m·K')[0].split('-')[-1].strip())
                    if tc_numeric > 100:
                        interaction['thermalResponse'] = 'Rapid heat dissipation, requires higher power settings'
                    elif tc_numeric > 10:
                        interaction['thermalResponse'] = 'Moderate heat dissipation, standard power settings'
                    else:
                        interaction['thermalResponse'] = 'Low heat dissipation, careful power control needed'
                except:
                    pass
        
        # Processing characteristics from machine settings
        if 'processing_speed' in ms and 'ablation_threshold' in ms:
            interaction['processingEfficiency'] = {
                'speed': ms['processing_speed'],
                'threshold': ms['ablation_threshold']
            }
        
        return interaction
    
    # === Utility Methods ===
    
    def _has_chemical_data(self, material_data: Dict) -> bool:
        """Check if material has sufficient chemical data for chemical properties section."""
        chemical_fields = ['formula', 'symbol', 'composition', 'chemical_resistance', 
                          'ionic_conductivity', 'common_alloys']
        return any(field in material_data for field in chemical_fields)
    
    def _format_property_value(self, value: Any, default_unit: str) -> Dict:
        """Format property value with proper units and numeric extraction."""
        if isinstance(value, (int, float)):
            return {
                'value': value,
                'unit': default_unit,
                'numeric': value
            }
        elif isinstance(value, str):
            return {
                'value': value,
                'unit': self._extract_unit(value) or default_unit,
                'numeric': self._extract_numeric_value(value)
            }
        else:
            return {'value': value}
    
    def _contains_numeric_range(self, value: str) -> bool:
        """Check if value contains numeric range."""
        if not isinstance(value, str):
            return False
        return any(sep in value for sep in ['–', '-', 'to', '±'])
    
    def _extract_numeric_info(self, value: str) -> Dict:
        """Extract numeric information from range strings."""
        try:
            # Handle different range formats
            if '–' in value:
                parts = value.split('–')
            elif '-' in value and not value.startswith('-'):
                parts = value.split('-')
            else:
                return {'value': value}
            
            if len(parts) == 2:
                min_val = float(''.join(filter(str.isdigit or '.'.__eq__, parts[0])))
                max_val = float(''.join(filter(str.isdigit or '.'.__eq__, parts[1])))
                return {
                    'min': min_val,
                    'max': max_val,
                    'average': (min_val + max_val) / 2
                }
        except:
            pass
        
        return {'value': value}
    
    def _extract_unit(self, value: str) -> Optional[str]:
        """Extract unit from value string."""
        common_units = ['W', 'Hz', 'mm', 'nm', 'ns', 'J/cm²', 'MPa', 'GPa', 'g/cm³', 'W/m·K', '°C', '%']
        for unit in common_units:
            if unit in value:
                return unit
        return None
    
    def _extract_numeric_value(self, value: str) -> Optional[float]:
        """Extract first numeric value from string."""
        try:
            import re
            numbers = re.findall(r'\d+\.?\d*', value)
            if numbers:
                return float(numbers[0])
        except:
            pass
        return None
    
    def _generate_keywords_from_data(self, material_data: Dict, material_name: str) -> str:
        """Generate keywords from structured material data instead of using AI."""
        keywords = [material_name.lower(), f"{material_name.lower()} {material_data.get('category', 'material')}"]
        
        # Add laser-specific terms
        keywords.extend(['laser ablation', 'laser cleaning', 'non-contact cleaning'])
        
        # Add from machine settings
        if 'machine_settings' in material_data:
            ms = material_data['machine_settings']
            if 'laser_type' in ms:
                laser_type = ms['laser_type'].lower()
                keywords.append(laser_type)
            if 'wavelength_optimal' in ms:
                keywords.append(f"{ms['wavelength_optimal']} wavelength")
        
        # Add from applications
        applications = material_data.get('applications', [])
        for app in applications[:2]:  # First 2 applications
            if ':' in app:
                industry = app.split(':')[0].strip().lower()
                keywords.append(f"{industry} applications")
        
        # Add technical terms
        technical_terms = ['surface contamination removal', 'industrial laser parameters', 
                          'thermal processing', 'surface restoration']
        keywords.extend(technical_terms[:2])
        
        return ', '.join(keywords)


# === Integration Helper ===

def enhance_frontmatter_with_materials_data(
    existing_frontmatter: Dict, 
    material_data: Dict, 
    material_name: str
) -> Dict:
    """
    ADDITIVE enhancement function - enhances existing frontmatter with rich materials.yaml data.
    
    This function preserves ALL existing frontmatter content while adding rich materials.yaml data.
    No breaking changes - existing functionality continues to work unchanged.
    """
    mapper = MaterialsYamlFrontmatterMapper()
    enhanced_data = mapper.map_materials_to_comprehensive_frontmatter(material_data, material_name)
    
    # Merge enhanced data into existing frontmatter (existing takes precedence)
    result = enhanced_data.copy()
    result.update(existing_frontmatter)  # Existing frontmatter overrides enhanced data
    
    # Add materials.yaml enhancement metadata
    result['dataSource'] = {
        'materialsYaml': True,
        'aiSupplemental': 'api_client' in existing_frontmatter,
        'enhancementLevel': 'comprehensive'
    }
    
    return result


if __name__ == "__main__":
    # Example usage demonstration
    print("🚀 Materials.yaml Enhanced Frontmatter Mapper")
    print("=" * 50)
    
    # Load sample material for demonstration
    import yaml
    with open('data/materials.yaml', 'r') as f:
        data = yaml.safe_load(f)
    
    # Find Steel material
    steel_data = None
    for cat_data in data['materials'].values():
        if 'items' in cat_data:
            for item in cat_data['items']:
                if item['name'] == 'Steel':
                    steel_data = item
                    break
    
    if steel_data:
        mapper = MaterialsYamlFrontmatterMapper()
        enhanced_frontmatter = mapper.map_materials_to_comprehensive_frontmatter(steel_data, 'Steel')
        
        print(f"✅ Generated comprehensive frontmatter with {len(enhanced_frontmatter)} sections")
        print(f"📊 Sections: {list(enhanced_frontmatter.keys())}")
        
        if 'machineSettings' in enhanced_frontmatter:
            ms = enhanced_frontmatter['machineSettings']
            print(f"🔧 Machine Settings: {len(ms)} parameters mapped from materials.yaml")
    
    print("\n💡 This additive approach reduces AI dependency while preserving existing functionality!")
