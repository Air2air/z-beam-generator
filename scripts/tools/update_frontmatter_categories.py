#!/usr/bin/env python3
"""
Update frontmatter YAML files from 3-category to 2-category structure.

Consolidates materialProperties categories:
- energy_coupling → laser_material_interaction (renamed)
- structural_response + material_properties → material_characteristics (merged)

Preserves all property data: value, unit, confidence, description, min, max, source, notes
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import shutil

# Root directory
ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTMATTER_DIR = ROOT_DIR / "content" / "components" / "frontmatter"
BACKUP_DIR = ROOT_DIR / "backups" / f"frontmatter_3to2_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Category mapping
OLD_TO_NEW_CATEGORIES = {
    'energy_coupling': 'laser_material_interaction',
    'structural_response': 'material_characteristics',
    'material_properties': 'material_characteristics'
}

NEW_CATEGORY_LABELS = {
    'laser_material_interaction': 'Laser-Material Interaction',
    'material_characteristics': 'Material Characteristics'
}

NEW_CATEGORY_DESCRIPTIONS = {
    'laser_material_interaction': 'Optical and thermal properties governing laser energy absorption, reflection, propagation, and ablation thresholds',
    'material_characteristics': 'Intrinsic physical, mechanical, chemical, and structural properties affecting cleaning outcomes and material integrity'
}

NEW_CATEGORY_PERCENTAGES = {
    'laser_material_interaction': 47.3,
    'material_characteristics': 52.7
}


class FrontmatterUpdater:
    """Updates frontmatter YAML files from 3-category to 2-category structure."""
    
    def __init__(self, dry_run: bool = False, backup: bool = True):
        self.dry_run = dry_run
        self.backup = backup
        self.stats = {
            'total_files': 0,
            'processed': 0,
            'skipped': 0,
            'errors': 0,
            'backed_up': 0
        }
        self.error_log: List[str] = []
        
    def backup_file(self, file_path: Path) -> bool:
        """Create backup of original file."""
        if not self.backup:
            return True
            
        try:
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            backup_path = BACKUP_DIR / file_path.name
            shutil.copy2(file_path, backup_path)
            self.stats['backed_up'] += 1
            return True
        except Exception as e:
            self.error_log.append(f"Backup failed for {file_path.name}: {str(e)}")
            return False
    
    def transform_material_properties(self, material_props: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform materialProperties from 3-category to 2-category structure.
        
        Before:
        {
            'energy_coupling': {...},
            'structural_response': {...},
            'material_properties': {...}
        }
        
        After:
        {
            'laser_material_interaction': {...},
            'material_characteristics': {merged structural_response + material_properties}
        }
        """
        new_props = {}
        material_chars_props = {}
        
        for old_cat, data in material_props.items():
            new_cat = OLD_TO_NEW_CATEGORIES.get(old_cat, old_cat)
            
            if new_cat == 'laser_material_interaction':
                # Rename energy_coupling to laser_material_interaction
                new_props[new_cat] = {
                    'label': NEW_CATEGORY_LABELS[new_cat],
                    'properties': data.get('properties', {}),
                    'description': NEW_CATEGORY_DESCRIPTIONS[new_cat],
                    'percentage': NEW_CATEGORY_PERCENTAGES[new_cat]
                }
            elif new_cat == 'material_characteristics':
                # Merge structural_response and material_properties into material_characteristics
                if 'properties' not in material_chars_props:
                    material_chars_props['properties'] = {}
                material_chars_props['properties'].update(data.get('properties', {}))
        
        # Add merged material_characteristics
        if material_chars_props:
            new_props['material_characteristics'] = {
                'label': NEW_CATEGORY_LABELS['material_characteristics'],
                'properties': material_chars_props['properties'],
                'description': NEW_CATEGORY_DESCRIPTIONS['material_characteristics'],
                'percentage': NEW_CATEGORY_PERCENTAGES['material_characteristics']
            }
        
        return new_props
    
    def update_file(self, file_path: Path) -> bool:
        """Update a single frontmatter YAML file."""
        try:
            # Read existing file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Check if materialProperties exists and needs update
            if 'materialProperties' not in data:
                self.stats['skipped'] += 1
                return True
            
            mat_props = data['materialProperties']
            
            # Check if already 2-category (skip if so)
            if 'laser_material_interaction' in mat_props or 'material_characteristics' in mat_props:
                print(f"  ⏭️  {file_path.name} - Already 2-category structure")
                self.stats['skipped'] += 1
                return True
            
            # Check if 3-category structure exists
            has_3_cats = all(cat in mat_props for cat in ['energy_coupling', 'structural_response', 'material_properties'])
            if not has_3_cats:
                print(f"  ⚠️  {file_path.name} - Unexpected structure, skipping")
                self.stats['skipped'] += 1
                return True
            
            # Backup original
            if not self.dry_run:
                if not self.backup_file(file_path):
                    return False
            
            # Transform materialProperties
            new_mat_props = self.transform_material_properties(mat_props)
            data['materialProperties'] = new_mat_props
            
            # Write updated file
            if not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            print(f"  ✅ {file_path.name} - Transformed 3→2 categories")
            self.stats['processed'] += 1
            return True
            
        except Exception as e:
            error_msg = f"Error processing {file_path.name}: {str(e)}"
            self.error_log.append(error_msg)
            print(f"  ❌ {error_msg}")
            self.stats['errors'] += 1
            return False
    
    def update_all_files(self) -> Dict[str, Any]:
        """Update all frontmatter YAML files in the directory."""
        if not FRONTMATTER_DIR.exists():
            print(f"❌ Frontmatter directory not found: {FRONTMATTER_DIR}")
            return self.stats
        
        yaml_files = list(FRONTMATTER_DIR.glob("*.yaml"))
        self.stats['total_files'] = len(yaml_files)
        
        print(f"\n{'=' * 70}")
        print(f"Frontmatter Category Update: 3→2 Categories")
        print(f"{'=' * 70}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE UPDATE'}")
        print(f"Backup: {'Enabled' if self.backup else 'Disabled'}")
        print(f"Files: {self.stats['total_files']}")
        print(f"Directory: {FRONTMATTER_DIR}")
        if self.backup:
            print(f"Backup Dir: {BACKUP_DIR}")
        print(f"{'=' * 70}\n")
        
        for yaml_file in yaml_files:
            self.update_file(yaml_file)
        
        return self.stats
    
    def print_summary(self):
        """Print update summary."""
        print(f"\n{'=' * 70}")
        print(f"Update Summary")
        print(f"{'=' * 70}")
        print(f"Total Files:    {self.stats['total_files']}")
        print(f"Processed:      {self.stats['processed']} ✅")
        print(f"Skipped:        {self.stats['skipped']} ⏭️")
        print(f"Errors:         {self.stats['errors']} ❌")
        if self.backup:
            print(f"Backed Up:      {self.stats['backed_up']} 💾")
        print(f"{'=' * 70}")
        
        if self.error_log:
            print(f"\n❌ Error Log ({len(self.error_log)} errors):")
            for error in self.error_log:
                print(f"  - {error}")
        
        if self.dry_run:
            print("\n⚠️  DRY RUN - No files were modified")
        else:
            print(f"\n✅ Update complete - {self.stats['processed']} files transformed")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Update frontmatter YAML files from 3-category to 2-category structure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (preview changes)
  python3 scripts/tools/update_frontmatter_categories.py --dry-run
  
  # Update with backup
  python3 scripts/tools/update_frontmatter_categories.py
  
  # Update without backup
  python3 scripts/tools/update_frontmatter_categories.py --no-backup
  
  # Test on single file
  python3 scripts/tools/update_frontmatter_categories.py --test titanium-laser-cleaning.yaml
        """
    )
    
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying files')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backups')
    parser.add_argument('--test', metavar='FILE', help='Test on single file only')
    
    args = parser.parse_args()
    
    updater = FrontmatterUpdater(
        dry_run=args.dry_run,
        backup=not args.no_backup
    )
    
    if args.test:
        # Test mode - single file
        test_file = FRONTMATTER_DIR / args.test
        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            sys.exit(1)
        
        print(f"\n🧪 Testing on single file: {args.test}\n")
        updater.stats['total_files'] = 1
        updater.update_file(test_file)
        updater.print_summary()
    else:
        # Normal mode - all files
        updater.update_all_files()
        updater.print_summary()
    
    sys.exit(0 if updater.stats['errors'] == 0 else 1)


if __name__ == '__main__':
    main()
