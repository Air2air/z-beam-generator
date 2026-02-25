#!/usr/bin/env python3
"""
Phase 2 Frontmatter Migration Script

PURPOSE: Reorganize scattered top-level keys under 'relationships' parent key

CHANGES APPLIED:
1. Move technical data under relationships (laser_properties, machine_settings, material_properties)
2. Move regulatory data under relationships (regulatory_standards, regulatory_classification)
3. Move compatibility data under relationships (compatible_materials, prohibited_materials)
4. Move safety data under relationships (ppe_requirements, emergency_response)
5. Move chemical data under relationships (physical_properties, chemical_properties, reactivity)
6. Move production data under relationships (produced_by_materials, produced_by_contaminants)
7. Move exposure data under relationships (workplace_exposure, exposure_limits)
8. Preserve all cross-reference arrays (related_materials, related_contaminants, etc.)

PRIORITY:
- Phase 2.1: Compounds (~50 files) - Most scattered data
- Phase 2.2: Materials (153 files) - Moderate reorganization needed
- Phase 2.3: Contaminants (196 files) - Light reorganization + verification
- Phase 2.4: Settings (255 files) - Similar to contaminants

USAGE:
    python3 scripts/migrate_frontmatter_phase2.py --dry-run --all
    python3 scripts/migrate_frontmatter_phase2.py --type compounds
    python3 scripts/migrate_frontmatter_phase2.py --file frontmatter/compounds/acetaldehyde-compound.yaml
"""

import yaml
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Set

