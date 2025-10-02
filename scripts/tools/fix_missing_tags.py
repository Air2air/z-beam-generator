#!/usr/bin/env python3
"""
Fix Missing Tags in Frontmatter Files

Generates and adds tags to frontmatter files that are missing them.
Uses the same logic as TagsComponentGenerator but runs directly on frontmatter data.
"""

import yaml
from pathlib import Path

# Materials missing tags
MISSING_TAGS_MATERIALS = ["basalt", "birch", "maple", "mdf", "plywood", "redwood", "rosewood", "willow"]

BASE_PATH = Path(__file__).resolve().parents[2]

def generate_tags_from_frontmatter(data: dict, material_name: str) -> list:
    """Generate tags based on frontmatter data"""
    tags = []
    
    # 1. Category
    category = data.get('category', 'material').lower()
    tags.append(category)
    
    # 2-5. Industries from applications (up to 5)
    applications = data.get('applications', [])
    industries = []
    for app in applications:
        if isinstance(app, str) and ':' in app:
            industry = app.split(':')[0].strip().lower().replace(' ', '-')
            if industry not in industries:
                industries.append(industry)
                if len(industries) >= 5:
                    break
    tags.extend(industries)
    
    # 6-9. Characteristics from materialProperties
    props = data.get('materialProperties', {})
    characteristics = []
    
    # Priority 1: Reflectivity
    if 'reflectivity' in props and len(characteristics) < 4:
        refl_val = props['reflectivity'].get('value', 0)
        if refl_val > 70:
            characteristics.append('reflective')
        elif refl_val < 30:
            characteristics.append('absorptive')
    
    # Priority 2: Thermal Conductivity
    if 'thermalConductivity' in props and len(characteristics) < 4:
        tc_val = props['thermalConductivity'].get('value', 0)
        if tc_val > 100:
            characteristics.append('conductive')
        elif tc_val < 10:
            characteristics.append('insulating')
    
    # Priority 3: Hardness
    if 'hardness' in props and len(characteristics) < 4:
        hard_val = props['hardness'].get('value', 0)
        unit = props['hardness'].get('unit', '')
        if unit == 'Mohs':
            if hard_val > 7:
                characteristics.append('durable')
            elif hard_val < 3:
                characteristics.append('soft')
        else:  # HV or other
            if hard_val > 300:
                characteristics.append('durable')
            elif hard_val < 50:
                characteristics.append('soft')
    
    # Priority 4: Porosity
    if 'porosity' in props and len(characteristics) < 4:
        poros_val = props['porosity'].get('value', 0)
        if poros_val > 5:
            characteristics.append('porous')
    
    # Priority 5: Density
    if 'density' in props and len(characteristics) < 4:
        dens_val = props['density'].get('value', 0)
        if dens_val > 7:
            characteristics.append('dense')
        elif dens_val < 2:
            characteristics.append('lightweight')
    
    tags.extend(characteristics)
    
    # 10. Author
    author = data.get('author', {})
    if isinstance(author, dict):
        author_name = author.get('name', 'Todd Dunning')
    else:
        author_name = str(author) if author else 'Todd Dunning'
    author_slug = author_name.lower().replace(' ', '-').replace('.', '').replace(',', '')
    tags.append(author_slug)
    
    # Ensure 4-10 tags
    while len(tags) < 4:
        tags.append(f"{category}-material")
    tags = tags[:10]
    
    return tags

def main():
    print("🏷️  Fixing Missing Tags in Frontmatter Files")
    print("=" * 60)
    
    updated_count = 0
    
    for material in MISSING_TAGS_MATERIALS:
        frontmatter_file = BASE_PATH / f"content/components/frontmatter/{material}-laser-cleaning.yaml"
        
        if not frontmatter_file.exists():
            print(f"❌ {material}: Frontmatter file not found")
            continue
        
        # Load frontmatter
        with open(frontmatter_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Check if tags already exist
        if data.get('tags') and len(data.get('tags', [])) >= 5:
            print(f"✓  {material}: Already has {len(data['tags'])} tags")
            continue
        
        # Generate tags
        tags = generate_tags_from_frontmatter(data, material)
        
        # Update frontmatter
        data['tags'] = tags
        
        # Save frontmatter
        with open(frontmatter_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, indent=2)
        
        print(f"✅ {material}: Added {len(tags)} tags - {', '.join(tags)}")
        updated_count += 1
    
    print("=" * 60)
    print(f"🎉 Updated {updated_count}/{len(MISSING_TAGS_MATERIALS)} materials")

if __name__ == '__main__':
    main()
