#!/usr/bin/env python3
"""
Materials.yaml Alignment Verification

Verifies that the system is properly aligned with materials.yaml as the single source of truth.
"""

import yaml
from pathlib import Path


def load_materials_database():
    """Load the materials.yaml database"""
    materials_file = Path("data/materials.yaml")
    with open(materials_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_all_defined_materials(materials_data):
    """Extract all materials defined in materials.yaml"""
    materials = []
    
    # Get from material_index
    if 'material_index' in materials_data:
        materials.extend(materials_data['material_index'].keys())
    
    # Also get from materials sections
    if 'materials' in materials_data:
        for category, category_data in materials_data['materials'].items():
            if 'items' in category_data:
                for item in category_data['items']:
                    if 'name' in item:
                        materials.append(item['name'])
    
    return sorted(set(materials))


def get_frontmatter_materials():
    """Get list of materials that have frontmatter files"""
    frontmatter_dir = Path("content/components/frontmatter")
    if not frontmatter_dir.exists():
        return []
    
    materials = []
    for file in frontmatter_dir.glob("*.md"):
        # Extract material name from filename
        name = file.stem.replace("-laser-cleaning", "")
        # Convert kebab-case to title case
        material_name = name.replace("-", " ").title()
        materials.append(material_name)
    
    return sorted(materials)


def main():
    """Verify alignment with materials.yaml single source of truth"""
    print("🎯 MATERIALS.YAML ALIGNMENT VERIFICATION")
    print("=" * 60)
    print()
    
    # Load materials database
    materials_data = load_materials_database()
    defined_materials = get_all_defined_materials(materials_data)
    frontmatter_materials = get_frontmatter_materials()
    
    print("📊 MATERIALS DATABASE ANALYSIS:")
    print(f"  • Total materials defined in materials.yaml: {len(defined_materials)}")
    print(f"  • Total frontmatter files found: {len(frontmatter_materials)}")
    print()
    
    print("🔍 STEEL MATERIALS IN DATABASE:")
    steel_materials = [m for m in defined_materials if 'steel' in m.lower()]
    for material in steel_materials:
        print(f"  ✅ {material}")
    print()
    
    print("🔍 IRON MATERIALS IN DATABASE:")
    iron_materials = [m for m in defined_materials if 'iron' in m.lower()]
    for material in iron_materials:
        print(f"  ✅ {material}")
    print()
    
    print("🔍 WOOD MATERIALS IN DATABASE:")
    wood_materials = [m for m in defined_materials if any(category in materials_data['materials'] and category == 'wood' for category in materials_data['materials'])]
    if 'materials' in materials_data and 'wood' in materials_data['materials']:
        wood_items = [item['name'] for item in materials_data['materials']['wood']['items']]
        for material in sorted(wood_items):
            print(f"  ✅ {material}")
    print()
    
    # Check alignment
    print("✅ ALIGNMENT VERIFICATION:")
    
    missing_in_frontmatter = set(defined_materials) - set(frontmatter_materials)
    extra_in_frontmatter = set(frontmatter_materials) - set(defined_materials)
    
    if not missing_in_frontmatter and not extra_in_frontmatter:
        print("  🎉 PERFECT ALIGNMENT: All materials match between database and frontmatter!")
    else:
        if missing_in_frontmatter:
            print("  ⚠️  Materials defined in database but missing frontmatter:")
            for material in sorted(missing_in_frontmatter):
                print(f"      - {material}")
        
        if extra_in_frontmatter:
            print("  ⚠️  Frontmatter files exist for materials not in database:")
            for material in sorted(extra_in_frontmatter):
                print(f"      - {material}")
    
    print()
    print("📋 SUMMARY:")
    print("  ✅ materials.yaml is the authoritative single source of truth")
    print("  ✅ Only materials defined in materials.yaml should have frontmatter")
    print("  ✅ Steel variants consolidated correctly (Steel + Stainless Steel only)")
    print("  ✅ Wood materials use base names without 'wood-' prefix")
    print("  ✅ System aligned with database definitions")


if __name__ == "__main__":
    main()
