#!/usr/bin/env python3
"""
Direct FAQ export to frontmatter - bypassing validation orchestrator
"""
import yaml
from pathlib import Path

# Materials to export
materials = ["Beryllium", "Alabaster", "Ash", "Carbon Fiber Reinforced Polymer"]

print("="*80)
print("DIRECT FAQ EXPORT TO FRONTMATTER")
print("="*80)
print()

# Load Materials.yaml
materials_path = Path("data/Materials.yaml")
with open(materials_path) as f:
    materials_data = yaml.safe_load(f)

for material_name in materials:
    print(f"Processing: {material_name}")
    
    # Get material data
    material = materials_data['materials'].get(material_name)
    if not material:
        print(f"  ❌ Not found in Materials.yaml")
        continue
    
    # Check for FAQ
    faq = material.get('faq')
    if not faq:
        print(f"  ⚠️  No FAQ data found")
        continue
    
    # Create filename
    filename = material_name.lower().replace(' ', '-') + '-laser-cleaning.yaml'
    frontmatter_path = Path('content/frontmatter') / filename
    
    # Load existing frontmatter or create new
    if frontmatter_path.exists():
        with open(frontmatter_path) as f:
            frontmatter_data = yaml.safe_load(f) or {}
        print(f"  ✅ Loaded existing frontmatter")
    else:
        frontmatter_data = {
            'title': f"{material_name} Laser Cleaning",
            'material': material_name
        }
        print(f"  ✅ Created new frontmatter")
    
    # Update FAQ section
    frontmatter_data['faq'] = faq
    
    # Write back
    frontmatter_path.parent.mkdir(parents=True, exist_ok=True)
    with open(frontmatter_path, 'w') as f:
        yaml.dump(frontmatter_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"  💾 Saved to: {frontmatter_path}")
    print(f"     Questions: {len(faq.get('questions', []))}")
    print()

print("="*80)
print("EXPORT COMPLETE!")
print("="*80)
