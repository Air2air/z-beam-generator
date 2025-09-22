#!/usr/bin/env python3
"""
Fix Surface Roughness Values - Ensure Single Averaged Values

Ensures all surface roughness values in frontmatter are single averaged numbers.
Fixes YAML structure issues and applies consistent formatting.
"""

import yaml
from pathlib import Path

def fix_frontmatter_and_apply_surface_roughness():
    """Fix frontmatter structure and apply single surface roughness values"""
    
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
        "palladium": {"before": 3.1, "after": 0.7},
        "rhodium": {"before": 2.8, "after": 0.6},
        "iridium": {"before": 3.5, "after": 0.8},
        "ruthenium": {"before": 4.2, "after": 1.0},
        "tungsten": {"before": 6.3, "after": 1.8},
        "molybdenum": {"before": 5.8, "after": 1.5},
        "tantalum": {"before": 5.2, "after": 1.3},
        "niobium": {"before": 4.8, "after": 1.2},
        "rhenium": {"before": 5.5, "after": 1.6},
        "silicon": {"before": 0.8, "after": 0.15},
        "germanium": {"before": 1.2, "after": 0.25},
        "gallium-arsenide": {"before": 1.5, "after": 0.3},
        "indium-phosphide": {"before": 1.8, "after": 0.4},
        "silicon-carbide": {"before": 2.2, "after": 0.6},
        "gallium-nitride": {"before": 2.8, "after": 0.7},
        "alumina": {"before": 3.5, "after": 0.8},
        "zirconia": {"before": 4.2, "after": 1.0},
        "silicon-nitride": {"before": 2.8, "after": 0.7},
        "boron-carbide": {"before": 5.5, "after": 1.5},
        "tungsten-carbide": {"before": 6.8, "after": 1.8},
        "titanium-carbide": {"before": 5.2, "after": 1.4},
        "granite": {"before": 25.5, "after": 8.5},
        "marble": {"before": 18.2, "after": 6.2},
        "limestone": {"before": 22.8, "after": 7.8},
        "sandstone": {"before": 28.5, "after": 9.5},
        "slate": {"before": 15.5, "after": 5.2},
        "quartzite": {"before": 12.8, "after": 4.2},
        "travertine": {"before": 28.5, "after": 9.8},
        "onyx": {"before": 18.5, "after": 6.5},
        "basalt": {"before": 32.5, "after": 11.2},
        "shale": {"before": 35.8, "after": 12.5},
        "porphyry": {"before": 22.5, "after": 7.8},
        "alabaster": {"before": 15.2, "after": 5.5},
        "oak": {"before": 45.5, "after": 18.2},
        "maple": {"before": 38.8, "after": 15.5},
        "cherry": {"before": 42.2, "after": 16.8},
        "walnut": {"before": 44.8, "after": 17.8},
        "mahogany": {"before": 41.5, "after": 16.2},
        "pine": {"before": 52.5, "after": 21.8},
        "fir": {"before": 48.2, "after": 19.8},
        "cedar": {"before": 55.8, "after": 23.2},
        "birch": {"before": 38.5, "after": 15.2},
        "ash": {"before": 46.8, "after": 18.8},
        "beech": {"before": 41.2, "after": 16.5},
        "hickory": {"before": 48.5, "after": 19.2},
        "poplar": {"before": 58.2, "after": 24.5},
        "basswood": {"before": 62.5, "after": 26.2},
        "willow": {"before": 68.8, "after": 28.8},
        "bamboo": {"before": 35.2, "after": 14.8},
        "teak": {"before": 32.5, "after": 13.2},
        "rosewood": {"before": 28.8, "after": 11.8},
        "ebony": {"before": 25.5, "after": 10.5},
        "carbon-fiber": {"before": 8.5, "after": 2.8},
        "fiberglass": {"before": 12.8, "after": 4.5},
        "kevlar": {"before": 15.2, "after": 5.8},
        "nomex": {"before": 18.5, "after": 7.2},
        "glass": {"before": 2.8, "after": 0.8},
        "quartz": {"before": 1.5, "after": 0.4},
        "borosilicate": {"before": 2.2, "after": 0.6},
        "acrylic": {"before": 8.8, "after": 3.2},
        "polycarbonate": {"before": 12.5, "after": 4.8},
        "delrin": {"before": 15.8, "after": 6.2},
        "nylon": {"before": 18.2, "after": 7.5},
        "peek": {"before": 8.2, "after": 3.5},
        "teflon": {"before": 22.5, "after": 9.8}
    }
    
    frontmatter_dir = Path("content/components/frontmatter")
    
    if not frontmatter_dir.exists():
        print(f"Error: {frontmatter_dir} directory not found")
        return
    
    processed = 0
    updated = 0
    errors = 0
    
    print("🔧 Fixing frontmatter structure and applying single surface roughness values...")
    
    for file_path in frontmatter_dir.glob("*-laser-cleaning.md"):
        material_name = file_path.stem.replace("-laser-cleaning", "")
        
        try:
            # Read the entire file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Handle files that might not have proper YAML delimiters
            if content.startswith('---\n'):
                # Find the end of frontmatter
                end_marker_pos = content.find('\n---\n', 4)
                if end_marker_pos == -1:
                    # No closing marker found, add one
                    yaml_content = content[4:]  # Remove opening ---\n
                    body_content = ""
                else:
                    yaml_content = content[4:end_marker_pos]
                    body_content = content[end_marker_pos + 5:]  # After \n---\n
            else:
                print(f"❌ {material_name}: No frontmatter structure found")
                errors += 1
                continue
            
            # Parse YAML
            try:
                data = yaml.safe_load(yaml_content)
            except yaml.YAMLError as e:
                print(f"❌ {material_name}: YAML parsing error - {e}")
                errors += 1
                continue
            
            if not isinstance(data, dict):
                print(f"❌ {material_name}: Invalid YAML structure")
                errors += 1
                continue
            
            # Apply surface roughness data if available
            if material_name in surface_data:
                if 'outcomes' not in data:
                    data['outcomes'] = {}
                
                # Apply single values only
                roughness = surface_data[material_name]
                data['outcomes']['surface_roughness_before'] = float(roughness['before'])
                data['outcomes']['surface_roughness_after'] = float(roughness['after'])
                
                # Write back with proper structure
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("---\n")
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                    f.write("---\n")
                    if body_content.strip():
                        f.write(body_content)
                
                print(f"✅ {material_name:<20} - {roughness['before']} → {roughness['after']} μm (SINGLE VALUES)")
                updated += 1
            else:
                # Still fix the file structure even without surface roughness data
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("---\n")
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                    f.write("---\n")
                    if body_content.strip():
                        f.write(body_content)
                
                print(f"🔧 {material_name:<20} - Fixed structure (no surface data)")
            
            processed += 1
            
        except Exception as e:
            print(f"❌ {material_name}: Error - {e}")
            errors += 1
    
    print("\n📊 Summary:")
    print(f"   Files processed: {processed}")
    print(f"   Surface roughness updated: {updated}")
    print(f"   Errors: {errors}")
    
    if updated > 0:
        print(f"\n✅ Successfully applied single averaged values to {updated} materials")

if __name__ == "__main__":
    fix_frontmatter_and_apply_surface_roughness()
