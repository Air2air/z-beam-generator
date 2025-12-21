#!/usr/bin/env python3
"""
Fix broken relationship links in Contaminants and Settings

Removes references to non-existent materials.
"""

import yaml
from pathlib import Path
from datetime import datetime
import shutil

def load_valid_ids():
    """Load valid IDs from all domains."""
    with open('data/materials/Materials.yaml', 'r', encoding='utf-8') as f:
        materials = yaml.safe_load(f)
    
    with open('data/contaminants/Contaminants.yaml', 'r', encoding='utf-8') as f:
        contaminants = yaml.safe_load(f)
    
    return set(materials['materials'].keys()), set(contaminants['contamination_patterns'].keys())

def fix_contaminants(valid_material_ids):
    """Remove invalid material references from Contaminants."""
    contaminants_path = Path("data/contaminants/Contaminants.yaml")
    
    backup_path = contaminants_path.with_suffix(f'.yaml.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    shutil.copy2(contaminants_path, backup_path)
    print(f"✅ Backup: {backup_path.name}")
    
    with open(contaminants_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    removed = 0
    for pattern_data in data['contamination_patterns'].values():
        rel = pattern_data.get('relationships', {})
        found_on = rel.get('found_on_materials', [])
        
        valid_links = [link for link in found_on if link.get('id') in valid_material_ids]
        removed += len(found_on) - len(valid_links)
        rel['found_on_materials'] = valid_links
    
    with open(contaminants_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
    
    print(f"✅ Contaminants: Removed {removed} invalid material links")

def fix_settings(valid_material_ids, valid_contaminant_ids):
    """Remove invalid references from Settings."""
    settings_path = Path("data/settings/Settings.yaml")
    
    backup_path = settings_path.with_suffix(f'.yaml.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    shutil.copy2(settings_path, backup_path)
    print(f"✅ Backup: {backup_path.name}")
    
    with open(settings_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    removed_materials = 0
    removed_contaminants = 0
    
    for setting_data in data['settings'].values():
        rel = setting_data.get('relationships', {})
        
        # Fix optimized_for_materials
        materials = rel.get('optimized_for_materials', [])
        valid_materials = [link for link in materials if link.get('id') in valid_material_ids]
        removed_materials += len(materials) - len(valid_materials)
        rel['optimized_for_materials'] = valid_materials
        
        # Fix removes_contaminants
        contaminants = rel.get('removes_contaminants', [])
        valid_contaminants = [link for link in contaminants if link.get('id') in valid_contaminant_ids]
        removed_contaminants += len(contaminants) - len(valid_contaminants)
        rel['removes_contaminants'] = valid_contaminants
    
    with open(settings_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
    
    print(f"✅ Settings: Removed {removed_materials} invalid material links")
    print(f"✅ Settings: Removed {removed_contaminants} invalid contaminant links")

def main():
    print("🔧 Fixing broken relationship links...\n")
    
    valid_material_ids, valid_contaminant_ids = load_valid_ids()
    print(f"📦 Valid IDs: {len(valid_material_ids)} materials, {len(valid_contaminant_ids)} contaminants\n")
    
    fix_contaminants(valid_material_ids)
    fix_settings(valid_material_ids, valid_contaminant_ids)
    
    print("\n✅ All broken links removed")

if __name__ == "__main__":
    main()
