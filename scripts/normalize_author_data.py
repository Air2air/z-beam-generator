#!/usr/bin/env python3
"""
Author Data Normalization Script

PURPOSE: Normalize author data across all frontmatter files to match materials example

NORMALIZATION ACTIONS:
1. Expand author: {id: 1} to full author object with all fields
2. Populate empty author: {} objects
3. Ensure consistent author structure across all content types

AUTHOR PROFILES (from data/authors/):
- ID 1: Yi-Chun Lin (Taiwan, Ph.D., Laser Processing Engineer)
- ID 2: Todd Dunning (USA, Founder, Laser Safety Expert)
- ID 3: Alessandro Moretti (Italy, Senior Researcher)
- ID 4: Ikmanda Roswati (Indonesia, Technical Writer)

USAGE:
    python3 scripts/normalize_author_data.py --dry-run --all
    python3 scripts/normalize_author_data.py --type compounds
    python3 scripts/normalize_author_data.py --all
"""

import yaml
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

# Complete author profiles
AUTHOR_PROFILES = {
    1: {
        'id': 1,
        'name': 'Yi-Chun Lin',
        'country': 'Taiwan',
        'country_display': 'Taiwan',
        'title': 'Ph.D.',
        'sex': 'f',
        'jobTitle': 'Laser Processing Engineer',
        'expertise': ['Laser Materials Processing'],
        'affiliation': {
            'name': 'National Taiwan University',
            'type': 'EducationalOrganization'
        },
        'credentials': [
            'Ph.D. Materials Engineering, National Taiwan University, 2018',
            "Post-Ph.D. fellowship at TSMC's laser fab lab, 2018-2020"
        ]
    },
    2: {
        'id': 2,
        'name': 'Todd Dunning',
        'country': 'USA',
        'country_display': 'United States',
        'title': 'Founder',
        'sex': 'm',
        'jobTitle': 'Laser Safety Expert',
        'expertise': ['Laser Safety', 'Industrial Applications'],
        'affiliation': {
            'name': 'Z-Beam',
            'type': 'Organization'
        },
        'credentials': [
            'Founder of Z-Beam laser cleaning solutions',
            '15+ years in industrial laser applications'
        ]
    },
    3: {
        'id': 3,
        'name': 'Alessandro Moretti',
        'country': 'Italy',
        'country_display': 'Italy',
        'title': 'Dr.',
        'sex': 'm',
        'jobTitle': 'Senior Researcher',
        'expertise': ['Laser Physics', 'Material Science'],
        'affiliation': {
            'name': 'Italian Institute of Technology',
            'type': 'EducationalOrganization'
        },
        'credentials': [
            'Ph.D. Physics, University of Bologna, 2015',
            'Senior researcher in laser-material interactions'
        ]
    },
    4: {
        'id': 4,
        'name': 'Ikmanda Roswati',
        'country': 'Indonesia',
        'country_display': 'Indonesia',
        'title': 'B.Sc.',
        'sex': 'f',
        'jobTitle': 'Technical Writer',
        'expertise': ['Technical Documentation', 'Safety Standards'],
        'affiliation': {
            'name': 'Z-Beam',
            'type': 'Organization'
        },
        'credentials': [
            'B.Sc. Chemical Engineering, University of Indonesia, 2019',
            'Technical writer specializing in industrial safety'
        ]
    }
}

