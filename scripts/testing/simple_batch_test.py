#!/usr/bin/env python3
"""
Simple Batch Caption Test
==========================
Generates micros for 4 materials (one per author) and produces a report.

This is a simplified version that WILL complete successfully.
"""

import subprocess
import sys
import time
import yaml
from pathlib import Path
from datetime import datetime

# Test materials - one per author
TEST_MATERIALS = {
    'Bamboo': 1,      # Author 1
    'Limestone': 2,   # Author 2  
    'Marble': 3,      # Author 3
    'Oak': 4          # Author 4
}

def run_caption_generation(material_name):
    """Run caption generation for a single material."""
    cmd = ['python3', 'run.py', '--micro', material_name]
    
    print(f'\n{"="*70}')
    print(f'🚀 Generating caption for: {material_name}')
    print(f'{"="*70}')
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=Path(__file__).parent.parent
        )
        
        elapsed = time.time() - start_time
        success = result.returncode == 0
        
        # Extract key metrics from output
        output = result.stdout + result.stderr
        winston_score = None
        realism_score = None
        combined_score = None
        
        for line in output.split('\n'):
            if 'Human Score:' in line and '%' in line:
                try:
                    parts = line.split('Human Score:')[1].split('%')[0].strip()
                    winston_score = float(parts)
                except:
                    pass
            elif 'Realism passed:' in line:
                try:
                    parts = line.split('Realism passed:')[1].split('/')[0].strip()
                    realism_score = float(parts)
                except:
                    pass
            elif 'Combined Score:' in line:
                try:
                    parts = line.split('Combined Score:')[1].split('/')[0].strip()
                    combined_score = float(parts)
                except:
                    pass
        
        return {
            'material': material_name,
            'success': success,
            'elapsed_seconds': round(elapsed, 1),
            'winston_score': winston_score,
            'realism_score': realism_score,
            'combined_score': combined_score,
            'exit_code': result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            'material': material_name,
            'success': False,
            'elapsed_seconds': 120.0,
            'error': 'Timeout after 120 seconds',
            'exit_code': -1
        }
    except Exception as e:
        return {
            'material': material_name,
            'success': False,
            'error': str(e),
            'exit_code': -1
        }


def main():
    """Run batch test for 4 materials."""
    print('=' * 70)
    print('📊 SIMPLE BATCH CAPTION TEST')
    print('=' * 70)
    print(f'Testing {len(TEST_MATERIALS)} materials (one per author)')
    print(f'Started: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()
    
    results = []
    start_time = time.time()
    
    for material_name, author_id in TEST_MATERIALS.items():
        print(f'\n[{len(results)+1}/{len(TEST_MATERIALS)}] Author {author_id}: {material_name}')
        result = run_caption_generation(material_name)
        results.append(result)
        
        # Print immediate result
        if result['success']:
            print(f'   ✅ SUCCESS in {result["elapsed_seconds"]}s')
            if result.get('winston_score'):
                print(f'   📊 Winston: {result["winston_score"]}%')
            if result.get('realism_score'):
                print(f'   📊 Realism: {result["realism_score"]}/10')
            if result.get('combined_score'):
                print(f'   📊 Combined: {result["combined_score"]}/10')
        else:
            print(f'   ❌ FAILED: {result.get("error", "Unknown error")}')
    
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
        
        print(f'\n{i}. {status} {material} ({elapsed}s)')
        
        if result['success']:
            if result.get('winston_score'):
                print(f'   Winston: {result["winston_score"]}%')
            if result.get('realism_score'):
                print(f'   Realism: {result["realism_score"]}/10')
            if result.get('combined_score'):
                print(f'   Combined: {result["combined_score"]}/10')
        else:
            print(f'   Error: {result.get("error", "Unknown error")}')
    
    # Save report
    report_file = Path('SIMPLE_BATCH_TEST_REPORT.md')
    with open(report_file, 'w') as f:
        f.write(f'# Simple Batch Caption Test Report\n\n')
        f.write(f'**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
        f.write(f'## Summary\n\n')
        f.write(f'- **Total Materials**: {len(results)}\n')
        f.write(f'- **Successes**: {successes} ({successes/len(results)*100:.1f}%)\n')
        f.write(f'- **Failures**: {failures} ({failures/len(results)*100:.1f}%)\n')
        f.write(f'- **Total Time**: {total_elapsed:.1f}s\n')
        f.write(f'- **Average Time**: {total_elapsed/len(results):.1f}s per material\n\n')
        f.write(f'## Results\n\n')
        
        for i, result in enumerate(results, 1):
            status = '✅ SUCCESS' if result['success'] else '❌ FAILED'
            f.write(f'### {i}. {result["material"]} - {status}\n\n')
            f.write(f'- **Time**: {result.get("elapsed_seconds", 0)}s\n')
            
            if result['success']:
                if result.get('winston_score'):
                    f.write(f'- **Winston Score**: {result["winston_score"]}%\n')
                if result.get('realism_score'):
                    f.write(f'- **Realism Score**: {result["realism_score"]}/10\n')
                if result.get('combined_score'):
                    f.write(f'- **Combined Score**: {result["combined_score"]}/10\n')
            else:
                f.write(f'- **Error**: {result.get("error", "Unknown error")}\n')
            
            f.write('\n')
    
    print(f'\n📄 Report saved: {report_file}')
    print('=' * 70)
    
    return 0 if successes == len(results) else 1


if __name__ == '__main__':
    sys.exit(main())
