#!/usr/bin/env python3
"""
Update imports from data.materials to domains.materials

This script updates all import statements to reflect the new architecture:
- data.materials.loader → domains.materials.data_loader
- data.materials.materials → domains.materials.materials_cache
- data.materials → domains.materials.data_loader

USAGE:
    python3 scripts/tools/update_materials_imports.py --dry-run  # Preview changes
    python3 scripts/tools/update_materials_imports.py            # Apply changes
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


class ImportUpdater:
    def __init__(self, root_dir: str = '.'):
        self.root_dir = Path(root_dir)
        self.changes: List[Tuple[str, int, str, str]] = []
        
    def update_imports(self, file_path: Path, dry_run: bool = True) -> int:
        """Update imports in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")
            return 0
        
        content = original_content
        changes_count = 0
        
        # Pattern 1: from domains.materials.data_loader_v2 import ...
        pattern1 = r'from data\.materials\.loader import'
        replacement1 = 'from domains.materials.data_loader_v2 import'
        if re.search(pattern1, content):
            content = re.sub(pattern1, replacement1, content)
            changes_count += len(re.findall(pattern1, original_content))
            self.changes.append((str(file_path), changes_count, pattern1, replacement1))
        
        # Pattern 2: from domains.materials.materials_cache import ...
        pattern2 = r'from data\.materials\.materials import'
        replacement2 = 'from domains.materials.materials_cache import'
        if re.search(pattern2, content):
            count = len(re.findall(pattern2, original_content))
            content = re.sub(pattern2, replacement2, content)
            changes_count += count
            self.changes.append((str(file_path), count, pattern2, replacement2))
        
        # Pattern 3: from data.materials import ... (generic, must be specific)
        # Only match specific imports to avoid breaking other things
        pattern3 = r'from data\.materials import load_materials_data'
        replacement3 = 'from domains.materials.data_loader_v2 import load_materials_data'
        if re.search(pattern3, content):
            count = len(re.findall(pattern3, original_content))
            content = re.sub(pattern3, replacement3, content)
            changes_count += count
            self.changes.append((str(file_path), count, pattern3, replacement3))
        
        # Pattern 4: import domains.materials.data_loader
        pattern4 = r'import data\.materials\.loader'
        replacement4 = 'import domains.materials.data_loader'
        if re.search(pattern4, content):
            count = len(re.findall(pattern4, original_content))
            content = re.sub(pattern4, replacement4, content)
            changes_count += count
            self.changes.append((str(file_path), count, pattern4, replacement4))
        
        # Pattern 5: import domains.materials.materials_cache
        pattern5 = r'import data\.materials\.materials'
        replacement5 = 'import domains.materials.materials_cache'
        if re.search(pattern5, content):
            count = len(re.findall(pattern5, original_content))
            content = re.sub(pattern5, replacement5, content)
            changes_count += count
            self.changes.append((str(file_path), count, pattern5, replacement5))
        
        if changes_count > 0 and not dry_run:
            # Write updated content
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Updated {file_path} ({changes_count} import(s))")
            except Exception as e:
                print(f"❌ Error writing {file_path}: {e}")
                return 0
        elif changes_count > 0:
            print(f"🔍 Would update {file_path} ({changes_count} import(s))")
        
        return changes_count
    
    def scan_directory(self, dry_run: bool = True) -> int:
        """Scan all Python files and update imports."""
        total_files = 0
        total_changes = 0
        
        # Directories to scan
        scan_dirs = [
            'domains',
            'export',
            'scripts',
            'shared',
            'generation',
            'components',
            'postprocessing',
            'parameters',
            'learning',
            'frontmatter'
        ]
        
        for scan_dir in scan_dirs:
            dir_path = self.root_dir / scan_dir
            if not dir_path.exists():
                continue
            
            print(f"\n📁 Scanning {scan_dir}/")
            for py_file in dir_path.rglob('*.py'):
                # Skip __pycache__ directories
                if '__pycache__' in py_file.parts:
                    continue
                
                changes = self.update_imports(py_file, dry_run=dry_run)
                if changes > 0:
                    total_files += 1
                    total_changes += changes
        
        return total_files, total_changes
    
    def print_summary(self, total_files: int, total_changes: int, dry_run: bool):
        """Print summary of changes."""
        print("\n" + "="*80)
        print("📊 IMPORT UPDATE SUMMARY")
        print("="*80)
        
        if dry_run:
            print(f"🔍 DRY RUN MODE - No files were modified")
        else:
            print(f"✅ FILES UPDATED MODE - Changes applied")
        
        print(f"\n📈 Statistics:")
        print(f"   • Files affected: {total_files}")
        print(f"   • Total import statements updated: {total_changes}")
        
        if self.changes:
            print(f"\n📝 Changes by file:")
            current_file = None
            for file_path, count, pattern, replacement in self.changes:
                if file_path != current_file:
                    print(f"\n   {file_path}:")
                    current_file = file_path
                print(f"      • {pattern} → {replacement}")
        
        print("\n" + "="*80)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Update imports from data.materials to domains.materials'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--root',
        default='.',
        help='Root directory (default: current directory)'
    )
    
    args = parser.parse_args()
    
    updater = ImportUpdater(root_dir=args.root)
    
    print("🚀 Starting import update process...")
    print(f"📂 Root directory: {Path(args.root).resolve()}")
    
    if args.dry_run:
        print("🔍 Running in DRY RUN mode - no files will be modified\n")
    else:
        print("⚠️  Running in UPDATE mode - files will be modified\n")
        response = input("Continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("❌ Aborted by user")
            return
    
    total_files, total_changes = updater.scan_directory(dry_run=args.dry_run)
    updater.print_summary(total_files, total_changes, args.dry_run)
    
    if args.dry_run and total_changes > 0:
        print("\n💡 To apply changes, run without --dry-run flag:")
        print("   python3 scripts/tools/update_materials_imports.py")


if __name__ == '__main__':
    main()
