#!/usr/bin/env python3
"""
Migration Script: Subtitle → Material Description Field Restructuring
=====================================================================

This script performs a comprehensive migration across the entire Z-Beam Generator system:

CHANGES TO FRONTMATTER/MATERIALS/*.YAML (152 FILES):
1. Remove 'subtitle_metadata' field
2. Rename 'subtitle' → 'material_description'
3. Remove 'description' field (moves to settings)

CHANGES TO FRONTMATTER/SETTINGS/*.YAML (152 FILES):
1. Add 'settings_description' field (copied from materials 'description')

CHANGES TO DATA/MATERIALS/MATERIALS.YAML:
1. Apply same field transformations to source of truth

GENERATED FILES TO UPDATE:
- frontmatter/materials/*.yaml (132 main + 20 new)
- frontmatter/settings/*.yaml (132 main + 20 new)
- data/materials/Materials.yaml

Author: Z-Beam AI Assistant
Date: November 22, 2025
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class SubtitleMigration:
    """Handles the migration of subtitle fields to material_description."""
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize migration.
        
        Args:
            dry_run: If True, show changes without applying them
        """
        self.dry_run = dry_run
        self.stats = {
            'materials_processed': 0,
            'settings_processed': 0,
            'materials_updated': 0,
            'settings_updated': 0,
            'errors': []
        }
        
    def migrate_material_file(self, filepath: Path) -> bool:
        """
        Migrate a single material frontmatter file.
        
        Changes:
        1. Remove subtitle_metadata
        2. Rename subtitle → material_description
        3. Extract description for settings
        
        Returns:
            tuple: (success, description_value)
        """
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            
            changes_made = False
            description_for_settings = None
            
            # Extract description before removing it
            if 'description' in data:
                description_for_settings = data['description']
                del data['description']
                changes_made = True
            
            # Remove subtitle_metadata
            if 'subtitle_metadata' in data:
                del data['subtitle_metadata']
                changes_made = True
            
            # Rename subtitle → material_description
            if 'subtitle' in data:
                data['material_description'] = data['subtitle']
                del data['subtitle']
                changes_made = True
            
            if changes_made and not self.dry_run:
                with open(filepath, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                self.stats['materials_updated'] += 1
            
            self.stats['materials_processed'] += 1
            return (True, description_for_settings)
            
        except Exception as e:
            error_msg = f"Error processing {filepath}: {str(e)}"
            self.stats['errors'].append(error_msg)
            return (False, None)
    
    def migrate_settings_file(self, filepath: Path, description: str) -> bool:
        """
        Migrate a single settings frontmatter file.
        
        Changes:
        1. Add settings_description field
        
        Args:
            filepath: Path to settings file
            description: Description value from corresponding materials file
            
        Returns:
            bool: Success status
        """
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            
            changes_made = False
            
            # Add settings_description if we have description content
            if description:
                data['settings_description'] = description
                changes_made = True
            
            if changes_made and not self.dry_run:
                with open(filepath, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                self.stats['settings_updated'] += 1
            
            self.stats['settings_processed'] += 1
            return True
            
        except Exception as e:
            error_msg = f"Error processing {filepath}: {str(e)}"
            self.stats['errors'].append(error_msg)
            return False
    
    def migrate_materials_yaml(self, filepath: Path) -> bool:
        """
        Migrate the Materials.yaml source of truth.
        
        Changes:
        1. For each material: Remove subtitle_metadata
        2. For each material: Rename subtitle → material_description
        3. For each material: Move description to components.settings_description
        
        Returns:
            bool: Success status
        """
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            
            changes_made = False
            
            for material_name, material_data in data.items():
                if not isinstance(material_data, dict):
                    continue
                
                # Remove subtitle_metadata
                if 'subtitle_metadata' in material_data:
                    del material_data['subtitle_metadata']
                    changes_made = True
                
                # Rename subtitle → material_description
                if 'subtitle' in material_data:
                    material_data['material_description'] = material_data['subtitle']
                    del material_data['subtitle']
                    changes_made = True
                
                # Move description to components
                if 'description' in material_data:
                    if 'components' not in material_data:
                        material_data['components'] = {}
                    material_data['components']['settings_description'] = material_data['description']
                    del material_data['description']
                    changes_made = True
            
            if changes_made and not self.dry_run:
                with open(filepath, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            
            return True
            
        except Exception as e:
            error_msg = f"Error processing Materials.yaml: {str(e)}"
            self.stats['errors'].append(error_msg)
            return False
    
    def migrate_all(self) -> Dict[str, Any]:
        """
        Run complete migration across all files.
        
        Returns:
            dict: Migration statistics
        """
        print("🚀 Starting Subtitle → Material Description Migration")
        print("=" * 70)
        print()
        
        if self.dry_run:
            print("⚠️  DRY RUN MODE - No files will be modified")
            print()
        
        # Step 1: Migrate Materials.yaml
        print("📄 Step 1/3: Migrating Materials.yaml (source of truth)...")
        materials_yaml = project_root / "data" / "materials" / "Materials.yaml"
        if materials_yaml.exists():
            self.migrate_materials_yaml(materials_yaml)
            print(f"   ✅ Processed Materials.yaml")
        else:
            print(f"   ⚠️  Materials.yaml not found at {materials_yaml}")
        print()
        
        # Step 2: Migrate frontmatter/materials files
        print("📁 Step 2/3: Migrating frontmatter/materials files...")
        materials_dirs = [
            project_root / "frontmatter" / "materials",
            project_root / "frontmatter" / "materials-new"
        ]
        
        material_descriptions = {}  # Store for settings migration
        
        for materials_dir in materials_dirs:
            if not materials_dir.exists():
                continue
                
            for filepath in sorted(materials_dir.glob("*.yaml")):
                success, description = self.migrate_material_file(filepath)
                if success and description:
                    # Store description for corresponding settings file
                    material_descriptions[filepath.stem] = description
        
        print(f"   ✅ Processed {self.stats['materials_processed']} material files")
        print(f"   ✅ Updated {self.stats['materials_updated']} material files")
        print()
        
        # Step 3: Migrate frontmatter/settings files
        print("📁 Step 3/3: Migrating frontmatter/settings files...")
        settings_dirs = [
            project_root / "frontmatter" / "settings",
            project_root / "frontmatter" / "settings-new"
        ]
        
        for settings_dir in settings_dirs:
            if not settings_dir.exists():
                continue
                
            for filepath in sorted(settings_dir.glob("*.yaml")):
                # Match material file to settings file by stem
                material_stem = filepath.stem.replace('-settings', '-laser-cleaning')
                description = material_descriptions.get(material_stem)
                
                if description:
                    self.migrate_settings_file(filepath, description)
        
        print(f"   ✅ Processed {self.stats['settings_processed']} settings files")
        print(f"   ✅ Updated {self.stats['settings_updated']} settings files")
        print()
        
        # Print summary
        print("=" * 70)
        print("📊 MIGRATION SUMMARY")
        print("=" * 70)
        print(f"Materials Processed: {self.stats['materials_processed']}")
        print(f"Materials Updated: {self.stats['materials_updated']}")
        print(f"Settings Processed: {self.stats['settings_processed']}")
        print(f"Settings Updated: {self.stats['settings_updated']}")
        
        if self.stats['errors']:
            print(f"\n⚠️  Errors: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:10]:  # Show first 10
                print(f"   • {error}")
        else:
            print("\n✅ No errors encountered")
        
        print()
        
        if self.dry_run:
            print("ℹ️  This was a dry run. Run without --dry-run to apply changes.")
        else:
            print("✅ Migration complete!")
        
        print()
        
        return self.stats


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migrate subtitle fields to material_description across entire system'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    parser.add_argument(
        '--confirm',
        action='store_true',
        help='Skip confirmation prompt (required for non-dry-run)'
    )
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.confirm:
        print("\n⚠️  WARNING: This will modify 300+ files across the system!")
        print()
        print("Changes:")
        print("  • Materials: Remove subtitle_metadata, rename subtitle → material_description, remove description")
        print("  • Settings: Add settings_description")
        print("  • Materials.yaml: Apply same transformations")
        print()
        response = input("Are you sure you want to proceed? (yes/no): ")
        if response.lower() != 'yes':
            print("Migration cancelled.")
            return 1
    
    migration = SubtitleMigration(dry_run=args.dry_run)
    stats = migration.migrate_all()
    
    return 0 if not stats['errors'] else 1


if __name__ == '__main__':
    sys.exit(main())
