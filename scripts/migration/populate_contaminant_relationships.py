#!/usr/bin/env python3
"""
Populate contaminant relationship data

Intelligently populates:
- produces_compounds: Match byproducts to compound IDs
- found_on_materials: Match contamination names/categories to materials
"""

import yaml
from pathlib import Path
from datetime import datetime
import shutil
import re

def load_data():
    """Load all data files."""
    with open('data/materials/Materials.yaml', 'r', encoding='utf-8') as f:
        materials = yaml.safe_load(f)
    
    with open('data/compounds/Compounds.yaml', 'r', encoding='utf-8') as f:
        compounds = yaml.safe_load(f)
    
    with open('data/contaminants/Contaminants.yaml', 'r', encoding='utf-8') as f:
        contaminants = yaml.safe_load(f)
    
    return materials, compounds, contaminants

def extract_material_slug(material_id):
    """Extract base material slug from full ID."""
    # aluminum-laser-cleaning → aluminum
    return material_id.replace('-laser-cleaning', '')

def match_byproducts_to_compounds(byproducts, compound_ids):
    """Match byproduct compounds to compound IDs."""
    matches = []
    
    for byproduct in byproducts:
        compound_name = byproduct.get('compound', '')
        
        # Direct match
        if compound_name in compound_ids:
            matches.append({
                'id': compound_name,
                'phase': byproduct.get('phase', 'unknown'),
                'hazard_level': byproduct.get('hazard_level', 'unknown')
            })
    
    return matches

def match_contamination_to_materials(pattern_id, pattern_data, material_slugs):
    """Match contamination pattern to materials it's found on."""
    matches = []
    
    # Extract key terms from pattern ID
    pattern_lower = pattern_id.lower()
    
    # Material-specific contamination (e.g., aluminum-oxidation, copper-tarnish)
    for slug in material_slugs:
        if slug in pattern_lower:
            matches.append({
                'id': f"{slug}-laser-cleaning",
                'frequency': 'very_common'
            })
    
    # Category-based matching
    category = pattern_data.get('category', '').lower()
    
    # Rust/oxidation → metals
    if 'rust' in pattern_lower or 'oxidation' in pattern_lower or 'corrosion' in pattern_lower:
        metal_materials = [
            'steel', 'iron', 'stainless-steel-316', 'aluminum', 'copper',
            'brass', 'bronze', 'titanium', 'zinc', 'nickel'
        ]
        for metal in metal_materials:
            material_id = f"{metal}-laser-cleaning"
            if material_id not in [m['id'] for m in matches]:
                freq = 'very_common' if metal in ['steel', 'iron', 'aluminum'] else 'common'
                matches.append({'id': material_id, 'frequency': freq})
    
    # Paint → many materials
    if 'paint' in pattern_lower:
        paint_materials = ['steel', 'aluminum', 'wood', 'concrete', 'plastic']
        for mat in paint_materials:
            matches.append({
                'id': f"{mat}-laser-cleaning",
                'frequency': 'common'
            })
    
    # Oil/grease → metals and some non-metals
    if 'oil' in pattern_lower or 'grease' in pattern_lower:
        oil_materials = ['steel', 'aluminum', 'brass', 'bronze', 'copper']
        for mat in oil_materials:
            matches.append({
                'id': f"{mat}-laser-cleaning",
                'frequency': 'very_common'
            })
    
    # Biological → organics
    if category == 'biological':
        bio_materials = ['wood', 'leather', 'paper', 'fabric']
        for mat in bio_materials:
            matches.append({
                'id': f"{mat}-laser-cleaning",
                'frequency': 'common'
            })
    
    # Remove duplicates
    seen = set()
    unique_matches = []
    for match in matches:
        if match['id'] not in seen:
            seen.add(match['id'])
            unique_matches.append(match)
    
    return unique_matches

def populate_contaminant_relationships():
    """Populate produces_compounds and found_on_materials for all contaminants."""
    
    print("🔄 Loading data...")
    materials, compounds, contaminants = load_data()
    
    material_ids = list(materials['materials'].keys())
    material_slugs = [extract_material_slug(mid) for mid in material_ids]
    compound_ids = list(compounds['compounds'].keys())
    
    print(f"✅ Loaded {len(material_ids)} materials, {len(compound_ids)} compounds")
    
    # Backup
    contaminants_path = Path("data/contaminants/Contaminants.yaml")
    backup_path = contaminants_path.with_suffix(f'.yaml.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    shutil.copy2(contaminants_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    
    # Process each contamination pattern
    patterns = contaminants['contamination_patterns']
    compounds_added = 0
    materials_added = 0
    
    for pattern_id, pattern_data in patterns.items():
        relationships = pattern_data.get('relationships', {})
        
        # Populate produces_compounds from byproducts
        if 'laser_properties' in pattern_data:
            laser_props = pattern_data['laser_properties']
            if 'removal_characteristics' in laser_props:
                removal = laser_props['removal_characteristics']
                if 'byproducts' in removal and removal['byproducts']:
                    compound_matches = match_byproducts_to_compounds(
                        removal['byproducts'],
                        compound_ids
                    )
                    if compound_matches:
                        relationships['produces_compounds'] = compound_matches
                        compounds_added += len(compound_matches)
        
        # Populate found_on_materials based on contamination type
        material_matches = match_contamination_to_materials(
            pattern_id,
            pattern_data,
            material_slugs
        )
        if material_matches:
            relationships['found_on_materials'] = material_matches
            materials_added += len(material_matches)
        
        pattern_data['relationships'] = relationships
    
    # Save
    with open(contaminants_path, 'w', encoding='utf-8') as f:
        yaml.dump(contaminants, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
    
    print(f"\n✅ Population complete:")
    print(f"   • {compounds_added} compound relationships added")
    print(f"   • {materials_added} material relationships added")
    print(f"   • Processed {len(patterns)} contamination patterns")
    
    # Summary stats
    patterns_with_compounds = sum(1 for p in patterns.values() 
                                  if p.get('relationships', {}).get('produces_compounds'))
    patterns_with_materials = sum(1 for p in patterns.values() 
                                  if p.get('relationships', {}).get('found_on_materials'))
    
    print(f"\n📊 Coverage:")
    print(f"   • Patterns with compound links: {patterns_with_compounds}/{len(patterns)} ({patterns_with_compounds/len(patterns)*100:.1f}%)")
    print(f"   • Patterns with material links: {patterns_with_materials}/{len(patterns)} ({patterns_with_materials/len(patterns)*100:.1f}%)")

if __name__ == "__main__":
    populate_contaminant_relationships()
