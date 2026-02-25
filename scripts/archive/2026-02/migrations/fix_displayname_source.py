#!/usr/bin/env python3
"""
Fix displayName in Source YAML Files

PROBLEM: Source data in z-beam-generator has incorrect displayName values:
- Contaminants: displayName ends with "Laser Cleaning" instead of "Contaminants"
- Compounds: displayName includes chemical formula instead of "Compound"
- Settings: displayName includes "Laser Cleaning Settings" instead of just "Settings"

SOLUTION: Update displayName to match pageTitle pattern for consistency
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any

def load_yaml(file_path: Path) -> Dict[str, Any]:
    """Load YAML file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_yaml(file_path: Path, data: Dict[str, Any]) -> None:
    """Save YAML file"""
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

def fix_contaminants():
    """Fix displayName in Contaminants.yaml"""
    file_path = Path('/Users/todddunning/Desktop/Z-Beam/z-beam-generator/data/contaminants/Contaminants.yaml')
    
    print("📁 Processing Contaminants.yaml...")
    data = load_yaml(file_path)
    
    updated = 0
    for contaminant_id, contaminant_data in data.get('contaminants', {}).items():
        if 'displayName' in contaminant_data:
            old_display_name = contaminant_data['displayName']
            
            # Remove "Laser Cleaning" suffix if present
            if old_display_name.endswith(' Laser Cleaning'):
                # Replace with "Contaminants"
                new_display_name = old_display_name.replace(' Laser Cleaning', ' Contaminants')
                contaminant_data['displayName'] = new_display_name
                print(f"  🔧 {contaminant_id}")
                print(f"     OLD: {old_display_name}")
                print(f"     NEW: {new_display_name}")
                updated += 1
            elif not old_display_name.endswith(' Contaminants'):
                # Just add "Contaminants" suffix
                new_display_name = f"{old_display_name} Contaminants"
                contaminant_data['displayName'] = new_display_name
                print(f"  🔧 {contaminant_id}")
                print(f"     OLD: {old_display_name}")
                print(f"     NEW: {new_display_name}")
                updated += 1
    
    if updated > 0:
        save_yaml(file_path, data)
        print(f"✅ Updated {updated} contaminants")
    else:
        print("✅ All contaminants already correct")
    
    return updated

def fix_compounds():
    """Fix displayName in Compounds.yaml"""
    file_path = Path('/Users/todddunning/Desktop/Z-Beam/z-beam-generator/data/compounds/Compounds.yaml')
    
    print("\n📁 Processing Compounds.yaml...")
    data = load_yaml(file_path)
    
    updated = 0
    for compound_id, compound_data in data.get('compounds', {}).items():
        if 'displayName' in compound_data and 'name' in compound_data:
            old_display_name = compound_data['displayName']
            name = compound_data['name']
            
            # displayName should be: "{name} Compound"
            # But name often includes chemical formula like "Ammonia (NH₃)"
            # Extract just the base name without formula
            base_name = name.split('(')[0].strip() if '(' in name else name
            
            expected_display_name = f"{base_name} Compound"
            
            if old_display_name != expected_display_name:
                compound_data['displayName'] = expected_display_name
                print(f"  🔧 {compound_id}")
                print(f"     OLD: {old_display_name}")
                print(f"     NEW: {expected_display_name}")
                updated += 1
    
    if updated > 0:
        save_yaml(file_path, data)
        print(f"✅ Updated {updated} compounds")
    else:
        print("✅ All compounds already correct")
    
    return updated

def fix_settings():
    """Fix displayName in Settings.yaml"""
    file_path = Path('/Users/todddunning/Desktop/Z-Beam/z-beam-generator/data/settings/Settings.yaml')
    
    print("\n📁 Processing Settings.yaml...")
    data = load_yaml(file_path)
    
    updated = 0
    for setting_id, setting_data in data.get('settings', {}).items():
        if 'displayName' in setting_data and 'name' in setting_data:
            old_display_name = setting_data['displayName']
            name = setting_data['name']
            
            # displayName should be: "{name} Settings"
            expected_display_name = f"{name} Settings"
            
            if old_display_name != expected_display_name:
                setting_data['displayName'] = expected_display_name
                print(f"  🔧 {setting_id}")
                print(f"     OLD: {old_display_name}")
                print(f"     NEW: {expected_display_name}")
                updated += 1
    
    if updated > 0:
        save_yaml(file_path, data)
        print(f"✅ Updated {updated} settings")
    else:
        print("✅ All settings already correct")
    
    return updated

def main():
    """Main execution"""
    print("=" * 80)
    print("Fix displayName in Source YAML Files")
    print("=" * 80)
    
    total_updated = 0
    total_updated += fix_contaminants()
    total_updated += fix_compounds()
    total_updated += fix_settings()
    
    print("\n" + "=" * 80)
    print(f"✅ Total updated: {total_updated} entries")
    print("=" * 80)
    
    if total_updated > 0:
        print("\n✨ Source data updated! Now generators will produce correct displayName values.")
    else:
        print("\n✅ All source data already correct!")

if __name__ == '__main__':
    main()
