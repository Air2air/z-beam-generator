#!/usr/bin/env python3
"""Generate FAQs for first 5 materials without them"""
import sys
sys.path.insert(0, '.')

from components.faq.generators.faq_generator import FAQComponentGenerator
from api.client_factory import create_api_client
import yaml
import time

# Load Materials.yaml
with open('data/Materials.yaml', 'r') as f:
    data = yaml.safe_load(f)

materials = data['materials']

# Find first 5 without FAQs
to_generate = []
for name, mat in materials.items():
    if 'faq' not in mat or not mat['faq']:
        to_generate.append(name)
        if len(to_generate) >= 5:
            break

print(f"🎯 Generating FAQs for {len(to_generate)} materials:")
for name in to_generate:
    print(f"   • {name}")
print()

# Initialize
api_client = create_api_client('grok')
faq_gen = FAQComponentGenerator()

# Generate
for idx, name in enumerate(to_generate, 1):
    print(f"\n[{idx}/5] {name}")
    print("-" * 40)
    
    try:
        result = faq_gen.generate(name, materials[name], api_client=api_client)
        
        if result.success:
            faq_yaml = yaml.safe_load(result.content)
            faq_data = faq_yaml.get('faq', [])
            
            # Save
            materials[name]['faq'] = faq_data
            data['materials'] = materials
            
            with open('data/Materials.yaml', 'w') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            print(f"✅ Generated {len(faq_data)} FAQs - Saved!")
        else:
            print(f"❌ Failed: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    if idx < len(to_generate):
        time.sleep(2)

print("\n✅ Batch complete!")
