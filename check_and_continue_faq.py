#!/usr/bin/env python3
"""
Check FAQ status and continue generation
"""
import sys
import time
sys.path.insert(0, '.')

from components.faq.generators.faq_generator import FAQComponentGenerator
from api.client_factory import create_api_client
import yaml
from pathlib import Path

def main():
    print("🔍 Checking FAQ status...")
    
    # Load materials
    try:
        with open('data/Materials.yaml', 'r') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Error loading Materials.yaml: {e}")
        return 1
    
    materials = data.get('materials', {})
    total = len(materials)
    
    # Count materials with/without FAQs
    with_faq = []
    without_faq = []
    
    for name, mat_data in materials.items():
        if 'faq' in mat_data and mat_data['faq']:
            with_faq.append(name)
        else:
            without_faq.append(name)
    
    print(f"\n📊 FAQ Status Report")
    print(f"=" * 60)
    print(f"Total materials: {total}")
    print(f"With FAQs: {len(with_faq)} ({(len(with_faq)/total*100):.1f}%)")
    print(f"Without FAQs: {len(without_faq)} ({(len(without_faq)/total*100):.1f}%)")
    
    if not without_faq:
        print("\n✅ All materials have FAQs!")
        return 0
    
    print(f"\n📝 Materials needing FAQs ({len(without_faq)}):")
    for i, name in enumerate(without_faq[:10], 1):
        print(f"   {i}. {name}")
    if len(without_faq) > 10:
        print(f"   ... and {len(without_faq) - 10} more")
    
    # Ask to continue
    print(f"\n{'=' * 60}")
    response = input(f"\n🤖 Generate FAQs for {len(without_faq)} materials? (y/n): ").strip().lower()
    
    if response != 'y':
        print("❌ Cancelled by user")
        return 0
    
    # Initialize generator
    print("\n📦 Initializing FAQ generator...")
    api_client = create_api_client('grok')
    faq_gen = FAQComponentGenerator()
    
    # Generate FAQs
    generated = 0
    failed = 0
    failed_list = []
    
    print(f"\n{'=' * 60}")
    print("🚀 GENERATING FAQs")
    print(f"{'=' * 60}\n")
    
    for idx, material_name in enumerate(without_faq, 1):
        print(f"\n[{idx}/{len(without_faq)}] {material_name}")
        print("-" * 50)
        
        try:
            material_data = materials[material_name]
            
            print(f"🤖 Generating...")
            start = time.time()
            
            result = faq_gen.generate(
                material_name,
                material_data,
                api_client=api_client
            )
            
            elapsed = time.time() - start
            
            if result.success:
                # Parse FAQ
                faq_yaml = yaml.safe_load(result.content)
                faq_data = faq_yaml.get('faq', [])
                
                # Save to materials
                material_data['faq'] = faq_data
                materials[material_name] = material_data
                data['materials'] = materials
                
                # Save immediately
                with open('data/Materials.yaml', 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                
                word_counts = [len(f['answer'].split()) for f in faq_data]
                avg_words = sum(word_counts) / len(word_counts) if word_counts else 0
                
                print(f"✅ Generated {len(faq_data)} FAQs")
                print(f"   Words: {min(word_counts)}-{max(word_counts)} (avg {avg_words:.1f})")
                print(f"   Time: {elapsed:.1f}s")
                print(f"💾 Saved to Materials.yaml")
                
                generated += 1
                
                # Brief pause
                if idx < len(without_faq):
                    time.sleep(2)
                    
            else:
                print(f"❌ Failed: {result.error_message}")
                failed += 1
                failed_list.append(material_name)
                
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Interrupted by user")
            print(f"💾 Progress saved: {generated} materials completed")
            return 0
            
        except Exception as e:
            print(f"❌ Error: {e}")
            failed += 1
            failed_list.append(material_name)
    
    # Summary
    print(f"\n{'=' * 60}")
    print("📊 GENERATION COMPLETE")
    print(f"{'=' * 60}")
    print(f"\nGenerated: {generated}")
    print(f"Failed: {failed}")
    
    if failed_list:
        print(f"\n❌ Failed materials:")
        for mat in failed_list:
            print(f"   • {mat}")
    
    print(f"\n💾 All changes saved to: data/Materials.yaml")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
