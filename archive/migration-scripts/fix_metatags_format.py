#!/usr/bin/env python3
"""
Metatags Format Checker

Script to check and fix the format of metatags files.
"""

from pathlib import Path
import yaml

def check_metatags_file(file_path):
    """Check and fix the format of a metatags file"""
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Parse the content
    try:
        if content.startswith("---"):
            end_marker = content.find("---", 3)
            if end_marker != -1:
                yaml_content = content[3:end_marker].strip()
                data = yaml.safe_load(yaml_content)
                
                # Check for problematic title format
                if "title" in data and isinstance(data["title"], list):
                    print(f"Fixing title in {file_path}")
                    
                    # Get the material name from the filename
                    material_name = Path(file_path).stem.split("-laser-cleaning")[0].replace("-", " ").title()
                    
                    # Fix the title
                    data["title"] = f"{material_name} Laser Cleaning"
                    
                    # Fix Twitter title
                    for i, item in enumerate(data.get("twitter", [])):
                        if item.get("name") == "twitter:title" and isinstance(item.get("content"), list):
                            data["twitter"][i]["content"] = f"{material_name} Laser Cleaning - Precision Guide"
                    
                    # Fix OG title
                    for i, item in enumerate(data.get("opengraph", [])):
                        if item.get("property") == "og:title" and isinstance(item.get("content"), list):
                            data["opengraph"][i]["content"] = f"{material_name} Laser Cleaning - Technical Guide"
                    
                    # Write the fixed data back
                    yaml_content = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
                    new_content = f"---\n{yaml_content.strip()}\n---\n"
                    
                    # Preserve version information
                    if "# Version Information" in content:
                        version_start = content.find("# Version Information")
                        version_info = content[version_start:]
                        new_content += f"\n{version_info}"
                    
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    
                    print(f"✅ Fixed {file_path}")
                    return True
        
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to check all metatags files"""
    
    metatags_dir = Path("content/components/metatags")
    if not metatags_dir.exists():
        print(f"Metatags directory not found: {metatags_dir}")
        return
    
    files = list(metatags_dir.glob("*.md"))
    print(f"Found {len(files)} metatags files")
    
    fixed_count = 0
    for file_path in files:
        if check_metatags_file(file_path):
            fixed_count += 1
    
    print(f"Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
