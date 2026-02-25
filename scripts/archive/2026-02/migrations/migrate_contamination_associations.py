#!/usr/bin/env python3
"""
Migrate Material-Contaminant Associations
==========================================

Populates material_contaminant_associations in DomainAssociations.yaml 
from contamination.valid lists in Materials.yaml.

This migration script addresses the link correction requirements by:
1. Reading contamination.valid from each material
2. Creating proper associations with full IDs (with -contamination suffix)
3. Writing to DomainAssociations.yaml

Usage:
    python3 scripts/migrate_contamination_associations.py
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any

def load_materials() -> Dict[str, Any]:
    """Load Materials.yaml"""
    materials_path = Path(__file__).parent.parent / "data" / "materials" / "Materials.yaml"
    with open(materials_path, 'r') as f:
        return yaml.safe_load(f)

def load_associations() -> Dict[str, Any]:
    """Load DomainAssociations.yaml"""
    assoc_path = Path(__file__).parent.parent / "data" / "associations" / "DomainAssociations.yaml"
    with open(assoc_path, 'r') as f:
        return yaml.safe_load(f)

def save_associations(data: Dict[str, Any]):
    """Save updated DomainAssociations.yaml"""
    assoc_path = Path(__file__).parent.parent / "data" / "associations" / "DomainAssociations.yaml"
    with open(assoc_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, width=120, sort_keys=False)

def create_association(material_id: str, contaminant_id: str) -> Dict[str, Any]:
    """
    Create a material-contaminant association entry.
    
    Args:
        material_id: Full material ID with -laser-cleaning suffix
        contaminant_id: Contaminant ID (will add -contamination suffix if missing)
    
    Returns:
        Association dictionary
    """
    # Ensure contaminant ID has proper suffix
    if not contaminant_id.endswith('-contamination'):
        full_contaminant_id = f"{contaminant_id}-contamination"
    else:
        full_contaminant_id = contaminant_id
    
    return {
        'material_id': material_id,
        'contaminant_id': full_contaminant_id,
        'frequency': 'common',  # Default, should be reviewed
        'severity': 'moderate',  # Default, should be reviewed
        'typical_context': 'general',
        'verified': False,  # Migrated data needs verification
        'notes': 'Migrated from Materials.yaml contamination.valid list'
    }

def migrate_associations():
    """Main migration logic"""
    print("🔄 Starting migration of material-contaminant associations")
    
    # Load data
    materials_data = load_materials()
    associations_data = load_associations()
    
    # Collect all associations
    new_associations = []
    
    materials = materials_data.get('materials', {})
    print(f"📊 Found {len(materials)} materials")
    
    for material_id, material in materials.items():
        # Get contamination.valid list
        contamination = material.get('contamination', {})
        valid_contaminants = contamination.get('valid', [])
        
        if not valid_contaminants:
            print(f"   ⏭️  {material_id}: No valid contaminants")
            continue
        
        print(f"   ✅ {material_id}: {len(valid_contaminants)} contaminants")
        
        # Create association for each valid contaminant
        for contaminant_id in valid_contaminants:
            # Normalize contaminant ID: convert underscores and spaces to hyphens
            contaminant_id = contaminant_id.replace('_', '-').replace(' ', '-')
            association = create_association(material_id, contaminant_id)
            new_associations.append(association)
    
    # Update associations data
    associations_data['material_contaminant_associations'] = new_associations
    
    # Update metadata
    if 'metadata' not in associations_data:
        associations_data['metadata'] = {}
    
    associations_data['metadata']['total_associations'] = (
        len(new_associations) + 
        len(associations_data.get('contaminant_compound_associations', []))
    )
    
    # Save
    save_associations(associations_data)
    
    print(f"\n✅ Migration complete!")
    print(f"   Created {len(new_associations)} material-contaminant associations")
    print(f"   Saved to: data/associations/DomainAssociations.yaml")
    print(f"\n⚠️  Next steps:")
    print(f"   1. Review the migrated associations")
    print(f"   2. Update frequency/severity values from 'common'/'moderate' defaults")
    print(f"   3. Add typical_context descriptions")
    print(f"   4. Set verified=true after review")
    print(f"   5. Run export to regenerate frontmatter: python3 run.py --export --domain materials")

if __name__ == '__main__':
    migrate_associations()
