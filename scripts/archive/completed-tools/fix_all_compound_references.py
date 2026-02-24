#!/usr/bin/env python3
"""
Fix Compound ID References in All Data Files

Updates old compound IDs (with -compound suffix) to new IDs (without suffix)
in Materials.yaml, contaminants.yaml, Settings.yaml, and Compounds.yaml
"""

import yaml
from pathlib import Path
import sys
from typing import Dict, List, Any

# Mapping of old to new compound IDs
OLD_TO_NEW = {
    'carbon-dioxide-compound': 'carbon-dioxide',
    'water-vapor-compound': 'water-vapor',
    'carbon-particulates-compound': 'carbon-particulates',
    'vocs-compound': 'vocs',
    'carbon-ash-compound': 'carbon-ash',
    'nitrogen-oxides-compound': 'nitrogen-oxides',
    'aluminum-oxide-compound': 'aluminum-oxide',
    'carbon-monoxide-compound': 'carbon-monoxide',
    'metal-oxides-mixed-compound': 'metal-oxides-mixed',
    'organic-residues-compound': 'organic-residues',
    'pahs-compound': 'pahs',
    'formaldehyde-compound': 'formaldehyde',
    'benzene-compound': 'benzene',
    'toluene-compound': 'toluene',
    'acetaldehyde-compound': 'acetaldehyde',
    'styrene-compound': 'styrene',
    'acrolein-compound': 'acrolein',
    'iron-oxide-compound': 'iron-oxide',
    'chromium-vi-compound': 'chromium-vi',
    'lead-oxide-compound': 'lead-oxide',
    'cadmium-oxide-compound': 'cadmium-oxide',
    'zinc-oxide-compound': 'zinc-oxide',
    'copper-oxide-compound': 'copper-oxide',
    'tin-oxide-compound': 'tin-oxide',
    'metal-vapors-mixed-compound': 'metal-vapors-mixed',
    'nanoparticulates-compound': 'nanoparticulates',
    'silicon-dioxide-compound': 'silicon-dioxide',
    'calcium-oxide-compound': 'calcium-oxide',
    'sulfur-dioxide-compound': 'sulfur-dioxide',
    'hydrogen-chloride-compound': 'hydrogen-chloride',
    'hydrogen-cyanide-compound': 'hydrogen-cyanide',
    'phosgene-compound': 'phosgene',
    'ammonia-compound': 'ammonia',
    'benzoapyrene-compound': 'benzoapyrene',
}

def fix_compound_references_in_list(items: List) -> int:
    """Fix compound IDs in a list of items"""
    count = 0
    if not items:
        return 0
    
    for item in items:
        if isinstance(item, dict) and 'id' in item:
            old_id = item['id']
            if old_id in OLD_TO_NEW:
                new_id = OLD_TO_NEW[old_id]
                item['id'] = new_id
                count += 1
                print(f"      {old_id} → {new_id}")
    
    return count

def fix_contaminants_file(path: Path) -> int:
    """Fix compound references in contaminants.yaml"""
    print(f"\n📋 Processing {path.name}...")
    
    with open(path) as f:
        data = yaml.safe_load(f)
    
    patterns = data['contamination_patterns']
    total_updates = 0
    updated_patterns = []
    
    for pattern_id, pattern_data in patterns.items():
        if 'relationships' in pattern_data:
            relationships = pattern_data['relationships']
            if 'produces_compounds' in relationships:
                compounds = relationships['produces_compounds']
                if compounds:
                    count = fix_compound_references_in_list(compounds)
                    if count > 0:
                        total_updates += count
                        updated_patterns.append(pattern_id)
                        print(f"   ✓ {pattern_id}: Fixed {count} references")
    
    if total_updates > 0:
        print(f"\n   💾 Saving changes...")
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        print(f"   ✅ Fixed {total_updates} references across {len(updated_patterns)} patterns")
    else:
        print(f"   ✅ No updates needed")
    
    return total_updates

