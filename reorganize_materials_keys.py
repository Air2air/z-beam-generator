#!/usr/bin/env python3
"""
Materials.yaml Key Organization Script

This script reorganizes Materials.yaml to make material keys clear and easy to find by:
1. Moving the 'name' field to the top of each material entry
2. Confirming no materialProperties or machineSettings exist
3. Maintaining all other data integrity
"""

import yaml
import sys
from pathlib import Path
from collections import OrderedDict

def reorganize_materials_yaml():
    """Reorganize Materials.yaml for better key visibility"""
    
    print("🔧 Materials.yaml Key Organization")
    print("=" * 50)
    
    # Load current Materials.yaml
    materials_path = Path(__file__).parent / "data" / "Materials.yaml"
    print(f"📂 Loading: {materials_path}")
    
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Analyze current structure
    materials = data.get('materials', {})
    print(f"📦 Found {len(materials)} material categories")
    
    total_materials = 0
    reorganized_count = 0
    forbidden_keys_found = []
    
    # Check for forbidden keys and reorganize
    print("\n🔍 Processing materials...")
    
    for category, category_data in materials.items():
        items = category_data.get('items', [])
        total_materials += len(items)
        print(f"  📁 {category}: {len(items)} materials")
        
        for i, item in enumerate(items):
            # Check for forbidden keys
            forbidden_keys = ['materialProperties', 'machineSettings']
            for forbidden in forbidden_keys:
                if forbidden in item:
                    forbidden_keys_found.append({
                        'category': category,
                        'item_index': i,
                        'name': item.get('name', 'unnamed'),
                        'forbidden_key': forbidden
                    })
            
            # Reorganize keys - move name to the top
            if 'name' in item:
                # Create new ordered dict with name first
                new_item = OrderedDict()
                new_item['name'] = item['name']
                
                # Add all other keys in their original order
                for key, value in item.items():
                    if key != 'name':
                        new_item[key] = value
                
                # Replace the item
                category_data['items'][i] = dict(new_item)
                reorganized_count += 1
    
    # Report forbidden keys
    print(f"\n🚫 Checking for forbidden keys:")
    if forbidden_keys_found:
        print(f"  ❌ Found {len(forbidden_keys_found)} forbidden keys:")
        for found in forbidden_keys_found:
            print(f"    • {found['category']}/{found['name']}: {found['forbidden_key']}")
    else:
        print(f"  ✅ No forbidden keys found")
    
    # Report reorganization
    print(f"\n📋 Reorganization Summary:")
    print(f"  • Total materials processed: {total_materials}")
    print(f"  • Materials with name reorganized: {reorganized_count}")
    print(f"  • Materials without name: {total_materials - reorganized_count}")
    
    if reorganized_count > 0:
        # Save reorganized file
        print(f"\n💾 Saving reorganized Materials.yaml...")
        
        with open(materials_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"✅ Successfully reorganized {reorganized_count} materials")
        print(f"   Material names are now at the top of each entry for easy identification")
    else:
        print(f"ℹ️  No reorganization needed - all materials already properly organized")
    
    # Verify the changes
    print(f"\n🔍 Verification:")
    
    # Reload and check first few materials
    with open(materials_path, 'r', encoding='utf-8') as f:
        verify_data = yaml.safe_load(f)
    
    verify_materials = verify_data.get('materials', {})
    sample_count = 0
    
    for category, category_data in verify_materials.items():
        items = category_data.get('items', [])
        if items and sample_count < 3:  # Check first 3 materials
            first_item = items[0]
            if 'name' in first_item:
                keys = list(first_item.keys())
                name_position = keys.index('name') + 1
                print(f"  ✅ {category}/{first_item['name']}: name at position #{name_position}")
                sample_count += 1
    
    return {
        'total_materials': total_materials,
        'reorganized_count': reorganized_count,
        'forbidden_keys_found': len(forbidden_keys_found),
        'success': len(forbidden_keys_found) == 0
    }


def main():
    """Main execution function"""
    try:
        result = reorganize_materials_yaml()
        
        print(f"\n" + "=" * 50)
        if result['success']:
            print("✅ MATERIALS.YAML ORGANIZATION COMPLETED SUCCESSFULLY")
            print(f"📊 Summary:")
            print(f"  • {result['total_materials']} materials processed")  
            print(f"  • {result['reorganized_count']} materials reorganized")
            print(f"  • 0 forbidden keys found")
            print(f"  • Material names now easily visible at top of entries")
        else:
            print("⚠️  MATERIALS.YAML ORGANIZATION COMPLETED WITH WARNINGS")
            print(f"📊 Summary:")
            print(f"  • {result['total_materials']} materials processed")
            print(f"  • {result['reorganized_count']} materials reorganized") 
            print(f"  • {result['forbidden_keys_found']} forbidden keys found (need manual removal)")
        
        print(f"=" * 50)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()