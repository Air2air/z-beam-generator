#!/usr/bin/env python3
"""
Batch Generate All Frontmatter Files

Uses the existing run.py system to regenerate all 109 frontmatter files
with progress tracking and validation.
"""

import subprocess
import sys
import time
import yaml
from pathlib import Path

def load_materials():
    """Load all materials from materials.yaml"""
    materials_file = Path(__file__).parent.parent.parent / "data" / "materials.yaml"
    with open(materials_file, 'r') as f:
        data = yaml.safe_load(f)
    return data.get('material_index', {})

def run_frontmatter_generation(material_name: str) -> bool:
    """Generate frontmatter for a single material using run.py"""
    try:
        # Use the existing run.py system
        cmd = [
            sys.executable, "run.py", 
            "--material", material_name, 
            "--components", "frontmatter"
        ]
        
        # Get timeout from centralized configuration
        # Get timeout from centralized configuration - FAIL FAST
        from run import get_batch_timeout
        timeout = get_batch_timeout("frontmatter_generation")
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        
        if result.returncode == 0:
            return True
        else:
            print(f"❌ Failed to generate {material_name}: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏱️ Timeout generating {material_name}")
        return False
    except Exception as e:
        print(f"💥 Error generating {material_name}: {e}")
        return False

def main():
    """Generate frontmatter for all materials"""
    print("🚀 BATCH FRONTMATTER GENERATION")
    print("=" * 50)
    
    # Load materials
    materials = load_materials()
    material_names = list(materials.keys())
    total_count = len(material_names)
    
    print(f"📋 Found {total_count} materials to process")
    print(f"🎯 Target: Generate all frontmatter files")
    print()
    
    # Track progress
    successful = 0
    failed = 0
    start_time = time.time()
    
    for i, material_name in enumerate(material_names, 1):
        print(f"[{i:3d}/{total_count}] Processing {material_name}...", end=" ")
        
        if run_frontmatter_generation(material_name):
            successful += 1
            print("✅")
        else:
            failed += 1
            print("❌")
        
        # Progress update every 10 materials
        if i % 10 == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed
            remaining = (total_count - i) / rate if rate > 0 else 0
            print(f"   📊 Progress: {i}/{total_count} ({i/total_count*100:.1f}%) - ETA: {remaining/60:.1f}m")
    
    # Final summary
    elapsed = time.time() - start_time
    print("\n" + "=" * 50)
    print("🎉 BATCH GENERATION COMPLETE")
    print(f"✅ Successful: {successful}/{total_count} ({successful/total_count*100:.1f}%)")
    print(f"❌ Failed: {failed}/{total_count} ({failed/total_count*100:.1f}%)")
    print(f"⏱️ Total time: {elapsed/60:.1f} minutes")
    print(f"📈 Average: {elapsed/total_count:.1f} seconds per material")
    
    if failed > 0:
        print(f"\n⚠️ {failed} materials failed - check errors above")
        return 1
    else:
        print("\n🎊 All frontmatter files generated successfully!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
