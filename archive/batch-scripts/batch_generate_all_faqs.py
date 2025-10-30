#!/usr/bin/env python3
"""
Batch FAQ Generation for All Materials
Generates FAQs for all materials in Materials.yaml
"""
import sys
import time
sys.path.insert(0, '.')

from components.faq.generators.faq_generator import FAQComponentGenerator
from api.client_factory import create_api_client
import yaml
from pathlib import Path

def load_materials():
    """Load Materials.yaml"""
    with open('data/Materials.yaml', 'r') as f:
        return yaml.safe_load(f)

def save_materials(data):
    """Save Materials.yaml"""
    with open('data/Materials.yaml', 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

def main():
    print("=" * 80)
    print("🚀 BATCH FAQ GENERATION FOR ALL MATERIALS")
    print("=" * 80)
    
    # Load materials
    print("\n📂 Loading Materials.yaml...")
    materials_data = load_materials()
    all_materials = list(materials_data['materials'].keys())
    total = len(all_materials)
    
    print(f"✅ Found {total} materials")
    
    # Initialize generator
    print("\n📦 Initializing FAQ generator...")
    api_client = create_api_client('grok')
    faq_gen = FAQComponentGenerator()
    print("✅ Generator ready")
    
    # Track progress
    generated = 0
    skipped = 0
    failed = 0
    failed_materials = []
    
    print(f"\n{'=' * 80}")
    print("🤖 GENERATING FAQs")
    print(f"{'=' * 80}\n")
    
    for idx, material_name in enumerate(all_materials, 1):
        material_data = materials_data['materials'][material_name]
        
        print(f"\n[{idx}/{total}] {material_name}")
        print("-" * 70)
        
        # Check if FAQ already exists
        if 'faq' in material_data and material_data['faq']:
            existing_count = len(material_data['faq'])
            print(f"⏭️  Skipping (already has {existing_count} FAQs)")
            skipped += 1
            continue
        
        try:
            # Generate FAQ
            print(f"🤖 Generating...")
            start_time = time.time()
            
            result = faq_gen.generate(
                material_name,
                material_data,
                api_client=api_client
            )
            
            elapsed = time.time() - start_time
            
            if result.success:
                # Parse and save
                faq_yaml = yaml.safe_load(result.content)
                faq_data = faq_yaml.get('faq', [])
                
                # Calculate stats
                word_counts = [len(f['answer'].split()) for f in faq_data]
                avg_words = sum(word_counts) / len(word_counts) if word_counts else 0
                
                # Save to materials data
                material_data['faq'] = faq_data
                materials_data['materials'][material_name] = material_data
                
                print(f"✅ Generated {len(faq_data)} FAQs")
                print(f"   Words: {min(word_counts)}-{max(word_counts)} (avg {avg_words:.1f})")
                print(f"   Time: {elapsed:.1f}s")
                
                # Save immediately (incremental save)
                save_materials(materials_data)
                print(f"💾 Saved to Materials.yaml")
                
                generated += 1
                
                # Brief pause between materials
                if idx < total:
                    time.sleep(2)
                
            else:
                print(f"❌ Generation failed: {result.error_message}")
                failed += 1
                failed_materials.append(material_name)
                
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Interrupted by user")
            print(f"💾 Progress saved: {generated} materials completed")
            sys.exit(0)
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            failed += 1
            failed_materials.append(material_name)
            continue
    
    # Final summary
    print(f"\n{'=' * 80}")
    print("📊 BATCH GENERATION COMPLETE")
    print(f"{'=' * 80}")
    print(f"\n📈 Statistics:")
    print(f"   Total Materials: {total}")
    print(f"   Generated: {generated}")
    print(f"   Skipped: {skipped} (already had FAQs)")
    print(f"   Failed: {failed}")
    
    if failed_materials:
        print(f"\n❌ Failed Materials:")
        for mat in failed_materials:
            print(f"   • {mat}")
    
    print(f"\n💾 All FAQs saved to: data/Materials.yaml")
    print(f"{'=' * 80}\n")
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
