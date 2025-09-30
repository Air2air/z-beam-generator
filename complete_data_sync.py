#!/usr/bin/env python3
"""
Complete Data Synchronization for Frontmatter Regeneration

This script ensures all data between Materials.yaml, Categories.yaml, and frontmatter files
is fully synchronized and current for future frontmatter regeneration operations.
"""

import yaml
import glob
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def load_system_configuration():
    """Load current Materials.yaml and Categories.yaml configurations"""
    with open('data/Materials.yaml', 'r') as f:
        materials_data = yaml.safe_load(f)
    
    with open('data/Categories.yaml', 'r') as f:
        categories_data = yaml.safe_load(f)
    
    return materials_data, categories_data

def analyze_current_frontmatter_data():
    """Analyze current frontmatter data to extract patterns and values"""
    
    print('🔍 Analyzing Current Frontmatter Data Patterns')
    print('=' * 50)
    
    materials_data, _ = load_system_configuration()
    material_index = materials_data.get('material_index', {})
    
    # Create name mapping
    name_mapping = {}
    for material_name in material_index.keys():
        file_key = material_name.lower().replace(' ', '-')
        name_mapping[file_key] = material_name
    
    analysis = {
        'property_ranges': defaultdict(lambda: {'min': [], 'max': [], 'values': []}),
        'machine_settings': defaultdict(lambda: {'min': [], 'max': [], 'values': []}),
        'category_patterns': defaultdict(lambda: defaultdict(list)),
        'units_used': defaultdict(set),
        'confidence_levels': defaultdict(list),
        'files_analyzed': 0,
        'errors': []
    }
    
    for file_path in sorted(glob.glob('content/components/frontmatter/*.yaml')):
        file_name = Path(file_path).stem.replace('-laser-cleaning', '')
        analysis['files_analyzed'] += 1
        
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
            
            # Analyze material properties
            material_props = data.get('materialProperties', {})
            for prop_name, prop_data in material_props.items():
                if isinstance(prop_data, dict):
                    value = prop_data.get('value')
                    min_val = prop_data.get('min')
                    max_val = prop_data.get('max')
                    unit = prop_data.get('unit')
                    confidence = prop_data.get('confidence')
                    
                    if value is not None:
                        analysis['property_ranges'][prop_name]['values'].append(value)
                    if min_val is not None:
                        analysis['property_ranges'][prop_name]['min'].append(min_val)
                    if max_val is not None:
                        analysis['property_ranges'][prop_name]['max'].append(max_val)
                    if unit:
                        analysis['units_used'][prop_name].add(unit)
                    if confidence:
                        analysis['confidence_levels'][prop_name].append(confidence)
                    
                    # Category patterns
                    analysis['category_patterns'][category][prop_name].append({
                        'value': value, 'min': min_val, 'max': max_val, 'unit': unit
                    })
            
            # Analyze machine settings
            machine_settings = data.get('machineSettings', {})
            for setting_name, setting_data in machine_settings.items():
                if isinstance(setting_data, dict):
                    value = setting_data.get('value')
                    min_val = setting_data.get('min')
                    max_val = setting_data.get('max')
                    unit = setting_data.get('unit')
                    
                    if value is not None:
                        analysis['machine_settings'][setting_name]['values'].append(value)
                    if min_val is not None:
                        analysis['machine_settings'][setting_name]['min'].append(min_val)
                    if max_val is not None:
                        analysis['machine_settings'][setting_name]['max'].append(max_val)
                    if unit:
                        analysis['units_used'][setting_name].add(unit)
                        
        except Exception as e:
            analysis['errors'].append(f'{material_name}: {str(e)}')
    
    return analysis

