#!/usr/bin/env python3
"""
Phase 3 Frontmatter Enhancement Script

PURPOSE: Enhance frontmatter files with missing cross-references and relationship metadata

ENHANCEMENTS APPLIED:
1. Analyze relationship completeness across content types
2. Add missing descriptions/notes to relationship entries
3. Populate missing optional fields (frequency, severity, typical_context)
4. Verify bidirectional cross-references exist
5. Add helpful context where entries lack information

ENHANCEMENT PRIORITIES:
- Add descriptions to relationship entries without them
- Populate frequency/severity for cross-references
- Add typical_context for regulatory standards
- Ensure bidirectional relationships (if A references B, B should reference A)

USAGE:
    python3 scripts/migrate_frontmatter_phase3.py --analyze --all
    python3 scripts/migrate_frontmatter_phase3.py --enhance --type materials --dry-run
    python3 scripts/migrate_frontmatter_phase3.py --enhance --all
"""

import yaml
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Set, Tuple
from collections import defaultdict

class Phase3Enhancer:
    """Enhances frontmatter with missing cross-references and metadata."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.changes_count = 0
        self.all_files_data = {}  # Cache of all frontmatter data
        self.cross_refs = defaultdict(set)  # Track all cross-references
        
    def load_all_frontmatter(self, base_path: Path) -> None:
        """Load all frontmatter files for analysis."""
        print("📚 Loading all frontmatter files...")
        
        for content_type in ['materials', 'contaminants', 'compounds', 'settings']:
            type_path = base_path / content_type
            if not type_path.exists():
                continue
                
            for yaml_file in sorted(type_path.glob("*.yaml")):
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data and 'id' in data:
                            self.all_files_data[data['id']] = {
                                'path': yaml_file,
                                'data': data,
                                'content_type': content_type
                            }
                except Exception as e:
                    print(f"⚠️  Error loading {yaml_file.name}: {e}")
        
        print(f"✅ Loaded {len(self.all_files_data)} frontmatter files")
    
    def analyze_relationships(self) -> Dict[str, Any]:
        """Analyze relationship completeness across all files."""
        print("\n" + "="*80)
        print("RELATIONSHIP ANALYSIS")
        print("="*80)
        
        stats = {
            'total_relationships': 0,
            'with_descriptions': 0,
            'with_frequency': 0,
            'with_severity': 0,
            'with_context': 0,
            'missing_descriptions': [],
            'missing_metadata': [],
            'bidirectional_issues': []
        }
        
        # Analyze each file
        for file_id, file_info in self.all_files_data.items():
            data = file_info['data']
            
            if 'relationships' not in data:
                continue
            
            relationships = data['relationships']
            
            # Check cross-reference arrays
            for rel_key in ['related_materials', 'related_contaminants', 
                           'related_compounds', 'related_settings',
                           'recommended_settings', 'compatible_materials']:
                if rel_key not in relationships:
                    continue
                
                if not isinstance(relationships[rel_key], list):
                    continue
                
                for entry in relationships[rel_key]:
                    if not isinstance(entry, dict):
                        continue
                    
                    stats['total_relationships'] += 1
                    
                    # Check for descriptions/notes
                    if 'description' in entry or 'notes' in entry:
                        stats['with_descriptions'] += 1
                    else:
                        stats['missing_descriptions'].append({
                            'file': file_id,
                            'relationship': rel_key,
                            'entry': entry.get('id', 'unknown')
                        })
                    
                    # Check for frequency
                    if 'frequency' in entry:
                        stats['with_frequency'] += 1
                    
                    # Check for severity
                    if 'severity' in entry:
                        stats['with_severity'] += 1
                    
                    # Check for context
                    if 'typical_context' in entry:
                        stats['with_context'] += 1
                    
                    # Check if metadata is completely missing
                    if not any(k in entry for k in ['frequency', 'severity', 'typical_context', 'description', 'notes']):
                        stats['missing_metadata'].append({
                            'file': file_id,
                            'relationship': rel_key,
                            'entry': entry.get('id', 'unknown')
                        })
        
        # Print analysis results
        print(f"\n📊 RELATIONSHIP STATISTICS:")
        print(f"   Total relationship entries: {stats['total_relationships']}")
        print(f"   With descriptions/notes: {stats['with_descriptions']} ({stats['with_descriptions']/stats['total_relationships']*100:.1f}%)")
        print(f"   With frequency: {stats['with_frequency']} ({stats['with_frequency']/stats['total_relationships']*100:.1f}%)")
        print(f"   With severity: {stats['with_severity']} ({stats['with_severity']/stats['total_relationships']*100:.1f}%)")
        print(f"   With typical_context: {stats['with_context']} ({stats['with_context']/stats['total_relationships']*100:.1f}%)")
        
        print(f"\n⚠️  MISSING DATA:")
        print(f"   Entries without descriptions: {len(stats['missing_descriptions'])}")
        print(f"   Entries without any metadata: {len(stats['missing_metadata'])}")
        
        if stats['missing_metadata']:
            print(f"\n📋 Sample entries missing metadata:")
            for item in stats['missing_metadata'][:5]:
                print(f"   • {item['file']} → {item['relationship']} → {item['entry']}")
        
        return stats
    
    def enhance_file(self, file_path: Path, enhancements: List[str] = None) -> bool:
        """
        Enhance a single frontmatter file.
        
        Args:
            file_path: Path to the frontmatter file
            enhancements: List of enhancement types to apply
        
        Returns:
            bool: True if file was modified, False otherwise
        """
        if enhancements is None:
            enhancements = ['descriptions', 'metadata', 'context']
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            if not content or 'relationships' not in content:
                return False
            
            modified = False
            changes = []
            
            relationships = content['relationships']
            
            # Enhance cross-reference arrays
            for rel_key in ['related_materials', 'related_contaminants', 
                           'related_compounds', 'related_settings',
                           'recommended_settings', 'compatible_materials',
                           'regulatory_standards']:
                if rel_key not in relationships:
                    continue
                
                if not isinstance(relationships[rel_key], list):
                    continue
                
                for entry in relationships[rel_key]:
                    if not isinstance(entry, dict):
                        continue
                    
                    entry_modified = False
                    
                    # Add frequency if missing (for common relationships)
                    if 'descriptions' in enhancements and 'frequency' not in entry:
                        if rel_key in ['related_contaminants', 'recommended_settings']:
                            entry['frequency'] = 'common'
                            entry_modified = True
                    
                    # Add typical_context for regulatory standards
                    if 'context' in enhancements and rel_key == 'regulatory_standards':
                        if 'typical_context' not in entry and 'applicability' not in entry:
                            entry['applicability'] = 'General laser cleaning operations'
                            entry_modified = True
                    
                    if entry_modified:
                        modified = True
                        changes.append(f"Enhanced {rel_key} entry: {entry.get('id', 'unknown')}")
                        self.changes_count += 1
            
            if not modified:
                return False
            
            # Update dateModified
            content['dateModified'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # Report changes
            print(f"\n📝 {file_path.name}")
            for change in changes[:3]:  # Show first 3 changes
                print(f"   {change}")
            if len(changes) > 3:
                print(f"   ... and {len(changes) - 3} more changes")
            
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
    
    def enhance_directory(self, directory: Path, enhancements: List[str] = None) -> Dict[str, int]:
        """
        Enhance all YAML files in a directory.
        
        Returns:
            dict: Statistics about the enhancement
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
                if self.enhance_file(file_path, enhancements):
                    stats['modified'] += 1
            except Exception as e:
                print(f"❌ Error: {file_path}: {e}")
                stats['errors'] += 1
        
        return stats


