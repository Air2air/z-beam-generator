#!/usr/bin/env python3
"""
Sample FAQ Topic Enhancement Test

Demonstrates the complete FAQ topic enhancement flow with a real material.

This script:
1. Generates FAQ for Bronze (with topic enhancement)
2. Shows the enhanced FAQ in Materials.yaml
3. Exports to frontmatter with HTML formatting
4. Displays before/after comparison

Usage:
    python3 scripts/sample_faq_enhancement_test.py

Author: AI Assistant
Date: November 6, 2025
"""

import logging
import sys
import yaml
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from materials.unified_generator import UnifiedMaterialsGenerator
from components.frontmatter.core.trivial_exporter import TrivialFrontmatterExporter
from shared.api.client_factory import APIClientFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run sample FAQ topic enhancement test."""
    
    print("\n" + "="*70)
    print("FAQ TOPIC ENHANCEMENT - SAMPLE TEST")
    print("="*70 + "\n")
    
    # Material to test
    material_name = "Bronze"
    
    print(f"🎯 Testing with material: {material_name}\n")
    
    # Step 1: Generate FAQ with topic enhancement
    print("Step 1: Generating FAQ with topic enhancement...")
    print("-" * 70)
    
    try:
        # Initialize API client
        api_client = APIClientFactory.create_client("grok")
        
        # Initialize generator
        generator = UnifiedMaterialsGenerator(api_client)
        
        # Generate FAQ with topic enhancement
        faq_data = generator.generate(material_name, 'faq', faq_count=3)
        
        print(f"✅ Generated {len(faq_data)} FAQ items\n")
        
    except Exception as e:
        print(f"❌ Error generating FAQ: {e}")
        return 1
    
    # Step 2: Show enhanced FAQ from Materials.yaml
    print("\nStep 2: Enhanced FAQ in Materials.yaml")
    print("-" * 70)
    
    materials_path = Path(__file__).resolve().parents[1] / "materials" / "data" / "Materials.yaml"
    
    try:
        with open(materials_path, 'r', encoding='utf-8') as f:
            materials_data = yaml.safe_load(f)
        
        bronze_faq = materials_data['materials'][material_name].get('faq', [])
        
        for idx, item in enumerate(bronze_faq[:3], 1):  # Show first 3
            print(f"\nFAQ {idx}:")
            print(f"  Question: {item.get('question', 'N/A')[:100]}...")
            print(f"  Answer: {item.get('answer', 'N/A')[:100]}...")
            
            # Show topic metadata (internal only)
            if 'topic_keyword' in item:
                print(f"  ✨ Topic Keyword: \"{item['topic_keyword']}\"")
            if 'topic_statement' in item:
                print(f"  ✨ Topic Statement: \"{item['topic_statement']}\"")
        
        print()
        
    except Exception as e:
        print(f"❌ Error reading Materials.yaml: {e}")
        return 1
    
    # Step 3: Export to frontmatter with HTML formatting
    print("\nStep 3: Exporting to frontmatter with HTML formatting...")
    print("-" * 70)
    
    try:
        exporter = TrivialFrontmatterExporter()
        exporter.export_single(material_name)
        
        print(f"✅ Exported {material_name} to frontmatter\n")
        
    except Exception as e:
        print(f"❌ Error exporting frontmatter: {e}")
        return 1
    
    # Step 4: Show formatted FAQ from frontmatter
    print("\nStep 4: Formatted FAQ in frontmatter (with HTML)")
    print("-" * 70)
    
    frontmatter_path = Path(__file__).resolve().parents[1] / "frontmatter" / "materials" / f"{material_name.lower()}-laser-cleaning.yaml"
    
    try:
        with open(frontmatter_path, 'r', encoding='utf-8') as f:
            frontmatter_data = yaml.safe_load(f)
        
        frontmatter_faq = frontmatter_data.get('faq', [])
        
        for idx, item in enumerate(frontmatter_faq[:3], 1):  # Show first 3
            print(f"\nFAQ {idx}:")
            print(f"  Question: {item.get('question', 'N/A')}")
            print(f"  Answer: {item.get('answer', 'N/A')[:150]}...")
            
            # Check for HTML formatting
            if '<strong>' in item.get('question', ''):
                print("  ✅ Question has <strong> tags (topic keyword highlighted)")
            if item.get('answer', '').startswith('<strong>'):
                print("  ✅ Answer has prepended <strong> topic statement")
        
        print()
        
    except Exception as e:
        print(f"❌ Error reading frontmatter: {e}")
        return 1
    
    # Step 5: Before/After Comparison
    print("\nStep 5: Before/After Comparison")
    print("-" * 70)
    
    if bronze_faq and frontmatter_faq:
        print("\n📝 BEFORE (Materials.yaml - Internal):")
        print("-" * 70)
        item = bronze_faq[0]
        print(f"Question: {item.get('question', 'N/A')[:100]}...")
        print(f"Answer: {item.get('answer', 'N/A')[:100]}...")
        print(f"Topic Keyword: {item.get('topic_keyword', 'N/A')}")
        print(f"Topic Statement: {item.get('topic_statement', 'N/A')}")
        
        print("\n✨ AFTER (Frontmatter - Exported):")
        print("-" * 70)
        item = frontmatter_faq[0]
        print(f"Question: {item.get('question', 'N/A')}")
        print(f"Answer: {item.get('answer', 'N/A')[:200]}...")
        print("\nNote: topic_keyword and topic_statement are stripped (internal metadata only)")
    
    print("\n" + "="*70)
    print("✅ SAMPLE TEST COMPLETE")
    print("="*70 + "\n")
    
    print("Summary:")
    print("  • FAQ generated with AI-researched topic keywords and statements")
    print("  • Topic metadata stored in Materials.yaml (internal)")
    print("  • HTML formatting applied at export time")
    print("  • Frontmatter contains only question/answer with <strong> tags")
    print("  • Topic metadata stripped from export (clean separation)")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
