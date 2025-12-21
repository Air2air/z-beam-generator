#!/usr/bin/env python3
"""
Export Diff Tool

Compare two frontmatter export runs to see what changed.
Tracks additions, modifications, deletions, and field-level changes.

Usage:
    # Compare two export directories
    python3 scripts/tools/export_diff.py \\
        --before ../z-beam/frontmatter.backup \\
        --after ../z-beam/frontmatter

    # Compare specific domain
    python3 scripts/tools/export_diff.py \\
        --before backup/ --after current/ \\
        --domain materials

    # JSON output
    python3 scripts/tools/export_diff.py --before backup/ --after current/ --json

Created: December 20, 2025
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple
import yaml

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


def load_frontmatter(file_path: Path) -> Dict:
    """Load frontmatter from YAML file"""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"⚠️  Warning: Could not load {file_path}: {e}", file=sys.stderr)
        return {}


def get_files_in_domain(domain_path: Path) -> Dict[str, Path]:
    """Get all YAML files in a domain directory"""
    if not domain_path.exists():
        return {}
    
    files = {}
    for file_path in domain_path.glob('*.yaml'):
        files[file_path.name] = file_path
    
    return files


def compare_frontmatter(before: Dict, after: Dict, item_name: str) -> Dict:
    """
    Compare two frontmatter dicts and return differences.
    
    Returns:
        Dict with 'modified_fields', 'added_fields', 'removed_fields'
    """
    diff = {
        'modified_fields': {},
        'added_fields': {},
        'removed_fields': {}
    }
    
    before_keys = set(before.keys())
    after_keys = set(after.keys())
    
    # Removed fields
    for key in before_keys - after_keys:
        diff['removed_fields'][key] = before[key]
    
    # Added fields
    for key in after_keys - before_keys:
        diff['added_fields'][key] = after[key]
    
    # Modified fields
    for key in before_keys & after_keys:
        before_val = before[key]
        after_val = after[key]
        
        if before_val != after_val:
            diff['modified_fields'][key] = {
                'before': before_val,
                'after': after_val
            }
    
    return diff


def compare_domain(before_path: Path, after_path: Path, domain: str) -> Dict:
    """
    Compare frontmatter for a specific domain.
    
    Returns:
        Dict with 'added', 'modified', 'removed', 'unchanged' counts and details
    """
    before_domain_path = before_path / domain
    after_domain_path = after_path / domain
    
    before_files = get_files_in_domain(before_domain_path)
    after_files = get_files_in_domain(after_domain_path)
    
    before_names = set(before_files.keys())
    after_names = set(after_files.keys())
    
    result = {
        'domain': domain,
        'added': [],
        'removed': [],
        'modified': [],
        'unchanged': [],
        'added_count': 0,
        'removed_count': 0,
        'modified_count': 0,
        'unchanged_count': 0
    }
    
    # Removed files
    for name in before_names - after_names:
        result['removed'].append(name)
        result['removed_count'] += 1
    
    # Added files
    for name in after_names - before_names:
        result['added'].append(name)
        result['added_count'] += 1
    
    # Compare existing files
    for name in before_names & after_names:
        before_data = load_frontmatter(before_files[name])
        after_data = load_frontmatter(after_files[name])
        
        if before_data != after_data:
            diff = compare_frontmatter(before_data, after_data, name)
            result['modified'].append({
                'file': name,
                'diff': diff
            })
            result['modified_count'] += 1
        else:
            result['unchanged'].append(name)
            result['unchanged_count'] += 1
    
    return result


def print_diff_report(results: Dict[str, Dict], show_details: bool = False):
    """Print human-readable diff report"""
    print("\n" + "="*80)
    print("📊 EXPORT DIFF REPORT")
    print("="*80)
    
    total_added = 0
    total_removed = 0
    total_modified = 0
    total_unchanged = 0
    
    for domain, result in sorted(results.items()):
        print(f"\n🔹 {domain.upper()}")
        print(f"  ✅ Added: {result['added_count']}")
        print(f"  ❌ Removed: {result['removed_count']}")
        print(f"  📝 Modified: {result['modified_count']}")
        print(f"  ⚪ Unchanged: {result['unchanged_count']}")
        
        total_added += result['added_count']
        total_removed += result['removed_count']
        total_modified += result['modified_count']
        total_unchanged += result['unchanged_count']
        
        if show_details:
            # Show added files
            if result['added']:
                print(f"\n  ✅ Added files:")
                for name in sorted(result['added'])[:5]:
                    print(f"     + {name}")
                if len(result['added']) > 5:
                    print(f"     ... and {len(result['added']) - 5} more")
            
            # Show removed files
            if result['removed']:
                print(f"\n  ❌ Removed files:")
                for name in sorted(result['removed'])[:5]:
                    print(f"     - {name}")
                if len(result['removed']) > 5:
                    print(f"     ... and {len(result['removed']) - 5} more")
            
            # Show modified files
            if result['modified']:
                print(f"\n  📝 Modified files:")
                for item in sorted(result['modified'], key=lambda x: x['file'])[:5]:
                    name = item['file']
                    diff = item['diff']
                    field_count = len(diff['modified_fields']) + len(diff['added_fields']) + len(diff['removed_fields'])
                    print(f"     ~ {name} ({field_count} field changes)")
                if len(result['modified']) > 5:
                    print(f"     ... and {len(result['modified']) - 5} more")
    
    # Summary
    print("\n" + "="*80)
    print("📊 TOTAL SUMMARY")
    print("="*80)
    print(f"✅ Added:     {total_added:3d}")
    print(f"❌ Removed:   {total_removed:3d}")
    print(f"📝 Modified:  {total_modified:3d}")
    print(f"⚪ Unchanged: {total_unchanged:3d}")
    print(f"📊 Total:     {total_added + total_removed + total_modified + total_unchanged:3d}")
    
    if total_modified > 0:
        print(f"\n💡 TIP: Use --details to see field-level changes")
    
    print("="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Compare two frontmatter export runs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare backup vs current
  python3 scripts/tools/export_diff.py --before ../z-beam/frontmatter.backup --after ../z-beam/frontmatter
  
  # Compare specific domain
  python3 scripts/tools/export_diff.py --before backup/ --after current/ --domain materials
  
  # Show detailed changes
  python3 scripts/tools/export_diff.py --before backup/ --after current/ --details
  
  # JSON output
  python3 scripts/tools/export_diff.py --before backup/ --after current/ --json
        """
    )
    
    parser.add_argument('--before', required=True, help='Path to before export directory')
    parser.add_argument('--after', required=True, help='Path to after export directory')
    parser.add_argument('--domain', help='Compare specific domain only (materials, contaminants, etc.)')
    parser.add_argument('--details', action='store_true', help='Show detailed field-level changes')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    before_path = Path(args.before).resolve()
    after_path = Path(args.after).resolve()
    
    # Validate paths
    if not before_path.exists():
        print(f"❌ Error: Before path does not exist: {before_path}", file=sys.stderr)
        sys.exit(1)
    
    if not after_path.exists():
        print(f"❌ Error: After path does not exist: {after_path}", file=sys.stderr)
        sys.exit(1)
    
    # Determine domains to compare
    if args.domain:
        domains = [args.domain]
    else:
        # Auto-discover domains from after directory
        domains = [d.name for d in after_path.iterdir() if d.is_dir()]
        if not domains:
            # Try before directory
            domains = [d.name for d in before_path.iterdir() if d.is_dir()]
    
    if not domains:
        print(f"❌ Error: No domains found in {after_path} or {before_path}", file=sys.stderr)
        sys.exit(1)
    
    # Compare each domain
    results = {}
    for domain in sorted(domains):
        results[domain] = compare_domain(before_path, after_path, domain)
    
    # Output results
    if args.json:
        import json
        print(json.dumps(results, indent=2))
    else:
        print_diff_report(results, show_details=args.details)
    
    # Exit with error code if there are changes
    has_changes = any(
        r['added_count'] > 0 or r['removed_count'] > 0 or r['modified_count'] > 0
        for r in results.values()
    )
    
    sys.exit(1 if has_changes else 0)


if __name__ == '__main__':
    main()
