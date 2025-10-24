#!/usr/bin/env python3
"""Test auto-remediation across multiple materials"""

import subprocess
import sys
import yaml

# Test materials across different categories
test_materials = [
    ("Cast Iron", "metal"),
    ("Aluminum", "metal"),
    ("Tool Steel", "metal"),
    ("Polypropylene", "plastic"),
    ("Nylon 6", "plastic"),
    ("Carbon Fiber Reinforced Polymer", "composite"),
]

results = {
    'passed': [],
    'failed': [],
    'null_counts': {}
}

for material_name, category in test_materials:
    print(f"\n{'='*60}")
    print(f"Testing: {material_name} ({category})")
    print('='*60)
    
    # Run generation
    cmd = ['python3', 'run.py', '--material', material_name]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Check if frontmatter was generated
    frontmatter_file = f"content/components/frontmatter/{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml"
    
    try:
        with open(frontmatter_file, 'r') as f:
            data = yaml.safe_load(f)
        
        # Count nulls
        def count_nulls(obj, null_count_list):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if v is None and k in ('min', 'max'):
                        null_count_list.append(1)
                    else:
                        count_nulls(v, null_count_list)
            elif isinstance(obj, list):
                for item in obj:
                    count_nulls(item, null_count_list)
        
        null_count_list = []
        count_nulls(data, null_count_list)
        null_count = len(null_count_list)
        
        results['null_counts'][material_name] = null_count
        
        if '✅ frontmatter generated successfully' in result.stdout or '✅ frontmatter generated successfully' in result.stderr:
            results['passed'].append(material_name)
            print(f"✅ PASSED - {null_count} nulls remaining")
        else:
            results['failed'].append(material_name)
            print(f"❌ FAILED - Check output")
            
    except FileNotFoundError:
        results['failed'].append(material_name)
        print(f"❌ FAILED - Frontmatter file not found")
    except Exception as e:
        results['failed'].append(material_name)
        print(f"❌ FAILED - {str(e)}")

# Summary
print(f"\n{'='*60}")
print("TEST SUMMARY")
print('='*60)
print(f"✅ Passed: {len(results['passed'])}/{len(test_materials)}")
print(f"❌ Failed: {len(results['failed'])}/{len(test_materials)}")
print(f"\nNull counts:")
for mat, count in results['null_counts'].items():
    print(f"  {mat}: {count} nulls")

if results['failed']:
    print(f"\nFailed materials:")
    for mat in results['failed']:
        print(f"  - {mat}")
    sys.exit(1)
else:
    print(f"\n🎉 All materials passed!")
    sys.exit(0)
