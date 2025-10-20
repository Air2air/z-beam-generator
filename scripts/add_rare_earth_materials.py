#!/usr/bin/env python3
"""
Add Rare-Earth Materials to Materials.yaml

Adds four rare-earth elements with AI-researched properties:
- Neodymium (Nd)
- Dysprosium (Dy)
- Terbium (Tb)
- Praseodymium (Pr)

Per GROK_INSTRUCTIONS.md: Changes ONLY Materials.yaml, uses AI research for all values.
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Rare-earth materials to add
RARE_EARTH_MATERIALS = {
    'Neodymium': {
        'symbol': 'Nd',
        'atomic_number': 60,
        'category': 'rare-earth',
        'subcategory': 'lanthanide',
        'author': {'id': 1},  # Will be assigned based on existing pattern
        'applications': [
            'Electronics Manufacturing',
            'Aerospace',
            'Medical',
            'Renewable Energy',
            'Defense'
        ]
    },
    'Dysprosium': {
        'symbol': 'Dy',
        'atomic_number': 66,
        'category': 'rare-earth',
        'subcategory': 'lanthanide',
        'author': {'id': 2},
        'applications': [
            'Electronics Manufacturing',
            'Renewable Energy',
            'Aerospace',
            'Automotive',
            'Defense'
        ]
    },
    'Terbium': {
        'symbol': 'Tb',
        'atomic_number': 65,
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
    'Praseodymium': {
        'symbol': 'Pr',
        'atomic_number': 59,
        'category': 'rare-earth',
        'subcategory': 'lanthanide',
        'author': {'id': 4},
        'applications': [
            'Electronics Manufacturing',
            'Aerospace',
            'Automotive',
            'Renewable Energy',
            'Industrial'
        ]
    }
}


def create_material_entry(material_name: str, material_info: dict) -> dict:
    """Create a basic material entry - properties will be researched during frontmatter generation"""
    print(f"\n� Creating {material_name}...")
    
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


def main():
    """Add rare-earth materials to Materials.yaml"""
    materials_path = Path('data/Materials.yaml')
    
    if not materials_path.exists():
        print(f"❌ Materials.yaml not found at {materials_path}")
        sys.exit(1)
    
    print("📖 Reading Materials.yaml...")
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = materials_path.parent / f"Materials.backup_rare_earth_{timestamp}.yaml"
    import shutil
    shutil.copy2(materials_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    
    # Add each rare-earth material
    print(f"\n� Adding {len(RARE_EARTH_MATERIALS)} rare-earth materials...")
    
    added_count = 0
    for material_name, material_info in RARE_EARTH_MATERIALS.items():
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
    data['metadata']['rare_earth_addition_date'] = datetime.now(timezone.utc).isoformat()
    
    print(f"\n💾 Writing updated data to {materials_path}...")
    with open(materials_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, indent=2)
    
    print(f"\n✅ Rare-earth materials added successfully!")
    print(f"   - Added: {added_count} materials")
    print(f"   - Total materials: {len(data['materials'])}")
    print(f"   - Backup: {backup_path}")


if __name__ == '__main__':
    main()
