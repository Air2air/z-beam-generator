#!/usr/bin/env python3
"""
Repopulate contaminant→material relationships using ONLY valid material IDs.

Strategy:
1. Load all 153 actual material IDs from Materials.yaml
2. Intelligently map contamination patterns to materials based on:
   - Material categories (metals, ceramics, composites, etc.)
   - Contamination type characteristics
   - Industry context and environmental conditions
3. Target: 90%+ coverage with average 5-10 material links per pattern
"""

import yaml
from pathlib import Path
from typing import Dict, List, Set

# Material categorization for intelligent matching
MATERIAL_CATEGORIES = {
    'metals_ferrous': [
        'steel', 'iron', 'cast-iron', 'stainless-steel', 'carbon-steel'
    ],
    'metals_nonferrous': [
        'aluminum', 'copper', 'brass', 'bronze', 'titanium', 'nickel', 'zinc', 'magnesium'
    ],
    'metals_precious': [
        'gold', 'silver', 'platinum'
    ],
    'ceramics': [
        'ceramic', 'porcelain', 'terracotta', 'tile', 'brick'
    ],
    'stone': [
        'granite', 'marble', 'limestone', 'sandstone', 'slate', 'concrete'
    ],
    'glass': [
        'glass', 'crystal'
    ],
    'composites': [
        'composite', 'carbon-fiber', 'fiberglass'
    ],
    'coated': [
        'coated', 'painted', 'anodized', 'galvanized', 'plated'
    ]
}

# Contamination pattern to material category mappings
CONTAMINATION_MAPPINGS = {
    # Oxidation & Rust
    'rust': ['metals_ferrous'],
    'oxidation': ['metals_ferrous', 'metals_nonferrous'],
    'tarnish': ['metals_nonferrous', 'metals_precious'],
    'corrosion': ['metals_ferrous', 'metals_nonferrous'],
    'patina': ['metals_nonferrous', 'metals_precious'],
    
    # Organic contamination
    'mold': ['stone', 'ceramics', 'glass', 'coated'],
    'algae': ['stone', 'ceramics', 'glass', 'coated'],
    'fungus': ['stone', 'ceramics', 'coated'],
    'biological': ['stone', 'ceramics', 'glass', 'coated', 'composites'],
    'organic': ['metals_ferrous', 'metals_nonferrous', 'stone', 'ceramics', 'glass', 'coated'],
    
    # Industrial contamination
    'grease': ['metals_ferrous', 'metals_nonferrous', 'composites'],
    'oil': ['metals_ferrous', 'metals_nonferrous', 'stone', 'composites'],
    'lubricant': ['metals_ferrous', 'metals_nonferrous', 'composites'],
    'hydraulic': ['metals_ferrous', 'metals_nonferrous'],
    
    # Particulate
    'dust': ['metals_ferrous', 'metals_nonferrous', 'stone', 'ceramics', 'glass', 'coated', 'composites'],
    'dirt': ['metals_ferrous', 'metals_nonferrous', 'stone', 'ceramics', 'glass', 'coated', 'composites'],
    'soot': ['metals_ferrous', 'metals_nonferrous', 'stone', 'ceramics', 'glass', 'coated'],
    'carbon': ['metals_ferrous', 'metals_nonferrous', 'stone', 'ceramics'],
    
    # Chemical
    'scale': ['metals_ferrous', 'metals_nonferrous', 'stone', 'glass'],
    'salt': ['metals_ferrous', 'metals_nonferrous', 'stone', 'ceramics', 'glass'],
    'mineral': ['metals_ferrous', 'metals_nonferrous', 'stone', 'glass'],
    'efflorescence': ['stone', 'ceramics'],
    
    # Paint & Coatings
    'paint': ['metals_ferrous', 'metals_nonferrous', 'stone', 'ceramics', 'composites', 'coated'],
    'coating': ['metals_ferrous', 'metals_nonferrous', 'stone', 'ceramics', 'composites', 'coated'],
    'epoxy': ['metals_ferrous', 'metals_nonferrous', 'composites', 'coated'],
    
    # Weathering
    'weather': ['metals_ferrous', 'metals_nonferrous', 'stone', 'ceramics', 'coated', 'composites'],
    'aging': ['metals_ferrous', 'metals_nonferrous', 'stone', 'ceramics', 'coated', 'composites'],
}


def load_materials() -> Dict[str, Dict]:
    """Load all materials from Materials.yaml."""
    materials_path = Path('data/materials/Materials.yaml')
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data['materials']


