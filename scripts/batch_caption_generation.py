#!/usr/bin/env python3
"""
Batch Caption Generation Script
Generates captions for all materials that have frontmatter data.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def get_materials_with_frontmatter():
    """Get list of materials that have frontmatter files"""
    frontmatter_dir = project_root / "content" / "components" / "frontmatter"
    materials = []
    
    if frontmatter_dir.exists():
        for file in frontmatter_dir.glob("*-laser-cleaning.md"):
            # Extract material name from filename
            material_name = file.stem.replace("-laser-cleaning", "")
            # Convert to proper case (capitalize each word)
            material_name = " ".join(word.capitalize() for word in material_name.split("-"))
            materials.append(material_name)
    
    return sorted(materials)

def run_caption_generation(material):
    """Run caption generation for a specific material"""
    try:
        cmd = [
            "python3", "run.py", 
            "--material", material, 
            "--components", "caption"
        ]
        
        result = subprocess.run(
            cmd, 
            cwd=project_root,
            capture_output=True, 
            text=True, 
            timeout=120  # 2 minute timeout per material
        )
        
        if result.returncode == 0:
            print(f"✅ {material}: Success")
            return True
        else:
            print(f"❌ {material}: Failed - {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {material}: Timeout (>2 minutes)")
        return False
    except Exception as e:
        print(f"❌ {material}: Error - {str(e)}")
        return False

def main():
    """Main batch processing function"""
    print("🚀 Starting batch caption generation for all materials...")
    
    # Get all materials with frontmatter
    materials = get_materials_with_frontmatter()
    print(f"📋 Found {len(materials)} materials with frontmatter data")
    
    # Check which materials already have captions
    caption_dir = project_root / "content" / "components" / "caption"
    existing_captions = set()
    if caption_dir.exists():
        for file in caption_dir.glob("*-laser-cleaning.yaml"):
            material_name = file.stem.replace("-laser-cleaning", "")
            material_name = " ".join(word.capitalize() for word in material_name.split("-"))
            existing_captions.add(material_name)
    
    print(f"📁 {len(existing_captions)} materials already have captions")
    
    # Filter to only process materials without captions (or process all since we cleared the directory)
    materials_to_process = materials  # Process all since we cleared the directory
    print(f"🎯 Processing {len(materials_to_process)} materials")
    
    # Process materials in batches
    successful = 0
    failed = 0
    start_time = time.time()
    
    for i, material in enumerate(materials_to_process, 1):
        print(f"\n[{i}/{len(materials_to_process)}] Processing: {material}")
        
        if run_caption_generation(material):
            successful += 1
        else:
            failed += 1
        
        # Small delay to avoid overwhelming the system (caption is static, but still good practice)
        if i < len(materials_to_process):
            time.sleep(0.5)  # Shorter delay since caption generation is static
    
    # Summary
    elapsed = time.time() - start_time
    print(f"\n" + "="*60)
    print(f"🎉 Batch processing complete!")
    print(f"⏱️  Total time: {elapsed:.1f} seconds")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success rate: {successful/(successful+failed)*100:.1f}%")
    
    if failed > 0:
        print(f"\n⚠️  {failed} materials failed. Check errors above.")

if __name__ == "__main__":
    main()
