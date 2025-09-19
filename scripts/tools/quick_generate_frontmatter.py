#!/usr/bin/env python3
"""
Generate Frontmatter for First 10 Materials

Quick test to generate frontmatter for the first 10 materials to check patterns.
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
        cmd = [
            sys.executable, "run.py", 
            "--material", material_name, 
            "--components", "frontmatter"
        ]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=120
        )
        
        if result.returncode == 0:
            return True
        else:
            print(f"❌ Failed: {result.stderr.split('/')[-1] if result.stderr else 'Unknown error'}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏱️ Timeout")
        return False
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

def main():
    """Generate frontmatter for first 10 materials"""
    print("🚀 QUICK FRONTMATTER GENERATION - First 10 Materials")
    print("=" * 60)
    
    materials = load_materials()
    material_names = list(materials.keys())[:10]  # First 10 only
    
    print(f"📋 Processing {len(material_names)} materials")
    print()
    
    successful = 0
    failed = 0
    start_time = time.time()
    
    for i, material_name in enumerate(material_names, 1):
        print(f"[{i:2d}/10] {material_name:<25}", end=" ")
        
        if run_frontmatter_generation(material_name):
            successful += 1
            print("✅")
        else:
            failed += 1
    
    elapsed = time.time() - start_time
    print(f"\n✅ Successful: {successful}/10")
    print(f"❌ Failed: {failed}/10") 
    print(f"⏱️ Time: {elapsed:.1f}s")
    
    if successful > 0:
        print(f"\n📁 Generated files:")
        subprocess.run(["ls", "-la", "content/components/frontmatter/*-laser-cleaning.md"], shell=True)

if __name__ == "__main__":
    main()
