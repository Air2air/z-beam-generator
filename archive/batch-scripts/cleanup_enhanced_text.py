#!/usr/bin/env python3
"""Clean up 'ENHANCED TEXT' debug artifacts from Materials.yaml and frontmatter files."""

import yaml
import re
from pathlib import Path


def clean_text(text):
    """Remove ENHANCED TEXT prefix and clean up formatting."""
    if not isinstance(text, str):
        return text
    
    # Remove "ENHANCED TEXT (incorporating your...)" prefix
    text = re.sub(
        r'^ENHANCED TEXT\s*\(incorporating your [^)]+\)\s*:?\s*\n?\s*',
        '',
        text,
        flags=re.IGNORECASE | re.MULTILINE
    )
    
    # Remove leading slashes
    text = re.sub(r'^\s*/+\s*', '', text, flags=re.MULTILINE)
    
    # Normalize excessive line breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def clean_materials_yaml():
    """Clean Materials.yaml file."""
    materials_path = Path('data/Materials.yaml')
    
    print(f"📖 Loading {materials_path}...")
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    cleaned_count = 0
    
    # Clean FAQ answers
    for material_name, material_data in data.get('materials', {}).items():
        if 'faq' in material_data:
            for faq_item in material_data['faq']:
                if 'answer' in faq_item:
                    original = faq_item['answer']
                    cleaned = clean_text(original)
                    if cleaned != original:
                        faq_item['answer'] = cleaned
                        cleaned_count += 1
        
        # Clean caption fields
        if 'caption' in material_data:
            for field in ['before', 'after']:
                if field in material_data['caption']:
                    original = material_data['caption'][field]
                    cleaned = clean_text(original)
                    if cleaned != original:
                        material_data['caption'][field] = cleaned
                        cleaned_count += 1
    
    if cleaned_count > 0:
        print(f"✅ Cleaned {cleaned_count} fields in Materials.yaml")
        print(f"💾 Saving {materials_path}...")
        with open(materials_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print("✅ Materials.yaml saved")
    else:
        print("✨ Materials.yaml is already clean")
    
    return cleaned_count > 0


def clean_frontmatter_files():
    """Clean all frontmatter YAML files."""
    frontmatter_dir = Path('content/frontmatter')
    
    if not frontmatter_dir.exists():
        print(f"⚠️  {frontmatter_dir} doesn't exist")
        return False
    
    yaml_files = list(frontmatter_dir.glob('*.yaml'))
    print(f"\n📂 Found {len(yaml_files)} frontmatter files")
    
    total_cleaned = 0
    
    for yaml_file in yaml_files:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        cleaned_count = 0
        
        # Clean FAQ questions
        if 'faq' in data and 'questions' in data['faq']:
            for faq_item in data['faq']['questions']:
                if 'answer' in faq_item:
                    original = faq_item['answer']
                    cleaned = clean_text(original)
                    if cleaned != original:
                        faq_item['answer'] = cleaned
                        cleaned_count += 1
        
        # Clean caption fields
        if 'caption' in data:
            for field in ['before', 'after']:
                if field in data['caption']:
                    original = data['caption'][field]
                    cleaned = clean_text(original)
                    if cleaned != original:
                        data['caption'][field] = cleaned
                        cleaned_count += 1
        
        if cleaned_count > 0:
            print(f"   ✅ {yaml_file.name}: cleaned {cleaned_count} fields")
            with open(yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            total_cleaned += 1
    
    if total_cleaned > 0:
        print(f"\n✅ Cleaned {total_cleaned} frontmatter files")
    else:
        print("\n✨ All frontmatter files are already clean")
    
    return total_cleaned > 0


if __name__ == '__main__':
    print("="*80)
    print("🧹 CLEANING ENHANCED TEXT DEBUG ARTIFACTS")
    print("="*80)
    
    materials_changed = clean_materials_yaml()
    frontmatter_changed = clean_frontmatter_files()
    
    print("\n" + "="*80)
    if materials_changed or frontmatter_changed:
        print("✅ CLEANUP COMPLETE")
    else:
        print("✨ NO CHANGES NEEDED - ALL FILES CLEAN")
    print("="*80)
