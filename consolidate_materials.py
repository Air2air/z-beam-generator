#!/usr/bin/env python3
"""
Comprehensive consolidation fix for materials frontmatter
Fixes structural inconsistencies identified by validator
"""

import yaml
from pathlib import Path
import sys

def fix_materials_structure():
    """Fix structural inconsistencies in materials frontmatter"""
    
    materials_dir = Path('/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/materials')
    
    if not materials_dir.exists():
        print(f"Materials directory not found: {materials_dir}")
        return
    
    print('🎯 COMPREHENSIVE MATERIALS CONSOLIDATION')
    print('=' * 60)
    
    files_fixed = 0
    issues_fixed = 0
    
    # Process each material file
    for yaml_file in materials_dir.glob('*.yaml'):
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
            
            file_modified = False
            
            # Check for duplicate contaminatedBy sections
            has_relationships_contaminated = ('relationships' in data and 
                                            'interactions' in data['relationships'] and 
                                            'contaminatedBy' in data['relationships']['interactions'])
            has_standalone_contaminated = 'contaminatedBy' in data
            
            if has_standalone_contaminated and has_relationships_contaminated:
                print(f"\n🔧 {yaml_file.name}")
                print(f"   Found duplicate contaminatedBy section")
                del data['contaminatedBy']
                file_modified = True
                issues_fixed += 1
                print(f"   ✅ Removed duplicate standalone contaminatedBy")
            
            # Check for missing _section metadata in relationships
            if 'relationships' in data:
                for category, sections in data['relationships'].items():
                    for section_name, section_data in sections.items():
                        if isinstance(section_data, dict) and 'items' in section_data:
                            if '_section' not in section_data:
                                print(f"\n🔧 {yaml_file.name}")
                                print(f"   Missing _section in {category}.{section_name}")
                                # Add minimal _section metadata
                                section_data['_section'] = {
                                    'sectionTitle': section_name.replace('_', ' ').title(),
                                    'order': 1,
                                    'variant': 'default'
                                }
                                file_modified = True
                                issues_fixed += 1
                                print(f"   ✅ Added _section metadata")
            
            # Save if modified
            if file_modified:
                with open(yaml_file, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                files_fixed += 1
                
        except Exception as e:
            print(f"❌ Error processing {yaml_file.name}: {e}")
    
    print(f'\n📊 CONSOLIDATION SUMMARY')
    print(f'Files processed: {len(list(materials_dir.glob("*.yaml")))}')
    print(f'Files fixed: {files_fixed}')
    print(f'Issues resolved: {issues_fixed}')
    
    if issues_fixed > 0:
        print('\n✨ Consolidation improvements applied!')
        print('Materials frontmatter now follows unified schema structure')
    else:
        print('\n✅ No structural issues found - already normalized!')

if __name__ == "__main__":
    fix_materials_structure()