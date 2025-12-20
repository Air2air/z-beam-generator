#!/usr/bin/env python3
"""
Regenerate Domain Associations

Scans all data files and rebuilds DomainAssociations.yaml with:
- material → contaminant associations (from Contaminants.yaml valid_materials)
- contaminant → compound associations (from Contaminants.yaml byproducts)
- material → compound associations (indirect through contaminants)

Usage:
    python3 scripts/sync/regenerate_associations.py [--dry-run]
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Set, List, Tuple
from datetime import datetime
import yaml

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_yaml(filepath: Path) -> Dict:
    """Load YAML file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_yaml(filepath: Path, data: Dict) -> None:
    """Save YAML file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)


def get_material_contaminant_associations(
    materials_data: Dict,
    contaminants_data: Dict
) -> List[Dict]:
    """Get material → contaminant associations (bidirectional)"""
    associations = []
    patterns = contaminants_data.get('contamination_patterns', {})
    
    for pattern_id, pattern in patterns.items():
        valid_materials = pattern.get('valid_materials', [])
        
        for material_name in valid_materials:
            # Normalize material name (handle variations)
            material_id = material_name.lower().replace(' ', '-')
            
            # Forward: Material → Contaminant
            associations.append({
                'source_domain': 'materials',
                'source_id': material_id,
                'target_domain': 'contaminants',
                'target_id': pattern_id,
                'relationship_type': 'can_have_contamination'
            })
            
            # Reverse: Contaminant → Material
            associations.append({
                'source_domain': 'contaminants',
                'source_id': pattern_id,
                'target_domain': 'materials',
                'target_id': material_id,
                'relationship_type': 'can_contaminate'
            })
    
    return associations


def get_contaminant_compound_associations(
    contaminants_data: Dict,
    compounds_data: Dict
) -> List[Dict]:
    """Get contaminant → compound associations (bidirectional)"""
    associations = []
    patterns = contaminants_data.get('contamination_patterns', {})
    compound_ids = set(compounds_data.get('compounds', {}).keys())
    
    for pattern_id, pattern in patterns.items():
        byproducts = pattern.get('laser_properties', {}).get('removal_characteristics', {}).get('byproducts', [])
        
        for bp in byproducts:
            compound = bp.get('compound', '')
            
            # Only create association if compound exists in Compounds.yaml
            if compound in compound_ids:
                # Forward: Contaminant → Compound
                associations.append({
                    'source_domain': 'contaminants',
                    'source_id': pattern_id,
                    'target_domain': 'compounds',
                    'target_id': compound,
                    'relationship_type': 'generates_byproduct'
                })
                
                # Reverse: Compound → Contaminant
                associations.append({
                    'source_domain': 'compounds',
                    'source_id': compound,
                    'target_domain': 'contaminants',
                    'target_id': pattern_id,
                    'relationship_type': 'byproduct_of'
                })
    
    return associations


def deduplicate_associations(associations: List[Dict]) -> List[Dict]:
    """Remove duplicate associations"""
    seen = set()
    unique = []
    
    for assoc in associations:
        key = (
            assoc['source_domain'],
            assoc['source_id'],
            assoc['target_domain'],
            assoc['target_id'],
            assoc['relationship_type']
        )
        if key not in seen:
            seen.add(key)
            unique.append(assoc)
    
    return unique


def main():
    parser = argparse.ArgumentParser(description='Regenerate domain associations')
    parser.add_argument('--dry-run', action='store_true', help='Show results without saving')
    
    args = parser.parse_args()
    
    # Paths
    materials_file = PROJECT_ROOT / 'data' / 'materials' / 'Materials.yaml'
    contaminants_file = PROJECT_ROOT / 'data' / 'contaminants' / 'Contaminants.yaml'
    compounds_file = PROJECT_ROOT / 'data' / 'compounds' / 'Compounds.yaml'
    associations_file = PROJECT_ROOT / 'data' / 'associations' / 'DomainAssociations.yaml'
    
    print('═' * 80)
    print('DOMAIN ASSOCIATIONS REGENERATION')
    print('═' * 80)
    print()
    
    if args.dry_run:
        print('🔍 DRY RUN MODE - No files will be modified')
        print()
    
    # Load data
    print('📂 Loading data files...')
    materials_data = load_yaml(materials_file)
    contaminants_data = load_yaml(contaminants_file)
    compounds_data = load_yaml(compounds_file)
    
    print(f'   ✅ {len(materials_data.get("materials", {}))} materials')
    print(f'   ✅ {len(contaminants_data.get("contamination_patterns", {}))} contaminants')
    print(f'   ✅ {len(compounds_data.get("compounds", {}))} compounds')
    print()
    
    # Generate associations
    print('🔗 Generating associations...')
    
    mat_cont = get_material_contaminant_associations(materials_data, contaminants_data)
    print(f'   • Material ↔ Contaminant: {len(mat_cont)} associations (bidirectional)')
    
    cont_comp = get_contaminant_compound_associations(contaminants_data, compounds_data)
    print(f'   • Contaminant ↔ Compound: {len(cont_comp)} associations (bidirectional)')
    
    # Combine and deduplicate
    all_associations = mat_cont + cont_comp
    all_associations = deduplicate_associations(all_associations)
    
    print()
    print(f'   📊 Total unique associations: {len(all_associations)}')
    print()
    
    # Count by type
    mat_cont_count = len([a for a in all_associations if a['relationship_type'] == 'can_have_contamination'])
    cont_mat_count = len([a for a in all_associations if a['relationship_type'] == 'can_contaminate'])
    cont_comp_count = len([a for a in all_associations if a['relationship_type'] == 'generates_byproduct'])
    comp_cont_count = len([a for a in all_associations if a['relationship_type'] == 'byproduct_of'])
    cont_mat_count = len([a for a in all_associations if a['relationship_type'] == 'can_contaminate'])
    cont_comp_count = len([a for a in all_associations if a['relationship_type'] == 'generates_byproduct'])
    comp_cont_count = len([a for a in all_associations if a['relationship_type'] == 'byproduct_of'])
    
    print('📊 Breakdown (bidirectional):')
    print(f'   • Material → Contaminant: {mat_cont_count}')
    print(f'   • Contaminant → Material: {cont_mat_count}')
    print(f'   • Contaminant → Compound: {cont_comp_count}')
    print(f'   • Compound → Contaminant: {comp_cont_count}')
    print()
    
    # Create associations data structure
    associations_data = {
        'metadata': {
            'version': '1.0.0',
            'description': 'Cross-domain relationships between materials, contaminants, and compounds (bidirectional)',
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'total_associations': len(all_associations),
            'breakdown': f'{mat_cont_count}+{cont_mat_count}+{cont_comp_count}+{comp_cont_count}',
            'bidirectional': True,
            'relationship_types': [
                'can_have_contamination (material → contaminant)',
                'can_contaminate (contaminant → material)',
                'generates_byproduct (contaminant → compound)',
                'byproduct_of (compound → contaminant)'
            ]
        },
        'associations': all_associations
    }
    
    # Save
    if not args.dry_run:
        print('💾 Saving DomainAssociations.yaml...')
        save_yaml(associations_file, associations_data)
        print('   ✅ Saved successfully')
        print()
        print('Next steps:')
        print('   1. Verify: git diff data/associations/DomainAssociations.yaml')
        print('   2. Check contaminant-compound coverage:')
        print('      python3 -c "import yaml; d=yaml.safe_load(open(\'data/associations/DomainAssociations.yaml\'));"\\')
        print('           "cont_comp = [a for a in d[\'associations\'] if a[\'relationship_type\']==\'generates_byproduct\'];"\\')
        print('           "print(f\'Contaminant-compound associations: {len(cont_comp)}\')"')
    else:
        print('✅ Dry run complete - no changes saved')
        print()
        print('To apply changes, run without --dry-run flag')
    
    print()


if __name__ == '__main__':
    main()
