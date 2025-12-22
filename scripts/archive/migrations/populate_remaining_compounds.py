#!/usr/bin/env python3
"""
Populate remaining compound relationships by analyzing:
1. Reverse relationships (which contaminants produce this compound?)
2. Material context (which materials produce contamination that creates this compound?)
3. Chemical relationships (oxide compounds from metal materials, organic compounds from coatings)
"""

import yaml
from pathlib import Path
from typing import Dict, List, Set

# Compound to material mappings based on chemistry
COMPOUND_MATERIAL_MAPPINGS = {
    # Metal oxides from their base metals
    'aluminum-oxide': ['aluminum', 'brass', 'bronze'],
    'iron-oxide': ['iron', 'steel', 'stainless-steel', 'cast-iron'],
    'copper-oxide': ['copper', 'brass', 'bronze'],
    'zinc-oxide': ['zinc', 'brass', 'galvanized'],
    'chromium-oxide': ['stainless-steel', 'chromium'],
    'chromium-vi': ['stainless-steel', 'chromium', 'plated'],
    'nickel-oxide': ['nickel', 'stainless-steel'],
    'tin-oxide': ['tin', 'bronze'],
    'lead-oxide': ['lead', 'bronze'],
    'cadmium-oxide': ['cadmium', 'plated'],
    'titanium-oxide': ['titanium'],
    'magnesium-oxide': ['magnesium'],
    
    # Organic compounds from coatings/paints
    'formaldehyde': ['painted', 'coated', 'epoxy', 'composite'],
    'acetaldehyde': ['painted', 'coated', 'epoxy', 'composite'],
    'acrolein': ['painted', 'coated', 'epoxy', 'composite'],
    'toluene': ['painted', 'coated', 'epoxy', 'composite'],
    'styrene': ['painted', 'coated', 'composite', 'fiberglass'],
    'benzene': ['painted', 'coated', 'epoxy', 'composite'],
    
    # Chlorinated compounds
    'hydrogen-chloride': ['pvc', 'painted', 'coated'],
    'phosgene': ['painted', 'coated'],
    'vinyl-chloride': ['pvc', 'painted'],
    
    # Nitrogen compounds
    'ammonia': ['painted', 'coated'],
    'hydrogen-cyanide': ['painted', 'coated', 'composite'],
    'nitrogen-dioxide': ['steel', 'stainless-steel', 'iron'],
    
    # Sulfur compounds
    'sulfur-dioxide': ['steel', 'iron', 'cast-iron', 'rubber'],
    'hydrogen-sulfide': ['rubber', 'steel', 'iron'],
    
    # Carbon compounds
    'carbon-monoxide': ['steel', 'iron', 'cast-iron', 'aluminum', 'copper'],
    'carbon-dioxide': ['steel', 'iron', 'cast-iron', 'aluminum', 'copper'],
}


def load_yaml(path: Path) -> Dict:
    """Load YAML file."""
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_yaml(path: Path, data: Dict):
    """Save YAML file."""
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)


def find_materials_by_keyword(materials: Dict, keywords: List[str]) -> List[str]:
    """Find material IDs that match any of the keywords."""
    matched = []
    for material_id in materials.keys():
        material_lower = material_id.lower()
        if any(keyword in material_lower for keyword in keywords):
            matched.append(material_id)
    return matched


def find_contaminants_producing_compound(contaminants: Dict, compound_id: str) -> List[str]:
    """Find contaminants that produce this compound."""
    producing = []
    for contam_id, contam_data in contaminants.items():
        produces = contam_data.get('relationships', {}).get('produces_compounds', [])
        compound_ids = [rel['id'] if isinstance(rel, dict) else rel for rel in produces]
        if f"{compound_id}-compound" in compound_ids:
            producing.append(contam_id)
    return producing


