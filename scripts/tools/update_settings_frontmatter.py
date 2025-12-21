#!/usr/bin/env python3
"""
Update Settings Frontmatter with Machine Settings Ranges

Adds machine_settings (with min/max ranges) from Settings.yaml 
to all settings frontmatter files.

Created: December 20, 2025
Purpose: Complete settings frontmatter after range propagation
"""

import yaml
from pathlib import Path


def update_frontmatter():
    """Update all settings frontmatter files with machine_settings."""
    
    print('='*80)
    print('🔧 UPDATING SETTINGS FRONTMATTER WITH RANGES')
    print('='*80)
    print()
    
    # Load Settings.yaml
    print('📂 Loading Settings.yaml...')
    with open('data/settings/Settings.yaml') as f:
        settings_data = yaml.safe_load(f)
    
    print(f'   Materials in Settings.yaml: {len(settings_data["settings"])}')
    print()
    
    # Process frontmatter files
    frontmatter_dir = Path('../z-beam/frontmatter/settings')
    files = list(frontmatter_dir.glob('*.yaml'))
    print(f'📁 Frontmatter files: {len(files)}')
    print()
    
    print('🔄 Updating frontmatter files...')
    updated_count = 0
    empty_count = 0
    not_found_count = 0
    
    for settings_file in files:
        # Load frontmatter
        with open(settings_file) as f:
            frontmatter = yaml.safe_load(f)
        
        # Get material name (remove " Settings" suffix)
        material_name = frontmatter.get('name', '').replace(' Settings', '')
        
        # Find matching settings
        if material_name not in settings_data['settings']:
            not_found_count += 1
            continue
        
        machine_settings = settings_data['settings'][material_name].get('machine_settings', {})
        
        if not machine_settings:
            empty_count += 1
            continue
        
        # Update frontmatter
        frontmatter['machineSettings'] = machine_settings
        
        # Save
        with open(settings_file, 'w') as f:
            yaml.dump(frontmatter, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        updated_count += 1
    
    print()
    print('='*80)
    print('📊 RESULTS')
    print('='*80)
    print(f'   ✅ Updated: {updated_count} files')
    print(f'   ⚠️  Empty settings: {empty_count} files')
    print(f'   ❌ Not found: {not_found_count} files')
    print(f'   📁 Location: {frontmatter_dir}')
    print()
    
    if updated_count > 0:
        print('✅ Settings frontmatter now has complete machine_settings with min/max ranges!')
    else:
        print('⚠️  No files updated - check material name matching')


if __name__ == '__main__':
    update_frontmatter()
