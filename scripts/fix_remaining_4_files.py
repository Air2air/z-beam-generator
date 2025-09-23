#!/usr/bin/env python3
"""
Fix the remaining 4 files with encoding/migration issues:
- aluminum-laser-cleaning.md
- copper-laser-cleaning.md  
- steel-laser-cleaning.md
- titanium-laser-cleaning.md

This script migrates them from meltingPoint to thermalDestructionPoint schema.
"""

import re
import yaml
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
    """Migrate frontmatter content from old thermal properties to unified schema."""
    thermal_destruction_type = get_thermal_destruction_type(material_name, materials_config)
    
    modified = False
    
    # Replace meltingPoint with thermalDestructionPoint
    melting_point_pattern = r'(\s+)meltingPoint:\s*["\']?([^"\'\n]+)["\']?'
    if re.search(melting_point_pattern, content):
        content = re.sub(
            melting_point_pattern,
            r'\1thermalDestructionPoint: "\2"',
            content
        )
        modified = True
        print(f"  ✅ Migrated meltingPoint to thermalDestructionPoint")
    
    # Replace decompositionPoint with thermalDestructionPoint
    decomp_point_pattern = r'(\s+)decompositionPoint:\s*["\']?([^"\'\n]+)["\']?'
    if re.search(decomp_point_pattern, content):
        content = re.sub(
            decomp_point_pattern,
            r'\1thermalDestructionPoint: "\2"',
            content
        )
        modified = True
        print(f"  ✅ Migrated decompositionPoint to thermalDestructionPoint")
    
    # Remove old thermalBehaviorType if present
    thermal_behavior_pattern = r'\s+thermalBehaviorType:\s*["\']?[^"\'\n]+["\']?\n?'
    if re.search(thermal_behavior_pattern, content):
        content = re.sub(thermal_behavior_pattern, '', content)
        modified = True
        print(f"  ✅ Removed old thermalBehaviorType")
    
    # Add thermalDestructionType if not present
    if 'thermalDestructionType:' not in content and 'thermalDestructionPoint:' in content:
        # Find the thermalDestructionPoint line and add thermalDestructionType after it
        thermal_point_pattern = r'(\s+thermalDestructionPoint:\s*["\'][^"\']+["\'])\n'
        match = re.search(thermal_point_pattern, content)
        if match:
            indent = re.match(r'^(\s+)', match.group(1)).group(1)
            replacement = f'{match.group(1)}\n{indent}thermalDestructionType: "{thermal_destruction_type}"\n'
            content = re.sub(thermal_point_pattern, replacement, content)
            modified = True
            print(f"  ✅ Added thermalDestructionType: {thermal_destruction_type}")
    
    return content, modified

def main():
    """Fix the 4 specific files with encoding/migration issues."""
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
            # Read current content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Migrate thermal properties
            new_content, modified = migrate_frontmatter_content(content, material_name, materials_config)
            
            if modified:
                # Write back the migrated content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"  ✅ Successfully migrated {filename}")
            else:
                print(f"  ℹ️  No migration needed for {filename}")
                
        except Exception as e:
            print(f"  ❌ Error processing {filename}: {e}")

if __name__ == "__main__":
    main()