def fix_materials_file(path: Path) -> int:
    """Fix compound references in Materials.yaml"""
    print(f"\n📋 Processing {path.name}...")
    
    with open(path) as f:
        data = yaml.safe_load(f)
    
    materials = data['materials']
    total_updates = 0
    updated_materials = []
    
    for material_id, material_data in materials.items():
        if 'relationships' in material_data:
            relationships = material_data['relationships']
            if 'related_compounds' in relationships:
                compounds = relationships['related_compounds']
                if compounds:
                    count = fix_compound_references_in_list(compounds)
                    if count > 0:
                        total_updates += count
                        updated_materials.append(material_id)
                        print(f"   ✓ {material_id}: Fixed {count} references")
    
    if total_updates > 0:
        print(f"\n   💾 Saving changes...")
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        print(f"   ✅ Fixed {total_updates} references across {len(updated_materials)} materials")
    else:
        print(f"   ✅ No updates needed")
    
    return total_updates

def fix_compounds_file(path: Path) -> int:
    """Fix any self-references in Compounds.yaml (shouldn't have old IDs)"""
    print(f"\n📋 Processing {path.name}...")
    
    with open(path) as f:
        data = yaml.safe_load(f)
    
    compounds = data['compounds']
    total_updates = 0
    
    for compound_id in list(compounds.keys()):
        if compound_id in OLD_TO_NEW:
            print(f"   ⚠️  Found old ID as key: {compound_id}")
            # This would require renaming the key itself - more complex
            total_updates += 1
    
    if total_updates > 0:
        print(f"   ⚠️  Found {total_updates} compounds using old IDs as keys")
        print(f"   ℹ️  These would need manual key renaming (more complex)")
    else:
        print(f"   ✅ No key updates needed")
    
    return 0  # Don't count key renames for now

def fix_settings_file(path: Path) -> int:
    """Fix compound references in Settings.yaml"""
    print(f"\n📋 Processing {path.name}...")
    
    with open(path) as f:
        data = yaml.safe_load(f)
    
    settings = data['settings']
    total_updates = 0
    updated_settings = []
    
    for setting_id, setting_data in settings.items():
        if 'relationships' in setting_data:
            relationships = setting_data['relationships']
            # Check for any compound references (if they exist)
            for rel_type in ['related_compounds', 'produces_compounds']:
                if rel_type in relationships:
                    compounds = relationships[rel_type]
                    if compounds:
                        count = fix_compound_references_in_list(compounds)
                        if count > 0:
                            total_updates += count
                            updated_settings.append(setting_id)
                            print(f"   ✓ {setting_id}: Fixed {count} references")
    
    if total_updates > 0:
        print(f"\n   💾 Saving changes...")
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        print(f"   ✅ Fixed {total_updates} references across {len(updated_settings)} settings")
    else:
        print(f"   ✅ No updates needed")
    
    return total_updates

def main():
    project_root = Path.cwd()
    
    print("=" * 80)
    print("FIX COMPOUND ID REFERENCES")
    print("=" * 80)
    print(f"\n📂 Project root: {project_root}")
    print(f"\n🔄 Updating {len(OLD_TO_NEW)} compound ID mappings...")
    
    total_fixed = 0
    
    # Fix each data file
    files_to_fix = [
        (project_root / 'data' / 'contaminants' / 'contaminants.yaml', fix_contaminants_file),
        (project_root / 'data' / 'materials' / 'Materials.yaml', fix_materials_file),
        (project_root / 'data' / 'settings' / 'Settings.yaml', fix_settings_file),
        (project_root / 'data' / 'compounds' / 'Compounds.yaml', fix_compounds_file),
    ]
    
    for file_path, fix_function in files_to_fix:
        if file_path.exists():
            count = fix_function(file_path)
            total_fixed += count
        else:
            print(f"\n⚠️  File not found: {file_path}")
    
    print("\n" + "=" * 80)
    if total_fixed > 0:
        print(f"✅ COMPLETE: Fixed {total_fixed} compound references across all data files")
        print("\n📝 Next steps:")
        print("   1. Run validation: python3 run.py --export-all --dry-run")
        print("   2. If validation passes, export: python3 run.py --export-all")
    else:
        print("✅ All compound references already correct!")
    print("=" * 80)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
