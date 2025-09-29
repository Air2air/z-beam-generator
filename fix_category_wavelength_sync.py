#!/usr/bin/env python3
"""
Wavelength Category Synchronization Fix

This script fixes category consistency issues by ensuring all materials
within each category use the proper researched wavelength ranges.
"""

import yaml
import glob
from pathlib import Path

def fix_category_wavelength_sync():
    """Fix wavelength ranges to be consistent within material categories"""
    
    print('🔄 Fixing Category Wavelength Synchronization')
    print('=' * 50)
    
    # Load material index
    with open('data/Materials.yaml', 'r') as f:
        materials_data = yaml.safe_load(f)
    material_index = materials_data.get('material_index', {})
    
    # Researched category standards (corrected to match current frontmatter)
    category_standards = {
        'metal': (355, 10640),
        'ceramic': (532, 10640),
        'glass': (532, 10640),
        'plastic': (355, 10640),  # Some use 532, but 355 is more comprehensive
        'composite': (355, 1080),  # Conservative range for mixed materials
        'wood': (355, 10640),
        'stone': (532, 10640),
        'masonry': (532, 10640),
        'semiconductor': (355, 1080)  # Precision range, avoid CO2 thermal damage
    }
    
    # Create name mapping
    name_mapping = {}
    for material_name in material_index.keys():
        file_key = material_name.lower().replace(' ', '-')
        name_mapping[file_key] = material_name
    
    stats = {
        'files_processed': 0,
        'files_updated': 0,
        'category_fixes': {},
        'errors': 0
    }
    
    print('📋 Applying category-specific wavelength ranges:')
    for category, (min_val, max_val) in category_standards.items():
        print(f'   {category}: {min_val}-{max_val} nm')
    print()
    
    for file_path in sorted(glob.glob('content/components/frontmatter/*.yaml')):
        file_name = Path(file_path).stem.replace('-laser-cleaning', '')
        stats['files_processed'] += 1
        
        # Find material name and category
        material_name = None
        if file_name in name_mapping:
            material_name = name_mapping[file_name]
        else:
            for key, value in name_mapping.items():
                if key.startswith(file_name) or file_name.startswith(key):
                    material_name = value
                    break
        
        if not material_name or material_name not in material_index:
            continue
            
        category = material_index[material_name]
        if category not in category_standards:
            continue
            
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            wavelength_data = data.get('machineSettings', {}).get('wavelength', {})
            current_min = wavelength_data.get('min')
            current_max = wavelength_data.get('max')
            
            # Get standard range for this category
            standard_min, standard_max = category_standards[category]
            
            # Check if update is needed
            if current_min != standard_min or current_max != standard_max:
                wavelength_data['min'] = standard_min
                wavelength_data['max'] = standard_max
                
                # Save the updated file
                with open(file_path, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                
                stats['files_updated'] += 1
                if category not in stats['category_fixes']:
                    stats['category_fixes'][category] = 0
                stats['category_fixes'][category] += 1
                
                print(f'✅ {material_name} ({category}): [{current_min}-{current_max}] → [{standard_min}-{standard_max}]')
                
        except Exception as e:
            print(f'❌ Error processing {material_name}: {e}')
            stats['errors'] += 1
    
    print()
    print('📊 CATEGORY SYNCHRONIZATION SUMMARY:')
    print(f'   📁 Files processed: {stats["files_processed"]}')
    print(f'   💾 Files updated: {stats["files_updated"]}')
    print(f'   ❌ Errors: {stats["errors"]}')
    
    if stats['category_fixes']:
        print('   📋 Updates by category:')
        for category, count in sorted(stats['category_fixes'].items()):
            print(f'      {category}: {count} materials')
    
    return stats

if __name__ == '__main__':
    fix_category_wavelength_sync()