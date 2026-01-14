#!/usr/bin/env python3
import yaml
from collections import Counter

with open('data/materials/Materials.yaml', 'r') as f:
    data = yaml.safe_load(f)

materials = data.get('materials', {})

# Find all fields ending in _description
description_fields = set()
for mat_data in materials.values():
    if isinstance(mat_data, dict):
        for key in mat_data.keys():
            if key.endswith('_description'):
                description_fields.add(key)

print(f'📊 Found {len(description_fields)} description fields:')
for field in sorted(description_fields):
    print(f'   - {field}')

# Analyze each description field
for field in sorted(description_fields):
    descriptions = []
    for mat_id, mat_data in materials.items():
        if isinstance(mat_data, dict) and field in mat_data:
            desc = mat_data[field]
            if desc:
                descriptions.append({
                    'material': mat_id,
                    'description': str(desc)
                })
    
    if descriptions:
        desc_texts = [d['description'] for d in descriptions]
        unique_descs = set(desc_texts)
        variation_pct = len(unique_descs) / len(descriptions) * 100
        
        print(f'\n🔍 {field.upper()}:')
        print(f'   Materials with field: {len(descriptions)}/153')
        print(f'   Unique descriptions: {len(unique_descs)}/{len(descriptions)} ({variation_pct:.1f}%)')
        
        if variation_pct < 50:
            print(f'   🚨 LOW VARIATION WARNING (<50%)')
        
        # Find duplicates
        desc_counter = Counter(desc_texts)
        duplicates = [(desc, count) for desc, count in desc_counter.items() if count > 1]
        
        if duplicates:
            print(f'   ⚠️  {len(duplicates)} duplicated descriptions')
            for desc, count in sorted(duplicates, key=lambda x: x[1], reverse=True)[:3]:
                desc_preview = desc[:70] + '...' if len(desc) > 70 else desc
                print(f'      {count}x: {desc_preview}')
