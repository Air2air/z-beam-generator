#!/usr/bin/env python3
"""
Backfill Software Metadata to Source Data Files

PURPOSE: Add complete software metadata fields to ALL source YAML files
COMPLIANCE: Core Principle 0.6 - Generate complete data to source, not during export
DATE: January 6, 2026

FIELDS ADDED:
- contentType: 'material' | 'contaminant' | 'compound' | 'setting'
- schemaVersion: '5.0.0'
- pageTitle: Page title for frontend (from title or name)
- fullPath: '/materials/metal/aluminum-laser-cleaning'
- breadcrumb: [{label, href}, ...]
- pageDescription: Generated from micro/description
- datePublished: Preserved or current timestamp
- dateModified: Current timestamp

USAGE:
    # Dry run (show what would change)
    python3 scripts/enrichment/backfill_software_metadata.py --dry-run
    
    # Backfill all domains
    python3 scripts/enrichment/backfill_software_metadata.py --all
    
    # Backfill specific domain
    python3 scripts/enrichment/backfill_software_metadata.py --domain materials

RELATED:
- MAXIMUM_FORMATTING_AT_SOURCE_JAN6_2026.md - Implementation plan
- Core Principle 0.6 - No data creation at export time
"""

import argparse
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import sys


class SoftwareMetadataBackfiller:
    """Add complete software metadata to source YAML files."""
    
    DOMAIN_FILES = {
        'materials': 'data/materials/Materials.yaml',
        'contaminants': 'data/contaminants/Contaminants.yaml',
        'compounds': 'data/compounds/Compounds.yaml',
        'settings': 'data/settings/Settings.yaml',
    }
    
    CONTENT_TYPE_MAP = {
        'materials': 'material',
        'contaminants': 'contaminant',
        'compounds': 'compound',
        'settings': 'setting',
    }
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.stats = {
            'total_items': 0,
            'items_modified': 0,
            'fields_added': 0,
        }
    
    def generate_breadcrumbs(self, item_data: Dict[str, Any], domain: str) -> List[Dict[str, str]]:
        """
        Generate breadcrumb navigation from category hierarchy.
        
        CRITICAL: URLs must use slugified categories/subcategories (hyphens not underscores).
        Display labels can use proper titles.
        """
        # Import here to avoid path issues
        import sys
        from pathlib import Path
        
        # Add project root to path if not already present
        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        from export.utils.url_formatter import slugify
        
        breadcrumbs = [{'label': 'Home', 'href': '/'}]
        
        # Add domain breadcrumb
        domain_labels = {
            'materials': 'Materials',
            'contaminants': 'Contaminants',
            'compounds': 'Compounds',
            'settings': 'Settings',
        }
        breadcrumbs.append({
            'label': domain_labels.get(domain, domain.title()),
            'href': f'/{domain}'
        })
        
        # Add category breadcrumb
        if item_data.get('category'):
            category = item_data['category']
            # Slugify URL: toxic_gas → toxic-gas
            category_slug = slugify(category)
            breadcrumbs.append({
                'label': category.replace('_', ' ').replace('-', ' ').title(),
                'href': f'/{domain}/{category_slug}'
            })
            
            # Add subcategory breadcrumb
            if item_data.get('subcategory'):
                subcategory = item_data['subcategory']
                # Slugify URL: acid_gas → acid-gas
                subcategory_slug = slugify(subcategory)
                breadcrumbs.append({
                    'label': subcategory.replace('_', ' ').replace('-', ' ').title(),
                    'href': f'/{domain}/{category_slug}/{subcategory_slug}'
                })
        
        return breadcrumbs
    
    def generate_full_path(self, item_data: Dict[str, Any], domain: str) -> str:
        """
        Generate fullPath from category hierarchy and ID.
        
        CRITICAL: Categories/subcategories with underscores (toxic_gas, corrosive_gas)
        must be slugified to hyphens (toxic-gas, corrosive-gas) for Next.js URL compatibility.
        """
        # Import here to avoid path issues
        import sys
        from pathlib import Path
        
        # Add project root to path if not already present
        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        from export.utils.url_formatter import slugify
        
        path_parts = [domain]
        
        if item_data.get('category'):
            # Slugify category: toxic_gas → toxic-gas, metal_fume → metal-fume
            path_parts.append(slugify(item_data['category']))
        if item_data.get('subcategory'):
            # Slugify subcategory: acid_gas → acid-gas, alkaline_gas → alkaline-gas
            path_parts.append(slugify(item_data['subcategory']))
        path_parts.append(item_data['id'])
        
        return '/' + '/'.join(path_parts)
    
    def generate_page_description(self, item_data: Dict[str, Any]) -> str:
        """Generate pageDescription from micro or description."""
        # Try micro.before first
        if isinstance(item_data.get('micro'), dict):
            micro_text = item_data['micro'].get('before', '')
            if micro_text:
                return micro_text[:157] + '...' if len(micro_text) > 160 else micro_text
        
        # Try description
        if item_data.get('description'):
            desc = item_data['description']
            return desc[:157] + '...' if len(desc) > 160 else desc
        
        # Fallback: generic description
        name = item_data.get('name', item_data.get('id', 'item'))
        return f"{name} laser cleaning guide. Technical specifications and applications."
    
    def enrich_item(self, item_data: Dict[str, Any], domain: str) -> tuple[Dict[str, Any], int]:
        """Add software metadata fields to item data."""
        fields_added = 0
        
        # 1. contentType
        if 'contentType' not in item_data:
            item_data['contentType'] = self.CONTENT_TYPE_MAP[domain]
            fields_added += 1
            print(f"  + contentType: {item_data['contentType']}")
        
        # 2. schemaVersion
        if 'schemaVersion' not in item_data:
            item_data['schemaVersion'] = '5.0.0'
            fields_added += 1
            print(f"  + schemaVersion: 5.0.0")
        
        # 3. fullPath (ALWAYS regenerate for URL safety - fixes toxic_gas → toxic-gas)
        old_path = item_data.get('fullPath')
        item_data['fullPath'] = self.generate_full_path(item_data, domain)
        if old_path != item_data['fullPath']:
            fields_added += 1
            print(f"  ✏️  fullPath: {old_path} → {item_data['fullPath']}")
        
        # 4. pageTitle (for frontend compatibility)
        if 'pageTitle' not in item_data:
            # Use title if available, otherwise name
            page_title = item_data.get('title') or item_data.get('name') or item_data.get('id', '').replace('-', ' ').title()
            item_data['pageTitle'] = page_title
            fields_added += 1
            print(f"  + pageTitle: {page_title}")
        
        # 5. breadcrumb (ALWAYS regenerate for URL safety - fixes toxic_gas → toxic-gas)
        old_breadcrumb = item_data.get('breadcrumb')
        item_data['breadcrumb'] = self.generate_breadcrumbs(item_data, domain)
        if old_breadcrumb != item_data['breadcrumb']:
            fields_added += 1
            print(f"  ✏️  breadcrumb: {len(item_data['breadcrumb'])} levels (URLs updated)")
        
        # 6. pageDescription
        if 'pageDescription' not in item_data:
            item_data['pageDescription'] = self.generate_page_description(item_data)
            fields_added += 1
            print(f"  + pageDescription: {len(item_data['pageDescription'])} chars")
        
        # 6. datePublished (preserve existing or use current)
        if 'datePublished' not in item_data:
            # Check for legacy metadata.created_date
            metadata = item_data.get('metadata', {})
            if isinstance(metadata, dict) and metadata.get('created_date'):
                item_data['datePublished'] = metadata['created_date']
            else:
                item_data['datePublished'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
            fields_added += 1
            print(f"  + datePublished: {item_data['datePublished']}")
        
        # 7. dateModified (always update to current)
        item_data['dateModified'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
        if fields_added > 0:  # Only count as added if other fields were added
            fields_added += 1
            print(f"  + dateModified: {item_data['dateModified']}")
        
        return item_data, fields_added
    
    def backfill_domain(self, domain: str) -> None:
        """Backfill software metadata for one domain."""
        file_path = Path(self.DOMAIN_FILES[domain])
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return
        
        print(f"\n{'='*80}")
        print(f"🔄 Processing {domain.upper()}")
        print(f"{'='*80}")
        print(f"File: {file_path}")
        
        # Load data
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        items_key = domain  # materials, contaminants, compounds, settings
        if items_key not in data:
            print(f"❌ Key '{items_key}' not found in {file_path}")
            return
        
        items = data[items_key]
        total_items = len(items)
        self.stats['total_items'] += total_items
        
        print(f"Total items: {total_items}")
        print()
        
        # Process each item
        items_modified = 0
        for item_name, item_data in items.items():
            if not isinstance(item_data, dict):
                continue
            
            print(f"📝 {item_name}")
            
            enriched_data, fields_added = self.enrich_item(item_data, domain)
            
            if fields_added > 0:
                items_modified += 1
                self.stats['fields_added'] += fields_added
                items[item_name] = enriched_data
            else:
                print(f"  ✅ Already complete")
            print()
        
        self.stats['items_modified'] += items_modified
        
        # Save if not dry run
        if not self.dry_run:
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, 
                         sort_keys=False, width=120)
            print(f"✅ Saved {file_path}")
        else:
            print(f"🔍 DRY RUN - No changes saved")
        
        print(f"\nSummary: {items_modified}/{total_items} items modified, {self.stats['fields_added']} fields added")
    
    def run(self, domains: List[str]) -> None:
        """Run backfill for specified domains."""
        print("\n" + "="*80)
        print("SOFTWARE METADATA BACKFILL")
        print("="*80)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print(f"Domains: {', '.join(domains)}")
        print()
        
        for domain in domains:
            self.backfill_domain(domain)
        
        # Final summary
        print("\n" + "="*80)
        print("FINAL SUMMARY")
        print("="*80)
        print(f"Total items processed: {self.stats['total_items']}")
        print(f"Items modified: {self.stats['items_modified']}")
        print(f"Fields added: {self.stats['fields_added']}")
        print()
        
        if self.dry_run:
            print("🔍 This was a DRY RUN - no files were modified")
            print("Run with --no-dry-run to apply changes")
        else:
            print("✅ All changes saved to source YAML files")
            print("Next steps:")
            print("  1. Verify changes: git diff data/")
            print("  2. Test export: python3 run.py --export --domain materials --limit 2")
            print("  3. Commit: git add data/ && git commit -m 'Add software metadata to source data'")


def main():
    parser = argparse.ArgumentParser(
        description='Backfill software metadata to source YAML files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--domain', choices=['materials', 'contaminants', 'compounds', 'settings'],
                       help='Backfill specific domain only')
    parser.add_argument('--all', action='store_true',
                       help='Backfill all domains')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Show what would change without modifying files (default)')
    parser.add_argument('--no-dry-run', action='store_true',
                       help='Actually modify files (USE WITH CAUTION)')
    
    args = parser.parse_args()
    
    # Determine domains to process
    if args.all:
        domains = list(SoftwareMetadataBackfiller.DOMAIN_FILES.keys())
    elif args.domain:
        domains = [args.domain]
    else:
        parser.error("Must specify --domain or --all")
    
    # Determine dry run mode
    dry_run = not args.no_dry_run
    
    # Run backfill
    backfiller = SoftwareMetadataBackfiller(dry_run=dry_run)
    backfiller.run(domains)


if __name__ == '__main__':
    main()
