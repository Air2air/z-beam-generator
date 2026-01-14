"""
Backfill Distinctive Properties to Materials.yaml

Populates section-specific distinctive properties for all materials.
Writes results to source data (Materials.yaml) for use during generation.

Complies with Core Principle 0.6: Generate to Data, Not Enrichers
- Distinctive properties calculated ONCE during backfill
- Stored in Materials.yaml for reading during generation
- Export only formats existing complete data

Usage:
    python3 scripts/backfill/populate_distinctive_properties.py
    python3 scripts/backfill/populate_distinctive_properties.py --material aluminum-laser-cleaning
    python3 scripts/backfill/populate_distinctive_properties.py --dry-run
"""

import sys
import argparse
import yaml
import tempfile
from pathlib import Path
from typing import Dict, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from generation.utils.property_selector import PropertySelector
from shared.utils.file_io import read_yaml_file


def load_materials() -> Dict:
    """Load Materials.yaml"""
    materials_path = project_root / 'data/materials/Materials.yaml'
    return read_yaml_file(materials_path)


def save_materials(data: Dict, dry_run: bool = False) -> None:
    """Save Materials.yaml with atomic write"""
    materials_path = project_root / 'data/materials/Materials.yaml'
    
    if dry_run:
        print(f"🔍 DRY RUN: Would save to {materials_path}")
        return
    
    # Atomic write pattern
    with tempfile.NamedTemporaryFile(
        mode='w',
        encoding='utf-8',
        dir=materials_path.parent,
        delete=False,
        suffix='.yaml'
    ) as temp_f:
        yaml.dump(
            data,
            temp_f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120
        )
        temp_path = temp_f.name
    
    # Replace original
    Path(temp_path).replace(materials_path)
    print(f"✅ Saved to {materials_path}")


def populate_distinctive_properties(
    material_name: str,
    material_data: Dict,
    selector: PropertySelector,
    section_types: List[str]
) -> Dict:
    """
    Populate distinctive properties for all section types.
    
    Args:
        material_name: Material identifier
        material_data: Material data dict (will be modified)
        selector: PropertySelector instance
        section_types: List of section types to populate
        
    Returns:
        Modified material_data with distinctive properties
    """
    print(f"\n📊 Processing: {material_name}")
    
    for section_type in section_types:
        try:
            distinctive_props = selector.select_distinctive_properties(
                material_name=material_name,
                section_type=section_type,
                count=3
            )
            
            if distinctive_props:
                # Store under section-specific key
                key = f"_distinctive_{section_type}"
                material_data[key] = distinctive_props
                
                print(f"  ✅ {section_type}: {len(distinctive_props)} properties")
                for prop in distinctive_props:
                    print(f"     • {prop['name']}: {prop['value']} {prop['unit']} (z={prop['distinctiveness_score']:.2f})")
            else:
                print(f"  ⚠️  {section_type}: No distinctive properties found")
                
        except Exception as e:
            print(f"  ❌ {section_type}: Error - {e}")
    
    return material_data


def main():
    parser = argparse.ArgumentParser(description='Backfill distinctive properties to Materials.yaml')
    parser.add_argument('--material', help='Process single material (e.g., aluminum-laser-cleaning)')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without saving')
    parser.add_argument('--section-types', nargs='+', 
                       default=['materialCharacteristics_description', 'laserMaterialInteraction_description'],
                       help='Section types to populate')
    
    args = parser.parse_args()
    
    print("="*80)
    print("🔬 DISTINCTIVE PROPERTIES BACKFILL")
    print("="*80)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'WRITE TO SOURCE'}")
    print(f"Section types: {', '.join(args.section_types)}")
    print("="*80)
    
    # Load materials
    materials_data = load_materials()
    materials = materials_data.get('materials', {})
    
    if not materials:
        print("❌ No materials found in Materials.yaml")
        return
    
    # Initialize PropertySelector
    selector = PropertySelector()
    
    # Process materials
    if args.material:
        # Single material
        if args.material not in materials:
            print(f"❌ Material '{args.material}' not found")
            return
        
        materials[args.material] = populate_distinctive_properties(
            args.material,
            materials[args.material],
            selector,
            args.section_types
        )
        processed = 1
    else:
        # All materials
        processed = 0
        for material_name, material_data in materials.items():
            materials[material_name] = populate_distinctive_properties(
                material_name,
                material_data,
                selector,
                args.section_types
            )
            processed += 1
    
    print("\n" + "="*80)
    print(f"📊 SUMMARY")
    print("="*80)
    print(f"Materials processed: {processed}")
    print(f"Section types per material: {len(args.section_types)}")
    print(f"Total distinctive property sets: {processed * len(args.section_types)}")
    
    # Save
    materials_data['materials'] = materials
    save_materials(materials_data, dry_run=args.dry_run)
    
    if not args.dry_run:
        print("\n✅ Distinctive properties written to Materials.yaml")
        print("   Generation will now read these pre-calculated properties")
        print("   Run generation to use the new data:")
        print(f"   python3 run.py --backfill --domain materials --generator multi_field_text --item {args.material or 'aluminum-laser-cleaning'}")


if __name__ == '__main__':
    main()
