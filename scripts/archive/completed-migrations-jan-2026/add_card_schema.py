#!/usr/bin/env python3
"""
Phase 1: Add Card Schema to All Entity Frontmatter

Generates card presentation data for all entities based on their properties.
This is an additive migration - no existing data is removed.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import yaml
from typing import Dict, Any, Optional


class CardSchemaGenerator:
    """Generate card schemas for different entity types."""
    
    def __init__(self):
        self.severity_map = {
            4: 'critical',
            3: 'high',
            2: 'moderate',
            1: 'low',
            0: 'low'
        }
    
    def generate_material_card(self, material: Dict[str, Any]) -> Dict[str, Any]:
        """Generate card schema for material entity."""
        name = material.get('name', '')
        category = material.get('category', '')
        subcategory = material.get('subcategory', '')
        
        # Get key properties
        props = material.get('properties', {})
        wavelength = props.get('optimal_wavelength_nm', '1064')
        reflectivity = props.get('reflectivity_percent')
        absorption = props.get('absorption_percent')
        
        # Determine badge
        if reflectivity and float(reflectivity) > 80:
            badge_text = "High Reflectivity"
            badge_variant = "warning"
        elif absorption and float(absorption) > 80:
            badge_text = "High Absorption"
            badge_variant = "success"
        else:
            badge_text = "Common"
            badge_variant = "info"
        
        card = {
            'default': {
                'heading': name,
                'subtitle': f"{category}{f' / {subcategory}' if subcategory else ''}",
                'badge': {
                    'text': badge_text,
                    'variant': badge_variant
                },
                'metric': {
                    'value': str(wavelength),
                    'unit': 'nm',
                    'legend': 'Optimal Wavelength'
                },
                'severity': 'low',
                'icon': 'cube'
            }
        }
        
        # Add contamination context
        if reflectivity:
            card['contamination_context'] = {
                'heading': name,
                'subtitle': 'Laser Cleaning Target',
                'badge': {
                    'text': 'Surface Treatment',
                    'variant': 'technical'
                },
                'metric': {
                    'value': str(reflectivity),
                    'unit': '%',
                    'legend': 'Reflectivity'
                },
                'severity': 'moderate',
                'icon': 'target'
            }
        
        return card
    
    def generate_contaminant_card(self, contaminant: Dict[str, Any]) -> Dict[str, Any]:
        """Generate card schema for contaminant entity."""
        name = contaminant.get('name', '')
        category = contaminant.get('category', '')
        subcategory = contaminant.get('subcategory', '')
        
        # Determine severity from category
        severity = 'moderate'
        if 'rust' in name.lower() or 'corrosion' in name.lower():
            severity = 'high'
        elif 'dirt' in name.lower() or 'dust' in name.lower():
            severity = 'low'
        
        card = {
            'default': {
                'heading': name,
                'subtitle': f"{category}{f' / {subcategory}' if subcategory else ''}",
                'badge': {
                    'text': 'Contamination',
                    'variant': 'warning'
                },
                'metric': {
                    'value': '1064',
                    'unit': 'nm',
                    'legend': 'Typical Wavelength'
                },
                'severity': severity,
                'icon': 'droplet'
            }
        }
        
        return card
    
    def generate_compound_card(self, compound: Dict[str, Any]) -> Dict[str, Any]:
        """Generate card schema for compound entity."""
        name = compound.get('name', '')
        category = compound.get('category', '')
        subcategory = compound.get('subcategory', '')
        
        # Get hazard data
        health_hazard = compound.get('health_hazard', {})
        if isinstance(health_hazard, dict):
            health_hazard = health_hazard.get('nfpa_rating', 1)
        else:
            health_hazard = 1
        
        exposure_limits = compound.get('exposure_limits') or {}
        osha_pel = exposure_limits.get('osha_pel_ppm') if isinstance(exposure_limits, dict) else None
        
        # Determine severity and badge
        severity = self.severity_map.get(health_hazard, 'moderate')
        
        if health_hazard >= 3:
            badge_text = "Highly Toxic"
            badge_variant = "danger"
        elif health_hazard == 2:
            badge_text = "Toxic"
            badge_variant = "warning"
        else:
            badge_text = "Low Hazard"
            badge_variant = "info"
        
        card = {
            'default': {
                'heading': name,
                'subtitle': f"{category}{f' / {subcategory}' if subcategory else ''}",
                'badge': {
                    'text': badge_text,
                    'variant': badge_variant
                },
                'metric': {
                    'value': str(osha_pel) if osha_pel else 'N/A',
                    'unit': 'ppm' if osha_pel else '',
                    'legend': 'OSHA PEL' if osha_pel else 'Exposure Limit'
                },
                'severity': severity,
                'icon': 'flask'
            }
        }
        
        # Add contamination context
        card['contamination_context'] = {
            'heading': name,
            'subtitle': 'Emission Product',
            'badge': {
                'text': badge_text,
                'variant': badge_variant
            },
            'metric': {
                'value': str(osha_pel) if osha_pel else 'N/A',
                'unit': 'ppm' if osha_pel else '',
                'legend': 'Exposure Limit'
            },
            'severity': severity,
            'icon': 'alert-triangle'
        }
        
        return card
    
    def generate_setting_card(self, setting: Dict[str, Any]) -> Dict[str, Any]:
        """Generate card schema for machine setting entity."""
        material_name = setting.get('material', '')
        
        # Get laser parameters
        laser_params = setting.get('laser_parameters', {})
        wavelength = laser_params.get('wavelength_nm', '1064')
        power_min = laser_params.get('power_w', {}).get('min', 100)
        power_max = laser_params.get('power_w', {}).get('max', 300)
        
        card = {
            'default': {
                'heading': material_name,
                'subtitle': 'Machine Settings',
                'badge': {
                    'text': 'Optimized',
                    'variant': 'success'
                },
                'metric': {
                    'value': f"{power_min}-{power_max}",
                    'unit': 'W',
                    'legend': 'Power Range'
                },
                'severity': 'low',
                'icon': 'settings'
            }
        }
        
        return card


def add_card_schemas_to_materials():
    """Add card schemas to Materials.yaml."""
    print("Processing Materials.yaml...")
    
    materials_path = project_root / 'data' / 'materials' / 'Materials.yaml'
    
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    generator = CardSchemaGenerator()
    added_count = 0
    
    for material_id, material_data in data['materials'].items():
        if 'card' not in material_data:
            card_schema = generator.generate_material_card(material_data)
            material_data['card'] = card_schema
            added_count += 1
    
    # Save
    with open(materials_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ Added card schemas to {added_count} materials")
    return added_count


def add_card_schemas_to_contaminants():
    """Add card schemas to Contaminants.yaml."""
    print("Processing Contaminants.yaml...")
    
    contaminants_path = project_root / 'data' / 'contaminants' / 'Contaminants.yaml'
    
    with open(contaminants_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    generator = CardSchemaGenerator()
    added_count = 0
    
    for pattern_id, pattern_data in data['contamination_patterns'].items():
        if 'card' not in pattern_data:
            card_schema = generator.generate_contaminant_card(pattern_data)
            pattern_data['card'] = card_schema
            added_count += 1
    
    # Save
    with open(contaminants_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ Added card schemas to {added_count} contaminants")
    return added_count


def add_card_schemas_to_compounds():
    """Add card schemas to Compounds.yaml."""
    print("Processing Compounds.yaml...")
    
    compounds_path = project_root / 'data' / 'compounds' / 'Compounds.yaml'
    
    with open(compounds_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    generator = CardSchemaGenerator()
    added_count = 0
    
    for compound_id, compound_data in data['compounds'].items():
        if 'card' not in compound_data:
            card_schema = generator.generate_compound_card(compound_data)
            compound_data['card'] = card_schema
            added_count += 1
    
    # Save
    with open(compounds_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ Added card schemas to {added_count} compounds")
    return added_count


def add_card_schemas_to_settings():
    """Add card schemas to Settings.yaml."""
    print("Processing Settings.yaml...")
    
    settings_path = project_root / 'data' / 'settings' / 'Settings.yaml'
    
    with open(settings_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    generator = CardSchemaGenerator()
    added_count = 0
    
    for setting_id, setting_data in data['settings'].items():
        if 'card' not in setting_data:
            card_schema = generator.generate_setting_card(setting_data)
            setting_data['card'] = card_schema
            added_count += 1
    
    # Save
    with open(settings_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ Added card schemas to {added_count} settings")
    return added_count


def main():
    """Run Phase 1: Add card schemas to all entities."""
    print("="*80)
    print("PHASE 1: ADD CARD SCHEMA TO ALL ENTITIES")
    print("="*80)
    print()
    
    total_added = 0
    
    # Process each domain
    total_added += add_card_schemas_to_materials()
    total_added += add_card_schemas_to_contaminants()
    total_added += add_card_schemas_to_compounds()
    total_added += add_card_schemas_to_settings()
    
    print()
    print("="*80)
    print(f"✅ PHASE 1 COMPLETE")
    print(f"   Total card schemas added: {total_added}")
    print("="*80)


if __name__ == '__main__':
    main()
