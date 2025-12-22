"""
Relationship Migration Script

Normalizes existing full relationship objects to reference-only format.

Usage:
    # Dry run (preview changes)
    python3 scripts/migration/normalize_relationships.py --domain compounds --dry-run
    
    # Apply changes
    python3 scripts/migration/normalize_relationships.py --domain compounds
    
    # Migrate all domains
    python3 scripts/migration/normalize_relationships.py --all
"""

import yaml
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.relationships.resolver import RelationshipNormalizer


class RelationshipMigrator:
    """Migrates relationship arrays from full objects to normalized references."""
    
    def __init__(self, domain: str, data_dir: str = 'data'):
        self.domain = domain
        self.data_dir = Path(data_dir)
        self.normalizer = RelationshipNormalizer()
        
        # Domain file mapping
        self.domain_files = {
            'materials': ('materials/Materials.yaml', 'materials'),
            'contaminants': ('contaminants/Contaminants.yaml', 'contamination_patterns'),
            'compounds': ('compounds/Compounds.yaml', 'compounds'),
            'settings': ('settings/Settings.yaml', 'settings')
        }
        
    def load_data(self) -> Dict[str, Any]:
        """Load domain data file."""
        if self.domain not in self.domain_files:
            raise ValueError(f"Unknown domain: {self.domain}")
            
        file_path, items_key = self.domain_files[self.domain]
        full_path = self.data_dir / file_path
        
        with open(full_path) as f:
            data = yaml.safe_load(f)
            
        return data
        
    def save_data(self, data: Dict[str, Any], backup: bool = True):
        """Save normalized data file with optional backup."""
        file_path, items_key = self.domain_files[self.domain]
        full_path = self.data_dir / file_path
        
        # Create backup if requested
        if backup:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = full_path.parent / f"{full_path.stem}_backup_{timestamp}.yaml"
            with open(backup_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            print(f"✅ Backup created: {backup_path}")
            
        # Save normalized data
        with open(full_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        print(f"✅ Saved normalized data: {full_path}")
        
    def normalize_domain(self, dry_run: bool = True) -> Dict[str, int]:
        """
        Normalize all relationship arrays in domain.
        
        Args:
            dry_run: If True, preview changes without saving
            
        Returns:
            Stats dict with counts
        """
        print(f"\n{'='*80}")
        print(f"NORMALIZING RELATIONSHIPS: {self.domain.upper()}")
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        print(f"{'='*80}\n")
        
        # Load data
        data = self.load_data()
        file_path, items_key = self.domain_files[self.domain]
        items = data[items_key]
        
        stats = {
            'items_processed': 0,
            'relationship_fields_found': 0,
            'references_normalized': 0,
            'references_skipped': 0,  # Already normalized
            'bytes_saved': 0
        }
        
        # Process each item
        for item_id, item in items.items():
            if 'relationships' not in item:
                continue
                
            stats['items_processed'] += 1
            relationships = item['relationships']
            original_size = len(yaml.dump(relationships, default_flow_style=False))
            
            # Normalize each relationship field
            for rel_field, rel_list in list(relationships.items()):
                if not isinstance(rel_list, list) or not rel_list:
                    continue
                    
                stats['relationship_fields_found'] += 1
                
                # Check if already normalized
                if self._is_normalized(rel_list):
                    stats['references_skipped'] += len(rel_list)
                    continue
                    
                # Normalize
                normalized = self.normalizer.normalize_relationships(rel_list)
                relationships[rel_field] = normalized
                stats['references_normalized'] += len(normalized)
                
                if dry_run:
                    print(f"  {item_id}.{rel_field}:")
                    print(f"    Before: {rel_list[0]}")
                    print(f"    After:  {normalized[0]}")
                    print()
                    
            # Calculate size savings
            new_size = len(yaml.dump(relationships, default_flow_style=False))
            stats['bytes_saved'] += (original_size - new_size)
            
        # Save if not dry run
        if not dry_run and stats['references_normalized'] > 0:
            self.save_data(data, backup=True)
            
        # Print stats
        print(f"\n{'='*80}")
        print("MIGRATION STATISTICS")
        print(f"{'='*80}")
        print(f"Items processed:           {stats['items_processed']}")
        print(f"Relationship fields found: {stats['relationship_fields_found']}")
        print(f"References normalized:     {stats['references_normalized']}")
        print(f"References skipped:        {stats['references_skipped']} (already normalized)")
        print(f"Bytes saved:               {stats['bytes_saved']:,} ({stats['bytes_saved']/1024:.1f} KB)")
        
        if stats['bytes_saved'] > 0:
            reduction_pct = (stats['bytes_saved'] / (stats['bytes_saved'] + new_size)) * 100
            print(f"Size reduction:            {reduction_pct:.1f}%")
            
        return stats
        
    def _is_normalized(self, rel_list: List[Dict[str, Any]]) -> bool:
        """Check if relationship list is already normalized (minimal format)."""
        if not rel_list:
            return True
            
        first_rel = rel_list[0]
        
        # Normalized refs have only id + context fields
        # Full objects have title, url, category
        has_derived_fields = any(f in first_rel for f in ['title', 'url', 'category'])
        
        return not has_derived_fields


def main():
    parser = argparse.ArgumentParser(
        description='Normalize relationship arrays to reference-only format'
    )
    parser.add_argument(
        '--domain',
        choices=['materials', 'contaminants', 'compounds', 'settings'],
        help='Domain to migrate'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Migrate all domains'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without saving'
    )
    
    args = parser.parse_args()
    
    if not args.domain and not args.all:
        parser.error("Must specify --domain or --all")
        
    domains = ['materials', 'contaminants', 'compounds', 'settings'] if args.all else [args.domain]
    
    # Migrate each domain
    total_stats = {
        'items_processed': 0,
        'relationship_fields_found': 0,
        'references_normalized': 0,
        'references_skipped': 0,
        'bytes_saved': 0
    }
    
    for domain in domains:
        migrator = RelationshipMigrator(domain)
        stats = migrator.normalize_domain(dry_run=args.dry_run)
        
        # Accumulate totals
        for key in total_stats:
            total_stats[key] += stats[key]
            
    # Print total stats if multiple domains
    if len(domains) > 1:
        print(f"\n{'='*80}")
        print("TOTAL STATISTICS (ALL DOMAINS)")
        print(f"{'='*80}")
        print(f"Items processed:           {total_stats['items_processed']}")
        print(f"Relationship fields found: {total_stats['relationship_fields_found']}")
        print(f"References normalized:     {total_stats['references_normalized']}")
        print(f"References skipped:        {total_stats['references_skipped']}")
        print(f"Bytes saved:               {total_stats['bytes_saved']:,} ({total_stats['bytes_saved']/1024:.1f} KB)")
        

if __name__ == '__main__':
    main()
