#!/usr/bin/env python3
"""
Remove Generated Fields from Source Data

Removes fields that should only exist in frontmatter output, not source data.
Removes:
- card (340 occurrences)
- description (340 occurrences)
- contamination (153 occurrences)
- components (152 occurrences)
- eeat (132 occurrences)
- voice_enhanced (132 occurrences)
- meta_description (126 occurrences)
- page_title (126 occurrences)
- settings_description (16 occurrences)
"""

import yaml
from pathlib import Path
from typing import Dict, Set
import shutil


class GeneratedFieldRemover:
    """Removes generated/export-only fields from source data"""
    
    # Fields that should NOT exist in source data
    GENERATED_FIELDS = {
        'card',
        'description', 
        'contamination',
        'components',
        'eeat',
        'voice_enhanced',
        'meta_description',
        'page_title',
        'settings_description',
    }
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.stats = {
            'files_processed': 0,
            'items_cleaned': 0,
            'fields_removed': 0,
        }
        self.removed_fields = {}
    
    def clean_item(self, item_id: str, item_data: Dict) -> int:
        """
        Remove generated fields from a single item
        
        Returns:
            Number of fields removed
        """
        removed = 0
        
        for field_name in self.GENERATED_FIELDS:
            if field_name in item_data:
                del item_data[field_name]
                removed += 1
                
                # Track for stats
                if field_name not in self.removed_fields:
                    self.removed_fields[field_name] = 0
                self.removed_fields[field_name] += 1
        
        return removed
    
    def clean_file(self, file_path: Path, items_key: str) -> tuple[int, int]:
        """
        Clean a single YAML file
        
        Returns:
            (items_cleaned, fields_removed)
        """
        print(f"\n{'='*70}")
        print(f"📄 Processing: {file_path.name}")
        print(f"{'='*70}")
        
        # Load file
        with open(file_path) as f:
            data = yaml.safe_load(f)
        
        if items_key not in data:
            print(f"⚠️  No '{items_key}' key found, skipping")
            return 0, 0
        
        items = data[items_key]
        items_cleaned = 0
        fields_removed = 0
        
        # Process each item
        for item_id, item_data in items.items():
            removed = self.clean_item(item_id, item_data)
            if removed > 0:
                items_cleaned += 1
                fields_removed += removed
        
        # Save changes
        if fields_removed > 0:
            print(f"\n🧹 Removed {fields_removed} generated fields from {items_cleaned} items")
            
            if not self.dry_run:
                # Backup original
                backup_path = file_path.with_suffix('.yaml.bak2')
                shutil.copy2(file_path, backup_path)
                print(f"💾 Backup created: {backup_path.name}")
                
                # Write cleaned data
                with open(file_path, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                
                print(f"✅ Saved changes")
            else:
                print(f"🔍 DRY RUN: Would remove {fields_removed} fields")
        else:
            print(f"\n✅ No generated fields found")
        
        self.stats['files_processed'] += 1
        self.stats['items_cleaned'] += items_cleaned
        self.stats['fields_removed'] += fields_removed
        
        return items_cleaned, fields_removed
    
    def clean_all(self):
        """Clean all source data files"""
        print("\n" + "="*70)
        print("🧹 REMOVING GENERATED FIELDS FROM SOURCE DATA")
        print("="*70)
        
        if self.dry_run:
            print("⚠️  DRY RUN MODE - No files will be modified")
        
        print("\nFields to remove:")
        for field in sorted(self.GENERATED_FIELDS):
            print(f"  - {field}")
        
        files_to_process = [
            ('data/materials/Materials.yaml', 'materials'),
            ('data/contaminants/Contaminants.yaml', 'contaminants'),
            ('data/settings/Settings.yaml', 'settings'),
            ('data/compounds/Compounds.yaml', 'compounds'),
        ]
        
        for file_path, items_key in files_to_process:
            path = Path(file_path)
            if path.exists():
                self.clean_file(path, items_key)
            else:
                print(f"\n⚠️  File not found: {file_path}")
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print cleaning summary"""
        print(f"\n{'='*70}")
        print("📊 CLEANING SUMMARY")
        print(f"{'='*70}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Items cleaned: {self.stats['items_cleaned']}")
        print(f"Total fields removed: {self.stats['fields_removed']}")
        
        if self.removed_fields:
            print("\nFields removed by type:")
            for field, count in sorted(self.removed_fields.items(), key=lambda x: -x[1]):
                print(f"  {field}: {count}")
        
        if self.dry_run:
            print("\n⚠️  This was a DRY RUN - run again without --dry-run to apply changes")
        else:
            print("\n✅ Cleaning complete!")
            print("\nNext steps:")
            print("1. Run: python3 scripts/validation/validate_source_schema.py")
            print("2. Run: python3 run.py --export --domain materials")
            print("3. Verify frontmatter still has all data (enrichers will regenerate)")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Remove generated fields from source data')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    args = parser.parse_args()
    
    remover = GeneratedFieldRemover(dry_run=args.dry_run)
    remover.clean_all()


if __name__ == '__main__':
    main()
