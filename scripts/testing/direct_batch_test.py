#!/usr/bin/env python3
"""
Direct Batch Caption Test - NO SUBPROCESS
==========================================
Tests caption generation by calling the generator directly (no subprocess).
This avoids subprocess signal handling issues.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test materials - one per author
TEST_MATERIALS = {
    'Bamboo': 1,      # Author 1
    'Limestone': 2,   # Author 2  
    'Marble': 3,      # Author 3
    'Oak': 4          # Author 4
}


def run_caption_generation_direct(material_name):
    """Generate caption by calling the handler directly (no subprocess)."""
    print(f'\n{"="*70}')
    print(f'🚀 Generating caption for: {material_name}')
    print(f'{"="*70}\n')
    
    start_time = time.time()
    
    try:
        # Import and call directly (no subprocess)
        from shared.commands.generation import handle_caption_generation
        
        success = handle_caption_generation(material_name)
        elapsed = time.time() - start_time
        
        return {
            'material': material_name,
            'success': success,
            'elapsed_seconds': round(elapsed, 1)
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            'material': material_name,
            'success': False,
            'elapsed_seconds': round(elapsed, 1),
            'error': str(e)
        }


def main():
    """Run batch test for 4 materials."""
    print('=' * 70)
    print('📊 DIRECT BATCH CAPTION TEST (No Subprocess)')
    print('=' * 70)
    print(f'Testing {len(TEST_MATERIALS)} materials (one per author)')
    print(f'Started: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()
    
    results = []
    start_time = time.time()
    
    for material_name, author_id in TEST_MATERIALS.items():
        print(f'\n[{len(results)+1}/{len(TEST_MATERIALS)}] Author {author_id}: {material_name}')
        result = run_caption_generation_direct(material_name)
        results.append(result)
        
        # Print immediate result
        if result['success']:
            print(f'\n✅ SUCCESS in {result["elapsed_seconds"]}s')
        else:
            error_msg = result.get('error', 'Unknown error')
            print(f'\n❌ FAILED in {result["elapsed_seconds"]}s')
            print(f'   Error: {error_msg}')
    
    total_elapsed = time.time() - start_time
    
    # Generate report
    print('\n' + '=' * 70)
    print('📊 BATCH TEST RESULTS')
    print('=' * 70)
    
    successes = sum(1 for r in results if r['success'])
    failures = len(results) - successes
    
    print(f'\n✅ Successes: {successes}/{len(results)} ({successes/len(results)*100:.1f}%)')
    print(f'❌ Failures: {failures}/{len(results)} ({failures/len(results)*100:.1f}%)')
    print(f'⏱️  Total time: {total_elapsed:.1f}s')
    print(f'⏱️  Average per material: {total_elapsed/len(results):.1f}s')
    
    print('\n📋 DETAILED RESULTS:')
    print('-' * 70)
    
    for i, result in enumerate(results, 1):
        status = '✅' if result['success'] else '❌'
        material = result['material']
        elapsed = result.get('elapsed_seconds', 0)
        
        print(f'{i}. {status} {material} ({elapsed}s)')
        
        if not result['success'] and 'error' in result:
            print(f'   Error: {result["error"]}')
    
    # Save report
    report_file = Path('DIRECT_BATCH_TEST_REPORT.md')
    with open(report_file, 'w') as f:
        f.write('# Direct Batch Caption Test Report\n\n')
        f.write(f'**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write(f'**Method**: Direct function calls (no subprocess)\n\n')
        f.write('## Summary\n\n')
        f.write(f'- **Total Materials**: {len(results)}\n')
        f.write(f'- **Successes**: {successes} ({successes/len(results)*100:.1f}%)\n')
        f.write(f'- **Failures**: {failures} ({failures/len(results)*100:.1f}%)\n')
        f.write(f'- **Total Time**: {total_elapsed:.1f}s\n')
        f.write(f'- **Average Time**: {total_elapsed/len(results):.1f}s per material\n\n')
        f.write('## Results\n\n')
        
        for i, result in enumerate(results, 1):
            status = '✅ SUCCESS' if result['success'] else '❌ FAILED'
            f.write(f'### {i}. {result["material"]} - {status}\n\n')
            f.write(f'- **Time**: {result.get("elapsed_seconds", 0)}s\n')
            
            if not result['success'] and 'error' in result:
                f.write(f'- **Error**: {result["error"]}\n')
            
            f.write('\n')
    
    print(f'\n📄 Report saved: {report_file}')
    print('=' * 70)
    
    return 0 if successes == len(results) else 1


if __name__ == '__main__':
    sys.exit(main())
