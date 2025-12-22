#!/usr/bin/env python3
"""
Replace level/valence with consolidated "intensity" field for strictly positive/negative color coding.

This script replaces the two-field system (level + valence) with a single directional intensity field:
- intensity: very_negative | negative | slightly_negative | slightly_positive | positive | very_positive

This provides a strict positive/negative gradient where:
- very_negative: Dark red (severe hazards, high severity)
- negative: Red (moderate hazards)
- slightly_negative: Light red (minor issues)
- slightly_positive: Light green (minor benefits)
- positive: Green (good performance)
- very_positive: Dark green (excellent results)

Usage:
    python3 scripts/tools/add_level_field.py --dry-run
    python3 scripts/tools/add_level_field.py
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# Intensity mapping for negative fields (severity, hazard)
NEGATIVE_INTENSITY_MAP = {
    'negligible': 'slightly_negative',
    'low': 'slightly_negative',
    'minimal': 'slightly_negative',
    'moderate': 'negative',
    'medium': 'negative',
    'high': 'very_negative',
    'extreme': 'very_negative',
    'critical': 'very_negative',
}

# Intensity mapping for positive fields (effectiveness)
POSITIVE_INTENSITY_MAP = {
    'poor': 'slightly_negative',
    'fair': 'slightly_positive',
    'moderate': 'slightly_positive',
    'medium': 'slightly_positive',
    'good': 'positive',
    'excellent': 'very_positive',
}

# Intensity mapping for frequency (context-dependent: rare contamination = good)
FREQUENCY_INTENSITY_MAP = {
    'rare': 'slightly_positive',      # Less contamination = better
    'occasional': 'slightly_negative',
    'common': 'negative',
    'very_common': 'very_negative',   # More contamination = worse
}


def determine_intensity(item: Dict[str, Any]) -> Optional[str]:
    """
    Determine consolidated intensity for a relationship item.
    
    Priority order for determining which field to use:
    1. severity (if present) - maps to negative intensity
    2. hazard_level (if present) - maps to negative intensity
    3. effectiveness (if present) - maps to positive intensity
    4. frequency (if present) - maps to negative intensity (common = bad)
    
    Args:
        item: Relationship item dictionary
        
    Returns:
        Intensity string or None
        - very_negative: severe hazards, high severity
        - negative: moderate hazards
        - slightly_negative: minor issues, common frequency
        - slightly_positive: minor benefits, rare frequency
        - positive: good performance
        - very_positive: excellent results
    """
    # Check severity/hazard (negative scale)
    if 'severity' in item:
        value = str(item['severity']).lower()
        if value in NEGATIVE_INTENSITY_MAP:
            return NEGATIVE_INTENSITY_MAP[value]
    
    if 'hazard_level' in item:
        value = str(item['hazard_level']).lower()
        if value in NEGATIVE_INTENSITY_MAP:
            return NEGATIVE_INTENSITY_MAP[value]
    
    # Check effectiveness (positive scale)
    if 'effectiveness' in item:
        value = str(item['effectiveness']).lower()
        if value in POSITIVE_INTENSITY_MAP:
            return POSITIVE_INTENSITY_MAP[value]
    
    # Check frequency (negative scale - more contamination = worse)
    if 'frequency' in item:
        value = str(item['frequency']).lower()
        if value in FREQUENCY_INTENSITY_MAP:
            return FREQUENCY_INTENSITY_MAP[value]
    
    return None


def add_intensity_to_relationships(data: Dict[str, Any]) -> tuple[int, int]:
    """
    Replace level/valence with consolidated intensity field in all relationship items.
    
    Args:
        data: Parsed YAML data (materials, contaminants, compounds, or settings)
        
    Returns:
        Tuple of (items_added, items_removed)
    """
    added_count = 0
    removed_count = 0
    
    # Handle different domain structures
    for domain_key in ['materials', 'contaminants', 'compounds', 'settings']:
        if domain_key not in data:
            continue
            
        for item_key, item_data in data[domain_key].items():
            if 'relationships' not in item_data:
                continue
                
            # Process all relationship types
            for rel_type, rel_items in item_data['relationships'].items():
                if not isinstance(rel_items, list):
                    continue
                    
                for rel_item in rel_items:
                    if not isinstance(rel_item, dict):
                        continue
                    
                    # Remove old level/valence fields if present
                    if 'level' in rel_item:
                        del rel_item['level']
                        removed_count += 1
                    if 'valence' in rel_item:
                        del rel_item['valence']
                        removed_count += 1
                    
                    # Skip if intensity already exists
                    if 'intensity' in rel_item:
                        continue
                    
                    # Determine and add intensity
                    intensity = determine_intensity(rel_item)
                    if intensity:
                        rel_item['intensity'] = intensity
                        added_count += 1
    
    return (added_count, removed_count)


def process_file(file_path: Path, dry_run: bool = False) -> Dict[str, int]:
    """
    Process a single YAML file to replace level/valence with intensity.
    
    Args:
        file_path: Path to YAML file
        dry_run: If True, do not save changes
        
    Returns:
        Dictionary with stats
    """
    print(f"\nProcessing: {file_path.name}")
    
    # Load YAML
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if not data:
        print("  ⚠️  Empty file")
        return {'added': 0, 'removed': 0}
    
    # Replace level/valence with intensity
    added_count, removed_count = add_intensity_to_relationships(data)
    
    if added_count == 0 and removed_count == 0:
        print("  ℹ️  No items to update")
        return {'added': 0, 'removed': 0}
    
    if removed_count > 0:
        print(f"  🗑️  Removed {removed_count} old fields (level/valence)")
    if added_count > 0:
        print(f"  ✅ Added intensity to {added_count} relationship items")
    
    # Save if not dry run
    if not dry_run:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, 
                     allow_unicode=True, width=1000)
        print(f"  💾 Saved changes")
    else:
        print(f"  🔍 Dry run - changes not saved")
    
    return {'added': added_count, 'removed': removed_count}


def main():
    parser = argparse.ArgumentParser(
        description='Replace level/valence with consolidated intensity field'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    args = parser.parse_args()
    
    print('=' * 80)
    print('REPLACE LEVEL/VALENCE WITH INTENSITY FIELD')
    print('=' * 80)
    
    if args.dry_run:
        print('🔍 DRY RUN MODE - No files will be modified')
    
    # Define files to process
    data_dir = project_root / 'data'
    files_to_process = [
        data_dir / 'materials' / 'Materials.yaml',
        data_dir / 'contaminants' / 'contaminants.yaml',
        data_dir / 'compounds' / 'Compounds.yaml',
        data_dir / 'settings' / 'Settings.yaml',
    ]
    
    # Process each file
    total_added = 0
    total_removed = 0
    
    for file_path in files_to_process:
        if not file_path.exists():
            print(f"\n⚠️  File not found: {file_path.name}")
            continue
        
        stats = process_file(file_path, dry_run=args.dry_run)
        total_added += stats['added']
        total_removed += stats['removed']
    
    # Summary
    print('\n' + '=' * 80)
    print('SUMMARY')
    print('=' * 80)
    print(f'Fields removed: {total_removed} (level + valence)')
    print(f'Fields added: {total_added} (intensity)')
    
    if args.dry_run:
        print('\n🔍 This was a dry run. Run without --dry-run to apply changes.')
    else:
        print('\n✅ All changes saved!')
        print('\nNext steps:')
        print('1. Review changes: git diff data/')
        print('2. Test export: python3 run.py --export-all --dry-run')
        print('3. Commit changes: git add data/ && git commit -m "Replace level/valence with intensity field"')


if __name__ == '__main__':
    main()
