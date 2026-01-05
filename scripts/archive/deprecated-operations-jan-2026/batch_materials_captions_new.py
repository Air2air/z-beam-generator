#!/usr/bin/env python3
"""
Batch Caption Generation for All Materials - Updated API

Generates captions (micros) for all materials through the processing pipeline.
"""

import sys
import time
import yaml
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.api.client_factory import APIClientFactory
from generation.field_router import FieldRouter
import yaml

# Unbuffered output
sys.stdout = open(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = open(sys.stderr.fileno(), 'w', buffering=1)

print("🚀 BATCH CAPTION GENERATION - ALL MATERIALS")
print("=" * 80)
print()

# Load all materials directly from YAML
materials_file = Path("data/materials/Materials.yaml")
with open(materials_file, 'r') as f:
    data = yaml.safe_load(f)
    materials = sorted(data['materials'].keys())

print(f"📋 Generating captions for {len(materials)} materials")
print(f"🔄 Using QualityEvaluatedGenerator pipeline")
print()

# Create API client
api_client = APIClientFactory.create_client(provider='grok')

results = {
    'success': [],
    'failed': [],
    'skipped': []
}
start_time = time.time()

for i, material_id in enumerate(materials, 1):
    print("=" * 80)
    print(f"🔄 MATERIAL {i}/{len(materials)}: {material_id}")
    print("=" * 80)
    
    test_start = time.time()
    
    try:
        # Generate micro (caption) through pipeline
        result = FieldRouter.generate_field(
            domain='materials',
            field='micro',
            item_name=material_id,
            api_client=api_client,
            dry_run=False
        )
        
        duration = time.time() - test_start
        
        if result['success']:
            print(f"\n✅ SUCCESS in {duration:.1f}s")
            print(f"📝 Generated: {len(result.get('content', ''))} characters")
            results['success'].append(material_id)
        else:
            error_msg = result.get('error', 'Unknown error')
            print(f"\n❌ FAILED: {error_msg}")
            results['failed'].append(material_id)
    
    except Exception as e:
        duration = time.time() - test_start
        print(f"\n💥 ERROR after {duration:.1f}s: {e}")
        results['failed'].append(material_id)
    
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

total = len(materials)
success_rate = (len(results['success'])/total*100) if total > 0 else 0
print(f"📈 Success rate: {success_rate:.1f}%")
