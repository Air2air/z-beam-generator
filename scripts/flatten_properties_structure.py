#!/usr/bin/env python3
"""
Flatten Properties Structure Script

Removes the nested 'properties' key from materialProperties groups.
Moves properties directly under material_characteristics and laser_material_interaction.

Before:
  material_characteristics:
    label: Material Characteristics
    properties:
      density: {...}
      hardness: {...}

After:
  material_characteristics:
    label: Material Characteristics
    density: {...}
    hardness: {...}

Date: November 2, 2025
"""

import yaml
from pathlib import Path
from datetime import datetime

# Backup materials.yaml first
materials_file = Path('materials/data/materials.yaml')
backup_file = Path(f'materials/data/materials_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml')

print("📋 Flattening materialProperties structure...")
print(f"📂 Input: {materials_file}")
print(f"💾 Backup: {backup_file}\n")

# Load materials.yaml
with open(materials_file, 'r') as f:
    data = yaml.safe_load(f)

materials = data.get('materials', {})
flattened_count = 0

for mat_name, mat_data in materials.items():
    mp = mat_data.get('materialProperties', {})
    
    # Flatten material_characteristics
    mc = mp.get('material_characteristics', {})
    if 'properties' in mc:
        props = mc.pop('properties')
        mc.update(props)
        flattened_count += 1
    
    # Flatten laser_material_interaction
    li = mp.get('laser_material_interaction', {})
    if 'properties' in li:
        props = li.pop('properties')
        li.update(props)

print(f"✅ Flattened {flattened_count} materials\n")

# Create backup
print(f"💾 Creating backup...")
with open(backup_file, 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

# Write flattened structure
print(f"📝 Writing flattened structure...")
with open(materials_file, 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

print(f"\n✅ Structure flattened successfully!")
print(f"   Backup saved: {backup_file}")
print(f"   Materials updated: {materials_file}")
