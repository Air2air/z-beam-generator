#!/usr/bin/env python3
"""
Batch Caption Generation for All Materials

Generates micros for all 132 materials with progress tracking.
"""

import sys
import subprocess
import time
import yaml
from pathlib import Path

# Unbuffered output
sys.stdout = open(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = open(sys.stderr.fileno(), 'w', buffering=1)

print("🚀 BATCH CAPTION GENERATION - ALL MATERIALS")
print("=" * 80)
print()

# Load all materials
materials_file = Path("data/materials/Materials.yaml")
with open(materials_file, 'r') as f:
    data = yaml.safe_load(f)
    materials = sorted(data['materials'].keys())

print(f"📋 Generating micros for {len(materials)} materials")
print()

results = {
    'success': [],
    'failed': [],
    'skipped': []
}
start_time = time.time()

for i, material in enumerate(materials, 1):
    print("=" * 80)
    print(f"🔄 MATERIAL {i}/{len(materials)}: {material}")
    print("=" * 80)
    
    # Force regeneration - skip the check
    # if 'micro' in data['materials'][material]:
    #     print("⏭️  Caption already exists, skipping...")
    #     results['skipped'].append(material)
    #     print()
    #     continue
    
    test_start = time.time()
    
    # Run caption generation using new API
    cmd = ["python3", "run.py", "--backfill", "--domain", "materials", "--generator", "caption", "--item", material]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=False,  # Real-time output
            text=True,
            timeout=300  # 5 minute timeout per material
        )
        
        duration = time.time() - test_start
        
        if result.returncode == 0:
            print(f"✅ SUCCESS in {duration:.1f}s")
            results['success'].append(material)
        else:
            print(f"❌ FAILED (exit code: {result.returncode})")
            results['failed'].append(material)
    
    except subprocess.TimeoutExpired:
        print(f"⏱️  TIMEOUT after 300s")
        results['failed'].append(material)
    
    except Exception as e:
        print(f"💥 ERROR: {e}")
        results['failed'].append(material)
    
    print()

# Final summary
total_time = time.time() - start_time
print()
print("=" * 80)
print("📊 BATCH GENERATION COMPLETE")
print("=" * 80)
print(f"⏱️  Total time: {total_time/60:.1f} minutes")
print(f"✅ Success: {len(results['success'])}")
print(f"⏭️  Skipped: {len(results['skipped'])}")
print(f"❌ Failed: {len(results['failed'])}")
print()

if results['failed']:
    print("Failed materials:")
    for mat in results['failed']:
        print(f"  - {mat}")
    print()

print(f"📈 Success rate: {len(results['success'])/(len(materials))*100 if len(materials) > 0 else 0:.1f}%")
