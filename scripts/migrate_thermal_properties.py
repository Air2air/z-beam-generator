#!/usr/bin/env python3
"""
Thermal Property Migration Script

Migrates existing frontmatter files from fragmented thermal properties 
(meltingPoint/decompositionPoint + thermalBehaviorType) to unified 
thermal property schema (thermalDestructionPoint + thermalDestructionType).

Usage: python3 scripts/migrate_thermal_properties.py [--dry-run]
"""

import re
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any, Tuple

def load_materials_config() -> Dict[str, Any]:
    """Load materials.yaml to get category-based thermal destruction types."""
    materials_path = Path(__file__).parent.parent / "data" / "materials.yaml"
    with open(materials_path, 'r') as f:
        return yaml.safe_load(f)

def get_thermal_destruction_type(material_name: str, materials_config: Dict[str, Any]) -> str:
    """Get the thermal destruction type for a material from materials.yaml."""
    material_index = materials_config.get("material_index", {})
    
    # Try original name, then title case
    lookup_name = material_name
    if lookup_name not in material_index:
        lookup_name = material_name.title()
    
    if lookup_name not in material_index:
        print(f"⚠️  Material '{material_name}' not found in materials.yaml - defaulting to 'melting'")
        return "melting"
    
    category = material_index[lookup_name].get("category")
    if not category:
        print(f"⚠️  Category not found for '{material_name}' - defaulting to 'melting'")
        return "melting"
    
    category_ranges = materials_config.get("category_ranges", {})
    if category not in category_ranges:
        print(f"⚠️  Category '{category}' not found in category_ranges - defaulting to 'melting'")
        return "melting"
    
    return category_ranges[category].get("thermalDestructionType", "melting")

def migrate_frontmatter_content(content: str, material_name: str, materials_config: Dict[str, Any]) -> Tuple[str, bool]:
    """
    Migrate frontmatter content from old thermal properties to unified schema.
    
    Returns:
        Tuple of (migrated_content, was_modified)
    """
    modified = False
    
    # Get the correct thermal destruction type for this material
    thermal_destruction_type = get_thermal_destruction_type(material_name, materials_config)
    
    # Pattern to find properties section
    properties_pattern = r'(properties:\s*\n)(.*?)(\n\w+:|$)'
    properties_match = re.search(properties_pattern, content, re.DOTALL)
    
    if not properties_match:
        print(f"⚠️  No properties section found in {material_name}")
        return content, False
    
    properties_section = properties_match.group(2)
    original_properties = properties_section
    
    # Check for existing thermal properties
    has_melting_point = 'meltingPoint:' in properties_section
    has_decomposition_point = 'decompositionPoint:' in properties_section
    has_thermal_behavior = 'thermalBehaviorType:' in properties_section
    has_thermal_destruction_point = 'thermalDestructionPoint:' in properties_section
    has_thermal_destruction_type = 'thermalDestructionType:' in properties_section
    
    # Skip if already migrated
    if has_thermal_destruction_point and has_thermal_destruction_type:
        print(f"✅ {material_name} already migrated")
        return content, False
    
    # Extract thermal property value
    thermal_value = None
    
    if has_melting_point:
        melting_match = re.search(r'meltingPoint:\s*(.+)', properties_section)
        if melting_match:
            thermal_value = melting_match.group(1).strip()
            # Remove meltingPoint line
            properties_section = re.sub(r'\s*meltingPoint:.*\n', '', properties_section)
            modified = True
    
    if has_decomposition_point:
        decomp_match = re.search(r'decompositionPoint:\s*(.+)', properties_section)
        if decomp_match:
            thermal_value = decomp_match.group(1).strip()
            # Remove decompositionPoint line
            properties_section = re.sub(r'\s*decompositionPoint:.*\n', '', properties_section)
            modified = True
    
    # Remove thermalBehaviorType if present
    if has_thermal_behavior:
        properties_section = re.sub(r'\s*thermalBehaviorType:.*\n', '', properties_section)
        modified = True
    
    # Add unified thermal properties if we found a thermal value
    if thermal_value and modified:
        # Add thermal destruction properties
        thermal_lines = f"  thermalDestructionPoint: {thermal_value}\n"
        thermal_lines += f"  thermalDestructionType: {thermal_destruction_type}\n"
        
        # Insert after density if present, otherwise at the beginning
        if 'density:' in properties_section:
            properties_section = re.sub(
                r'(density:.*\n)', 
                r'\1' + thermal_lines, 
                properties_section, 
                count=1
            )
        else:
            properties_section = thermal_lines + properties_section
    
    # Replace the properties section in the original content
    if modified:
        updated_content = content.replace(original_properties, properties_section)
        return updated_content, True
    
    return content, False

def migrate_frontmatter_file(file_path: Path, materials_config: Dict[str, Any], dry_run: bool = False) -> bool:
    """
    Migrate a single frontmatter file.
    
    Returns:
        True if file was modified, False otherwise
    """
    try:
        # Extract material name from filename
        material_name = file_path.stem.replace('-laser-cleaning', '')
        
        # Read file content with proper encoding handling
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        # Migrate content
        migrated_content, was_modified = migrate_frontmatter_content(content, material_name, materials_config)
        
        if was_modified:
            if dry_run:
                print(f"🔄 Would migrate: {file_path.name}")
            else:
                # Write migrated content back with UTF-8 encoding
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(migrated_content)
                print(f"✅ Migrated: {file_path.name}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error migrating {file_path.name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Migrate thermal properties in frontmatter files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    args = parser.parse_args()
    
    # Load materials configuration
    print("📊 Loading materials configuration...")
    materials_config = load_materials_config()
    
    # Find all frontmatter files
    frontmatter_dir = Path(__file__).parent.parent / "content" / "components" / "frontmatter"
    frontmatter_files = list(frontmatter_dir.glob("*-laser-cleaning.md"))
    
    print(f"🔍 Found {len(frontmatter_files)} frontmatter files")
    
    if args.dry_run:
        print("🧪 DRY RUN MODE - No files will be modified")
    
    # Migrate each file
    migrated_count = 0
    for file_path in frontmatter_files:
        if migrate_frontmatter_file(file_path, materials_config, args.dry_run):
            migrated_count += 1
    
    # Summary
    print("\n📈 Migration Summary:")
    print(f"   Total files: {len(frontmatter_files)}")
    print(f"   {'Would migrate' if args.dry_run else 'Migrated'}: {migrated_count}")
    print(f"   Already up-to-date: {len(frontmatter_files) - migrated_count}")
    
    if args.dry_run and migrated_count > 0:
        print("\n💡 Run without --dry-run to apply changes")

if __name__ == "__main__":
    main()
