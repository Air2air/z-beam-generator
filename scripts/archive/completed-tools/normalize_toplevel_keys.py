#!/usr/bin/env python3
"""
Normalize top-level keys in source data files to camelCase

Core Principle: Software metadata uses camelCase, domain data uses snake_case
Top-level keys are software metadata, so they should be camelCase.
"""

import yaml
from pathlib import Path
from typing import Dict, Any

# Top-level key mappings (snake_case → camelCase)
KEY_MAPPINGS = {
    'schema_version': 'schemaVersion',
    'last_updated': 'lastUpdated',
    'category_metadata': 'categoryMetadata',
    'material_index': 'materialIndex',
    'contaminant_index': 'contaminantIndex',
    'compound_index': 'compoundIndex',
    'setting_index': 'settingIndex',
}

def normalize_top_level_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize top-level keys from snake_case to camelCase"""
    normalized = {}
    
    for key, value in data.items():
        # Normalize key if it's in the mapping
        new_key = KEY_MAPPINGS.get(key, key)
        normalized[new_key] = value
        
        if new_key != key:
            print(f'  Renamed: {key} → {new_key}')
    
    return normalized

def normalize_file(filepath: str):
    """Normalize top-level keys in a data file"""
    print(f'\n{"="*80}')
    print(f'Normalizing: {filepath}')
    print(f'{"="*80}')
    
    # Load data
    with open(filepath) as f:
        data = yaml.safe_load(f)
    
    # Normalize top-level keys
    normalized_data = normalize_top_level_keys(data)
    
    # Save normalized data
    with open(filepath, 'w') as f:
        yaml.dump(normalized_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f'✅ Saved normalized data')

def main():
    """Normalize all domain data files"""
    
    files = [
        'data/materials/Materials.yaml',
        'data/contaminants/Contaminants.yaml',
        'data/compounds/Compounds.yaml',
        'data/settings/Settings.yaml',
    ]
    
    for filepath in files:
        if Path(filepath).exists():
            normalize_file(filepath)
        else:
            print(f'⚠️  File not found: {filepath}')
    
    print(f'\n{"="*80}')
    print('✅ Top-level key normalization complete!')
    print(f'{"="*80}\n')

if __name__ == '__main__':
    main()
