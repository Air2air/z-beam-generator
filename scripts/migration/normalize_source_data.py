#!/usr/bin/env python3
"""
Source Data Normalization Script

Normalizes data structure across all domains:
1. Contaminants: Migrates visual_characteristics and laser_properties to relationships
2. Compounds: Removes null root fields that exist properly in relationships

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


def wrap_with_card_format(data: Any) -> Dict[str, Any]:
    """Wrap data in card format {presentation: 'card', items: [...]}."""
    if isinstance(data, list):
        return {'presentation': 'card', 'items': data}
    elif isinstance(data, dict):
        # Single dict becomes single-item array
        return {'presentation': 'card', 'items': [data]}
    else:
        return {'presentation': 'card', 'items': []}


def normalize_contaminants(file_path: Path, dry_run: bool = False) -> Tuple[int, List[str]]:
    """
    Migrate visual_characteristics and laser_properties from root to relationships.
    
    Returns:
        (items_modified, list_of_changes)
    """
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    
    patterns = data['contamination_patterns']
    modified_count = 0
    changes = []
    
    fields_to_migrate = ['visual_characteristics', 'laser_properties']
    
    for pattern_id, pattern in patterns.items():
        pattern_changes = []
        
        # Ensure relationships dict exists
        if 'relationships' not in pattern:
            pattern['relationships'] = {}
        
        for field in fields_to_migrate:
            # Check if field exists at root and has data
            if field in pattern and pattern[field] is not None:
                root_data = pattern[field]
                
                # Check if relationship field is null or missing
                rel_value = pattern['relationships'].get(field)
                if rel_value is None or not rel_value:
                    # Migrate: wrap with card format and move to relationships
                    pattern['relationships'][field] = wrap_with_card_format(root_data)
                    
                    # Remove from root
                    del pattern[field]
                    
                    pattern_changes.append(f"Migrated {field} to relationships")
            
            # Also clean up null values in relationships
            elif field in pattern['relationships'] and pattern['relationships'][field] is None:
                # Remove null relationship
                del pattern['relationships'][field]
                pattern_changes.append(f"Removed null {field} from relationships")
        
        if pattern_changes:
            modified_count += 1
            changes.append(f"{pattern_id}: {', '.join(pattern_changes)}")
    
    if not dry_run and modified_count > 0:
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    return modified_count, changes


def normalize_compounds(file_path: Path, dry_run: bool = False) -> Tuple[int, List[str]]:
    """
    Remove null root fields that exist properly in relationships.
    
    Returns:
        (items_modified, list_of_changes)
    """
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    
    compounds = data['compounds']
    modified_count = 0
    changes = []
    
    # Fields that should ONLY exist in relationships, not at root
    relationship_only_fields = [
        'health_effects',
        'chemical_properties',
        'environmental_impact',
        'detection_monitoring',
        'ppe_requirements',
        'emergency_response',
        'physical_properties'
    ]
    
    for compound_id, compound in compounds.items():
        compound_changes = []
        
        for field in relationship_only_fields:
            # Check if field exists at root with null value
            if field in compound and compound[field] is None:
                # Check if it exists properly in relationships
                if 'relationships' in compound and field in compound['relationships']:
                    rel_value = compound['relationships'][field]
                    if rel_value is not None and rel_value:
                        # Has valid relationship data, safe to remove null root field
                        del compound[field]
                        compound_changes.append(f"Removed null {field} from root")
        
        if compound_changes:
            modified_count += 1
            changes.append(f"{compound_id}: {', '.join(compound_changes)}")
    
    if not dry_run and modified_count > 0:
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    return modified_count, changes


def validate_normalization(base_path: Path) -> Dict[str, Any]:
    """Validate that normalization was successful."""
    results = {
        'materials': {'status': 'N/A', 'issues': []},
        'compounds': {'status': 'PASS', 'issues': []},
        'contaminants': {'status': 'PASS', 'issues': []},
        'settings': {'status': 'N/A', 'issues': []}
    }
    
    # Check Compounds - only check for duplicate fields that also exist in relationships
    with open(base_path / 'compounds/Compounds.yaml', 'r') as f:
        data = yaml.safe_load(f)
    
    relationship_fields = [
        'health_effects', 'chemical_properties', 'environmental_impact',
        'detection_monitoring', 'ppe_requirements', 'emergency_response', 'physical_properties'
    ]
    
    for compound_id, compound in data['compounds'].items():
        # Check for null root fields ONLY if they also exist in relationships (duplicate issue)
        if 'relationships' in compound:
            for field in relationship_fields:
                if field in compound and compound[field] is None:
                    if field in compound['relationships'] and compound['relationships'][field] is not None:
                        results['compounds']['issues'].append(
                            f"{compound_id}: null {field} at root but has data in relationships"
                        )
                        results['compounds']['status'] = 'FAIL'
    
    # Check Contaminants
    with open(base_path / 'contaminants/Contaminants.yaml', 'r') as f:
        data = yaml.safe_load(f)
    
    for pattern_id, pattern in data['contamination_patterns'].items():
        # Check that visual_characteristics and laser_properties are in relationships
        if 'visual_characteristics' in pattern and pattern['visual_characteristics'] is not None:
            results['contaminants']['issues'].append(f"{pattern_id}: visual_characteristics still at root")
            results['contaminants']['status'] = 'FAIL'
        
        if 'laser_properties' in pattern and pattern['laser_properties'] is not None:
            results['contaminants']['issues'].append(f"{pattern_id}: laser_properties still at root")
            results['contaminants']['status'] = 'FAIL'
        
        # Check that they're in relationships with card format
        if 'relationships' in pattern:
            for field in ['visual_characteristics', 'laser_properties']:
                if field in pattern['relationships']:
                    rel_data = pattern['relationships'][field]
                    if not isinstance(rel_data, dict) or 'presentation' not in rel_data or 'items' not in rel_data:
                        results['contaminants']['issues'].append(f"{pattern_id}: {field} not in card format")
                        results['contaminants']['status'] = 'FAIL'
    
    return results


def main():
    """Run normalization with dry-run option."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Normalize source data structure across domains')
    parser.add_argument('--dry-run', action='store_true', help='Show what would change without modifying files')
    parser.add_argument('--validate-only', action='store_true', help='Only validate, do not modify')
    args = parser.parse_args()
    
    base_path = Path(__file__).resolve().parent.parent.parent / 'data'
    
    print("=" * 80)
    print("SOURCE DATA NORMALIZATION")
    print("=" * 80)
    print()
    
    if args.validate_only:
        print("🔍 VALIDATION ONLY MODE")
        results = validate_normalization(base_path)
        
        print("\n📊 VALIDATION RESULTS:")
        for domain, result in results.items():
            status_icon = '✅' if result['status'] == 'PASS' else '⚠️' if result['status'] == 'N/A' else '❌'
            print(f"\n{status_icon} {domain.upper()}: {result['status']}")
            if result['issues']:
                for issue in result['issues'][:5]:
                    print(f"  • {issue}")
                if len(result['issues']) > 5:
                    print(f"  ... and {len(result['issues']) - 5} more issues")
        
        return
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified\n")
    
    # 1. Normalize Contaminants
    print("📦 CONTAMINANTS NORMALIZATION")
    print("-" * 80)
    contaminants_path = base_path / 'contaminants/Contaminants.yaml'
    
    if not args.dry_run:
        backup_file(contaminants_path)
    
    modified, changes = normalize_contaminants(contaminants_path, dry_run=args.dry_run)
    
    print(f"Items modified: {modified}/98")
    if changes:
        print("\nChanges:")
        for change in changes[:10]:
            print(f"  • {change}")
        if len(changes) > 10:
            print(f"  ... and {len(changes) - 10} more")
    
    # 2. Normalize Compounds
    print("\n📦 COMPOUNDS NORMALIZATION")
    print("-" * 80)
    compounds_path = base_path / 'compounds/Compounds.yaml'
    
    if not args.dry_run:
        backup_file(compounds_path)
    
    modified, changes = normalize_compounds(compounds_path, dry_run=args.dry_run)
    
    print(f"Items modified: {modified}/34")
    if changes:
        print("\nChanges:")
        for change in changes[:10]:
            print(f"  • {change}")
        if len(changes) > 10:
            print(f"  ... and {len(changes) - 10} more")
    
    # 3. Validate
    if not args.dry_run:
        print("\n🔍 VALIDATION")
        print("-" * 80)
        results = validate_normalization(base_path)
        
        all_pass = all(r['status'] in ['PASS', 'N/A'] for r in results.values())
        
        for domain, result in results.items():
            status_icon = '✅' if result['status'] == 'PASS' else '⚠️' if result['status'] == 'N/A' else '❌'
            print(f"{status_icon} {domain.upper()}: {result['status']}")
            if result['issues']:
                for issue in result['issues'][:3]:
                    print(f"  • {issue}")
                if len(result['issues']) > 3:
                    print(f"  ... and {len(result['issues']) - 3} more")
        
        print("\n" + "=" * 80)
        if all_pass:
            print("✅ NORMALIZATION COMPLETE - All domains normalized")
        else:
            print("⚠️  NORMALIZATION COMPLETE - Some issues remain")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("🔍 DRY RUN COMPLETE - Run without --dry-run to apply changes")
        print("=" * 80)


if __name__ == '__main__':
    main()
