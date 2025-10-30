#!/usr/bin/env python3
"""
Export FAQs for Steel, Aluminum, and Bronze to frontmatter YAML files.
"""

import yaml
from pathlib import Path
from datetime import datetime

def export_faq_to_frontmatter(material_name: str):
    """Export FAQ from Materials.yaml to frontmatter file."""
    
    # Load Materials.yaml
    materials_path = Path("data/materials.yaml")
    with open(materials_path, 'r') as f:
        materials_data = yaml.safe_load(f)
    
    # Get material data
    material_data = materials_data['materials'].get(material_name)
    if not material_data:
        print(f"❌ {material_name} not found in Materials.yaml")
        return False
    
    faq = material_data.get('faq', [])
    if not faq:
        print(f"❌ {material_name} has no FAQ data")
        return False
    
    # Create frontmatter structure
    frontmatter = {
        'material_name': material_name,
        'last_updated': datetime.now().isoformat(),
        'faq_count': len(faq),
        'faq': faq
    }
    
    # Create output directory
    output_dir = Path("content/materials/faq")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create filename (lowercase, replace spaces with hyphens)
    filename = material_name.lower().replace(' ', '-') + "-faq.yaml"
    output_path = output_dir / filename
    
    # Write frontmatter file
    with open(output_path, 'w') as f:
        yaml.dump(frontmatter, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ {material_name}: {len(faq)} questions exported to {output_path}")
    return True

def main():
    print("=" * 70)
    print("EXPORTING 3 TEST FAQs TO FRONTMATTER")
    print("=" * 70)
    print()
    
    materials = ["Steel", "Aluminum", "Bronze"]
    
    success_count = 0
    for material in materials:
        if export_faq_to_frontmatter(material):
            success_count += 1
        print()
    
    print("=" * 70)
    print(f"EXPORT COMPLETE: {success_count}/{len(materials)} materials")
    print("=" * 70)
    print()
    print("Output directory: content/materials/faq/")
    print("Files created:")
    output_dir = Path("content/materials/faq")
    if output_dir.exists():
        for file in sorted(output_dir.glob("*-faq.yaml")):
            if any(m.lower() in file.name for m in materials):
                print(f"  - {file.name}")

if __name__ == "__main__":
    main()
