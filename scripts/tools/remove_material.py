#!/usr/bin/env python3
"""
Remove a material from the data and frontmatter.

This script:
1. Removes the material from data/materials/Materials.yaml (with backup)
2. Deletes the corresponding frontmatter file from frontmatter/materials/
3. Deletes the corresponding settings file from frontmatter/settings/ (if exists)

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


def load_materials_yaml(materials_file: Path) -> dict:
    """Load Materials.yaml file."""
    with open(materials_file) as f:
        return yaml.safe_load(f)


def save_materials_yaml(materials_file: Path, data: dict) -> None:
    """Save Materials.yaml file."""
    with open(materials_file, 'w') as f:
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
    data = load_materials_yaml(materials_file)
    materials = data.get('materials', {})
    
    print(f"\n📋 Materials in {materials_file.name} ({len(materials)} total):\n")
    for name in sorted(materials.keys()):
        print(f"  • {name}")
    print()


def remove_material(material_name: str, dry_run: bool = False) -> bool:
    """
    Remove a material from all data sources.
    
    Returns True if successful, False otherwise.
    """
    base_path = Path(__file__).parent.parent.parent
    materials_file = base_path / 'data' / 'materials' / 'Materials.yaml'
    frontmatter_dir = base_path / 'frontmatter' / 'materials'
    settings_dir = base_path / 'frontmatter' / 'settings'
    
    # Load materials data
    if not materials_file.exists():
        print(f"❌ Error: Materials file not found: {materials_file}")
        return False
    
    data = load_materials_yaml(materials_file)
    materials = data.get('materials', {})
    
    # Find the material (case-insensitive)
    material_key = find_material_key(materials, material_name)
    
    if not material_key:
        print(f"❌ Error: Material '{material_name}' not found in Materials.yaml")
        print("\n💡 Tip: Use --list to see all available materials")
        return False
    
    # Generate expected file paths
    slug = slugify(material_key)
    frontmatter_file = frontmatter_dir / f"{slug}-laser-cleaning.yaml"
    settings_file = settings_dir / f"{slug}-laser-cleaning.yaml"
    
    print(f"\n{'🔍 DRY RUN - ' if dry_run else ''}Removing material: {material_key}")
    print("=" * 50)
    
    # Step 1: Show what will be removed from Materials.yaml
    print(f"\n📄 Materials.yaml:")
    print(f"   Will remove key: '{material_key}'")
    
    # Step 2: Check frontmatter file
    print(f"\n📁 Frontmatter file:")
    if frontmatter_file.exists():
        print(f"   Will delete: {frontmatter_file.relative_to(base_path)}")
    else:
        print(f"   Not found: {frontmatter_file.relative_to(base_path)} (skipping)")
    
    # Step 3: Check settings file
    print(f"\n⚙️  Settings file:")
    if settings_file.exists():
        print(f"   Will delete: {settings_file.relative_to(base_path)}")
    else:
        print(f"   Not found: {settings_file.relative_to(base_path)} (skipping)")
    
    if dry_run:
        print(f"\n🔍 DRY RUN complete - no changes made")
        return True
    
    # Confirm
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
    
    # Remove from Materials.yaml
    del materials[material_key]
    save_materials_yaml(materials_file, data)
    print(f"✅ Removed '{material_key}' from Materials.yaml")
    
    # Delete frontmatter file
    if frontmatter_file.exists():
        frontmatter_file.unlink()
        print(f"✅ Deleted {frontmatter_file.relative_to(base_path)}")
    
    # Delete settings file
    if settings_file.exists():
        settings_file.unlink()
        print(f"✅ Deleted {settings_file.relative_to(base_path)}")
    
    print(f"\n🎉 Material '{material_key}' successfully removed!")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Remove a material from data and frontmatter files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/tools/remove_material.py "Nitinol"
  python3 scripts/tools/remove_material.py --dry-run "Aluminum"
  python3 scripts/tools/remove_material.py --list
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
    
    success = remove_material(args.material, dry_run=args.dry_run)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
