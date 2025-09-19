#!/usr/bin/env python3
"""
Generate frontmatter for all materials in the database

This script iterates through all materials and generates frontmatter files.
"""

import yaml
import subprocess
import sys
import time
from pathlib import Path

def load_all_materials():
    """Load all materials from the materials database"""
    with open('data/materials.yaml', 'r') as f:
        data = yaml.safe_load(f)
    
    materials = []
    material_index = data.get('material_index', {})
    
    # Get all material names from the index
    for material_name in sorted(material_index.keys()):
        materials.append(material_name)
    
    return materials

def generate_frontmatter_for_material(material_name):
    """Generate frontmatter for a specific material"""
    print(f"🚀 Generating frontmatter for: {material_name}")
    
    try:
        # Run the generation command
        result = subprocess.run([
            'python3', 'run.py', 
            '--material', material_name, 
            '--components', 'frontmatter'
        ], capture_output=True, text=True, timeout=180)  # 3 minute timeout
        
        if result.returncode == 0:
            print(f"✅ {material_name} - Success")
            return True
        else:
            print(f"❌ {material_name} - Failed")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {material_name} - Timeout (3 minutes)")
        return False
    except Exception as e:
        print(f"❌ {material_name} - Exception: {e}")
        return False

def main():
    """Main function to generate all frontmatter files"""
    print("🔍 Loading materials database...")
    
    try:
        materials = load_all_materials()
        print(f"📊 Found {len(materials)} materials to process")
        
        # Create counters
        successful = 0
        failed = 0
        start_time = time.time()
        
        print("\n🏭 Starting frontmatter generation for all materials...")
        print("=" * 60)
        
        for i, material in enumerate(materials, 1):
            print(f"\n[{i:3d}/{len(materials)}] Processing {material}...")
            
            if generate_frontmatter_for_material(material):
                successful += 1
            else:
                failed += 1
            
            # Add small delay to avoid overwhelming the API
            time.sleep(2)
            
            # Progress update every 10 materials
            if i % 10 == 0:
                elapsed = time.time() - start_time
                avg_time = elapsed / i
                estimated_remaining = (len(materials) - i) * avg_time
                print(f"\n📊 Progress: {i}/{len(materials)} ({i/len(materials)*100:.1f}%)")
                print(f"⏱️  Estimated time remaining: {estimated_remaining/60:.1f} minutes")
        
        # Final summary
        total_time = time.time() - start_time
        print("\n" + "=" * 60)
        print("🎉 FRONTMATTER GENERATION COMPLETE!")
        print("=" * 60)
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total: {len(materials)}")
        print(f"📈 Success rate: {successful/len(materials)*100:.1f}%")
        print(f"⏱️  Total time: {total_time/60:.1f} minutes")
        print(f"⚡ Average time per material: {total_time/len(materials):.1f} seconds")
        
        # Check results
        frontmatter_dir = Path("content/components/frontmatter")
        generated_files = list(frontmatter_dir.glob("*-laser-cleaning.md"))
        print(f"📁 Generated files found: {len(generated_files)}")
        
        return successful > 0
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Z-Beam Frontmatter Generator - Generate All Materials")
    print("=" * 60)
    
    success = main()
    sys.exit(0 if success else 1)
