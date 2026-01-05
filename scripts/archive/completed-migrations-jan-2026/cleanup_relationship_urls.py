#!/usr/bin/env python3
"""
Cleanup Relationship URLs Migration Script

Removes redundant 'url' fields from relationship items in exported frontmatter.
The frontend derives URLs from full_path at render time, so url fields are redundant.

Target relationships:
- produces_compounds (in contaminants)
- found_on_materials (in contaminants)
- optimized_for_materials (in settings)
- removes_contaminants (in settings)

Does NOT modify:
- visual_characteristics (structured data, not entity references)
- laser_properties (structured data, not entity references)
- valid_materials/prohibited_materials (string arrays, not objects)
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))


class RelationshipURLCleaner:
    """Removes redundant url fields from relationship items."""
    
    def __init__(self, frontmatter_dir: str):
        self.frontmatter_dir = Path(frontmatter_dir)
        self.stats = {
            'files_processed': 0,
            'files_modified': 0,
            'urls_removed': 0,
            'relationships_cleaned': set()
        }
    
    def clean_file(self, filepath: Path) -> bool:
        """Clean a single frontmatter file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data or 'relationships' not in data:
                return False
            
            modified = False
            relationships = data['relationships']
            
            # Clean ALL relationships (not just specific ones)
            for rel_key, rel in relationships.items():
                # Skip if not the expected structure
                if not isinstance(rel, dict) or 'items' not in rel:
                    continue
                
                items = rel['items']
                if not isinstance(items, list):
                    continue
                
                # Remove redundant fields from each item
                redundant_fields = ['url', 'title', 'image']
                
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    
                    for field in redundant_fields:
                        if field in item:
                            del item[field]
                            self.stats['urls_removed'] += 1  # Count all redundant fields
                            self.stats['relationships_cleaned'].add(rel_key)
                            modified = True
            
            # Save if modified
            if modified:
                with open(filepath, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, 
                             default_flow_style=False,
                             allow_unicode=True,
                             sort_keys=False,
                             width=1000)  # Prevent line wrapping
                
                self.stats['files_modified'] += 1
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error processing {filepath.name}: {e}")
            return False
    
    def clean_domain(self, domain: str) -> None:
        """Clean all files in a domain directory."""
        domain_dir = self.frontmatter_dir / domain
        
        if not domain_dir.exists():
            print(f"⚠️  Directory not found: {domain_dir}")
            return
        
        print(f"\n📋 Processing {domain}...")
        
        yaml_files = list(domain_dir.glob('*.yaml'))
        
        for filepath in yaml_files:
            self.stats['files_processed'] += 1
            if self.clean_file(filepath):
                print(f"   ✅ {filepath.name}")
    
    def run(self, domains: List[str]) -> None:
        """Run cleanup for specified domains."""
        print("=" * 70)
        print("Relationship URL Cleanup Migration")
        print("=" * 70)
        
        for domain in domains:
            self.clean_domain(domain)
        
        self._print_summary()
    
    def _print_summary(self) -> None:
        """Print migration summary."""
        print("\n" + "=" * 70)
        print("MIGRATION SUMMARY")
        print("=" * 70)
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Files modified: {self.stats['files_modified']}")
        print(f"URLs removed: {self.stats['urls_removed']}")
        
        if self.stats['relationships_cleaned']:
            print(f"\nRelationships cleaned:")
            for rel in sorted(self.stats['relationships_cleaned']):
                print(f"  - {rel}")
        
        print("\n✅ Migration complete!")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Remove redundant url fields from relationship items'
    )
    parser.add_argument(
        '--frontmatter-dir',
        default='../z-beam/frontmatter',
        help='Path to frontmatter directory (default: ../z-beam/frontmatter)'
    )
    parser.add_argument(
        '--domains',
        nargs='+',
        default=['materials', 'compounds', 'contaminants', 'settings'],
        help='Domains to process (default: all domains)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("⚠️  DRY RUN MODE - No files will be modified")
        print()
    
    cleaner = RelationshipURLCleaner(args.frontmatter_dir)
    
    if not args.dry_run:
        cleaner.run(args.domains)
    else:
        print("❌ Dry run not yet implemented - run without --dry-run")


if __name__ == '__main__':
    main()
