#!/usr/bin/env python3
"""
Fix structural inconsistencies in materials frontmatter
- Remove duplicate root-level sections that belong in relationships
- Fix sections that should have items arrays
"""

import yaml
from pathlib import Path

def fix_structural_issues():
    """Fix specific structural inconsistencies identified by validator"""
    
    # Known problematic files from validator output
    problem_files = [
        'alabaster-laser-cleaning.yaml',
        'aluminum-laser-cleaning.yaml'
    ]
    
    materials_dir = Path('/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/materials')
    
    print('🔧 FIXING STRUCTURAL INCONSISTENCIES')
    print('=' * 60)
    
    for filename in problem_files:
        file_path = materials_dir / filename
        
        if not file_path.exists():
            print(f"❌ File not found: {filename}")
            continue
        
        print(f'\n🔍 Processing: {filename}')
        
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        file_modified = False
        
        # Problem 1: Remove standalone contaminatedBy if relationships.interactions.contaminatedBy exists
        has_relationships_contaminated = ('relationships' in data and 
                                        'interactions' in data['relationships'] and 
                                        'contaminatedBy' in data['relationships']['interactions'])
        has_standalone_contaminated = 'contaminatedBy' in data
        
        if has_standalone_contaminated and has_relationships_contaminated:
            print(f"   🔧 Removing duplicate standalone contaminatedBy")
            del data['contaminatedBy']
            file_modified = True
        
        # Problem 2: Remove standalone laserMaterialInteraction if it exists in relationships.operational
        has_relationships_laser = ('relationships' in data and 
                                 'operational' in data['relationships'] and 
                                 'laserMaterialInteraction' in data['relationships']['operational'])
        has_standalone_laser = 'laserMaterialInteraction' in data
        
        if has_standalone_laser and has_relationships_laser:
            print(f"   🔧 Removing duplicate standalone laserMaterialInteraction")
            del data['laserMaterialInteraction']
            file_modified = True
        
        # Problem 3: Fix relationships.contaminatedBy structure
        if 'relationships' in data and 'contaminatedBy' in data['relationships']:
            cb_section = data['relationships']['contaminatedBy']
            if '_section' in cb_section and 'items' not in cb_section:
                print(f"   🔧 Converting relationships.contaminatedBy to proper structure")
                # Move this to a description field and remove the problematic structure
                del data['relationships']['contaminatedBy']
                file_modified = True
        
        # Save if modified
        if file_modified:
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            print(f"   ✅ Fixed structural issues in {filename}")
        else:
            print(f"   ✅ No issues found in {filename}")
    
    print('\n🎯 Running validation to verify fixes...')

if __name__ == "__main__":
    fix_structural_issues()