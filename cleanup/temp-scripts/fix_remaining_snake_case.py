#!/usr/bin/env python3
"""
Fix remaining snake_case keys in Materials.yaml that were missed in the initial migration
"""

import yaml
import shutil
from datetime import datetime

def fix_remaining_snake_case():
    """Fix remaining snake_case keys in Materials.yaml"""
    
    # Create backup
    backup_path = f"data/materials_backup_fix_snake_case_{int(datetime.now().timestamp())}.yaml"
    shutil.copy("data/Materials.yaml", backup_path)
    print(f"Created backup: {backup_path}")
    
    # Load materials data
    with open("data/Materials.yaml", 'r') as f:
        data = yaml.safe_load(f)
    
    changes_made = 0
    
    # Fix machine_settings -> machineSettings
    if 'materials' in data:
        for category_name, category_data in data['materials'].items():
            if 'items' in category_data:
                for material in category_data['items']:
                    if 'machine_settings' in material:
                        # Move machine_settings to machineSettings
                        material['machineSettings'] = material.pop('machine_settings')
                        changes_made += 1
                        print(f"Fixed machine_settings -> machineSettings in {material.get('name', 'Unknown')}")
    
    # Save updated data
    with open("data/Materials.yaml", 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, 
                 sort_keys=False, width=120, indent=2)
    
    print(f"\nCompleted fixing remaining snake_case keys:")
    print(f"- Changes made: {changes_made}")
    print(f"- Backup created: {backup_path}")

if __name__ == "__main__":
    fix_remaining_snake_case()