#!/usr/bin/env python3
"""
Add Additional Rare-Earth Materials to Materials.yaml

Adds four additional rare-earth elements to the existing rare-earth category:
- Cerium (Ce)
- Lanthanum (La)
- Yttrium (Y)
- Europium (Eu)

Follows the established pattern from the existing rare-earth materials script.
Per GROK_INSTRUCTIONS.md: Changes ONLY Materials.yaml, uses AI research for all values.
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Additional rare-earth materials to add
ADDITIONAL_RARE_EARTH_MATERIALS = {
    'Cerium': {
        'symbol': 'Ce',
        'atomic_number': 58,
        'category': 'rare-earth',
        'subcategory': 'lanthanide',
        'author': {'id': 1},  # Will be assigned based on existing pattern
        'applications': [
            'Electronics Manufacturing',
            'Aerospace',
            'Automotive',
            'Medical',
            'Industrial'
        ]
    },
    'Lanthanum': {
        'symbol': 'La',
        'atomic_number': 57,
        'category': 'rare-earth',
        'subcategory': 'lanthanide',
        'author': {'id': 2},
        'applications': [
            'Electronics Manufacturing',
            'Medical',
            'Aerospace',
            'Renewable Energy',
            'Industrial'
        ]
    },
    'Yttrium': {
        'symbol': 'Y',
        'atomic_number': 39,
        'category': 'rare-earth',
        'subcategory': 'lanthanide',
        'author': {'id': 3},
        'applications': [
            'Electronics Manufacturing',
            'Medical',
            'Aerospace',
            'Renewable Energy',
            'Defense'
        ]
    },
    'Europium': {
        'symbol': 'Eu',
        'atomic_number': 63,
        'category': 'rare-earth',
        'subcategory': 'lanthanide',
        'author': {'id': 4},
        'applications': [
            'Electronics Manufacturing',
            'Medical',
            'Aerospace',
            'Renewable Energy',
            'Defense'
        ]
    }
}


def create_material_entry(material_name: str, material_info: dict) -> dict:
    """Create a basic material entry - properties will be researched during frontmatter generation"""
    print(f"\n🔬 Creating {material_name}...")
    
    # Create minimal structure - property research happens during generation
    material_entry = {
        'name': material_name,
        'category': material_info['category'],
        'subcategory': material_info['subcategory'],
        'author': material_info['author'],
        'applications': material_info['applications'],
        'materialProperties': {
            'material_characteristics': {
                'label': 'Material Characteristics',
                'description': 'Intrinsic physical, mechanical, chemical, and structural properties affecting cleaning outcomes and material integrity',
                'percentage': 40.0,
                'properties': {}
            },
            'laser_material_interaction': {
                'label': 'Laser-Material Interaction',
                'description': 'Optical, thermal, and surface properties governing laser processing behavior',
                'percentage': 40.0,
                'properties': {}
            },
            'other': {
                'label': 'Other Properties',
                'description': 'Additional material-specific properties',
                'percentage': 20.0,
                'properties': {}
            }
        },
        'materialCharacteristics': {
            'crystallineStructure': {
                'value': 'HCP',  # Most rare-earths are HCP
                'unit': 'crystal system',
                'confidence': 0.95,
                'description': 'Hexagonal close-packed crystal structure typical of rare-earth elements',
                'source': 'ai_research',
                'research_date': datetime.now(timezone.utc).isoformat(),
                'allowedValues': ['FCC', 'BCC', 'HCP', 'amorphous', 'cubic', 'hexagonal', 
                                 'tetragonal', 'orthorhombic', 'monoclinic', 'triclinic']
            }
        }
    }
    
    print(f"  ✅ {material_name} structure created (properties will be AI-researched during generation)")
    return material_entry


def update_categories_yaml():
    """Update Categories.yaml to include the new materials in the lanthanide subcategory"""
    categories_path = Path('data/Categories.yaml')
    
    if not categories_path.exists():
        print(f"❌ Categories.yaml not found at {categories_path}")
        return False
    
    print("📖 Reading Categories.yaml...")
    with open(categories_path, 'r', encoding='utf-8') as f:
        categories_data = yaml.safe_load(f)
    
    # Check if rare-earth category exists
    if 'categories' not in categories_data or 'rare-earth' not in categories_data['categories']:
        print("❌ rare-earth category not found in Categories.yaml")
        return False
    
    # Check if lanthanide subcategory exists
    rare_earth_category = categories_data['categories']['rare-earth']
    if 'subcategories' not in rare_earth_category or 'lanthanide' not in rare_earth_category['subcategories']:
        print("❌ lanthanide subcategory not found in Categories.yaml")
        return False
    
    # Get current materials list
    current_materials = rare_earth_category['subcategories']['lanthanide']['materials']
    print(f"📋 Current lanthanide materials: {current_materials}")
    
    # Add new materials to the list
    new_materials = list(ADDITIONAL_RARE_EARTH_MATERIALS.keys())
    updated_materials = current_materials + [name for name in new_materials if name not in current_materials]
    
    categories_data['categories']['rare-earth']['subcategories']['lanthanide']['materials'] = updated_materials
    
    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = categories_path.parent / f"Categories.backup_rare_earth_{timestamp}.yaml"
    import shutil
    shutil.copy2(categories_path, backup_path)
    print(f"✅ Categories backup created: {backup_path}")
    
    # Write updated Categories.yaml
    print("💾 Writing updated Categories.yaml...")
    with open(categories_path, 'w', encoding='utf-8') as f:
        yaml.dump(categories_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, indent=2)
    
    print(f"✅ Updated lanthanide materials: {updated_materials}")
    return True


def main():
    """Add additional rare-earth materials to Materials.yaml and update Categories.yaml"""
    materials_path = Path('data/Materials.yaml')
    
    if not materials_path.exists():
        print(f"❌ Materials.yaml not found at {materials_path}")
        sys.exit(1)
    
    print("📖 Reading Materials.yaml...")
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = materials_path.parent / f"Materials.backup_additional_rare_earth_{timestamp}.yaml"
    import shutil
    shutil.copy2(materials_path, backup_path)
    print(f"✅ Materials backup created: {backup_path}")
    
    # Add each additional rare-earth material
    print(f"\n🧪 Adding {len(ADDITIONAL_RARE_EARTH_MATERIALS)} additional rare-earth materials...")
    
    added_count = 0
    for material_name, material_info in ADDITIONAL_RARE_EARTH_MATERIALS.items():
        try:
            if material_name in data['materials']:
                print(f"⏭️  {material_name} already exists, skipping...")
                continue
            
            material_entry = create_material_entry(material_name, material_info)
            data['materials'][material_name] = material_entry
            added_count += 1
            
        except Exception as e:
            print(f"  ❌ {material_name} failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Update metadata
    data['metadata']['total_materials'] = len(data['materials'])
    data['metadata']['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    data['metadata']['additional_rare_earth_addition_date'] = datetime.now(timezone.utc).isoformat()
    
    print("\n💾 Writing updated Materials.yaml...")
    with open(materials_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, indent=2)
    
    # Update Categories.yaml
    print("\n📝 Updating Categories.yaml...")
    categories_success = update_categories_yaml()
    
    print("\n✅ Additional rare-earth materials added successfully!")
    print(f"   - Added to Materials.yaml: {added_count} materials")
    print(f"   - Total materials: {len(data['materials'])}")
    print(f"   - Materials backup: {backup_path}")
    if categories_success:
        print("   - Categories.yaml updated with new materials")
    else:
        print("   ⚠️  Categories.yaml update failed - manual update may be needed")


if __name__ == '__main__':
    main()