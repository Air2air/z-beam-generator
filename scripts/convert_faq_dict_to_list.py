#!/usr/bin/env python3
"""
Convert FAQ dict format to list format in Materials.yaml.

Old format:
  faq:
    questions:
      - question: ...
        answer: ...
    generated: timestamp
    question_count: 5

New format:
  faq:
    - question: ...
      answer: ...
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any

def convert_faq_dict_to_list(materials_data: Dict) -> tuple[int, List[str]]:
    """
    Convert FAQ dict format to list format for all materials.
    
    Returns:
        Tuple of (converted_count, list of converted material names)
    """
    converted_count = 0
    converted_materials = []
    
    for name, material in materials_data['materials'].items():
        faq = material.get('faq')
        
        # Skip if no FAQ or already list format
        if faq is None or isinstance(faq, list):
            continue
        
        # Convert dict format to list format
        if isinstance(faq, dict) and 'questions' in faq:
            questions = faq['questions']
            
            # Ensure questions is a list
            if isinstance(questions, list):
                # Replace dict with just the questions list
                material['faq'] = questions
                converted_count += 1
                converted_materials.append(name)
                print(f"  ✓ Converted {name}: {len(questions)} FAQ items")
    
    return converted_count, converted_materials


def main():
    """Main conversion process."""
    print("\n" + "="*80)
    print("📋 FAQ DICT → LIST CONVERSION")
    print("="*80 + "\n")
    
    # Load Materials.yaml
    materials_path = Path('materials/data/Materials.yaml')
    
    print("📂 Loading Materials.yaml...")
    with open(materials_path, 'r', encoding='utf-8') as f:
        materials_data = yaml.safe_load(f)
    
    total_materials = len(materials_data['materials'])
    print(f"   Found {total_materials} materials\n")
    
    # Count current formats
    list_format = sum(1 for m in materials_data['materials'].values() 
                     if isinstance(m.get('faq'), list))
    dict_format = sum(1 for m in materials_data['materials'].values() 
                     if isinstance(m.get('faq'), dict))
    
    print(f"📊 Current Status:")
    print(f"   List format: {list_format}")
    print(f"   Dict format: {dict_format}")
    print(f"   No FAQ: {total_materials - list_format - dict_format}\n")
    
    if dict_format == 0:
        print("✅ All materials already in list format!")
        return
    
    # Convert
    print(f"🔄 Converting {dict_format} materials from dict → list format...\n")
    converted_count, converted_materials = convert_faq_dict_to_list(materials_data)
    
    # Save back to Materials.yaml
    print(f"\n💾 Saving changes to Materials.yaml...")
    with open(materials_path, 'w', encoding='utf-8') as f:
        yaml.dump(materials_data, f, default_flow_style=False, 
                 allow_unicode=True, sort_keys=False, width=1000)
    
    print("   ✅ Materials.yaml updated successfully\n")
    
    # Summary
    print("="*80)
    print("✅ CONVERSION COMPLETE")
    print("="*80)
    print(f"\n📊 STATISTICS:")
    print(f"   Materials Converted: {converted_count}/{dict_format}")
    print(f"   Success Rate: {converted_count/dict_format*100:.1f}%\n")
    
    print("Next steps:")
    print("  1. Run enhancement: python3 scripts/enhance_existing_faqs.py")
    print("  2. Export to frontmatter: python3 run.py --deploy")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
