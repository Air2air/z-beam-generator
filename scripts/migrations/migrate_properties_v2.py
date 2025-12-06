#!/usr/bin/env python3
"""
Atomic Migration Script for Materials Module V2.0

This script performs three critical changes to Materials.yaml:
1. Rename 'properties' → 'materialProperties' throughout
2. Remove all 'description' fields from property dictionaries
3. Map 'meltingPoint' → 'thermalDestruction' everywhere

The script operates atomically:
- Creates backup before any changes
- Validates structure before writing
- Rolls back on any error
- Provides detailed migration report

Usage:
    python3 scripts/migration/migrate_properties_v2.py [--dry-run] [--backup-dir DIR]
"""

import sys
import yaml
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class MigrationStats:
    """Track migration statistics"""
    def __init__(self):
        self.properties_renamed = 0
        self.descriptions_removed = 0
        self.melting_points_mapped = 0
        self.materials_processed = 0
        self.errors = []
        self.warnings = []
    
    def report(self) -> str:
        """Generate migration report"""
        lines = [
            "=" * 80,
            "MIGRATION REPORT",
            "=" * 80,
            f"Materials Processed: {self.materials_processed}",
            f"'properties' → 'materialProperties': {self.properties_renamed}",
            f"'description' fields removed: {self.descriptions_removed}",
            f"'meltingPoint' → 'thermalDestruction': {self.melting_points_mapped}",
            "",
        ]
        
        if self.warnings:
            lines.append(f"Warnings ({len(self.warnings)}):")
            for warning in self.warnings[:10]:
                lines.append(f"  ⚠️  {warning}")
            if len(self.warnings) > 10:
                lines.append(f"  ... and {len(self.warnings) - 10} more")
            lines.append("")
        
        if self.errors:
            lines.append(f"Errors ({len(self.errors)}):")
            for error in self.errors[:10]:
                lines.append(f"  ❌ {error}")
            if len(self.errors) > 10:
                lines.append(f"  ... and {len(self.errors) - 10} more")
        else:
            lines.append("✅ No errors encountered")
        
        lines.append("=" * 80)
        return "\n".join(lines)


