#!/usr/bin/env python3
"""
Enhance Existing FAQs with Topic Keywords and Statements

This script ONLY adds topic enhancements to existing FAQ entries.
It does NOT regenerate or modify the question/answer text.

Process:
1. Load existing FAQs from Materials.yaml
2. For each FAQ, analyze the existing Q&A text
3. Extract topic keyword (2-4 words from question)
4. Generate topic statement (2-5 word answer summary)
5. Add topic_keyword and topic_statement fields
6. Save back to Materials.yaml (preserving original Q&A text)

Usage:
    python3 scripts/enhance_existing_faqs.py

Author: AI Assistant
Date: November 6, 2025
"""

import logging
import sys
import time
from pathlib import Path
from typing import Dict

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from materials.research.faq_topic_researcher import FAQTopicResearcher
from shared.api.client_factory import create_api_client
from materials.data.materials import load_materials_cached
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def enhance_existing_faqs():
    """Enhance existing FAQs with topic keywords and statements."""
    
    print("\n" + "="*80)
    print("ENHANCE EXISTING FAQs - TOPIC KEYWORDS & STATEMENTS")
    print("="*80 + "\n")
    
    print("📋 THIS SCRIPT WILL:")
    print("  ✓ Read existing FAQ questions and answers")
    print("  ✓ Analyze them to extract topic keywords and statements")
    print("  ✓ Add topic_keyword and topic_statement fields")
    print("  ✓ Preserve all original Q&A text unchanged")
    print("="*80 + "\n")
    
    # Load materials
    print("📂 Loading materials database...")
    materials_data = load_materials_cached()
    material_names = sorted(materials_data['materials'].keys())
    
    # Filter to only materials with existing FAQs
    materials_with_faqs = [
        name for name in material_names 
        if materials_data['materials'][name].get('faq') 
        and isinstance(materials_data['materials'][name]['faq'], list)
        and len(materials_data['materials'][name]['faq']) > 0
    ]
    
    total_materials = len(materials_with_faqs)
    print(f"✅ Found {total_materials} materials with existing FAQs\n")
    
    # Initialize API client
    print("🔧 Initializing Grok API client...")
    api_client = create_api_client('grok')
    print("✅ Grok client ready\n")
    
    # Initialize topic researcher
    print("🔧 Initializing FAQTopicResearcher...")
    researcher = FAQTopicResearcher(api_client)
    print("✅ Researcher ready\n")
    
    # Statistics
    stats = {
        'total_materials': total_materials,
        'processed': 0,
        'successful': 0,
        'failed': 0,
        'total_faqs': 0,
        'enhanced_faqs': 0,
        'already_enhanced': 0,
        'failed_enhancements': 0,
        'errors': []
    }
    
    start_time = time.time()
    
    print("="*80)
    print("🚀 STARTING FAQ ENHANCEMENT")
    print("="*80 + "\n")
    
    # Load Materials.yaml directly for editing
    materials_path = Path(__file__).resolve().parents[1] / "materials" / "data" / "Materials.yaml"
    
    with open(materials_path, 'r', encoding='utf-8') as f:
        materials_yaml = yaml.safe_load(f)
    
    # Process each material
    for idx, material_name in enumerate(materials_with_faqs, 1):
        print(f"\n{'─'*80}")
        print(f"[{idx}/{total_materials}] Processing: {material_name}")
        print(f"{'─'*80}")
        
        try:
            # Get existing FAQs
            existing_faqs = materials_yaml['materials'][material_name]['faq']
            
            if not isinstance(existing_faqs, list):
                print(f"  ⚠️  Skipping - FAQ is not a list")
                continue
            
            num_faqs = len(existing_faqs)
            print(f"  📝 Found {num_faqs} existing FAQ items")
            
            # Check which FAQs already have topic enhancements
            already_enhanced = sum(
                1 for faq in existing_faqs 
                if 'topic_keyword' in faq and 'topic_statement' in faq
            )
            
            if already_enhanced == num_faqs:
                print(f"  ✓ All {num_faqs} FAQs already enhanced - skipping")
                stats['already_enhanced'] += num_faqs
                stats['total_faqs'] += num_faqs
                stats['enhanced_faqs'] += num_faqs
                stats['successful'] += 1
                stats['processed'] += 1
                continue
            
            print(f"  🔍 Analyzing existing FAQ text...")
            
            # Enhance FAQs (adds topic fields without changing Q&A text)
            enhanced_faqs = researcher.enhance_faq_topics(material_name, existing_faqs)
            
            # Count new enhancements
            newly_enhanced = sum(
                1 for faq in enhanced_faqs 
                if 'topic_keyword' in faq and 'topic_statement' in faq
            ) - already_enhanced
            
            stats['total_faqs'] += num_faqs
            stats['enhanced_faqs'] += newly_enhanced
            stats['failed_enhancements'] += (num_faqs - (already_enhanced + newly_enhanced))
            
            print(f"  ✅ Enhanced {newly_enhanced} new FAQs (already had {already_enhanced})")
            
            # Update Materials.yaml
            materials_yaml['materials'][material_name]['faq'] = enhanced_faqs
            
            stats['successful'] += 1
            stats['processed'] += 1
            
            # Progress update every 10 materials
            if idx % 10 == 0:
                elapsed = time.time() - start_time
                rate = stats['processed'] / elapsed
                remaining = (total_materials - stats['processed']) / rate if rate > 0 else 0
                print(f"\n  📊 Progress: {stats['processed']}/{total_materials} ({stats['processed']/total_materials*100:.1f}%)")
                print(f"  ⏱️  Elapsed: {elapsed/60:.1f}m | Estimated remaining: {remaining/60:.1f}m")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            stats['failed'] += 1
            stats['processed'] += 1
            stats['errors'].append({
                'material': material_name,
                'error': str(e)
            })
    
    # Save updated Materials.yaml
    print("\n" + "="*80)
    print("💾 SAVING ENHANCED FAQs TO MATERIALS.YAML")
    print("="*80)
    
    try:
        with open(materials_path, 'w', encoding='utf-8') as f:
            yaml.dump(materials_yaml, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
        print("✅ Materials.yaml updated successfully")
    except Exception as e:
        print(f"❌ Error saving Materials.yaml: {e}")
        return 1
    
    # Final statistics
    elapsed_time = time.time() - start_time
    
    print("\n" + "="*80)
    print("✅ FAQ ENHANCEMENT COMPLETE")
    print("="*80 + "\n")
    
    print("📊 FINAL STATISTICS:")
    print("─"*80)
    print(f"  Materials Processed:     {stats['processed']}/{stats['total_materials']}")
    print(f"  Successful:              {stats['successful']} ({stats['successful']/stats['total_materials']*100:.1f}%)")
    print(f"  Failed:                  {stats['failed']}")
    print()
    print(f"  Total FAQ Items:         {stats['total_faqs']}")
    print(f"  Newly Enhanced:          {stats['enhanced_faqs']}")
    print(f"  Already Enhanced:        {stats['already_enhanced']}")
    print(f"  Failed Enhancements:     {stats['failed_enhancements']}")
    if stats['total_faqs'] > 0:
        total_enhanced = stats['enhanced_faqs'] + stats['already_enhanced']
        print(f"  Total Enhanced:          {total_enhanced}/{stats['total_faqs']} ({total_enhanced/stats['total_faqs']*100:.1f}%)")
    print()
    print(f"  Processing Time:         {elapsed_time/60:.1f} minutes")
    if stats['processed'] > 0:
        print(f"  Average per Material:    {elapsed_time/stats['processed']:.1f} seconds")
    print("─"*80)
    
    if stats['errors']:
        print("\n⚠️  ERRORS:")
        print("─"*80)
        for error in stats['errors']:
            print(f"  • {error['material']}: {error['error']}")
        print("─"*80)
    
    print("\n" + "="*80)
    print("🎉 ENHANCEMENT COMPLETE!")
    print("="*80)
    print("\nNext steps:")
    print("  1. Review enhanced FAQs in Materials.yaml")
    print("  2. Export to frontmatter: python3 run.py --deploy")
    print("  3. Verify HTML formatting in frontmatter files")
    print("="*80 + "\n")
    
    return 0 if stats['failed'] == 0 else 1


if __name__ == '__main__':
    try:
        sys.exit(enhance_existing_faqs())
    except KeyboardInterrupt:
        print("\n\n⚠️  Enhancement interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
