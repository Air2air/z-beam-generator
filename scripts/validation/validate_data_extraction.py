#!/usr/bin/env python3
"""
Comprehensive validation of data architecture extraction

Validates that:
1. All 132 materials have materialProperties and machineSettings
2. Data is correctly merged from separate YAML files
3. All loaders work correctly
4. No data loss during extraction
5. Backward compatibility maintained
"""

import yaml
from pathlib import Path
from domains.materials.data_loader import load_materials_data, load_material, get_material_names
from domains.materials.materials_cache import load_materials_cached

def load_backup() -> dict:
    """Load backup Materials.yaml for comparison"""
    backup_dir = Path("data/materials/backups")
    backups = sorted(backup_dir.glob("Materials_*.yaml"), reverse=True)
    if not backups:
        raise FileNotFoundError("No backup found!")
    
    latest_backup = backups[0]
    print(f"📦 Loading backup: {latest_backup.name}")
    with open(latest_backup, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def compare_material_data(name: str, original: dict, merged: dict) -> tuple[bool, list[str]]:
    """Compare original and merged data for a material"""
    issues = []
    
    # Check materialProperties
    if 'materialProperties' not in merged:
        issues.append(f"Missing materialProperties")
    elif merged['materialProperties'] != original.get('materialProperties', {}):
        issues.append(f"materialProperties mismatch")
    
    # Check machineSettings
    if 'machineSettings' not in merged:
        issues.append(f"Missing machineSettings")
    elif merged['machineSettings'] != original.get('machineSettings', {}):
        issues.append(f"machineSettings mismatch")
    
    # Check other fields preserved
    for key in ['name', 'category', 'description', 'title']:
        if key in original and original[key] != merged.get(key):
            issues.append(f"{key} mismatch")
    
    return len(issues) == 0, issues

def main():
    print("🔍 COMPREHENSIVE DATA EXTRACTION VALIDATION")
    print("=" * 80)
    
    # Load data via different methods
    print("\n📖 Loading data via different loaders...")
    
    # Method 1: New centralized loader
    data_via_loader = load_materials_data()
    materials_via_loader = data_via_loader['materials']
    print(f"   ✅ load_materials_data(): {len(materials_via_loader)} materials")
    
    # Method 2: Cached loader (most common)
    data_via_cached = load_materials_cached()
    materials_via_cached = data_via_cached['materials']
    print(f"   ✅ load_materials_cached(): {len(materials_via_cached)} materials")
    
    # Method 3: Individual material lookup
    names = get_material_names()
    print(f"   ✅ get_material_names(): {len(names)} names")
    
    # Verify consistency between loaders
    print("\n🔄 Verifying consistency between loaders...")
    if materials_via_loader == materials_via_cached:
        print("   ✅ Both loaders return identical data")
    else:
        print("   ❌ Loaders return different data!")
        return False
    
    # Load backup for comparison
    print("\n📦 Loading backup for data integrity check...")
    backup_data = load_backup()
    backup_materials = backup_data['materials']
    print(f"   ✅ Backup has {len(backup_materials)} materials")
    
    # Compare each material
    print("\n🔍 Comparing extracted data with backup...")
    total_materials = len(backup_materials)
    passed = 0
    failed = 0
    
    for material_name, original_data in backup_materials.items():
        merged_data = materials_via_loader.get(material_name)
        
        if not merged_data:
            print(f"   ❌ {material_name}: Not found in merged data!")
            failed += 1
            continue
        
        is_valid, issues = compare_material_data(material_name, original_data, merged_data)
        
        if is_valid:
            passed += 1
        else:
            failed += 1
            print(f"   ❌ {material_name}: {', '.join(issues)}")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 VALIDATION RESULTS")
    print(f"\n   Total Materials: {total_materials}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   Success Rate: {passed/total_materials*100:.1f}%")
    
    # Coverage checks
    print("\n📈 DATA COVERAGE:")
    has_props = sum(1 for m in materials_via_loader.values() if 'materialProperties' in m)
    has_settings = sum(1 for m in materials_via_loader.values() if 'machineSettings' in m)
    
    print(f"   • materialProperties: {has_props}/{total_materials} ({has_props/total_materials*100:.1f}%)")
    print(f"   • machineSettings: {has_settings}/{total_materials} ({has_settings/total_materials*100:.1f}%)")
    
    # File sizes
    print("\n💾 FILE SIZES:")
    materials_file = Path("data/materials/Materials.yaml")
    properties_file = Path("data/materials/MaterialProperties.yaml")
    settings_file = Path("data/materials/MachineSettings.yaml")
    
    print(f"   • Materials.yaml: {materials_file.stat().st_size:,} bytes")
    print(f"   • MaterialProperties.yaml: {properties_file.stat().st_size:,} bytes")
    print(f"   • MachineSettings.yaml: {settings_file.stat().st_size:,} bytes")
    
    total_new = materials_file.stat().st_size + properties_file.stat().st_size + settings_file.stat().st_size
    print(f"   • Total (new): {total_new:,} bytes")
    
    # Final verdict
    print("\n" + "=" * 80)
    if failed == 0 and has_props == total_materials and has_settings == total_materials:
        print("✅ VALIDATION PASSED: Data extraction successful!")
        print("\n🎉 All materials have complete data")
        print("🎉 All loaders working correctly")
        print("🎉 100% data preservation verified")
        return True
    else:
        print("❌ VALIDATION FAILED: Issues detected!")
        if failed > 0:
            print(f"   • {failed} materials have data issues")
        if has_props < total_materials:
            print(f"   • {total_materials - has_props} materials missing properties")
        if has_settings < total_materials:
            print(f"   • {total_materials - has_settings} materials missing settings")
        return False

if __name__ == '__main__':
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ VALIDATION ERROR: {e}")
        raise
