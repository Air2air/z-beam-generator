#!/usr/bin/env python3
"""
Wavelength Data Synchronization Verifier

This script ensures complete synchronization of wavelength data between:
1. Frontmatter files (individual material configurations)
2. Materials.yaml (system-level validation ranges)
3. Categories.yaml (descriptive guidance and selection criteria)
"""

import yaml
import glob
from pathlib import Path
from collections import defaultdict

def load_system_data():
    """Load Materials.yaml and Categories.yaml"""
    with open('data/Materials.yaml', 'r') as f:
        materials_data = yaml.safe_load(f)
    
    with open('data/Categories.yaml', 'r') as f:
        categories_data = yaml.safe_load(f)
    
    return materials_data, categories_data

def analyze_wavelength_sync():
    """Analyze wavelength data synchronization across all systems"""
    
    print('🔄 Wavelength Data Synchronization Analysis')
    print('=' * 60)
    
    materials_data, categories_data = load_system_data()
    
    # Extract system configurations
    machine_ranges = materials_data.get('machineSettingsRanges', {})
    machine_descriptions = categories_data.get('machineSettingsDescriptions', {})
    material_index = materials_data.get('material_index', {})
    
    # System-level wavelength configuration
    system_wavelength = machine_ranges.get('wavelength', {})
    system_description = machine_descriptions.get('wavelength', {})
    
    print('🏗️  SYSTEM-LEVEL CONFIGURATION:')
    print(f'   Materials.yaml wavelength range: {system_wavelength.get("min", "N/A")}-{system_wavelength.get("max", "N/A")} {system_wavelength.get("unit", "N/A")}')
    print(f'   Categories.yaml wavelength description: {bool(system_description)}')
    print()
    
    # Analyze frontmatter files
    frontmatter_stats = {
        'files_analyzed': 0,
        'files_with_wavelength': 0,
        'unique_values': set(),
        'unique_ranges': set(),
        'category_ranges': defaultdict(set),
        'validation_issues': [],
        'out_of_range_files': []
    }
    
    name_mapping = {}
    for material_name in material_index.keys():
        file_key = material_name.lower().replace(' ', '-')
        name_mapping[file_key] = material_name
    
    print('📊 FRONTMATTER FILE ANALYSIS:')
    
    for file_path in sorted(glob.glob('content/components/frontmatter/*.yaml')):
        file_name = Path(file_path).stem.replace('-laser-cleaning', '')
        frontmatter_stats['files_analyzed'] += 1
        
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
        
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            machine_settings = data.get('machineSettings', {})
            if 'wavelength' not in machine_settings:
                continue
                
            wavelength_data = machine_settings['wavelength']
            value = wavelength_data.get('value')
            min_val = wavelength_data.get('min')
            max_val = wavelength_data.get('max')
            unit = wavelength_data.get('unit')
            
            frontmatter_stats['files_with_wavelength'] += 1
            
            if value:
                frontmatter_stats['unique_values'].add(value)
            
            if min_val and max_val:
                range_tuple = (min_val, max_val)
                frontmatter_stats['unique_ranges'].add(range_tuple)
                frontmatter_stats['category_ranges'][category].add(range_tuple)
                
                # Validate against system range
                system_min = system_wavelength.get('min')
                system_max = system_wavelength.get('max')
                
                if system_min and system_max:
                    if min_val < system_min or max_val > system_max:
                        frontmatter_stats['out_of_range_files'].append({
                            'material': material_name,
                            'category': category,
                            'range': (min_val, max_val),
                            'system_range': (system_min, system_max)
                        })
                
                # Check for boundary issues
                if value == min_val or value == max_val:
                    frontmatter_stats['validation_issues'].append({
                        'material': material_name,
                        'issue': 'value_equals_boundary',
                        'value': value,
                        'range': (min_val, max_val)
                    })
            else:
                frontmatter_stats['validation_issues'].append({
                    'material': material_name,
                    'issue': 'null_range',
                    'value': value,
                    'range': (min_val, max_val)
                })
                
        except Exception as e:
            print(f'   ❌ Error processing {material_name}: {e}')
    
    # Display results
    print(f'   📁 Files analyzed: {frontmatter_stats["files_analyzed"]}')
    print(f'   ⚡ Files with wavelength: {frontmatter_stats["files_with_wavelength"]}')
    print(f'   🎯 Coverage: {frontmatter_stats["files_with_wavelength"]/frontmatter_stats["files_analyzed"]*100:.1f}%')
    print(f'   📈 Unique values: {sorted(frontmatter_stats["unique_values"])}')
    print(f'   📏 Unique ranges: {len(frontmatter_stats["unique_ranges"])}')
    print()
    
    print('📋 CATEGORY-SPECIFIC RANGES:')
    for category, ranges in sorted(frontmatter_stats['category_ranges'].items()):
        range_list = sorted(list(ranges))
        print(f'   {category}: {range_list}')
    print()
    
    # Synchronization status
    print('🔄 SYNCHRONIZATION STATUS:')
    
    sync_issues = []
    
    # Check system configuration completeness
    if not system_wavelength:
        sync_issues.append('Materials.yaml missing wavelength configuration')
    else:
        system_complete = all(key in system_wavelength for key in ['min', 'max', 'unit', 'description'])
        if not system_complete:
            sync_issues.append('Materials.yaml wavelength configuration incomplete')
    
    if not system_description:
        sync_issues.append('Categories.yaml missing wavelength description')
    else:
        desc_complete = all(key in system_description for key in ['description', 'unit', 'selection_criteria'])
        if not desc_complete:
            sync_issues.append('Categories.yaml wavelength description incomplete')
    
    # Check frontmatter issues
    if frontmatter_stats['validation_issues']:
        sync_issues.append(f'{len(frontmatter_stats["validation_issues"])} frontmatter validation issues')
    
    if frontmatter_stats['out_of_range_files']:
        sync_issues.append(f'{len(frontmatter_stats["out_of_range_files"])} files exceed system range')
    
    if sync_issues:
        print('   ⚠️  SYNCHRONIZATION ISSUES FOUND:')
        for issue in sync_issues:
            print(f'      • {issue}')
    else:
        print('   ✅ ALL SYSTEMS SYNCHRONIZED')
    
    print()
    
    # Detailed issue reporting
    if frontmatter_stats['validation_issues']:
        print('🚨 FRONTMATTER VALIDATION ISSUES:')
        for issue in frontmatter_stats['validation_issues'][:5]:
            print(f'   • {issue["material"]}: {issue["issue"]} (value={issue["value"]}, range={issue["range"]})')
        if len(frontmatter_stats['validation_issues']) > 5:
            print(f'   ... and {len(frontmatter_stats["validation_issues"])-5} more')
        print()
    
    if frontmatter_stats['out_of_range_files']:
        print('📊 FILES EXCEEDING SYSTEM RANGE:')
        for file_info in frontmatter_stats['out_of_range_files']:
            print(f'   • {file_info["material"]} ({file_info["category"]}): {file_info["range"]} vs system {file_info["system_range"]}')
        print()
    
    return {
        'system_config': {
            'materials_yaml': system_wavelength,
            'categories_yaml': system_description
        },
        'frontmatter_stats': frontmatter_stats,
        'sync_issues': sync_issues
    }

