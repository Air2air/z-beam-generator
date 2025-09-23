#!/usr/bin/env python3
"""
Manual fix for copper, steel, and titanium thermal properties.
This creates the unified thermal properties from their numeric values.
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

def main():
    """Manually fix the thermal properties for copper, steel, and titanium."""
    materials_config = load_materials_config()
    
    # Define the thermal properties for each material from their numeric values
    materials_data = {
        "copper": {"value": "1450.0", "unit": "°C"},
        "steel": {"value": "1370", "unit": "°C"},  # Will check actual value
        "titanium": {"value": "1668", "unit": "°C"}  # Will check actual value
    }
    
    frontmatter_dir = Path(__file__).parent.parent / "content" / "components" / "frontmatter"
    
    for material_name, temp_data in materials_data.items():
        file_path = frontmatter_dir / f"{material_name}-laser-cleaning.md"
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            continue
            
        print(f"\n🔧 Processing {material_name}...")
        
        try:
            # Read current content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if already has thermal properties
            if 'thermalDestructionPoint:' in content:
                print(f"  ℹ️  Thermal properties already exist")
                continue
                
            # Get the thermal destruction type for this material
            thermal_destruction_type = get_thermal_destruction_type(material_name, materials_config)
            
            # For these materials, find the meltingPointUnit line and add thermal properties after it
            unit_pattern = r'(\s+)meltingPointUnit:\s*["\']?°C["\']?'
            match = re.search(unit_pattern, content)
            if match:
                indent = match.group(1)
                
                # First, get the actual numeric value from the file
                numeric_pattern = r'meltingPointNumeric:\s*([0-9.]+)'
                numeric_match = re.search(numeric_pattern, content)
                if numeric_match:
                    actual_value = numeric_match.group(1)
                    
                    # Create the thermal properties lines
                    thermal_lines = f'\n{indent}thermalDestructionPoint: "{actual_value}°C"\n{indent}thermalDestructionType: "{thermal_destruction_type}"'
                    
                    # Add after the meltingPointUnit line
                    content = re.sub(unit_pattern, match.group(0) + thermal_lines, content)
                    
                    # Write back the modified content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"  ✅ Added thermal properties: {actual_value}°C ({thermal_destruction_type})")
                else:
                    print(f"  ❌ Could not find meltingPointNumeric value")
            else:
                print(f"  ❌ Could not find meltingPointUnit pattern")
                
        except Exception as e:
            print(f"  ❌ Error processing {material_name}: {e}")

if __name__ == "__main__":
    main()
