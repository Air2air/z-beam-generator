#!/usr/bin/env python3
"""Batch generate captions for all materials"""

import yaml
import subprocess
import time
from datetime import datetime

# Load Materials.yaml to get all material names
with open('data/Materials.yaml', 'r') as f:
    materials_data = yaml.safe_load(f)

all_materials = list(materials_data['materials'].keys())
total = len(all_materials)

print('=' * 80)
print('🚀 BATCH CAPTION GENERATION - ALL MATERIALS')
print('=' * 80)
print(f'Starting: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print(f'Total materials: {total}')
print('=' * 80)
print()

start_time = time.time()
success_count = 0
error_count = 0
skipped_count = 0
errors = []

for i, material in enumerate(all_materials, 1):
    print(f'[{i}/{total}] Processing: {material}...')
    
    # REGENERATE ALL - Skip check disabled to replace existing captions
    
    try:
        result = subprocess.run(
            ['python3', 'run.py', '--caption', material],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f'  ✅ Success')
            success_count += 1
        else:
            print(f'  ❌ Error: {result.stderr[:100]}')
            error_count += 1
            errors.append((material, result.stderr[:200]))
    except subprocess.TimeoutExpired:
        print(f'  ⏱️  Timeout')
        error_count += 1
        errors.append((material, 'Timeout after 30s'))
    except Exception as e:
        print(f'  ❌ Exception: {str(e)[:100]}')
        error_count += 1
        errors.append((material, str(e)[:200]))
    
    # Small delay to avoid rate limiting
    if i % 10 == 0 and i < total:
        print(f'  💤 Brief pause after batch...')
        time.sleep(2)

elapsed = time.time() - start_time

print()
print('=' * 80)
print('📊 BATCH GENERATION COMPLETE')
print('=' * 80)
print(f'Finished: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print(f'Elapsed time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)')
print()
print('Results:')
print(f'  ✅ Success: {success_count}')
print(f'  ⏭️  Skipped: {skipped_count}')
print(f'  ❌ Errors: {error_count}')
print(f'  📊 Total: {total}')
print()

if errors:
    print('❌ ERRORS ENCOUNTERED:')
    for material, error in errors[:5]:  # Show first 5 errors
        print(f'  - {material}: {error}')
    if len(errors) > 5:
        print(f'  ... and {len(errors) - 5} more')
    print()

print(f'Average time per material: {elapsed/total:.1f}s')
print('=' * 80)
