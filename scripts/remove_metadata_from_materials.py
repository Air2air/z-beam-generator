#!/usr/bin/env python3
"""
Remove metadata fields from Materials.yaml to match template structure exactly.

Removes:
- From caption: word_count, character_count, generated, generation_method, author, total_words, word_count_before, word_count_after
- From faq items: word_count

Keeps only template-defined fields:
- caption: {before, after}
- faq: [{question, answer}]
"""

import yaml
from pathlib import Path
from datetime import datetime

# Load Materials.yaml
materials_path = Path('materials/data/Materials.yaml')
print(f"Loading {materials_path}...")

with open(materials_path, 'r') as f:
    data = yaml.safe_load(f)

materials_dict = data.get('materials', {})
print(f"Found {len(materials_dict)} materials")

# Create backup
backup_path = materials_path.parent / f'materials_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml'
with open(backup_path, 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
print(f"✅ Backup created: {backup_path}")

# Track changes
caption_metadata_removed = 0
faq_metadata_removed = 0
caption_metadata_types = set()
faq_metadata_types = set()

# Clean metadata from all materials
for name, material_data in materials_dict.items():
    # Clean caption metadata
    if 'caption' in material_data and isinstance(material_data['caption'], dict):
        caption = material_data['caption']
        metadata_fields = [
            'word_count', 'character_count', 'generated', 'generation_method', 
            'author', 'total_words', 'word_count_before', 'word_count_after'
        ]
        
        removed = []
        for field in metadata_fields:
            if field in caption:
                removed.append(field)
                caption_metadata_types.add(field)
                del caption[field]
        
        if removed:
            caption_metadata_removed += 1
            
        # Keep only before and after
        material_data['caption'] = {
            'before': caption.get('before', ''),
            'after': caption.get('after', '')
        }
    
    # Clean FAQ metadata
    if 'faq' in material_data and isinstance(material_data['faq'], list):
        for faq_item in material_data['faq']:
            if isinstance(faq_item, dict) and 'word_count' in faq_item:
                faq_metadata_types.add('word_count')
                del faq_item['word_count']
                faq_metadata_removed += 1

# Save cleaned data
with open(materials_path, 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

print(f"\n✅ Metadata Removal Complete:")
print(f"   - Caption metadata removed from {caption_metadata_removed} materials")
print(f"   - Caption metadata types: {sorted(caption_metadata_types)}")
print(f"   - FAQ metadata items removed: {faq_metadata_removed}")
print(f"   - FAQ metadata types: {sorted(faq_metadata_types)}")
print(f"\n✅ Saved: {materials_path}")
print(f"✅ Backup: {backup_path}")
