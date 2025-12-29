#!/usr/bin/env python3
"""
Migrate 'title' to 'page_title' in Frontmatter Files
====================================================

This script migrates the deprecated root-level 'title' field to 'page_title',
overwriting any existing content in 'page_title' with the 'title' value.

Background:
- Old structure: 'title' (root level) + 'page_title' (SEO field)
- New structure: 'page_title' only (root level becomes SEO field)
- Reason: Consolidation - one field for page title display

Usage:
    python3 scripts/tools/migrate_title_to_page_title.py --dry-run  # Preview
    python3 scripts/tools/migrate_title_to_page_title.py            # Apply
"""

import argparse
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

# Frontmatter directories relative to z-beam repo
FRONTMATTER_DIRS = [
    Path("../z-beam/frontmatter/materials"),
    Path("../z-beam/frontmatter/contaminants"),
    Path("../z-beam/frontmatter/compounds"),
    Path("../z-beam/frontmatter/settings"),
]


class TitleMigrator:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.files_checked = 0
        self.files_migrated = 0
        self.migrations = []
    
    def migrate_file(self, file_path: Path) -> Tuple[bool, str]:
        """
        Migrate title to page_title in a single file.
        
        Returns:
            (migrated, reason) tuple
        """
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        if not isinstance(data, dict):
            return False, "Not a dict"
        
        # Check if migration needed
        if 'title' not in data:
            return False, "No 'title' field"
        
        title_value = data['title']
        had_page_title = 'page_title' in data
        old_page_title = data.get('page_title', None)
        
        # Perform migration
        if not self.dry_run:
            # Move title to page_title (overwrite if exists)
            data['page_title'] = title_value
            # Remove old title field
            del data['title']
            
            # Write back
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        # Build reason message
        if had_page_title and old_page_title != title_value:
            reason = f"Overwrote page_title: '{old_page_title}' → '{title_value}'"
        elif had_page_title:
            reason = f"Renamed (page_title was same): '{title_value}'"
        else:
            reason = f"Created page_title: '{title_value}'"
        
        self.migrations.append({
            'file': file_path.name,
            'title_value': title_value,
            'had_page_title': had_page_title,
            'old_page_title': old_page_title,
            'reason': reason
        })
        
        return True, reason
    
    def migrate_directory(self, dir_path: Path):
        """Migrate all YAML files in directory."""
        if not dir_path.exists():
            print(f"⚠️  Directory not found: {dir_path}")
            return
        
        yaml_files = list(dir_path.rglob("*.yaml"))
        print(f"\n📁 {dir_path.name}: {len(yaml_files)} files")
        
        migrated_count = 0
        for file_path in yaml_files:
            self.files_checked += 1
            migrated, reason = self.migrate_file(file_path)
            if migrated:
                migrated_count += 1
                self.files_migrated += 1
        
        print(f"   ✅ Migrated: {migrated_count}/{len(yaml_files)}")
    
    def run(self):
        """Execute migration across all domains."""
        print("="*80)
        print("🔄 MIGRATING 'title' → 'page_title'")
        print("="*80)
        
        if self.dry_run:
            print("🔄 DRY-RUN MODE (no files will be modified)\n")
        else:
            print("⚠️  LIVE MODE (files will be modified!)\n")
        
        # Migrate each domain directory
        for dir_path in FRONTMATTER_DIRS:
            self.migrate_directory(dir_path)
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate summary report."""
        print("\n" + "="*80)
        print("📊 MIGRATION SUMMARY")
        print("="*80)
        
        print(f"\n✅ Files checked: {self.files_checked}")
        print(f"🔄 Files migrated: {self.files_migrated}")
        print(f"⏭️  Files skipped: {self.files_checked - self.files_migrated}")
        
        if self.migrations:
            # Group by type
            overwrites = [m for m in self.migrations if m['had_page_title'] and m['old_page_title'] != m['title_value']]
            renames = [m for m in self.migrations if m['had_page_title'] and m['old_page_title'] == m['title_value']]
            creates = [m for m in self.migrations if not m['had_page_title']]
            
            print(f"\n📝 Migration breakdown:")
            print(f"   • Overwrote page_title: {len(overwrites)}")
            print(f"   • Renamed (same value): {len(renames)}")
            print(f"   • Created page_title: {len(creates)}")
            
            if overwrites and len(overwrites) <= 10:
                print(f"\n⚠️  Files where page_title was overwritten:")
                for m in overwrites[:10]:
                    print(f"   • {m['file']}")
                    print(f"     Old: '{m['old_page_title']}'")
                    print(f"     New: '{m['title_value']}'")
            elif len(overwrites) > 10:
                print(f"\n⚠️  {len(overwrites)} files had page_title overwritten (showing first 5):")
                for m in overwrites[:5]:
                    print(f"   • {m['file']}: '{m['old_page_title']}' → '{m['title_value']}'")
                print(f"   ... and {len(overwrites) - 5} more")
        
        if not self.dry_run and self.files_migrated > 0:
            print(f"\n✅ Migration complete! {self.files_migrated} files updated.")
            print("\n📋 Next steps:")
            print("   1. Review changes: cd ../z-beam && git diff frontmatter/")
            print("   2. Test the website to ensure titles display correctly")
            print("   3. Commit if everything looks good")
        elif self.dry_run:
            print("\n🔄 Run without --dry-run to apply these changes")


def main():
    parser = argparse.ArgumentParser(
        description="Migrate 'title' to 'page_title' in frontmatter files"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Preview changes without modifying files"
    )
    
    args = parser.parse_args()
    
    migrator = TitleMigrator(dry_run=args.dry_run)
    migrator.run()


if __name__ == '__main__':
    main()
