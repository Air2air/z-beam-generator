"""
Fix source data files to comply with Frontend Spec 5.0.0.

This script updates source data files (Materials.yaml, Contaminants.yaml, etc.)
to ensure they have all required fields per BACKEND_FRONTMATTER_SPEC.md:
- Remove deprecated 'description' field (use page_description instead)
- Add images structure with width/height dimensions
- Ensure page_description exists

Per FRONTMATTER_SOURCE_OF_TRUTH_POLICY.md, we MUST fix source data,
not frontmatter files directly.
"""

import yaml
from pathlib import Path
from typing import Dict, Any


def add_images_structure(data: Dict[str, Any], item_id: str, name: str, domain: str) -> None:
    """Add properly structured images field with dimensions per spec."""
    
    domain_paths = {
        'materials': 'material',
        'contaminants': 'contaminant',
        'compounds': 'compound',
        'settings': 'settings'
    }
    
    path_prefix = domain_paths.get(domain, domain)
    
    if 'images' not in data:
        # Create complete structure
        data['images'] = {
            'hero': {
                'url': f'/images/{path_prefix}/{item_id}-hero.jpg',
                'alt': f'{name} laser cleaning visualization showing process effects',
                'width': 1200,
                'height': 630
            },
            'micro': {
                'url': f'/images/{path_prefix}/{item_id}-micro.jpg',
                'alt': f'{name} microscopic detail view showing surface characteristics',
                'width': 800,
                'height': 600
            }
        }
    else:
        # Add missing dimensions to existing images
        if 'hero' in data['images']:
            if 'width' not in data['images']['hero']:
                data['images']['hero']['width'] = 1200
            if 'height' not in data['images']['hero']:
                data['images']['hero']['height'] = 630
        
        if 'micro' in data['images']:
            if 'width' not in data['images']['micro']:
                data['images']['micro']['width'] = 800
            if 'height' not in data['images']['micro']:
                data['images']['micro']['height'] = 600


def fix_materials():
    """Fix Materials.yaml - add width/height to existing images."""
    print("\n" + "=" * 80)
    print("FIXING MATERIALS")
    print("=" * 80)
    
    filepath = Path('data/materials/Materials.yaml')
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    
    count = 0
    for item_id, item_data in data['materials'].items():
        if 'images' in item_data:
            # Add dimensions to existing images
            add_images_structure(item_data, item_id, item_data.get('name', item_id), 'materials')
            count += 1
    
    with open(filepath, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"✅ Updated {count} materials with image dimensions")


def fix_contaminants():
    """Fix Contaminants.yaml - remove description, add images."""
    print("\n" + "=" * 80)
    print("FIXING CONTAMINANTS")
    print("=" * 80)
    
    filepath = Path('data/contaminants/Contaminants.yaml')
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    
    removed_description = 0
    added_images = 0
    
    for item_id, item_data in data['contamination_patterns'].items():
        # Remove deprecated description field
        if 'description' in item_data:
            del item_data['description']
            removed_description += 1
        
        # Add images structure
        add_images_structure(item_data, item_id, item_data.get('name', item_id), 'contaminants')
        added_images += 1
    
    with open(filepath, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"✅ Removed 'description' field from {removed_description} contaminants")
    print(f"✅ Added images structure to {added_images} contaminants")


def fix_compounds():
    """Fix Compounds.yaml - remove description, add images, ensure page_description."""
    print("\n" + "=" * 80)
    print("FIXING COMPOUNDS")
    print("=" * 80)
    
    filepath = Path('data/compounds/Compounds.yaml')
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    
    removed_description = 0
    added_images = 0
    added_page_desc = 0
    
    for item_id, item_data in data['compounds'].items():
        # Remove deprecated description field
        if 'description' in item_data:
            desc = item_data['description']
            del item_data['description']
            removed_description += 1
            
            # If no page_description, create one from first sentence of description
            if 'page_description' not in item_data and desc:
                # Take first sentence (up to 160 chars)
                first_sentence = desc.split('.')[0][:160]
                item_data['page_description'] = first_sentence + '.' if not first_sentence.endswith('.') else first_sentence
                added_page_desc += 1
        
        # Add images structure
        add_images_structure(item_data, item_id, item_data.get('name', item_id), 'compounds')
        added_images += 1
    
    with open(filepath, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"✅ Removed 'description' field from {removed_description} compounds")
    print(f"✅ Added page_description to {added_page_desc} compounds")
    print(f"✅ Added images structure to {added_images} compounds")


def fix_settings():
    """Fix Settings.yaml - add images."""
    print("\n" + "=" * 80)
    print("FIXING SETTINGS")
    print("=" * 80)
    
    filepath = Path('data/settings/Settings.yaml')
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    
    added_images = 0
    
    for item_id, item_data in data['settings'].items():
        # Add images structure
        add_images_structure(item_data, item_id, item_data.get('name', item_id), 'settings')
        added_images += 1
    
    with open(filepath, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"✅ Added images structure to {added_images} settings")


if __name__ == '__main__':
    print("=" * 80)
    print("FRONTEND SPEC 5.0.0 COMPLIANCE FIX")
    print("=" * 80)
    print("\nUpdating source data files per BACKEND_FRONTMATTER_SPEC.md")
    print("Reference: docs/BACKEND_FRONTMATTER_SPEC.md")
    
    fix_materials()
    fix_contaminants()
    fix_compounds()
    fix_settings()
    
    print("\n" + "=" * 80)
    print("✅ ALL SOURCE DATA UPDATED")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Re-export all domains: for d in materials contaminants compounds settings; do python3 run.py --export --domain $d; done")
    print("2. Verify compliance: python3 scripts/tools/verify_frontmatter_compliance.py")
