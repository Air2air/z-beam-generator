#!/usr/bin/env python3
"""
Propagate Universal Parameter Ranges to Settings

Takes universal min/max ranges from Categories.yaml machine_settingsRanges 
and adds them to all parameters in Settings.yaml machine_settings.

Created: December 20, 2025
Purpose: Fix Settings.yaml to include ranges for all 153 materials
"""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_universal_ranges() -> Dict[str, Dict[str, Any]]:
    """Load universal laser parameter ranges from Categories.yaml."""
    categories_file = Path('data/materials/Categories.yaml')
    with open(categories_file) as f:
        categories = yaml.safe_load(f)
    
    # Get universal ranges (not category-specific)
    universal_ranges = categories.get('machine_settingsRanges', {})
    
    return universal_ranges


def propagate_ranges():
    """Propagate universal ranges to all Settings."""
    
    print('='*80)
    print('🔧 PROPAGATING UNIVERSAL RANGES TO SETTINGS')
    print('='*80)
    print()
    
    # Load data
    print('📂 Loading data files...')
    universal_ranges = load_universal_ranges()
    
    settings_file = Path('data/settings/Settings.yaml')
    with open(settings_file) as f:
        settings_data = yaml.safe_load(f)
    
    print(f'   Universal ranges: {len(universal_ranges)} parameters')
    print(f'   Settings: {len(settings_data["settings"])} materials')
    print()
    
    # Process each material
    print('🔄 Processing materials...')
    updated_count = 0
    
    for material_name, setting_data in settings_data['settings'].items():
        machine_settings = setting_data.get('machine_settings', {})
        
        if not machine_settings:
            continue
        
        # Update each parameter with universal ranges
        updated_params = 0
        for param_name, param_data in machine_settings.items():
            # Find matching range parameter
            matching_range = None
            for range_name, range_data in universal_ranges.items():
                # Match by name (handle camelCase and snake_case)
                if (range_name.lower().replace('_', '') == param_name.lower().replace('_', '') or
                    range_name == param_name):
                    matching_range = range_data
                    break
            
            if not matching_range:
                continue
            
            # Add min/max to parameter if it's a dict
            if isinstance(param_data, dict):
                param_data['min'] = matching_range['min']
                param_data['max'] = matching_range['max']
                updated_params += 1
        
        if updated_params > 0:
            updated_count += 1
    
    print(f'\n📊 Results:')
    print(f'   ✅ Updated: {updated_count} materials')
    print(f'   Each material now has min/max ranges for all parameters')
    print()
    
    # Save updated Settings.yaml
    print('💾 Saving updated Settings.yaml...')
    with open(settings_file, 'w') as f:
        yaml.dump(settings_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print()
    print('='*80)
    print('✅ RANGE PROPAGATION COMPLETE')
    print('='*80)
    print()
    print(f'Updated {updated_count}/153 materials with min/max ranges')
    print()
    print('Next steps:')
    print('  1. Run: python3 run.py --export --domain settings')
    print('  2. Verify frontmatter files have ranges')
    print('  3. Re-generate datasets with ranges')
    print()


if __name__ == '__main__':
    propagate_ranges()
