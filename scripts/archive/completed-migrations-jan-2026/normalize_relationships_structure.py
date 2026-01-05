#!/usr/bin/env python3
"""
Normalize Relationships Structure

Moves relationship fields from top level into relationships block.
Specifically handles:
- regulatory_standards (150 materials)
- health_effects (14 compounds)
"""

import yaml
from pathlib import Path
from typing import Dict
import shutil
from datetime import datetime


class RelationshipNormalizer:
    """Normalizes relationship field locations in source data"""
    
    # Fields that should be in relationships block
    RELATIONSHIP_FIELDS = {
        'regulatory_standards',
        'health_effects',
    }
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.stats = {
            'files_processed': 0,
            'items_fixed': 0,
            'fields_moved': 0,
        }
    
    def normalize_item(self, item_id: str, item_data: Dict) -> bool:
        """
        Normalize a single item's relationships
        
        Returns:
            True if changes were made
        """
        changed = False
        
        # Ensure relationships block exists
        if 'relationships' not in item_data:
            item_data['relationships'] = {}
        
        relationships = item_data['relationships']
        
        # Move relationship fields into relationships block
        for field_name in self.RELATIONSHIP_FIELDS:
            if field_name in item_data:
                # Move to relationships
                field_data = item_data.pop(field_name)
                
                # Wrap in proper structure
                if isinstance(field_data, list):
                    # Check if it's a list of objects or simple strings
                    if field_data and isinstance(field_data[0], dict):
                        # List of objects - wrap with presentation
                        relationships[field_name] = {
                            'presentation': 'card',
                            'items': field_data
                        }
                    else:
                        # Simple list - keep as is
                        relationships[field_name] = field_data
                else:
                    # Already a dict - keep structure
                    relationships[field_name] = field_data
                
                print(f"  ✓ Moved {field_name} into relationships block")
                self.stats['fields_moved'] += 1
                changed = True
        
        return changed
    
    def normalize_file(self, file_path: Path, items_key: str) -> int:
        """
        Normalize a single YAML file
        
        Returns:
            Number of items fixed
        """
        print(f"\n{'='*70}")
        print(f"📄 Processing: {file_path.name}")
        print(f"{'='*70}")
        
        # Load file
        with open(file_path) as f:
            data = yaml.safe_load(f)
        
        if items_key not in data:
            print(f"⚠️  No '{items_key}' key found, skipping")
            return 0
        
        items = data[items_key]
        items_fixed = 0
        
        # Process each item
        for item_id, item_data in items.items():
            if self.normalize_item(item_id, item_data):
                items_fixed += 1
        
        # Save changes
        if items_fixed > 0:
            if not self.dry_run:
                # Backup original
                backup_path = file_path.with_suffix('.yaml.bak')
                shutil.copy2(file_path, backup_path)
                print(f"\n💾 Backup created: {backup_path.name}")
                
                # Write normalized data
                with open(file_path, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                
                print(f"✅ Saved changes: {items_fixed} items normalized")
            else:
                print(f"\n🔍 DRY RUN: Would normalize {items_fixed} items")
        else:
            print(f"\n✅ No changes needed")
        
        self.stats['files_processed'] += 1
        self.stats['items_fixed'] += items_fixed
        
        return items_fixed
    
    def normalize_all(self):
        """Normalize all source data files"""
        print("\n" + "="*70)
        print("🔧 NORMALIZING RELATIONSHIP STRUCTURES")
        print("="*70)
        
        if self.dry_run:
            print("⚠️  DRY RUN MODE - No files will be modified")
        
        files_to_process = [
            ('data/materials/Materials.yaml', 'materials'),
            ('data/compounds/Compounds.yaml', 'compounds'),
            ('data/settings/Settings.yaml', 'settings'),
            ('data/contaminants/Contaminants.yaml', 'contaminants'),
        ]
        
        for file_path, items_key in files_to_process:
            path = Path(file_path)
            if path.exists():
                self.normalize_file(path, items_key)
            else:
                print(f"\n⚠️  File not found: {file_path}")
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print normalization summary"""
        print(f"\n{'='*70}")
        print("📊 NORMALIZATION SUMMARY")
        print(f"{'='*70}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Items fixed: {self.stats['items_fixed']}")
        print(f"Fields moved: {self.stats['fields_moved']}")
        
        if self.dry_run:
            print("\n⚠️  This was a DRY RUN - run again without --dry-run to apply changes")
        else:
            print("\n✅ Normalization complete!")
            print("\nNext steps:")
            print("1. Run: python3 scripts/migration/remove_generated_fields.py")
            print("2. Run: python3 scripts/validation/validate_source_schema.py")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Normalize relationship structures in source data')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    args = parser.parse_args()
    
    normalizer = RelationshipNormalizer(dry_run=args.dry_run)
    normalizer.normalize_all()


if __name__ == '__main__':
    main()
