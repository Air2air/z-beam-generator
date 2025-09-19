#!/usr/bin/env python3
"""
Batch Caption Generation Script

Generates caption components for all materials using the updated 
fail-fast caption component with frontmatter integration.
"""

import subprocess
import yaml
import time
from pathlib import Path

def load_materials():
    """Load all materials from the materials database"""
    materials_file = Path("data/materials.yaml")
    if not materials_file.exists():
        raise FileNotFoundError("Materials database not found")
    
    with open(materials_file, 'r') as f:
        data = yaml.safe_load(f)
    
    material_index = data.get('material_index', {})
    return list(material_index.keys())

def generate_caption_for_material(material_name):
    """Generate caption for a single material"""
    try:
        result = subprocess.run(
            ['python3', 'run.py', '--material', material_name, '--components', 'caption'],
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout per material
        )
        
        if result.returncode == 0:
            return True, "Success"
        else:
            return False, result.stderr.strip()
            
    except subprocess.TimeoutExpired:
        return False, "Timeout after 60 seconds"
    except Exception as e:
        return False, str(e)

def main():
    """Generate captions for all materials"""
    print("🚀 BATCH CAPTION GENERATION - ALL MATERIALS")
    print("=" * 50)
    print("")
    
    # Load materials
    try:
        materials = load_materials()
        print(f"📋 Found {len(materials)} materials to process")
        print("")
    except Exception as e:
        print(f"❌ Error loading materials: {e}")
        return 1
    
    # Track progress
    successful = []
    failed = []
    start_time = time.time()
    
    # Process each material
    for i, material in enumerate(materials, 1):
        print(f"📄 Processing {i}/{len(materials)}: {material}")
        
        success, message = generate_caption_for_material(material)
        
        if success:
            successful.append(material)
            print("   ✅ Success")
        else:
            failed.append((material, message))
            print(f"   ❌ Failed: {message}")
        
        # Progress indicator every 10 materials
        if i % 10 == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            estimated_remaining = (len(materials) - i) / rate if rate > 0 else 0
            print(f"   📊 Progress: {i}/{len(materials)} ({i/len(materials)*100:.1f}%) - "
                  f"Rate: {rate:.1f}/min - ETA: {estimated_remaining/60:.1f}min")
        
        print("")
    
    # Final summary
    elapsed = time.time() - start_time
    print("🎯 BATCH GENERATION COMPLETE")
    print("=" * 50)
    print(f"✅ Successful: {len(successful)}/{len(materials)}")
    print(f"❌ Failed: {len(failed)}/{len(materials)}")
    print(f"⏱️  Total time: {elapsed/60:.1f} minutes")
    print(f"📊 Success rate: {len(successful)/len(materials)*100:.1f}%")
    
    if failed:
        print("\n❌ Failed materials:")
        for material, error in failed:
            print(f"   • {material}: {error}")
    
    return 0 if len(failed) == 0 else 1

if __name__ == "__main__":
    exit(main())
