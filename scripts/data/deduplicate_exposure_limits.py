#!/usr/bin/env python3
"""
Deduplicate Exposure Limits (CRITICAL - Tier 1 Priority)

PROBLEM: Exposure limits duplicated in:
  - contaminants.laser_properties.safety_data.fumes_generated[].exposure_limit_mg_m3
  - compounds.workplace_exposure (AUTHORITATIVE SOURCE)

SOLUTION: Remove exposure_limit_mg_m3 from contaminants, use compound_id reference only

Usage:
    python3 scripts/data/deduplicate_exposure_limits.py --dry-run
    python3 scripts/data/deduplicate_exposure_limits.py --apply
"""

import argparse
from pathlib import Path
from typing import Dict, List

# Use shared YAML utilities
from shared.utils.file_io import read_yaml_file, write_yaml_file

# Paths
DATA_DIR = Path(__file__).parent.parent.parent / "data"
CONTAMINANTS_FILE = DATA_DIR / "contaminants" / "Contaminants.yaml"
COMPOUNDS_FILE = DATA_DIR / "compounds" / "Compounds.yaml"

def standardize_compound_name_to_id(compound_name: str) -> str:
    """Convert compound name to kebab-case ID"""
    return compound_name.lower().replace(' ', '-').replace('_', '-')

def verify_compound_exists(compound_id: str, compounds: dict) -> bool:
    """Check if compound exists in Compounds.yaml"""
    return compound_id in compounds['compounds']

def deduplicate_exposure_limits(contaminants: dict, compounds: dict, dry_run: bool = True) -> dict:
    """
    Remove duplicate exposure limits from contaminants
    
    Returns stats dictionary
    """
    stats = {
        'contaminants_processed': 0,
        'fumes_entries_updated': 0,
        'exposure_limits_removed': 0,
        'compound_ids_standardized': 0,
        'warnings': []
    }
    
    for contaminant_slug, contaminant_data in contaminants['contaminants'].items():
        fumes = contaminant_data.get('laser_properties', {}).get('safety_data', {}).get('fumes_generated', [])
        
        if not fumes:
            continue
        
        stats['contaminants_processed'] += 1
        
        for i, fume in enumerate(fumes):
            updated = False
            
            # Standardize compound name to compound_id
            if 'compound' in fume and 'compound_id' not in fume:
                compound_name = fume['compound']
                compound_id = standardize_compound_name_to_id(compound_name)
                
                # Verify compound exists
                if verify_compound_exists(compound_id, compounds):
                    fume['compound_id'] = compound_id
                    del fume['compound']
                    stats['compound_ids_standardized'] += 1
                    updated = True
                else:
                    stats['warnings'].append(
                        f"{contaminant_slug}: Compound '{compound_name}' (id: {compound_id}) not found in Compounds.yaml"
                    )
            
            # Remove duplicate exposure_limit_mg_m3
            if 'exposure_limit_mg_m3' in fume:
                exposure_limit = fume['exposure_limit_mg_m3']
                compound_id = fume.get('compound_id', fume.get('compound', ''))
                
                # Log removal
                if not dry_run:
                    print(f"   Removing: {contaminant_slug} → {compound_id}: exposure_limit_mg_m3={exposure_limit}")
                
                del fume['exposure_limit_mg_m3']
                stats['exposure_limits_removed'] += 1
                updated = True
            
            # Remove hazard_class (get from compounds instead)
            if 'hazard_class' in fume:
                del fume['hazard_class']
                updated = True
            
            if updated:
                stats['fumes_entries_updated'] += 1
    
    return stats

def main(dry_run: bool = True):
    """Main deduplication function"""
    print("=" * 80)
    print("EXPOSURE LIMITS DEDUPLICATION (CRITICAL - TIER 1)")
    print("=" * 80)
    print()
    
    print("🎯 GOAL: Remove duplicate exposure limits from contaminants")
    print("   - Keep ONLY in Compounds.yaml (single source of truth)")
    print("   - Reference via compound_id in contaminants")
    print()
    
    # Load data
    print("📂 Loading data files...")
    contaminants = read_yaml_file(CONTAMINANTS_FILE)
    compounds = read_yaml_file(COMPOUNDS_FILE)
    
    print(f"   ✅ Contaminants: {len(contaminants['contaminants'])} entries")
    print(f"   ✅ Compounds: {len(compounds['compounds'])} entries")
    print()
    
    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
        print()
    
    # Process deduplication
    print("🔄 Processing contaminants...")
    print()
    stats = deduplicate_exposure_limits(contaminants, compounds, dry_run)
    
    # Report results
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"Contaminants processed: {stats['contaminants_processed']}")
    print(f"Fumes entries updated: {stats['fumes_entries_updated']}")
    print(f"Exposure limits removed: {stats['exposure_limits_removed']}")
    print(f"Compound IDs standardized: {stats['compound_ids_standardized']}")
    print()
    
    if stats['warnings']:
        print("⚠️  WARNINGS:")
        for warning in stats['warnings']:
            print(f"   {warning}")
        print()
    
    # Show example
    print("📋 EXAMPLE - adhesive-residue-contamination:")
    adhesive = contaminants['contaminants'].get('adhesive-residue-contamination', {})
    fumes = adhesive.get('laser_properties', {}).get('safety_data', {}).get('fumes_generated', [])
    
    if fumes:
        print("   BEFORE:")
        print("     fumes_generated:")
        print("       - compound: Formaldehyde")
        print("         exposure_limit_mg_m3: 0.3  ❌ DUPLICATE")
        print("         hazard_class: carcinogenic  ❌ DUPLICATE")
        print()
        print("   AFTER:")
        print("     fumes_generated:")
        for fume in fumes[:1]:  # Show first entry
            print(f"       - compound_id: {fume.get('compound_id', 'N/A')}")
            print(f"         concentration_mg_m3: {fume.get('concentration_mg_m3', 'N/A')}")
            print("         # Exposure limit comes from Compounds.yaml ✅")
        print()
    
    # Save changes
    if not dry_run:
        print("💾 Saving changes...")
        write_yaml_file(CONTAMINANTS_FILE, contaminants, sort_keys=False)
        print(f"   ✅ Contaminants.yaml updated")
        print()
        print("✅ DEDUPLICATION COMPLETE")
    else:
        print("✅ DRY RUN COMPLETE - Run with --apply to save changes")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deduplicate exposure limits between contaminants and compounds")
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Show what would be changed without modifying files (default)')
    parser.add_argument('--apply', action='store_true',
                        help='Apply changes to data files')
    
    args = parser.parse_args()
    
    # If --apply is specified, turn off dry_run
    dry_run = not args.apply
    
    main(dry_run=dry_run)
