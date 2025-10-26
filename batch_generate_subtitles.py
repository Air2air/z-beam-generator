#!/usr/bin/env python3
"""
Batch Subtitle Generation Script
Generates subtitles for all materials with progress tracking and error handling
"""

import yaml
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def load_materials():
    """Load list of materials from Materials.yaml"""
    with open('data/Materials.yaml', 'r') as f:
        data = yaml.safe_load(f)
    return list(data['materials'].keys())

def generate_subtitle(material, timeout=45):
    """Generate subtitle for a single material"""
    try:
        result = subprocess.run(
            ['python3', 'run.py', '--subtitle', material],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stderr if result.returncode != 0 else None
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

def main():
    materials = load_materials()
    total = len(materials)
    
    print('=' * 80)
    print('🚀 SUBTITLE BATCH GENERATION - ALL MATERIALS')
    print('=' * 80)
    print(f'📊 Total materials: {total}')
    print(f'⏱️  Estimated time: ~{total * 4 / 60:.1f} minutes')
    print()
    
    success_count = 0
    error_count = 0
    errors = []
    
    start_time = datetime.now()
    
    for i, material in enumerate(materials, 1):
        success, error_msg = generate_subtitle(material)
        
        if success:
            success_count += 1
            status = '✅'
        else:
            error_count += 1
            status = '❌'
            errors.append((material, error_msg[:200] if error_msg else 'Unknown error'))
        
        # Progress every 10 materials
        if i % 10 == 0 or i == total:
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = i / elapsed if elapsed > 0 else 0
            remaining = (total - i) / rate if rate > 0 else 0
            print(f'{status} [{i:3d}/{total}] {material:40s} | ✅ {success_count:3d} ❌ {error_count:3d} | ETA: {remaining:4.0f}s')
    
    elapsed_time = (datetime.now() - start_time).total_seconds()
    
    print()
    print('=' * 80)
    print('📊 BATCH GENERATION COMPLETE')
    print('=' * 80)
    print(f'✅ Success: {success_count}/{total} materials ({100*success_count/total:.1f}%)')
    print(f'❌ Errors: {error_count}/{total} materials ({100*error_count/total:.1f}%)')
    print(f'⏱️  Total time: {elapsed_time:.1f}s ({elapsed_time/60:.1f} minutes)')
    print(f'⚡ Average: {elapsed_time/total:.1f}s per material')
    print()
    
    if errors:
        print('FIRST 20 ERRORS:')
        for material, error in errors[:20]:
            print(f'  ❌ {material}: {error}')
        if len(errors) > 20:
            print(f'  ... and {len(errors) - 20} more errors')
        print()
    
    print('=' * 80)
    
    return 0 if error_count == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
