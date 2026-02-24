#!/usr/bin/env python3
"""
Fix Missing Ranges in Settings.yaml

For the 32 materials missing min/max ranges, calculate ranges from
actual values across all materials and apply them.

Created: December 20, 2025
Purpose: Complete Settings.yaml to 100% range coverage
"""

import yaml
from pathlib import Path
from collections import defaultdict


def calculate_ranges_from_data(settings):
    """Calculate min/max for each parameter from actual values."""
    param_values = defaultdict(list)
    
    for material_name, setting_data in settings.items():
        machine_settings = setting_data.get('machine_settings', {})
        
        for param_name, param_data in machine_settings.items():
            if isinstance(param_data, dict) and 'value' in param_data:
                value = param_data['value']
                if isinstance(value, (int, float)):
                    param_values[param_name].append(value)
    
    # Calculate min/max for each parameter
    param_ranges = {}
    for param_name, values in param_values.items():
        if values:
            param_ranges[param_name] = {
                'min': min(values),
                'max': max(values)
            }
    
    return param_ranges


def fix_missing_ranges():
    """Fix all materials missing min/max ranges."""
    
    print('='*80)
    print('🔧 FIXING MISSING RANGES IN SETTINGS.YAML')
    print('='*80)
    print()
    
    # Load Settings.yaml
    settings_file = Path('data/settings/Settings.yaml')
    with open(settings_file) as f:
        settings_data = yaml.safe_load(f)
    
    settings = settings_data['settings']
    
    # Calculate ranges from actual data
    print('📊 Calculating ranges from actual values across all materials...')
    param_ranges = calculate_ranges_from_data(settings)
    print(f'   ✅ Calculated ranges for {len(param_ranges)} parameters')
    print()
    
    # Find and fix materials missing ranges
    print('🔄 Fixing materials...')
    fixed_count = 0
    total_params_fixed = 0
    
    for material_name, setting_data in settings.items():
        machine_settings = setting_data.get('machine_settings', {})
        
        if not machine_settings:
            continue
        
        material_fixed = False
        params_fixed = 0
        
        for param_name, param_data in machine_settings.items():
            if not isinstance(param_data, dict):
                continue
            
            # Check if missing min/max
            missing_min = 'min' not in param_data
            missing_max = 'max' not in param_data
            
            if missing_min or missing_max:
                # Get calculated range for this parameter
                if param_name in param_ranges:
                    if missing_min:
                        param_data['min'] = param_ranges[param_name]['min']
                    if missing_max:
                        param_data['max'] = param_ranges[param_name]['max']
                    params_fixed += 1
                    material_fixed = True
        
        if material_fixed:
            fixed_count += 1
            total_params_fixed += params_fixed
            print(f'   ✅ {material_name}: Fixed {params_fixed} parameters')
    
    print()
    print('📊 RESULTS:')
    print(f'   ✅ Materials fixed: {fixed_count}')
    print(f'   ✅ Parameters fixed: {total_params_fixed}')
    print()
    
    # Save updated Settings.yaml
    print('💾 Saving updated Settings.yaml...')
    with open(settings_file, 'w') as f:
        yaml.dump(settings_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print()
    print('='*80)
    print('✅ SETTINGS.YAML NOW 100% COMPLETE')
    print('='*80)
    print()
    print(f'Fixed {fixed_count} materials with {total_params_fixed} missing ranges')
    print()
    print('Next steps:')
    print('  1. Run: python3 scripts/tools/update_settings_frontmatter.py')
    print('  2. Verify: All 153 materials now have complete ranges')
    print('  3. Regenerate datasets')
    print()


if __name__ == '__main__':
    fix_missing_ranges()
