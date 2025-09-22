#!/usr/bin/env python3
"""
Apply Single Surface Roughness Values Only

Only updates surface_roughness_before and surface_roughness_after values,
leaving all other YAML structure unchanged.
"""

import re
from pathlib import Path

def apply_single_surface_roughness_values():
    """Apply only single surface roughness values, preserving existing structure"""
    
    # Single averaged surface roughness data
    surface_data = {
        "aluminum": {"before": 8.5, "after": 1.2},
        "steel": {"before": 15.8, "after": 1.8},
        "stainless-steel": {"before": 6.8, "after": 0.8},
        "titanium": {"before": 4.5, "after": 0.6},
        "copper": {"before": 4.2, "after": 0.7},
        "brass": {"before": 5.8, "after": 1.2},
        "bronze": {"before": 6.2, "after": 1.4},
        "iron": {"before": 18.5, "after": 2.2},
        "nickel": {"before": 5.5, "after": 1.0},
        "zinc": {"before": 8.2, "after": 1.8},
        "lead": {"before": 12.5, "after": 3.2},
        "tin": {"before": 7.8, "after": 1.5},
        "magnesium": {"before": 16.5, "after": 2.5},
        "beryllium": {"before": 3.2, "after": 0.8},
        "gold": {"before": 2.1, "after": 0.4},
        "silver": {"before": 3.8, "after": 0.6},
        "platinum": {"before": 2.5, "after": 0.5},
        "silicon": {"before": 0.8, "after": 0.15},
        "granite": {"before": 25.5, "after": 8.5},
        "marble": {"before": 18.2, "after": 6.2},
        "limestone": {"before": 22.8, "after": 7.8},
        "sandstone": {"before": 28.5, "after": 9.5},
        "slate": {"before": 15.5, "after": 5.2},
        "onyx": {"before": 18.5, "after": 6.5},
        "basalt": {"before": 32.5, "after": 11.2},
        "shale": {"before": 35.8, "after": 12.5},
        "alabaster": {"before": 15.2, "after": 5.5},
        "oak": {"before": 45.5, "after": 18.2},
        "maple": {"before": 38.8, "after": 15.5},
        "cherry": {"before": 42.2, "after": 16.8},
        "pine": {"before": 52.5, "after": 21.8},
        "fir": {"before": 48.2, "after": 19.8},
        "cedar": {"before": 55.8, "after": 23.2},
        "birch": {"before": 38.5, "after": 15.2},
        "ash": {"before": 46.8, "after": 18.8},
        "beech": {"before": 41.2, "after": 16.5},
        "bamboo": {"before": 35.2, "after": 14.8}
    }
    
    frontmatter_dir = Path("content/components/frontmatter")
    
    if not frontmatter_dir.exists():
        print(f"Error: {frontmatter_dir} directory not found")
        return
    
    updated = 0
    skipped = 0
    errors = 0
    
    print("🔧 Applying single surface roughness values (preserving existing structure)...")
    
    for file_path in frontmatter_dir.glob("*-laser-cleaning.md"):
        material_name = file_path.stem.replace("-laser-cleaning", "")
        
        if material_name not in surface_data:
            continue
            
        try:
            # Read the entire file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            roughness = surface_data[material_name]
            
            # Pattern to match and replace surface_roughness_before
            before_pattern = r'(\s*surface_roughness_before:\s*)([0-9.]+)'
            after_pattern = r'(\s*surface_roughness_after:\s*)([0-9.]+)'
            
            # Check if patterns exist
            before_match = re.search(before_pattern, content)
            after_match = re.search(after_pattern, content)
            
            if before_match and after_match:
                # Replace with single values
                content = re.sub(before_pattern, r'\g<1>' + str(roughness['before']), content)
                content = re.sub(after_pattern, r'\g<1>' + str(roughness['after']), content)
                
                # Write back
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ {material_name:<20} - {roughness['before']} → {roughness['after']} μm")
                updated += 1
            else:
                # Need to add surface roughness values
                outcomes_match = re.search(r'(outcomes:\s*\n)', content)
                if outcomes_match:
                    insert_pos = outcomes_match.end()
                    insert_text = f"  surface_roughness_before: {roughness['before']}\n"
                    insert_text += f"  surface_roughness_after: {roughness['after']}\n"
                    
                    content = content[:insert_pos] + insert_text + content[insert_pos:]
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"✅ {material_name:<20} - Added: {roughness['before']} → {roughness['after']} μm")
                    updated += 1
                else:
                    print(f"⚠️  {material_name}: No outcomes section found")
                    skipped += 1
                
        except Exception as e:
            print(f"❌ {material_name}: Error - {e}")
            errors += 1
    
    print("\n📊 Summary:")
    print(f"   Files updated: {updated}")
    print(f"   Files skipped: {skipped}")
    print(f"   Errors: {errors}")
    
    if updated > 0:
        print(f"\n✅ Successfully applied single averaged values to {updated} materials")

if __name__ == "__main__":
    apply_single_surface_roughness_values()
