#!/usr/bin/env python3
"""
Generate Bidirectional Linkages Between Domains

Analyzes existing unidirectional links and generates reverse links:
- Contaminant → Material (via valid_materials) → Material → Contaminant (new: related_contaminants)
- Contaminant → Compound (via byproducts) → Compound → Contaminant (new: produced_by_contaminants)

Usage:
    python3 scripts/data/generate_bidirectional_linkages.py --dry-run
    python3 scripts/data/generate_bidirectional_linkages.py --apply
"""

import yaml
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

# Paths
DATA_DIR = Path(__file__).parent.parent.parent / "data"
MATERIALS_FILE = DATA_DIR / "materials" / "Materials.yaml"
CONTAMINANTS_FILE = DATA_DIR / "contaminants" / "Contaminants.yaml"
COMPOUNDS_FILE = DATA_DIR / "compounds" / "Compounds.yaml"
SETTINGS_FILE = DATA_DIR / "settings" / "Settings.yaml"

def load_yaml(filepath: Path) -> dict:
    """Load YAML file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_yaml(filepath: Path, data: dict):
    """Save YAML file with proper formatting"""
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

def analyze_contaminant_material_links(contaminants: dict) -> Dict[str, Set[str]]:
    """
    Analyze Contaminant → Material links (via valid_materials)
    Returns: {material_name: set(contaminant_slugs)}
    """
    material_to_contaminants = defaultdict(set)
    
    for contaminant_slug, contaminant_data in contaminants['contaminants'].items():
        valid_materials = contaminant_data.get('valid_materials', [])
        for material in valid_materials:
            material_to_contaminants[material].add(contaminant_slug)
    
    return material_to_contaminants

def analyze_contaminant_compound_links(contaminants: dict) -> Dict[str, Set[str]]:
    """
    Analyze Contaminant → Compound links (via byproducts + fumes_generated)
    Returns: {compound_id: set(contaminant_slugs)}
    """
    compound_to_contaminants = defaultdict(set)
    
    for contaminant_slug, contaminant_data in contaminants['contaminants'].items():
        # Check byproducts
        byproducts = contaminant_data.get('laser_properties', {}).get('removal_characteristics', {}).get('byproducts', [])
        for byproduct in byproducts:
            compound = byproduct.get('compound', '')
            if compound and compound not in ['H2O', 'CO2', 'O2', 'N2']:  # Skip common non-hazardous
                # Convert to kebab-case ID
                compound_id = compound.lower().replace(' ', '-').replace('_', '-')
                compound_to_contaminants[compound_id].add(contaminant_slug)
        
        # Check fumes_generated
        fumes = contaminant_data.get('laser_properties', {}).get('safety_data', {}).get('fumes_generated', [])
        for fume in fumes:
            compound = fume.get('compound', '')
            if compound:
                compound_id = compound.lower().replace(' ', '-').replace('_', '-')
                compound_to_contaminants[compound_id].add(contaminant_slug)
    
    return compound_to_contaminants

def add_material_linkages(materials: dict, material_to_contaminants: Dict[str, Set[str]]) -> int:
    """
    Add related_contaminants to materials
    Returns: Number of materials updated
    """
    updated_count = 0
    
    for material_name, material_data in materials['materials'].items():
        related_contaminants = sorted(material_to_contaminants.get(material_name, set()))
        
        if related_contaminants:
            if 'related_contaminants' not in material_data or material_data.get('related_contaminants') != related_contaminants:
                material_data['related_contaminants'] = [
                    {
                        'contaminant_id': slug,
                        'frequency': 'common',  # Default, can be refined later
                        'severity': 'moderate'  # Default, can be refined later
                    }
                    for slug in related_contaminants
                ]
                updated_count += 1
    
    return updated_count

def add_compound_linkages(compounds: dict, compound_to_contaminants: Dict[str, Set[str]]) -> int:
    """
    Add produced_by_contaminants to compounds
    Returns: Number of compounds updated
    """
    updated_count = 0
    
    for compound_id, compound_data in compounds['compounds'].items():
        related_contaminants = sorted(compound_to_contaminants.get(compound_id, set()))
        
        if related_contaminants:
            if 'produced_by_contaminants' not in compound_data or compound_data.get('produced_by_contaminants') != related_contaminants:
                compound_data['produced_by_contaminants'] = [
                    {
                        'contaminant_id': slug,
                        'source': 'laser_ablation',
                        'typical_concentration_range': 'moderate'  # Default, can be refined
                    }
                    for slug in related_contaminants
                ]
                updated_count += 1
    
    return updated_count

def generate_linkages(dry_run: bool = True):
    """
    Main function to generate all bidirectional linkages
    """
    print("=" * 80)
    print("BIDIRECTIONAL LINKAGE GENERATION")
    print("=" * 80)
    print()
    
    # Load data files
    print("📂 Loading data files...")
    materials = load_yaml(MATERIALS_FILE)
    contaminants = load_yaml(CONTAMINANTS_FILE)
    compounds = load_yaml(COMPOUNDS_FILE)
    
    print(f"   ✅ Materials: {len(materials['materials'])} entries")
    print(f"   ✅ Contaminants: {len(contaminants['contaminants'])} entries")
    print(f"   ✅ Compounds: {len(compounds['compounds'])} entries")
    print()
    
    # Analyze existing links
    print("🔍 Analyzing existing links...")
    print()
    
    print("1️⃣  Contaminant → Material links (via valid_materials)")
    material_to_contaminants = analyze_contaminant_material_links(contaminants)
    print(f"   Found: {len(material_to_contaminants)} materials with contaminant links")
    print(f"   Example: Aluminum has {len(material_to_contaminants.get('Aluminum', set()))} related contaminants")
    print()
    
    print("2️⃣  Contaminant → Compound links (via byproducts + fumes)")
    compound_to_contaminants = analyze_contaminant_compound_links(contaminants)
    print(f"   Found: {len(compound_to_contaminants)} compounds with contaminant links")
    print(f"   Example: formaldehyde produced by {len(compound_to_contaminants.get('formaldehyde', set()))} contaminants")
    print()
    
    # Generate reverse links
    print("🔄 Generating reverse links...")
    print()
    
    if dry_run:
        print("   🔍 DRY RUN MODE - No files will be modified")
        print()
    
    # Update materials with related_contaminants
    print("3️⃣  Adding related_contaminants to Materials.yaml")
    materials_updated = add_material_linkages(materials, material_to_contaminants)
    print(f"   Would update: {materials_updated} materials")
    
    # Show example
    if materials_updated > 0:
        for material_name, material_data in materials['materials'].items():
            if 'related_contaminants' in material_data:
                print(f"\n   Example: {material_name}")
                print(f"   related_contaminants:")
                for link in material_data['related_contaminants'][:3]:
                    print(f"     - contaminant_id: {link['contaminant_id']}")
                    print(f"       frequency: {link['frequency']}")
                    print(f"       severity: {link['severity']}")
                if len(material_data['related_contaminants']) > 3:
                    print(f"     ... and {len(material_data['related_contaminants']) - 3} more")
                break
    print()
    
    # Update compounds with produced_by_contaminants
    print("4️⃣  Adding produced_by_contaminants to Compounds.yaml")
    compounds_updated = add_compound_linkages(compounds, compound_to_contaminants)
    print(f"   Would update: {compounds_updated} compounds")
    
    # Show example
    if compounds_updated > 0:
        for compound_id, compound_data in compounds['compounds'].items():
            if 'produced_by_contaminants' in compound_data:
                print(f"\n   Example: {compound_id}")
                print(f"   produced_by_contaminants:")
                for link in compound_data['produced_by_contaminants'][:3]:
                    print(f"     - contaminant_id: {link['contaminant_id']}")
                    print(f"       source: {link['source']}")
                    print(f"       typical_concentration_range: {link['typical_concentration_range']}")
                if len(compound_data['produced_by_contaminants']) > 3:
                    print(f"     ... and {len(compound_data['produced_by_contaminants']) - 3} more")
                break
    print()
    
    # Save changes
    if not dry_run:
        print("💾 Saving changes...")
        save_yaml(MATERIALS_FILE, materials)
        save_yaml(COMPOUNDS_FILE, compounds)
        print(f"   ✅ Materials.yaml updated ({materials_updated} entries)")
        print(f"   ✅ Compounds.yaml updated ({compounds_updated} entries)")
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Materials with new linkages: {materials_updated}")
    print(f"Compounds with new linkages: {compounds_updated}")
    print(f"Total bidirectional links created: {materials_updated + compounds_updated}")
    print()
    
    if dry_run:
        print("✅ DRY RUN COMPLETE - Run with --apply to save changes")
    else:
        print("✅ LINKAGES APPLIED - Data files updated")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate bidirectional linkages between domains")
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Show what would be changed without modifying files (default)')
    parser.add_argument('--apply', action='store_true',
                        help='Apply changes to data files')
    
    args = parser.parse_args()
    
    # If --apply is specified, turn off dry_run
    dry_run = not args.apply
    
    generate_linkages(dry_run=dry_run)
