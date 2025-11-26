#!/usr/bin/env python3
"""
Migrate Properties from Legacy "other" Group to Proper Category Groups

This script moves properties from the legacy "other" group in materialProperties
into the appropriate category groups (material_characteristics or laser_material_interaction)
based on property type classification.

PROPERTY CLASSIFICATION:
- material_characteristics: Physical, mechanical, chemical properties
  (density, hardness, tensile strength, porosity, etc.)
  
- laser_material_interaction: Optical, thermal, ablation properties
  (thermal conductivity, reflectivity, absorption, ablation threshold, etc.)

Usage:
    python3 scripts/tools/migrate_other_properties.py [--dry-run] [--material NAME]
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Set

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from domains.materials.materials_cache import load_materials

# Property classification based on material science categories
MATERIAL_CHARACTERISTICS_PROPERTIES = {
    # Physical properties
    'density', 'porosity', 'grainSize', 'crystallineStructure',
    'molecularWeight', 'specificGravity', 'bulkDensity',
    
    # Mechanical properties
    'hardness', 'tensileStrength', 'compressiveStrength', 'flexuralStrength',
    'youngsModulus', 'shearModulus', 'elasticModulus', 'poissonsRatio',
    'fractureToughness', 'yieldStrength', 'ultimateStrength',
    
    # Chemical properties
    'chemicalComposition', 'oxidationResistance', 'corrosionResistance',
    'chemicalStability', 'reactivity',
    
    # Surface properties
    'surfaceRoughness', 'surfaceEnergy', 'wettability',
}

LASER_MATERIAL_INTERACTION_PROPERTIES = {
    # Thermal properties
    'thermalConductivity', 'thermalExpansion', 'thermalDiffusivity',
    'specificHeat', 'heatCapacity', 'meltingPoint', 'boilingPoint',
    'thermalDestruction', 'thermalShockResistance',
    
    # Optical properties
    'laserReflectivity', 'reflectivity', 'absorptionCoefficient',
    'refractiveIndex', 'transmissivity', 'emissivity', 'absorptivity',
    
    # Laser-specific properties
    'ablationThreshold', 'laserDamageThreshold', 'photonicEfficiency',
    'absorptionDepth', 'opticalPenetrationDepth',
}

# Required group structure
REQUIRED_GROUPS = {
    'material_characteristics': {
        'label': 'Material Characteristics',
        'description': 'Intrinsic physical, mechanical, chemical, and structural properties affecting cleaning outcomes and material integrity'
    },
    'laser_material_interaction': {
        'label': 'Laser-Material Interaction',
        'description': 'Optical and thermal properties governing laser energy absorption, reflection, propagation, and ablation thresholds'
    }
}


def classify_property(prop_name: str) -> str:
    """
    Classify a property into material_characteristics or laser_material_interaction.
    
    Args:
        prop_name: Property name to classify
        
    Returns:
        'material_characteristics' or 'laser_material_interaction'
    """
    # Normalize property name (handle camelCase variations)
    prop_lower = prop_name.lower()
    
    # Check material characteristics first
    for mat_prop in MATERIAL_CHARACTERISTICS_PROPERTIES:
        if mat_prop.lower() in prop_lower or prop_lower in mat_prop.lower():
            return 'material_characteristics'
    
    # Check laser interaction properties
    for laser_prop in LASER_MATERIAL_INTERACTION_PROPERTIES:
        if laser_prop.lower() in prop_lower or prop_lower in laser_prop.lower():
            return 'laser_material_interaction'
    
    # Default: if contains 'thermal', 'laser', 'optical', 'reflectivity' -> laser interaction
    thermal_keywords = ['thermal', 'laser', 'optical', 'reflect', 'absorb', 'ablat', 'emission']
    if any(keyword in prop_lower for keyword in thermal_keywords):
        return 'laser_material_interaction'
    
    # Default: material characteristics for everything else
    return 'material_characteristics'


def migrate_other_properties(material_data: Dict[str, Any], material_name: str, 
                             dry_run: bool = False) -> tuple:
    """
    Migrate properties from 'other' group to proper category groups.
    
    Args:
        material_data: Material dictionary
        material_name: Material name for logging
        dry_run: If True, only report what would be done
        
    Returns:
        Tuple of (updated_data, migration_report)
    """
    if 'materialProperties' not in material_data:
        return material_data, {'migrated': 0, 'properties': []}
    
    mat_props = material_data['materialProperties']
    
    # Check if 'other' group exists
    if 'other' not in mat_props:
        return material_data, {'migrated': 0, 'properties': []}
    
    other_group = mat_props['other']
    if not isinstance(other_group, dict):
        return material_data, {'migrated': 0, 'properties': []}
    
    # Extract properties from 'other' group (skip metadata fields)
    metadata_fields = {'label', 'description', 'percentage', 'properties'}
    properties_to_migrate = {k: v for k, v in other_group.items() 
                            if k not in metadata_fields}
    
    if not properties_to_migrate:
        return material_data, {'migrated': 0, 'properties': []}
    
    # Initialize report
    report = {
        'migrated': len(properties_to_migrate),
        'properties': [],
        'material_characteristics': [],
        'laser_material_interaction': []
    }
    
    if dry_run:
        # Just classify and report
        for prop_name in properties_to_migrate.keys():
            target_group = classify_property(prop_name)
            report['properties'].append({
                'name': prop_name,
                'target': target_group
            })
            report[target_group].append(prop_name)
        return material_data, report
    
    # Perform migration
    # Ensure target groups exist with proper structure
    for group_name, group_config in REQUIRED_GROUPS.items():
        if group_name not in mat_props:
            mat_props[group_name] = {
                'label': group_config['label'],
                'description': group_config['description'],
                'properties': {}
            }
        else:
            # Ensure 'properties' dict exists
            if 'properties' not in mat_props[group_name]:
                mat_props[group_name]['properties'] = {}
    
    # Migrate each property
    for prop_name, prop_data in properties_to_migrate.items():
        target_group = classify_property(prop_name)
        
        # Add to target group's properties dict
        mat_props[target_group]['properties'][prop_name] = prop_data
        
        # Track in report
        report['properties'].append({
            'name': prop_name,
            'target': target_group
        })
        report[target_group].append(prop_name)
    
    # Remove 'other' group entirely
    del mat_props['other']
    
    return material_data, report


def save_materials(data: Dict) -> None:
    """Save materials data back to Materials.yaml."""
    def convert_to_dict(obj):
        """Recursively convert OrderedDict to regular dict."""
        if hasattr(obj, 'items'):
            return {k: convert_to_dict(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_dict(item) for item in obj]
        return obj
    
    clean_data = convert_to_dict(data)
    
    materials_path = project_root / 'materials' / 'data' / 'Materials.yaml'
    with open(materials_path, 'w') as f:
        yaml.dump(clean_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migrate properties from legacy "other" group to proper category groups'
    )
    parser.add_argument('--dry-run', action='store_true', 
                       help='Report what would be migrated without making changes')
    parser.add_argument('--material', type=str,
                       help='Migrate only this specific material')
    
    args = parser.parse_args()
    
    print('=' * 80)
    print('MIGRATE LEGACY "OTHER" PROPERTIES TO CATEGORY GROUPS')
    print('=' * 80)
    print(f'Mode: {"DRY RUN" if args.dry_run else "MIGRATION"}')
    if args.material:
        print(f'Target: {args.material}')
    else:
        print('Target: All materials with "other" group')
    print('=' * 80)
    print()
    
    # Load materials
    materials_data = load_materials()
    materials = materials_data.get('materials', {})
    
    if args.material:
        if args.material not in materials:
            print(f'❌ Material "{args.material}" not found')
            return
        materials = {args.material: materials[args.material]}
    
    # Statistics
    total_materials = len(materials)
    materials_with_other = 0
    total_properties_migrated = 0
    materials_migrated = 0
    
    mat_char_total = 0
    laser_int_total = 0
    
    # Process each material
    for name, mat_data in materials.items():
        if 'materialProperties' in mat_data and 'other' in mat_data['materialProperties']:
            materials_with_other += 1
            
            updated_data, report = migrate_other_properties(mat_data, name, args.dry_run)
            
            if report['migrated'] > 0:
                total_properties_migrated += report['migrated']
                materials_migrated += 1
                
                mat_char_count = len(report['material_characteristics'])
                laser_int_count = len(report['laser_material_interaction'])
                
                mat_char_total += mat_char_count
                laser_int_total += laser_int_count
                
                status = '📋' if args.dry_run else '✅'
                print(f'{status} {name}:')
                print(f'   Migrated {report["migrated"]} properties:')
                print(f'   → material_characteristics: {mat_char_count}')
                print(f'   → laser_material_interaction: {laser_int_count}')
                
                if not args.dry_run:
                    materials_data['materials'][name] = updated_data
    
    print()
    print('=' * 80)
    print('SUMMARY')
    print('=' * 80)
    print(f'Total materials processed: {total_materials}')
    print(f'Materials with "other" group: {materials_with_other}')
    print(f'Materials migrated: {materials_migrated}')
    print(f'Total properties migrated: {total_properties_migrated}')
    print(f'  → material_characteristics: {mat_char_total}')
    print(f'  → laser_material_interaction: {laser_int_total}')
    
    if not args.dry_run and materials_migrated > 0:
        print()
        print('💾 Saving Materials.yaml...')
        save_materials(materials_data)
        print('✅ Migration complete!')
    
    print('=' * 80)


if __name__ == '__main__':
    main()
