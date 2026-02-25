#!/usr/bin/env python3
"""
Migrate All Settings to Library Enrichment System

Adds library relationship references to all settings in Settings.yaml.
Similar to migrate_all_materials.py but for settings domain.

Usage:
    python3 scripts/migrate_all_settings.py

Author: AI Assistant
Date: December 18, 2025
"""

import yaml
from pathlib import Path
from typing import Dict, Any


def migrate_settings():
    """Add library relationships to all settings"""
    
    # Load settings data
    settings_path = Path('data/settings/Settings.yaml')
    print(f'📖 Loading {settings_path}...')
    
    with open(settings_path) as f:
        data = yaml.safe_load(f)
    
    settings = data['settings']
    print(f'   Found {len(settings)} settings')
    
    # Track changes
    updated_count = 0
    
    # Add regulatory_standards to all settings
    for setting_id, setting_data in settings.items():
        # Initialize relationships dict if not exists
        if 'relationships' not in setting_data:
            setting_data['relationships'] = {}
        
        relationships = setting_data['relationships']
        
        # Add regulatory_standards if not exists
        if 'regulatory_standards' not in relationships:
            # All laser cleaning operations require these 2 core standards
            relationships['regulatory_standards'] = [
                {'type': 'regulatory_standards', 'id': 'osha-ppe-requirements'},
                {'type': 'regulatory_standards', 'id': 'ansi-z136-1-laser-safety'}
            ]
            updated_count += 1
        
        # Preserve existing related relationships
        # The relationships dict now has BOTH old linkages AND new library relationships
    
    print(f'\n✅ Updated {updated_count} settings with regulatory_standards')
    
    # Save back to file
    print(f'\n💾 Saving to {settings_path}...')
    with open(settings_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print('✅ Migration complete!')
    print(f'\nNext steps:')
    print(f'1. Update export/config/settings.yaml with library_enrichments section')
    print(f'2. Export settings and verify regulatory_standards_detail appears')


if __name__ == '__main__':
    migrate_settings()
