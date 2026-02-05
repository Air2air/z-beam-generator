#!/usr/bin/env python3
"""
Fix duplicate contaminatedBy sections in materials frontmatter
Part of consolidation work for better normalization
"""

import yaml
from pathlib import Path

def fix_duplicate_sections():
    """Fix duplicate contaminatedBy sections that cause structural inconsistencies"""
    
    # Target file with known issue
    file_path = Path('/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/materials/alabaster-laser-cleaning.yaml')
    
    print('🔧 FIXING STRUCTURAL INCONSISTENCY')
    print('=' * 50)
    
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Check for duplicate contaminatedBy sections
    has_relationships = ('relationships' in data and 
                        'interactions' in data['relationships'] and 
                        'contaminatedBy' in data['relationships']['interactions'])
    has_standalone = 'contaminatedBy' in data
    
    print(f'Has relationships.interactions.contaminatedBy: {has_relationships}')
    print(f'Has standalone contaminatedBy: {has_standalone}')
    
    if has_standalone and has_relationships:
        print('\n⚠️  Found duplicate contaminatedBy section')
        print('Removing standalone version to fix structural consistency')
        
        # Remove the standalone version
        del data['contaminatedBy']
        
        # Save the fixed file
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        print('✅ Fixed: Removed duplicate contaminatedBy section')
        print('Structure now follows unified schema pattern')
        return True
    else:
        print('No duplicate sections found')
        return False

if __name__ == "__main__":
    fixed = fix_duplicate_sections()
    if fixed:
        print('\n✨ Consolidation improvement applied!')
        print('File structure normalized to unified schema')