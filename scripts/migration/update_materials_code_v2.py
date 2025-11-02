#!/usr/bin/env python3
"""
Code Update Script for Materials Module V2.0

Updates all Python code to use 'materialProperties' instead of 'properties'
in the materials module.

Usage:
    python3 scripts/migration/update_materials_code_v2.py [--dry-run]
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class CodeUpdater:
    """Updates materials module code for V2.0"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.materials_dir = project_root / "materials"
        self.changes_count = 0
        self.files_modified = []
    
    def find_python_files(self) -> List[Path]:
        """Find all Python files in materials module"""
        return list(self.materials_dir.rglob("*.py"))
    
    def update_file(self, file_path: Path, dry_run: bool = False) -> int:
        """Update a single file, return number of changes"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        original_content = content
        changes = 0
        
        # Pattern 1: material['properties'] → material['materialProperties']
        # Pattern 2: material.get('properties') → material.get('materialProperties')
        # Pattern 3: data['properties'] → data['materialProperties']
        # Pattern 4: data.get('properties') → data.get('materialProperties')
        # BUT preserve: category_data.get('properties') - this is for categories.yaml
        # BUT preserve: schema['properties'] - this is JSON schema structure
        # BUT preserve: frontmatter_schema['properties'] - this is JSON schema
        
        # Step 1: Replace dictionary access patterns
        # Count changes by tracking actual replacements
        
        # Pattern 1: material_entry['properties'] → material_entry['materialProperties']
        pattern1 = r"material_entry\['properties'\]"
        new_content, n1 = re.subn(pattern1, "material_entry['materialProperties']", content)
        content = new_content
        changes += n1
        
        # Pattern 2: material_data['properties'] → material_data['materialProperties']
        pattern2 = r"material_data\['properties'\]"
        new_content, n2 = re.subn(pattern2, "material_data['materialProperties']", content)
        content = new_content
        changes += n2
        
        # Pattern 3: material['properties'] → material['materialProperties']
        pattern3 = r"material\['properties'\]"
        new_content, n3 = re.subn(pattern3, "material['materialProperties']", content)
        content = new_content
        changes += n3
        
        # Pattern 4: material_entry.get('properties' → material_entry.get('materialProperties'
        pattern4 = r"material_entry\.get\('properties'"
        new_content, n4 = re.subn(pattern4, "material_entry.get('materialProperties'", content)
        content = new_content
        changes += n4
        
        # Pattern 5: material_data.get('properties' → material_data.get('materialProperties'
        pattern5 = r"material_data\.get\('properties'"
        new_content, n5 = re.subn(pattern5, "material_data.get('materialProperties'", content)
        content = new_content
        changes += n5
        
        # Pattern 6: material.get('properties' → material.get('materialProperties'
        # BUT NOT: schema.get('properties' or frontmatter_schema.get('properties'
        pattern6 = r"(?<!schema\.)(?<!_schema\.)material\.get\('properties'"
        new_content, n6 = re.subn(pattern6, "material.get('materialProperties'", content)
        content = new_content
        changes += n6
        
        # Pattern 7: properties = material_data.get('properties', {})
        pattern7 = r"properties = material_data\.get\('properties', \{\}\)"
        new_content, n7 = re.subn(pattern7, "properties = material_data.get('materialProperties', {})", content)
        content = new_content
        changes += n7
        
        # Pattern 8: corrected_data['properties'] = {}
        pattern8 = r"corrected_data\['properties'\] = \{\}"
        new_content, n8 = re.subn(pattern8, "corrected_data['materialProperties'] = {}", content)
        content = new_content
        changes += n8
        
        # Write changes if not dry run and content changed
        if content != original_content:
            self.changes_count += changes
            self.files_modified.append(file_path)
            
            if not dry_run:
                with open(file_path, 'w') as f:
                    f.write(content)
            
            return changes
        
        return 0
    
    def update_all(self, dry_run: bool = False) -> Tuple[int, int]:
        """Update all Python files"""
        files = self.find_python_files()
        
        print(f"🔍 Found {len(files)} Python files in materials module")
        
        if dry_run:
            print("🔍 DRY RUN MODE - No files will be modified\n")
        else:
            print("🔄 Updating files...\n")
        
        total_changes = 0
        
        for file_path in files:
            changes = self.update_file(file_path, dry_run)
            if changes > 0:
                rel_path = file_path.relative_to(self.project_root)
                status = "Would update" if dry_run else "Updated"
                print(f"  {status}: {rel_path} ({changes} changes)")
                total_changes += changes
        
        return total_changes, len(self.files_modified)
    
    def report(self, dry_run: bool = False):
        """Print summary report"""
        mode = "DRY RUN" if dry_run else "COMPLETE"
        print(f"\n{'=' * 60}")
        print(f"CODE UPDATE {mode}")
        print(f"{'=' * 60}")
        print(f"Files modified: {len(self.files_modified)}")
        print(f"Total changes: {self.changes_count}")
        
        if dry_run:
            print("\n🔍 DRY RUN - No files were actually modified")
        else:
            print("\n✅ All files updated successfully")
        print(f"{'=' * 60}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Update materials module code for V2.0'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path.cwd()
    
    if not (project_root / "materials").exists():
        print("❌ materials/ directory not found")
        return 1
    
    # Create updater and run
    updater = CodeUpdater(project_root)
    updater.update_all(dry_run=args.dry_run)
    updater.report(dry_run=args.dry_run)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
