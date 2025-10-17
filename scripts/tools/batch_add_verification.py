#!/usr/bin/env python3
"""
Batch Add Prompt Chain Verification Metadata

Regenerates all frontmatter files to add prompt_chain_verification metadata.
Phase 6.1 completion script.
"""

import sys
import subprocess
import yaml
from pathlib import Path
from typing import List, Dict

def get_materials_needing_verification() -> List[str]:
    """Get list of materials without prompt_chain_verification."""
    frontmatter_dir = Path("content/components/frontmatter")
    materials_needing_update = []
    
    for yaml_file in sorted(frontmatter_dir.glob("*.yaml")):
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
            
            # Check if prompt_chain_verification exists
            if 'prompt_chain_verification' not in data:
                # Extract material name from filename
                material_name = yaml_file.stem.replace('-laser-cleaning', '').replace('-', ' ').title()
                materials_needing_update.append(material_name)
        except Exception as e:
            print(f"⚠️  Error reading {yaml_file.name}: {e}")
            continue
    
    return materials_needing_update

def regenerate_material(material_name: str) -> bool:
    """Regenerate frontmatter for a single material."""
    try:
        print(f"🔄 Regenerating: {material_name}...", end=" ", flush=True)
        
        result = subprocess.run(
            ['python3', 'run.py', '--material', material_name, '--components', 'frontmatter'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✅")
            return True
        else:
            print(f"❌ (exit code: {result.returncode})")
            if "Missing essential properties" in result.stderr or "Missing essential properties" in result.stdout:
                print(f"   ⚠️  Missing essential properties (expected for some materials)")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main batch regeneration process."""
    print("=" * 70)
    print("🔍 PHASE 6.1: Batch Add Prompt Chain Verification")
    print("=" * 70)
    print()
    
    # Get materials needing update
    materials = get_materials_needing_verification()
    
    if not materials:
        print("✅ All materials already have prompt_chain_verification metadata!")
        return 0
    
    print(f"📊 Found {len(materials)} materials needing verification metadata")
    print()
    
    # Ask for confirmation
    response = input(f"Proceed with regenerating {len(materials)} files? (y/N): ")
    if response.lower() != 'y':
        print("❌ Aborted by user")
        return 1
    
    print()
    print("🚀 Starting batch regeneration...")
    print("-" * 70)
    
    # Track results
    successful = []
    failed = []
    
    # Regenerate each material
    for i, material in enumerate(materials, 1):
        print(f"[{i}/{len(materials)}] ", end="")
        if regenerate_material(material):
            successful.append(material)
        else:
            failed.append(material)
    
    # Summary
    print()
    print("=" * 70)
    print("📊 BATCH REGENERATION SUMMARY")
    print("=" * 70)
    print(f"✅ Successful: {len(successful)}/{len(materials)}")
    print(f"❌ Failed: {len(failed)}/{len(materials)}")
    
    if failed:
        print()
        print("❌ Failed materials:")
        for material in failed[:10]:  # Show first 10
            print(f"   - {material}")
        if len(failed) > 10:
            print(f"   ... and {len(failed) - 10} more")
    
    # Verify prompt_chain_verification was added
    print()
    print("🔍 Verifying prompt_chain_verification was added...")
    remaining = get_materials_needing_verification()
    
    print(f"📊 Materials still needing verification: {len(remaining)}")
    print(f"✅ Materials with verification: {124 - len(remaining)}/124")
    
    if len(remaining) == 0:
        print()
        print("🎉 SUCCESS! All materials now have prompt_chain_verification metadata!")
        return 0
    else:
        print()
        print(f"⚠️  {len(remaining)} materials still need attention")
        return 1

if __name__ == '__main__':
    sys.exit(main())
