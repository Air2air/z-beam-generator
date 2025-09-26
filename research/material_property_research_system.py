#!/usr/bin/env python3
"""
Material Property Research System

Researches what material properties are commonly used for different material types.
Provides comprehensive property recommendations based on material category, 
industry standards, and laser processing relevance.
"""

import sys
import json
from typing import Dict, List, Any
from dataclasses import dataclass
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data.materials import load_materials


@dataclass
class PropertyDefinition:
    """Comprehensive definition of a material property"""
    name: str
    common_names: List[str]
    units: List[str]
    description: str
    laser_relevance: float  # 0.0-1.0
    industry_importance: float  # 0.0-1.0
    measurement_difficulty: float  # 0.0-1.0 (higher = harder to measure)
    material_categories: List[str]  # Which categories use this property
    typical_ranges: Dict[str, Dict[str, float]]  # Per category ranges
    related_properties: List[str]  # Properties that correlate with this one
    industry_standards: List[str]  # ASTM, ISO standards for measurement
    research_sources: List[str]


class MaterialPropertyResearchSystem:
    """Researches and recommends properties for different material types"""
    
    def __init__(self):
        self.materials_data = load_materials()
        self.property_definitions = self._initialize_property_definitions()
        self.category_property_maps = self._create_category_property_maps()
        
    def _initialize_property_definitions(self) -> Dict[str, PropertyDefinition]:
        """Initialize comprehensive property definitions for all material types"""
        
        properties = {}
        
        # === MECHANICAL PROPERTIES ===
        properties['density'] = PropertyDefinition(
            name='density',
            common_names=['Density', 'Mass Density', 'Bulk Density'],
            units=['g/cm³', 'kg/m³', 'lb/ft³'],
            description='Mass per unit volume - fundamental for laser absorption calculations',
            laser_relevance=0.95,
            industry_importance=0.98,
            measurement_difficulty=0.2,
            material_categories=['metal', 'ceramic', 'polymer', 'composite', 'stone', 'glass', 'wood'],
            typical_ranges={
                'metal': {'min': 0.534, 'max': 22.587},  # Li to Os
                'ceramic': {'min': 1.8, 'max': 15.7},
                'polymer': {'min': 0.85, 'max': 2.2},
                'composite': {'min': 0.5, 'max': 8.0},
                'stone': {'min': 1.5, 'max': 5.0},
                'glass': {'min': 2.0, 'max': 8.0},
                'wood': {'min': 0.3, 'max': 1.2}
            },
            related_properties=['specific_heat', 'thermal_conductivity'],
            industry_standards=['ASTM B311', 'ISO 3369', 'ASTM D792'],
            research_sources=['CRC Handbook', 'ASM Materials Database']
        )
        
        properties['tensile_strength'] = PropertyDefinition(
            name='tensile_strength',
            common_names=['Tensile Strength', 'Ultimate Tensile Strength', 'UTS'],
            units=['MPa', 'psi', 'ksi', 'N/mm²'],
            description='Maximum stress material can withstand under tension',
            laser_relevance=0.7,
            industry_importance=0.95,
            measurement_difficulty=0.6,
            material_categories=['metal', 'ceramic', 'polymer', 'composite'],
            typical_ranges={
                'metal': {'min': 50, 'max': 4000},  # Lead to high-strength steels
                'ceramic': {'min': 50, 'max': 1000},
                'polymer': {'min': 10, 'max': 300},
                'composite': {'min': 100, 'max': 3000}
            },
            related_properties=['youngs_modulus', 'hardness'],
            industry_standards=['ASTM E8', 'ISO 6892', 'ASTM D638'],
            research_sources=['ASM Mechanical Properties', 'MatWeb Database']
        )
        
        properties['youngs_modulus'] = PropertyDefinition(
            name='youngs_modulus',
            common_names=['Young\'s Modulus', 'Elastic Modulus', 'Modulus of Elasticity'],
            units=['GPa', 'psi', 'MPa'],
            description='Material stiffness - resistance to elastic deformation',
            laser_relevance=0.6,
            industry_importance=0.9,
            measurement_difficulty=0.5,
            material_categories=['metal', 'ceramic', 'polymer', 'composite'],
            typical_ranges={
                'metal': {'min': 1.8, 'max': 1200},  # Lead to Diamond-like carbon
                'ceramic': {'min': 150, 'max': 700},
                'polymer': {'min': 0.01, 'max': 15},
                'composite': {'min': 10, 'max': 500}
            },
            related_properties=['tensile_strength', 'hardness'],
            industry_standards=['ASTM E111', 'ISO 6892'],
            research_sources=['ASM Handbook', 'Engineering Materials Database']
        )
        
        properties['hardness'] = PropertyDefinition(
            name='hardness',
            common_names=['Hardness', 'Surface Hardness'],
            units=['HV', 'HRC', 'HRB', 'Mohs', 'Shore A', 'Shore D'],
            description='Resistance to indentation, scratching, and wear',
            laser_relevance=0.8,
            industry_importance=0.85,
            measurement_difficulty=0.4,
            material_categories=['metal', 'ceramic', 'polymer', 'composite'],
            typical_ranges={
                'metal': {'min': 10, 'max': 1000},  # HV scale
                'ceramic': {'min': 5.5, 'max': 10},  # Mohs scale
                'polymer': {'min': 20, 'max': 95},  # Shore D scale
                'composite': {'min': 50, 'max': 800}  # HV scale
            },
            related_properties=['tensile_strength', 'youngs_modulus'],
            industry_standards=['ASTM E18', 'ISO 6508', 'ASTM D2240'],
            research_sources=['ASM Metals Handbook', 'Hardness Database']
        )
        
        # === THERMAL PROPERTIES ===
        properties['thermal_conductivity'] = PropertyDefinition(
            name='thermal_conductivity',
            common_names=['Thermal Conductivity', 'Heat Conductivity'],
            units=['W/m·K', 'BTU/hr·ft·°F', 'cal/s·cm·°C'],
            description='Rate of heat conduction - critical for laser processing temperature distribution',
            laser_relevance=0.98,
            industry_importance=0.9,
            measurement_difficulty=0.7,
            material_categories=['metal', 'ceramic', 'polymer', 'composite', 'glass'],
            typical_ranges={
                'metal': {'min': 1.4, 'max': 429},  # Bismuth to Silver
                'ceramic': {'min': 0.1, 'max': 400},  # Aerogel to Diamond
                'polymer': {'min': 0.1, 'max': 2.0},
                'composite': {'min': 0.1, 'max': 200},
                'glass': {'min': 0.5, 'max': 2.0}
            },
            related_properties=['thermal_diffusivity', 'specific_heat'],
            industry_standards=['ASTM E1461', 'ISO 22007'],
            research_sources=['CRC Handbook', 'Thermal Properties Database']
        )
        
        properties['specific_heat'] = PropertyDefinition(
            name='specific_heat',
            common_names=['Specific Heat Capacity', 'Heat Capacity'],
            units=['J/g·K', 'J/kg·K', 'cal/g·°C', 'BTU/lb·°F'],
            description='Heat capacity per unit mass - affects laser heating rate',
            laser_relevance=0.9,
            industry_importance=0.75,
            measurement_difficulty=0.6,
            material_categories=['metal', 'ceramic', 'polymer', 'composite'],
            typical_ranges={
                'metal': {'min': 0.122, 'max': 3.582},  # Lead to Lithium
                'ceramic': {'min': 0.4, 'max': 1.1},
                'polymer': {'min': 1.0, 'max': 2.5},
                'composite': {'min': 0.5, 'max': 2.0}
            },
            related_properties=['thermal_conductivity', 'density'],
            industry_standards=['ASTM E1269', 'ISO 11357'],
            research_sources=['NIST Chemistry WebBook', 'Thermal Properties Database']
        )
        
        properties['melting_point'] = PropertyDefinition(
            name='melting_point',
            common_names=['Melting Point', 'Fusion Point', 'Liquidus Temperature'],
            units=['°C', '°F', 'K'],
            description='Temperature at which material transitions to liquid state',
            laser_relevance=0.95,
            industry_importance=0.9,
            measurement_difficulty=0.3,
            material_categories=['metal', 'ceramic', 'polymer', 'glass'],
            typical_ranges={
                'metal': {'min': -38.8, 'max': 3695},  # Hg to W
                'ceramic': {'min': 1000, 'max': 3827},
                'polymer': {'min': 80, 'max': 400},  # Degradation temperature
                'glass': {'min': 400, 'max': 1700}
            },
            related_properties=['thermal_conductivity', 'crystalline_structure'],
            industry_standards=['ASTM E324', 'ISO 3146'],
            research_sources=['CRC Handbook', 'Phase Diagrams Database']
        )
        
        properties['thermal_expansion'] = PropertyDefinition(
            name='thermal_expansion',
            common_names=['Coefficient of Thermal Expansion', 'CTE', 'Linear Expansion'],
            units=['µm/m·K', '1/K', 'ppm/°C'],
            description='Dimensional change per unit temperature change',
            laser_relevance=0.85,
            industry_importance=0.8,
            measurement_difficulty=0.6,
            material_categories=['metal', 'ceramic', 'polymer', 'composite', 'glass'],
            typical_ranges={
                'metal': {'min': 0.2, 'max': 29.0},  # Invar to Cesium
                'ceramic': {'min': 0.1, 'max': 14.0},
                'polymer': {'min': 20, 'max': 200},
                'composite': {'min': 1, 'max': 50},
                'glass': {'min': 3, 'max': 15}
            },
            related_properties=['thermal_conductivity', 'crystalline_structure'],
            industry_standards=['ASTM E228', 'ISO 11359'],
            research_sources=['ASM Handbook', 'Thermal Expansion Database']
        )
        
        properties['thermal_diffusivity'] = PropertyDefinition(
            name='thermal_diffusivity',
            common_names=['Thermal Diffusivity'],
            units=['mm²/s', 'm²/s', 'cm²/s'],
            description='Rate of temperature change through material thickness',
            laser_relevance=0.8,
            industry_importance=0.7,
            measurement_difficulty=0.8,
            material_categories=['metal', 'ceramic', 'polymer'],
            typical_ranges={
                'metal': {'min': 1.0, 'max': 174.0},
                'ceramic': {'min': 0.3, 'max': 120.0},
                'polymer': {'min': 0.1, 'max': 0.3}
            },
            related_properties=['thermal_conductivity', 'specific_heat', 'density'],
            industry_standards=['ASTM E1461'],
            research_sources=['Thermal Properties Database']
        )
        
        # === OPTICAL/LASER PROPERTIES ===
        properties['laser_absorption'] = PropertyDefinition(
            name='laser_absorption',
            common_names=['Laser Absorption Coefficient', 'Absorptivity', 'Absorption Factor'],
            units=['cm⁻¹', 'm⁻¹', '%'],
            description='Material-specific laser energy absorption rate',
            laser_relevance=1.0,
            industry_importance=0.95,
            measurement_difficulty=0.9,
            material_categories=['metal', 'ceramic', 'polymer', 'composite'],
            typical_ranges={
                'metal': {'min': 0.01, 'max': 1000},
                'ceramic': {'min': 0.1, 'max': 50},
                'polymer': {'min': 0.05, 'max': 200},
                'composite': {'min': 0.05, 'max': 100}
            },
            related_properties=['reflectivity', 'surface_roughness'],
            industry_standards=['ASTM F3039'],
            research_sources=['Laser Processing Database', 'Optical Properties Database']
        )
        
        properties['reflectivity'] = PropertyDefinition(
            name='reflectivity',
            common_names=['Surface Reflectivity', 'Reflectance', 'Optical Reflectivity'],
            units=['%', 'fraction'],
            description='Percentage of incident laser light reflected from surface',
            laser_relevance=0.95,
            industry_importance=0.8,
            measurement_difficulty=0.7,
            material_categories=['metal', 'ceramic', 'polymer', 'glass'],
            typical_ranges={
                'metal': {'min': 5, 'max': 98},  # Black surfaces to polished silver
                'ceramic': {'min': 5, 'max': 90},
                'polymer': {'min': 2, 'max': 80},
                'glass': {'min': 4, 'max': 95}
            },
            related_properties=['laser_absorption', 'surface_finish'],
            industry_standards=['ASTM E903'],
            research_sources=['Optical Properties Database']
        )
        
        # === ELECTRICAL PROPERTIES ===
        properties['electrical_conductivity'] = PropertyDefinition(
            name='electrical_conductivity',
            common_names=['Electrical Conductivity', 'Specific Conductance'],
            units=['S/m', 'MS/m', 'mS/cm'],
            description='Ability to conduct electric current - correlates with laser coupling',
            laser_relevance=0.7,
            industry_importance=0.85,
            measurement_difficulty=0.4,
            material_categories=['metal', 'ceramic', 'composite'],
            typical_ranges={
                'metal': {'min': 0.69e6, 'max': 63.0e6},  # Bismuth to Silver
                'ceramic': {'min': 1e-12, 'max': 1e6},  # Insulators to conductors
                'composite': {'min': 1e-10, 'max': 1e8}
            },
            related_properties=['thermal_conductivity'],
            industry_standards=['ASTM B193'],
            research_sources=['CRC Handbook', 'Electrical Properties Database']
        )
        
        # === CHEMICAL PROPERTIES ===
        properties['corrosion_resistance'] = PropertyDefinition(
            name='corrosion_resistance',
            common_names=['Corrosion Resistance', 'Chemical Resistance'],
            units=['rating', 'qualitative'],
            description='Resistance to chemical degradation and oxidation',
            laser_relevance=0.6,
            industry_importance=0.9,
            measurement_difficulty=0.8,
            material_categories=['metal', 'ceramic', 'polymer', 'composite'],
            typical_ranges={},  # Qualitative property
            related_properties=['surface_finish', 'composition'],
            industry_standards=['ASTM G48', 'ISO 3651'],
            research_sources=['Corrosion Database', 'ASM Corrosion Handbook']
        )
        
        # === POLYMER-SPECIFIC PROPERTIES ===
        properties['glass_transition_temperature'] = PropertyDefinition(
            name='glass_transition_temperature',
            common_names=['Glass Transition Temperature', 'Tg'],
            units=['°C', '°F', 'K'],
            description='Temperature at which polymer transitions from hard to soft state',
            laser_relevance=0.9,
            industry_importance=0.95,
            measurement_difficulty=0.5,
            material_categories=['polymer', 'plastic'],
            typical_ranges={
                'polymer': {'min': -125, 'max': 375},  # Silicone rubber to Polyimide
                'plastic': {'min': -125, 'max': 375}   # Same ranges for plastic
            },
            related_properties=['melting_point', 'thermal_expansion'],
            industry_standards=['ASTM D3418', 'ISO 11357'],
            research_sources=['Polymer Database', 'DSC Database']
        )
        
        # === CERAMIC-SPECIFIC PROPERTIES ===
        properties['thermal_shock_resistance'] = PropertyDefinition(
            name='thermal_shock_resistance',
            common_names=['Thermal Shock Resistance'],
            units=['°C', 'K', 'rating'],
            description='Ability to withstand rapid temperature changes without cracking',
            laser_relevance=0.95,
            industry_importance=0.8,
            measurement_difficulty=0.7,
            material_categories=['ceramic', 'glass'],
            typical_ranges={
                'ceramic': {'min': 50, 'max': 1000},
                'glass': {'min': 20, 'max': 500}
            },
            related_properties=['thermal_expansion', 'thermal_conductivity'],
            industry_standards=['ASTM C1171'],
            research_sources=['Ceramics Database']
        )
        
        # === SURFACE PROPERTIES ===
        properties['surface_roughness'] = PropertyDefinition(
            name='surface_roughness',
            common_names=['Surface Roughness', 'Ra', 'Surface Finish'],
            units=['μm', 'μin', 'nm'],
            description='Surface texture measurement - affects laser absorption',
            laser_relevance=0.8,
            industry_importance=0.7,
            measurement_difficulty=0.5,
            material_categories=['metal', 'ceramic', 'polymer', 'composite'],
            typical_ranges={
                'metal': {'min': 0.1, 'max': 50},
                'ceramic': {'min': 0.1, 'max': 10},
                'polymer': {'min': 0.5, 'max': 25},
                'composite': {'min': 0.2, 'max': 20}
            },
            related_properties=['laser_absorption', 'reflectivity'],
            industry_standards=['ISO 4287', 'ASTM B46.1'],
            research_sources=['Surface Metrology Database']
        )
        
        return properties
    
    def _create_category_property_maps(self) -> Dict[str, List[str]]:
        """Create mapping of material categories to their most relevant properties"""
        
        category_maps = {}
        
        # Metal properties (ranked by importance)
        category_maps['metal'] = [
            'density',
            'thermal_conductivity', 
            'melting_point',
            'specific_heat',
            'laser_absorption',
            'reflectivity',
            'electrical_conductivity',
            'tensile_strength',
            'youngs_modulus',
            'thermal_expansion',
            'hardness',
            'thermal_diffusivity',
            'surface_roughness',
            'corrosion_resistance'
        ]
        
        # Ceramic properties
        category_maps['ceramic'] = [
            'density',
            'hardness',
            'thermal_conductivity',
            'melting_point',
            'thermal_shock_resistance',
            'laser_absorption',
            'reflectivity',
            'specific_heat',
            'thermal_expansion',
            'youngs_modulus',
            'tensile_strength',
            'surface_roughness',
            'corrosion_resistance'
        ]
        
        # Polymer/Plastic properties
        polymer_properties = [
            'density',
            'glass_transition_temperature',
            'thermal_conductivity',
            'specific_heat',
            'laser_absorption',
            'reflectivity',
            'thermal_expansion',
            'tensile_strength',
            'youngs_modulus',
            'hardness',
            'surface_roughness',
            'corrosion_resistance'
        ]
        category_maps['polymer'] = polymer_properties
        category_maps['plastic'] = polymer_properties  # plastic maps to polymer properties
        
        # Composite properties
        category_maps['composite'] = [
            'density',
            'thermal_conductivity',
            'specific_heat',
            'laser_absorption',
            'reflectivity',
            'tensile_strength',
            'youngs_modulus',
            'thermal_expansion',
            'hardness',
            'electrical_conductivity',
            'surface_roughness',
            'corrosion_resistance'
        ]
        
        # Glass properties
        category_maps['glass'] = [
            'density',
            'thermal_conductivity',
            'melting_point',
            'thermal_shock_resistance',
            'reflectivity',
            'laser_absorption',
            'thermal_expansion',
            'hardness',
            'surface_roughness'
        ]
        
        # Stone properties
        category_maps['stone'] = [
            'density',
            'hardness',
            'thermal_conductivity',
            'specific_heat',
            'laser_absorption',
            'thermal_expansion',
            'surface_roughness'
        ]
        
        # Wood properties
        category_maps['wood'] = [
            'density',
            'thermal_conductivity',
            'specific_heat',
            'laser_absorption',
            'surface_roughness'
        ]
        
        return category_maps
    
    def get_recommended_properties_for_material(self, material_name: str) -> Dict[str, Any]:
        """Get recommended properties for a specific material"""
        
        try:
            from data.materials import get_material_by_name
            material_data = get_material_by_name(material_name)
            if not material_data:
                return {'error': f'Material {material_name} not found'}
        except Exception as e:
            return {'error': f'Error loading material: {str(e)}'}
        
        category = material_data.get('category', 'unknown')
        subcategory = material_data.get('subcategory', '')
        
        if category not in self.category_property_maps:
            return {
                'material_name': material_name,
                'category': category,
                'error': f'No property recommendations for category: {category}'
            }
        
        # Get recommended properties for this category
        recommended_property_names = self.category_property_maps[category]
        
        recommended_properties = []
        for prop_name in recommended_property_names:
            if prop_name in self.property_definitions:
                prop_def = self.property_definitions[prop_name]
                
                # Get typical range for this category
                typical_range = prop_def.typical_ranges.get(category, {})
                
                recommended_properties.append({
                    'name': prop_name,
                    'common_names': prop_def.common_names,
                    'units': prop_def.units,
                    'description': prop_def.description,
                    'laser_relevance': prop_def.laser_relevance,
                    'industry_importance': prop_def.industry_importance,
                    'measurement_difficulty': prop_def.measurement_difficulty,
                    'typical_range': typical_range,
                    'industry_standards': prop_def.industry_standards,
                    'priority_rank': recommended_property_names.index(prop_name) + 1
                })
        
        # Get current properties if any
        current_properties = material_data.get('properties', {})
        
        return {
            'material_name': material_name,
            'category': category,
            'subcategory': subcategory,
            'total_recommended': len(recommended_properties),
            'current_properties_count': len(current_properties),
            'current_properties': list(current_properties.keys()),
            'recommended_properties': recommended_properties,
            'priority_properties': [p for p in recommended_properties if p['priority_rank'] <= 5],
            'laser_critical_properties': [p for p in recommended_properties if p['laser_relevance'] >= 0.9]
        }
    
    def analyze_all_materials(self) -> Dict[str, Any]:
        """Analyze property recommendations for all materials in the database"""
        
        results = {
            'total_materials': 0,
            'categories_analyzed': {},
            'property_usage_analysis': {},
            'recommendations_summary': {},
            'top_missing_properties': {},
            'category_coverage': {}
        }
        
        if 'material_index' not in self.materials_data:
            return {'error': 'No material index found'}
        
        results['total_materials'] = len(self.materials_data['material_index'])
        
        # Track categories and their property needs
        category_stats = {}
        all_missing_properties = {}
        
        for material_name, material_info in self.materials_data['material_index'].items():
            category = material_info.get('category', 'unknown')
            
            if category not in category_stats:
                category_stats[category] = {
                    'material_count': 0,
                    'total_recommended': 0,
                    'total_current': 0,
                    'missing_properties': {},
                    'materials': []
                }
            
            category_stats[category]['material_count'] += 1
            category_stats[category]['materials'].append(material_name)
            
            # Get recommendations for this material
            recommendations = self.get_recommended_properties_for_material(material_name)
            
            if 'error' not in recommendations:
                recommended_count = recommendations['total_recommended']
                current_count = recommendations['current_properties_count']
                
                category_stats[category]['total_recommended'] += recommended_count
                category_stats[category]['total_current'] += current_count
                
                # Track missing properties
                current_props = set(recommendations['current_properties'])
                recommended_props = {p['name'] for p in recommendations['recommended_properties']}
                missing_props = recommended_props - current_props
                
                for missing_prop in missing_props:
                    if missing_prop not in category_stats[category]['missing_properties']:
                        category_stats[category]['missing_properties'][missing_prop] = 0
                    category_stats[category]['missing_properties'][missing_prop] += 1
                    
                    if missing_prop not in all_missing_properties:
                        all_missing_properties[missing_prop] = 0
                    all_missing_properties[missing_prop] += 1
        
        # Compile results
        results['categories_analyzed'] = {
            cat: {
                'material_count': stats['material_count'],
                'avg_recommended': stats['total_recommended'] / stats['material_count'] if stats['material_count'] > 0 else 0,
                'avg_current': stats['total_current'] / stats['material_count'] if stats['material_count'] > 0 else 0,
                'top_missing': dict(sorted(stats['missing_properties'].items(), key=lambda x: x[1], reverse=True)[:5])
            }
            for cat, stats in category_stats.items()
        }
        
        # Overall top missing properties
        results['top_missing_properties'] = dict(sorted(all_missing_properties.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Calculate coverage percentages
        for category, stats in category_stats.items():
            if stats['total_recommended'] > 0:
                coverage = (stats['total_current'] / stats['total_recommended']) * 100
                results['category_coverage'][category] = coverage
        
        return results
    
    def generate_property_population_plan(self) -> Dict[str, Any]:
        """Generate a plan for populating missing properties across all materials"""
        
        analysis = self.analyze_all_materials()
        
        if 'error' in analysis:
            return analysis
        
        plan = {
            'total_materials': analysis['total_materials'],
            'current_properties': 0,
            'potential_properties': 0,
            'priority_actions': [],
            'category_plans': {},
            'implementation_phases': []
        }
        
        # Calculate current and potential properties
        for category, stats in analysis['categories_analyzed'].items():
            current = int(stats['avg_current'] * stats['material_count'])
            potential = int(stats['avg_recommended'] * stats['material_count'])
            
            plan['current_properties'] += current
            plan['potential_properties'] += potential
            
            plan['category_plans'][category] = {
                'materials': stats['material_count'],
                'current_properties': current,
                'potential_properties': potential,
                'improvement_ratio': f"{potential/current:.1f}x" if current > 0 else "∞",
                'top_priorities': list(stats['top_missing'].keys())[:3]
            }
        
        # Create priority actions based on missing property frequency
        for prop_name, missing_count in list(analysis['top_missing_properties'].items())[:5]:
            if prop_name in self.property_definitions:
                prop_def = self.property_definitions[prop_name]
                plan['priority_actions'].append({
                    'property': prop_name,
                    'materials_missing': missing_count,
                    'laser_relevance': prop_def.laser_relevance,
                    'industry_importance': prop_def.industry_importance,
                    'measurement_difficulty': prop_def.measurement_difficulty,
                    'implementation_priority': prop_def.laser_relevance * (missing_count / analysis['total_materials'])
                })
        
        # Sort priority actions by implementation priority
        plan['priority_actions'].sort(key=lambda x: x['implementation_priority'], reverse=True)
        
        # Create implementation phases
        plan['implementation_phases'] = [
            {
                'phase': 1,
                'name': 'Critical Laser Properties',
                'properties': [action['property'] for action in plan['priority_actions'][:3]],
                'estimated_properties_added': sum(action['materials_missing'] for action in plan['priority_actions'][:3])
            },
            {
                'phase': 2, 
                'name': 'Industry Standard Properties',
                'properties': [action['property'] for action in plan['priority_actions'][3:5]],
                'estimated_properties_added': sum(action['materials_missing'] for action in plan['priority_actions'][3:5])
            },
            {
                'phase': 3,
                'name': 'Comprehensive Material Database',
                'properties': 'All remaining recommended properties',
                'estimated_properties_added': plan['potential_properties'] - plan['current_properties']
            }
        ]
        
        return plan


def main():
    """Command line interface for material property research"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Material Property Research System')
    parser.add_argument('--material', help='Get property recommendations for specific material')
    parser.add_argument('--analyze-all', action='store_true', help='Analyze all materials')
    parser.add_argument('--population-plan', action='store_true', help='Generate property population plan')
    parser.add_argument('--demo', action='store_true', help='Run comprehensive demo')
    
    args = parser.parse_args()
    
    system = MaterialPropertyResearchSystem()
    
    if args.material:
        result = system.get_recommended_properties_for_material(args.material)
        print(json.dumps(result, indent=2))
        
    elif args.analyze_all:
        result = system.analyze_all_materials()
        print(json.dumps(result, indent=2))
        
    elif args.population_plan:
        result = system.generate_property_population_plan()
        print(json.dumps(result, indent=2))
        
    elif args.demo:
        print("🔬 MATERIAL PROPERTY RESEARCH SYSTEM DEMO")
        print("=" * 60)
        
        # Test specific material
        print("\n📊 Material Analysis: Aluminum")
        result = system.get_recommended_properties_for_material("Aluminum")
        if 'error' not in result:
            print(f"  Category: {result['category']}")
            print(f"  Recommended properties: {result['total_recommended']}")
            print(f"  Current properties: {result['current_properties_count']}")
            print("  Top 5 priority properties:")
            for i, prop in enumerate(result['priority_properties'][:5], 1):
                print(f"    {i}. {prop['name']} (laser relevance: {prop['laser_relevance']:.2f})")
        
        # Overall analysis
        print("\n🏭 Overall Analysis")
        analysis = system.analyze_all_materials()
        if 'error' not in analysis:
            print(f"  Total materials: {analysis['total_materials']}")
            print(f"  Categories: {len(analysis['categories_analyzed'])}")
            print("  Top missing properties:")
            for i, (prop, count) in enumerate(list(analysis['top_missing_properties'].items())[:5], 1):
                print(f"    {i}. {prop}: missing from {count} materials")
        
        # Population plan
        print("\n🚀 Property Population Plan")
        plan = system.generate_property_population_plan()
        if 'error' not in plan:
            print(f"  Current properties: {plan['current_properties']}")
            print(f"  Potential properties: {plan['potential_properties']}")
            improvement = plan['potential_properties'] / plan['current_properties'] if plan['current_properties'] > 0 else float('inf')
            print(f"  Improvement potential: {improvement:.1f}x")
    
    else:
        # Default demo
        system = MaterialPropertyResearchSystem()
        result = system.get_recommended_properties_for_material("Aluminum")
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()