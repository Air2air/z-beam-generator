#!/usr/bin/env python3
"""
Restore description fields in regulatoryStandards that were removed by mistake.
The description field should be kept in regulatoryStandards items.
"""

import yaml
from pathlib import Path
from datetime import datetime


# Standard regulatory descriptions (to restore if missing)
STANDARD_DESCRIPTIONS = {
    'FDA': 'FDA 21 CFR 1040.10 - Laser Product Performance Standards',
    'ANSI': 'ANSI Z136.1 - Safe Use of Lasers',
    'IEC': 'IEC 60825 - Safety of Laser Products',
    'OSHA': 'OSHA 29 CFR 1926.95 - Personal Protective Equipment'
}


def restore_regulatory_descriptions(material_data):
    """Restore description field in regulatoryStandards if missing"""
    if 'regulatoryStandards' not in material_data:
        return 0
    
    regs = material_data['regulatoryStandards']
    if not isinstance(regs, list):
        return 0
    
    restored = 0
    for reg in regs:
        if not isinstance(reg, dict):
            continue
        
        # If description is missing, try to restore it
        if 'description' not in reg:
            name = reg.get('name', '')
            if name in STANDARD_DESCRIPTIONS:
                reg['description'] = STANDARD_DESCRIPTIONS[name]
                restored += 1
            elif 'longName' in reg:
                # Create description from longName if available
                reg['description'] = f"{name} - {reg['longName']}"
                restored += 1
    
    return restored


def main():
    print("=" * 60)
    print("RESTORE REGULATORY STANDARDS DESCRIPTIONS")
    print("=" * 60)
    print()
    
    # Load Materials.yaml
    materials_file = Path('data/materials/Materials.yaml')
    print(f"Loading {materials_file}...")
    
    with open(materials_file, 'r') as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {})
    print(f"✅ Loaded {len(materials)} materials\n")
    
    # Track changes
    total_restored = 0
    materials_modified = 0
    
    # Restore descriptions in each material
    for mat_name, mat_data in materials.items():
        if not isinstance(mat_data, dict):
            continue
        
        restored = restore_regulatory_descriptions(mat_data)
        if restored > 0:
            total_restored += restored
            materials_modified += 1
    
    # Print summary
    print("Restoration Summary:")
    print("=" * 60)
    print(f"  Descriptions restored:        {total_restored:3d} instances")
    print(f"  Materials modified:           {materials_modified:3d}/{len(materials)}")
    print("=" * 60)
    print()
    
    if total_restored == 0:
        print("✅ No changes needed - descriptions already present")
        return
    
    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = Path(f'data/materials/backups/materials_backup_{timestamp}.yaml')
    backup_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(materials_file, 'r') as f:
        backup_content = f.read()
    with open(backup_file, 'w') as f:
        f.write(backup_content)
    print(f'✅ Backup created: {backup_file}')
    
    # Save updated data
    with open(materials_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)
    print(f'✅ Saved: {materials_file}')
    
    print()
    print('✅ Restoration complete!')
    print(f'   - Restored {total_restored} description fields in regulatoryStandards')


if __name__ == '__main__':
    main()
