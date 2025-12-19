#!/usr/bin/env python3
"""
Frontmatter Migration Script - Phase 1: Structure Fixes

Implements Phase 1 from FRONTMATTER_FORMATTING_SPECIFICATION.md:
1. Remove 'slug' from relationship entries
2. Fix URLs to use full IDs (not just slugs)
3. Remove 'category'/'subcategory' from relationships
4. Ensure all relationship entries have required fields: id, title, url

Usage:
    # Dry run (show changes without applying)
    python3 scripts/migrate_frontmatter_phase1.py --dry-run
    
    # Migrate specific content type
    python3 scripts/migrate_frontmatter_phase1.py --type settings
    
    # Migrate all files
    python3 scripts/migrate_frontmatter_phase1.py --all
    
    # Migrate specific file
    python3 scripts/migrate_frontmatter_phase1.py --file ../z-beam/frontmatter/settings/Aluminum-settings.yaml
"""

import yaml
import argparse
from pathlib import Path
from typing import Dict, Any, List
import re
from datetime import datetime


class FrontmatterMigrator:
    """Migrates frontmatter files to Phase 1 spec compliance."""
    
    # URL base paths by content type
    URL_BASES = {
        'materials': '/materials',
        'contaminants': '/contaminants',
        'compounds': '/compounds',
        'settings': '/settings'
    }
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.changes_made = 0
        self.files_modified = 0
        
    def migrate_file(self, filepath: Path) -> bool:
        """
        Migrate a single frontmatter file.
        
        Returns:
            True if file was modified, False otherwise
        """
        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Processing: {filepath.name}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                print(f"  ⚠️  Empty file, skipping")
                return False
            
            original_data = yaml.dump(data, sort_keys=False)
            file_changes = 0
            
            # Process relationships section
            if 'relationships' in data:
                file_changes += self._process_relationships(data['relationships'])
            
            # Check if anything changed
            new_data = yaml.dump(data, sort_keys=False)
            if original_data == new_data:
                print(f"  ✅ No changes needed")
                return False
            
            print(f"  🔧 {file_changes} fixes applied")
            self.changes_made += file_changes
            
            # Write back if not dry run
            if not self.dry_run:
                # Update dateModified
                data['dateModified'] = datetime.utcnow().isoformat() + 'Z'
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                print(f"  💾 File updated")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def _process_relationships(self, relationships: Dict[str, Any]) -> int:
        """
        Process all relationship arrays in the relationships section.
        
        Returns:
            Number of changes made
        """
        changes = 0
        
        for key, value in relationships.items():
            if isinstance(value, list):
                for entry in value:
                    if isinstance(entry, dict):
                        changes += self._fix_relationship_entry(entry, key)
        
        return changes
    
    def _fix_relationship_entry(self, entry: Dict[str, Any], parent_key: str) -> int:
        """
        Fix a single relationship entry according to Phase 1 spec.
        
        Fixes:
        1. Remove 'slug' field
        2. Remove 'category'/'subcategory' fields
        3. Ensure 'url' field exists and uses full ID
        4. Ensure required fields: id, title, url
        
        Returns:
            Number of changes made to this entry
        """
        changes = 0
        
        # Fix 1: Remove 'slug' field
        if 'slug' in entry:
            print(f"    - Removing 'slug': {entry['slug']}")
            del entry['slug']
            changes += 1
        
        # Fix 2: Remove 'category' and 'subcategory' fields
        for field in ['category', 'subcategory']:
            if field in entry:
                print(f"    - Removing '{field}': {entry[field]}")
                del entry[field]
                changes += 1
        
        # Fix 3 & 4: Ensure URL exists and uses full ID
        if 'id' in entry:
            entry_id = entry['id']
            
            # Determine content type from entry ID or parent key
            content_type = self._detect_content_type(entry_id, parent_key)
            
            if content_type:
                expected_url = f"{self.URL_BASES[content_type]}/{entry_id}"
                
                if 'url' not in entry:
                    print(f"    - Adding 'url': {expected_url}")
                    entry['url'] = expected_url
                    changes += 1
                elif entry['url'] != expected_url:
                    # Fix partial URLs or incorrect URLs
                    if not entry['url'].startswith('/'):
                        print(f"    - Fixing 'url': {entry['url']} → {expected_url}")
                        entry['url'] = expected_url
                        changes += 1
        
        # Ensure 'title' exists
        if 'id' in entry and 'title' not in entry:
            # Generate title from ID if missing
            title = self._generate_title_from_id(entry['id'])
            print(f"    - Adding 'title': {title}")
            entry['title'] = title
            changes += 1
        
        return changes
    
    def _detect_content_type(self, entry_id: str, parent_key: str) -> str:
        """
        Detect content type from entry ID or parent key.
        
        Args:
            entry_id: The ID of the entry
            parent_key: The parent key (e.g., 'related_materials')
        
        Returns:
            Content type string or None
        """
        # Try to detect from parent key
        if 'material' in parent_key:
            return 'materials'
        elif 'contaminant' in parent_key:
            return 'contaminants'
        elif 'compound' in parent_key:
            return 'compounds'
        elif 'setting' in parent_key:
            return 'settings'
        
        # Try to detect from entry ID patterns
        if entry_id.endswith('-laser-cleaning'):
            return 'materials'
        elif entry_id.endswith('-contamination'):
            return 'contaminants'
        elif entry_id.endswith('-settings'):
            return 'settings'
        
        # Check for common compound indicators (chemical names, CAS patterns)
        if re.match(r'^[a-z]+(-[a-z]+)*$', entry_id) and not entry_id.endswith('-contamination'):
            # Could be compound or regulatory standard
            # If it has 'standard' or regulatory terms, likely not compound
            if any(term in entry_id for term in ['standard', 'osha', 'ansi', 'iso', 'iec', 'fda']):
                return None  # Regulatory standard, not a domain content type
            return 'compounds'
        
        return None
    
    def _generate_title_from_id(self, entry_id: str) -> str:
        """Generate a human-readable title from an ID."""
        # Remove common suffixes
        title = entry_id.replace('-laser-cleaning', '')
        title = title.replace('-contamination', '')
        title = title.replace('-settings', '')
        
        # Convert to title case
        title = title.replace('-', ' ').title()
        
        return title


