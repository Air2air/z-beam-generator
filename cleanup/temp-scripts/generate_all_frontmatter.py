#!/usr/bin/env python3
"""
Batch Generate All Frontmatter - Sequential Processing

Generate frontmatter for all materials without interruption using the working run.py system.
"""

import subprocess
import sys
import time
import yaml
from pathlib import Path

def load_materials():
    """Load all materials from Materials.yaml"""
    materials_file = Path(__file__).parent / "data" / "Materials.yaml"
    with open(materials_file, 'r') as f:
        data = yaml.safe_load(f)
    return data.get('material_index', {})

def generate_frontmatter(material_name: str) -> bool:
    """Generate frontmatter for a single material"""
    try:
        cmd = [sys.executable, "run.py", "--material", material_name, "--components", "frontmatter"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 minute timeout
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout for {material_name}")
        return False
    except Exception as e:
        print(f"💥 Error for {material_name}: {e}")
        return False

def main():
    print("🚀 BATCH FRONTMATTER GENERATION - ALL MATERIALS")
    print("=" * 60)
    
    # Load materials
    materials = load_materials()
    material_names = sorted(materials.keys())
    total = len(material_names)
    
    print(f"📋 Found {total} materials to process")
    print("🎯 Target: Generate all frontmatter files without interruption")
    print()
    
    successful = 0
    failed = 0
    start_time = time.time()
    
    for i, material_name in enumerate(material_names, 1):
        print(f"[{i:3d}/{total}] Processing {material_name}...", end=" ")
        
        if generate_frontmatter(material_name):
            print("✅")
            successful += 1
        else:
            print("❌")
            failed += 1
        
        # Progress update every 10 materials
        if i % 10 == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed * 60  # per minute
            eta = (total - i) / rate if rate > 0 else 0
            print(f"   📊 Progress: {i}/{total} ({i/total*100:.1f}%) - Rate: {rate:.1f}/min - ETA: {eta:.1f}m")
    
    # Final summary
    total_time = time.time() - start_time
    print()
    print("=" * 60)
    print("🎉 BATCH GENERATION COMPLETE")
    print(f"✅ Successful: {successful}/{total} ({successful/total*100:.1f}%)")
    print(f"❌ Failed: {failed}/{total} ({failed/total*100:.1f}%)")
    print(f"⏱️ Total time: {total_time/60:.1f} minutes")
    print(f"📈 Average: {total_time/total:.1f} seconds per material")
    
    if failed > 0:
        print(f"\n⚠️ {failed} materials failed - check individual outputs for details")
    else:
        print("\n🎊 All materials generated successfully!")

if __name__ == "__main__":
    main()