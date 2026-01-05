#!/usr/bin/env python3
"""
Author Denormalization Migration Script
Author: AI Assistant
Date: December 23, 2025

Purpose: Convert full author objects to ID-only references across all domains.

Current State:
  author:
    id: 2
    name: Alessandro Moretti
    country: Italy
    [... 12+ more fields]

Target State:
  author:
    id: 2

Impact: Eliminates 6,570+ duplicated data points across 438 files.
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List
import copy

class AuthorDenormalizer:
    """Migrates author objects to ID-only references."""
    
    def __init__(self):
        self.domains = {
            'materials': 'data/materials/Materials.yaml',
            'contaminants': 'data/contaminants/Contaminants.yaml',
            'compounds': 'data/compounds/Compounds.yaml',
            'settings': 'data/settings/Settings.yaml'
        }
        self.items_keys = {
            'materials': 'materials',
            'contaminants': 'contamination_patterns',
            'compounds': 'compounds',
            'settings': 'settings'
        }
        self.stats = {
            'files_processed': 0,
            'authors_converted': 0,
            'fields_removed': 0,
            'errors': []
        }
    
    def load_yaml(self, path: str) -> Dict[str, Any]:
        """Load YAML file."""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def save_yaml(self, path: str, data: Dict[str, Any]) -> None:
        """Save YAML file with proper formatting."""
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, 
                     sort_keys=False, width=120)
    
    def denormalize_author(self, author_obj: Any) -> Dict[str, int]:
        """Convert full author object to ID-only reference."""
        if author_obj is None:
            return None
        
        if isinstance(author_obj, dict):
            author_id = author_obj.get('id')
            if author_id is None:
                self.stats['errors'].append(f"Author object missing 'id' field: {author_obj}")
                return author_obj
            
            # Count fields being removed
            field_count = len(author_obj) - 1  # Subtract 1 for 'id' field
            self.stats['fields_removed'] += field_count
            
            # Return ID-only reference
            return {'id': author_id}
        
        # If it's already just an ID or other format, return as-is
        return author_obj
    
    def process_domain(self, domain: str, dry_run: bool = False) -> None:
        """Process all items in a domain."""
        source_path = self.domains[domain]
        items_key = self.items_keys[domain]
        
        print(f"\n{'='*70}")
        print(f"Processing {domain.upper()}")
        print(f"{'='*70}")
        print(f"Source: {source_path}")
        
        # Load data
        try:
            data = self.load_yaml(source_path)
        except Exception as e:
            self.stats['errors'].append(f"{domain}: Failed to load - {e}")
            print(f"❌ Failed to load: {e}")
            return
        
        if items_key not in data:
            self.stats['errors'].append(f"{domain}: Missing '{items_key}' key")
            print(f"❌ Missing '{items_key}' key in data")
            return
        
        items = data[items_key]
        item_count = len(items)
        converted_count = 0
        
        # Process each item
        for item_id, item_data in items.items():
            if 'author' in item_data:
                original_author = copy.deepcopy(item_data['author'])
                new_author = self.denormalize_author(item_data['author'])
                
                # Check if actually changed
                if new_author != original_author:
                    item_data['author'] = new_author
                    converted_count += 1
                    
                    if dry_run:
                        print(f"  📝 {item_id}: Would convert")
                        print(f"      From: {original_author}")
                        print(f"      To:   {new_author}")
        
        # Save if not dry run
        if not dry_run and converted_count > 0:
            try:
                self.save_yaml(source_path, data)
                print(f"✅ Saved {source_path}")
            except Exception as e:
                self.stats['errors'].append(f"{domain}: Failed to save - {e}")
                print(f"❌ Failed to save: {e}")
                return
        
        # Update stats
        self.stats['files_processed'] += 1
        self.stats['authors_converted'] += converted_count
        
        print(f"📊 Items: {item_count}")
        print(f"✅ Converted: {converted_count}")
        
        if dry_run and converted_count > 0:
            print(f"🔍 DRY RUN - No changes saved")
    
    def run(self, dry_run: bool = False) -> None:
        """Run migration across all domains."""
        print("="*70)
        print("AUTHOR DENORMALIZATION MIGRATION")
        print("="*70)
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        print()
        
        # Process each domain
        for domain in self.domains.keys():
            self.process_domain(domain, dry_run)
        
        # Print summary
        print("\n" + "="*70)
        print("MIGRATION SUMMARY")
        print("="*70)
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Authors converted: {self.stats['authors_converted']}")
        print(f"Fields removed: {self.stats['fields_removed']}")
        
        if self.stats['errors']:
            print(f"\n⚠️  Errors: {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                print(f"  - {error}")
        else:
            print(f"\n✅ No errors")
        
        if not dry_run:
            print(f"\n✅ Migration complete!")
            print(f"   Data reduction: {self.stats['fields_removed']} fields eliminated")
        else:
            print(f"\n🔍 Dry run complete - no changes saved")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert full author objects to ID-only references'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without saving'
    )
    
    args = parser.parse_args()
    
    migrator = AuthorDenormalizer()
    migrator.run(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