def main():
    parser = argparse.ArgumentParser(
        description='Migrate frontmatter files to Phase 1 spec compliance'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    parser.add_argument(
        '--type',
        choices=['materials', 'contaminants', 'compounds', 'settings'],
        help='Migrate only files of this content type'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Migrate all frontmatter files'
    )
    parser.add_argument(
        '--file',
        type=Path,
        help='Migrate a specific file'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not (args.all or args.type or args.file):
        parser.error('Must specify --all, --type, or --file')
    
    # Determine base path
    script_dir = Path(__file__).parent.parent
    frontmatter_base = script_dir.parent / 'z-beam' / 'frontmatter'
    
    if not frontmatter_base.exists():
        print(f"❌ Frontmatter directory not found: {frontmatter_base}")
        return 1
    
    # Create migrator
    migrator = FrontmatterMigrator(dry_run=args.dry_run)
    
    # Collect files to process
    files_to_process = []
    
    if args.file:
        if args.file.exists():
            files_to_process.append(args.file)
        else:
            print(f"❌ File not found: {args.file}")
            return 1
    
    elif args.type:
        type_dir = frontmatter_base / args.type
        if type_dir.exists():
            files_to_process.extend(type_dir.glob('*.yaml'))
        else:
            print(f"❌ Directory not found: {type_dir}")
            return 1
    
    elif args.all:
        for content_type in ['materials', 'contaminants', 'compounds', 'settings']:
            type_dir = frontmatter_base / content_type
            if type_dir.exists():
                files_to_process.extend(type_dir.glob('*.yaml'))
    
    if not files_to_process:
        print("❌ No files found to process")
        return 1
    
    # Process files
    print(f"\n{'='*70}")
    print(f"FRONTMATTER MIGRATION - PHASE 1: Structure Fixes")
    print(f"{'='*70}")
    print(f"Mode: {'DRY RUN (no changes will be made)' if args.dry_run else 'LIVE (files will be modified)'}")
    print(f"Files to process: {len(files_to_process)}")
    print(f"{'='*70}\n")
    
    for filepath in sorted(files_to_process):
        if migrator.migrate_file(filepath):
            migrator.files_modified += 1
    
    # Summary
    print(f"\n{'='*70}")
    print(f"MIGRATION COMPLETE")
    print(f"{'='*70}")
    print(f"Files processed: {len(files_to_process)}")
    print(f"Files modified: {migrator.files_modified}")
    print(f"Total changes: {migrator.changes_made}")
    
    if args.dry_run:
        print(f"\n⚠️  DRY RUN MODE - No files were actually modified")
        print(f"Run without --dry-run to apply changes")
    else:
        print(f"\n✅ Migration complete!")
    
    print(f"{'='*70}\n")
    
    return 0


if __name__ == '__main__':
    exit(main())
