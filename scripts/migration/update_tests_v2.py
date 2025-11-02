#!/usr/bin/env python3
"""
Test Update Script for Materials Module V2.0

Updates all test files to use 'materialProperties' instead of 'properties'
for materials.yaml structure.

Usage:
    python3 scripts/migration/update_tests_v2.py [--dry-run]
"""

import sys
import re
from pathlib import Path
from typing import List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestUpdater:
    """Updates test files for V2.0"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tests_dir = project_root / "tests"
        self.changes_count = 0
        self.files_modified = []
    
    def find_test_files(self) -> List[Path]:
        """Find all Python test files"""
        return list(self.tests_dir.rglob("*.py"))
    
    def update_file(self, file_path: Path, dry_run: bool = False) -> int:
        """Update a single test file, return number of changes"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        original_content = content
        changes = 0
        
        # Pattern 1: material_data['properties'] → material_data['materialProperties']
        pattern1 = r"material_data\['properties'\]"
        new_content, n1 = re.subn(pattern1, "material_data['materialProperties']", content)
        content = new_content
        changes += n1
        
        # Pattern 2: mat_data['properties'] → mat_data['materialProperties']
        pattern2 = r"mat_data\['properties'\]"
        new_content, n2 = re.subn(pattern2, "mat_data['materialProperties']", content)
        content = new_content
        changes += n2
        
        # Pattern 3: material_data.get('properties' → material_data.get('materialProperties'
        pattern3 = r"material_data\.get\('properties'"
        new_content, n3 = re.subn(pattern3, "material_data.get('materialProperties'", content)
        content = new_content
        changes += n3
        
        # Pattern 4: mat_data.get('properties' → mat_data.get('materialProperties'
        pattern4 = r"mat_data\.get\('properties'"
        new_content, n4 = re.subn(pattern4, "mat_data.get('materialProperties'", content)
        content = new_content
        changes += n4
        
        # Pattern 5: item['properties'] → item['materialProperties'] (for materials iteration)
        # Only in test_materials_uniqueness_requirements.py
        if 'test_materials_uniqueness_requirements.py' in str(file_path):
            pattern5 = r"item\['properties'\]"
            new_content, n5 = re.subn(pattern5, "item['materialProperties']", content)
            content = new_content
            changes += n5
            
            pattern5b = r"item\.get\('properties'"
            new_content, n5b = re.subn(pattern5b, "item.get('materialProperties'", content)
            content = new_content
            changes += n5b
        
        # Pattern 6: props = material_data.get('properties', {})
        pattern6 = r"props = material_data\.get\('properties', \{\}\)"
        new_content, n6 = re.subn(pattern6, "props = material_data.get('materialProperties', {})", content)
        content = new_content
        changes += n6
        
        # Pattern 7: properties = material_data.get('properties', {})
        pattern7 = r"properties = material_data\.get\('properties', \{\}\)"
        new_content, n7 = re.subn(pattern7, "properties = material_data.get('materialProperties', {})", content)
        content = new_content
        changes += n7
        
        # Pattern 8: properties = material_data['properties']
        pattern8 = r"properties = material_data\['properties'\]"
        new_content, n8 = re.subn(pattern8, "properties = material_data['materialProperties']", content)
        content = new_content
        changes += n8
        
        # Pattern 9: enhanced['properties'] in test_property_enhancer.py
        if 'test_property_enhancer.py' in str(file_path):
            pattern9 = r"enhanced\['properties'\]"
            new_content, n9 = re.subn(pattern9, "enhanced['materialProperties']", content)
            content = new_content
            changes += n9
            
            pattern9b = r"steel\['properties'\]"
            new_content, n9b = re.subn(pattern9b, "steel['materialProperties']", content)
            content = new_content
            changes += n9b
        
        # Pattern 10: other_section['properties'] / updated_properties
        if 'test_validation_stage3_fix.py' in str(file_path):
            pattern10 = r"other_section\['properties'\]"
            new_content, n10 = re.subn(pattern10, "other_section['materialProperties']", content)
            content = new_content
            changes += n10
            
            pattern10b = r"other_section\.get\('properties'"
            new_content, n10b = re.subn(pattern10b, "other_section.get('materialProperties'", content)
            content = new_content
            changes += n10b
        
        # Pattern 11: test_audit_frontmatter_regeneration.py
        if 'test_audit_frontmatter_regeneration.py' in str(file_path):
            pattern11 = r"material_data\['properties'\]\['density'\]"
            new_content, n11 = re.subn(pattern11, "material_data['materialProperties']['density']", content)
            content = new_content
            changes += n11
        
        # Pattern 12: test_range_propagation.py - copper_material references
        if 'test_range_propagation.py' in str(file_path):
            pattern12 = r"copper_material\['properties'\]"
            new_content, n12 = re.subn(pattern12, "copper_material['materialProperties']", content)
            content = new_content
            changes += n12
        
        # Write changes if not dry run and content changed
        if content != original_content:
            self.changes_count += changes
            self.files_modified.append(file_path)
            
            if not dry_run:
                with open(file_path, 'w') as f:
                    f.write(content)
            
            return changes
        
        return 0
    
    def update_all(self, dry_run: bool = False) -> tuple:
        """Update all test files"""
        files = self.find_test_files()
        
        print(f"🔍 Found {len(files)} test files")
        
        if dry_run:
            print("🔍 DRY RUN MODE - No files will be modified\n")
        else:
            print("🔄 Updating test files...\n")
        
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
        print(f"TEST UPDATE {mode}")
        print(f"{'=' * 60}")
        print(f"Files modified: {len(self.files_modified)}")
        print(f"Total changes: {self.changes_count}")
        
        if dry_run:
            print("\n🔍 DRY RUN - No files were actually modified")
        else:
            print("\n✅ All test files updated successfully")
        print(f"{'=' * 60}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Update test files for materials V2.0'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path.cwd()
    
    if not (project_root / "tests").exists():
        print("❌ tests/ directory not found")
        return 1
    
    # Create updater and run
    updater = TestUpdater(project_root)
    updater.update_all(dry_run=args.dry_run)
    updater.report(dry_run=args.dry_run)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
