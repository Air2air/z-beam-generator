#!/usr/bin/env python3
"""
Enhanced Frontmatter Regeneration

Uses the consolidated frontmatter generator to create complete, validation-ready
frontmatter files with automatic triple format fields.
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

def generate_frontmatter(material_name: str) -> bool:
    """Generate frontmatter for a single material"""
    try:
        cmd = [sys.executable, "run.py", "--material", material_name, "--components", "frontmatter"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"⏱️ Timeout: {material_name}")
        return False
    except Exception:
        return False

def main():
    """Generate frontmatter for key materials"""
    print("🚀 ENHANCED FRONTMATTER REGENERATION")
    print("=" * 50)
    
    # Start with key materials from different categories
    key_materials = [
        "Aluminum", "Steel", "Copper", "Titanium",  # Metals
        "Stainless Steel", "Brass", "Bronze",      # More metals
        "Glass", "Quartz Glass", "Pyrex",          # Glass
        "Concrete", "Granite", "Marble",           # Stone/masonry
        "Oak", "Pine", "Bamboo"                    # Wood
    ]
    
    print(f"📋 Generating {len(key_materials)} key materials with enhanced generator")
    print("🎯 Each will include: triple format, technical specs, validation-ready structure")
    print()
    
    successful = 0
    failed = 0
    start_time = time.time()
    
    for i, material in enumerate(key_materials, 1):
        print(f"[{i:2d}/{len(key_materials)}] {material:<20}", end=" ")
        
        if generate_frontmatter(material):
            successful += 1
            print("✅")
        else:
            failed += 1 
            print("❌")
    
    elapsed = time.time() - start_time
    print("\n" + "=" * 50)
    print("🎉 ENHANCED REGENERATION COMPLETE")
    print(f"✅ Successful: {successful}/{len(key_materials)} ({successful/len(key_materials)*100:.1f}%)")
    print(f"❌ Failed: {failed}/{len(key_materials)} ({failed/len(key_materials)*100:.1f}%)")
    print(f"⏱️ Total time: {elapsed/60:.1f} minutes")
    print(f"📈 Average: {elapsed/len(key_materials):.1f} seconds per material")
    
    # Test validation on generated files
    print("\n🔍 TESTING VALIDATION...")
    validation_passed = 0
    
    for material in key_materials[:5]:  # Test first 5
        material_slug = material.lower().replace(" ", "-")
        cmd = [sys.executable, "scripts/tools/frontmatter_data_validation.py", material_slug]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                validation_passed += 1
                print(f"✅ {material}")
            else:
                print(f"❌ {material}")
        except:
            print(f"⚠️ {material} (validation error)")
    
    print(f"\n📊 Validation Results: {validation_passed}/5 materials passed")
    
    if successful > 0:
        print(f"\n🎊 Generated {successful} materials with enhanced consolidated generator!")
        print("🔧 Each includes: numeric fields, unit fields, technical specs, validation-ready structure")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
