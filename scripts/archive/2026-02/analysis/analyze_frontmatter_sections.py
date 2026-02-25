#!/usr/bin/env python3
"""
Analyze section descriptions in frontmatter for duplication and similarity patterns.
"""
import yaml
from pathlib import Path
from collections import Counter

frontmatter_dir = Path('/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/materials')

# Extract section descriptions from frontmatter files
section_descriptions = {}
materials_processed = 0

for yaml_file in sorted(frontmatter_dir.glob('*.yaml')):
    with open(yaml_file, 'r') as f:
        try:
            data = yaml.safe_load(f)
            if not data:
                continue
            
            materials_processed += 1
            mat_id = data.get('id', yaml_file.stem)
            
            # Check all keys for _section metadata
            for key, value in data.items():
                if isinstance(value, dict) and '_section' in value:
                    section = value['_section']
                    if isinstance(section, dict) and 'description' in section:
                        section_type = key
                        if section_type not in section_descriptions:
                            section_descriptions[section_type] = []
                        section_descriptions[section_type].append({
                            'material': mat_id,
                            'description': section['description']
                        })
        except Exception as e:
            print(f'Error reading {yaml_file.name}: {e}')
            continue

print(f'📊 Analyzed {materials_processed} materials')
print(f'📊 Found {len(section_descriptions)} section types with descriptions:\n')

# Analyze each section type
for section_type in sorted(section_descriptions.keys()):
    descs = section_descriptions[section_type]
    print(f'\n🔍 {section_type.upper()} ({len(descs)} materials)')
    print('=' * 70)
    
    # Get unique descriptions
    desc_texts = [d['description'] for d in descs]
    unique_descs = set(desc_texts)
    
    variation_pct = len(unique_descs)/len(descs)*100
    print(f'   Unique descriptions: {len(unique_descs)}/{len(descs)} ({variation_pct:.1f}%)')
    
    if variation_pct < 50:
        print(f'   🚨 LOW VARIATION WARNING (<50%)')
    
    # Find duplicates
    desc_counter = Counter(desc_texts)
    duplicates = [(desc, count) for desc, count in desc_counter.items() if count > 1]
    
    if duplicates:
        print(f'\n   ⚠️  DUPLICATES FOUND: {len(duplicates)} unique duplicated descriptions')
        for desc, count in sorted(duplicates, key=lambda x: x[1], reverse=True)[:5]:
            desc_preview = desc[:70] + '...' if len(desc) > 70 else desc
            print(f'      {count}x ({count/len(descs)*100:.1f}%): {desc_preview}')
            materials_with_desc = [d['material'] for d in descs if d['description'] == desc]
            mat_preview = ', '.join(materials_with_desc[:5])
            if len(materials_with_desc) > 5:
                mat_preview += '...'
            print(f'          Materials: {mat_preview}')