def populate_compound_relationships():
    """Populate relationships for under-populated compounds."""
    print("Loading data files...")
    compounds_data = load_yaml(Path('data/compounds/Compounds.yaml'))
    materials_data = load_yaml(Path('data/materials/Materials.yaml'))
    contaminants_data = load_yaml(Path('data/contaminants/Contaminants.yaml'))
    
    compounds = compounds_data['compounds']
    materials = materials_data['materials']
    contaminants = contaminants_data['contamination_patterns']
    
    print(f"\nFound {len(compounds)} compounds")
    print(f"Found {len(materials)} materials")
    print(f"Found {len(contaminants)} contaminants")
    
    updates_made = 0
    total_links_added = 0
    
    print("\n" + "="*80)
    print("POPULATING COMPOUND RELATIONSHIPS")
    print("="*80)
    
    for compound_id, compound_data in compounds.items():
        name = compound_data.get('name', compound_id)
        relationships = compound_data.setdefault('relationships', {})
        
        current_materials = relationships.get('produced_from_materials', [])
        current_contaminants = relationships.get('produced_from_contaminants', [])
        
        current_total = len(current_materials) + len(current_contaminants)
        
        # Skip if already well-populated (5+ links)
        if current_total >= 5:
            continue
        
        print(f"\n🔍 {name} ({compound_id})")
        print(f"   Current: {len(current_materials)} materials, {len(current_contaminants)} contaminants")
        
        new_materials = set()
        new_contaminants = set()
        
        # Strategy 1: Find contaminants that produce this compound
        producing_contaminants = find_contaminants_producing_compound(contaminants, compound_id)
        if producing_contaminants:
            print(f"   Found {len(producing_contaminants)} contaminants that produce this compound")
            new_contaminants.update(producing_contaminants)
        
        # Strategy 2: Use chemistry-based material mappings
        if compound_id in COMPOUND_MATERIAL_MAPPINGS:
            keywords = COMPOUND_MATERIAL_MAPPINGS[compound_id]
            matched_materials = find_materials_by_keyword(materials, keywords)
            if matched_materials:
                print(f"   Matched {len(matched_materials)} materials by chemistry")
                new_materials.update(matched_materials)
        
        # Convert existing to IDs for comparison
        current_material_ids = {rel['id'] if isinstance(rel, dict) else rel for rel in current_materials}
        current_contaminant_ids = {rel['id'] if isinstance(rel, dict) else rel for rel in current_contaminants}
        
        # Add only new materials
        new_material_ids = new_materials - current_material_ids
        new_contaminant_ids = new_contaminants - current_contaminant_ids
        
        if new_material_ids or new_contaminant_ids:
            # Add new materials
            if new_material_ids:
                relationships['produced_from_materials'] = current_materials + [
                    {'id': mat_id} for mat_id in sorted(new_material_ids)
                ]
                print(f"   ✅ Added {len(new_material_ids)} new materials")
            
            # Add new contaminants
            if new_contaminant_ids:
                relationships['produced_from_contaminants'] = current_contaminants + [
                    {'id': cont_id} for cont_id in sorted(new_contaminant_ids)
                ]
                print(f"   ✅ Added {len(new_contaminant_ids)} new contaminants")
            
            updates_made += 1
            total_links_added += len(new_material_ids) + len(new_contaminant_ids)
            
            new_total = len(relationships['produced_from_materials']) + len(relationships['produced_from_contaminants'])
            print(f"   📊 Total links: {current_total} → {new_total}")
        else:
            print(f"   ℹ️  No new relationships found")
    
    # Save updated data
    print("\n" + "="*80)
    print("SAVING UPDATED DATA")
    print("="*80)
    
    output_path = Path('data/compounds/Compounds.yaml')
    backup_path = output_path.with_suffix('.yaml.backup_populated')
    
    # Create backup
    if output_path.exists():
        with open(output_path, 'r', encoding='utf-8') as f:
            backup_data = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(backup_data)
        print(f"✅ Backup created: {backup_path}")
    
    # Save updated data
    save_yaml(output_path, compounds_data)
    print(f"✅ Updated data saved: {output_path}")
    
    # Final statistics
    print("\n" + "="*80)
    print("POPULATION COMPLETE")
    print("="*80)
    print(f"Compounds updated: {updates_made}")
    print(f"Total links added: {total_links_added}")
    
    # Check final coverage
    under_populated = sum(1 for c in compounds.values() 
                         if len(c.get('relationships', {}).get('produced_from_materials', [])) + 
                            len(c.get('relationships', {}).get('produced_from_contaminants', [])) < 5)
    
    coverage = (len(compounds) - under_populated) / len(compounds) * 100
    print(f"\nFinal coverage: {len(compounds) - under_populated}/{len(compounds)} compounds well-populated ({coverage:.1f}%)")
    print(f"Under-populated compounds remaining: {under_populated}")


if __name__ == '__main__':
    populate_compound_relationships()
