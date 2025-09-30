#!/usr/bin/env python3
"""
Fix Wavelength Ranges in Frontmatter Files

This script fixes wavelength range issues in frontmatter files by:
1. Adding min/max ranges to files with null ranges
2. Fixing value/range boundary issues
3. Using category-appropriate wavelength ranges based on materials science
"""

import yaml
import glob
from pathlib import Path

def load_wavelength_standards():
    """Load the researched wavelength standards"""
    wavelength_standards = {
        'metal': {'range': (355, 10640), 'optimal': 1064},
        'ceramic': {'range': (532, 10640), 'optimal': 1064},
        'glass': {'range': (532, 10640), 'optimal': 1064},
        'plastic': {'range': (355, 10640), 'optimal': 1064},
        'composite': {'range': (355, 1064), 'optimal': 1064},
        'wood': {'range': (355, 10640), 'optimal': 1064},
        'stone': {'range': (532, 10640), 'optimal': 1064},
        'masonry': {'range': (532, 10640), 'optimal': 1064},
        'semiconductor': {'range': (355, 1064), 'optimal': 532}
    }
    return wavelength_standards

def load_material_index():
    """Load the material index from Materials.yaml"""
    with open('data/Materials.yaml', 'r') as f:
        materials_data = yaml.safe_load(f)
    return materials_data.get('material_index', {})

def create_name_mapping(material_index):
    """Create mapping from file names to material names"""
    name_mapping = {}
    for material_name in material_index.keys():
        # Convert to lowercase and replace spaces with hyphens
        file_key = material_name.lower().replace(' ', '-')
        name_mapping[file_key] = material_name
    return name_mapping

def fix_wavelength_ranges():
    """Fix wavelength ranges in all frontmatter files"""
    
    print('🔧 Fixing Wavelength Ranges in Frontmatter Files')
    print('=' * 60)
    
    # Load configuration
    wavelength_standards = load_wavelength_standards()
    material_index = load_material_index()
    name_mapping = create_name_mapping(material_index)
    
    stats = {
        'files_processed': 0,
        'null_ranges_fixed': 0,
        'boundary_issues_fixed': 0,
        'files_updated': 0,
        'errors': 0
    }
    
    files_updated = []
    
    for file_path in sorted(glob.glob('content/components/frontmatter/*.yaml')):
        file_name = Path(file_path).stem.replace('-laser-cleaning', '')
        stats['files_processed'] += 1
        
        # Find the actual material name and category
        material_name = None
        if file_name in name_mapping:
            material_name = name_mapping[file_name]
        else:
            # Try partial matching
            for key, value in name_mapping.items():
                if key.startswith(file_name) or file_name.startswith(key):
                    material_name = value
                    break
        
        if not material_name or material_name not in material_index:
            print(f'⚠️  Skipping {file_name}: Material not found in index')
            continue
            
        category = material_index[material_name]
        if category not in wavelength_standards:
            print(f'⚠️  Skipping {material_name}: Category {category} not in standards')
            continue
            
        try:
            # Load the file
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            machine_settings = data.get('machineSettings', {})
            if 'wavelength' not in machine_settings:
                continue
                
            wavelength_data = machine_settings['wavelength']
            current_value = wavelength_data.get('value')
            current_min = wavelength_data.get('min')
            current_max = wavelength_data.get('max')
            
            # Get category standards
            category_range = wavelength_standards[category]['range']
            min_standard, max_standard = category_range
            
            file_updated = False
            
            # Fix null ranges
            if current_min is None or current_max is None:
                wavelength_data['min'] = min_standard
                wavelength_data['max'] = max_standard
                stats['null_ranges_fixed'] += 1
                file_updated = True
                print(f'✅ Fixed null range: {material_name} ({category}) -> [{min_standard}-{max_standard}]')
            
            # Fix boundary issues (value equals min or max)
            elif current_value == current_min or current_value == current_max:
                # Adjust range to provide margin around the value
                if current_value == 1064:  # Most common case
                    if category in ['metal', 'plastic', 'wood']:
                        # Use full range for materials that can handle it
                        new_min, new_max = min_standard, max_standard
                    else:
                        # Use conservative range around 1064
                        new_min, new_max = max(min_standard, 532), min(max_standard, 1080)
                elif current_value == 532:
                    # Provide range around 532nm
                    new_min, new_max = max(min_standard, 355), min(max_standard, 1064)
                else:
                    # Use category standard range
                    new_min, new_max = min_standard, max_standard
                
                wavelength_data['min'] = new_min
                wavelength_data['max'] = new_max
                stats['boundary_issues_fixed'] += 1
                file_updated = True
                print(f'🔄 Fixed boundary: {material_name} value={current_value} range=[{current_min}-{current_max}] -> [{new_min}-{new_max}]')
            
            # Save the file if updated
            if file_updated:
                with open(file_path, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                stats['files_updated'] += 1
                files_updated.append(material_name)
                
        except Exception as e:
            print(f'❌ Error processing {material_name}: {e}')
            stats['errors'] += 1
    
    # Print summary
    print()
    print('📊 WAVELENGTH RANGE FIX SUMMARY:')
    print(f'   📁 Files processed: {stats["files_processed"]}')
    print(f'   🔧 Null ranges fixed: {stats["null_ranges_fixed"]}')
    print(f'   🔄 Boundary issues fixed: {stats["boundary_issues_fixed"]}')
    print(f'   💾 Files updated: {stats["files_updated"]}')
    print(f'   ❌ Errors: {stats["errors"]}')
    
    if files_updated:
        print()
        print(f'📝 Updated materials: {", ".join(sorted(files_updated)[:10])}' + 
              (f' (+{len(files_updated)-10} more)' if len(files_updated) > 10 else ''))
    
    return stats

if __name__ == '__main__':
    fix_wavelength_ranges()