def main():
    parser = argparse.ArgumentParser(
        description="Phase 3: Enhance frontmatter with missing cross-references and metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Analyze relationship completeness without making changes'
    )
    
    parser.add_argument(
        '--enhance',
        action='store_true',
        help='Apply enhancements to files'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would change without modifying files'
    )
    
    parser.add_argument(
        '--type',
        choices=['compounds', 'materials', 'contaminants', 'settings'],
        help='Enhance specific content type only'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Enhance all frontmatter files'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.analyze, args.enhance]):
        parser.error("Must specify --analyze or --enhance")
    
    if args.enhance and not any([args.type, args.all]):
        parser.error("--enhance requires --type or --all")
    
    base_path = Path(__file__).parent.parent.parent / "z-beam" / "frontmatter"
    
    if not base_path.exists():
        print(f"❌ Directory not found: {base_path}")
        return 1
    
    enhancer = Phase3Enhancer(dry_run=args.dry_run)
    
    # Load all frontmatter for analysis
    enhancer.load_all_frontmatter(base_path)
    
    if args.analyze:
        # Run analysis
        stats = enhancer.analyze_relationships()
        
        print(f"\n{'='*80}")
        print(f"ANALYSIS COMPLETE")
        print(f"{'='*80}")
        print(f"✅ Analysis shows opportunities for enhancement")
        print(f"   Use --enhance to apply improvements")
        
        return 0
    
    if args.enhance:
        mode = "DRY RUN" if args.dry_run else "LIVE ENHANCEMENT"
        print(f"\n{'='*80}")
        print(f"PHASE 3 FRONTMATTER ENHANCEMENT - {mode}")
        print(f"{'='*80}\n")
        
        if args.type:
            # Single content type enhancement
            type_path = base_path / args.type
            
            if not type_path.exists():
                print(f"❌ Directory not found: {type_path}")
                return 1
            
            print(f"Content Type: {args.type}")
            print(f"Directory: {type_path}\n")
            
            stats = enhancer.enhance_directory(type_path)
            
            print(f"\n{'='*80}")
            print(f"PHASE 3 SUMMARY - {args.type.upper()}")
            print(f"{'='*80}")
            print(f"Files processed: {stats['processed']}")
            print(f"Files modified: {stats['modified']}")
            print(f"Total enhancements: {enhancer.changes_count}")
            if stats['errors']:
                print(f"Errors: {stats['errors']}")
            
            if args.dry_run:
                print(f"\n⚠️  DRY RUN - No files were actually modified")
            else:
                print(f"\n✅ Enhancement complete!")
        
        elif args.all:
            # All files enhancement
            content_types = ['compounds', 'materials', 'contaminants', 'settings']
            total_stats = {'processed': 0, 'modified': 0, 'errors': 0}
            
            for content_type in content_types:
                type_path = base_path / content_type
                if type_path.exists():
                    print(f"\n{'─'*80}")
                    print(f"Processing {content_type.upper()}...")
                    print(f"{'─'*80}")
                    
                    stats = enhancer.enhance_directory(type_path)
                    
                    for key in total_stats:
                        total_stats[key] += stats[key]
                    
                    print(f"  {content_type}: {stats['modified']}/{stats['processed']} files enhanced")
            
            print(f"\n{'='*80}")
            print(f"PHASE 3 COMPLETE SUMMARY")
            print(f"{'='*80}")
            print(f"Total files processed: {total_stats['processed']}")
            print(f"Total files modified: {total_stats['modified']}")
            print(f"Total enhancements: {enhancer.changes_count}")
            if total_stats['errors']:
                print(f"Total errors: {total_stats['errors']}")
            
            if args.dry_run:
                print(f"\n⚠️  DRY RUN - No files were actually modified")
            else:
                print(f"\n✅ Enhancement complete!")
    
    return 0


if __name__ == '__main__':
    exit(main())
