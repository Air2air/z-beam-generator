#!/usr/bin/env python3
"""
Remove Confidence Fields from Materials.yaml

Removes all 'confidence' fields from property values in materials.yaml.
Per user requirements: confidence tracking is no longer needed.

Date: November 2, 2025
"""

import yaml
from pathlib import Path
from datetime import datetime

materials_file = Path('materials/data/materials.yaml')
backup_file = Path(f'materials/data/materials_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml')

print("📋 Removing confidence fields from Materials.yaml...")
print(f"📂 Input: {materials_file}")
print(f"💾 Backup: {backup_file}\n")

# Load materials.yaml
with open(materials_file, 'r') as f:
    data = yaml.safe_load(f)

materials = data.get('materials', {})
confidence_removed = 0

for mat_name, mat_data in materials.items():
    # Check materialProperties
    mp = mat_data.get('materialProperties', {})
    
    for group_name, group_data in mp.items():
        if not isinstance(group_data, dict):
            continue
        
        # Iterate through properties in this group
        for prop_name, prop_data in group_data.items():
            if prop_name == 'label':
                continue
            
            if isinstance(prop_data, dict) and 'confidence' in prop_data:
                del prop_data['confidence']
                confidence_removed += 1
    
    # Check machineSettings
    ms = mat_data.get('machineSettings', {})
    if isinstance(ms, dict):
        for setting_name, setting_data in ms.items():
            if isinstance(setting_data, dict) and 'confidence' in setting_data:
                del setting_data['confidence']
                confidence_removed += 1

print(f"✅ Removed {confidence_removed} confidence fields\n")

# Create backup
print("💾 Creating backup...")
with open(backup_file, 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

# Write updated structure
print("📝 Writing updated structure...")
with open(materials_file, 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

print(f"\n✅ Confidence fields removed successfully!")
print(f"   Backup saved: {backup_file}")
print(f"   Materials updated: {materials_file}")

# Verify
print("\n🔍 Verifying removal...")
with open(materials_file, 'r') as f:
    verify_data = yaml.safe_load(f)

verify_materials = verify_data.get('materials', {})
remaining = 0
for mat_name, mat_data in verify_materials.items():
    mp = mat_data.get('materialProperties', {})
    for group_name, group_data in mp.items():
        if isinstance(group_data, dict):
            for prop_name, prop_data in group_data.items():
                if isinstance(prop_data, dict) and 'confidence' in prop_data:
                    remaining += 1

if remaining == 0:
    print("   ✅ No confidence fields remain")
else:
    print(f"   ⚠️  {remaining} confidence fields still present")
