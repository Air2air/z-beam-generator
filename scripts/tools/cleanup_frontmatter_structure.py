#!/usr/bin/env python3
"""
Clean up frontmatter structure after 2-category consolidation.

Actions:
1. Remove excess machineSettings keys (fluenceThreshold, energyDensity, dwellTime)
2. Remove unexpected properties from materialProperties
3. Verify 2-category structure
4. Report properties with null ranges (informational only)
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
import shutil

# Root directory
ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTMATTER_DIR = ROOT_DIR / "content" / "components" / "frontmatter"
BACKUP_DIR = ROOT_DIR / "backups" / f"frontmatter_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Valid keys
VALID_MACHINE_KEYS = {
    'powerRange', 'wavelength', 'spotSize', 'repetitionRate',
    'pulseWidth', 'scanSpeed', 'fluence', 'overlapRatio', 'passCount'
}

VALID_MATERIAL_CATEGORIES = {
    'laser_material_interaction', 'material_characteristics'
}

# Properties that should be removed if found
PROPERTIES_TO_REMOVE = {
    'vaporizationTemperature',  # Not in official 55-property list
    'meltingPoint',  # Replaced by thermalDegradationPoint
}


class FrontmatterCleaner:
    """Cleans frontmatter YAML files to match 2-category structure."""
    
    def __init__(self, dry_run: bool = False, backup: bool = True):
        self.dry_run = dry_run
        self.backup = backup
        self.stats = {
            'total_files': 0,
            'processed': 0,
            'skipped': 0,
            'errors': 0,
            'backed_up': 0,
            'machine_keys_removed': 0,
            'properties_removed': 0,
            'null_range_properties': 0
        }
        self.changes_log: List[str] = []
        self.null_range_report: Dict[str, int] = {}
        
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
            self.changes_log.append(f"❌ Backup failed for {file_path.name}: {str(e)}")
            return False
    
    def cleanup_machine_settings(self, data: Dict) -> List[str]:
        """Remove excess machineSettings keys."""
        changes = []
        
        if 'machineSettings' not in data:
            return changes
        
        excess_keys = set(data['machineSettings'].keys()) - VALID_MACHINE_KEYS
        for key in excess_keys:
            del data['machineSettings'][key]
            changes.append(f"  Removed machineSettings.{key}")
            self.stats['machine_keys_removed'] += 1
        
        return changes
    
    def cleanup_material_properties(self, data: Dict) -> List[str]:
        """Remove unexpected properties from materialProperties."""
        changes = []
        
        if 'materialProperties' not in data:
            return changes
        
        for cat_name, cat_data in data['materialProperties'].items():
            if not isinstance(cat_data, dict) or 'properties' not in cat_data:
                continue
            
            # Remove unexpected properties
            props_to_remove = []
            for prop_name in cat_data['properties'].keys():
                if prop_name in PROPERTIES_TO_REMOVE:
                    props_to_remove.append(prop_name)
            
            for prop_name in props_to_remove:
                del cat_data['properties'][prop_name]
                changes.append(f"  Removed {cat_name}.properties.{prop_name}")
                self.stats['properties_removed'] += 1
        
        return changes
    
    def check_null_ranges(self, data: Dict, filename: str):
        """Check for properties with null min/max (informational only)."""
        if 'materialProperties' not in data:
            return
        
        for cat_name, cat_data in data['materialProperties'].items():
            if not isinstance(cat_data, dict) or 'properties' not in cat_data:
                continue
            
            for prop_name, prop_data in cat_data['properties'].items():
                if not isinstance(prop_data, dict):
                    continue
                
                min_val = prop_data.get('min')
                max_val = prop_data.get('max')
                
                if min_val is None or max_val is None:
                    if prop_name not in self.null_range_report:
                        self.null_range_report[prop_name] = 0
                    self.null_range_report[prop_name] += 1
    
    def verify_structure(self, data: Dict) -> List[str]:
        """Verify the 2-category structure is correct."""
        issues = []
        
        # Check materialProperties has exactly 2 categories
        if 'materialProperties' in data:
            cats = set(data['materialProperties'].keys())
            if cats != VALID_MATERIAL_CATEGORIES:
                issues.append(f"  ⚠️  Unexpected categories: {cats}")
        
        # Check machineSettings has exactly 9 keys
        if 'machineSettings' in data:
            key_count = len(data['machineSettings'])
            if key_count != 9:
                issues.append(f"  ⚠️  machineSettings has {key_count} keys (expected 9)")
        
        return issues
    
    def cleanup_file(self, file_path: Path) -> bool:
        """Clean up a single frontmatter YAML file."""
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Track changes
            file_changes = []
            
            # Clean up machine settings
            machine_changes = self.cleanup_machine_settings(data)
            file_changes.extend(machine_changes)
            
            # Clean up material properties
            property_changes = self.cleanup_material_properties(data)
            file_changes.extend(property_changes)
            
            # Check for null ranges (informational)
            self.check_null_ranges(data, file_path.name)
            
            # Verify structure
            structure_issues = self.verify_structure(data)
            
            # If changes were made
            if file_changes:
                # Backup original
                if not self.dry_run:
                    if not self.backup_file(file_path):
                        return False
                
                # Write updated file
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                
                print(f"✅ {file_path.name}")
                for change in file_changes:
                    print(change)
                
                self.stats['processed'] += 1
            else:
                if structure_issues:
                    print(f"⚠️  {file_path.name}")
                    for issue in structure_issues:
                        print(issue)
                    self.stats['processed'] += 1
                else:
                    self.stats['skipped'] += 1
            
            return True
            
        except Exception as e:
            error_msg = f"Error processing {file_path.name}: {str(e)}"
            self.changes_log.append(f"❌ {error_msg}")
            print(f"❌ {error_msg}")
            self.stats['errors'] += 1
            return False
    
    def cleanup_all_files(self) -> Dict:
        """Clean up all frontmatter YAML files."""
        if not FRONTMATTER_DIR.exists():
            print(f"❌ Frontmatter directory not found: {FRONTMATTER_DIR}")
            return self.stats
        
        yaml_files = sorted(list(FRONTMATTER_DIR.glob("*.yaml")))
        self.stats['total_files'] = len(yaml_files)
        
        print(f"\n{'=' * 70}")
        print(f"Frontmatter Structure Cleanup")
        print(f"{'=' * 70}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE CLEANUP'}")
        print(f"Backup: {'Enabled' if self.backup else 'Disabled'}")
        print(f"Files: {self.stats['total_files']}")
        print(f"Directory: {FRONTMATTER_DIR}")
        if self.backup:
            print(f"Backup Dir: {BACKUP_DIR}")
        print(f"{'=' * 70}\n")
        
        for yaml_file in yaml_files:
            self.cleanup_file(yaml_file)
        
        return self.stats
    
    def print_summary(self):
        """Print cleanup summary."""
        print(f"\n{'=' * 70}")
        print(f"Cleanup Summary")
        print(f"{'=' * 70}")
        print(f"Total Files:           {self.stats['total_files']}")
        print(f"Cleaned:               {self.stats['processed']} ✅")
        print(f"Skipped (no changes):  {self.stats['skipped']} ⏭️")
        print(f"Errors:                {self.stats['errors']} ❌")
        if self.backup:
            print(f"Backed Up:             {self.stats['backed_up']} 💾")
        print(f"\nChanges Made:")
        print(f"  Machine Keys Removed:  {self.stats['machine_keys_removed']}")
        print(f"  Properties Removed:    {self.stats['properties_removed']}")
        print(f"{'=' * 70}")
        
        if self.null_range_report:
            print(f"\n📊 Properties with NULL min/max (informational):")
            print(f"{'=' * 70}")
            for prop, count in sorted(self.null_range_report.items(), key=lambda x: -x[1]):
                print(f"  {prop}: {count} files")
            print(f"\nNote: NULL ranges are valid for properties without category ranges.")
        
        if self.changes_log:
            print(f"\n⚠️  Issues Log ({len(self.changes_log)} items):")
            for log in self.changes_log[:10]:
                print(f"  {log}")
            if len(self.changes_log) > 10:
                print(f"  ... and {len(self.changes_log) - 10} more")
        
        if self.dry_run:
            print(f"\n⚠️  DRY RUN - No files were modified")
        else:
            print(f"\n✅ Cleanup complete - {self.stats['processed']} files processed")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Clean up frontmatter structure after 2-category consolidation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (preview changes)
  python3 scripts/tools/cleanup_frontmatter_structure.py --dry-run
  
  # Clean up with backup
  python3 scripts/tools/cleanup_frontmatter_structure.py
  
  # Clean up without backup
  python3 scripts/tools/cleanup_frontmatter_structure.py --no-backup
        """
    )
    
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying files')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backups')
    
    args = parser.parse_args()
    
    cleaner = FrontmatterCleaner(
        dry_run=args.dry_run,
        backup=not args.no_backup
    )
    
    cleaner.cleanup_all_files()
    cleaner.print_summary()
    
    sys.exit(0 if cleaner.stats['errors'] == 0 else 1)


if __name__ == '__main__':
    main()
