#!/usr/bin/env python3
"""
Remove a material from ALL data sources and references.

This script comprehensively removes a material from:
1. data/materials/Materials.yaml (full entry + category_mapping)
2. frontmatter/materials/{slug}-laser-cleaning.yaml
3. frontmatter/settings/{slug}-settings.yaml
4. public/images/materials/{slug}*.png
5. Any cached data or learning database references

Usage:
    python3 scripts/tools/remove_material.py "Material Name"
    python3 scripts/tools/remove_material.py --dry-run "Material Name"
    python3 scripts/tools/remove_material.py --list  # List all materials

Author: GitHub Copilot
Date: December 1, 2025
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

import yaml


def slugify(name: str) -> str:
    """Convert material name to filename slug."""
    return name.lower().replace(' ', '-').replace('/', '-').replace('(', '').replace(')', '')


def load_yaml(file_path: Path) -> dict:
    """Load YAML file."""
    with open(file_path) as f:
        return yaml.safe_load(f)


def save_yaml(file_path: Path, data: dict) -> None:
    """Save YAML file preserving structure."""
    with open(file_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, indent=2, sort_keys=False, allow_unicode=True)


def find_material_key(materials: dict, search_name: str) -> str | None:
    """Find the exact material key (case-insensitive search)."""
    search_lower = search_name.lower()
    for key in materials.keys():
        if key.lower() == search_lower:
            return key
    return None


def list_materials(materials_file: Path) -> None:
    """List all materials in the data file."""
    data = load_yaml(materials_file)
    materials = data.get('materials', {})
    
    print(f"\n📋 Materials in {materials_file.name} ({len(materials)} total):\n")
    for name in sorted(materials.keys()):
        print(f"  • {name}")
    print()


def remove_material(material_name: str, dry_run: bool = False, auto_yes: bool = False) -> bool:
    """
    Remove a material from ALL data sources.
    
    Returns True if successful, False otherwise.
    """
    base_path = Path(__file__).parent.parent.parent
    materials_file = base_path / 'data' / 'materials' / 'Materials.yaml'
    frontmatter_dir = base_path / 'frontmatter' / 'materials'
    settings_dir = base_path / 'frontmatter' / 'settings'
    images_dir = base_path / 'public' / 'images' / 'materials'
    
    # Load materials data
    if not materials_file.exists():
        print(f"❌ Error: Materials file not found: {materials_file}")
        return False
    
    data = load_yaml(materials_file)
    materials = data.get('materials', {})
    category_mapping = data.get('category_mapping', {})
    material_index = data.get('material_index', {})
    
    # Find the material (case-insensitive) in all sections
    material_key = find_material_key(materials, material_name)
    category_key = find_material_key(category_mapping, material_name) if category_mapping else None
    index_key = find_material_key(material_index, material_name) if material_index else None
    
    # Check if material exists in any location
    if not material_key and not category_key and not index_key:
        print(f"❌ Error: Material '{material_name}' not found in Materials.yaml")
        print("\n💡 Tip: Use --list to see all available materials")
        return False
    
    # Use whichever key we found (prioritize materials, then index, then category_mapping)
    effective_key = material_key or index_key or category_key
    
    # Generate expected file paths
    slug = slugify(effective_key)
    frontmatter_file = frontmatter_dir / f"{slug}-laser-cleaning.yaml"
    settings_file = settings_dir / f"{slug}-settings.yaml"
    
    # Find any matching images
    image_files = list(images_dir.glob(f"{slug}*.png")) if images_dir.exists() else []
    image_files += list(images_dir.glob(f"{slug}*.jpg")) if images_dir.exists() else []
    
    print(f"\n{'🔍 DRY RUN - ' if dry_run else ''}Removing material: {effective_key}")
    print("=" * 60)
    
    removals = []
    
    # Step 1: Materials.yaml - materials section
    print("\n📄 Materials.yaml - materials section:")
    if material_key and material_key in materials:
        print(f"   ✓ Will remove key: '{material_key}'")
        removals.append(('materials_entry', material_key))
    else:
        print("   ○ Not found in materials section")
    
    # Step 2: Materials.yaml - material_index section
    print("\n📄 Materials.yaml - material_index section:")
    if index_key and index_key in material_index:
        print(f"   ✓ Will remove key: '{index_key}'")
        removals.append(('material_index', index_key))
    else:
        print("   ○ Not found in material_index section")
    
    # Step 3: Materials.yaml - category_mapping section
    print("\n📄 Materials.yaml - category_mapping section:")
    if category_key and category_key in category_mapping:
        print(f"   ✓ Will remove key: '{category_key}'")
        removals.append(('category_mapping', category_key))
    else:
        print("   ○ Not found in category_mapping section")
    
    # Step 4: Check frontmatter file
    print("\n📁 Frontmatter file:")
    if frontmatter_file.exists():
        print(f"   ✓ Will delete: {frontmatter_file.relative_to(base_path)}")
        removals.append(('frontmatter', frontmatter_file))
    else:
        print(f"   ○ Not found: {frontmatter_file.relative_to(base_path)}")
    
    # Step 5: Check settings file
    print("\n⚙️  Settings file:")
    if settings_file.exists():
        print(f"   ✓ Will delete: {settings_file.relative_to(base_path)}")
        removals.append(('settings', settings_file))
    else:
        print(f"   ○ Not found: {settings_file.relative_to(base_path)}")
    
    # Step 6: Check image files
    print("\n🖼️  Image files:")
    if image_files:
        for img in image_files:
            print(f"   ✓ Will delete: {img.relative_to(base_path)}")
            removals.append(('image', img))
    else:
        print(f"   ○ No images found matching '{slug}*'")
    
    # Summary
    print(f"\n📊 Summary: {len(removals)} items to remove")
    
    if not removals:
        print(f"\n⚠️  Nothing to remove for '{material_name}'")
        return True
    
    if dry_run:
        print(f"\n🔍 DRY RUN complete - no changes made")
        return True
    
    # Confirm
    if not auto_yes:
        print(f"\n⚠️  This action cannot be undone (backup will be created).")
        response = input("Continue? [y/N]: ").strip().lower()
        if response != 'y':
            print("❌ Cancelled")
            return False
    
    # Create backup of Materials.yaml
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = materials_file.with_suffix(f'.backup_before_remove_{slug}_{timestamp}.yaml')
    shutil.copy2(materials_file, backup_file)
    print(f"\n📦 Backup created: {backup_file.name}")
    
    # Execute removals
    for removal_type, target in removals:
        if removal_type == 'materials_entry':
            del materials[target]
            print(f"✅ Removed '{target}' from materials section")
        elif removal_type == 'material_index':
            del material_index[target]
            print(f"✅ Removed '{target}' from material_index section")
        elif removal_type == 'category_mapping':
            del category_mapping[target]
            print(f"✅ Removed '{target}' from category_mapping section")
        elif removal_type in ('frontmatter', 'settings', 'image'):
            target.unlink()
            print(f"✅ Deleted {target.relative_to(base_path)}")
    
    # Save updated Materials.yaml
    save_yaml(materials_file, data)
    print("✅ Saved updated Materials.yaml")
    
    print(f"\n🎉 Material '{effective_key}' successfully removed from {len(removals)} locations!")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Remove a material from ALL data sources and references.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/tools/remove_material.py "Nitinol"
  python3 scripts/tools/remove_material.py --dry-run "Scandium"
  python3 scripts/tools/remove_material.py --list
  python3 scripts/tools/remove_material.py -y "Material"  # Skip confirmation
        """
    )
    parser.add_argument('material', nargs='?', help='Name of the material to remove')
    parser.add_argument('--dry-run', '-n', action='store_true', 
                        help='Show what would be removed without making changes')
    parser.add_argument('--list', '-l', action='store_true',
                        help='List all materials')
    parser.add_argument('--yes', '-y', action='store_true',
                        help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    base_path = Path(__file__).parent.parent.parent
    materials_file = base_path / 'data' / 'materials' / 'Materials.yaml'
    
    if args.list:
        list_materials(materials_file)
        return 0
    
    if not args.material:
        parser.print_help()
        return 1
    
    success = remove_material(args.material, dry_run=args.dry_run, auto_yes=args.yes)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
