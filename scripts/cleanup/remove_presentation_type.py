#!/usr/bin/env python3
"""
Remove redundant presentation_type from sectionMetadata blocks.

The presentation_type field in sectionMetadata is redundant with the 
presentation field at the relationship level. This script removes all
occurrences from active data files.

ONLY processes active files:
- data/materials/Materials.yaml
- data/compounds/Compounds.yaml
- data/settings/Settings.yaml
- data/contaminants/Contaminants.yaml

Skips backup files (*.backup-*, *.yaml.backup-*, etc.)

USAGE:
    python3 scripts/cleanup/remove_presentation_type.py --dry-run
    python3 scripts/cleanup/remove_presentation_type.py
"""

import re
import argparse
from pathlib import Path
from typing import List, Tuple


def is_backup_file(file_path: Path) -> bool:
    """Check if this is a backup file (should be skipped)."""
    name = file_path.name
    return (
        '.backup' in name or
        'backup-' in name or
        name.endswith('.backup') or
        name.startswith('backup-')
    )


def remove_presentation_type_lines(content: str) -> Tuple[str, int]:
    """
    Remove all lines containing 'presentation_type:' from YAML content.
    
    Returns:
        (modified_content, num_removals)
    """
    lines = content.split('\n')
    removed_count = 0
    new_lines = []
    
    for line in lines:
        # Check if line contains presentation_type field
        if re.match(r'^\s*presentation_type:\s*\w+\s*$', line):
            removed_count += 1
            print(f"    Removing: {line.strip()}")
            continue
        new_lines.append(line)
    
    return '\n'.join(new_lines), removed_count


def process_file(file_path: Path, dry_run: bool = False) -> Tuple[bool, int]:
    """
    Process a single YAML file to remove presentation_type lines.
    
    Returns:
        (success, num_removals)
    """
    if is_backup_file(file_path):
        print(f"  ⏭️  Skipping backup file: {file_path.name}")
        return True, 0
    
    if not file_path.exists():
        print(f"  ⚠️  File not found: {file_path}")
        return False, 0
    
    print(f"\n📄 Processing: {file_path.name}")
    
    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove presentation_type lines
    modified_content, removed_count = remove_presentation_type_lines(content)
    
    if removed_count == 0:
        print(f"  ✅ No presentation_type fields found")
        return True, 0
    
    if dry_run:
        print(f"  🔍 DRY-RUN: Would remove {removed_count} presentation_type lines")
        return True, removed_count
    
    # Write modified content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"  ✅ Removed {removed_count} presentation_type lines")
    return True, removed_count


def main():
    parser = argparse.ArgumentParser(
        description='Remove redundant presentation_type from sectionMetadata'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    args = parser.parse_args()
    
    # Define active data files to process
    base_dir = Path(__file__).parent.parent.parent
    data_files = [
        base_dir / 'data/materials/Materials.yaml',
        base_dir / 'data/compounds/Compounds.yaml',
        base_dir / 'data/settings/Settings.yaml',
        base_dir / 'data/contaminants/Contaminants.yaml',
    ]
    
    mode = "DRY-RUN" if args.dry_run else "EXECUTION"
    print(f"\n{'='*70}")
    print(f"🧹 REMOVE PRESENTATION_TYPE - {mode}")
    print(f"{'='*70}")
    
    total_removals = 0
    processed = 0
    
    for file_path in data_files:
        if file_path.exists():
            success, removed = process_file(file_path, args.dry_run)
            if success:
                processed += 1
                total_removals += removed
    
    # Summary
    print(f"\n{'='*70}")
    print(f"📊 SUMMARY")
    print(f"{'='*70}")
    print(f"  Files processed: {processed}/{len(data_files)}")
    print(f"  Total removals: {total_removals}")
    
    if args.dry_run:
        print(f"\n  🔍 DRY-RUN complete - no files modified")
        print(f"  Run without --dry-run to apply changes")
    else:
        print(f"\n  ✅ Changes applied successfully")
    
    print()


if __name__ == '__main__':
    main()