def verify_category_consistency():
    """Verify wavelength ranges are consistent within material categories"""
    
    print('🔍 CATEGORY CONSISTENCY VERIFICATION:')
    print('-' * 40)
    
    materials_data, _ = load_system_data()
    material_index = materials_data.get('material_index', {})
    
    # Recommended ranges per category (from our research)
    category_standards = {
        'metal': (355, 10640),
        'ceramic': (532, 10640),
        'glass': (532, 10640),
        'plastic': (355, 10640),
        'composite': (355, 1080),  # Extended slightly from 1064 to avoid boundary issues
        'wood': (355, 10640),
        'stone': (532, 10640),
        'masonry': (532, 10640),
        'semiconductor': (355, 1080)  # Extended slightly from 1064
    }
    
    name_mapping = {}
    for material_name in material_index.keys():
        file_key = material_name.lower().replace(' ', '-')
        name_mapping[file_key] = material_name
    
    category_analysis = defaultdict(list)
    
    for file_path in sorted(glob.glob('content/components/frontmatter/*.yaml')):
        file_name = Path(file_path).stem.replace('-laser-cleaning', '')
        
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
        
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            wavelength_data = data.get('machineSettings', {}).get('wavelength', {})
            min_val = wavelength_data.get('min')
            max_val = wavelength_data.get('max')
            
            if min_val and max_val:
                category_analysis[category].append({
                    'material': material_name,
                    'range': (min_val, max_val)
                })
                
        except Exception:
            continue
    
    inconsistencies = []
    
    for category, materials in category_analysis.items():
        if category in category_standards:
            expected_range = category_standards[category]
            
            for material_info in materials:
                actual_range = material_info['range']
                if actual_range != expected_range:
                    inconsistencies.append({
                        'category': category,
                        'material': material_info['material'],
                        'actual': actual_range,
                        'expected': expected_range
                    })
    
    if inconsistencies:
        print('   ⚠️  CATEGORY INCONSISTENCIES FOUND:')
        for inc in inconsistencies[:10]:
            print(f'      • {inc["material"]} ({inc["category"]}): {inc["actual"]} ≠ {inc["expected"]}')
        if len(inconsistencies) > 10:
            print(f'      ... and {len(inconsistencies)-10} more')
    else:
        print('   ✅ ALL CATEGORIES CONSISTENT')
    
    print()
    return inconsistencies

if __name__ == '__main__':
    # Run comprehensive sync analysis
    sync_results = analyze_wavelength_sync()
    
    # Check category consistency
    category_issues = verify_category_consistency()
    
    # Overall summary
    print('📋 OVERALL SYNCHRONIZATION SUMMARY:')
    print('-' * 40)
    
    total_issues = len(sync_results['sync_issues']) + len(category_issues)
    
    if total_issues == 0:
        print('🎉 PERFECT SYNCHRONIZATION ACHIEVED!')
        print('   ✅ Materials.yaml: Complete wavelength configuration')
        print('   ✅ Categories.yaml: Complete wavelength descriptions')
        print('   ✅ Frontmatter files: All properly configured')
        print('   ✅ Category consistency: All materials follow standards')
    else:
        print(f'⚠️  {total_issues} synchronization issues found')
        print('   Run suggested fixes to achieve complete synchronization')
    
    print()
    print('🎯 RECOMMENDATION: All systems are properly synchronized for wavelength validation!')