def load_contaminants() -> Dict[str, Dict]:
    """Load all contamination patterns from Contaminants.yaml."""
    contaminants_path = Path('data/contaminants/Contaminants.yaml')
    with open(contaminants_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data['contamination_patterns']


def categorize_material(material_id: str) -> List[str]:
    """Determine which categories a material belongs to."""
    categories = []
    material_lower = material_id.lower()
    
    for category, keywords in MATERIAL_CATEGORIES.items():
        if any(keyword in material_lower for keyword in keywords):
            categories.append(category)
    
    return categories if categories else ['other']


def match_pattern_to_materials(pattern_id: str, pattern_name: str, all_materials: Dict[str, Dict]) -> List[str]:
    """Intelligently match a contamination pattern to appropriate materials."""
    pattern_lower = pattern_name.lower()
    pattern_id_lower = pattern_id.lower()
    
    # Find applicable material categories based on contamination keywords
    target_categories = set()
    for keyword, categories in CONTAMINATION_MAPPINGS.items():
        if keyword in pattern_lower or keyword in pattern_id_lower:
            target_categories.update(categories)
    
    # If no specific mapping, apply to common industrial materials
    if not target_categories:
        target_categories = {'metals_ferrous', 'metals_nonferrous', 'stone', 'ceramics'}
    
    # Match materials to categories
    matched_materials = []
    for material_id in all_materials.keys():
        material_categories = categorize_material(material_id)
        if any(cat in target_categories for cat in material_categories):
            matched_materials.append(material_id)
    
    return matched_materials


def repopulate_contaminant_materials():
    """Repopulate found_on_materials for all contamination patterns."""
    print("Loading materials and contaminants...")
    materials = load_materials()
    contaminants = load_contaminants()
    
    print(f"\nFound {len(materials)} materials")
    print(f"Found {len(contaminants)} contamination patterns")
    
    # Statistics
    patterns_updated = 0
    total_links_added = 0
    patterns_already_populated = 0
    
    print("\n" + "="*80)
    print("REPOPULATING CONTAMINANT → MATERIAL RELATIONSHIPS")
    print("="*80)
    
    for pattern_id, pattern_data in contaminants.items():
        pattern_name = pattern_data.get('name', pattern_id)
        
        # Get current relationships
        relationships = pattern_data.setdefault('relationships', {})
        current_materials = relationships.get('found_on_materials', [])
        
        if len(current_materials) >= 5:
            # Already well-populated
            patterns_already_populated += 1
            continue
        
        # Find matching materials
        matched_materials = match_pattern_to_materials(pattern_id, pattern_name, materials)
        
        if matched_materials:
            # Convert to minimal reference format
            new_materials = [{'id': mat_id} for mat_id in matched_materials]
            relationships['found_on_materials'] = new_materials
            
            patterns_updated += 1
            total_links_added += len(new_materials)
            
            print(f"\n✅ {pattern_name}")
            print(f"   Pattern: {pattern_id}")
            print(f"   Materials: {len(new_materials)} matched")
            if len(new_materials) <= 10:
                print(f"   IDs: {', '.join(matched_materials[:10])}")
            else:
                print(f"   IDs: {', '.join(matched_materials[:10])} ... (+{len(new_materials)-10} more)")
    
    # Save updated data
    print("\n" + "="*80)
    print("SAVING UPDATED DATA")
    print("="*80)
    
    output_path = Path('data/contaminants/Contaminants.yaml')
    backup_path = output_path.with_suffix('.yaml.backup_repopulated')
    
    # Create backup
    if output_path.exists():
        with open(output_path, 'r', encoding='utf-8') as f:
            backup_data = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(backup_data)
        print(f"✅ Backup created: {backup_path}")
    
    # Save updated data
    output_data = {'contamination_patterns': contaminants}
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(output_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)
    
    print(f"✅ Updated data saved: {output_path}")
    
    # Final statistics
    print("\n" + "="*80)
    print("REPOPULATION COMPLETE")
    print("="*80)
    print(f"Patterns updated: {patterns_updated}")
    print(f"Patterns already populated: {patterns_already_populated}")
    print(f"Total material links added: {total_links_added}")
    print(f"Average links per updated pattern: {total_links_added/patterns_updated:.1f}" if patterns_updated > 0 else "N/A")
    
    # Check final coverage
    patterns_with_materials = sum(1 for p in contaminants.values() if p.get('relationships', {}).get('found_on_materials'))
    coverage = patterns_with_materials / len(contaminants) * 100
    
    print(f"\nFinal coverage: {patterns_with_materials}/{len(contaminants)} patterns ({coverage:.1f}%)")
    
    total_material_links = sum(len(p.get('relationships', {}).get('found_on_materials', [])) for p in contaminants.values())
    avg_links = total_material_links / len(contaminants)
    print(f"Total material links: {total_material_links}")
    print(f"Average links per pattern: {avg_links:.1f}")


if __name__ == '__main__':
    repopulate_contaminant_materials()
