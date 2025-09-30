#!/usr/bin/env python3
"""
Batch Tags Generation Script
Generates tags for all materials that have frontmatter data.
"""

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

def run_tags_generation(material):
    """Run tags generation for a specific material"""
    try:
        cmd = [
            "python3", "run.py", 
            "--material", material, 
            "--components", "tags"
        ]
        
        # Get timeout from centralized configuration
        # Get timeout from centralized configuration - FAIL FAST
        from run import get_batch_timeout
        timeout = get_batch_timeout("tags_generation")
        
        result = subprocess.run(
            cmd, 
            cwd=project_root,
            capture_output=True, 
            text=True, 
            timeout=timeout
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
    print("🚀 Starting batch tags generation for all materials...")
    
    # Get all materials with frontmatter
    materials = get_materials_with_frontmatter()
    print(f"📋 Found {len(materials)} materials with frontmatter data")
    
    # Check which materials already have tags
    tags_dir = project_root / "content" / "components" / "tags"
    existing_tags = set()
    if tags_dir.exists():
        for file in tags_dir.glob("*-laser-cleaning.md"):
            material_name = file.stem.replace("-laser-cleaning", "")
            material_name = " ".join(word.capitalize() for word in material_name.split("-"))
            existing_tags.add(material_name)
    
    print(f"📁 {len(existing_tags)} materials already have tags")
    
    # Filter to only process materials without tags
    materials_to_process = [m for m in materials if m not in existing_tags]
    print(f"🎯 Processing {len(materials_to_process)} new materials")
    
    if not materials_to_process:
        print("✨ All materials already have tags generated!")
        return
    
    # Process materials in batches
    successful = 0
    failed = 0
    start_time = time.time()
    
    for i, material in enumerate(materials_to_process, 1):
        print(f"\n[{i}/{len(materials_to_process)}] Processing: {material}")
        
        if run_tags_generation(material):
            successful += 1
        else:
            failed += 1
        
        # Small delay to avoid overwhelming the API
        if i < len(materials_to_process):
            time.sleep(1)
    
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
