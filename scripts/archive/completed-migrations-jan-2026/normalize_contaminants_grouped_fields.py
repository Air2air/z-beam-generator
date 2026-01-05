#!/usr/bin/env python3
"""
Normalize Contaminants Grouped Fields

Converts dict-based grouped fields (materials, safety_data) to card format.

Created: December 22, 2025
"""

import yaml
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple


def backup_file(file_path: Path) -> Path:
    """Create timestamped backup of file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = file_path.parent / f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backed up: {backup_path.name}")
    return backup_path


def wrap_grouped_field_with_card(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert grouped dict field to card format.
    
    Input: {title: "X", description: "Y", groups: [...]}
    Output: {presentation: 'card', items: [{title: "X", description: "Y", groups: [...]}]}
    """
    return {
        'presentation': 'card',
        'items': [data]
    }


def normalize_contaminants_grouped_fields(file_path: Path, dry_run: bool = False) -> Tuple[int, List[str]]:
    """
    Normalize materials and safety_data fields to card format.
    
    Returns:
        (items_modified, list_of_changes)
    """
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    
    patterns = data['contamination_patterns']
    modified_count = 0
    changes = []
    
    # Fields that should be in card format if they're dicts
    grouped_fields = ['materials', 'safety_data']
    
    for pattern_id, pattern in patterns.items():
        pattern_changes = []
        
        if 'relationships' not in pattern:
            continue
        
        for field in grouped_fields:
            if field in pattern['relationships']:
                field_data = pattern['relationships'][field]
                
                # Check if it's a dict without presentation wrapper
                if isinstance(field_data, dict) and 'presentation' not in field_data:
                    # Convert to card format
                    pattern['relationships'][field] = wrap_grouped_field_with_card(field_data)
                    pattern_changes.append(f"Wrapped {field} in card format")
        
        if pattern_changes:
            modified_count += 1
            changes.append(f"{pattern_id}: {', '.join(pattern_changes)}")
    
    if not dry_run and modified_count > 0:
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    return modified_count, changes


def validate_normalization(file_path: Path) -> Dict[str, Any]:
    """Validate that all grouped fields are in card format."""
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    
    results = {'status': 'PASS', 'issues': []}
    grouped_fields = ['materials', 'safety_data']
    
    for pattern_id, pattern in data['contamination_patterns'].items():
        if 'relationships' not in pattern:
            continue
        
        for field in grouped_fields:
            if field in pattern['relationships']:
                field_data = pattern['relationships'][field]
                
                # Check if it's a dict without presentation
                if isinstance(field_data, dict):
                    if 'presentation' not in field_data or 'items' not in field_data:
                        results['issues'].append(
                            f"{pattern_id}: {field} missing card format wrapper"
                        )
                        results['status'] = 'FAIL'
                # Check if it's already card format
                elif not isinstance(field_data, dict):
                    results['issues'].append(
                        f"{pattern_id}: {field} is {type(field_data).__name__}, expected dict"
                    )
                    results['status'] = 'FAIL'
    
    return results


def main():
    """Run normalization with dry-run option."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Normalize contaminants grouped fields')
    parser.add_argument('--dry-run', action='store_true', help='Show what would change without modifying files')
    parser.add_argument('--validate-only', action='store_true', help='Only validate, do not modify')
    args = parser.parse_args()
    
    file_path = Path(__file__).resolve().parent.parent.parent / 'data/contaminants/Contaminants.yaml'
    
    print("=" * 80)
    print("CONTAMINANTS GROUPED FIELDS NORMALIZATION")
    print("=" * 80)
    print()
    
    if args.validate_only:
        print("🔍 VALIDATION ONLY MODE")
        results = validate_normalization(file_path)
        
        status_icon = '✅' if results['status'] == 'PASS' else '❌'
        print(f"\n{status_icon} VALIDATION: {results['status']}")
        if results['issues']:
            print(f"\n⚠️  Issues found: {len(results['issues'])}")
            for issue in results['issues'][:10]:
                print(f"  • {issue}")
            if len(results['issues']) > 10:
                print(f"  ... and {len(results['issues']) - 10} more")
        
        return
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified\n")
    
    # Normalize
    print("📦 NORMALIZING GROUPED FIELDS")
    print("-" * 80)
    
    if not args.dry_run:
        backup_file(file_path)
    
    modified, changes = normalize_contaminants_grouped_fields(file_path, dry_run=args.dry_run)
    
    print(f"Items modified: {modified}/98")
    if changes:
        print("\nChanges:")
        for change in changes[:10]:
            print(f"  • {change}")
        if len(changes) > 10:
            print(f"  ... and {len(changes) - 10} more")
    
    # Validate
    if not args.dry_run:
        print("\n🔍 VALIDATION")
        print("-" * 80)
        results = validate_normalization(file_path)
        
        status_icon = '✅' if results['status'] == 'PASS' else '❌'
        print(f"{status_icon} VALIDATION: {results['status']}")
        if results['issues']:
            for issue in results['issues'][:3]:
                print(f"  • {issue}")
            if len(results['issues']) > 3:
                print(f"  ... and {len(results['issues']) - 3} more")
        
        print("\n" + "=" * 80)
        if results['status'] == 'PASS':
            print("✅ NORMALIZATION COMPLETE - All grouped fields in card format")
        else:
            print("⚠️  NORMALIZATION COMPLETE - Some issues remain")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("🔍 DRY RUN COMPLETE - Run without --dry-run to apply changes")
        print("=" * 80)


if __name__ == '__main__':
    main()
