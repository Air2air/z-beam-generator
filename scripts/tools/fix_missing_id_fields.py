#!/usr/bin/env python3
"""
Fix Missing and Incorrect ID Fields

PROBLEM:
- 88 contaminants missing 'id' field
- 10 contaminants have wrong id format (full slug instead of base)
- 153 materials missing 'id' field
- 153 settings missing 'id' field

SOLUTION:
Add 'id' field matching the full key name for all entities:
- Contaminants: 'pattern-name-contamination' → id: 'pattern-name-contamination'
- Materials: 'material-laser-cleaning' → id: 'material-laser-cleaning'
- Settings: 'material-settings' → id: 'material-settings'

Created: December 23, 2025
"""

import yaml
import sys
from pathlib import Path

def fix_contaminants():
    """Fix missing id fields in Contaminants.yaml"""
    filepath = Path('data/contaminants/Contaminants.yaml')
    
    with open(filepath) as f:
        data = yaml.safe_load(f)
    
    fixed_count = 0
    
    for pattern_id, pattern_data in data['contamination_patterns'].items():
        # ID should match the full key (with -contamination suffix)
        expected_id = pattern_id
        actual_id = pattern_data.get('id')
        
        if actual_id is None:
            # Missing id - add it with full suffix
            pattern_data['id'] = expected_id
            fixed_count += 1
            if fixed_count <= 5:
                print(f"  Added id to {pattern_id}: '{expected_id}'")
    
    if fixed_count > 0:
        with open(filepath, 'w') as f:
            yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"\n✅ Contaminants.yaml: {fixed_count} ids added")
        if fixed_count > 5:
            print(f"   (showing first 5, total: {fixed_count})")
    else:
        print("\n✅ Contaminants.yaml: All ids present")
    
    return fixed_count

def fix_materials():
    """Fix missing id fields in Materials.yaml"""
    filepath = Path('data/materials/Materials.yaml')
    
    with open(filepath) as f:
        data = yaml.safe_load(f)
    
    fixed_count = 0
    
    for material_id, material_data in data['materials'].items():
        # ID should match the full key (with -laser-cleaning suffix)
        expected_id = material_id
        
        if 'id' not in material_data:
            material_data['id'] = expected_id
            fixed_count += 1
            if fixed_count <= 5:
                print(f"  Added id to {material_id}: '{expected_id}'")
    
    if fixed_count > 0:
        with open(filepath, 'w') as f:
            yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"\n✅ Materials.yaml: {fixed_count} ids added")
        if fixed_count > 5:
            print(f"   (showing first 5, total: {fixed_count})")
    else:
        print("\n✅ Materials.yaml: All ids present")
    
    return fixed_count

def fix_settings():
    """Fix missing id fields in Settings.yaml"""
    filepath = Path('data/settings/Settings.yaml')
    
    with open(filepath) as f:
        data = yaml.safe_load(f)
    
    fixed_count = 0
    
    for setting_id, setting_data in data['settings'].items():
        # ID should match the full key (with -settings suffix)
        expected_id = setting_id
        
        if 'id' not in setting_data:
            setting_data['id'] = expected_id
            fixed_count += 1
            if fixed_count <= 5:
                print(f"  Added id to {setting_id}: '{expected_id}'")
    
    if fixed_count > 0:
        with open(filepath, 'w') as f:
            yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"\n✅ Settings.yaml: {fixed_count} ids added")
        if fixed_count > 5:
            print(f"   (showing first 5, total: {fixed_count})")
    else:
        print("\n✅ Settings.yaml: All ids present")
    
    return fixed_count

def main():
    print("🔧 FIXING MISSING ID FIELDS")
    print("="*60)
    
    total = 0
    
    print("\n1️⃣  Contaminants.yaml")
    print("-" * 60)
    total += fix_contaminants()
    
    print("\n\n2️⃣  Materials.yaml")
    print("-" * 60)
    total += fix_materials()
    
    print("\n\n3️⃣  Settings.yaml")
    print("-" * 60)
    total += fix_settings()
    
    print("\n" + "="*60)
    print(f"📊 TOTAL FIXES: {total}")
    print("="*60)
    
    if total > 0:
        print("\n✅ All id fields fixed!")
        print("   Next: Re-export all domains to propagate changes")
        return 0
    else:
        print("\n✅ No fixes needed - all ids present and correct")
        return 0

if __name__ == '__main__':
    sys.exit(main())
