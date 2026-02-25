#!/usr/bin/env python3
"""
Add presentation field to all relationship entries across all domains.

This script adds 'presentation: card' to all relationship entries in:
- Materials.yaml (contaminated_by, produces_compounds)
- Compounds.yaml (produced_from_contaminants, produced_from_materials)
- Contaminants.yaml (produces_compounds, found_on_materials)
- Settings.yaml (optimized_for_materials, removes_contaminants)

Usage:
    python3 scripts/maintenance/add_presentation_field.py --dry-run
    python3 scripts/maintenance/add_presentation_field.py
"""

import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Any
import shutil
from datetime import datetime


class PresentationFieldAdder:
    """Add presentation field to relationship entries."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.stats = {
            'materials': {'files': 0, 'relationships': 0, 'entries_updated': 0},
            'compounds': {'files': 0, 'relationships': 0, 'entries_updated': 0},
            'contaminants': {'files': 0, 'relationships': 0, 'entries_updated': 0},
            'settings': {'files': 0, 'relationships': 0, 'entries_updated': 0}
        }
        
        self.data_files = {
            'materials': Path('data/materials/Materials.yaml'),
            'compounds': Path('data/compounds/Compounds.yaml'),
            'contaminants': Path('data/contaminants/Contaminants.yaml'),
            'settings': Path('data/settings/Settings.yaml')
        }
    
    def backup_file(self, file_path: Path) -> Path:
        """Create backup of file before modification."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = file_path.with_suffix(f'.backup_{timestamp}.yaml')
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def add_presentation_to_entry(self, entry: Dict[str, Any]) -> bool:
        """Add presentation field to a relationship entry if not present."""
        if 'presentation' not in entry:
            entry['presentation'] = 'card'
            return True
        return False
    
    def process_relationships(self, item_data: Dict[str, Any], domain: str) -> int:
        """Process relationships for a single item."""
        entries_updated = 0
        
        relationships = item_data.get('relationships', {})
        if not relationships:
            return 0
        
        for rel_key, rel_items in relationships.items():
            if not isinstance(rel_items, list):
                continue
            
            self.stats[domain]['relationships'] += 1
            
            for entry in rel_items:
                if isinstance(entry, dict):
                    if self.add_presentation_to_entry(entry):
                        entries_updated += 1
        
        return entries_updated
    
    def process_domain(self, domain: str, file_path: Path) -> bool:
        """Process a single domain data file."""
        if not file_path.exists():
            print(f"⚠️  {domain}: File not found at {file_path}")
            return False
        
        print(f"\n📊 Processing {domain.upper()}")
        print(f"   File: {file_path}")
        
        # Load data
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Get top-level key (materials, compounds, contaminants, settings)
        top_key = domain if domain in data else list(data.keys())[0]
        items = data[top_key]
        
        if not items:
            print(f"   No items found")
            return False
        
        self.stats[domain]['files'] = 1
        total_entries_updated = 0
        
        # Process each item
        for item_id, item_data in items.items():
            entries_updated = self.process_relationships(item_data, domain)
            total_entries_updated += entries_updated
        
        self.stats[domain]['entries_updated'] = total_entries_updated
        
        print(f"   Items processed: {len(items)}")
        print(f"   Entries updated: {total_entries_updated}")
        
        # Save if not dry-run
        if not self.dry_run and total_entries_updated > 0:
            # Create backup
            backup_path = self.backup_file(file_path)
            print(f"   ✅ Backup created: {backup_path.name}")
            
            # Save updated data
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            print(f"   ✅ Updated file saved")
        elif self.dry_run and total_entries_updated > 0:
            print(f"   🔍 DRY RUN: Would update {total_entries_updated} entries")
        else:
            print(f"   ℹ️  No updates needed (all entries already have presentation field)")
        
        return True
    
    def run(self):
        """Process all domain files."""
        print("=" * 70)
        print("📝 ADD PRESENTATION FIELD TO RELATIONSHIPS")
        print("=" * 70)
        
        if self.dry_run:
            print("🔍 DRY RUN MODE - No files will be modified")
        
        # Process each domain
        for domain, file_path in self.data_files.items():
            self.process_domain(domain, file_path)
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        
        total_entries = sum(s['entries_updated'] for s in self.stats.values())
        total_relationships = sum(s['relationships'] for s in self.stats.values())
        
        for domain, stats in self.stats.items():
            if stats['files'] > 0:
                print(f"{domain.upper()}:")
                print(f"   Relationship types processed: {stats['relationships']}")
                print(f"   Entries updated: {stats['entries_updated']}")
        
        print(f"\nTOTAL ENTRIES UPDATED: {total_entries}")
        print(f"TOTAL RELATIONSHIP TYPES: {total_relationships}")
        
        if self.dry_run:
            print("\n🔍 This was a DRY RUN - no files were modified")
            print("   Run without --dry-run to apply changes")
        else:
            print(f"\n✅ All files updated successfully")
            print(f"   Backups created with timestamp suffix")
        
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Add presentation field to all relationship entries"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    
    args = parser.parse_args()
    
    adder = PresentationFieldAdder(dry_run=args.dry_run)
    adder.run()


if __name__ == '__main__':
    main()
