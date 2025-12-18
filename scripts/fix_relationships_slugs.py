#!/usr/bin/env python3
"""
Add missing 'slug' field to all domain linkage entries.

This script fixes Schema 5.0.0 compliance by extracting slugs from URLs
and adding them to all relationships entries across all domains.

Affects: 2,060 entries in 271 files (Materials, Contaminants, Compounds)
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any


def extract_slug_from_url(url: str) -> str:
    """Extract slug from URL path.
    
    Examples:
        /materials/aluminum-laser-cleaning → aluminum-laser-cleaning
        /contaminants/rust-contamination → rust-contamination
        /compounds/carbon-monoxide → carbon-monoxide
    """
    return url.rstrip('/').split('/')[-1]


def add_slug_to_linkages(data: Dict[str, Any]) -> tuple[int, int]:
    """Add slug field to all domain linkage entries.
    
    Returns:
        tuple: (entries_processed, entries_updated)
    """
    if not data or 'relationships' not in data:
        return 0, 0
    
    entries_processed = 0
    entries_updated = 0
    
    linkages = data['relationships']
    
    for linkage_type, entries in linkages.items():
        if not entries:
            continue
        
        for entry in entries:
            entries_processed += 1
            
            # Skip if slug already exists
            if 'slug' in entry:
                continue
            
            # Extract slug from URL
            if 'url' not in entry:
                print(f"  ⚠️  Entry missing URL: {entry.get('id', 'unknown')}")
                continue
            
            slug = extract_slug_from_url(entry['url'])
            entry['slug'] = slug
            entries_updated += 1
    
    return entries_processed, entries_updated


def process_domain(domain_name: str, domain_path: str) -> Dict[str, int]:
    """Process all files in a domain directory.
    
    Returns:
        dict: Statistics about processing
    """
    domain_dir = Path(domain_path)
    
    if not domain_dir.exists():
        print(f"❌ Directory not found: {domain_dir}")
        return {'files': 0, 'processed': 0, 'updated': 0, 'entries': 0}
    
    files = list(domain_dir.glob("*.yaml"))
    files_updated = 0
    total_entries = 0
    total_updated = 0
    
    print(f"\n{'='*80}")
    print(f"Processing {domain_name.upper()}")
    print(f"{'='*80}")
    print(f"Files to check: {len(files)}")
    
    for file_path in files:
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                continue
            
            # Add slugs
            entries_processed, entries_updated = add_slug_to_linkages(data)
            
            if entries_updated > 0:
                # Write back with SafeDumper
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(
                        data,
                        f,
                        Dumper=yaml.SafeDumper,
                        default_flow_style=False,
                        allow_unicode=True,
                        sort_keys=False
                    )
                
                files_updated += 1
                total_entries += entries_processed
                total_updated += entries_updated
                
                if entries_updated > 0:
                    print(f"  ✅ {file_path.name}: {entries_updated} slugs added")
        
        except Exception as e:
            print(f"  ❌ Error processing {file_path.name}: {e}")
    
    print(f"\nSummary:")
    print(f"  Files updated: {files_updated}/{len(files)}")
    print(f"  Entries processed: {total_entries}")
    print(f"  Slugs added: {total_updated}")
    
    return {
        'files': len(files),
        'processed': files_updated,
        'updated': total_updated,
        'entries': total_entries
    }


def main():
    """Main execution function."""
    print("\n" + "="*80)
    print("DOMAIN LINKAGES SLUG ADDITION SCRIPT")
    print("="*80)
    print("Adding missing 'slug' fields to all relationships entries")
    print("Schema 5.0.0 compliance fix\n")
    
    domains = [
        ("materials", "frontmatter/materials"),
        ("contaminants", "frontmatter/contaminants"),
        ("compounds", "frontmatter/compounds"),
        ("settings", "frontmatter/settings"),
    ]
    
    total_stats = {
        'files': 0,
        'processed': 0,
        'updated': 0,
        'entries': 0
    }
    
    for domain_name, domain_path in domains:
        stats = process_domain(domain_name, domain_path)
        total_stats['files'] += stats['files']
        total_stats['processed'] += stats['processed']
        total_stats['updated'] += stats['updated']
        total_stats['entries'] += stats['entries']
    
    print(f"\n{'='*80}")
    print("OVERALL SUMMARY")
    print(f"{'='*80}")
    print(f"Total files checked: {total_stats['files']}")
    print(f"Files updated: {total_stats['processed']}")
    print(f"Entries processed: {total_stats['entries']}")
    print(f"Slugs added: {total_stats['updated']}")
    print(f"\n✅ Complete! Run tests to verify:")
    print(f"   pytest tests/test_*_filename_compliance.py::*::test_relationships_have_required_fields -v")
    print()


if __name__ == "__main__":
    main()
