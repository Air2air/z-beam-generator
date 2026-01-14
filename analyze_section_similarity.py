#!/usr/bin/env python3
"""
Analyze section descriptions for duplication and similarity patterns.
"""
import yaml
from pathlib import Path
from collections import Counter
import difflib

# Load Materials.yaml
with open('data/materials/Materials.yaml', 'r') as f:
    data = yaml.safe_load(f)

materials = data.get('materials', {})

# Extract section descriptions
section_descriptions = {}
section_types = set()

for mat_id, mat_data in materials.items():
    if isinstance(mat_data, dict):
        for key, value in mat_data.items():
            if isinstance(value, dict) and '_section' in value:
                section = value['_section']
                if isinstance(section, dict) and 'description' in section:
                    section_type = key
                    section_types.add(section_type)
                    if section_type not in section_descriptions:
                        section_descriptions[section_type] = []
                    section_descriptions[section_type].append({
                        'material': mat_id,
                        'description': section['description']
                    })

print(f'📊 Found {len(section_types)} section types with descriptions:\n')

# Analyze each section type
for section_type in sorted(section_types):
    descs = section_descriptions[section_type]
    print(f'\n🔍 {section_type.upper()} ({len(descs)} materials)')
    print('=' * 70)
    
    # Get unique descriptions
    desc_texts = [d['description'] for d in descs]
    unique_descs = set(desc_texts)
    
    print(f'   Unique descriptions: {len(unique_descs)}/{len(descs)} ({len(unique_descs)/len(descs)*100:.1f}%)')
    
    # Find duplicates
    desc_counter = Counter(desc_texts)
    duplicates = [(desc, count) for desc, count in desc_counter.items() if count > 1]
    
    if duplicates:
        print(f'\n   ⚠️  DUPLICATES FOUND:')
        for desc, count in sorted(duplicates, key=lambda x: x[1], reverse=True)[:5]:
            desc_preview = desc[:80] + '...' if len(desc) > 80 else desc
            print(f'      {count}x: {desc_preview}')
            materials_with_desc = [d['material'] for d in descs if d['description'] == desc]
            print(f'          Materials: {", ".join(materials_with_desc[:5])}')
    
    # Check similarity between descriptions
    if len(unique_descs) > 1:
        similarities = []
        desc_list = list(unique_descs)
        for i in range(min(10, len(desc_list))):
            for j in range(i+1, min(10, len(desc_list))):
                ratio = difflib.SequenceMatcher(None, desc_list[i], desc_list[j]).ratio()
                if ratio > 0.7:
                    similarities.append((ratio, desc_list[i], desc_list[j]))
        
        if similarities:
            print(f'\n   ⚠️  HIGH SIMILARITY (>70%):')
            for ratio, desc1, desc2 in sorted(similarities, reverse=True)[:3]:
                print(f'      {ratio*100:.1f}% similar:')
                print(f'        A: {desc1[:80]}...')
                print(f'        B: {desc2[:80]}...')
