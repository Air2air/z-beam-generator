#!/usr/bin/env python3
"""
Remove Deprecated 'description' Field Cleanup Script
====================================================

This script systematically removes the deprecated 'description' field from:
- Data YAML files (Materials, Contaminants, Compounds, Settings)
- Export configuration files
- FrontmatterFieldOrder.yaml (already done)

The 'description' field has been replaced by 'page_description' everywhere.

Usage:
    python3 scripts/tools/remove_deprecated_description_field.py --dry-run  # Preview changes
    python3 scripts/tools/remove_deprecated_description_field.py           # Apply changes
"""

import argparse
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Define paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_FILES = [
    PROJECT_ROOT / "data/materials/Materials.yaml",
    PROJECT_ROOT / "data/contaminants/contaminants.yaml",
    PROJECT_ROOT / "data/compounds/Compounds.yaml",
    PROJECT_ROOT / "data/settings/Settings.yaml",
]
EXPORT_CONFIGS = [
    PROJECT_ROOT / "export/config/materials.yaml",
    PROJECT_ROOT / "export/config/contaminants.yaml",
    PROJECT_ROOT / "export/config/compounds.yaml",
    PROJECT_ROOT / "export/config/settings.yaml",
]


class DescriptionFieldCleaner:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.changes_made = []
        self.items_cleaned = 0
        self.files_modified = 0

    def clean_data_file(self, file_path: Path) -> Tuple[bool, int]:
        """Remove 'description' field from data YAML file."""
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            return False, 0

        print(f"\n📄 Processing: {file_path.name}")
        
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Determine the top-level key (materials, contamination_patterns, compounds, settings)
        top_key = None
        for key in ['materials', 'contamination_patterns', 'compounds', 'settings']:
            if key in data:
                top_key = key
                break
        
        if not top_key:
            print(f"   ❌ Could not find data key in {file_path.name}")
            return False, 0
        
        items = data[top_key]
        removed_count = 0
        items_with_description = []
        
        # Check each item for 'description' field
        for item_id, item_data in items.items():
            if isinstance(item_data, dict) and 'description' in item_data:
                items_with_description.append(item_id)
                removed_count += 1
                
                # Store info about what we're removing
                desc_preview = item_data['description'][:80] + "..." if len(item_data['description']) > 80 else item_data['description']
                has_page_desc = 'page_description' in item_data
                
                self.changes_made.append({
                    'file': file_path.name,
                    'item': item_id,
                    'description_preview': desc_preview,
                    'has_page_description': has_page_desc
                })
                
                if not self.dry_run:
                    del item_data['description']
        
        if removed_count > 0:
            print(f"   🔍 Found {removed_count} items with 'description' field:")
            for item_id in items_with_description[:5]:  # Show first 5
                print(f"      - {item_id}")
            if len(items_with_description) > 5:
                print(f"      ... and {len(items_with_description) - 5} more")
            
            if not self.dry_run:
                # Write back to file
                with open(file_path, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                print(f"   ✅ Removed 'description' from {removed_count} items")
                self.files_modified += 1
            else:
                print(f"   🔄 Would remove 'description' from {removed_count} items (dry-run)")
        else:
            print(f"   ✓ No 'description' fields found")
        
        self.items_cleaned += removed_count
        return removed_count > 0, removed_count

    def clean_export_config(self, file_path: Path) -> Tuple[bool, int]:
        """Remove 'description' from export configuration field lists."""
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            return False, 0

        print(f"\n📄 Processing: {file_path.name}")
        
        with open(file_path, 'r') as f:
            content = f.read()
            data = yaml.safe_load(content)
        
        removed_count = 0
        modified_sections = []
        
        # Check various sections that might have field lists
        sections_to_check = [
            'fields',
            'field_order',
            'content_fields',
            'text_fields',
        ]
        
        def remove_from_list(data_dict, path=""):
            nonlocal removed_count, modified_sections
            for key, value in data_dict.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, list) and 'description' in value:
                    if not self.dry_run:
                        value.remove('description')
                    removed_count += 1
                    modified_sections.append(current_path)
                elif isinstance(value, dict):
                    remove_from_list(value, current_path)
        
        if isinstance(data, dict):
            remove_from_list(data)
        
        if removed_count > 0:
            print(f"   🔍 Found 'description' in {removed_count} field list(s):")
            for section in modified_sections:
                print(f"      - {section}")
            
            if not self.dry_run:
                with open(file_path, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                print(f"   ✅ Removed 'description' from config")
                self.files_modified += 1
            else:
                print(f"   🔄 Would remove 'description' from config (dry-run)")
        else:
            print(f"   ✓ No 'description' references found")
        
        return removed_count > 0, removed_count

    def generate_report(self):
        """Generate summary report of changes."""
        print("\n" + "="*70)
        print("📊 CLEANUP SUMMARY")
        print("="*70)
        
        if self.dry_run:
            print("🔄 DRY RUN MODE - No files were modified")
        else:
            print(f"✅ Files modified: {self.files_modified}")
        
        print(f"📝 Total items cleaned: {self.items_cleaned}")
        print(f"🔍 Total changes found: {len(self.changes_made)}")
        
        # Check for items without page_description
        items_without_replacement = [
            c for c in self.changes_made 
            if not c['has_page_description']
        ]
        
        if items_without_replacement:
            print(f"\n⚠️  WARNING: {len(items_without_replacement)} items had 'description' but NO 'page_description':")
            for item in items_without_replacement[:5]:
                print(f"   - {item['file']}: {item['item']}")
            if len(items_without_replacement) > 5:
                print(f"   ... and {len(items_without_replacement) - 5} more")
            print("\n   These items may need manual review!")
        
        if not self.dry_run and self.files_modified > 0:
            print(f"\n✅ Cleanup complete! {self.files_modified} files updated.")
            print("   Remember to:")
            print("   1. Review the changes with: git diff")
            print("   2. Test the system to ensure nothing broke")
            print("   3. Commit the changes if everything looks good")
        elif self.dry_run:
            print("\n🔄 Run without --dry-run to apply these changes")

    def run(self):
        """Execute the cleanup process."""
        print("🧹 Deprecated 'description' Field Cleanup")
        print("="*70)
        
        if self.dry_run:
            print("🔄 Running in DRY-RUN mode (no files will be modified)")
        else:
            print("⚠️  LIVE mode - files will be modified!")
        
        # Clean data files
        print("\n" + "="*70)
        print("📁 CLEANING DATA FILES")
        print("="*70)
        for data_file in DATA_FILES:
            self.clean_data_file(data_file)
        
        # Clean export configs
        print("\n" + "="*70)
        print("⚙️  CLEANING EXPORT CONFIGURATIONS")
        print("="*70)
        for config_file in EXPORT_CONFIGS:
            self.clean_export_config(config_file)
        
        # Generate report
        self.generate_report()


def main():
    parser = argparse.ArgumentParser(
        description="Remove deprecated 'description' field from project"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Preview changes without modifying files"
    )
    
    args = parser.parse_args()
    
    cleaner = DescriptionFieldCleaner(dry_run=args.dry_run)
    cleaner.run()


if __name__ == '__main__':
    main()
