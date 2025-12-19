#!/usr/bin/env python3
"""
Extract properties and machine_settings from Materials.yaml

This script:
1. Reads Materials.yaml
2. Extracts all properties into MaterialProperties.yaml
3. Extracts all machine_settings into MachineSettings.yaml
4. Creates updated Materials.yaml without those fields
5. Preserves all associations via material names
6. Creates backup of original file

Data Structure:
- MaterialProperties.yaml: { material_name: { ...properties } }
- MachineSettings.yaml: { material_name: { ...settings } }
- Materials.yaml: All other fields except properties and machine_settings
"""

from pathlib import Path
from datetime import datetime
import shutil
from typing import Dict, Any

# Use shared YAML utilities
from shared.utils.file_io import read_yaml_file, write_yaml_file

# Paths
MATERIALS_FILE = Path("data/materials/Materials.yaml")
PROPERTIES_FILE = Path("data/materials/MaterialProperties.yaml")
SETTINGS_FILE = Path("data/materials/MachineSettings.yaml")
BACKUP_DIR = Path("data/materials/backups")


def create_backup(file_path: Path) -> Path:
    """Create timestamped backup of file"""
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"{file_path.stem}_{timestamp}.yaml"
    shutil.copy2(file_path, backup_path)
    print(f"📦 Created backup: {backup_path}")
    return backup_path


def extract_data() -> None:
    """Main extraction function"""
    
    print("🔄 EXTRACTING MATERIAL PROPERTIES AND MACHINE SETTINGS")
    print("=" * 80)
    
    # Load Materials.yaml
    print(f"\n📖 Loading {MATERIALS_FILE}...")
    materials_data = read_yaml_file(MATERIALS_FILE)
    
    if 'materials' not in materials_data:
        raise ValueError("No 'materials' key found in Materials.yaml")
    
    materials = materials_data['materials']
    print(f"   Found {len(materials)} materials")
    
    # Extract properties and machine_settings
    print("\n🔍 Extracting data...")
    material_properties = {}
    machine_settings = {}
    materials_without_extracted = {}
    
    extracted_props_count = 0
    extracted_settings_count = 0
    
    for material_name, material_data in materials.items():
        # Extract properties
        if 'properties' in material_data:
            material_properties[material_name] = material_data.pop('properties')
            extracted_props_count += 1
        
        # Extract machine_settings
        if 'machine_settings' in material_data:
            machine_settings[material_name] = material_data.pop('machine_settings')
            extracted_settings_count += 1
        
        # Store cleaned material data
        materials_without_extracted[material_name] = material_data
    
    print(f"   ✅ Extracted properties from {extracted_props_count} materials")
    print(f"   ✅ Extracted machine_settings from {extracted_settings_count} materials")
    
    # Create backup of original Materials.yaml
    print(f"\n💾 Creating backup...")
    create_backup(MATERIALS_FILE)
    
    # Save MaterialProperties.yaml
    print(f"\n📝 Saving {PROPERTIES_FILE}...")
    properties_output = {
        '_metadata': {
            'description': 'Material properties extracted from Materials.yaml',
            'extracted_date': datetime.now().isoformat(),
            'total_materials': len(material_properties),
            'structure': 'Each material name maps to its properties data'
        },
        'properties': material_properties
    }
    save_yaml(properties_output, PROPERTIES_FILE)
    print(f"   ✅ Saved {len(material_properties)} material property sets")
    
    # Save MachineSettings.yaml
    print(f"\n📝 Saving {SETTINGS_FILE}...")
    settings_output = {
        '_metadata': {
            'description': 'Machine settings extracted from Materials.yaml',
            'extracted_date': datetime.now().isoformat(),
            'total_materials': len(machine_settings),
            'structure': 'Each material name maps to its machine_settings data'
        },
        'settings': machine_settings
    }
    save_yaml(settings_output, SETTINGS_FILE)
    print(f"   ✅ Saved {len(machine_settings)} machine setting sets")
    
    # Update Materials.yaml with cleaned data
    print(f"\n📝 Updating {MATERIALS_FILE}...")
    materials_data['materials'] = materials_without_extracted
    
    # Add extraction metadata
    if 'category_metadata' not in materials_data:
        materials_data['category_metadata'] = {}
    
    materials_data['_extraction_metadata'] = {
        'extracted_date': datetime.now().isoformat(),
        'extracted_fields': ['properties', 'machine_settings'],
        'new_files': ['MaterialProperties.yaml', 'MachineSettings.yaml'],
        'note': 'Use materials.data.loader module to load complete material data'
    }
    
    save_yaml(materials_data, MATERIALS_FILE)
    print(f"   ✅ Updated Materials.yaml (removed extracted fields)")
    
    # Summary
    print("\n" + "=" * 80)
    print("✨ EXTRACTION COMPLETE")
    print(f"\n📊 Summary:")
    print(f"   • {PROPERTIES_FILE}: {len(material_properties)} materials")
    print(f"   • {SETTINGS_FILE}: {len(machine_settings)} materials")
    print(f"   • {MATERIALS_FILE}: Updated (extraction metadata added)")
    print(f"\n📂 File sizes:")
    print(f"   • {PROPERTIES_FILE}: {PROPERTIES_FILE.stat().st_size:,} bytes")
    print(f"   • {SETTINGS_FILE}: {SETTINGS_FILE.stat().st_size:,} bytes")
    print(f"   • {MATERIALS_FILE}: {MATERIALS_FILE.stat().st_size:,} bytes")
    print(f"\n💡 Next step: Create materials/data/loader.py to merge data on load")


if __name__ == '__main__':
    try:
        extract_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