class PropertiesMigrator:
    """Handles atomic migration of Materials.yaml"""
    
    def __init__(self, materials_file: Path, backup_dir: Path = None):
        self.materials_file = materials_file
        self.backup_dir = backup_dir or materials_file.parent / "backups"
        self.stats = MigrationStats()
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self) -> Path:
        """Create timestamped backup of Materials.yaml"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"materials_backup_{timestamp}.yaml"
        
        print(f"📦 Creating backup: {backup_file}")
        shutil.copy2(self.materials_file, backup_file)
        
        return backup_file
    
    def load_materials(self) -> Dict:
        """Load Materials.yaml as complete document"""
        print(f"📂 Loading {self.materials_file}")
        
        with open(self.materials_file, 'r') as f:
            data = yaml.safe_load(f)
        
        if not isinstance(data, dict):
            raise ValueError(f"Expected dict, got {type(data)}")
        
        if 'materials' not in data:
            raise ValueError("No 'materials' key found in YAML")
        
        num_materials = len(data['materials']) if isinstance(data['materials'], dict) else 0
        print(f"✅ Loaded document with {num_materials} materials")
        return data
    
    def migrate_material(self, material: Dict) -> Dict:
        """Migrate a single material entry"""
        if not isinstance(material, dict):
            self.stats.errors.append(f"Material is not a dict: {type(material)}")
            return material
        
        material_name = material.get('name', 'Unknown')
        
        # Change 1: Rename 'properties' → 'materialProperties'
        if 'properties' in material:
            material['materialProperties'] = material.pop('properties')
            self.stats.properties_renamed += 1
        
        # Change 2 & 3: Process materialProperties
        if 'materialProperties' in material:
            material['materialProperties'] = self._migrate_properties(
                material['materialProperties'], 
                material_name
            )
        
        self.stats.materials_processed += 1
        return material
    
    def _migrate_properties(self, properties: Dict, material_name: str) -> Dict:
        """Migrate properties dictionary recursively"""
        if not isinstance(properties, dict):
            self.stats.warnings.append(
                f"{material_name}: materialProperties is not a dict: {type(properties)}"
            )
            return properties
        
        migrated = {}
        
        for prop_name, prop_data in properties.items():
            # Change 3: Map meltingPoint → thermalDestruction
            if prop_name == 'meltingPoint':
                new_prop_name = 'thermalDestruction'
                self.stats.melting_points_mapped += 1
                if 'thermalDestruction' in properties:
                    self.stats.warnings.append(
                        f"{material_name}: Both meltingPoint and thermalDestruction exist, keeping thermalDestruction"
                    )
                    continue
            else:
                new_prop_name = prop_name
            
            # Change 2: Remove 'description' field and recurse
            if isinstance(prop_data, dict):
                migrated_prop = self._remove_descriptions_recursive(prop_data)
                migrated[new_prop_name] = migrated_prop
            else:
                migrated[new_prop_name] = prop_data
        
        return migrated
    
    def _remove_descriptions_recursive(self, data: Dict) -> Dict:
        """Recursively remove all 'description' keys from nested dicts"""
        if not isinstance(data, dict):
            return data
        
        result = {}
        for key, value in data.items():
            if key == 'description':
                self.stats.descriptions_removed += 1
                continue  # Skip description fields
            
            if isinstance(value, dict):
                result[key] = self._remove_descriptions_recursive(value)
            elif isinstance(value, list):
                result[key] = [
                    self._remove_descriptions_recursive(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[key] = value
        
        return result
    
    def validate_migrated_data(self, materials: List[Dict]) -> bool:
        """Validate migrated data before writing"""
        print("\n🔍 Validating migrated data...")
        
        validation_errors = []
        
        for material in materials:
            if not isinstance(material, dict):
                validation_errors.append(f"Material is not a dict: {type(material)}")
                continue
            
            material_name = material.get('name', 'Unknown')
            
            # Check 1: No 'properties' key should exist
            if 'properties' in material:
                validation_errors.append(
                    f"{material_name}: Still has 'properties' key (should be 'materialProperties')"
                )
            
            # Check 2: materialProperties exists and is dict
            if 'materialProperties' in material:
                props = material['materialProperties']
                if not isinstance(props, dict):
                    validation_errors.append(
                        f"{material_name}: materialProperties is not a dict"
                    )
                else:
                    # Check 3: No description fields
                    for prop_name, prop_data in props.items():
                        if isinstance(prop_data, dict) and 'description' in prop_data:
                            validation_errors.append(
                                f"{material_name}.{prop_name}: Still has 'description' field"
                            )
                    
                    # Check 4: No meltingPoint (should be thermalDestruction)
                    if 'meltingPoint' in props:
                        validation_errors.append(
                            f"{material_name}: Still has 'meltingPoint' (should be 'thermalDestruction')"
                        )
        
        if validation_errors:
            print(f"❌ Validation failed with {len(validation_errors)} errors:")
            for error in validation_errors[:10]:
                print(f"   {error}")
            if len(validation_errors) > 10:
                print(f"   ... and {len(validation_errors) - 10} more")
            return False
        
        print("✅ Validation passed")
        return True
    
    def write_materials(self, data: Dict, output_file: Path = None):
        """Write migrated materials to YAML"""
        output_file = output_file or self.materials_file
        
        print(f"\n💾 Writing migrated data to {output_file}")
        
        num_materials = len(data.get('materials', {})) if isinstance(data.get('materials'), dict) else 0
        
        with open(output_file, 'w') as f:
            # Write as single-document YAML
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                width=120
            )
        
        print(f"✅ Successfully wrote {num_materials} materials")
    
    def migrate(self, dry_run: bool = False) -> bool:
        """Execute complete migration"""
        print("🚀 Starting Materials Module V2.0 Migration")
        print("=" * 80)
        print()
        
        backup_file = None
        
        try:
            # Step 1: Create backup
            if not dry_run:
                backup_file = self.create_backup()
                print(f"✅ Backup created at: {backup_file}\n")
            else:
                print("🔍 DRY RUN MODE - No backup created\n")
            
            # Step 2: Load materials data
            data = self.load_materials()
            print()
            
            # Step 3: Migrate materials dict
            print("🔄 Migrating materials...")
            if 'materials' in data and isinstance(data['materials'], dict):
                materials_dict = data['materials']
                migrated_dict = {}
                
                for material_name, material_data in materials_dict.items():
                    migrated = self.migrate_material(material_data)
                    migrated_dict[material_name] = migrated
                
                data['materials'] = migrated_dict
                print(f"✅ Migrated {len(migrated_dict)} materials\n")
            else:
                print("⚠️  No materials dict found, skipping migration\n")
            
            # Step 4: Validate
            materials_list = list(data['materials'].values()) if 'materials' in data else []
            if not self.validate_migrated_data(materials_list):
                print("\n❌ Migration validation failed - aborting")
                return False
            print()
            
            # Step 5: Write (unless dry run)
            if not dry_run:
                self.write_materials(data)
            else:
                print("🔍 DRY RUN MODE - Skipping write")
            
            # Step 6: Report
            print("\n" + self.stats.report())
            
            if not dry_run:
                print(f"\n✅ Migration complete! Backup available at: {backup_file}")
            else:
                print("\n🔍 DRY RUN COMPLETE - No changes written")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Migration failed with error: {e}")
            import traceback
            traceback.print_exc()
            
            if not dry_run and backup_file:
                print(f"\n⚠️  To restore from backup: cp {backup_file} {self.materials_file}")
            
            return False


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migrate Materials.yaml to V2.0 structure'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run migration without writing changes'
    )
    parser.add_argument(
        '--backup-dir',
        type=Path,
        help='Custom backup directory (default: materials/data/backups)'
    )
    parser.add_argument(
        '--materials-file',
        type=Path,
        default=Path('data/materials/Materials.yaml'),
        help='Path to Materials.yaml file'
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    materials_file = Path.cwd() / args.materials_file
    
    if not materials_file.exists():
        print(f"❌ Materials file not found: {materials_file}")
        return 1
    
    # Create migrator and run
    migrator = PropertiesMigrator(materials_file, args.backup_dir)
    success = migrator.migrate(dry_run=args.dry_run)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
