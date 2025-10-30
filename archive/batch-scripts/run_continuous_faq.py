#!/usr/bin/env python3
"""Continuously generate FAQs using Grok until all materials have them"""
import sys
import time
sys.path.insert(0, '.')

from components.faq.generators.faq_generator import FAQComponentGenerator
from api.client_factory import create_api_client
import yaml

def get_materials_without_faq():
    """Get list of materials without FAQs"""
    with open('data/Materials.yaml', 'r') as f:
        data = yaml.safe_load(f)
    materials = data['materials']
    return [name for name, mat in materials.items() if 'faq' not in mat or not mat['faq']]

def main():
    print("🚀 Continuous FAQ Generation with Grok")
    print("=" * 60)
    
    # Initialize once
    print("\n📦 Initializing Grok API client...")
    api_client = create_api_client('grok')
    faq_gen = FAQComponentGenerator()
    print("✅ Ready!\n")
    
    batch_num = 0
    total_generated = 0
    
    while True:
        # Check how many need FAQs
        without_faq = get_materials_without_faq()
        
        if not without_faq:
            print("\n🎉 ALL DONE! All 132 materials have FAQs!")
            break
        
        # Get next batch (5 at a time)
        batch = without_faq[:5]
        batch_num += 1
        
        print(f"\n📦 Batch #{batch_num} - {len(without_faq)} remaining")
        print("=" * 60)
        
        for idx, name in enumerate(batch, 1):
            print(f"\n[{idx}/5] {name}")
            print("-" * 50)
            
            try:
                # Load current data
                with open('data/Materials.yaml', 'r') as f:
                    data = yaml.safe_load(f)
                
                material_data = data['materials'][name]
                
                # Generate
                result = faq_gen.generate(name, material_data, api_client=api_client)
                
                if result.success:
                    faq_yaml = yaml.safe_load(result.content)
                    faq_data = faq_yaml.get('faq', [])
                    
                    # Save with safer YAML dumping
                    material_data['faq'] = faq_data
                    data['materials'][name] = material_data
                    
                    # Use safer dumping with explicit width to prevent line wrapping issues
                    with open('data/Materials.yaml', 'w') as f:
                        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, 
                                 sort_keys=False, width=1000, explicit_start=False)
                    
                    print(f"✅ Generated {len(faq_data)} FAQs - Saved!")
                    total_generated += 1
                else:
                    print(f"❌ Failed: {result.error_message}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Brief pause between materials
            if idx < len(batch):
                time.sleep(2)
        
        print(f"\n✅ Batch #{batch_num} complete! Total generated: {total_generated}")
        time.sleep(3)
    
    print(f"\n{'=' * 60}")
    print(f"🎊 FINISHED! Generated FAQs for {total_generated} materials")
    print(f"{'=' * 60}")
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user")
        sys.exit(0)
