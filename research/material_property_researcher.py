#!/usr/bin/env python3
"""
Material Property Research System

Implements three-step material property research:
1. Research scientific property fields commonly used for specific materials
2. Research machine settings fields commonly used for specific materials  
3. Research field keys for values found in metrics schemas

This system enhances material-specific property generation with research-backed data.
"""

import sys
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data.materials import get_material_by_name, load_materials


@dataclass
class PropertyResearch:
    """Research data for a specific property"""
    field_key: str
    common_name: str
    units: List[str]
    typical_range: Optional[Dict[str, float]]
    laser_relevance_score: float
    material_categories: List[str]
    description: str
    research_priority: int  # 1=critical, 2=important, 3=useful


@dataclass 
class MachineSettingResearch:
    """Research data for a machine setting"""
    field_key: str
    parameter_name: str
    units: List[str]
    typical_range: Optional[Dict[str, float]]
    material_dependency: float  # How much this varies by material (0.0-1.0)
    laser_types: List[str]  # Which laser types use this parameter
    description: str
    optimization_priority: int  # 1=critical, 2=important, 3=fine-tuning


@dataclass
class MaterialResearchProfile:
    """Complete research profile for a material category"""
    category: str
    subcategories: List[str]
    scientific_properties: List[PropertyResearch]
    machine_settings: List[MachineSettingResearch]
    special_considerations: List[str]


