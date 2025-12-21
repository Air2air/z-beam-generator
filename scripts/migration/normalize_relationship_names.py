"""
Normalize Relationship Field Names

Implements consistent naming convention:
- Pattern: {action}_{direction}_{content_type}
- Active present-tense verbs
- Clear directionality (from, on, by, for)
- Semantically explicit

Migrations:
- Compounds: produced_by_contaminants → produced_from_contaminants
- Compounds: produced_by_materials → produced_from_materials
- Contaminants: applicable_materials → found_on_materials
- Materials: applicable_contaminants → contaminated_by
- Settings: applicable_materials → optimized_for_materials
- Settings: target_contaminants → removes_contaminants
"""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


# Mapping of old names to new names by domain
FIELD_MIGRATIONS = {
    'compounds': {
        'produced_by_contaminants': 'produced_from_contaminants',
        'produced_by_materials': 'produced_from_materials',
    },
    'contaminants': {
        'applicable_materials': 'found_on_materials',
        # 'produces_compounds' stays the same
    },
    'materials': {
        'applicable_contaminants': 'contaminated_by',
        # 'produces_compounds' stays the same
    },
    'settings': {
        'applicable_materials': 'optimized_for_materials',
        'target_contaminants': 'removes_contaminants',
    }
}


def create_backup(file_path: Path) -> Path:
    """Create timestamped backup of file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = file_path.parent / f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
    
    with open(file_path) as f:
        data = f.read()
    
    with open(backup_path, 'w') as f:
        f.write(data)
    
    print(f"✅ Backup created: {backup_path}")
    return backup_path


def rename_relationship_fields(data: Dict[str, Any], domain: str) -> tuple[Dict[str, Any], int]:
    """
    Rename relationship fields according to migration map.
    
    Returns:
        (modified_data, count_of_renames)
    """
    migrations = FIELD_MIGRATIONS.get(domain, {})
    if not migrations:
        return data, 0
    
    items_key = {
        'compounds': 'compounds',
        'contaminants': 'contaminants',
        'materials': 'materials',
        'settings': 'settings'
    }.get(domain)
    
    if not items_key or items_key not in data:
        return data, 0
    
    rename_count = 0
    items = data[items_key]
    
    for item_id, item_data in items.items():
        if 'relationships' not in item_data:
            continue
        
        relationships = item_data['relationships']
        
        # Rename fields according to migration map
        for old_name, new_name in migrations.items():
            if old_name in relationships:
                relationships[new_name] = relationships.pop(old_name)
                rename_count += 1
                print(f"  Renamed: {item_id}.relationships.{old_name} → {new_name}")
    
    return data, rename_count


def migrate_domain(domain: str, dry_run: bool = False) -> None:
    """Migrate relationship names for a single domain."""
    data_dir = Path('data') / domain
    file_name = f"{domain.capitalize()}.yaml"
    file_path = data_dir / file_name
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"\n{'='*80}")
    print(f"NORMALIZING RELATIONSHIP NAMES: {domain.upper()}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'='*80}\n")
    
    # Load data
    with open(file_path) as f:
        data = yaml.safe_load(f)
    
    # Rename fields
    modified_data, rename_count = rename_relationship_fields(data, domain)
    
    if rename_count == 0:
        print(f"  No relationship fields to rename in {domain}")
        return
    
    # Save or show preview
    if dry_run:
        print(f"\n📋 Preview: {rename_count} fields would be renamed")
    else:
        # Create backup
        create_backup(file_path)
        
        # Save modified data
        with open(file_path, 'w') as f:
            yaml.dump(modified_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        print(f"✅ Saved normalized data: {file_path}")
    
    print(f"\n{'='*80}")
    print(f"MIGRATION STATISTICS")
    print(f"{'='*80}")
    print(f"Fields renamed: {rename_count}")
    print()


def main():
    """Run migration on all domains."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Normalize relationship field names')
    parser.add_argument('--domain', choices=['compounds', 'contaminants', 'materials', 'settings'],
                       help='Specific domain to migrate')
    parser.add_argument('--all', action='store_true',
                       help='Migrate all domains')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview changes without modifying files')
    
    args = parser.parse_args()
    
    if args.all:
        domains = ['compounds', 'contaminants', 'materials', 'settings']
    elif args.domain:
        domains = [args.domain]
    else:
        print("Error: Specify --domain or --all")
        parser.print_help()
        return
    
    total_renames = 0
    
    for domain in domains:
        migrate_domain(domain, args.dry_run)
    
    print(f"\n{'='*80}")
    print(f"MIGRATION COMPLETE")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
