#!/usr/bin/env python3
"""
Enrich Author Metadata in Materials.yaml

Reads Materials.yaml and enriches minimal author data (id only) with full metadata
from data/authors/registry.py. This migration ensures Materials.yaml has complete
author information for display, evaluation, and export.

Created: December 30, 2025 - Author Attribution Refactor
Policy: Generate to Data, Not Enrichers (Core Principle 0.5)

Usage:
    # Dry run (safe - shows what would change)
    python3 scripts/data/enrich_author_metadata.py
    
    # Execute changes
    python3 scripts/data/enrich_author_metadata.py --execute
    
    # Process specific domain
    python3 scripts/data/enrich_author_metadata.py --domain materials --execute
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data.authors.registry import get_author
from shared.utils.yaml_utils import load_yaml, save_yaml


def enrich_author_field(author_field: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich minimal author field with full metadata from registry.
    
    Args:
        author_field: Minimal author dict (may only have 'id')
        
    Returns:
        Enriched author dict with name, country, and other essential fields
    """
    # Validate input
    if not isinstance(author_field, dict):
        print(f"⚠️  Author field not a dict: {type(author_field)}")
        return author_field
    
    if 'id' not in author_field:
        print("⚠️  Author field missing 'id' - cannot enrich")
        return author_field
    
    # Check if already enriched
    if 'name' in author_field and 'country' in author_field:
        return author_field  # Already enriched
    
    # Enrich from registry
    try:
        full_author = get_author(author_field['id'])
        
        # Return essential fields only (no internal prompt files)
        return {
            'id': full_author['id'],
            'name': full_author['name'],
            'country': full_author['country'],
            'country_display': full_author['country_display'],
            'title': full_author['title'],
            'sex': full_author['sex'],
            'expertise': full_author['expertise'],
        }
        
    except KeyError as e:
        print(f"❌ Author ID {author_field['id']} not found in registry: {e}")
        return author_field  # Return original on error


def enrich_domain_authors(
    domain: str,
    dry_run: bool = True
) -> Dict[str, int]:
    """
    Enrich all items in a domain with full author metadata.
    
    Args:
        domain: Domain name (materials, compounds, contaminants, settings)
        dry_run: If True, show changes without writing
        
    Returns:
        Dict with counts: {'total': N, 'enriched': M, 'skipped': K}
    """
    # Determine data file path
    domain_title = domain.title()
    data_path = Path(f'data/{domain}/{domain_title}.yaml')
    
    if not data_path.exists():
        print(f"❌ Data file not found: {data_path}")
        return {'total': 0, 'enriched': 0, 'skipped': 0}
    
    print(f"\n{'='*80}")
    print(f"🔍 Processing domain: {domain}")
    print(f"📄 Data file: {data_path}")
    print(f"{'='*80}\n")
    
    # Load data
    data = load_yaml(data_path)
    
    # Determine correct key for domain (contaminants uses 'contamination_patterns')
    if domain == 'contaminants':
        data_key = 'contamination_patterns'
    else:
        data_key = domain
    
    items = data.get(data_key, {})
    
    if not items:
        print(f"⚠️  No items found in {data_key} section")
        return {'total': 0, 'enriched': 0, 'skipped': 0}
    
    total = len(items)
    enriched_count = 0
    skipped_count = 0
    
    # Process each item
    for item_name, item_data in items.items():
        author = item_data.get('author', {})
        
        # Check if needs enrichment
        if not isinstance(author, dict):
            print(f"⚠️  {item_name}: author not a dict, skipping")
            skipped_count += 1
            continue
        
        if 'id' not in author:
            print(f"⚠️  {item_name}: author missing id, skipping")
            skipped_count += 1
            continue
        
        if 'name' in author and 'country' in author:
            # Already enriched
            skipped_count += 1
            continue
        
        # Enrich author
        enriched_author = enrich_author_field(author)
        
        if enriched_author != author:  # Changed
            item_data['author'] = enriched_author
            enriched_count += 1
            print(f"✅ {item_name}: {enriched_author['name']} ({enriched_author['country']})")
        else:
            skipped_count += 1
    
    # Summary
    print(f"\n{'='*80}")
    print(f"📊 SUMMARY for {domain}:")
    print(f"   Total items: {total}")
    print(f"   Enriched: {enriched_count}")
    print(f"   Skipped: {skipped_count}")
    print(f"{'='*80}\n")
    
    # Save if not dry run
    if not dry_run and enriched_count > 0:
        # Create backup
        backup_path = data_path.with_suffix('.yaml.backup')
        import shutil
        shutil.copy2(data_path, backup_path)
        print(f"💾 Backup created: {backup_path}")
        
        # Save enriched data
        save_yaml(data_path, data)
        print(f"✅ Saved enriched data to: {data_path}\n")
    elif dry_run and enriched_count > 0:
        print(f"🔍 DRY RUN: Would enrich {enriched_count} items in {data_path}\n")
    
    return {
        'total': total,
        'enriched': enriched_count,
        'skipped': skipped_count
    }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Enrich author metadata in domain data files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (safe - shows what would change)
  python3 scripts/data/enrich_author_metadata.py
  
  # Execute changes for all domains
  python3 scripts/data/enrich_author_metadata.py --execute
  
  # Execute for specific domain only
  python3 scripts/data/enrich_author_metadata.py --domain materials --execute
        """
    )
    
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Actually write changes (default: dry run)'
    )
    
    parser.add_argument(
        '--domain',
        type=str,
        choices=['materials', 'compounds', 'contaminants', 'settings'],
        help='Process specific domain only (default: all domains)'
    )
    
    args = parser.parse_args()
    
    # Determine domains to process
    if args.domain:
        domains = [args.domain]
    else:
        domains = ['materials', 'compounds', 'contaminants', 'settings']
    
    # Show mode
    mode = "EXECUTE" if args.execute else "DRY RUN"
    print(f"\n{'='*80}")
    print(f"🚀 Author Metadata Enrichment - {mode}")
    print(f"{'='*80}")
    print(f"Mode: {'✅ EXECUTE (will write changes)' if args.execute else '🔍 DRY RUN (no changes written)'}")
    print(f"Domains: {', '.join(domains)}")
    print(f"{'='*80}\n")
    
    # Process each domain
    all_results = {}
    for domain in domains:
        results = enrich_domain_authors(domain, dry_run=not args.execute)
        all_results[domain] = results
    
    # Final summary
    print(f"\n{'='*80}")
    print(f"🎯 FINAL SUMMARY - {mode}")
    print(f"{'='*80}")
    
    total_items = sum(r['total'] for r in all_results.values())
    total_enriched = sum(r['enriched'] for r in all_results.values())
    total_skipped = sum(r['skipped'] for r in all_results.values())
    
    for domain, results in all_results.items():
        if results['total'] > 0:
            print(f"  {domain.title():12} - {results['enriched']:3} enriched, {results['skipped']:3} skipped, {results['total']:3} total")
    
    print(f"{'='*80}")
    print(f"  {'TOTAL':12} - {total_enriched:3} enriched, {total_skipped:3} skipped, {total_items:3} total")
    print(f"{'='*80}\n")
    
    if not args.execute and total_enriched > 0:
        print("🔍 This was a DRY RUN. No files were modified.")
        print("   Run with --execute to apply changes.\n")
    elif total_enriched > 0:
        print("✅ Author metadata enrichment complete!")
        print("   Backup files created with .backup extension.\n")
    else:
        print("✅ All items already have complete author metadata.\n")


if __name__ == '__main__':
    main()
