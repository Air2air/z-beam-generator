#!/usr/bin/env python3
"""
Research properties for 3 ceramic materials with auto-sync to frontmatter.
This script combines property research with immediate frontmatter synchronization.
"""

import sys
import yaml
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from generation.utils.frontmatter_sync import sync_field_to_frontmatter

def research_and_sync_properties():
    """Research properties and sync to frontmatter immediately."""
    
    materials = [
        "Boron Nitride",
        "Titanium Nitride", 
        "Yttria-Stabilized Zirconia"
    ]
    
    print("=" * 80)
    print("🔬 PROPERTY RESEARCH WITH FRONTMATTER SYNC")
    print("=" * 80)
    print(f"\n📋 Materials: {len(materials)}")
    for mat in materials:
        print(f"   • {mat}")
    print()
    
    # Step 1: Run property research
    print("🔬 Step 1: Running property research...")
    print("-" * 80)
    
    import subprocess
    materials_arg = ",".join(materials)
    cmd = [
        "python3", "run.py",
        "--research-missing-properties",
        "--research-materials", materials_arg,
        "--skip-integrity-check"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, capture_output=False, text=True)
    
    if result.returncode != 0:
        print(f"\n❌ Property research failed with code {result.returncode}")
        return False
    
    print("\n✅ Property research complete")
    
    # Step 2: Sync properties to frontmatter
    print("\n🔄 Step 2: Syncing properties to frontmatter...")
    print("-" * 80)
    
    # Load Materials.yaml to get the researched properties
    with open('data/materials/Materials.yaml', 'r') as f:
        data = yaml.safe_load(f)
    
    sync_count = 0
    for material_name in materials:
        if material_name not in data['materials']:
            print(f"⚠️  {material_name}: Not found in Materials.yaml")
            continue
            
        mat_data = data['materials'][material_name]
        props = mat_data.get('properties', {})
        
        if not props:
            print(f"⚠️  {material_name}: No properties to sync")
            continue
        
        print(f"\n📝 {material_name}:")
        print(f"   Properties: {len(props)}")
        
        # Sync properties field to frontmatter
        try:
            sync_field_to_frontmatter(material_name, 'properties', props)
            print(f"   ✅ Synced to frontmatter")
            sync_count += 1
        except Exception as e:
            print(f"   ❌ Sync failed: {e}")
    
    print()
    print("=" * 80)
    print(f"✅ COMPLETE: {sync_count}/{len(materials)} materials synced to frontmatter")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = research_and_sync_properties()
    sys.exit(0 if success else 1)