class Phase2Migrator:
    """Reorganizes scattered top-level keys under 'relationships' parent."""
    
    # Keys that should stay at top level (page identity & content)
    TOP_LEVEL_KEYS = {
        'id', 'name', 'display_name', 'title', 'slug', 'category', 'subcategory',
        'content_type', 'schema_version', 'datePublished', 'dateModified',
        'description', 'micro', 'faq', 'author', 'images', 'breadcrumb', 'breadcrumb_text'
    }
    
    # Keys that should be moved to relationships (if not already there)
    RELATIONSHIP_KEYS = {
        # Cross-references (already should be under relationships, but verify)
        'related_materials', 'related_contaminants', 'related_compounds', 'related_settings',
        
        # Production & Sources
        'produced_by_contaminants', 'produced_by_materials',
        
        # Regulatory & Standards
        'regulatory_standards', 'regulatory_classification',
        
        # Compatibility
        'compatible_materials', 'prohibited_materials', 'recommended_settings',
        
        # Technical Data
        'laser_properties', 'machine_settings', 'material_properties', 'optical_properties',
        
        # Safety & PPE
        'ppe_requirements', 'emergency_response', 'storage_requirements',
        
        # Exposure & Monitoring
        'workplace_exposure', 'exposure_limits', 'detection_monitoring',
        
        # Chemical Data
        'physical_properties', 'chemical_properties', 'reactivity', 'environmental_impact',
        
        # Identifiers & Metadata
        'synonyms_identifiers', 'health_effects_keywords', 'sources_in_laser_cleaning',
        
        # Applications
        'applications', 'characteristics', 'challenges',
        
        # Composition (Contaminants)
        'composition', 'visual_characteristics'
    }
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.changes_count = 0
    
    def migrate_file(self, file_path: Path) -> bool:
        """
        Migrate a single frontmatter file.
        
        Returns:
            bool: True if file was modified, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            if not content:
                return False
            
            original_content = yaml.dump(content, allow_unicode=True, sort_keys=False)
            keys_moved = []
            
            # Find keys at top level that should be under relationships
            top_level_keys = set(content.keys())
            keys_to_move = top_level_keys & self.RELATIONSHIP_KEYS
            
            if not keys_to_move:
                return False  # Nothing to migrate
            
            # Create relationships dict if it doesn't exist
            if 'relationships' not in content:
                content['relationships'] = {}
            
            # Move each key
            for key in sorted(keys_to_move):
                if key not in content['relationships']:
                    content['relationships'][key] = content.pop(key)
                    keys_moved.append(key)
                    self.changes_count += 1
            
            if not keys_moved:
                return False
            
            # Update dateModified
            content['dateModified'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # Report changes
            print(f"\n📝 {file_path.name}")
            print(f"   Moved to relationships: {', '.join(keys_moved)}")
            
            # Save if not dry run
            if not self.dry_run:
                # Preserve order: top-level identity fields first, then relationships
                ordered_content = {}
                
                # Add top-level keys in preferred order
                for key in ['id', 'name', 'display_name', 'title', 'slug', 'category', 
                           'subcategory', 'content_type', 'schema_version', 
                           'datePublished', 'dateModified']:
                    if key in content:
                        ordered_content[key] = content[key]
                
                # Add remaining top-level keys (description, micro, faq, etc.)
                for key in content.keys():
                    if key not in ordered_content and key != 'relationships':
                        ordered_content[key] = content[key]
                
                # Add relationships last
                if 'relationships' in content:
                    ordered_content['relationships'] = content['relationships']
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    # Write with proper formatting
                    yaml.dump(ordered_content, f, 
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
    
    def migrate_directory(self, directory: Path, recursive: bool = True) -> Dict[str, int]:
        """
        Migrate all YAML files in a directory.
        
        Returns:
            dict: Statistics about the migration
        """
        stats = {
            'processed': 0,
            'modified': 0,
            'errors': 0
        }
        
        pattern = "**/*.yaml" if recursive else "*.yaml"
        yaml_files = sorted(directory.glob(pattern))
        
        for file_path in yaml_files:
            stats['processed'] += 1
            try:
                if self.migrate_file(file_path):
                    stats['modified'] += 1
            except Exception as e:
                print(f"❌ Error: {file_path}: {e}")
                stats['errors'] += 1
        
        return stats


def main():
    parser = argparse.ArgumentParser(
        description="Phase 2: Reorganize frontmatter by moving scattered keys under relationships",
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
        help='Migrate specific content type only'
    )
    
    parser.add_argument(
        '--file',
        type=Path,
        help='Migrate a single file'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Migrate all frontmatter files'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.file, args.type, args.all]):
        parser.error("Must specify --file, --type, or --all")
    
    migrator = Phase2Migrator(dry_run=args.dry_run)
    
    mode = "DRY RUN" if args.dry_run else "LIVE MIGRATION"
    print(f"\n{'='*80}")
    print(f"PHASE 2 FRONTMATTER MIGRATION - {mode}")
    print(f"{'='*80}\n")
    
    if args.file:
        # Single file migration
        if not args.file.exists():
            print(f"❌ File not found: {args.file}")
            return 1
        
        print(f"File: {args.file}")
        modified = migrator.migrate_file(args.file)
        
        if modified:
            print(f"\n✅ File would be modified" if args.dry_run else "\n✅ File updated")
        else:
            print("\n✨ No changes needed")
    
    elif args.type:
        # Content type migration
        base_path = Path(__file__).parent.parent.parent / "z-beam" / "frontmatter" / args.type
        
        if not base_path.exists():
            print(f"❌ Directory not found: {base_path}")
            return 1
        
        print(f"Content Type: {args.type}")
        print(f"Directory: {base_path}\n")
        
        stats = migrator.migrate_directory(base_path, recursive=True)
        
        print(f"\n{'='*80}")
        print(f"PHASE 2 SUMMARY - {args.type.upper()}")
        print(f"{'='*80}")
        print(f"Files processed: {stats['processed']}")
        print(f"Files modified: {stats['modified']}")
        print(f"Total keys moved: {migrator.changes_count}")
        if stats['errors']:
            print(f"Errors: {stats['errors']}")
        
        if args.dry_run:
            print(f"\n⚠️  DRY RUN - No files were actually modified")
        else:
            print(f"\n✅ Migration complete!")
    
    elif args.all:
        # All files migration
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
                
                stats = migrator.migrate_directory(type_path, recursive=True)
                
                for key in total_stats:
                    total_stats[key] += stats[key]
                
                print(f"  {content_type}: {stats['modified']}/{stats['processed']} files modified")
        
        print(f"\n{'='*80}")
        print(f"PHASE 2 COMPLETE SUMMARY")
        print(f"{'='*80}")
        print(f"Total files processed: {total_stats['processed']}")
        print(f"Total files modified: {total_stats['modified']}")
        print(f"Total keys moved: {migrator.changes_count}")
        if total_stats['errors']:
            print(f"Total errors: {total_stats['errors']}")
        
        if args.dry_run:
            print(f"\n⚠️  DRY RUN - No files were actually modified")
        else:
            print(f"\n✅ Migration complete!")
    
    return 0


if __name__ == '__main__':
    exit(main())
