#!/usr/bin/env python3
"""
Generate author components for all materials with frontmatter data
"""

import os
import subprocess
import glob

def main():
    # Get all frontmatter files
    frontmatter_dir = "frontmatter/materials"
    frontmatter_files = glob.glob(f"{frontmatter_dir}/*-laser-cleaning.md")
    
    # Extract material names (convert kebab-case to Title Case for run.py)
    materials = []
    for file_path in frontmatter_files:
        filename = os.path.basename(file_path)
        # Remove '-laser-cleaning.md' suffix to get material name in kebab-case
        material_kebab = filename.replace('-laser-cleaning.md', '')
        # Convert kebab-case to Title Case for run.py command
        material_name = material_kebab.replace('-', ' ').title()
        materials.append(material_name)
    
    print(f"🚀 Found {len(materials)} materials with frontmatter data")
    print("📋 Generating author components for all materials...")
    
    success_count = 0
    error_count = 0
    
    for material in materials:
        try:
            print(f"\n📝 Generating author for: {material}")
            
            # Run the generation command
            cmd = ["python3", "run.py", "--material", material, "--components", "author"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0:
                print(f"✅ Success: {material}")
                success_count += 1
            else:
                print(f"❌ Failed: {material}")
                print(f"   Error: {result.stderr.strip()}")
                error_count += 1
                
        except Exception as e:
            print(f"❌ Exception for {material}: {e}")
            error_count += 1
    
    print(f"\n🎉 Generation complete!")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {error_count}")
    print(f"📊 Total: {len(materials)}")

if __name__ == "__main__":
    main()
