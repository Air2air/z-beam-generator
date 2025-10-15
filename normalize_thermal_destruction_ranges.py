#!/usr/bin/env python3
"""
Normalize thermalDestruction in materials.yaml to match standard property pattern.

Issue: thermalDestruction.point contains material-specific min/max values.
Fix: Remove min/max from materials.yaml - they should come from Categories.yaml like all other properties.

This ensures thermalDestruction follows the same pipeline as all other properties:
- Categories.yaml: category-wide min/max ranges
- materials.yaml: material-specific value, unit, confidence, research metadata
- Generator: combines value from materials.yaml with min/max from Categories.yaml
"""

import yaml
from pathlib import Path
from datetime import datetime

def normalize_material(material_name, material_data):
    """Remove material-specific min/max from thermalDestruction.point"""
    changes = []
    
    if 'properties' not in material_data:
        return changes
    
    props = material_data['properties']
    
    if 'thermalDestruction' not in props:
        return changes
    
    td = props['thermalDestruction']
    if not isinstance(td, dict) or 'point' not in td:
        return changes
    
    point = td['point']
    if not isinstance(point, dict):
        return changes
    
    # Remove material-specific min/max (should come from Categories.yaml)
    removed = []
    if 'min' in point:
        del point['min']
        removed.append('min')
    if 'max' in point:
        del point['max']
        removed.append('max')
    
    if removed:
        changes.append(f"Removed material-specific {', '.join(removed)} from thermalDestruction.point")
    
    return changes

def main():
    materials_file = Path('data/materials.yaml')
    
    print("📖 Loading materials.yaml...")
    with open(materials_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if 'materials' not in data:
        print("❌ Error: No 'materials' key found")
        return
    
    # Create backup
    backup_file = materials_file.with_suffix(f'.yaml.backup_normalize_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    print(f"💾 Creating backup: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    materials = data['materials']
    total = 0
    changed = 0
    
    print("\n🔄 Normalizing thermalDestruction ranges...")
    print("=" * 70)
    
    for material_name, material_data in materials.items():
        if not isinstance(material_data, dict):
            continue
        
        total += 1
        changes = normalize_material(material_name, material_data)
        
        if changes:
            changed += 1
            print(f"\n✅ {material_name}:")
            for change in changes:
                print(f"   • {change}")
    
    print("\n" + "=" * 70)
    print(f"\n📊 Summary:")
    print(f"   Total materials: {total}")
    print(f"   Materials normalized: {changed}")
    
    if changed > 0:
        print(f"\n💾 Writing normalized materials.yaml...")
        with open(materials_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)
        print(f"✅ Successfully normalized {materials_file}")
        print(f"📁 Backup saved to {backup_file}")
    else:
        print(f"\n✅ All materials already normalized")
    
    print(f"\n✨ Done!")

if __name__ == '__main__':
    main()