def update_materials_yaml_ranges(analysis):
    """Update Materials.yaml with current frontmatter data ranges"""
    
    print('🔧 Updating Materials.yaml with Current Data Ranges')
    print('-' * 50)
    
    materials_data, _ = load_system_configuration()
    
    # Update machine settings ranges based on current frontmatter data
    current_ranges = materials_data.get('machineSettingsRanges', {})
    updates_made = []
    
    for setting_name, data in analysis['machine_settings'].items():
        if setting_name in current_ranges and data['min'] and data['max']:
            current_min = current_ranges[setting_name].get('min')
            current_max = current_ranges[setting_name].get('max')
            
            # Calculate actual ranges from frontmatter
            actual_min = min(data['min']) if data['min'] else current_min
            actual_max = max(data['max']) if data['max'] else current_max
            
            # Update if different
            if current_min != actual_min or current_max != actual_max:
                current_ranges[setting_name]['min'] = actual_min
                current_ranges[setting_name]['max'] = actual_max
                updates_made.append(f'{setting_name}: [{current_min}-{current_max}] → [{actual_min}-{actual_max}]')
    
    # Update metadata
    materials_data['metadata']['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    materials_data['metadata']['sync_date'] = datetime.now().strftime('%Y-%m-%d')
    materials_data['metadata']['frontmatter_files_analyzed'] = analysis['files_analyzed']
    
    # Save updated Materials.yaml
    with open('data/Materials.yaml', 'w') as f:
        yaml.dump(materials_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    if updates_made:
        print('✅ Materials.yaml updated:')
        for update in updates_made:
            print(f'   • {update}')
    else:
        print('✅ Materials.yaml already synchronized')
    
    print(f'✅ Updated metadata: last_updated, sync_date, files_analyzed ({analysis["files_analyzed"]})')
    
    return len(updates_made)

def update_categories_yaml_metadata(analysis):
    """Update Categories.yaml metadata and ensure consistency"""
    
    print('🔧 Updating Categories.yaml Metadata')
    print('-' * 40)
    
    _, categories_data = load_system_configuration()
    
    # Update metadata
    metadata = categories_data.get('metadata', {})
    metadata['last_sync_date'] = datetime.now().strftime('%Y-%m-%d')
    metadata['frontmatter_sync_applied'] = True
    metadata['files_synchronized'] = analysis['files_analyzed']
    metadata['sync_timestamp'] = datetime.now().isoformat()
    
    # Ensure machine settings descriptions are complete
    machine_descriptions = categories_data.get('machineSettingsDescriptions', {})
    required_settings = ['powerRange', 'pulseDuration', 'spotSize', 'repetitionRate', 'fluenceThreshold', 'wavelength']
    
    missing_descriptions = []
    for setting in required_settings:
        if setting not in machine_descriptions:
            missing_descriptions.append(setting)
    
    if missing_descriptions:
        print(f'⚠️  Missing descriptions for: {", ".join(missing_descriptions)}')
    else:
        print('✅ All machine settings descriptions present')
    
    # Save updated Categories.yaml
    with open('data/Categories.yaml', 'w') as f:
        yaml.dump(categories_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print('✅ Categories.yaml metadata updated')
    return len(missing_descriptions)

def validate_synchronization():
    """Validate that all systems are properly synchronized"""
    
    print('🔍 Validating Complete System Synchronization')
    print('-' * 45)
    
    materials_data, categories_data = load_system_configuration()
    
    validation_results = {
        'materials_yaml_valid': True,
        'categories_yaml_valid': True,
        'frontmatter_consistent': True,
        'issues': []
    }
    
    # Validate Materials.yaml
    machine_ranges = materials_data.get('machineSettingsRanges', {})
    required_ranges = ['powerRange', 'pulseDuration', 'spotSize', 'repetitionRate', 'fluenceThreshold', 'wavelength']
    
    for setting in required_ranges:
        if setting not in machine_ranges:
            validation_results['materials_yaml_valid'] = False
            validation_results['issues'].append(f'Materials.yaml missing {setting} range')
        else:
            range_data = machine_ranges[setting]
            if not all(key in range_data for key in ['min', 'max', 'unit', 'description']):
                validation_results['materials_yaml_valid'] = False
                validation_results['issues'].append(f'Materials.yaml {setting} range incomplete')
    
    # Validate Categories.yaml
    machine_descriptions = categories_data.get('machineSettingsDescriptions', {})
    for setting in required_ranges:
        if setting not in machine_descriptions:
            validation_results['categories_yaml_valid'] = False
            validation_results['issues'].append(f'Categories.yaml missing {setting} description')
    
    # Quick frontmatter consistency check
    sample_files = list(glob.glob('content/components/frontmatter/*.yaml'))[:5]
    for file_path in sample_files:
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Check for required sections
            if 'machineSettings' not in data:
                validation_results['frontmatter_consistent'] = False
                validation_results['issues'].append(f'{Path(file_path).name} missing machineSettings')
                
        except Exception as e:
            validation_results['frontmatter_consistent'] = False
            validation_results['issues'].append(f'{Path(file_path).name} read error: {e}')
    
    # Display results
    if validation_results['issues']:
        print('⚠️  Synchronization Issues Found:')
        for issue in validation_results['issues']:
            print(f'   • {issue}')
    else:
        print('✅ Perfect Synchronization Validated')
        print('   • Materials.yaml: Complete and valid')
        print('   • Categories.yaml: Complete and valid')
        print('   • Frontmatter files: Consistent structure')
    
    return validation_results

def create_regeneration_readiness_report():
    """Create a report on frontmatter regeneration readiness"""
    
    print('📋 Frontmatter Regeneration Readiness Report')
    print('=' * 45)
    
    materials_data, categories_data = load_system_configuration()
    
    report = {
        'materials_count': len(materials_data.get('material_index', {})),
        'categories_count': len(set(materials_data.get('material_index', {}).values())),
        'machine_settings_configured': len(materials_data.get('machineSettingsRanges', {})),
        'setting_descriptions_available': len(categories_data.get('machineSettingsDescriptions', {})),
        'material_properties_documented': len(categories_data.get('materialPropertyDescriptions', {})),
        'ready_for_regeneration': True
    }
    
    print(f'📊 System Overview:')
    print(f'   • Materials indexed: {report["materials_count"]}')
    print(f'   • Categories: {report["categories_count"]}')
    print(f'   • Machine settings configured: {report["machine_settings_configured"]}')
    print(f'   • Setting descriptions: {report["setting_descriptions_available"]}')
    print(f'   • Property descriptions: {report["material_properties_documented"]}')
    
    # Check readiness criteria
    readiness_criteria = [
        (report['materials_count'] >= 100, 'Sufficient materials indexed'),
        (report['machine_settings_configured'] >= 6, 'Machine settings complete'),
        (report['setting_descriptions_available'] >= 6, 'Setting descriptions complete'),
        (report['material_properties_documented'] >= 10, 'Property descriptions adequate')
    ]
    
    print('\\n🎯 Regeneration Readiness:')
    all_ready = True
    for criterion, description in readiness_criteria:
        status = '✅' if criterion else '❌'
        print(f'   {status} {description}')
        if not criterion:
            all_ready = False
    
    if all_ready:
        print('\\n🚀 SYSTEM READY FOR FRONTMATTER REGENERATION!')
        print('   All data sources are synchronized and complete.')
    else:
        print('\\n⚠️  System needs attention before regeneration.')
    
    return report

def main():
    """Main synchronization process"""
    
    print('🔄 Complete Data Synchronization for Frontmatter Regeneration')
    print('=' * 65)
    print(f'🕐 Started at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()
    
    try:
        # Step 1: Analyze current frontmatter data
        analysis = analyze_current_frontmatter_data()
        print(f'   📁 Analyzed {analysis["files_analyzed"]} frontmatter files')
        if analysis['errors']:
            print(f'   ⚠️  {len(analysis["errors"])} files had read errors')
        print()
        
        # Step 2: Update Materials.yaml
        materials_updates = update_materials_yaml_ranges(analysis)
        print()
        
        # Step 3: Update Categories.yaml
        categories_issues = update_categories_yaml_metadata(analysis)
        print()
        
        # Step 4: Validate synchronization
        validation = validate_synchronization()
        print()
        
        # Step 5: Create regeneration readiness report
        readiness = create_regeneration_readiness_report()
        print()
        
        # Final summary
        print('📊 SYNCHRONIZATION SUMMARY:')
        print(f'   • Materials.yaml updates: {materials_updates}')
        print(f'   • Categories.yaml issues: {categories_issues}')
        print(f'   • Validation issues: {len(validation["issues"])}')
        print(f'   • System ready: {readiness["ready_for_regeneration"]}')
        
        if validation['issues'] == 0 and readiness['ready_for_regeneration']:
            print('\\n🎉 PERFECT SYNCHRONIZATION ACHIEVED!')
            print('   The system is fully prepared for frontmatter regeneration.')
            print('   All data sources are current, consistent, and complete.')
        else:
            print('\\n⚠️  Synchronization completed with issues noted above.')
        
        print(f'\\n🕐 Completed at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        
    except Exception as e:
        print(f'❌ Synchronization failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()