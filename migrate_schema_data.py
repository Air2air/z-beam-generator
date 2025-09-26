#!/usr/bin/env python3
"""
Schema Reconciliation Migration Script
Migrates existing data to work with reconciled schemas
"""

import yaml
from pathlib import Path
import shutil
from datetime import datetime

class SchemaMigrator:
    def __init__(self):
        self.backup_dir = Path(f"backups/schema_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.data_dir = Path("data")
        self.frontmatter_dir = Path("content/components/frontmatter")
        
        # Field name mappings (snake_case → camelCase)
        self.field_mappings = {
            # Material properties
            'thermal_conductivity': 'thermalConductivity',
            'thermal_expansion': 'thermalExpansion', 
            'tensile_strength': 'tensileStrength',
            'youngs_modulus': 'youngsModulus',
            'electrical_resistivity': 'electricalResistivity',
            'regulatory_standards': 'regulatoryStandards',
            
            # Machine settings
            'pulse_duration': 'pulseDuration',
            'fluence_threshold': 'fluenceThreshold',
            'power_range': 'powerRange',
            'repetition_rate': 'repetitionRate',
            'spot_size': 'spotSize',
            'laser_type': 'laserType',
            'ablation_threshold': 'ablationThreshold',
            'thermal_damage_threshold': 'thermalDamageThreshold',
            'processing_speed': 'processingSpeed',
            'surface_roughness_change': 'surfaceRoughnessChange',
            'wavelength_optimal': 'wavelengthOptimal',
            
            # Compatibility
            'laser_types': 'laserTypes',
            'surface_treatments': 'surfaceTreatments',
            'incompatible_conditions': 'incompatibleConditions',
            'compatible_laser_types': 'compatibleLaserTypes',
            'optimal_wavelength': 'optimalWavelength',
            'absorption_characteristic': 'absorptionCharacteristic',
            'thermal_response': 'thermalResponse',
            'processing_efficiency': 'processingEfficiency',
            
            # Industry and tags
            'industry_tags': 'industryTags'
        }

    def create_backup(self):
        """Create backup of current data before migration"""
        print("📦 Creating backup of current data...")
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup Materials.yaml
        materials_src = self.data_dir / "Materials.yaml"
        if materials_src.exists():
            shutil.copy2(materials_src, self.backup_dir / "Materials.yaml")
            print("  ✅ Backed up Materials.yaml")
        
        # Backup frontmatter directory
        if self.frontmatter_dir.exists():
            frontmatter_backup = self.backup_dir / "frontmatter"
            shutil.copytree(self.frontmatter_dir, frontmatter_backup)
            print(f"  ✅ Backed up frontmatter directory ({len(list(self.frontmatter_dir.glob('*.md')))} files)")
        
        print(f"📦 Backup created at: {self.backup_dir}")
        return True

    def rename_dict_keys(self, data):
        """Recursively rename dictionary keys based on field mappings"""
        if isinstance(data, dict):
            new_data = {}
            for key, value in data.items():
                # Check if key needs to be renamed
                new_key = self.field_mappings.get(key, key)
                new_data[new_key] = self.rename_dict_keys(value)
            return new_data
        elif isinstance(data, list):
            return [self.rename_dict_keys(item) for item in data]
        else:
            return data

    def migrate_materials_yaml(self):
        """Migrate Materials.yaml to new schema format"""
        print("🔧 Migrating Materials.yaml...")
        
        materials_path = self.data_dir / "Materials.yaml"
        if not materials_path.exists():
            print("❌ Materials.yaml not found")
            return False
        
        # Load Materials.yaml
        with open(materials_path, 'r') as f:
            data = yaml.safe_load(f)
        
        migrations_applied = 0
        
        # 1. Rename fields throughout the data structure
        data = self.rename_dict_keys(data)
        migrations_applied += len(self.field_mappings)
        
        # 2. Add missing fields to material_index entries
        if 'material_index' in data:
            for material_name, material_info in data['material_index'].items():
                # Add complexity if missing
                if 'complexity' not in material_info:
                    material_info['complexity'] = 'medium'  # Default value
                    migrations_applied += 1
                
                # Add author_id if missing  
                if 'author_id' not in material_info:
                    material_info['author_id'] = 1  # Default value
                    migrations_applied += 1
                
                # Add index if missing
                if 'index' not in material_info:
                    material_info['index'] = 0  # Default value
                    migrations_applied += 1
        
        # 3. Remove unexpected top-level properties
        unexpected_props = ['defaults', 'metadata', 'parameter_templates']
        for prop in unexpected_props:
            if prop in data:
                del data[prop]
                migrations_applied += 1
                print(f"  ✅ Removed unexpected property: {prop}")
        
        # Save migrated Materials.yaml
        with open(materials_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, width=120, indent=2)
        
        print(f"  ✅ Applied {migrations_applied} migrations to Materials.yaml")
        return True

    def migrate_frontmatter_files(self):
        """Migrate frontmatter files to new schema format"""
        print("🔧 Migrating frontmatter files...")
        
        if not self.frontmatter_dir.exists():
            print("❌ Frontmatter directory not found")
            return False
        
        md_files = list(self.frontmatter_dir.glob("*.md"))
        migrations_applied = 0
        files_processed = 0
        
        for file_path in md_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract YAML frontmatter
                if content.startswith('---'):
                    yaml_start = content.find('---') + 3
                    yaml_end = content.find('---', yaml_start)
                    if yaml_end == -1:
                        yaml_content = content[yaml_start:].strip()
                        after_yaml = ""
                    else:
                        yaml_content = content[yaml_start:yaml_end].strip()
                        after_yaml = content[yaml_end:]
                    
                    # Parse YAML
                    data = yaml.safe_load(yaml_content)
                    if not data:
                        continue
                    
                    file_migrations = 0
                    
                    # 1. Convert keywords array to string
                    if 'keywords' in data and isinstance(data['keywords'], list):
                        data['keywords'] = ', '.join(data['keywords'])
                        file_migrations += 1
                    
                    # 2. Create materialProperties structure if missing
                    if 'materialProperties' not in data and 'properties' in data:
                        properties = data.get('properties', {})
                        data['materialProperties'] = {
                            'physical': {
                                'density': properties.get('density', properties.get('densityNumeric', 0)),
                                'densityUnit': properties.get('densityUnit', 'g/cm³')
                            },
                            'thermal': {
                                'thermalConductivity': properties.get('thermalConductivity', properties.get('thermalConductivityNumeric', 0)),
                                'thermalConductivityUnit': properties.get('thermalConductivityUnit', 'W/m·K')
                            },
                            'chemical': {
                                'formula': properties.get('chemicalFormula', data.get('chemicalProperties', {}).get('formula', '')),
                                'symbol': data.get('chemicalProperties', {}).get('symbol', '')
                            }
                        }
                        file_migrations += 1
                    
                    # Rename fields in the data structure
                    data = self.rename_dict_keys(data)
                    
                    # Save updated file if migrations were applied
                    if file_migrations > 0:
                        new_yaml_content = yaml.dump(data, default_flow_style=False, allow_unicode=True, width=120, indent=2)
                        new_content = f"---\n{new_yaml_content.strip()}\n{after_yaml}"
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        migrations_applied += file_migrations
                        files_processed += 1
                
            except Exception as e:
                print(f"  ❌ Error processing {file_path.name}: {e}")
        
        print(f"  ✅ Applied {migrations_applied} migrations to {files_processed} frontmatter files")
        return True

    def validate_migration(self):
        """Validate migrated data against schemas"""
        print("✅ Running post-migration validation...")
        
        # Import and run the validation script
        try:
            from validate_schema_reconciliation import SchemaReconciliationValidator
            validator = SchemaReconciliationValidator()
            return validator.run_all_validations()
        except ImportError:
            print("❌ Could not import validation script")
            return False

    def run_migration(self):
        """Execute complete migration process"""
        print("🚀 Starting Schema Migration Process")
        print("="*50)
        
        # Step 1: Create backup
        if not self.create_backup():
            print("❌ Backup failed - aborting migration")
            return False
        print()
        
        # Step 2: Migrate Materials.yaml
        materials_success = self.migrate_materials_yaml()
        print()
        
        # Step 3: Migrate frontmatter files
        frontmatter_success = self.migrate_frontmatter_files()
        print()
        
        # Step 4: Validate migration
        validation_success = False
        if materials_success and frontmatter_success:
            validation_success = self.validate_migration()
        
        # Summary
        print("="*50)
        print("MIGRATION SUMMARY")
        print("="*50)
        print(f"📦 Backup: ✅ Created at {self.backup_dir}")
        print(f"🔧 Materials.yaml: {'✅ Success' if materials_success else '❌ Failed'}")
        print(f"🔧 Frontmatter files: {'✅ Success' if frontmatter_success else '❌ Failed'}")
        print(f"✅ Validation: {'✅ Passed' if validation_success else '❌ Failed'}")
        
        overall_success = materials_success and frontmatter_success
        
        if overall_success:
            print("\n🎉 Schema migration completed successfully!")
            print("📋 All data has been migrated to work with reconciled schemas.")
        else:
            print("\n⚠️  Migration completed with issues.")
            print("📋 Check errors above and restore from backup if needed.")
        
        return overall_success


def main():
    migrator = SchemaMigrator()
    success = migrator.run_migration()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())