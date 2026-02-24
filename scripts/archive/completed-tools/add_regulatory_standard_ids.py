#!/usr/bin/env python3
"""
Add standard IDs to regulatory standards in Materials.yaml.

This script adds 'standard_id' fields to link material-specific regulatory
standards to the parent RegulatoryStandards.yaml framework.

Mapping:
- "FDA 21 CFR 1040.10" → std_fda_21cfr1040
- "ANSI Z136.1" → std_ansi_z136_1
- "IEC 60825" → std_iec_60825_1
- "OSHA 29 CFR 1926.95" → std_osha_1926_95
"""

import yaml
import sys
from pathlib import Path

# Standard ID mapping based on description patterns
STANDARD_ID_MAP = {
    "FDA 21 CFR 1040.10": "std_fda_21cfr1040",
    "ANSI Z136.1": "std_ansi_z136_1",
    "IEC 60825": "std_iec_60825_1",
    "OSHA 29 CFR 1926.95": "std_osha_1926_95",
    "OSHA 29 CFR 1910.1200": "std_osha_1910_1200",
    "EPA 40 CFR Part 261": "std_epa_40cfr261",
    "EPA Clean Air Act": "std_epa_clean_air",
    "ISO 45001": "std_iso_45001",
    "ISO 14001": "std_iso_14001",
    "AS9100": "std_as9100",
    "NADCAP": "std_nadcap",
    "AMS 2644": "std_ams_2644",
    "ISO 13485": "std_iso_13485",
    "IATF 16949": "std_iatf_16949",
}

def find_standard_id(description: str) -> str | None:
    """Find standard ID by matching description patterns."""
    for pattern, std_id in STANDARD_ID_MAP.items():
        if pattern in description:
            return std_id
    return None

def add_standard_ids_to_materials(materials_file: Path) -> None:
    """Add standard_id fields to all regulatory standards in materials."""
    
    print(f"Reading {materials_file}...")
    with open(materials_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if 'materials' not in data:
        print("ERROR: No 'materials' key found in file")
        return
    
    materials = data['materials']
    total_materials = len(materials)
    modified_count = 0
    standards_updated = 0
    
    print(f"\nProcessing {total_materials} materials...")
    
    for material_name, material_data in materials.items():
        if 'regulatory_standards' not in material_data:
            continue
            
        standards = material_data['regulatory_standards']
        if not isinstance(standards, list):
            continue
        
        material_modified = False
        for standard in standards:
            if 'description' not in standard:
                continue
            
            # Skip if already has standard_id
            if 'standard_id' in standard:
                continue
                
            description = standard['description']
            standard_id = find_standard_id(description)
            
            if standard_id:
                standard['standard_id'] = standard_id
                standards_updated += 1
                material_modified = True
        
        if material_modified:
            modified_count += 1
    
    print(f"\nResults:")
    print(f"  Materials modified: {modified_count}/{total_materials}")
    print(f"  Standards updated: {standards_updated}")
    
    if standards_updated > 0:
        # Create backup
        backup_file = materials_file.parent / f"{materials_file.stem}_before_standard_ids.yaml"
        print(f"\nCreating backup: {backup_file.name}")
        with open(backup_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        # Write updated file
        print(f"Writing updated file: {materials_file.name}")
        with open(materials_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print("\n✅ Standard IDs added successfully!")
        print("\nExample material regulatory standards now include standard_id:")
        print("  - standard_id: std_fda_21cfr1040")
        print("    description: FDA 21 CFR 1040.10 - Laser Product Performance Standards")
        print("    name: FDA")
        print("    image: /images/logo/logo-org-fda.png")
        print("    url: https://...")
    else:
        print("\n⚠️  No standards needed updating (all already have standard_id)")

if __name__ == "__main__":
    # Get Materials.yaml path
    repo_root = Path(__file__).parent.parent.parent
    materials_file = repo_root / "data" / "materials" / "Materials.yaml"
    
    if not materials_file.exists():
        print(f"ERROR: Materials.yaml not found at {materials_file}")
        sys.exit(1)
    
    add_standard_ids_to_materials(materials_file)
