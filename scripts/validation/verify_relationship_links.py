#!/usr/bin/env python3
"""
Verify relationship link accuracy across all domains

Checks that all relationship IDs reference valid items in target domains.
"""

import yaml
from pathlib import Path

def load_all_data():
    """Load all domain data files."""
    with open('data/materials/Materials.yaml', 'r', encoding='utf-8') as f:
        materials = yaml.safe_load(f)
    
    with open('data/compounds/Compounds.yaml', 'r', encoding='utf-8') as f:
        compounds = yaml.safe_load(f)
    
    with open('data/contaminants/Contaminants.yaml', 'r', encoding='utf-8') as f:
        contaminants = yaml.safe_load(f)
    
    with open('data/settings/Settings.yaml', 'r', encoding='utf-8') as f:
        settings = yaml.safe_load(f)
    
    return materials, compounds, contaminants, settings

def check_materials_links(materials, contaminants):
    """Check Materials → Contaminants links."""
    print("\n🔍 Checking Materials domain...")
    
    valid_contaminant_ids = set(contaminants['contamination_patterns'].keys())
    errors = []
    total_links = 0
    
    for material_id, material_data in materials['materials'].items():
        rel = material_data.get('relationships', {})
        contaminatedBy = rel.get('contaminatedBy', [])
        
        for link in contaminated_by:
            total_links += 1
            target_id = link.get('id', '')
            if target_id not in valid_contaminant_ids:
                errors.append(f"  ❌ {material_id} → {target_id} (NOT FOUND)")
    
    if errors:
        print(f"❌ Found {len(errors)} broken links:")
        for error in errors[:10]:
            print(error)
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
    else:
        print(f"✅ All {total_links} links valid")
    
    return len(errors) == 0

def check_compounds_links(compounds, contaminants, materials):
    """Check Compounds → Contaminants/Materials links."""
    print("\n🔍 Checking Compounds domain...")
    
    valid_contaminant_ids = set(contaminants['contamination_patterns'].keys())
    valid_material_ids = set(materials['materials'].keys())
    errors = []
    total_links = 0
    
    for compound_id, compound_data in compounds['compounds'].items():
        rel = compound_data.get('relationships', {})
        
        # Check produced_from_contaminants
        for link in rel.get('produced_from_contaminants', []):
            total_links += 1
            target_id = link.get('id', '')
            if target_id not in valid_contaminant_ids:
                errors.append(f"  ❌ {compound_id} → contaminant:{target_id} (NOT FOUND)")
        
        # Check produced_from_materials
        for link in rel.get('produced_from_materials', []):
            total_links += 1
            target_id = link.get('id', '')
            if target_id not in valid_material_ids:
                errors.append(f"  ❌ {compound_id} → material:{target_id} (NOT FOUND)")
    
    if errors:
        print(f"❌ Found {len(errors)} broken links:")
        for error in errors[:10]:
            print(error)
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
    else:
        print(f"✅ All {total_links} links valid")
    
    return len(errors) == 0

def check_contaminants_links(contaminants, compounds, materials):
    """Check Contaminants → Compounds/Materials links."""
    print("\n🔍 Checking Contaminants domain...")
    
    valid_compound_ids = set(compounds['compounds'].keys())
    valid_material_ids = set(materials['materials'].keys())
    errors = []
    total_links = 0
    
    for pattern_id, pattern_data in contaminants['contamination_patterns'].items():
        rel = pattern_data.get('relationships', {})
        
        # Check produces_compounds
        for link in rel.get('produces_compounds', []):
            total_links += 1
            target_id = link.get('id', '')
            # Remove -compound suffix for validation
            base_id = target_id.replace('-compound', '')
            if base_id not in valid_compound_ids:
                errors.append(f"  ❌ {pattern_id} → compound:{target_id} (base:{base_id} NOT FOUND)")
        
        # Check found_on_materials
        for link in rel.get('found_on_materials', []):
            total_links += 1
            target_id = link.get('id', '')
            if target_id not in valid_material_ids:
                errors.append(f"  ❌ {pattern_id} → material:{target_id} (NOT FOUND)")
    
    if errors:
        print(f"❌ Found {len(errors)} broken links:")
        for error in errors[:10]:
            print(error)
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
    else:
        print(f"✅ All {total_links} links valid")
    
    return len(errors) == 0

def check_settings_links(settings, materials, contaminants):
    """Check Settings → Materials/Contaminants links."""
    print("\n🔍 Checking Settings domain...")
    
    valid_material_ids = set(materials['materials'].keys())
    valid_contaminant_ids = set(contaminants['contamination_patterns'].keys())
    errors = []
    total_links = 0
    
    for setting_id, setting_data in settings['settings'].items():
        rel = setting_data.get('relationships', {})
        
        # Check optimized_for_materials
        for link in rel.get('optimized_for_materials', []):
            total_links += 1
            target_id = link.get('id', '')
            if target_id not in valid_material_ids:
                errors.append(f"  ❌ {setting_id} → material:{target_id} (NOT FOUND)")
        
        # Check removes_contaminants
        for link in rel.get('removes_contaminants', []):
            total_links += 1
            target_id = link.get('id', '')
            if target_id not in valid_contaminant_ids:
                errors.append(f"  ❌ {setting_id} → contaminant:{target_id} (NOT FOUND)")
    
    if errors:
        print(f"❌ Found {len(errors)} broken links:")
        for error in errors[:10]:
            print(error)
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
    else:
        print(f"✅ All {total_links} links valid")
    
    return len(errors) == 0

def main():
    print("=" * 80)
    print("📊 RELATIONSHIP LINK ACCURACY VALIDATION")
    print("=" * 80)
    
    materials, compounds, contaminants, settings = load_all_data()
    
    print(f"\n📦 Loaded:")
    print(f"   • {len(materials['materials'])} materials")
    print(f"   • {len(compounds['compounds'])} compounds")
    print(f"   • {len(contaminants['contamination_patterns'])} contaminants")
    print(f"   • {len(settings['settings'])} settings")
    
    results = []
    results.append(check_materials_links(materials, contaminants))
    results.append(check_compounds_links(compounds, contaminants, materials))
    results.append(check_contaminants_links(contaminants, compounds, materials))
    results.append(check_settings_links(settings, materials, contaminants))
    
    print("\n" + "=" * 80)
    if all(results):
        print("✅ ALL RELATIONSHIP LINKS VALID - No broken references found!")
    else:
        print("❌ VALIDATION FAILED - Broken links found in one or more domains")
    print("=" * 80)

if __name__ == "__main__":
    main()
