#!/usr/bin/env python3
"""
Script to check which materials are missing thermal properties
"""

import yaml

def check_thermal_properties():
    # Load materials
    with open('data/materials.yaml') as f:
        data = yaml.safe_load(f)

    print('🔍 CHECKING MATERIALS FOR MISSING THERMAL PROPERTIES')
    print('=' * 60)
    
    incomplete_materials = []
    complete_materials = []
    
    # Check each category
    for category_name, category_data in data.get('category_ranges', {}).items():
        if 'items' in category_data:
            print(f'\n📂 {category_name.upper()} MATERIALS:')
            for item in category_data['items']:
                name = item.get('name', 'Unknown')
                
                # Check for thermal properties
                thermal_props = {
                    'density': 'density' in item,
                    'melting_point': 'melting_point' in item,
                    'thermal_conductivity': 'thermal_conductivity' in item,
                    'thermal_expansion': 'thermal_expansion' in item
                }
                
                thermal_count = sum(thermal_props.values())
                
                if thermal_count == 0:
                    status = '❌ NO thermal properties'
                    incomplete_materials.append((name, category_name, 'none'))
                elif thermal_count < 3:
                    status = f'⚠️  PARTIAL thermal properties ({thermal_count}/4)'
                    missing = [prop for prop, present in thermal_props.items() if not present]
                    incomplete_materials.append((name, category_name, 'partial', missing))
                else:
                    status = f'✅ COMPLETE thermal properties ({thermal_count}/4)'
                    complete_materials.append((name, category_name))
                    
                print(f'   {name:<35} {status}')
    
    # Summary
    print('\n' + '=' * 60)
    print('📊 SUMMARY:')
    print(f'✅ Complete materials: {len(complete_materials)}')
    print(f'⚠️  Incomplete materials: {len(incomplete_materials)}')
    
    if incomplete_materials:
        print('\n🔧 MATERIALS NEEDING THERMAL PROPERTIES:')
        for item in incomplete_materials:
            if len(item) == 3:  # No thermal properties
                name, category, status = item
                print(f'   {name} ({category}) - NO thermal properties')
            else:  # Partial thermal properties
                name, category, status, missing = item
                print(f'   {name} ({category}) - Missing: {", ".join(missing)}')

if __name__ == '__main__':
    check_thermal_properties()
