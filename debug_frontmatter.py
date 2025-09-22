#!/usr/bin/env python3
"""Debug frontmatter loading for caption generator"""

import yaml
from pathlib import Path

def debug_frontmatter_loading(material_name: str):
    """Debug frontmatter loading exactly like the caption generator"""
    cache_key = material_name.lower()
    
    # Convert material name to filename format - try multiple variations
    filename_variations = [
        f"{material_name.lower().replace(' ', '-').replace('_', '-')}-laser-cleaning.md",  # dashes
        f"{material_name.lower()}-laser-cleaning.md",  # preserve spaces as spaces  
        f"{material_name}-laser-cleaning.md"  # preserve original case and spaces
    ]
    
    print(f"🔍 Debugging frontmatter loading for: {material_name}")
    print(f"📝 Filename variations to try: {filename_variations}")
    
    frontmatter_path = None
    for filename in filename_variations:
        potential_path = Path(__file__).parents[1] / "content" / "components" / "frontmatter" / filename
        print(f"  Trying: {potential_path}")
        print(f"  Exists: {potential_path.exists()}")
        if potential_path.exists():
            frontmatter_path = potential_path
            print(f"  ✅ Found frontmatter at: {frontmatter_path}")
            break
    
    if frontmatter_path and frontmatter_path.exists():
        try:
            with open(frontmatter_path, 'r') as f:
                content = f.read()
                print(f"📄 File content length: {len(content)}")
                print(f"📄 Starts with ---: {content.startswith('---')}")
                
                # Extract YAML frontmatter
                if content.startswith('---'):
                    # Handle both cases: with and without closing ---
                    yaml_end = content.find('---', 3)
                    if yaml_end != -1:
                        # Traditional frontmatter with closing ---
                        yaml_content = content[3:yaml_end].strip()
                        print(f"📄 Found closing ---, using traditional format")
                    else:
                        # Pure YAML file without closing --- (our current format)
                        yaml_content = content[4:].strip()  # Skip opening ---\n
                        print(f"📄 No closing ---, using pure YAML format")
                    
                    print(f"📄 YAML content length: {len(yaml_content)}")
                    
                    data = yaml.safe_load(yaml_content)
                    print(f"✅ Successfully loaded frontmatter data")
                    print(f"📊 Keys found: {list(data.keys())[:10]}")
                    print(f"🏗️  Surface roughness before: {data.get('surface_roughness_before', 'NOT FOUND')}")
                    print(f"🏗️  Surface roughness after: {data.get('surface_roughness_after', 'NOT FOUND')}")
                    return data
                else:
                    print(f"❌ File doesn't start with ---")
                    return {}
        except Exception as e:
            print(f"❌ Error loading frontmatter: {e}")
            return {}
    else:
        print(f"❌ No frontmatter file found")
        return {}

if __name__ == "__main__":
    result = debug_frontmatter_loading("aluminum")
    print(f"\n📊 Final result: {bool(result)} (found {len(result)} keys)")
