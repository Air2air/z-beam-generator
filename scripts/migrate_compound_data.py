#!/usr/bin/env python3
"""
Migrate compound data from fumes_generated to relationships.produces_compounds
Adds concentration_range and hazard_class fields
Removes legacy fumes_generated array
"""

import sys
from pathlib import Path
from typing import Dict, List, Any

# Use shared YAML utilities
from shared.utils.file_io import read_yaml_file, write_yaml_file
from shared.utils.formatters import normalize_compound_name

def migrate_frontmatter(file_path: Path, dry_run: bool = False) -> Dict[str, Any]:
    """
    Migrate single frontmatter file
    
    Returns dict with migration stats
    """
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Processing: {file_path.name}")
    
    data = read_yaml_file(file_path)
    stats = {
        'file': file_path.name,
        'compounds_updated': 0,
        'fields_added': [],
        'mismatches': [],
        'fumes_removed': False
    }
    
    # Check if migration needed
    if 'relationships' not in data or 'produces_compounds' not in data['relationships']:
        print("  ⚠️  No produces_compounds found, skipping")
        return stats
    
    # Get legacy fumes data
    fumes_generated = []
    if 'laser_properties' in data and 'safety_data' in data['laser_properties']:
        fumes_generated = data['laser_properties']['safety_data'].get('fumes_generated', [])
    
    if not fumes_generated:
        print("  ℹ️  No fumes_generated found, checking for missing fields only")
    
    # Create lookup: normalized_name -> fume_data
    fumes_lookup = {}
    for fume in fumes_generated:
        normalized = normalize_compound_name(fume.get('compound', ''), slug_format=True)
        fumes_lookup[normalized] = fume
    
    # Update each compound in produces_compounds
    compounds = data['relationships']['produces_compounds']
    
    for compound in compounds:
        # Extract normalized name from title
        title = compound.get('title', '')
        normalized_title = normalize_compound_name(title, slug_format=True)
        
        # Find matching fume
        fume = fumes_lookup.get(normalized_title)
        
        if not fume and fumes_lookup:
            # Try matching by last word (e.g., "Carbon Monoxide" -> "monoxide")
            last_word = normalize_compound_name(title.split()[-1] if title else '', slug_format=True)
            fume = next((f for name, f in fumes_lookup.items() if last_word in name), None)
        
        if fume:
            updated = False
            
            # Add concentration_range if missing
            if 'concentration_range' not in compound:
                conc = fume.get('concentration_mg_m3', '')
                # Convert to standardized format
                if isinstance(conc, str):
                    # Handle various formats
                    if 'mg/m' not in conc.lower():
                        compound['concentration_range'] = f"{conc} mg/m³"
                    else:
                        compound['concentration_range'] = conc.replace('mg/m3', 'mg/m³')
                else:
                    compound['concentration_range'] = f"{conc} mg/m³"
                stats['fields_added'].append(f"{title}: concentration_range")
                updated = True
            
            # Add hazard_class if missing
            if 'hazard_class' not in compound:
                compound['hazard_class'] = fume.get('hazard_class', 'toxic')
                stats['fields_added'].append(f"{title}: hazard_class")
                updated = True
            
            # Validate exposure_limit matches ACGIH (if present)
            if 'exposure_limit_mg_m3' in fume:
                acgih = compound.get('exposure_limits', {}).get('acgih_tlv_mg_m3')
                if acgih and acgih != fume['exposure_limit_mg_m3']:
                    stats['mismatches'].append(
                        f"{title}: ACGIH mismatch ({acgih} vs {fume['exposure_limit_mg_m3']})"
                    )
            
            if updated:
                stats['compounds_updated'] += 1
        else:
            # No fume data, check if fields already exist or need defaults
            if 'concentration_range' not in compound:
                print(f"  ⚠️  No fume data for: {title}, skipping concentration_range")
            if 'hazard_class' not in compound:
                print(f"  ⚠️  No fume data for: {title}, skipping hazard_class")
    
    # Remove fumes_generated
    if 'laser_properties' in data and 'safety_data' in data['laser_properties']:
        if 'fumes_generated' in data['laser_properties']['safety_data']:
            if not dry_run:
                del data['laser_properties']['safety_data']['fumes_generated']
            stats['fumes_removed'] = True
            print("  ✅ Removed fumes_generated")
    
    # Save if not dry run
    if not dry_run and (stats['compounds_updated'] > 0 or stats['fumes_removed']):
        write_yaml_file(file_path, data, sort_keys=False)
        print(f"  ✅ Updated {stats['compounds_updated']} compounds")
    elif dry_run:
        print(f"  ℹ️  Would update {stats['compounds_updated']} compounds")
    
    return stats

def migrate_all_contaminants(contaminants_dir: Path, dry_run: bool = False):
    """Migrate all contaminant frontmatter files"""
    
    yaml_files = list(contaminants_dir.glob('*.yaml'))
    print(f"Found {len(yaml_files)} YAML files")
    
    all_stats = []
    
    for yaml_file in yaml_files:
        try:
            stats = migrate_frontmatter(yaml_file, dry_run)
            all_stats.append(stats)
        except Exception as e:
            print(f"  ❌ Error processing {yaml_file.name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Print summary
    print("\n" + "="*80)
    print("MIGRATION SUMMARY")
    print("="*80)
    
    total_updated = sum(s['compounds_updated'] for s in all_stats)
    total_files = len([s for s in all_stats if s['compounds_updated'] > 0])
    total_fields = sum(len(s['fields_added']) for s in all_stats)
    total_fumes_removed = len([s for s in all_stats if s['fumes_removed']])
    
    print(f"Files processed: {len(all_stats)}")
    print(f"Files updated: {total_files}")
    print(f"Compounds updated: {total_updated}")
    print(f"Fields added: {total_fields}")
    print(f"Fumes_generated removed: {total_fumes_removed}")
    
    # Show mismatches
    mismatches = [m for s in all_stats for m in s.get('mismatches', [])]
    if mismatches:
        print(f"\n⚠️  {len(mismatches)} exposure limit mismatches found:")
        for mismatch in mismatches[:10]:  # Show first 10
            print(f"  - {mismatch}")
    
    print("\n✅ Migration complete!")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate compound data')
    parser.add_argument('--contaminants-dir', 
                       default='frontmatter/contaminants',
                       help='Path to contaminants directory')
    parser.add_argument('--dry-run', 
                       action='store_true',
                       help='Run without making changes')
    
    args = parser.parse_args()
    
    contaminants_dir = Path(args.contaminants_dir)
    if not contaminants_dir.exists():
        print(f"Error: Directory not found: {contaminants_dir}")
        sys.exit(1)
    
    migrate_all_contaminants(contaminants_dir, args.dry_run)
