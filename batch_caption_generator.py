#!/usr/bin/env python3
"""
Batch Caption Generator
Generates captions for all 132 materials with progress tracking.
Overwrites existing captions in frontmatter.
"""

import yaml
import subprocess
import time
import sys
from pathlib import Path

def main():
    # Load all materials
    materials_file = Path('data/Materials.yaml')
    with open(materials_file, 'r') as f:
        data = yaml.safe_load(f)
    
    materials = list(data['materials'].keys())
    total_materials = len(materials)
    
    print('=' * 80)
    print('🚀 BATCH CAPTION GENERATION - ALL MATERIALS')
    print('=' * 80)
    print(f'Total materials: {total_materials}')
    print(f'Mode: OVERWRITE existing captions')
    print(f'Technical Intensity: Level 4 (Technical)')
    print(f'Voice Intensity: Level 2 (Light)')
    print('=' * 80)
    print()
    
    start_time = time.time()
    successful = 0
    failed = 0
    failed_materials = []
    
    for i, material in enumerate(materials, 1):
        mat_start = time.time()
        
        # Progress indicator
        progress_bar = '█' * (i * 40 // total_materials)
        progress_pct = i * 100 / total_materials
        
        print(f'[{i:3d}/{total_materials}] [{progress_bar:<40}] {progress_pct:5.1f}% | {material:<25}', end=' ')
        sys.stdout.flush()
        
        # Run caption generation
        result = subprocess.run(
            ['python3', 'run.py', '--caption', material],
            capture_output=True,
            text=True,
            timeout=120  # 120 second timeout per material
        )
        
        mat_time = time.time() - mat_start
        
        if result.returncode == 0:
            print(f'✓ {mat_time:5.1f}s')
            successful += 1
        else:
            print(f'✗ {mat_time:5.1f}s FAILED')
            failed += 1
            failed_materials.append(material)
            # Log error to file
            with open('caption_generation_errors.log', 'a') as f:
                f.write(f'\n{"=" * 80}\n')
                f.write(f'Material: {material}\n')
                f.write(f'Time: {time.strftime("%Y-%m-%d %H:%M:%S")}\n')
                f.write(f'Error:\n{result.stderr}\n')
        
        # Progress summary every 10 materials
        if i % 10 == 0:
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            remaining_items = total_materials - i
            estimated_remaining = remaining_items * avg_time
            
            print()
            print(f'  ⏱️  Elapsed: {elapsed/60:6.1f} min | Remaining: {estimated_remaining/60:6.1f} min | Success: {successful}/{i}')
            print()
    
    # Final summary
    total_time = time.time() - start_time
    
    print()
    print('=' * 80)
    print('✅ BATCH GENERATION COMPLETE')
    print('=' * 80)
    print(f'Total materials: {total_materials}')
    print(f'Successful: {successful} ({successful/total_materials*100:.1f}%)')
    print(f'Failed: {failed} ({failed/total_materials*100:.1f}%)')
    print(f'Total time: {total_time/60:.1f} minutes')
    print(f'Average per material: {total_time/total_materials:.1f} seconds')
    print('=' * 80)
    
    if failed_materials:
        print()
        print('❌ Failed materials:')
        for mat in failed_materials:
            print(f'  - {mat}')
        print()
        print(f'Error details saved to: caption_generation_errors.log')
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('\n\n⚠️  Generation interrupted by user')
        sys.exit(130)
    except Exception as e:
        print(f'\n\n❌ Fatal error: {e}')
        sys.exit(1)
