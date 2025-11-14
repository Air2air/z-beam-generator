#!/usr/bin/env python3
"""
Batch FAQ Topic Enhancement for All Materials

Generates FAQ with topic enhancement for all 132 materials.

This script:
1. Loads all materials from Materials.yaml
2. For each material, generates FAQ with topic enhancement
3. Tracks success/failure statistics
4. Exports to frontmatter with HTML formatting
5. Reports final statistics

Usage:
    python3 scripts/batch_faq_topic_enhancement.py

Author: AI Assistant
Date: November 6, 2025
"""

import logging
import sys
import time
from pathlib import Path
from typing import Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from materials.unified_generator import UnifiedMaterialsGenerator
from components.frontmatter.core.trivial_exporter import TrivialFrontmatterExporter
from shared.api.client_factory import create_api_client
from data.materials.materials import load_materials_cached

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def batch_enhance_all_faqs():
    """Generate FAQ with topic enhancement for all materials."""
    
    print("\n" + "="*80)
    print("FAQ TOPIC ENHANCEMENT - BATCH PROCESSING ALL 132 MATERIALS")
    print("="*80 + "\n")
    
    # Load materials
    print("📂 Loading materials database...")
    materials_data = load_materials_cached()
    material_names = sorted(materials_data['materials'].keys())
    total_materials = len(material_names)
    
    print(f"✅ Loaded {total_materials} materials\n")
    
    # Initialize API client
    print("🔧 Initializing Grok API client...")
    api_client = create_api_client('grok')
    print("✅ Grok client ready\n")
    
    # Initialize generator
    print("🔧 Initializing UnifiedMaterialsGenerator...")
    generator = UnifiedMaterialsGenerator(api_client)
    print("✅ Generator ready\n")
    
    # Initialize exporter
    print("🔧 Initializing TrivialFrontmatterExporter...")
    exporter = TrivialFrontmatterExporter()
    print("✅ Exporter ready\n")
    
    # Statistics
    stats = {
        'total_materials': total_materials,
        'processed': 0,
        'successful': 0,
        'failed': 0,
        'total_faqs': 0,
        'enhanced_faqs': 0,
        'failed_enhancements': 0,
        'errors': []
    }
    
    start_time = time.time()
    
    print("="*80)
    print("🚀 STARTING BATCH PROCESSING")
    print("="*80 + "\n")
    
    # Process each material
    for idx, material_name in enumerate(material_names, 1):
        print(f"\n{'─'*80}")
        print(f"[{idx}/{total_materials}] Processing: {material_name}")
        print(f"{'─'*80}")
        
        try:
            # Generate FAQ with topic enhancement
            print(f"  🤖 Generating FAQ...")
            faq_list = generator.generate(material_name, 'faq')
            
            # Count enhancements
            num_faqs = len(faq_list)
            num_enhanced = sum(1 for faq in faq_list if 'topic_keyword' in faq)
            
            stats['total_faqs'] += num_faqs
            stats['enhanced_faqs'] += num_enhanced
            stats['failed_enhancements'] += (num_faqs - num_enhanced)
            
            print(f"  ✅ Generated {num_faqs} FAQs ({num_enhanced} enhanced)")
            
            # Export to frontmatter
            print(f"  📤 Exporting to frontmatter...")
            material_data = materials_data['materials'][material_name]
            exporter.export_single(material_name, material_data)
            
            print(f"  ✅ Exported successfully")
            
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
    
    # Final statistics
    elapsed_time = time.time() - start_time
    
    print("\n" + "="*80)
    print("✅ BATCH PROCESSING COMPLETE")
    print("="*80 + "\n")
    
    print("📊 FINAL STATISTICS:")
    print("─"*80)
    print(f"  Materials Processed:     {stats['processed']}/{stats['total_materials']}")
    print(f"  Successful:              {stats['successful']} ({stats['successful']/stats['total_materials']*100:.1f}%)")
    print(f"  Failed:                  {stats['failed']}")
    print()
    print(f"  Total FAQ Items:         {stats['total_faqs']}")
    print(f"  Enhanced with Topics:    {stats['enhanced_faqs']} ({stats['enhanced_faqs']/stats['total_faqs']*100:.1f}%)")
    print(f"  Failed Enhancements:     {stats['failed_enhancements']} ({stats['failed_enhancements']/stats['total_faqs']*100:.1f}%)")
    print()
    print(f"  Processing Time:         {elapsed_time/60:.1f} minutes")
    print(f"  Average per Material:    {elapsed_time/stats['processed']:.1f} seconds")
    print("─"*80)
    
    if stats['errors']:
        print("\n⚠️  ERRORS:")
        print("─"*80)
        for error in stats['errors']:
            print(f"  • {error['material']}: {error['error']}")
        print("─"*80)
    
    print("\n" + "="*80)
    print("🎉 BATCH ENHANCEMENT COMPLETE!")
    print("="*80 + "\n")
    
    return stats


if __name__ == '__main__':
    try:
        stats = batch_enhance_all_faqs()
        sys.exit(0 if stats['failed'] == 0 else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Batch processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
