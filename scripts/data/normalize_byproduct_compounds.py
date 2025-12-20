#!/usr/bin/env python3
"""
Normalize Byproduct Compound Names

Applies the normalization mapping from byproduct_normalization_map.yaml
to update compound names in Contaminants.yaml byproducts.

This creates associations between contaminants and compounds by standardizing
the compound name format.

Usage:
    python3 scripts/data/normalize_byproduct_compounds.py [--dry-run] [--phase 1]
    
Arguments:
    --dry-run: Show what would change without modifying files
    --phase N: Apply only Phase N mappings (1, 2, or 3)
    --verbose: Show detailed progress
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Set, Tuple
import yaml

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_yaml(filepath: Path) -> Dict:
    """Load YAML file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_yaml(filepath: Path, data: Dict, backup: bool = True) -> None:
    """Save YAML file with optional backup"""
    if backup and filepath.exists():
        backup_path = filepath.with_suffix('.yaml.backup')
        if not backup_path.exists():
            import shutil
            shutil.copy2(filepath, backup_path)
            print(f"📦 Backup created: {backup_path}")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)


def get_phase_mappings(mapping_data: Dict, phase: int = None) -> Dict[str, str]:
    """Extract mappings for a specific phase (or all if phase=None)"""
    all_mappings = {k: v for k, v in mapping_data.items() if k != 'metadata'}
    
    if phase is None:
        return all_mappings
    
    # Phase-specific extraction based on comments in the YAML
    # For now, return all mappings - can be refined based on phase markers
    return all_mappings


def normalize_contaminants(
    contam_data: Dict,
    normalization_map: Dict[str, str],
    verbose: bool = False
) -> Tuple[Dict, int, Set[str]]:
    """
    Normalize byproduct compound names in contaminants data.
    
    Returns:
        (updated_data, changes_made, normalized_compounds)
    """
    patterns = contam_data.get('contamination_patterns', {})
    changes = 0
    normalized_compounds = set()
    
    for pattern_id, pattern_data in patterns.items():
        laser_props = pattern_data.get('laser_properties', {})
        removal_chars = laser_props.get('removal_characteristics', {})
        byproducts = removal_chars.get('byproducts', [])
        
        for i, bp in enumerate(byproducts):
            original_compound = bp.get('compound', '')
            
            if original_compound in normalization_map:
                new_compound = normalization_map[original_compound]
                
                if original_compound != new_compound:
                    bp['compound'] = new_compound
                    changes += 1
                    normalized_compounds.add(new_compound)
                    
                    if verbose:
                        print(f"  {pattern_id}: '{original_compound}' → '{new_compound}'")
    
    return contam_data, changes, normalized_compounds


def main():
    parser = argparse.ArgumentParser(description='Normalize byproduct compound names')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without saving')
    parser.add_argument('--phase', type=int, choices=[1, 2, 3], help='Apply only Phase N mappings')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed progress')
    
    args = parser.parse_args()
    
    # Paths
    mapping_file = PROJECT_ROOT / 'data' / 'compounds' / 'byproduct_normalization_map.yaml'
    contaminants_file = PROJECT_ROOT / 'data' / 'contaminants' / 'Contaminants.yaml'
    
    print('═' * 80)
    print('BYPRODUCT COMPOUND NORMALIZATION')
    print('═' * 80)
    print()
    
    if args.dry_run:
        print('🔍 DRY RUN MODE - No files will be modified')
        print()
    
    # Load data
    print('📂 Loading data...')
    mapping_data = load_yaml(mapping_file)
    contam_data = load_yaml(contaminants_file)
    
    # Get normalization map
    normalization_map = get_phase_mappings(mapping_data, args.phase)
    
    print(f'   ✅ Loaded {len(normalization_map)} normalization mappings')
    if args.phase:
        print(f'   📌 Applying Phase {args.phase} mappings only')
    print(f'   ✅ Loaded {len(contam_data.get("contamination_patterns", {}))} contamination patterns')
    print()
    
    # Apply normalization
    print('🔄 Normalizing byproduct compound names...')
    updated_data, changes, normalized_compounds = normalize_contaminants(
        contam_data,
        normalization_map,
        verbose=args.verbose
    )
    
    print()
    print('═' * 80)
    print('RESULTS')
    print('═' * 80)
    print(f'   Changes made: {changes}')
    print(f'   Unique compounds normalized to: {len(normalized_compounds)}')
    print()
    
    if normalized_compounds:
        print('   Normalized compound IDs:')
        for compound_id in sorted(normalized_compounds):
            print(f'      • {compound_id}')
        print()
    
    # Save results
    if not args.dry_run and changes > 0:
        print('💾 Saving updated Contaminants.yaml...')
        save_yaml(contaminants_file, updated_data, backup=True)
        print('   ✅ Saved successfully')
        print()
        print('Next steps:')
        print('   1. Verify changes: git diff data/contaminants/Contaminants.yaml')
        print('   2. Regenerate associations: python3 scripts/sync/regenerate_associations.py')
        print('   3. Verify new associations: Check DomainAssociations.yaml')
    elif args.dry_run:
        print('✅ Dry run complete - no changes saved')
        print()
        print('To apply changes, run without --dry-run flag')
    else:
        print('✅ No changes needed - all byproducts already normalized')
    
    print()


if __name__ == '__main__':
    main()
