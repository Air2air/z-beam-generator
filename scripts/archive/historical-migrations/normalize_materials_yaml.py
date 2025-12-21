#!/usr/bin/env python3
"""
Materials.yaml Normalization Script

Normalizes all material entries in Materials.yaml to match the frontmatter template structure.
Migrates FLAT structure to GROUPED structure and ensures consistent field ordering.

MIGRATION: FLAT → GROUPED Structure
- Flat: All properties directly under properties
- Grouped: Properties organized into material_characteristics and laser_material_interaction

Field Order (canonical):
1. name, category, subcategory, title, description, subtitle
2. author (moved earlier per template)
3. images
4. caption
5. regulatory_standards
6. applications
7. properties (GROUPED: material_characteristics, laser_material_interaction)
8. characteristics (qualitative properties)
9. machine_settings
10. environmentalImpact
11. outcomeMetrics
12. faq
13. _metadata

Usage:
    python3 scripts/tools/normalize_materials_yaml.py [--dry-run] [--material MATERIAL_NAME]
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, List
from collections import OrderedDict

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))


# Canonical field order for material entries (matches frontmatter_template.yaml)
CANONICAL_ORDER = [
    'name',
    'category',
    'subcategory',
    'title',
    'subtitle',
    'description',
    'author',
    'images',
    'micro',
    'regulatory_standards',
    'applications',
    'properties',
    'characteristics',
    'machine_settings',
    'environmentalImpact',
    'outcomeMetrics',
    'faq',
    '_metadata',
]

# Property group order within properties
PROPERTY_GROUP_ORDER = [
    'material_characteristics',
    'laser_material_interaction',
    'other',
]

# Property classification: which group does each property belong to?
MATERIAL_CHARACTERISTICS_PROPS = [
    'density', 'porosity', 'surfaceRoughness',
    'tensileStrength', 'youngsModulus', 'hardness', 'flexuralStrength', 'compressiveStrength',
    'oxidationResistance', 'corrosionResistance',
]

LASER_INTERACTION_PROPS = [
    'thermalConductivity', 'thermalExpansion', 'thermalDiffusivity', 'specificHeat', 'thermalShockResistance',
    'laserReflectivity', 'absorptionCoefficient', 'ablationThreshold', 'laserDamageThreshold',
]

# Property order within each group
MATERIAL_CHARACTERISTICS_ORDER = MATERIAL_CHARACTERISTICS_PROPS
LASER_INTERACTION_ORDER = LASER_INTERACTION_PROPS

MACHINE_SETTINGS_ORDER = [
    'powerRange', 'wavelength', 'pulseDuration', 'spotSize', 'repetitionRate',
    'fluenceThreshold', 'energyDensity', 'pulseWidth', 'beamDiameter',
    'scanSpeed', 'passCount', 'overlapRatio', 'dwellTime',
]


def ordered_dict_representer(dumper, data):
    """Custom YAML representer for OrderedDict"""
    return dumper.represent_dict(data.items())


def normalize_property_group(group_data: Dict, property_order: List[str]) -> OrderedDict:
    """Normalize property order within a group"""
    if not isinstance(group_data, dict):
        return group_data
    
    normalized = OrderedDict()
    
    # Add label, description, percentage first if they exist
    for key in ['label', 'description', 'percentage']:
        if key in group_data:
            normalized[key] = group_data[key]
    
    # Add properties in canonical order
    if 'properties' in group_data:
        properties = group_data['properties']
        ordered_properties = OrderedDict()
        
        # First add properties in canonical order
        for prop in property_order:
            if prop in properties:
                ordered_properties[prop] = properties[prop]
        
        # Then add any remaining properties not in the canonical list
        for prop, value in properties.items():
            if prop not in ordered_properties:
                ordered_properties[prop] = value
        
        normalized['properties'] = ordered_properties
    
    return normalized


def migrate_flat_to_grouped(mat_props: Dict) -> OrderedDict:
    """
    Migrate FLAT structure to GROUPED structure.
    
    FLAT: properties: { density: {...}, thermalConductivity: {...}, ... }
    GROUPED: properties:
               material_characteristics:
                 label: Material Characteristics
                 description: ...
                 properties: { density: {...}, ... }
               laser_material_interaction:
                 label: Laser-Material Interaction
                 description: ...
                 properties: { thermalConductivity: {...}, ... }
    """
    if not isinstance(mat_props, dict):
        return mat_props
    
    # Check if already grouped (has material_characteristics or laser_material_interaction keys)
    if 'material_characteristics' in mat_props or 'laser_material_interaction' in mat_props:
        # Already grouped, just normalize
        return normalize_material_properties(mat_props)
    
    # Migrate from FLAT to GROUPED
    grouped = OrderedDict()
    
    # Create material_characteristics group
    material_char_props = OrderedDict()
    for prop in MATERIAL_CHARACTERISTICS_ORDER:
        if prop in mat_props:
            material_char_props[prop] = mat_props[prop]
    
    # Add any other properties not in laser interaction list
    for prop, value in mat_props.items():
        if prop not in LASER_INTERACTION_PROPS and prop not in material_char_props:
            material_char_props[prop] = value
    
    if material_char_props:
        grouped['material_characteristics'] = OrderedDict([
            ('label', 'Material Characteristics'),
            ('description', 'Intrinsic physical, mechanical, chemical, and structural properties affecting cleaning outcomes and material integrity'),
            ('properties', material_char_props)
        ])
    
    # Create laser_material_interaction group
    laser_props = OrderedDict()
    for prop in LASER_INTERACTION_ORDER:
        if prop in mat_props:
            laser_props[prop] = mat_props[prop]
    
    if laser_props:
        grouped['laser_material_interaction'] = OrderedDict([
            ('label', 'Laser-Material Interaction'),
            ('description', 'Optical and thermal properties governing laser energy absorption, reflection, propagation, and ablation thresholds'),
            ('properties', laser_props)
        ])
    
    return grouped


def normalize_material_properties(mat_props: Dict) -> OrderedDict:
    """Normalize properties structure (assumes already grouped)"""
    if not isinstance(mat_props, dict):
        return mat_props
    
    normalized = OrderedDict()
    
    # Add groups in canonical order
    for group in PROPERTY_GROUP_ORDER:
        if group in mat_props:
            if group == 'material_characteristics':
                normalized[group] = normalize_property_group(mat_props[group], MATERIAL_CHARACTERISTICS_ORDER)
            elif group == 'laser_material_interaction':
                normalized[group] = normalize_property_group(mat_props[group], LASER_INTERACTION_ORDER)
            else:
                normalized[group] = mat_props[group]
    
    # Add any remaining groups not in canonical order
    for group, data in mat_props.items():
        if group not in normalized:
            normalized[group] = data
    
    return normalized


def normalize_machine_settings(settings: Dict) -> OrderedDict:
    """Normalize machine_settings order"""
    if not isinstance(settings, dict):
        return settings
    
    normalized = OrderedDict()
    
    # Add settings in canonical order
    for setting in MACHINE_SETTINGS_ORDER:
        if setting in settings:
            normalized[setting] = settings[setting]
    
    # Add any remaining settings
    for setting, value in settings.items():
        if setting not in normalized:
            normalized[setting] = value
    
    return normalized


def normalize_material_entry(material_data: Dict) -> OrderedDict:
    """Normalize a single material entry to canonical field order and GROUPED structure"""
    normalized = OrderedDict()
    
    # Add fields in canonical order
    for field in CANONICAL_ORDER:
        if field in material_data:
            if field == 'properties':
                # Migrate FLAT → GROUPED and normalize
                normalized[field] = migrate_flat_to_grouped(material_data[field])
            elif field == 'machine_settings':
                normalized[field] = normalize_machine_settings(material_data[field])
            else:
                normalized[field] = material_data[field]
    
    # Add any remaining fields not in canonical order
    for field, value in material_data.items():
        if field not in normalized:
            normalized[field] = value
    
    return normalized


def normalize_materials_yaml(materials_path: Path, dry_run: bool = False, specific_material: str = None) -> Dict:
    """
    Normalize all materials in Materials.yaml
    
    Args:
        materials_path: Path to Materials.yaml
        dry_run: If True, print changes without writing
        specific_material: If provided, only normalize this material
        
    Returns:
        Normalized materials data
    """
    print(f"📖 Loading materials from: {materials_path}")
    
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if 'materials' not in data:
        print("❌ No 'materials' section found in Materials.yaml")
        return data
    
    materials = data['materials']
    total_count = len(materials)
    normalized_count = 0
    
    print(f"📊 Found {total_count} materials")
    
    # Normalize each material
    normalized_materials = OrderedDict()
    
    for material_name, material_data in materials.items():
        # Skip if specific material requested and this isn't it
        if specific_material and material_name != specific_material:
            normalized_materials[material_name] = material_data
            continue
        
        print(f"  🔄 Normalizing: {material_name}")
        normalized_materials[material_name] = normalize_material_entry(material_data)
        normalized_count += 1
    
    data['materials'] = normalized_materials
    
    print(f"\n✅ Normalized {normalized_count} material(s)")
    
    if dry_run:
        print("\n🔍 DRY RUN - No changes written")
        return data
    
    # Write back to file
    print(f"\n💾 Writing normalized data to: {materials_path}")
    
    # Register OrderedDict representer
    yaml.add_representer(OrderedDict, ordered_dict_representer)
    
    with open(materials_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)
    
    print("✅ Normalization complete!")
    
    return data


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Normalize Materials.yaml structure')
    parser.add_argument('--dry-run', action='store_true', help='Print changes without writing')
    parser.add_argument('--material', type=str, help='Normalize only this specific material')
    parser.add_argument('--materials-yaml', type=str, default='data/materials/Materials.yaml',
                       help='Path to Materials.yaml file')
    
    args = parser.parse_args()
    
    materials_path = project_root / args.materials_yaml
    
    if not materials_path.exists():
        print(f"❌ Materials file not found: {materials_path}")
        sys.exit(1)
    
    try:
        normalize_materials_yaml(materials_path, dry_run=args.dry_run, specific_material=args.material)
    except Exception as e:
        print(f"❌ Error during normalization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