class AuthorNormalizer:
    """Normalizes author data across frontmatter files."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.changes_count = 0
        self.files_modified = 0
    
    def normalize_file(self, file_path: Path) -> bool:
        """
        Normalize author data in a single frontmatter file.
        
        Returns:
            bool: True if file was modified, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            if not content:
                return False
            
            original_author = content.get('author', {})
            modified = False
            
            # Case 1: Empty author object
            if not original_author or original_author == {}:
                # Default to author ID 1
                content['author'] = AUTHOR_PROFILES[1].copy()
                modified = True
                print(f"📝 {file_path.name}")
                print(f"   Added complete author profile (ID 1: Yi-Chun Lin)")
            
            # Case 2: Only has 'id' field
            elif isinstance(original_author, dict) and list(original_author.keys()) == ['id']:
                author_id = original_author['id']
                
                if author_id in AUTHOR_PROFILES:
                    content['author'] = AUTHOR_PROFILES[author_id].copy()
                    modified = True
                    print(f"📝 {file_path.name}")
                    print(f"   Expanded author ID {author_id} to full profile: {AUTHOR_PROFILES[author_id]['name']}")
                else:
                    print(f"⚠️  {file_path.name}: Unknown author ID {author_id}, using default")
                    content['author'] = AUTHOR_PROFILES[1].copy()
                    modified = True
            
            # Case 3: Already has full author data
            elif isinstance(original_author, dict) and 'name' in original_author:
                # Already normalized
                return False
            
            if not modified:
                return False
            
            # Update dateModified
            content['dateModified'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            
            self.changes_count += 1
            
            # Save if not dry run
            if not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(content, f, 
                             allow_unicode=True, 
                             sort_keys=False,
                             default_flow_style=False,
                             width=120,
                             indent=2)
                
                print(f"   💾 File updated")
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False
    
    def normalize_directory(self, directory: Path) -> Dict[str, int]:
        """
        Normalize all YAML files in a directory.
        
        Returns:
            dict: Statistics about the normalization
        """
        stats = {
            'processed': 0,
            'modified': 0,
            'errors': 0
        }
        
        yaml_files = sorted(directory.glob("*.yaml"))
        
        for file_path in yaml_files:
            stats['processed'] += 1
            try:
                if self.normalize_file(file_path):
                    stats['modified'] += 1
                    self.files_modified += 1
            except Exception as e:
                print(f"❌ Error: {file_path}: {e}")
                stats['errors'] += 1
        
        return stats


def main():
    parser = argparse.ArgumentParser(
        description="Normalize author data across all frontmatter files",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would change without modifying files'
    )
    
    parser.add_argument(
        '--type',
        choices=['compounds', 'materials', 'contaminants', 'settings'],
        help='Normalize specific content type only'
    )
    
    parser.add_argument(
        '--file',
        type=Path,
        help='Normalize a single file'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Normalize all frontmatter files'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.file, args.type, args.all]):
        parser.error("Must specify --file, --type, or --all")
    
    normalizer = AuthorNormalizer(dry_run=args.dry_run)
    
    mode = "DRY RUN" if args.dry_run else "LIVE NORMALIZATION"
    print(f"\n{'='*80}")
    print(f"AUTHOR DATA NORMALIZATION - {mode}")
    print(f"{'='*80}\n")
    
    if args.file:
        # Single file normalization
        if not args.file.exists():
            print(f"❌ File not found: {args.file}")
            return 1
        
        print(f"File: {args.file}")
        modified = normalizer.normalize_file(args.file)
        
        if modified:
            print(f"\n✅ File would be modified" if args.dry_run else "\n✅ File updated")
        else:
            print("\n✨ No changes needed")
    
    elif args.type:
        # Content type normalization
        base_path = Path(__file__).parent.parent.parent / "z-beam" / "frontmatter" / args.type
        
        if not base_path.exists():
            print(f"❌ Directory not found: {base_path}")
            return 1
        
        print(f"Content Type: {args.type}")
        print(f"Directory: {base_path}\n")
        
        stats = normalizer.normalize_directory(base_path)
        
        print(f"\n{'='*80}")
        print(f"NORMALIZATION SUMMARY - {args.type.upper()}")
        print(f"{'='*80}")
        print(f"Files processed: {stats['processed']}")
        print(f"Files modified: {stats['modified']}")
        if stats['errors']:
            print(f"Errors: {stats['errors']}")
        
        if args.dry_run:
            print(f"\n⚠️  DRY RUN - No files were actually modified")
        else:
            print(f"\n✅ Normalization complete!")
    
    elif args.all:
        # All files normalization
        base_path = Path(__file__).parent.parent.parent / "z-beam" / "frontmatter"
        
        if not base_path.exists():
            print(f"❌ Directory not found: {base_path}")
            return 1
        
        content_types = ['compounds', 'materials', 'contaminants', 'settings']
        total_stats = {'processed': 0, 'modified': 0, 'errors': 0}
        
        for content_type in content_types:
            type_path = base_path / content_type
            if type_path.exists():
                print(f"\n{'─'*80}")
                print(f"Processing {content_type.upper()}...")
                print(f"{'─'*80}")
                
                stats = normalizer.normalize_directory(type_path)
                
                for key in total_stats:
                    total_stats[key] += stats[key]
                
                print(f"  {content_type}: {stats['modified']}/{stats['processed']} files modified")
        
        print(f"\n{'='*80}")
        print(f"COMPLETE NORMALIZATION SUMMARY")
        print(f"{'='*80}")
        print(f"Total files processed: {total_stats['processed']}")
        print(f"Total files modified: {total_stats['modified']}")
        print(f"Total normalizations: {normalizer.changes_count}")
        if total_stats['errors']:
            print(f"Total errors: {total_stats['errors']}")
        
        if args.dry_run:
            print(f"\n⚠️  DRY RUN - No files were actually modified")
        else:
            print(f"\n✅ Normalization complete!")
    
    return 0


if __name__ == '__main__':
    exit(main())
