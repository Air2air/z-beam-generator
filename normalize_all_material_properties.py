#!/usr/bin/env python3
"""
Complete Pipeline Normalization: Remove ALL material-specific min/max from materials.yaml

This achieves full consistency with thermalDestruction pattern:
- Categories.yaml: category-wide min/max ranges ONLY
- materials.yaml: value, unit, confidence, research metadata ONLY (NO min/max)
- Frontmatter: combines value from materials + min/max from Categories

This removes material-specific uncertainty ranges in favor of category-wide ranges,
ensuring complete normalization across the entire property pipeline.
"""

import yaml
from pathlib import Path
from datetime import datetime

def normalize_material_properties(material_name, material_data):
    """Remove min/max from all properties in a material"""
    changes = []
    
    if 'properties' not in material_data:
        return changes
    
    props = material_data['properties']
    
    for prop_name, prop_data in props.items():
        if not isinstance(prop_data, dict):
            continue
        
        # Skip thermalDestruction - already normalized
        if prop_name == 'thermalDestruction':
            continue
        
        # Remove min/max from regular properties
        removed = []
        if 'min' in prop_data:
            del prop_data['min']
            removed.append('min')
        if 'max' in prop_data:
            del prop_data['max']
            removed.append('max')
        
        if removed:
            changes.append(f"{prop_name}: removed {', '.join(removed)}")
    
    return changes

def main():
    materials_file = Path('data/materials.yaml')
    
    print("=" * 70)
    print("Complete Pipeline Normalization: materials.yaml")
    print("=" * 70)
    print("\nRemoving ALL material-specific min/max ranges")
    print("Min/max will come from Categories.yaml (category-wide) ONLY")
    
    print("\n📖 Loading materials.yaml...")
    with open(materials_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if 'materials' not in data:
        print("❌ Error: No 'materials' key found")
        return
    
    # Create backup
    backup_file = materials_file.with_suffix(f'.yaml.backup_normalize_all_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    print(f"💾 Creating backup: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    materials = data['materials']
    total = 0
    changed = 0
    total_properties_cleaned = 0
    
    print("\n🔄 Normalizing all properties...")
    print("=" * 70)
    
    for material_name, material_data in materials.items():
        if not isinstance(material_data, dict):
            continue
        
        total += 1
        changes = normalize_material_properties(material_name, material_data)
        
        if changes:
            changed += 1
            total_properties_cleaned += len(changes)
            print(f"\n✅ {material_name}:")
            for change in changes:
                print(f"   • {change}")
    
    print("\n" + "=" * 70)
    print("\n📊 Summary:")
    print(f"   Total materials: {total}")
    print(f"   Materials normalized: {changed}")
    print(f"   Total properties cleaned: {total_properties_cleaned}")
    
    if changed > 0:
        print(f"\n💾 Writing fully normalized materials.yaml...")
        with open(materials_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)
        print(f"✅ Successfully normalized {materials_file}")
        print(f"📁 Backup saved to {backup_file}")
        
        print("\n" + "=" * 70)
        print("🎉 COMPLETE NORMALIZATION ACHIEVED!")
        print("=" * 70)
        print("\n✅ Categories.yaml: Category-wide min/max ONLY")
        print("✅ materials.yaml: Value/unit/confidence ONLY (no min/max)")
        print("✅ Generator: Combines values + category ranges")
        print("✅ Frontmatter: Shows both (value from material, min/max from category)")
        print("\n💯 ALL properties now follow same pattern as thermalDestruction!")
    else:
        print("\n✅ All materials already fully normalized")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
