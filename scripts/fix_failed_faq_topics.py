#!/usr/bin/env python3
"""
Fix FAQs that failed topic enhancement due to validation errors.

Re-runs enhancement with stricter prompt emphasizing exact substring requirement.
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from materials.research.faq_topic_researcher import FAQTopicResearcher

def find_failed_faqs() -> List[Tuple[str, List[int]]]:
    """
    Find all FAQs missing topic enhancements.
    
    Returns:
        List of (material_name, [faq_indices]) tuples
    """
    materials_path = Path('materials/data/Materials.yaml')
    
    with open(materials_path, 'r', encoding='utf-8') as f:
        materials_data = yaml.safe_load(f)
    
    failed_faqs = []
    
    for name, material in materials_data['materials'].items():
        faq_list = material.get('faq', [])
        if not isinstance(faq_list, list):
            continue
        
        # Find FAQs without topic enhancements
        missing_indices = []
        for i, faq in enumerate(faq_list):
            if not isinstance(faq, dict):
                continue
            
            # Check if topic fields are missing
            if 'topic_keyword' not in faq or 'topic_statement' not in faq:
                missing_indices.append(i)
        
        if missing_indices:
            failed_faqs.append((name, missing_indices))
    
    return failed_faqs


def enhance_failed_faqs(dry_run: bool = False) -> Dict:
    """
    Re-enhance FAQs that failed the first time.
    
    Args:
        dry_run: If True, don't save changes
        
    Returns:
        Statistics dict
    """
    print("\n" + "="*80)
    print("🔧 FIXING FAILED FAQ TOPIC ENHANCEMENTS")
    print("="*80 + "\n")
    
    # Find failed FAQs
    print("🔍 Scanning for FAQs without topic enhancements...")
    failed_faqs = find_failed_faqs()
    
    if not failed_faqs:
        print("✅ All FAQs already have topic enhancements!")
        return {'total': 0, 'fixed': 0, 'still_failed': 0}
    
    total_failed = sum(len(indices) for _, indices in failed_faqs)
    print(f"   Found {total_failed} FAQs across {len(failed_faqs)} materials\n")
    
    # Load Materials.yaml
    materials_path = Path('materials/data/Materials.yaml')
    with open(materials_path, 'r', encoding='utf-8') as f:
        materials_data = yaml.safe_load(f)
    
    # Initialize researcher with stricter prompt
    from shared.config.api_keys import API_KEYS
    researcher = FAQTopicResearcher(API_KEYS['GROK_API_KEY'])
    
    # Process failed FAQs
    fixed_count = 0
    still_failed_count = 0
    
    for material_name, failed_indices in failed_faqs:
        print(f"📝 Processing {material_name}: {len(failed_indices)} FAQs")
        
        material = materials_data['materials'][material_name]
        faq_list = material['faq']
        
        for idx in failed_indices:
            faq = faq_list[idx]
            question = faq.get('question', '')
            answer = faq.get('answer', '')
            
            if not question or not answer:
                continue
            
            # Try enhancement with explicit substring requirement
            print(f"   Attempting FAQ {idx + 1}...")
            
            # Try to research topic for this FAQ
            try:
                result = researcher._research_single_faq(
                    question=question,
                    answer=answer,
                    material_name=material_name
                )
                
                if result:
                    # Successfully enhanced
                    faq['topic_keyword'] = result['topic_keyword']
                    faq['topic_statement'] = result['topic_statement']
                    fixed_count += 1
                    print(f"      ✓ Fixed: '{result['topic_keyword']}' → '{result['topic_statement']}'")
                else:
                    # Still failed validation
                    still_failed_count += 1
                    print(f"      ✗ Enhancement failed validation")
                    
            except Exception as e:
                still_failed_count += 1
                print(f"      ✗ Error: {e}")
    
    # Save if not dry run
    if not dry_run and fixed_count > 0:
        print(f"\n💾 Saving {fixed_count} fixed FAQs to Materials.yaml...")
        with open(materials_path, 'w', encoding='utf-8') as f:
            yaml.dump(materials_data, f, default_flow_style=False,
                     allow_unicode=True, sort_keys=False, width=1000)
        print("   ✅ Saved successfully")
    
    # Summary
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"   Total Failed FAQs: {total_failed}")
    print(f"   Fixed: {fixed_count} ({fixed_count/total_failed*100:.1f}%)")
    print(f"   Still Failed: {still_failed_count} ({still_failed_count/total_failed*100:.1f}%)")
    
    if dry_run:
        print("\n⚠️  DRY RUN - No changes saved")
    
    print("="*80 + "\n")
    
    return {
        'total': total_failed,
        'fixed': fixed_count,
        'still_failed': still_failed_count
    }


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix failed FAQ topic enhancements')
    parser.add_argument('--dry-run', action='store_true', help='Preview without saving')
    args = parser.parse_args()
    
    enhance_failed_faqs(dry_run=args.dry_run)
