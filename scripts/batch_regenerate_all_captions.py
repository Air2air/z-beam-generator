#!/usr/bin/env python3
"""
Batch regeneration script for all caption files using enhanced YAML v2.0 format
Regenerates all 109 materials with standardized parameters and comprehensive metadata
"""

import sys
import subprocess
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def get_all_materials():
    """Get all material names from frontmatter files"""
    frontmatter_dir = PROJECT_ROOT / "content" / "components" / "frontmatter"
    materials = []
    
    for file_path in frontmatter_dir.glob("*-laser-cleaning.md"):
        # Extract material name (remove -laser-cleaning.md suffix)
        material_name = file_path.stem.replace("-laser-cleaning", "")
        # Convert to title case for the run command
        material_display = material_name.replace("-", " ").title()
        materials.append(material_display)
    
    return sorted(materials)

def regenerate_caption(material_name, index, total):
    """Regenerate caption for a single material"""
    print(f"🔄 [{index:3d}/{total}] Regenerating: {material_name}")
    
    try:
        # Run the caption generation
        cmd = [
            "python3", 
            str(PROJECT_ROOT / "run.py"),
            "--material", material_name,
            "--components", "caption"
        ]
        
        # Get timeout from centralized configuration
        try:
            from run import get_batch_timeout
            timeout = get_batch_timeout("caption_generation")
        except ImportError:
            timeout = 60  # Fallback if run.py not available
        
        result = subprocess.run(
            cmd, 
            cwd=PROJECT_ROOT,
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        
        if result.returncode == 0:
            print(f"✅ [{index:3d}/{total}] SUCCESS: {material_name}")
            return True
        else:
            print(f"❌ [{index:3d}/{total}] FAILED: {material_name}")
            print(f"   Error: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ [{index:3d}/{total}] TIMEOUT: {material_name}")
        return False
    except Exception as e:
        print(f"💥 [{index:3d}/{total}] EXCEPTION: {material_name} - {str(e)}")
        return False

def main():
    """Main batch regeneration function"""
    print("🚀 BATCH CAPTION REGENERATION - ENHANCED YAML v2.0")
    print("=" * 60)
    print("📋 Features:")
    print("   • Standardized 1000x magnification")
    print("   • Standardized 200 μm field of view") 
    print("   • Material-specific contamination from frontmatter")
    print("   • Real laser parameters from materials data")
    print("   • Comprehensive YAML v2.0 format (~5KB per file)")
    print("   • Category-specific authors and expertise")
    print("=" * 60)
    
    # Get all materials
    materials = get_all_materials()
    total_materials = len(materials)
    
    print(f"📊 Found {total_materials} materials to regenerate")
    print("")
    
    # Track progress
    success_count = 0
    failed_materials = []
    start_time = time.time()
    
    # Regenerate each material
    for index, material in enumerate(materials, 1):
        if regenerate_caption(material, index, total_materials):
            success_count += 1
        else:
            failed_materials.append(material)
        
        # Add small delay to avoid overwhelming the system
        time.sleep(0.5)
    
    # Final summary
    elapsed_time = time.time() - start_time
    print("")
    print("=" * 60)
    print("📊 BATCH REGENERATION COMPLETE")
    print("=" * 60)
    print(f"✅ Successfully regenerated: {success_count}/{total_materials} files")
    print(f"⏱️  Total time: {elapsed_time:.1f} seconds")
    print(f"📈 Average time per file: {elapsed_time/total_materials:.1f} seconds")
    
    if failed_materials:
        print(f"❌ Failed materials ({len(failed_materials)}):")
        for material in failed_materials:
            print(f"   • {material}")
    
    print("")
    print("🎯 Enhanced features applied to all files:")
    print("   • YAML v2.0 comprehensive format")
    print("   • Standardized microscopy parameters")
    print("   • Material-specific contamination analysis")
    print("   • Real laser parameters and technical data")
    print("   • SEO-optimized metadata and keywords")
    print("   • Accessibility information")
    print("   • Quality metrics and performance data")

if __name__ == "__main__":
    main()
