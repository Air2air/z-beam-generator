#!/usr/bin/env python3
"""
Add longName field to all regulatory standards in Materials.yaml
"""

import yaml
from pathlib import Path
from datetime import datetime

# Organization name mappings
ORG_LONG_NAMES = {
    'FDA': 'Food and Drug Administration',
    'ANSI': 'American National Standards Institute',
    'IEC': 'International Electrotechnical Commission',
    'OSHA': 'Occupational Safety and Health Administration',
    'ISO': 'International Organization for Standardization',
    'EN': 'European Committee for Standardization',
    'ASTM': 'American Society for Testing and Materials',
    'EPA': 'Environmental Protection Agency',
    'Unknown': 'Unknown Organization'
}

def add_long_names(data: dict) -> int:
    """
    Add longName field to all regulatory standards in Materials.yaml.
    
    Returns:
        Number of standards updated
    """
    updated_count = 0
    
    materials = data.get('materials', {})
    
    for material_name, material_data in materials.items():
        if 'regulatoryStandards' not in material_data:
            continue
        
        standards = material_data['regulatoryStandards']
        if not isinstance(standards, list):
            continue
        
        for standard in standards:
            if not isinstance(standard, dict):
                continue
            
            if 'name' in standard and 'longName' not in standard:
                org_name = standard['name']
                if org_name in ORG_LONG_NAMES:
                    standard['longName'] = ORG_LONG_NAMES[org_name]
                    updated_count += 1
    
    return updated_count

def main():
    materials_path = Path(__file__).parent.parent.parent / 'data' / 'Materials.yaml'
    
    print(f"Loading {materials_path}...")
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Create backup
    backup_path = materials_path.parent / f'Materials.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml'
    print(f"Creating backup: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Add longNames
    print("\nAdding longName fields...")
    updated_count = add_long_names(data)
    
    # Save updated file
    print("\nSaving updated Materials.yaml...")
    with open(materials_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print("\n" + "=" * 60)
    print("✅ Complete!")
    print("=" * 60)
    print(f"📊 Standards updated: {updated_count}")
    print(f"💾 Backup saved: {backup_path.name}")
    print("=" * 60)

if __name__ == '__main__':
    main()
