#!/usr/bin/env python3
"""
Synchronize frontmatter property updates back to Materials.yaml.

This script takes the properties we moved from preservedData to active sections
in frontmatter files and ensures they are permanently saved in Materials.yaml.
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
import shutil

# Root directory
ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTMATTER_DIR = ROOT_DIR / "content" / "frontmatter"
MATERIALS_FILE = ROOT_DIR / "data" / "Materials.yaml"
BACKUP_DIR = ROOT_DIR / "backups" / f"materials_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Materials that were updated in the frontmatter move operation
UPDATED_MATERIALS = {
    'cerium-laser-cleaning.yaml': 'Cerium',
    'dysprosium-laser-cleaning.yaml': 'Dysprosium', 
    'europium-laser-cleaning.yaml': 'Europium',
    'gallium-laser-cleaning.yaml': 'Gallium',
    'lanthanum-laser-cleaning.yaml': 'Lanthanum',
    'neodymium-laser-cleaning.yaml': 'Neodymium',
    'praseodymium-laser-cleaning.yaml': 'Praseodymium',
    'terbium-laser-cleaning.yaml': 'Terbium',
    'tool-steel-laser-cleaning.yaml': 'Tool Steel',
    'yttrium-laser-cleaning.yaml': 'Yttrium'
}


class MaterialsYamlSynchronizer:
    """Synchronizes frontmatter property updates back to Materials.yaml."""
    
    def __init__(self, dry_run: bool = False, backup: bool = True):
        self.dry_run = dry_run
        self.backup = backup
        self.stats = {
            'materials_processed': 0,
            'materials_updated': 0,
            'properties_added': 0,
            'properties_updated': 0,
            'errors': 0
        }
        self.changes_log: List[str] = []
        
    def backup_materials_file(self) -> bool:
        """Create backup of Materials.yaml."""
        if not self.backup:
            return True
            
        try:
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            backup_path = BACKUP_DIR / "Materials.yaml"
            shutil.copy2(MATERIALS_FILE, backup_path)
            return True
        except Exception as e:
            self.changes_log.append(f"❌ Backup failed: {str(e)}")
            return False
    
    def find_material_in_materials_yaml(self, target_name: str, materials_section: Dict) -> Optional[str]:
        """Find a material in Materials.yaml with flexible name matching."""
        # Try various name formats
        possible_names = [
            target_name,
            target_name.replace('-', ' '),
            target_name.replace('-', ''),
            target_name.lower(),
            target_name.upper(),
            target_name.title()
        ]
        
        for possible_name in possible_names:
            if possible_name in materials_section:
                return possible_name
        
        return None
    
    def load_frontmatter_properties(self, frontmatter_file: str) -> Dict:
        """Load materialProperties from a frontmatter file."""
        frontmatter_path = FRONTMATTER_DIR / frontmatter_file
        
        if not frontmatter_path.exists():
            raise FileNotFoundError(f"Frontmatter file not found: {frontmatter_file}")
        
        with open(frontmatter_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return data.get('materialProperties', {})
    
    def merge_properties(self, materials_props: Dict, frontmatter_props: Dict, material_name: str) -> Tuple[Dict, List[str]]:
        """Merge frontmatter properties into Materials.yaml format."""
        changes = []
        merged_props = materials_props.copy() if materials_props else {}
        
        for category_name, category_data in frontmatter_props.items():
            if not isinstance(category_data, dict):
                continue
            
            # Ensure category exists in merged props
            if category_name not in merged_props:
                merged_props[category_name] = {
                    'label': category_data.get('label', category_name.replace('_', ' ').title()),
                    'description': category_data.get('description', f'{category_name} properties')
                }
                changes.append(f"  Created category: {category_name}")
            
            # Process properties in this category
            for prop_name, prop_data in category_data.items():
                if prop_name in ['label', 'description'] or not isinstance(prop_data, dict):
                    continue
                
                # Check if property already exists in Materials.yaml
                existing_prop = None
                if category_name in materials_props and prop_name in materials_props[category_name]:
                    existing_prop = materials_props[category_name][prop_name]
                
                if existing_prop:
                    # Update existing property - merge data intelligently
                    updated_prop = existing_prop.copy()
                    
                    # Add any new fields from frontmatter
                    for field, value in prop_data.items():
                        if field not in updated_prop or updated_prop[field] is None:
                            updated_prop[field] = value
                    
                    merged_props[category_name][prop_name] = updated_prop
                    changes.append(f"  Updated {category_name}.{prop_name}")
                    self.stats['properties_updated'] += 1
                else:
                    # Add new property
                    merged_props[category_name][prop_name] = prop_data
                    changes.append(f"  Added {category_name}.{prop_name}")
                    self.stats['properties_added'] += 1
        
        return merged_props, changes
    
    def synchronize_material(self, frontmatter_file: str, material_name: str, materials_data: Dict) -> List[str]:
        """Synchronize one material's properties from frontmatter to Materials.yaml."""
        changes = []
        
        try:
            # Load frontmatter properties
            frontmatter_props = self.load_frontmatter_properties(frontmatter_file)
            
            if not frontmatter_props:
                changes.append(f"  No materialProperties found in {frontmatter_file}")
                return changes
            
            # Find material in Materials.yaml
            materials_section = materials_data.get('materials', {})
            found_name = self.find_material_in_materials_yaml(material_name, materials_section)
            
            if not found_name:
                changes.append(f"  Material '{material_name}' not found in Materials.yaml")
                return changes
            
            # Get existing properties
            existing_material = materials_section[found_name]
            existing_props = existing_material.get('materialProperties', {})
            
            # Merge properties
            merged_props, merge_changes = self.merge_properties(existing_props, frontmatter_props, material_name)
            
            # Update Materials.yaml data
            materials_data['materials'][found_name]['materialProperties'] = merged_props
            
            changes.extend(merge_changes)
            self.stats['materials_updated'] += 1
            
        except Exception as e:
            error_msg = f"Error synchronizing {material_name}: {str(e)}"
            changes.append(f"  ❌ {error_msg}")
            self.changes_log.append(error_msg)
            self.stats['errors'] += 1
        
        return changes
    
    def synchronize_all_materials(self) -> Dict:
        """Synchronize all updated materials from frontmatter to Materials.yaml."""
        
        print(f"\n{'=' * 70}")
        print(f"Materials.yaml Synchronization")
        print(f"{'=' * 70}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE SYNCHRONIZATION'}")
        print(f"Backup: {'Enabled' if self.backup else 'Disabled'}")
        print(f"Materials to sync: {len(UPDATED_MATERIALS)}")
        if self.backup:
            print(f"Backup Dir: {BACKUP_DIR}")
        print(f"{'=' * 70}\n")
        
        # Load Materials.yaml
        try:
            with open(MATERIALS_FILE, 'r', encoding='utf-8') as f:
                materials_data = yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Failed to load Materials.yaml: {e}")
            return self.stats
        
        # Backup if not dry run
        if not self.dry_run:
            if not self.backup_materials_file():
                print("❌ Backup failed, aborting synchronization")
                return self.stats
        
        # Process each material
        for frontmatter_file, material_name in UPDATED_MATERIALS.items():
            print(f"🔄 Synchronizing {material_name} ({frontmatter_file})")
            
            changes = self.synchronize_material(frontmatter_file, material_name, materials_data)
            
            if changes:
                for change in changes:
                    print(change)
            else:
                print("  No changes needed")
            
            self.stats['materials_processed'] += 1
        
        # Save updated Materials.yaml
        if not self.dry_run and self.stats['materials_updated'] > 0:
            try:
                # Add sync metadata
                if 'metadata' not in materials_data:
                    materials_data['metadata'] = {}
                
                materials_data['metadata']['last_frontmatter_sync'] = datetime.now().isoformat()
                materials_data['metadata']['frontmatter_sync_materials'] = list(UPDATED_MATERIALS.values())
                materials_data['metadata']['sync_stats'] = {
                    'properties_added': self.stats['properties_added'],
                    'properties_updated': self.stats['properties_updated'],
                    'materials_updated': self.stats['materials_updated']
                }
                
                with open(MATERIALS_FILE, 'w', encoding='utf-8') as f:
                    yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                
                print(f"\n✅ Materials.yaml updated successfully")
                
            except Exception as e:
                error_msg = f"Failed to save Materials.yaml: {e}"
                print(f"❌ {error_msg}")
                self.changes_log.append(error_msg)
                self.stats['errors'] += 1
        
        return self.stats
    
    def print_summary(self):
        """Print synchronization summary."""
        print(f"\n{'=' * 70}")
        print(f"Synchronization Summary")
        print(f"{'=' * 70}")
        print(f"Materials Processed:    {self.stats['materials_processed']}")
        print(f"Materials Updated:      {self.stats['materials_updated']} ✅")
        print(f"Properties Added:       {self.stats['properties_added']} 🆕")
        print(f"Properties Updated:     {self.stats['properties_updated']} 🔄")
        print(f"Errors:                 {self.stats['errors']} ❌")
        print(f"{'=' * 70}")
        
        if self.changes_log:
            print(f"\n⚠️  Issues Log ({len(self.changes_log)} items):")
            for log in self.changes_log[:10]:
                print(f"  {log}")
            if len(self.changes_log) > 10:
                print(f"  ... and {len(self.changes_log) - 10} more")
        
        if self.dry_run:
            print(f"\n⚠️  DRY RUN - Materials.yaml was not modified")
        else:
            if self.stats['materials_updated'] > 0:
                print(f"\n✅ Synchronization complete - {self.stats['materials_updated']} materials updated")
                print(f"🔄 Total property changes: {self.stats['properties_added'] + self.stats['properties_updated']}")
            else:
                print(f"\n📋 No materials needed synchronization")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Synchronize frontmatter property updates back to Materials.yaml',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (preview changes)
  python3 scripts/tools/sync_materials_yaml.py --dry-run
  
  # Synchronize with backup
  python3 scripts/tools/sync_materials_yaml.py
  
  # Synchronize without backup
  python3 scripts/tools/sync_materials_yaml.py --no-backup
        """
    )
    
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying Materials.yaml')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backups')
    
    args = parser.parse_args()
    
    synchronizer = MaterialsYamlSynchronizer(
        dry_run=args.dry_run,
        backup=not args.no_backup
    )
    
    synchronizer.synchronize_all_materials()
    synchronizer.print_summary()
    
    sys.exit(0 if synchronizer.stats['errors'] == 0 else 1)


if __name__ == '__main__':
    main()