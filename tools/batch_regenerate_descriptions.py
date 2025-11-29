#!/usr/bin/env python3
"""
Batch regenerate all material descriptions with the corrected word count logic.
Shows progress and tracks which materials have been completed.
"""

import yaml
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def get_materials():
    """Load all material names from Materials.yaml"""
    with open('data/materials/Materials.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return list(data['materials'].keys())

def has_description(material_name):
    """Check if material already has a description"""
    with open('data/materials/Materials.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    material = data['materials'].get(material_name, {})
    desc = material.get('description')
    return desc is not None and len(str(desc).strip()) > 0

def regenerate_material(material_name):
    """Regenerate description for one material"""
    try:
        result = subprocess.run(
            ['python3', 'run.py', '--description', material_name, '--skip-integrity-check'],
            capture_output=True,
            text=True,
            timeout=90
        )
        
        if result.returncode == 0:
            # Extract word count from output
            word_count = None
            for line in result.stdout.split('\n'):
                if 'Word count:' in line or 'word count:' in line:
                    word_count = line.strip()
                    break
            return True, word_count
        else:
            return False, f"Exit code {result.returncode}"
            
    except subprocess.TimeoutExpired:
        return False, "Timeout (90s)"
    except Exception as e:
        return False, str(e)

def main():
    materials = get_materials()
    total = len(materials)
    
    print(f"🚀 Batch Regeneration: {total} Material Descriptions")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    success_count = 0
    skip_count = 0
    fail_count = 0
    failed_materials = []
    
    for i, material in enumerate(materials, 1):
        print(f"\n[{i}/{total}] {material}")
        
        # Check if already has description
        if has_description(material):
            print(f"   ⏭️  Already has description, regenerating...")
        
        # Regenerate
        success, info = regenerate_material(material)
        
        if success:
            print(f"   ✅ {info if info else 'Success'}")
            success_count += 1
        else:
            print(f"   ❌ FAILED: {info}")
            fail_count += 1
            failed_materials.append((material, info))
        
        # Progress update every 10 materials
        if i % 10 == 0:
            elapsed = (datetime.now() - datetime.now()).total_seconds()
            remaining = total - i
            print(f"\n   📊 Progress: {i}/{total} ({i/total*100:.1f}%) | Success: {success_count} | Failed: {fail_count}")
    
    # Final report
    print("\n" + "=" * 80)
    print(f"📊 BATCH COMPLETE")
    print(f"   ⏰ Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   ✅ Success: {success_count}/{total} ({success_count/total*100:.1f}%)")
    print(f"   ❌ Failed: {fail_count}/{total}")
    
    if failed_materials:
        print(f"\n❌ Failed Materials ({len(failed_materials)}):")
        for mat, reason in failed_materials:
            print(f"   - {mat}: {reason}")

if __name__ == '__main__':
    main()