class MaterialPropertyResearcher:
    """Researches and provides material-specific property and machine setting recommendations"""
    
    def __init__(self):
        self.materials_data = load_materials()
        self.research_profiles = self._initialize_research_profiles()
        self.schema_fields = self._load_schema_fields()
        
    def _initialize_research_profiles(self) -> Dict[str, MaterialResearchProfile]:
        """Initialize research profiles for different material categories"""
        profiles = {}
        
        # Metal research profile
        profiles['metal'] = MaterialResearchProfile(
            category='metal',
            subcategories=['ferrous', 'non-ferrous', 'alloy', 'precious'],
            scientific_properties=[
                PropertyResearch(
                    field_key='density',
                    common_name='Density',
                    units=['g/cm³', 'kg/m³'],
                    typical_range={'min': 0.5, 'max': 22.6},  # Li to Os
                    laser_relevance_score=0.9,
                    material_categories=['metal'],
                    description='Mass per unit volume - critical for laser absorption calculations',
                    research_priority=1
                ),
                PropertyResearch(
                    field_key='thermal_conductivity',
                    common_name='Thermal Conductivity',
                    units=['W/m·K'],
                    typical_range={'min': 1.0, 'max': 429.0},  # Steel to Silver
                    laser_relevance_score=0.95,
                    material_categories=['metal'],
                    description='Heat conduction efficiency - affects processing temperature distribution',
                    research_priority=1
                ),
                PropertyResearch(
                    field_key='melting_point',
                    common_name='Melting Point',
                    units=['°C', 'K'],
                    typical_range={'min': 29.8, 'max': 3422.0},  # Ga to W
                    laser_relevance_score=0.98,
                    material_categories=['metal'],
                    description='Temperature at which material transitions to liquid state',
                    research_priority=1
                ),
                PropertyResearch(
                    field_key='specific_heat',
                    common_name='Specific Heat Capacity',
                    units=['J/g·K', 'J/kg·K'],
                    typical_range={'min': 0.1, 'max': 4.2},
                    laser_relevance_score=0.85,
                    material_categories=['metal'],
                    description='Heat capacity per unit mass - affects temperature rise rate',
                    research_priority=1
                ),
                PropertyResearch(
                    field_key='laser_absorption',
                    common_name='Laser Absorption Coefficient',
                    units=['cm⁻¹', 'm⁻¹'],
                    typical_range={'min': 0.01, 'max': 1000.0},
                    laser_relevance_score=1.0,
                    material_categories=['metal'],
                    description='Material-specific laser energy absorption rate',
                    research_priority=1
                ),
                PropertyResearch(
                    field_key='reflectivity',
                    common_name='Surface Reflectivity',
                    units=['%', 'fraction'],
                    typical_range={'min': 0.05, 'max': 0.98},
                    laser_relevance_score=0.95,
                    material_categories=['metal'],
                    description='Percentage of incident laser light reflected from surface',
                    research_priority=1
                ),
                PropertyResearch(
                    field_key='thermal_diffusivity',
                    common_name='Thermal Diffusivity',
                    units=['mm²/s', 'm²/s'],
                    typical_range={'min': 1.0, 'max': 174.0},
                    laser_relevance_score=0.8,
                    material_categories=['metal'],
                    description='Rate of temperature change through material thickness',
                    research_priority=2
                ),
                PropertyResearch(
                    field_key='thermal_expansion',
                    common_name='Coefficient of Thermal Expansion',
                    units=['µm/m·K', '1/K'],
                    typical_range={'min': 0.5, 'max': 25.0},
                    laser_relevance_score=0.7,
                    material_categories=['metal'],
                    description='Material dimensional change per unit temperature change',
                    research_priority=2
                ),
                PropertyResearch(
                    field_key='electrical_conductivity',
                    common_name='Electrical Conductivity',
                    units=['S/m', 'MS/m'],
                    typical_range={'min': 1e-8, 'max': 63.0},
                    laser_relevance_score=0.6,
                    material_categories=['metal'],
                    description='Ability to conduct electric current - relates to laser coupling',
                    research_priority=3
                )
            ],
            machine_settings=[
                MachineSettingResearch(
                    field_key='laser_power',
                    parameter_name='Laser Power',
                    units=['W', 'kW'],
                    typical_range={'min': 10.0, 'max': 10000.0},
                    material_dependency=0.9,
                    laser_types=['fiber', 'CO2', 'diode', 'excimer'],
                    description='Average laser output power for processing',
                    optimization_priority=1
                ),
                MachineSettingResearch(
                    field_key='pulse_frequency',
                    parameter_name='Pulse Frequency',
                    units=['Hz', 'kHz'],
                    typical_range={'min': 1.0, 'max': 1000000.0},
                    material_dependency=0.8,
                    laser_types=['pulsed_fiber', 'Nd:YAG', 'excimer'],
                    description='Number of laser pulses per second',
                    optimization_priority=1
                ),
                MachineSettingResearch(
                    field_key='scan_speed',
                    parameter_name='Scanning Speed',
                    units=['mm/min', 'm/min', 'mm/s'],
                    typical_range={'min': 10.0, 'max': 50000.0},
                    material_dependency=0.85,
                    laser_types=['all'],
                    description='Speed of laser beam movement across surface',
                    optimization_priority=1
                ),
                MachineSettingResearch(
                    field_key='fluence',
                    parameter_name='Laser Fluence',
                    units=['J/cm²', 'mJ/cm²'],
                    typical_range={'min': 0.001, 'max': 100.0},
                    material_dependency=0.95,
                    laser_types=['pulsed'],
                    description='Energy per unit area delivered per pulse',
                    optimization_priority=1
                ),
                MachineSettingResearch(
                    field_key='beam_diameter',
                    parameter_name='Beam Diameter',
                    units=['µm', 'mm'],
                    typical_range={'min': 10.0, 'max': 10000.0},
                    material_dependency=0.7,
                    laser_types=['all'],
                    description='Diameter of focused laser beam at material surface',
                    optimization_priority=2
                ),
                MachineSettingResearch(
                    field_key='overlap_percentage',
                    parameter_name='Pulse/Path Overlap',
                    units=['%'],
                    typical_range={'min': 0.0, 'max': 95.0},
                    material_dependency=0.6,
                    laser_types=['all'],
                    description='Percentage overlap between adjacent pulses or scan paths',
                    optimization_priority=2
                )
            ],
            special_considerations=[
                'Oxidation sensitivity during processing',
                'Heat-affected zone minimization',
                'Alloy composition variations affect processing parameters',
                'Surface finish impacts laser absorption',
                'Thermal stress management critical for dimensional stability'
            ]
        )
        
        # Add other material categories (ceramic, polymer, etc.)
        profiles.update(self._create_other_material_profiles())
        
        return profiles
    
    def _create_other_material_profiles(self) -> Dict[str, MaterialResearchProfile]:
        """Create research profiles for non-metal materials"""
        profiles = {}
        
        # Ceramic profile
        profiles['ceramic'] = MaterialResearchProfile(
            category='ceramic',
            subcategories=['oxide', 'carbide', 'nitride', 'composite'],
            scientific_properties=[
                PropertyResearch(
                    field_key='density',
                    common_name='Density',
                    units=['g/cm³'],
                    typical_range={'min': 1.8, 'max': 15.7},
                    laser_relevance_score=0.85,
                    material_categories=['ceramic'],
                    description='Mass per unit volume for ceramic materials',
                    research_priority=1
                ),
                PropertyResearch(
                    field_key='hardness',
                    common_name='Hardness (Mohs)',
                    units=['Mohs', 'HV', 'GPa'],
                    typical_range={'min': 6.0, 'max': 10.0},
                    laser_relevance_score=0.7,
                    material_categories=['ceramic'],
                    description='Resistance to scratching and abrasion',
                    research_priority=2
                ),
                PropertyResearch(
                    field_key='thermal_shock_resistance',
                    common_name='Thermal Shock Resistance',
                    units=['°C', 'K'],
                    typical_range={'min': 50.0, 'max': 1000.0},
                    laser_relevance_score=0.9,
                    material_categories=['ceramic'],
                    description='Ability to withstand rapid temperature changes',
                    research_priority=1
                )
            ],
            machine_settings=[
                MachineSettingResearch(
                    field_key='laser_power',
                    parameter_name='Laser Power',
                    units=['W'],
                    typical_range={'min': 50.0, 'max': 5000.0},
                    material_dependency=0.8,
                    laser_types=['CO2', 'fiber'],
                    description='Power requirements for ceramic processing',
                    optimization_priority=1
                )
            ],
            special_considerations=[
                'Thermal shock sensitivity requires gradual heating',
                'Microcracking can occur with aggressive parameters',
                'Surface contamination can affect laser coupling'
            ]
        )
        
        return profiles
    
    def _load_schema_fields(self) -> Dict[str, Any]:
        """Load field definitions from component schemas"""
        schema_fields = {}
        
        # Load frontmatter schema (contains all needed property definitions)
        frontmatter_path = project_root / 'schemas' / 'frontmatter.json'
        if frontmatter_path.exists():
            with open(frontmatter_path) as f:
                frontmatter_schema = json.load(f)
                # Extract property definitions from consolidated schema
                if 'properties' in frontmatter_schema and 'materialProperties' in frontmatter_schema['properties']:
                    schema_fields['properties'] = frontmatter_schema['properties']['materialProperties']
                if 'properties' in frontmatter_schema and 'machineSettings' in frontmatter_schema['properties']:
                    schema_fields['machine_settings'] = frontmatter_schema['properties']['machineSettings']
                
        return schema_fields
    
    def research_material_properties(self, material_name: str) -> Dict[str, Any]:
        """Step 1: Research scientific property fields for specific material"""
        # Get material data
        try:
            material_data = get_material_by_name(material_name)
            if not material_data:
                raise ValueError(f"Material '{material_name}' not found")
        except Exception as e:
            return {'error': str(e)}
        
        category = material_data.get('category', 'unknown')
        subcategory = material_data.get('subcategory', '')
        
        # Get research profile for this material category
        profile = self.research_profiles.get(category)
        if not profile:
            return {
                'material_name': material_name,
                'category': category,
                'error': f'No research profile available for category: {category}'
            }
        
        # Filter properties relevant to this specific material
        recommended_properties = []
        for prop in profile.scientific_properties:
            if self._is_property_relevant(prop, material_data, category, subcategory):
                recommended_properties.append({
                    'field_key': prop.field_key,
                    'common_name': prop.common_name,
                    'units': prop.units,
                    'typical_range': prop.typical_range,
                    'laser_relevance_score': prop.laser_relevance_score,
                    'description': prop.description,
                    'research_priority': prop.research_priority,
                    'current_value': material_data.get('properties', {}).get(prop.field_key)
                })
        
        return {
            'material_name': material_name,
            'category': category,
            'subcategory': subcategory,
            'recommended_properties': recommended_properties,
            'special_considerations': profile.special_considerations
        }
    
    def research_machine_settings(self, material_name: str) -> Dict[str, Any]:
        """Step 2: Research machine settings fields for specific material"""
        try:
            material_data = get_material_by_name(material_name)
            if not material_data:
                raise ValueError(f"Material '{material_name}' not found")
        except Exception as e:
            return {'error': str(e)}
        
        category = material_data.get('category', 'unknown')
        subcategory = material_data.get('subcategory', '')
        
        profile = self.research_profiles.get(category)
        if not profile:
            return {
                'material_name': material_name,
                'category': category,
                'error': f'No research profile available for category: {category}'
            }
        
        # Filter machine settings relevant to this material
        recommended_settings = []
        for setting in profile.machine_settings:
            if self._is_setting_relevant(setting, material_data, category, subcategory):
                # Calculate material-specific parameter ranges
                optimized_range = self._optimize_setting_range(setting, material_data)
                
                recommended_settings.append({
                    'field_key': setting.field_key,
                    'parameter_name': setting.parameter_name,
                    'units': setting.units,
                    'general_range': setting.typical_range,
                    'optimized_range': optimized_range,
                    'material_dependency': setting.material_dependency,
                    'laser_types': setting.laser_types,
                    'description': setting.description,
                    'optimization_priority': setting.optimization_priority
                })
        
        return {
            'material_name': material_name,
            'category': category,
            'subcategory': subcategory,
            'recommended_settings': recommended_settings
        }
    
    def get_recommended_machine_settings_for_material(self, material_name: str) -> Dict[str, Any]:
        """Get recommended machine settings for specific material - wrapper for research_machine_settings"""
        return self.research_machine_settings(material_name)
    
    def research_schema_field_values(self, field_key: str, material_name: str) -> Dict[str, Any]:
        """Step 3: Research field key values in schema context"""
        # Get current schema definition for this field
        schema_definition = self._get_schema_field_definition(field_key)
        
        # Get material-specific research for this field
        material_research = self._get_field_material_research(field_key, material_name)
        
        # Cross-reference with existing material data
        try:
            material_data = get_material_by_name(material_name)
            current_value = None
            if material_data:
                current_value = material_data.get('properties', {}).get(field_key)
                if not current_value:
                    current_value = material_data.get('machineSettings', {}).get(field_key)
        except Exception:
            current_value = None
        
        return {
            'field_key': field_key,
            'material_name': material_name,
            'schema_definition': schema_definition,
            'material_research': material_research,
            'current_value': current_value,
            'recommendations': self._generate_field_recommendations(
                field_key, material_name, schema_definition, material_research, current_value
            )
        }
    
    def _is_property_relevant(self, prop: PropertyResearch, material_data: Dict, 
                            category: str, subcategory: str) -> bool:
        """Check if a property is relevant for this specific material"""
        # Always include high-priority, high-relevance properties
        if prop.research_priority == 1 and prop.laser_relevance_score > 0.8:
            return True
        
        # Check category match
        if category not in prop.material_categories:
            return False
        
        # Material-specific logic can be added here
        return True
    
    def _is_setting_relevant(self, setting: MachineSettingResearch, material_data: Dict,
                           category: str, subcategory: str) -> bool:
        """Check if a machine setting is relevant for this material"""
        # Always include critical settings
        if setting.optimization_priority == 1:
            return True
            
        # Check if setting has high material dependency
        if setting.material_dependency > 0.7:
            return True
            
        return False
    
    def _optimize_setting_range(self, setting: MachineSettingResearch, 
                              material_data: Dict) -> Optional[Dict[str, float]]:
        """Calculate optimized parameter range for specific material"""
        if not setting.typical_range:
            return None
        
        # Get material properties that affect this setting
        properties = material_data.get('properties', {})
        
        # Basic optimization based on common material properties
        base_min = setting.typical_range['min']
        base_max = setting.typical_range['max']
        
        # Adjust for thermal properties if available
        if setting.field_key == 'laser_power':
            thermal_conductivity = properties.get('thermal_conductivity', {})
            if isinstance(thermal_conductivity, dict) and 'value' in thermal_conductivity:
                tc_value = thermal_conductivity['value']
                # Higher thermal conductivity materials may need more power
                if tc_value > 100:  # High TC
                    base_min *= 1.2
                    base_max *= 1.3
                elif tc_value < 10:  # Low TC
                    base_min *= 0.8
                    base_max *= 0.9
        
        return {'min': base_min, 'max': base_max}
    
    def _get_schema_field_definition(self, field_key: str) -> Optional[Dict]:
        """Get schema definition for a field"""
        # Check in properties schema
        if 'properties' in self.schema_fields:
            props_schema = self.schema_fields['properties']
            # Look in patternProperties for dynamic fields
            pattern_props = props_schema.get('properties', {}).get('materialProperties', {}).get('patternProperties', {})
            if pattern_props:
                for pattern, definition in pattern_props.items():
                    return definition
        
        # Check in machine settings schema
        if 'machine_settings' in self.schema_fields:
            machine_schema = self.schema_fields['machine_settings']
            pattern_props = machine_schema.get('properties', {}).get('machineSettings', {}).get('patternProperties', {})
            if pattern_props:
                for pattern, definition in pattern_props.items():
                    return definition
        
        return None
    
    def _get_field_material_research(self, field_key: str, material_name: str) -> Optional[Dict]:
        """Get research data for field-material combination"""
        try:
            material_data = get_material_by_name(material_name)
            if not material_data:
                return None
                
            category = material_data.get('category', 'unknown')
            profile = self.research_profiles.get(category)
            if not profile:
                return None
            
            # Search in properties
            for prop in profile.scientific_properties:
                if prop.field_key == field_key:
                    return {
                        'type': 'property',
                        'common_name': prop.common_name,
                        'units': prop.units,
                        'typical_range': prop.typical_range,
                        'laser_relevance_score': prop.laser_relevance_score,
                        'description': prop.description,
                        'research_priority': prop.research_priority
                    }
            
            # Search in machine settings
            for setting in profile.machine_settings:
                if setting.field_key == field_key:
                    return {
                        'type': 'machine_setting',
                        'parameter_name': setting.parameter_name,
                        'units': setting.units,
                        'typical_range': setting.typical_range,
                        'material_dependency': setting.material_dependency,
                        'laser_types': setting.laser_types,
                        'description': setting.description,
                        'optimization_priority': setting.optimization_priority
                    }
        except Exception:
            pass
            
        return None
    
    def _generate_field_recommendations(self, field_key: str, material_name: str,
                                      schema_def: Optional[Dict], material_research: Optional[Dict],
                                      current_value: Optional[Dict]) -> List[str]:
        """Generate recommendations for field improvement"""
        recommendations = []
        
        if not material_research:
            recommendations.append(f"No specific research data available for '{field_key}' in material category")
        
        if current_value is None:
            recommendations.append(f"Field '{field_key}' is missing - consider adding based on material research")
        elif isinstance(current_value, dict):
            # Check if current value is within recommended range
            if material_research and 'typical_range' in material_research:
                current_val = current_value.get('value')
                if current_val is not None:
                    range_data = material_research['typical_range']
                    if 'min' in range_data and current_val < range_data['min']:
                        recommendations.append(f"Current value {current_val} is below typical minimum {range_data['min']}")
                    elif 'max' in range_data and current_val > range_data['max']:
                        recommendations.append(f"Current value {current_val} is above typical maximum {range_data['max']}")
        
        if material_research:
            if material_research.get('type') == 'property':
                score = material_research.get('laser_relevance_score', 0)
                if score > 0.9:
                    recommendations.append("High laser processing relevance - ensure accurate values")
            elif material_research.get('type') == 'machine_setting':
                dependency = material_research.get('material_dependency', 0)
                if dependency > 0.8:
                    recommendations.append("High material dependency - optimize for this specific material")
        
        return recommendations
    
    def generate_comprehensive_research_report(self, material_name: str) -> Dict[str, Any]:
        """Generate a comprehensive research report combining all three steps"""
        # Step 1: Scientific properties research
        properties_research = self.research_material_properties(material_name)
        
        # Step 2: Machine settings research
        settings_research = self.research_machine_settings(material_name)
        
        # Step 3: Schema field analysis for key fields
        key_fields = []
        if 'recommended_properties' in properties_research:
            key_fields.extend([p['field_key'] for p in properties_research['recommended_properties'][:5]])
        if 'recommended_settings' in settings_research:
            key_fields.extend([s['field_key'] for s in settings_research['recommended_settings'][:5]])
        
        schema_analysis = {}
        for field_key in key_fields:
            schema_analysis[field_key] = self.research_schema_field_values(field_key, material_name)
        
        return {
            'material_name': material_name,
            'research_timestamp': 'generated',
            'step_1_properties': properties_research,
            'step_2_machine_settings': settings_research,
            'step_3_schema_analysis': schema_analysis,
            'summary': self._generate_research_summary(properties_research, settings_research, schema_analysis)
        }
    
    def _generate_research_summary(self, properties_research: Dict, settings_research: Dict, 
                                 schema_analysis: Dict) -> Dict[str, Any]:
        """Generate executive summary of research findings"""
        summary = {
            'critical_missing_properties': [],
            'critical_missing_settings': [],
            'optimization_opportunities': [],
            'data_quality_issues': []
        }
        
        # Analyze properties
        if 'recommended_properties' in properties_research:
            for prop in properties_research['recommended_properties']:
                if prop['research_priority'] == 1 and prop['current_value'] is None:
                    summary['critical_missing_properties'].append(prop['field_key'])
        
        # Analyze settings
        if 'recommended_settings' in settings_research:
            for setting in settings_research['recommended_settings']:
                if setting['optimization_priority'] == 1:
                    summary['optimization_opportunities'].append(setting['field_key'])
        
        # Analyze schema compliance
        for field_key, analysis in schema_analysis.items():
            if 'recommendations' in analysis:
                for rec in analysis['recommendations']:
                    if 'missing' in rec.lower():
                        if field_key not in summary['critical_missing_properties']:
                            summary['data_quality_issues'].append(f"{field_key}: {rec}")
        
        return summary


def main():
    """Command line interface for material research"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Material Property Research System')
    parser.add_argument('material', help='Material name to research')
    parser.add_argument('--step', type=int, choices=[1, 2, 3], 
                       help='Run specific research step only')
    parser.add_argument('--field', help='Research specific field (step 3)')
    parser.add_argument('--comprehensive', action='store_true',
                       help='Generate comprehensive research report')
    
    args = parser.parse_args()
    
    researcher = MaterialPropertyResearcher()
    
    if args.comprehensive:
        result = researcher.generate_comprehensive_research_report(args.material)
        print(json.dumps(result, indent=2))
    elif args.step == 1:
        result = researcher.research_material_properties(args.material)
        print(json.dumps(result, indent=2))
    elif args.step == 2:
        result = researcher.research_machine_settings(args.material)
        print(json.dumps(result, indent=2))
    elif args.step == 3:
        if not args.field:
            print("Error: --field required for step 3")
            sys.exit(1)
        result = researcher.research_schema_field_values(args.field, args.material)
        print(json.dumps(result, indent=2))
    else:
        # Default: run all steps
        result = researcher.generate_comprehensive_research_report(args.material)
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()