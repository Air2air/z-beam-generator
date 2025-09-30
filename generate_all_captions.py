#!/usr/bin/env python3
"""
Generate captions for all materials in the Materials.yaml database.
This script processes all materials systematically with progress tracking.
"""

import sys
import time
import yaml
from datetime import datetime

# Add project root to path
sys.path.insert(0, '.')

from run import main as run_main

def load_materials_list():
    """Load all materials from Materials.yaml"""
    try:
        with open('data/Materials.yaml', 'r') as f:
            materials_data = yaml.safe_load(f)
        
        material_index = materials_data.get('material_index', {})
        return list(material_index.keys()), material_index
    except Exception as e:
        print(f"❌ Error loading materials: {e}")
        return [], {}

def generate_captions_for_all_materials():
    """Generate captions for all materials with progress tracking"""
    
    print("🚀 Z-Beam Caption Generator - Batch Processing")
    print("=" * 60)
    
    # Load materials
    materials_list, material_index = load_materials_list()
    if not materials_list:
        print("❌ No materials found. Exiting.")
        return
    
    total_materials = len(materials_list)
    print(f"📊 Found {total_materials} materials to process")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    successful = 0
    failed = 0
    failed_materials = []
    
    # Sort materials for consistent processing
    sorted_materials = sorted(materials_list)
    
    for i, material in enumerate(sorted_materials, 1):
        category = material_index[material]
        
        print(f"\n📝 Processing {i:3d}/{total_materials}: {material} ({category})")
        print("-" * 50)
        
        try:
            # Generate caption using the main run function
            start_time = time.time()
            
            # Simulate calling: python3 run.py --material "material_name" --components caption
            sys.argv = ['run.py', '--material', material, '--components', 'caption']
            
            # Call the main function
            run_main()
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"✅ Success! Generated in {duration:.1f}s")
            successful += 1
            
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
            failed += 1
            failed_materials.append(material)
            
            # Continue with next material instead of stopping
            continue
        
        # Progress summary every 10 materials
        if i % 10 == 0:
            print(f"\n📊 Progress Update: {i}/{total_materials} processed")
            print(f"   ✅ Successful: {successful}")
            print(f"   ❌ Failed: {failed}")
            remaining = total_materials - i
            if successful > 0:
                avg_time = (time.time() - start_time) / i
                eta_minutes = (remaining * avg_time) / 60
                print(f"   🕐 ETA: ~{eta_minutes:.1f} minutes")
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 BATCH CAPTION GENERATION COMPLETE")
    print("=" * 60)
    print(f"📊 Total materials processed: {total_materials}")
    print(f"✅ Successful generations: {successful}")
    print(f"❌ Failed generations: {failed}")
    print(f"📈 Success rate: {(successful/total_materials)*100:.1f}%")
    print(f"🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if failed_materials:
        print(f"\n❌ Failed materials ({len(failed_materials)}):")
        for material in failed_materials:
            print(f"   - {material}")
    
    print("\n🚀 All caption generation completed!")

if __name__ == "__main__":
    generate_captions_for_all_materials()