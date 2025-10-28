#!/usr/bin/env python3
"""
Automatically generate FAQs for materials without them - NO PROMPTS
"""
import sys
import time
sys.path.insert(0, '.')

from components.faq.generators.faq_generator import FAQComponentGenerator
from api.client_factory import create_api_client
import yaml

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
    
    # Find materials without FAQs
    without_faq = [name for name, mat in materials.items() 
                   if 'faq' not in mat or not mat['faq']]
    
    print(f"\n📊 Status: {total - len(without_faq)}/{total} have FAQs")
    print(f"🎯 Need to generate: {len(without_faq)} materials\n")
    
    if not without_faq:
        print("✅ All materials have FAQs!")
        return 0
    
        # Initialize generator
    print("\n📦 Initializing FAQ generator...")
    api_client = create_api_client('grok')
    faq_gen = FAQComponentGenerator()
    print("✅ Ready\n")
    
    # Generate FAQs
    print("=" * 60)
    print("🚀 STARTING FAQ GENERATION")
    print("=" * 60 + "\n")
    
    generated = 0
    failed = 0
    failed_list = []
    
    for idx, material_name in enumerate(without_faq, 1):
        print(f"[{idx}/{len(without_faq)}] {material_name}")
        print("-" * 50)
        
        try:
            material_data = materials[material_name]
            
            start = time.time()
            result = faq_gen.generate(material_name, material_data, api_client=api_client)
            elapsed = time.time() - start
            
            if result.success:
                faq_yaml = yaml.safe_load(result.content)
                faq_data = faq_yaml.get('faq', [])
                
                # Save
                material_data['faq'] = faq_data
                materials[material_name] = material_data
                data['materials'] = materials
                
                with open('data/Materials.yaml', 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                
                words = [len(f['answer'].split()) for f in faq_data]
                avg = sum(words) / len(words) if words else 0
                
                print(f"✅ {len(faq_data)} FAQs | {min(words)}-{max(words)}w (avg {avg:.0f}) | {elapsed:.1f}s")
                generated += 1
                
                if idx < len(without_faq):
                    time.sleep(2)
                    
            else:
                print(f"❌ Failed: {result.error_message}")
                failed += 1
                failed_list.append(material_name)
                
        except KeyboardInterrupt:
            print(f"\n⚠️  Interrupted! Progress: {generated} completed")
            return 0
            
        except Exception as e:
            print(f"❌ Error: {e}")
            failed += 1
            failed_list.append(material_name)
        
        print()
    
    # Summary
    print("=" * 60)
    print("📊 COMPLETE")
    print("=" * 60)
    print(f"Generated: {generated} | Failed: {failed}")
    
    if failed_list:
        print(f"\n❌ Failed: {', '.join(failed_list[:5])}")
        if len(failed_list) > 5:
            print(f"   ... and {len(failed_list) - 5} more")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
