#!/usr/bin/env python3
"""
Materials.yaml Organization Optimizer

Implements the recommended optimizations:
1. Reorganize metal category into logical subcategories
2. Merge stone and masonry categories 
3. Reorder sections for better logical flow
4. Improve category balance

Preserves all data while optimizing structure.
"""

import yaml
import shutil
from pathlib import Path
from datetime import datetime

def create_backup(file_path):
    """Create timestamped backup of original file."""
    timestamp = int(datetime.now().timestamp())
    backup_path = f"{file_path}_organization_backup_{timestamp}.yaml"
    shutil.copy2(file_path, backup_path)
    return backup_path

def reorganize_metals(metal_items):
    """Split metals into logical subcategories."""
    
    # Define metal classifications
    pure_metals = {
        'Aluminum', 'Beryllium', 'Cadmium', 'Chromium', 'Cobalt', 'Copper', 
        'Gallium', 'Hafnium', 'Indium', 'Iron', 'Lead', 'Magnesium', 
        'Manganese', 'Mercury', 'Molybdenum', 'Nickel', 'Niobium', 'Osmium',
        'Palladium', 'Rhenium', 'Rhodium', 'Tantalum', 'Thallium', 'Tin', 
        'Titanium', 'Tungsten', 'Vanadium', 'Yttrium', 'Zinc', 'Zirconium'
    }
    
    precious_metals = {
        'Gold', 'Silver', 'Platinum', 'Palladium', 'Rhodium', 'Ruthenium', 'Iridium'
    }
    
    alloys = {
        'Brass', 'Bronze', 'Hastelloy', 'Inconel', 'Steel', 'Stainless Steel'
    }
    
    # Categorize metals
    categorized = {
        'pure_metals': {'description': 'Pure metallic elements', 'items': []},
        'precious_metals': {'description': 'Noble and precious metals', 'items': []},
        'alloys': {'description': 'Metal alloys and compositions', 'items': []}
    }
    
    for item in metal_items:
        name = item.get('name', '')
        if name in precious_metals:
            categorized['precious_metals']['items'].append(item)
        elif name in alloys:
            categorized['alloys']['items'].append(item)
        elif name in pure_metals:
            categorized['pure_metals']['items'].append(item)
        else:
            # Default to pure metals for unclassified
            categorized['pure_metals']['items'].append(item)
    
    return categorized

def merge_stone_masonry(stone_items, masonry_items):
    """Merge stone and masonry into mineral_materials category."""
    
    # Classify items
    natural_stones = []
    construction_materials = []
    
    # Stone items are mostly natural
    for item in stone_items:
        natural_stones.append(item)
    
    # Masonry items are mostly construction
    for item in masonry_items:
        construction_materials.append(item)
    
    # Some overlap handling - move manufactured stones to construction
    construction_names = {'Concrete', 'Cement', 'Mortar', 'Plaster', 'Stucco', 'Brick', 'Terracotta'}
    
    # Move any construction materials from natural stones
    final_natural = []
    for item in natural_stones:
        if item.get('name', '') in construction_names:
            construction_materials.append(item)
        else:
            final_natural.append(item)
    
    return {
        'natural_stone': {
            'description': 'Natural stone and mineral materials',
            'items': final_natural
        },
        'construction_materials': {
            'description': 'Manufactured construction and masonry materials', 
            'items': construction_materials
        }
    }

def reorder_sections(data):
    """Reorder sections for optimal logical flow."""
    
    optimal_order = [
        'metadata',
        'category_ranges', 
        'parameter_templates',
        'defaults',
        'material_index',
        'materials'
    ]
    
    reordered = {}
    for section in optimal_order:
        if section in data:
            reordered[section] = data[section]
    
    # Add any sections we missed
    for section, content in data.items():
        if section not in reordered:
            reordered[section] = content
    
    return reordered

def optimize_organization():
    """Main optimization function."""
    
    materials_path = Path("data/materials.yaml")
    
    print("🔧 OPTIMIZING MATERIALS.YAML ORGANIZATION")
    print("=" * 50)
    print()
    
    # Create backup
    backup_path = create_backup(materials_path)
    print(f"📁 Backup created: {backup_path}")
    print()
    
    # Load current data
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    print("🏗️ Phase 1: Reorganizing metal categories...")
    
    # Extract and reorganize metals
    original_metals = data['materials']['metal']['items']
    reorganized_metals = reorganize_metals(original_metals)
    
    print(f"   ✅ Split {len(original_metals)} metals into:")
    for subcat, subdata in reorganized_metals.items():
        count = len(subdata['items'])
        print(f"      • {subcat}: {count} materials")
    
    print()
    print("🤝 Phase 2: Merging stone and masonry categories...")
    
    # Extract and merge stone/masonry
    stone_items = data['materials']['stone']['items']
    masonry_items = data['materials']['masonry']['items']
    merged_mineral = merge_stone_masonry(stone_items, masonry_items)
    
    print(f"   ✅ Merged {len(stone_items)} stones + {len(masonry_items)} masonry items into:")
    for subcat, subdata in merged_mineral.items():
        count = len(subdata['items'])
        print(f"      • {subcat}: {count} materials")
    
    print()
    print("📊 Phase 3: Rebuilding materials section...")
    
    # Rebuild materials section with optimized structure
    new_materials = {}
    
    # Add reorganized metals
    new_materials['metals'] = reorganized_metals
    
    # Add merged mineral materials
    new_materials['mineral_materials'] = merged_mineral
    
    # Add remaining categories unchanged
    remaining_categories = ['ceramic', 'composite', 'glass', 'semiconductor', 'wood']
    for category in remaining_categories:
        if category in data['materials']:
            new_materials[category] = {
                'description': f'{category.title()} materials',
                'items': data['materials'][category]['items']
            }
    
    # Update the data structure
    data['materials'] = new_materials
    
    print("   ✅ Materials section rebuilt with optimized categories")
    print()
    print("🔄 Phase 4: Reordering sections...")
    
    # Reorder sections
    data = reorder_sections(data)
    print("   ✅ Sections reordered for optimal logical flow")
    print()
    
    print("💾 Phase 5: Saving optimized structure...")
    
    # Save optimized data
    with open(materials_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print("   ✅ Optimized materials.yaml saved")
    print()
    
    # Generate summary
    print("📊 OPTIMIZATION SUMMARY")
    print("=" * 30)
    
    total_materials = 0
    for category, cat_data in new_materials.items():
        if isinstance(cat_data, dict) and 'items' in cat_data:
            count = len(cat_data['items'])
            total_materials += count
            print(f"📂 {category}: {count} materials")
        elif isinstance(cat_data, dict):
            # Subcategorized (like metals, mineral_materials)
            subcount = 0
            for subcat, subdata in cat_data.items():
                if isinstance(subdata, dict) and 'items' in subdata:
                    subcount += len(subdata['items'])
            total_materials += subcount
            print(f"📂 {category}: {subcount} materials (subcategorized)")
    
    print()
    print(f"📈 Total materials maintained: {total_materials}")
    print(f"📁 Backup preserved: {backup_path}")
    print()
    print("✅ ORGANIZATION OPTIMIZATION COMPLETE!")
    
    return backup_path

if __name__ == "__main__":
    optimize_organization()
