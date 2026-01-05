#!/usr/bin/env python3
"""
Fix Empty Relationship Lists

Converts empty list relationships to proper dict structure with presentation/items.

Usage:
    python3 scripts/migration/fix_empty_relationship_lists.py
"""

import yaml
from pathlib import Path

def fix_empty_lists_in_relationships(data_dict):
    """Convert any empty list relationships to dict structure."""
    fixed_count = 0
    
    for entity_id, entity_data in data_dict.items():
        if 'relationships' not in entity_data:
            continue
        
        relationships = entity_data['relationships']
        if not isinstance(relationships, dict):
            continue
        
        for rel_name, rel_data in relationships.items():
            # If it's an empty list, convert to dict
            if isinstance(rel_data, list) and len(rel_data) == 0:
                relationships[rel_name] = {
                    'presentation': 'card',
                    'items': []
                }
                print(f"  Fixed: {entity_id}.{rel_name} (empty list → dict)")
                fixed_count += 1
    
    return fixed_count

def main():
    print("=" * 70)
    print("FIXING EMPTY RELATIONSHIP LISTS")
    print("=" * 70)
    
    total_fixed = 0
    
    # Fix contaminants
    print("\n📋 Fixing Contaminants.yaml...")
    cont_path = Path('data/contaminants/Contaminants.yaml')
    with open(cont_path, 'r', encoding='utf-8') as f:
        cont_data = yaml.safe_load(f)
    
    fixed = fix_empty_lists_in_relationships(cont_data['contamination_patterns'])
    if fixed > 0:
        with open(cont_path, 'w', encoding='utf-8') as f:
            yaml.dump(cont_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"   ✅ Fixed {fixed} relationships in Contaminants.yaml")
        total_fixed += fixed
    else:
        print(f"   ✓ No fixes needed")
    
    # Fix settings
    print("\n📋 Fixing Settings.yaml...")
    settings_path = Path('data/settings/Settings.yaml')
    with open(settings_path, 'r', encoding='utf-8') as f:
        settings_data = yaml.safe_load(f)
    
    fixed = fix_empty_lists_in_relationships(settings_data['settings'])
    if fixed > 0:
        with open(settings_path, 'w', encoding='utf-8') as f:
            yaml.dump(settings_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"   ✅ Fixed {fixed} relationships in Settings.yaml")
        total_fixed += fixed
    else:
        print(f"   ✓ No fixes needed")
    
    # Fix materials (just in case)
    print("\n📋 Checking Materials.yaml...")
    mat_path = Path('data/materials/Materials.yaml')
    with open(mat_path, 'r', encoding='utf-8') as f:
        mat_data = yaml.safe_load(f)
    
    fixed = fix_empty_lists_in_relationships(mat_data['materials'])
    if fixed > 0:
        with open(mat_path, 'w', encoding='utf-8') as f:
            yaml.dump(mat_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"   ✅ Fixed {fixed} relationships in Materials.yaml")
        total_fixed += fixed
    else:
        print(f"   ✓ No fixes needed")
    
    # Fix compounds (just in case)
    print("\n📋 Checking Compounds.yaml...")
    comp_path = Path('data/compounds/Compounds.yaml')
    with open(comp_path, 'r', encoding='utf-8') as f:
        comp_data = yaml.safe_load(f)
    
    fixed = fix_empty_lists_in_relationships(comp_data['compounds'])
    if fixed > 0:
        with open(comp_path, 'w', encoding='utf-8') as f:
            yaml.dump(comp_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"   ✅ Fixed {fixed} relationships in Compounds.yaml")
        total_fixed += fixed
    else:
        print(f"   ✓ No fixes needed")
    
    print("\n" + "=" * 70)
    print(f"✅ COMPLETE: Fixed {total_fixed} empty relationship lists")
    print("=" * 70)

if __name__ == '__main__':
    main()
