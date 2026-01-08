#!/usr/bin/env python3
"""
Add sectionMetadata to all _section blocks in source data.

Most sections already have sectionTitle and sectionDescription, 
but are missing the sectionMetadata field.

Usage:
    python3 scripts/enrichment/add_section_metadata_field.py --dry-run
    python3 scripts/enrichment/add_section_metadata_field.py
"""

import yaml
import argparse
from pathlib import Path
import tempfile
import shutil

DOMAIN_FILES = {
    'materials': ('data/materials/Materials.yaml', 'materials'),
    'contaminants': ('data/contaminants/Contaminants.yaml', 'contaminants'),
    'compounds': ('data/compounds/Compounds.yaml', 'compounds'),
    'settings': ('data/settings/Settings.yaml', 'settings')
}


def add_metadata_field(item_data: dict, domain: str) -> tuple[dict, int]:
    """
    Add sectionMetadata field to all _section blocks that are missing it.
    
    Returns:
        (modified_item, fields_added_count)
    """
    fields_added = 0
    
    relationships = item_data.get('relationships', {})
    if not relationships:
        return item_data, fields_added
    
    for group_name, group_data in relationships.items():
        if not isinstance(group_data, dict):
            continue
            
        for section_name, section_data in group_data.items():
            if not isinstance(section_data, dict):
                continue
            
            # Check if _section exists
            if '_section' not in section_data:
                continue
            
            _section = section_data['_section']
            
            # Add sectionMetadata if missing
            if 'sectionMetadata' not in _section:
                _section['sectionMetadata'] = {
                    'relationship_type': section_name
                }
                fields_added += 1
    
    return item_data, fields_added


def process_domain(domain: str, dry_run: bool = False) -> dict:
    """
    Add sectionMetadata field to all sections in a domain.
    
    Returns:
        Statistics dict
    """
    file_path, items_key = DOMAIN_FILES[domain]
    
    print(f"\n{'='*80}")
    print(f"Processing {domain.upper()}: {file_path}")
    print(f"{'='*80}")
    
    # Load data
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    items = data.get(items_key, {})
    
    items_processed = 0
    fields_added = 0
    
    for item_id, item_data in items.items():
        modified_item, added_count = add_metadata_field(item_data, domain)
        
        if added_count > 0:
            items_processed += 1
            fields_added += added_count
    
    if fields_added > 0:
        print(f"  Items with updates: {items_processed}")
        print(f"  Fields added: {fields_added}")
    else:
        print(f"  ✅ All sections already have sectionMetadata")
    
    # Save if not dry-run
    if not dry_run and fields_added > 0:
        temp_fd, temp_path = tempfile.mkstemp(
            suffix='.yaml',
            dir=Path(file_path).parent,
            text=True
        )
        
        try:
            with open(temp_fd, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            # Atomic replace
            shutil.move(temp_path, file_path)
            print(f"  💾 Saved {file_path}")
            
        except Exception as e:
            Path(temp_path).unlink(missing_ok=True)
            raise e
    
    return {
        'items_processed': items_processed,
        'fields_added': fields_added
    }


def main():
    parser = argparse.ArgumentParser(description='Add sectionMetadata field to all _section blocks')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without saving')
    parser.add_argument('--domain', choices=['materials', 'contaminants', 'compounds', 'settings'],
                        help='Process specific domain only')
    
    args = parser.parse_args()
    
    print("="*80)
    print("ADD SECTION METADATA FIELD TO SOURCE DATA")
    print("="*80)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'WRITE'}")
    
    # Process domains
    domains = [args.domain] if args.domain else list(DOMAIN_FILES.keys())
    
    total_items = 0
    total_fields = 0
    
    for domain in domains:
        stats = process_domain(domain, args.dry_run)
        total_items += stats['items_processed']
        total_fields += stats['fields_added']
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"  Items processed: {total_items}")
    print(f"  Fields added: {total_fields}")
    
    if args.dry_run:
        print("\n⚠️  DRY RUN - No files were modified")
        print("   Run without --dry-run to apply changes")
    else:
        print("\n✅ sectionMetadata fields added to source data")


if __name__ == '__main__':
    main()
