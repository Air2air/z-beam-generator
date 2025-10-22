#!/usr/bin/env python3
"""
Migration Script: Strip Descriptions from Applications Field
============================================================

Purpose:
    Simplify applications format from "Industry: Description" to just "Industry"
    
Before:
    applications:
    - 'Aerospace: Precision cleaning of aerospace components'
    - 'Automotive: Paint removal and surface preparation'

After:
    applications:
    - 'Aerospace'
    - 'Automotive'

Usage:
    # Dry run (preview changes):
    python3 scripts/tools/fix_applications_descriptions.py --dry-run
    
    # Execute changes:
    python3 scripts/tools/fix_applications_descriptions.py --execute

Author: AI Assistant
Date: 2025-01-XX
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import yaml


class ApplicationsMigrator:
    """Migrate applications from 'Industry: Description' to 'Industry'."""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.stats = {
            'files_checked': 0,
            'files_with_applications': 0,
            'files_needing_changes': 0,
            'applications_simplified': 0,
            'files_updated': 0,
            'errors': []
        }
    
    def simplify_application(self, app_string: str) -> Tuple[str, bool]:
        """
        Simplify application string by extracting industry name before colon.
        
        Args:
            app_string: Original application string (e.g., 'Aerospace: Description...')
            
        Returns:
            Tuple of (simplified_string, was_changed)
        """
        app_string = app_string.strip()
        
        # Check if it has the old format with colon
        if ':' not in app_string:
            return app_string, False
        
        # Extract industry name (everything before first colon)
        industry = app_string.split(':', 1)[0].strip()
        
        # Remove any quotes from industry name
        industry = industry.strip("'\"")
        
        return industry, True
    
    def process_file(self, file_path: Path) -> Dict:
        """
        Process a single frontmatter YAML file.
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            Dictionary with processing results
        """
        result = {
            'file': str(file_path),
            'had_applications': False,
            'needed_changes': False,
            'changes_made': 0,
            'error': None
        }
        
        try:
            # Read YAML file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            if not content or 'applications' not in content:
                return result
            
            result['had_applications'] = True
            applications = content.get('applications', [])
            
            if not isinstance(applications, list):
                result['error'] = f"Applications is not a list: {type(applications)}"
                return result
            
            # Process each application
            new_applications = []
            changes_made = 0
            
            for app in applications:
                # Handle dict format (old schema): {'industry': 'Aerospace', 'description': '...'}
                if isinstance(app, dict):
                    if 'industry' in app:
                        industry = app['industry'].strip().strip("'\"")
                        new_applications.append(industry)
                        changes_made += 1
                        if not self.dry_run:
                            print(f"    Dict -> '{industry}'")
                    else:
                        # Keep dict without 'industry' key as-is (shouldn't happen)
                        new_applications.append(app)
                    continue
                
                # Handle string format: "Industry: Description" or just "Industry"
                if not isinstance(app, str):
                    # Keep other types as-is (shouldn't happen)
                    new_applications.append(app)
                    continue
                
                simplified, was_changed = self.simplify_application(app)
                new_applications.append(simplified)
                
                if was_changed:
                    changes_made += 1
                    if not self.dry_run:
                        print(f"    '{app}' -> '{simplified}'")
            
            if changes_made > 0:
                result['needed_changes'] = True
                result['changes_made'] = changes_made
                
                # Update content
                content['applications'] = new_applications
                
                # Write back to file (unless dry-run)
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        yaml.dump(
                            content,
                            f,
                            default_flow_style=False,
                            allow_unicode=True,
                            sort_keys=False,
                            width=120
                        )
        
        except Exception as e:
            result['error'] = str(e)
            self.stats['errors'].append(f"{file_path}: {e}")
        
        return result
    
    def migrate_all(self, directory: Path) -> None:
        """
        Migrate all frontmatter files in directory.
        
        Args:
            directory: Path to directory containing frontmatter YAML files
        """
        print(f"{'=' * 80}")
        print(f"Applications Description Migration")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'EXECUTE'}")
        print(f"Directory: {directory}")
        print(f"{'=' * 80}\n")
        
        # Find all YAML files
        yaml_files = sorted(directory.glob("*.yaml"))
        
        if not yaml_files:
            print(f"❌ No YAML files found in {directory}")
            return
        
        print(f"Found {len(yaml_files)} YAML files\n")
        
        # Process each file
        for yaml_file in yaml_files:
            self.stats['files_checked'] += 1
            
            result = self.process_file(yaml_file)
            
            if result['had_applications']:
                self.stats['files_with_applications'] += 1
            
            if result['error']:
                print(f"❌ Error processing {yaml_file.name}: {result['error']}")
                continue
            
            if result['needed_changes']:
                self.stats['files_needing_changes'] += 1
                self.stats['applications_simplified'] += result['changes_made']
                
                if self.dry_run:
                    print(f"Would update {yaml_file.name}: {result['changes_made']} applications")
                else:
                    self.stats['files_updated'] += 1
                    print(f"✅ Updated {yaml_file.name}: {result['changes_made']} applications simplified")
        
        # Print summary
        self.print_summary()
    
    def print_summary(self) -> None:
        """Print migration summary statistics."""
        print(f"\n{'=' * 80}")
        print("MIGRATION SUMMARY")
        print(f"{'=' * 80}")
        print(f"Files checked:              {self.stats['files_checked']}")
        print(f"Files with applications:    {self.stats['files_with_applications']}")
        print(f"Files needing changes:      {self.stats['files_needing_changes']}")
        print(f"Applications simplified:    {self.stats['applications_simplified']}")
        
        if not self.dry_run:
            print(f"Files updated:              {self.stats['files_updated']}")
        
        if self.stats['errors']:
            print(f"\n❌ Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:5]:
                print(f"   {error}")
            if len(self.stats['errors']) > 5:
                print(f"   ... and {len(self.stats['errors']) - 5} more")
        
        print(f"{'=' * 80}")
        
        if self.dry_run and self.stats['files_needing_changes'] > 0:
            print("\n💡 This was a dry run. Use --execute to apply changes.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate applications from 'Industry: Description' to 'Industry'",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Preview changes (dry run):
    python3 scripts/tools/fix_applications_descriptions.py --dry-run
    
    # Apply changes:
    python3 scripts/tools/fix_applications_descriptions.py --execute
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files (default)'
    )
    
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Actually modify files'
    )
    
    parser.add_argument(
        '--directory',
        type=Path,
        default=Path('content/frontmatter'),
        help='Directory containing frontmatter YAML files (default: content/frontmatter)'
    )
    
    args = parser.parse_args()
    
    # Default to dry-run if neither specified
    if not args.dry_run and not args.execute:
        args.dry_run = True
    
    # Validate directory
    if not args.directory.exists():
        print(f"❌ Directory not found: {args.directory}")
        sys.exit(1)
    
    # Run migration
    migrator = ApplicationsMigrator(dry_run=args.dry_run)
    migrator.migrate_all(args.directory)
    
    # Exit with appropriate code
    if migrator.stats['errors']:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
