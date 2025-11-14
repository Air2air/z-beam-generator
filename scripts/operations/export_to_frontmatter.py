#!/usr/bin/env python3
"""
Simple Frontmatter Export Script

Exports Materials.yaml entries to frontmatter/*.yaml files.
This is a pure YAML-to-YAML copy operation - no AI generation needed.

Usage:
    python3 scripts/export_to_frontmatter.py              # Export all materials
    python3 scripts/export_to_frontmatter.py Aluminum     # Export single material
"""

import yaml
import sys
from pathlib import Path
from typing import Dict


def load_materials() -> Dict:
    """Load materials from Materials.yaml"""
    materials_file = Path(__file__).parent.parent / "materials" / "data" / "Materials.yaml"
    
    with open(materials_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def slugify(name: str) -> str:
    """Convert material name to filename slug"""
    return name.lower().replace(' ', '-').replace('_', '-')


def export_material(material_name: str, material_data: Dict, output_dir: Path) -> bool:
    """
    Export a single material to frontmatter file.
    
    Args:
        material_name: Name of material
        material_data: Material data from Materials.yaml
        output_dir: Output directory (frontmatter/materials/)
        
    Returns:
        True if successful
    """
    try:
        # Create filename
        slug = slugify(material_name)
        output_file = output_dir / f"{slug}-laser-cleaning.yaml"
        
        # Write YAML (preserve structure exactly as in Materials.yaml)
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(
                material_data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                width=120
            )
        
        print(f"✅ {material_name} → {output_file.name}")
        return True
        
    except Exception as e:
        print(f"❌ {material_name}: {e}")
        return False


def export_all_materials(materials_data: Dict, output_dir: Path) -> tuple:
    """
    Export all materials to frontmatter files.
    
    Returns:
        (success_count, failure_count)
    """
    materials_dict = materials_data.get('materials', {})
    
    success = 0
    failure = 0
    
    for material_name, material_data in materials_dict.items():
        if not isinstance(material_data, dict):
            print(f"⚠️  Skipping {material_name} - not a dict")
            continue
        
        if export_material(material_name, material_data, output_dir):
            success += 1
        else:
            failure += 1
    
    return success, failure


def main():
    """Main export function"""
    print("=" * 60)
    print("FRONTMATTER EXPORT - Materials.yaml → frontmatter/*.yaml")
    print("=" * 60)
    print()
    
    # Setup paths
    output_dir = Path(__file__).parent.parent / "frontmatter" / "materials"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load materials
    print("📂 Loading Materials.yaml...")
    materials_data = load_materials()
    print(f"✅ Loaded {len(materials_data.get('materials', {}))} materials")
    print()
    
    # Check if specific material requested
    if len(sys.argv) > 1:
        material_name = sys.argv[1]
        print(f"📤 Exporting single material: {material_name}")
        print()
        
        materials_dict = materials_data.get('materials', {})
        if material_name not in materials_dict:
            print(f"❌ Material '{material_name}' not found in Materials.yaml")
            sys.exit(1)
        
        material_data = materials_dict[material_name]
        success = export_material(material_name, material_data, output_dir)
        
        print()
        if success:
            print("✅ Export complete!")
            sys.exit(0)
        else:
            print("❌ Export failed")
            sys.exit(1)
    
    # Export all materials
    print("📤 Exporting all materials...")
    print()
    
    success, failure = export_all_materials(materials_data, output_dir)
    
    print()
    print("=" * 60)
    print(f"✅ Successfully exported: {success} materials")
    if failure > 0:
        print(f"❌ Failed: {failure} materials")
    print(f"📁 Output directory: {output_dir}")
    print("=" * 60)
    
    sys.exit(0 if failure == 0 else 1)


if __name__ == "__main__":
    main()
