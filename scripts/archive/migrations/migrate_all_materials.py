#!/usr/bin/env python3
"""
Materials Domain Migration Script

Adds library relationships to all materials in Materials.yaml:
- regulatory_standards (FDA, OSHA, ANSI, etc.)
- material_applications (industry uses)
- material_properties (thermal, mechanical)

Usage:
    python3 scripts/migration/migrate_all_materials.py
"""

import yaml
from pathlib import Path
from typing import Dict, Any

# Regulatory standard mappings by material category and usage
# IDs must match those in data/regulatory/RegulatoryStandards.yaml
REGULATORY_MAPPING = {
    # Medical/healthcare materials
    'medical': ['fda-laser-product-performance', 'osha-ppe-requirements', 'ansi-z136-1-laser-safety'],
    'dental': ['fda-laser-product-performance', 'ansi-z136-1-laser-safety'],
    
    # Industrial materials
    'metal': ['osha-ppe-requirements', 'ansi-z136-1-laser-safety', 'ce-machinery-directive'],
    'ceramic': ['osha-ppe-requirements', 'ansi-z136-1-laser-safety', 'ce-machinery-directive'],
    'stone': ['osha-ppe-requirements', 'ansi-z136-1-laser-safety'],
    'wood': ['osha-ppe-requirements', 'ansi-z136-1-laser-safety'],
    'composite': ['osha-ppe-requirements', 'ansi-z136-1-laser-safety', 'reach-chemical-restrictions'],
    
    # Electronics/technology
    'semiconductor': ['iec-60825-laser-safety', 'ce-machinery-directive', 'rohs-directive'],
    
    # Default fallback
    'default': ['osha-ppe-requirements', 'ansi-z136-1-laser-safety']
}

# Material application mappings by category
APPLICATION_MAPPING = {
    'metal': 'industrial-manufacturing',
    'ceramic': 'industrial-manufacturing',
    'stone': 'restoration-conservation',
    'wood': 'restoration-conservation',
    'composite': 'aerospace-automotive',
    'semiconductor': 'microelectronics',
    'glass': 'industrial-manufacturing',
    'polymer': 'industrial-manufacturing',
    'textile': 'restoration-conservation'
}

# Material property set mappings by category
PROPERTY_MAPPING = {
    'metal': 'metals-high-conductivity',
    'ceramic': 'ceramics-high-hardness',
    'stone': 'stone-porous',
    'wood': 'organic-low-density',
    'composite': 'composites-layered',
    'semiconductor': 'semiconductors-precision',
    'glass': 'glass-transparent',
    'polymer': 'polymers-low-melting',
    'textile': 'textiles-fibrous'
}


def determine_regulatory_standards(material: Dict[str, Any]) -> list:
    """Determine which regulatory standards apply to material."""
    category = material.get('category', '').lower()
    
    # Check for medical/dental applications
    desc = material.get('description', '').lower()
    if 'medical' in desc or 'surgical' in desc:
        standards = REGULATORY_MAPPING.get('medical', [])
    elif 'dental' in desc:
        standards = REGULATORY_MAPPING.get('dental', [])
    else:
        # Use category mapping
        standards = REGULATORY_MAPPING.get(category, REGULATORY_MAPPING['default'])
    
    return [{'type': 'regulatory_standards', 'id': std_id} for std_id in standards]


def determine_material_application(material: Dict[str, Any]) -> list:
    """Determine material application type."""
    category = material.get('category', '').lower()
    app_id = APPLICATION_MAPPING.get(category, 'industrial-manufacturing')
    
    return [{'type': 'material_applications', 'id': app_id}]


def determine_material_properties(material: Dict[str, Any]) -> list:
    """Determine material property set."""
    category = material.get('category', '').lower()
    prop_id = PROPERTY_MAPPING.get(category, 'metals-high-conductivity')
    
    return [{'type': 'material_properties', 'id': prop_id}]


def add_relationships_to_material(material_id: str, material: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create library relationships for a material.
    
    Returns dict with 1 relationship type:
    - regulatory_standards (material_applications and material_properties disabled until library files populated)
    """
    relationships = {
        'regulatory_standards': determine_regulatory_standards(material)
        # Disabled until library files are populated:
        # 'material_applications': determine_material_application(material),
        # 'material_properties': determine_material_properties(material)
    }
    
    return relationships


def main():
    """Migrate all materials to library relationships."""
    
    print("=" * 80)
    print("BATCH MIGRATION: All Materials → Library Relationships")
    print("=" * 80)
    
    # Load Materials.yaml
    materials_file = Path(__file__).parent.parent.parent / 'data' / 'materials' / 'Materials.yaml'
    print(f"Loading: {materials_file}")
    
    with open(materials_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {})
    print(f"✅ Found {len(materials)} materials\n")
    
    # Create backup
    backup_file = materials_file.with_suffix('.yaml.pre-migration-backup')
    print(f"Creating backup: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"✅ Backup created\n")
    
    # Migrate each material
    print("Migrating materials:")
    migrated = 0
    skipped = 0
    
    for material_id, material in materials.items():
        # Skip if already has library relationships
        rels = material.get('relationships', {})
        has_library_rels = 'regulatory_standards' in rels
        if has_library_rels:
            print(f"  ⏭️  {material_id} (already has regulatory_standards)")
            skipped += 1
            continue
        
        # Add relationships
        relationships = add_relationships_to_material(material_id, material)
        
        # Merge with existing relationships (preserve old linkages)
        if 'relationships' not in material:
            material['relationships'] = {}
        material['relationships'].update(relationships)
        
        # Show what was assigned
        reg_count = len(relationships['regulatory_standards'])
        
        print(f"  ✅ {material_id}")
        print(f"      Regulatory standards: {reg_count}")
        # print(f"      Application: {app_id}")  # Disabled
        # print(f"      Properties: {prop_id}")  # Disabled
        
        migrated += 1
    
    print(f"\nMigrated: {migrated}/{len(materials)}")
    print(f"Skipped: {skipped}/{len(materials)}\n")
    
    # Save updated file
    print(f"Saving updated file: {materials_file}")
    with open(materials_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"✅ File saved\n")
    
    print("=" * 80)
    print("✅ BATCH MIGRATION COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print(f"1. Review relationships in {materials_file}")
    print("2. Export test: python3 run.py --export --domain materials --item aluminum-laser-cleaning")
    print("3. Export all: python3 run.py --export --domain materials --all")
    print("4. Verify enriched output in ../z-beam/frontmatter/materials/")
    print("\nTo restore original:")
    print(f"  cp {backup_file} {materials_file}")


if __name__ == '__main__':
    main()
