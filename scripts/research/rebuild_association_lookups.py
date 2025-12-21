#!/usr/bin/env python3
"""
Rebuild Association Lookup Dictionaries

Rebuilds contaminant_to_material and material_to_contaminant lookup dictionaries
from the associations list in DomainAssociations.yaml.

This is needed after Phase 3 research because the researcher added associations
to the list but didn't rebuild the dictionaries that RemovalByMaterialEnricher uses.

Created: December 20, 2025
"""

import yaml
from pathlib import Path
from typing import Dict, List
from collections import defaultdict


def rebuild_lookups():
    """Rebuild lookup dictionaries from associations list."""
    
    project_root = Path(__file__).resolve().parents[2]
    assoc_file = project_root / 'data/associations/DomainAssociations.yaml'
    
    print("📂 Loading DomainAssociations.yaml...")
    with open(assoc_file) as f:
        data = yaml.safe_load(f)
    
    associations = data.get('associations', [])
    print(f"   Found {len(associations)} associations")
    
    # Build lookups from associations list
    material_to_contaminant = defaultdict(list)
    contaminant_to_material = defaultdict(list)
    
    print("\n🔧 Building lookup dictionaries...")
    for assoc in associations:
        source_domain = assoc.get('source_domain')
        source_id = assoc.get('source_id')
        target_domain = assoc.get('target_domain')
        target_id = assoc.get('target_id')
        relationship = assoc.get('relationship_type')
        
        # Material → Contaminant (can_have_contamination)
        if (source_domain == 'materials' and 
            target_domain == 'contaminants' and
            relationship == 'can_have_contamination'):
            
            if target_id not in material_to_contaminant[source_id]:
                material_to_contaminant[source_id].append(target_id)
        
        # Contaminant → Material (can_contaminate)
        if (source_domain == 'contaminants' and 
            target_domain == 'materials' and
            relationship == 'can_contaminate'):
            
            if target_id not in contaminant_to_material[source_id]:
                contaminant_to_material[source_id].append(target_id)
    
    # Convert defaultdicts to regular dicts and sort
    material_to_contaminant = {k: sorted(v) for k, v in sorted(material_to_contaminant.items())}
    contaminant_to_material = {k: sorted(v) for k, v in sorted(contaminant_to_material.items())}
    
    print(f"   material_to_contaminant: {len(material_to_contaminant)} materials")
    print(f"   contaminant_to_material: {len(contaminant_to_material)} contaminants")
    
    # Update data with new lookups
    data['material_to_contaminant'] = material_to_contaminant
    data['contaminant_to_material'] = contaminant_to_material
    
    # Update metadata
    if 'metadata' not in data:
        data['metadata'] = {}
    
    data['metadata']['total_associations'] = len(associations)
    data['metadata']['materials_count'] = len(material_to_contaminant)
    data['metadata']['contaminants_count'] = len(contaminant_to_material)
    
    # Save updated file
    print("\n💾 Writing updated file...")
    with open(assoc_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print("\n✅ Rebuild complete!")
    print(f"\n📊 SUMMARY:")
    print(f"   Materials with contaminant associations: {len(material_to_contaminant)}")
    print(f"   Contaminants with material associations: {len(contaminant_to_material)}")
    print(f"   Total bidirectional associations: {len(associations)}")
    
    # Sample some newly added contaminants
    print(f"\n🔍 Sample newly added contaminants:")
    sample_contaminants = ['water-stain-contamination', 'hydraulic-fluid-contamination', 
                          'plastic-residue-contamination', 'carbon-soot-contamination']
    for contam_id in sample_contaminants:
        materials = contaminant_to_material.get(contam_id, [])
        print(f"   {contam_id}: {len(materials)} materials")


if __name__ == '__main__':
    rebuild_lookups()
