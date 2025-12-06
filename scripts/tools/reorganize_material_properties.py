#!/usr/bin/env python3
"""
Reorganize materialProperties in Materials.yaml

Move laser-interaction properties from material_characteristics to laser_material_interaction.
This fixes the semantic separation between intrinsic material properties and laser interaction properties.

Usage:
    python3 scripts/reorganize_material_properties.py
"""

import yaml
from pathlib import Path
from collections import OrderedDict

# Custom YAML representer to preserve order and formatting
def represent_ordereddict(dumper, data):
    return dumper.represent_mapping('tag:yaml.org,2002:map', data.items())

yaml.add_representer(OrderedDict, represent_ordereddict)

# Properties that should be in laser_material_interaction
LASER_INTERACTION_PROPS = {
    # Thermal Transport (how material handles laser heat)
    'thermalConductivity',
    'thermalDiffusivity',
    'thermalExpansion',
    'specificHeat',
    'thermalShockResistance',
    'vaporPressure',
    'thermalDestruction',
    'thermalDestructionPoint',
    
    # Optical (how material interacts with laser light)
    'absorptivity',
    'laserAbsorption',
    'absorptionCoefficient',
    'reflectivity',
    'laserReflectivity',
    
    # Laser Processing Thresholds
    'laserDamageThreshold',
    'ablationThreshold',
}

# Properties that should stay in material_characteristics (for validation)
MATERIAL_CHARACTERISTICS_PROPS = {
    # Structural/Mechanical
    'density',
    'porosity',
    'surfaceRoughness',
    'hardness',
    'youngsModulus',
    'tensileStrength',
    'compressiveStrength',
    'flexuralStrength',
    'fractureToughness',
    
    # Electrical
    'electricalResistivity',
    'electricalConductivity',
    
    # Chemical/Environmental
    'oxidationResistance',
    'corrosionResistance',
    
    # Phase Transitions (intrinsic limits)
    'meltingPoint',
    'boilingPoint',
}

# Metadata keys that are not properties
METADATA_KEYS = {'label', 'percentage', 'description'}


def reorganize_material(material_name: str, material_data: dict) -> tuple[dict, dict]:
    """
    Reorganize a single material's properties.
    
    Returns:
        tuple of (updated_material_data, stats_dict)
    """
    stats = {'moved': [], 'already_correct': [], 'unclassified': []}
    
    if 'materialProperties' not in material_data:
        return material_data, stats
    
    mat_props = material_data['materialProperties']
    mat_chars = mat_props.get('material_characteristics', {})
    laser_int = mat_props.get('laser_material_interaction', {})
    
    # Initialize laser_material_interaction if empty or only has metadata
    if not laser_int or set(laser_int.keys()) <= METADATA_KEYS:
        laser_int = {
            'label': 'Laser-Material Interaction',
            'percentage': 40.0,
            'description': 'Optical and thermal properties governing laser energy absorption, reflection, propagation, and ablation thresholds',
        }
    
    # Ensure material_characteristics has metadata
    if 'label' not in mat_chars:
        mat_chars['label'] = 'Material Characteristics'
    if 'percentage' not in mat_chars:
        mat_chars['percentage'] = 60.0
    if 'description' not in mat_chars:
        mat_chars['description'] = 'Intrinsic physical, mechanical, chemical, and structural properties affecting cleaning outcomes and material integrity'
    
    # Move properties from material_characteristics to laser_material_interaction
    props_to_move = []
    for prop_name, prop_data in list(mat_chars.items()):
        if prop_name in METADATA_KEYS:
            continue
            
        if prop_name in LASER_INTERACTION_PROPS:
            # Check if already in laser_int (don't overwrite)
            if prop_name not in laser_int:
                laser_int[prop_name] = prop_data
                props_to_move.append(prop_name)
                stats['moved'].append(prop_name)
            else:
                stats['already_correct'].append(prop_name)
        elif prop_name in MATERIAL_CHARACTERISTICS_PROPS:
            # Property is correctly placed
            pass
        else:
            # Unknown property - log it
            stats['unclassified'].append(prop_name)
    
    # Remove moved properties from material_characteristics
    for prop_name in props_to_move:
        del mat_chars[prop_name]
    
    # Ensure percentages are correct
    mat_chars['percentage'] = 60.0
    laser_int['percentage'] = 40.0
    
    # Update the material
    mat_props['material_characteristics'] = mat_chars
    mat_props['laser_material_interaction'] = laser_int
    
    return material_data, stats


def main():
    yaml_path = Path('data/materials/Materials.yaml')
    
    print(f"Loading {yaml_path}...")
    with open(yaml_path, 'r') as f:
        content = f.read()
    
    # Use safe_load to get the data
    data = yaml.safe_load(content)
    
    if not data:
        print("ERROR: Could not load YAML data")
        return
    
    materials_section = data.get('materials', {})
    if not materials_section:
        print("ERROR: No 'materials' section found")
        return
    
    print(f"Found {len(materials_section)} materials to process\n")
    
    # Track statistics
    total_stats = {
        'materials_processed': 0,
        'materials_modified': 0,
        'properties_moved': 0,
        'unclassified_props': set(),
    }
    
    # Process each material
    for material_name, material_data in materials_section.items():
        if not isinstance(material_data, dict):
            continue
            
        updated_data, stats = reorganize_material(material_name, material_data)
        materials_section[material_name] = updated_data
        
        total_stats['materials_processed'] += 1
        
        if stats['moved']:
            total_stats['materials_modified'] += 1
            total_stats['properties_moved'] += len(stats['moved'])
            print(f"✓ {material_name}: Moved {len(stats['moved'])} props → laser_material_interaction")
            for prop in stats['moved']:
                print(f"    - {prop}")
        
        if stats['unclassified']:
            for prop in stats['unclassified']:
                total_stats['unclassified_props'].add(prop)
    
    # Save the reorganized data
    print(f"\nSaving reorganized data to {yaml_path}...")
    
    with open(yaml_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
    
    # Print summary
    print("\n" + "="*60)
    print("REORGANIZATION COMPLETE")
    print("="*60)
    print(f"Materials processed: {total_stats['materials_processed']}")
    print(f"Materials modified:  {total_stats['materials_modified']}")
    print(f"Properties moved:    {total_stats['properties_moved']}")
    
    if total_stats['unclassified_props']:
        print(f"\nUnclassified properties found (kept in material_characteristics):")
        for prop in sorted(total_stats['unclassified_props']):
            print(f"  - {prop}")
    
    print("\nNext steps:")
    print("1. Run: python3 -m pytest tests/ -v  # Verify tests pass")
    print("2. Run: python3 run.py --deploy      # Sync to frontmatter")


if __name__ == '__main__':
    main()
