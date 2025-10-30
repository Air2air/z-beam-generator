#!/usr/bin/env python3
"""
Resume Batch Caption Generator
Generates captions only for materials that don't have them yet.
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
    
    # Find materials without captions
    all_materials = list(data['materials'].keys())
    pending_materials = []
    
    for mat_name in all_materials:
        mat = data['materials'][mat_name]
        caption = mat.get('caption', {})
        if not (caption.get('beforeText') and caption.get('afterText')):
            pending_materials.append(mat_name)
    
    total_materials = len(all_materials)
    completed_count = total_materials - len(pending_materials)
    
    print('=' * 80)
    print('🔄 RESUME BATCH CAPTION GENERATION')
    print('=' * 80)
    print(f'Total materials: {total_materials}')
    print(f'Already completed: {completed_count}')
    print(f'Pending: {len(pending_materials)}')
    print(f'Mode: OVERWRITE existing captions')
    print(f'Technical Intensity: Level 4 (Technical)')
    print(f'Voice Intensity: Level 2 (Light)')
    print(f'Timeout: 120 seconds per material')
    print('=' * 80)
    print()
    
    if not pending_materials:
        print('✅ All materials already have captions!')
        return 0
    
    start_time = time.time()
    successful = 0
    failed = 0
    failed_materials = []
    
    for i, material in enumerate(pending_materials, 1):
        mat_start = time.time()
        
        # Progress indicator
        progress_bar = '█' * (i * 40 // len(pending_materials))
        progress_pct = i * 100 / len(pending_materials)
        
        print(f'[{i:3d}/{len(pending_materials)}] [{progress_bar:<40}] {progress_pct:5.1f}% | {material:<25}', end=' ')
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
        
        # Progress summary every 5 materials for small batches
        if i % 5 == 0 and i < len(pending_materials):
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            remaining_items = len(pending_materials) - i
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
    print(f'Materials processed: {len(pending_materials)}')
    print(f'Successful: {successful} ({successful/len(pending_materials)*100:.1f}%)')
    print(f'Failed: {failed} ({failed/len(pending_materials)*100:.1f}%)')
    print(f'Total time: {total_time/60:.1f} minutes')
    print(f'Average per material: {total_time/len(pending_materials):.1f} seconds')
    print()
    print(f'OVERALL: {completed_count + successful}/{total_materials} materials have captions')
    print('=' * 80)
    
    if failed_materials:
        print()
        print('❌ Failed materials:')
        for mat in failed_materials:
            print(f'  - {mat}')
        print()
        print('Error details saved to: caption_generation_errors.log')
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('\n\n⚠️  Generation interrupted by user')
        sys.exit(130)
    except Exception as e:
        print(f'\n\n❌ Fatal error: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
