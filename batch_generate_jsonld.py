#!/usr/bin/env python3
"""
Generate JSON-LD component for all materials in efficient batches.

This script processes materials in smaller batches with progress tracking
and handles timeouts gracefully.
"""

import subprocess
import sys
import time
from pathlib import Path

def get_all_materials():
    """Get list of all materials from frontmatter directory."""
    frontmatter_dir = Path("frontmatter/materials")
    materials = []
    
    for file in frontmatter_dir.glob("*-laser-cleaning.md"):
        material_name = file.stem.replace("-laser-cleaning", "")
        materials.append(material_name)
    
    materials.sort()
    return materials

def get_existing_jsonld_materials():
    """Get list of materials that already have JSON-LD files."""
    jsonld_dir = Path("content/components/jsonld")
    existing = set()
    
    if jsonld_dir.exists():
        for file in jsonld_dir.glob("*-laser-cleaning.yaml"):
            material_name = file.stem.replace("-laser-cleaning", "")
            existing.add(material_name)
    
    return existing

def generate_jsonld_for_material(material_name):
    """Generate JSON-LD for a specific material with timeout handling."""
    try:
        print(f"  🔧 Processing: {material_name}")
        
        cmd = ["python3", "run.py", "--material", material_name, "--components", "jsonld"]
        
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=90  # 90 second timeout per material
        )
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"  ✅ Success: {material_name} ({duration:.1f}s)")
            return True
        else:
            print(f"  ❌ Error: {material_name}")
            if result.stderr:
                print(f"     Error: {result.stderr[:100]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  ⏰ Timeout: {material_name} (90s limit exceeded)")
        return False
    except Exception as e:
        print(f"  💥 Exception: {material_name} - {e}")
        return False

def main():
    """Main execution function."""
    print("🎯 JSON-LD Batch Generator")
    print("=" * 40)
    
    # Get materials
    all_materials = get_all_materials()
    existing_materials = get_existing_jsonld_materials()
    
    # Find materials that need JSON-LD generation
    remaining_materials = [m for m in all_materials if m not in existing_materials]
    
    print(f"📊 Total materials: {len(all_materials)}")
    print(f"✅ Already have JSON-LD: {len(existing_materials)}")
    print(f"🔄 Need to generate: {len(remaining_materials)}")
    
    if not remaining_materials:
        print("🎉 All materials already have JSON-LD files!")
        return True
    
    print("\n📝 Existing materials with JSON-LD:")
    for material in sorted(existing_materials):
        print(f"  ✅ {material}")
    
    print(f"\n🚀 Starting generation for {len(remaining_materials)} materials...")
    print("=" * 40)
    
    successful = 0
    failed = 0
    batch_size = 5  # Process in smaller batches
    
    for i in range(0, len(remaining_materials), batch_size):
        batch = remaining_materials[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(remaining_materials) + batch_size - 1) // batch_size
        
        print(f"\n📦 Batch {batch_num}/{total_batches} ({len(batch)} materials)")
        
        for j, material in enumerate(batch, 1):
            overall_progress = i + j
            print(f"[{overall_progress}/{len(remaining_materials)}] Batch {batch_num}.{j}")
            
            if generate_jsonld_for_material(material):
                successful += 1
            else:
                failed += 1
            
            # Small delay between materials
            time.sleep(1)
        
        # Status update after each batch
        print(f"  📊 Batch {batch_num} complete: {successful} success, {failed} failed")
        
        # Brief pause between batches
        if i + batch_size < len(remaining_materials):
            print("  ⏸️  Brief pause before next batch...")
            time.sleep(3)
    
    print("\n" + "=" * 40)
    print("🏁 JSON-LD Generation Complete!")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Total processed: {len(remaining_materials)}")
    
    # Final verification
    final_existing = get_existing_jsonld_materials()
    print(f"📊 Total JSON-LD files now: {len(final_existing)}")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
