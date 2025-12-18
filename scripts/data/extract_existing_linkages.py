#!/usr/bin/env python3
"""
Extract Existing Domain Linkages
=================================

Extracts all existing relationships from frontmatter files and outputs
them in DomainAssociations.yaml format.

USAGE:
    python3 scripts/data/extract_existing_linkages.py
    
    Output can be copied into data/associations/DomainAssociations.yaml
"""

import yaml
import glob
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set


def extract_compound_contaminant_linkages(frontmatter_dir: Path) -> List[Dict]:
    """Extract contaminant→compound linkages from compound frontmatter files"""
    
    associations = []
    compounds_dir = frontmatter_dir / 'compounds'
    
    if not compounds_dir.exists():
        print(f"⚠️  Compounds directory not found: {compounds_dir}")
        return associations
    
    compound_files = list(compounds_dir.glob('*.yaml'))
    print(f"📋 Processing {len(compound_files)} compound files...")
    
    for compound_file in compound_files:
        with open(compound_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        compound_id = data.get('id')
        linkages = data.get('relationships', {}).get('produced_by_contaminants', [])
        
        for link in linkages:
            contaminant_id = link.get('id')
            if not contaminant_id:
                continue
            
            # Convert compound linkage to association format
            association = {
                'contaminant_id': contaminant_id,
                'compound_id': compound_id,
                'frequency': link.get('frequency', 'common'),
                'severity': link.get('severity', 'moderate'),
                'typical_context': link.get('typical_context', ''),
                'verified': False,  # Default to unverified, manual review needed
                'verification_source': None,
                'notes': ''
            }
            
            associations.append(association)
    
    print(f"✅ Extracted {len(associations)} contaminant→compound associations")
    return associations


def extract_contaminant_material_linkages(frontmatter_dir: Path) -> List[Dict]:
    """Extract contaminant→material linkages from contaminant frontmatter files"""
    
    associations = []
    contaminants_dir = frontmatter_dir / 'contaminants'
    
    if not contaminants_dir.exists():
        print(f"⚠️  Contaminants directory not found: {contaminants_dir}")
        return associations
    
    contaminant_files = list(contaminants_dir.glob('*-contamination.yaml'))
    print(f"📋 Processing {len(contaminant_files)} contaminant files...")
    
    for contaminant_file in contaminant_files:
        with open(contaminant_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        contaminant_id = data.get('id')
        linkages = data.get('relationships', {}).get('related_materials', [])
        
        for link in linkages:
            material_id = link.get('id')
            if not material_id:
                continue
            
            # Convert to association format
            association = {
                'material_id': material_id,
                'contaminant_id': contaminant_id,
                'frequency': link.get('frequency', 'common'),
                'severity': link.get('severity', 'moderate'),
                'typical_context': link.get('typical_context', ''),
                'verified': False,
                'verification_source': None,
                'notes': ''
            }
            
            associations.append(association)
    
    print(f"✅ Extracted {len(associations)} contaminant→material associations")
    return associations


def extract_material_contaminant_linkages(frontmatter_dir: Path) -> List[Dict]:
    """Extract material→contaminant linkages from material frontmatter files"""
    
    associations = []
    materials_dir = frontmatter_dir / 'materials'
    
    if not materials_dir.exists():
        print(f"⚠️  Materials directory not found: {materials_dir}")
        return associations
    
    material_files = list(materials_dir.glob('*-laser-cleaning.yaml'))
    print(f"📋 Processing {len(material_files)} material files...")
    
    for material_file in material_files:
        with open(material_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        material_id = data.get('id')
        linkages = data.get('relationships', {}).get('related_contaminants', [])
        
        for link in linkages:
            contaminant_id = link.get('id')
            if not contaminant_id:
                continue
            
            association = {
                'material_id': material_id,
                'contaminant_id': contaminant_id,
                'frequency': link.get('frequency', 'common'),
                'severity': link.get('severity', 'moderate'),
                'typical_context': link.get('typical_context', ''),
                'verified': False,
                'verification_source': None,
                'notes': ''
            }
            
            associations.append(association)
    
    print(f"✅ Extracted {len(associations)} material→contaminant associations")
    return associations


def deduplicate_associations(associations: List[Dict], key_fields: List[str]) -> List[Dict]:
    """Remove duplicate associations based on key fields"""
    
    seen = set()
    unique = []
    
    for assoc in associations:
        key = tuple(assoc.get(field) for field in key_fields)
        if key not in seen:
            seen.add(key)
            unique.append(assoc)
    
    return unique


def format_association_yaml(associations: List[Dict], indent: int = 2) -> str:
    """Format associations as YAML with proper indentation"""
    
    lines = []
    
    for assoc in associations:
        lines.append("")
        lines.append(f"{'  ' * indent}# {assoc['contaminant_id']} → {assoc.get('compound_id', assoc.get('material_id', 'unknown'))}")
        lines.append(f"{'  ' * indent}- contaminant_id: {assoc['contaminant_id']}")
        
        if 'compound_id' in assoc:
            lines.append(f"{'  ' * indent}  compound_id: {assoc['compound_id']}")
        if 'material_id' in assoc:
            lines.append(f"{'  ' * indent}  material_id: {assoc['material_id']}")
        
        lines.append(f"{'  ' * indent}  frequency: {assoc['frequency']}")
        lines.append(f"{'  ' * indent}  severity: {assoc['severity']}")
        
        if assoc.get('typical_context'):
            context = assoc['typical_context'].replace('"', '\\"')
            lines.append(f"{'  ' * indent}  typical_context: \"{context}\"")
        else:
            lines.append(f"{'  ' * indent}  typical_context: \"\"")
        
        lines.append(f"{'  ' * indent}  verified: {str(assoc['verified']).lower()}")
        
        if assoc.get('verification_source'):
            lines.append(f"{'  ' * indent}  verification_source: \"{assoc['verification_source']}\"")
        else:
            lines.append(f"{'  ' * indent}  verification_source: null")
        
        if assoc.get('notes'):
            lines.append(f"{'  ' * indent}  notes: \"{assoc['notes']}\"")
    
    return '\n'.join(lines)


def main():
    """Extract all linkages and output in associations format"""
    
    # Get paths
    repo_root = Path(__file__).parent.parent.parent
    frontmatter_dir = repo_root / 'frontmatter'
    output_file = repo_root / 'data' / 'associations' / 'ExtractedLinkages.yaml'
    
    print("="*80)
    print("EXTRACTING EXISTING DOMAIN LINKAGES")
    print("="*80)
    print()
    
    # Extract all linkages
    print("1️⃣  CONTAMINANT → COMPOUND LINKAGES")
    print("-"*80)
    cont_comp_assocs = extract_compound_contaminant_linkages(frontmatter_dir)
    cont_comp_assocs = deduplicate_associations(cont_comp_assocs, ['contaminant_id', 'compound_id'])
    print()
    
    print("2️⃣  MATERIAL → CONTAMINANT LINKAGES")
    print("-"*80)
    mat_cont_from_materials = extract_material_contaminant_linkages(frontmatter_dir)
    mat_cont_from_contaminants = extract_contaminant_material_linkages(frontmatter_dir)
    
    # Combine and deduplicate
    all_mat_cont = mat_cont_from_materials + mat_cont_from_contaminants
    mat_cont_assocs = deduplicate_associations(all_mat_cont, ['material_id', 'contaminant_id'])
    print(f"✅ Combined and deduplicated: {len(mat_cont_assocs)} unique associations")
    print()
    
    # Generate output YAML
    print("3️⃣  GENERATING OUTPUT")
    print("-"*80)
    
    output_yaml = f"""# Extracted Domain Linkages
# =============================================================================
# Generated: {Path(__file__).name}
# Source: frontmatter/ files
# 
# ⚠️  VERIFICATION STATUS: All associations extracted with verified=false
#     Manual review and verification_source required before production use
# =============================================================================

metadata:
  extracted_from: frontmatter/
  total_associations: {len(mat_cont_assocs) + len(cont_comp_assocs)}
  verified: 0
  verification_rate: "0%"

# =============================================================================
# MATERIAL ↔ CONTAMINANT ASSOCIATIONS
# =============================================================================
material_contaminant_associations:
{format_association_yaml(mat_cont_assocs, indent=1)}

# =============================================================================
# CONTAMINANT ↔ COMPOUND ASSOCIATIONS
# =============================================================================
contaminant_compound_associations:
{format_association_yaml(cont_comp_assocs, indent=1)}

# =============================================================================
# MATERIAL ↔ COMPOUND ASSOCIATIONS
# =============================================================================
# These will be generated from transitive relationships:
# Material → Contaminant → Compound
material_compound_associations: []
"""
    
    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_yaml)
    
    print(f"✅ Wrote extracted linkages to: {output_file}")
    print()
    
    # Summary
    print("="*80)
    print("EXTRACTION SUMMARY")
    print("="*80)
    print(f"  Material ↔ Contaminant: {len(mat_cont_assocs)}")
    print(f"  Contaminant ↔ Compound: {len(cont_comp_assocs)}")
    print(f"  Total: {len(mat_cont_assocs) + len(cont_comp_assocs)}")
    print()
    print("⚠️  NEXT STEPS:")
    print("  1. Review ExtractedLinkages.yaml")
    print("  2. Add verification_source for each association")
    print("  3. Set verified=true after confirming")
    print("  4. Merge into DomainAssociations.yaml")
    print()


if __name__ == '__main__':
    main()
