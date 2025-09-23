#!/usr/bin/env python3
"""
Fix encoding issues and migrate thermal properties for the 4 remaining files.
This script handles unicode escapes and migrates to unified thermal schema.
"""

import re
import yaml
from pathlib import Path
from typing import Dict, Any

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

def fix_unicode_escapes(content: str) -> str:
    """Fix common unicode escape sequences."""
    # Fix degree symbol
    content = content.replace('\\xB0', '°')
    # Fix superscript 3 (cubed)
    content = content.replace('\\xB3', '³')
    # Fix superscript 2 (squared)  
    content = content.replace('\\xB2', '²')
    # Fix middle dot
    content = content.replace('\\xB7', '·')
    return content

def migrate_thermal_properties(content: str, material_name: str, materials_config: Dict[str, Any]) -> str:
    """Migrate thermal properties to unified schema."""
    thermal_destruction_type = get_thermal_destruction_type(material_name, materials_config)
    
    # Replace meltingPoint with thermalDestructionPoint and add thermalDestructionType
    melting_point_pattern = r'(\s+)meltingPoint:\s*["\']?([^"\'\n]+)["\']?'
    if re.search(melting_point_pattern, content):
        # First replace meltingPoint with thermalDestructionPoint
        content = re.sub(
            melting_point_pattern,
            r'\1thermalDestructionPoint: "\2"\n\1thermalDestructionType: "' + thermal_destruction_type + '"',
            content
        )
        print(f"  ✅ Migrated meltingPoint to unified thermal properties")
    
    # Handle case where there's meltingPointNumeric but no meltingPoint
    elif 'meltingPointNumeric:' in content and 'thermalDestructionPoint:' not in content:
        # Find the meltingPointNumeric value and unit
        numeric_pattern = r'(\s+)meltingPointNumeric:\s*([0-9.]+)\s*\n\s+meltingPointUnit:\s*["\']?([^"\'\n]+)["\']?'
        match = re.search(numeric_pattern, content)
        if match:
            indent = match.group(1)
            numeric_value = match.group(2)
            unit = match.group(3)
            
            # Create the unified thermal properties after the existing meltingPointUnit line
            thermal_props = f'\n{indent}thermalDestructionPoint: "{numeric_value}{unit}"\n{indent}thermalDestructionType: "{thermal_destruction_type}"'
            
            # Insert after meltingPointUnit
            unit_pattern = r'(\s+meltingPointUnit:\s*["\']?[^"\'\n]+["\']?)'
            content = re.sub(unit_pattern, r'\1' + thermal_props, content)
            print(f"  ✅ Created thermal properties from numeric values: {numeric_value}{unit}")
    
    # Remove old thermalBehaviorType if present
    thermal_behavior_pattern = r'\s+thermalBehaviorType:\s*["\']?[^"\'\n]+["\']?\n?'
    if re.search(thermal_behavior_pattern, content):
        content = re.sub(thermal_behavior_pattern, '', content)
        print(f"  ✅ Removed old thermalBehaviorType")
    
    return content

def main():
    """Fix the 4 specific files with encoding and migration issues."""
    materials_config = load_materials_config()
    
    files_to_fix = [
        "aluminum-laser-cleaning.md",
        "copper-laser-cleaning.md", 
        "steel-laser-cleaning.md",
        "titanium-laser-cleaning.md"
    ]
    
    frontmatter_dir = Path(__file__).parent.parent / "content" / "components" / "frontmatter"
    
    for filename in files_to_fix:
        file_path = frontmatter_dir / filename
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            continue
            
        # Extract material name from filename
        material_name = filename.replace("-laser-cleaning.md", "")
        print(f"\n🔧 Processing {material_name}...")
        
        try:
            # Read current content as bytes to handle encoding issues
            with open(file_path, 'rb') as f:
                raw_content = f.read()
            
            # Decode with error handling
            try:
                content = raw_content.decode('utf-8')
            except UnicodeDecodeError:
                content = raw_content.decode('utf-8', errors='replace')
                print(f"  ⚠️  Had to replace some invalid unicode characters")
            
            # Fix unicode escapes
            content = fix_unicode_escapes(content)
            print(f"  ✅ Fixed unicode escape sequences")
            
            # Migrate thermal properties if needed
            if 'meltingPoint:' in content and 'thermalDestructionPoint:' not in content:
                content = migrate_thermal_properties(content, material_name, materials_config)
            elif 'thermalDestructionPoint:' in content:
                print(f"  ℹ️  Thermal properties already migrated")
            else:
                print(f"  ℹ️  No thermal properties found to migrate")
            
            # Write back the fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Successfully fixed {filename}")
                
        except Exception as e:
            print(f"  ❌ Error processing {filename}: {e}")

if __name__ == "__main__":
    main()
