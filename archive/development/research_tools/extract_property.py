#!/usr/bin/env python3
"""
Property Extraction Tool
========================
Extracts a single property from all materials into a focused research file.

This enables:
- Focused AI verification of one property at a time
- Easy comparison across all materials
- Systematic correction of inaccurate values
- Complete audit trail

Usage:
    python3 scripts/research_tools/extract_property.py --property density
    python3 scripts/research_tools/extract_property.py --property meltingPoint --output custom.yaml
    python3 scripts/research_tools/extract_property.py --setting powerRange
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from data.materials import load_materials


def extract_material_property(property_name: str, output_file: Path):
    """Extract a material property from all materials"""
    
    print(f"\n🔍 Extracting property: {property_name}")
    print("=" * 70)
    
    # Load materials
    materials_data = load_materials()
    materials = materials_data.get('materials', {})
    
    print(f"📂 Loaded {len(materials)} materials")
    
    # Extract property from each material
    extracted = {}
    found_count = 0
    missing_count = 0
    
    for material_name, material_data in materials.items():
        if not isinstance(material_data, dict):
            continue
        
        properties = material_data.get('properties', {})
        
        if property_name in properties:
            prop_data = properties[property_name]
            if isinstance(prop_data, dict):
                extracted[material_name] = {
                    'current_value': prop_data.get('value'),
                    'unit': prop_data.get('unit', ''),
                    'confidence': prop_data.get('confidence'),
                    'source': prop_data.get('source', ''),
                    'description': prop_data.get('description', ''),
                    'min': prop_data.get('min'),
                    'max': prop_data.get('max'),
                    'category': material_data.get('category', 'unknown'),
                    'ai_verified_value': None,  # To be filled by AI
                    'variance': None,           # To be calculated
                    'status': 'PENDING',        # PENDING, VERIFIED, NEEDS_REVIEW, ERROR
                }
                found_count += 1
            else:
                missing_count += 1
        else:
            missing_count += 1
    
    print(f"✅ Found {found_count} materials with property '{property_name}'")
    print(f"⚠️  Missing from {missing_count} materials")
    
    # Create research file
    research_data = {
        'property': {
            'name': property_name,
            'extraction_date': datetime.now().isoformat(),
            'total_materials': len(materials),
            'extracted_count': found_count,
            'missing_count': missing_count
        },
        'materials': extracted,
        'research_status': {
            'extraction_complete': True,
            'ai_verification_complete': False,
            'ready_for_merge': False
        }
    }
    
    # Write to file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        yaml.dump(research_data, f, default_flow_style=False, sort_keys=False, indent=2)
    
    print(f"\n✅ Extraction complete!")
    print(f"📄 Output file: {output_file}")
    print(f"\n💡 Next step: Run AI verification:")
    print(f"   python3 scripts/research_tools/ai_verify_property.py --file {output_file}")
    print("=" * 70 + "\n")


def extract_machine_setting(setting_name: str, output_file: Path):
    """Extract a machine setting from all materials"""
    
    print(f"\n🔍 Extracting setting: {setting_name}")
    print("=" * 70)
    
    # Load materials
    materials_data = load_materials()
    materials = materials_data.get('materials', {})
    
    print(f"📂 Loaded {len(materials)} materials")
    
    # Extract setting from each material
    extracted = {}
    found_count = 0
    missing_count = 0
    
    for material_name, material_data in materials.items():
        if not isinstance(material_data, dict):
            continue
        
        settings = material_data.get('settings', {})
        
        if setting_name in settings:
            setting_data = settings[setting_name]
            if isinstance(setting_data, dict):
                extracted[material_name] = {
                    'current_value': setting_data.get('value'),
                    'unit': setting_data.get('unit', ''),
                    'confidence': setting_data.get('confidence'),
                    'source': setting_data.get('source', ''),
                    'description': setting_data.get('description', ''),
                    'min': setting_data.get('min'),
                    'max': setting_data.get('max'),
                    'category': material_data.get('category', 'unknown'),
                    'ai_verified_value': None,
                    'variance': None,
                    'status': 'PENDING',
                }
                found_count += 1
            else:
                missing_count += 1
        else:
            missing_count += 1
    
    print(f"✅ Found {found_count} materials with setting '{setting_name}'")
    print(f"⚠️  Missing from {missing_count} materials")
    
    # Create research file
    research_data = {
        'setting': {
            'name': setting_name,
            'extraction_date': datetime.now().isoformat(),
            'total_materials': len(materials),
            'extracted_count': found_count,
            'missing_count': missing_count
        },
        'materials': extracted,
        'research_status': {
            'extraction_complete': True,
            'ai_verification_complete': False,
            'ready_for_merge': False
        }
    }
    
    # Write to file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        yaml.dump(research_data, f, default_flow_style=False, sort_keys=False, indent=2)
    
    print(f"\n✅ Extraction complete!")
    print(f"📄 Output file: {output_file}")
    print(f"\n💡 Next step: Run AI verification:")
    print(f"   python3 scripts/research_tools/ai_verify_property.py --file {output_file}")
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Extract a single property or setting from all materials for focused AI research'
    )
    parser.add_argument('--property', type=str, help='Material property name (e.g., density, meltingPoint)')
    parser.add_argument('--setting', type=str, help='Machine setting name (e.g., powerRange, wavelength)')
    parser.add_argument('--output', type=str, help='Output file path (optional)')
    
    args = parser.parse_args()
    
    if not args.property and not args.setting:
        print("❌ Error: Must specify either --property or --setting")
        parser.print_help()
        sys.exit(1)
    
    if args.property and args.setting:
        print("❌ Error: Specify only one of --property or --setting")
        sys.exit(1)
    
    # Determine output file
    if args.output:
        output_file = Path(args.output)
    elif args.property:
        output_file = project_root / 'data' / 'research' / 'material_properties' / f'{args.property}_research.yaml'
    else:  # args.setting
        output_file = project_root / 'data' / 'research' / 'machine_settings' / f'{args.setting}_research.yaml'
    
    # Extract
    if args.property:
        extract_material_property(args.property, output_file)
    else:
        extract_machine_setting(args.setting, output_file)


if __name__ == '__main__':
    main()
