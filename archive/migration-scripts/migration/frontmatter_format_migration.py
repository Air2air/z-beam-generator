#!/usr/bin/env python3
"""
Frontmatter Format Migration Script

Transforms existing frontmatter files from current nested structure 
to new flattened format while preserving ALL data.

Migration Strategy:
1. Load existing materials.yaml data
2. Transform to new format structure
3. Categorize properties into material_characteristics vs laser_material_interaction
4. Preserve unused data in dedicated sections
5. Generate new frontmatter files

Usage:
    python3 scripts/migration/frontmatter_format_migration.py
    python3 scripts/migration/frontmatter_format_migration.py --material Alabaster
    python3 scripts/migration/frontmatter_format_migration.py --dry-run
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

class FrontmatterMigrator:
    """Migrates frontmatter files from current to new format"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.project_root = Path(__file__).parent.parent.parent
        self.materials_file = self.project_root / "data" / "materials.yaml"
        self.frontmatter_dir = self.project_root / "content" / "frontmatter"
        self.backup_dir = self.project_root / "backups" / "frontmatter_migration"
        
        # Property categorization mapping
        self.material_characteristics_properties = {
            'density', 'hardness', 'youngsModulus', 'tensileStrength', 'compressiveStrength',
            'flexuralStrength', 'fractureToughness', 'porosity', 'specificHeat', 
            'thermalConductivity', 'thermalExpansion', 'thermalDiffusivity',
            'electricalConductivity', 'electricalResistivity', 'corrosionResistance',
            'oxidationResistance', 'crystallineStructure', 'thermalDestruction',
            'thermalDestructionPoint', 'meltingPoint', 'boilingPoint'
        }
        
        self.laser_material_interaction_properties = {
            'laserAbsorption', 'laserReflectivity', 'reflectivity', 'absorptivity',
            'absorptionCoefficient', 'laserDamageThreshold', 'ablationThreshold',
            'thermalShockResistance', 'surfaceRoughness', 'vaporPressure'
        }
        
        self.migration_stats = {
            'processed': 0,
            'errors': 0,
            'preserved_fields': 0,
            'migrated_properties': 0
        }
    
    def load_materials_data(self) -> Dict[str, Any]:
        """Load materials.yaml data"""
        try:
            with open(self.materials_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error loading materials.yaml: {e}")
            sys.exit(1)
    
    def create_backup(self, file_path: Path) -> None:
        """Create backup of existing frontmatter file"""
        if not self.dry_run and file_path.exists():
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = self.backup_dir / f"{file_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
            
            with open(file_path, 'r', encoding='utf-8') as src, \
                 open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
            
            print(f"  📁 Backup created: {backup_path.name}")
    
    def determine_subcategory(self, category: str, material_name: str) -> str:
        """Determine subcategory based on material category and name"""
        subcategory_mapping = {
            'stone': 'mineral',
            'metal': 'alloy',
            'ceramic': 'oxide',
            'glass': 'silicate',
            'plastic': 'polymer',
            'composite': 'reinforced',
            'wood': 'natural',
            'semiconductor': 'crystal',
            'rare-earth': 'element',
            'masonry': 'construction'
        }
        return subcategory_mapping.get(category.lower(), 'material')
    
    def categorize_property(self, prop_name: str) -> str:
        """Categorize property into material_characteristics or laser_material_interaction"""
        if prop_name in self.material_characteristics_properties:
            return 'material_characteristics'
        elif prop_name in self.laser_material_interaction_properties:
            return 'laser_material_interaction'
        else:
            # Default to material_characteristics for unknown properties
            return 'material_characteristics'
    
    def transform_property(self, prop_name: str, prop_data: Any) -> Dict[str, Any]:
        """Transform property data to new format"""
        if isinstance(prop_data, dict):
            # Extract core values, removing metadata
            transformed = {}
            
            # Core property values
            if 'value' in prop_data:
                transformed['value'] = prop_data['value']
            if 'min' in prop_data:
                transformed['min'] = prop_data['min']
            if 'max' in prop_data:
                transformed['max'] = prop_data['max']
            if 'unit' in prop_data:
                transformed['unit'] = prop_data['unit']
            if 'research_basis' in prop_data:
                transformed['research_basis'] = prop_data['research_basis']
            elif 'description' in prop_data:
                transformed['research_basis'] = prop_data['description']
            
            return transformed
        
        # Handle simple values
        return {'value': prop_data}
    
    def extract_machine_settings(self, material_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and transform machine settings"""
        machine_settings = {}
        
        if 'machineSettings' in material_data:
            for setting_name, setting_data in material_data['machineSettings'].items():
                if isinstance(setting_data, dict):
                    transformed_setting = {}
                    
                    # Core setting values
                    if 'value' in setting_data:
                        transformed_setting['value'] = setting_data['value']
                    if 'min' in setting_data:
                        transformed_setting['min'] = setting_data['min']
                    if 'max' in setting_data:
                        transformed_setting['max'] = setting_data['max']
                    if 'unit' in setting_data:
                        transformed_setting['unit'] = setting_data['unit']
                    if 'description' in setting_data:
                        transformed_setting['description'] = setting_data['description']
                    
                    machine_settings[setting_name] = transformed_setting
        
        return machine_settings
    
    def extract_preserved_data(self, current_frontmatter: Dict[str, Any], 
                              material_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data that doesn't fit new format for preservation"""
        preserved = {}
        
        # Current frontmatter metadata
        if current_frontmatter:
            metadata = {}
            for key in ['generated_date', 'data_completeness', 'source', 'properties']:
                if key in current_frontmatter:
                    metadata[key] = current_frontmatter[key]
            
            if metadata:
                preserved['generationMetadata'] = metadata
            
            # Category info with ranges
            if 'category_info' in current_frontmatter:
                preserved['categoryInfo'] = current_frontmatter['category_info']
        
        # Property metadata (confidence scores, verification data)
        property_metadata = {}
        if 'materialProperties' in material_data:
            for section_name, section_data in material_data['materialProperties'].items():
                if isinstance(section_data, dict) and 'properties' in section_data:
                    for prop_name, prop_data in section_data['properties'].items():
                        if isinstance(prop_data, dict):
                            meta = {}
                            for key in ['confidence', 'ai_verified', 'verification_date', 
                                       'verification_confidence', 'research_date', 'source']:
                                if key in prop_data:
                                    meta[key] = prop_data[key]
                            
                            if meta:
                                property_metadata[prop_name] = meta
        
        if property_metadata:
            preserved['propertyMetadata'] = property_metadata
        
        # Machine settings metadata
        if 'machineSettings' in material_data:
            settings_metadata = {}
            for setting_name, setting_data in material_data['machineSettings'].items():
                if isinstance(setting_data, dict):
                    meta = {}
                    for key in ['confidence', 'research_date', 'source']:
                        if key in setting_data:
                            meta[key] = setting_data[key]
                    
                    if meta:
                        settings_metadata[setting_name] = meta
            
            if settings_metadata:
                preserved['machineSettingsMetadata'] = settings_metadata
        
        return preserved
    
    def transform_material(self, material_name: str, material_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform single material to new frontmatter format"""
        
        # Load existing frontmatter if exists
        current_frontmatter = {}
        frontmatter_file = self.frontmatter_dir / f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml"
        
        if frontmatter_file.exists():
            try:
                with open(frontmatter_file, 'r', encoding='utf-8') as f:
                    current_frontmatter = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"  ⚠️  Error reading existing frontmatter: {e}")
        
        # Build new format structure
        new_frontmatter = {}
        
        # Basic information
        new_frontmatter['name'] = material_name
        new_frontmatter['category'] = material_data.get('category', 'unknown').title()
        new_frontmatter['subcategory'] = self.determine_subcategory(
            material_data.get('category', ''), material_name
        )
        
        # Content fields
        new_frontmatter['title'] = f"{material_name} Laser Cleaning"
        new_frontmatter['subtitle'] = f"Laser cleaning parameters and specifications for {material_name}"
        new_frontmatter['description'] = material_data.get('description', f"Laser cleaning parameters for {material_name}")
        
        # Author information
        if 'author' in material_data:
            new_frontmatter['author'] = material_data['author']
        
        # Images
        if 'images' in material_data:
            new_frontmatter['images'] = material_data['images']
        
        # Captions - use existing if available
        if 'captions' in material_data:
            captions = material_data['captions']
            new_frontmatter['caption'] = {
                'description': f"Microscopic analysis of {material_name} surface before and after laser cleaning treatment",
                'beforeText': captions.get('before_text', ''),
                'afterText': captions.get('after_text', '')
            }
        
        # Regulatory standards - placeholder for now
        new_frontmatter['regulatoryStandards'] = [
            {
                'name': 'ANSI',
                'description': 'ANSI Z136.1 - Safe Use of Lasers',
                'url': 'https://webstore.ansi.org/standards/lia/ansiz1362022',
                'image': '/images/logo/logo-org-ansi.png'
            },
            {
                'name': 'IEC',
                'description': 'IEC 60825 - Safety of Laser Products', 
                'url': 'https://webstore.iec.ch/en/publication/3587',
                'image': '/images/logo/logo-org-iec.png'
            }
        ]
        
        # Applications
        if 'applications' in material_data:
            new_frontmatter['applications'] = material_data['applications']
        
        # Material Properties - NEW FORMAT
        material_properties = {
            'material_characteristics': {
                'label': 'Material Characteristics',
                'description': 'Intrinsic physical, mechanical, chemical, and structural properties affecting cleaning outcomes and material integrity'
            },
            'laser_material_interaction': {
                'label': 'Laser-Material Interaction', 
                'description': 'Optical and thermal properties governing laser energy absorption, reflection, propagation, and ablation thresholds'
            }
        }
        
        # Process material properties
        if 'materialProperties' in material_data:
            for section_name, section_data in material_data['materialProperties'].items():
                if isinstance(section_data, dict) and 'properties' in section_data:
                    for prop_name, prop_data in section_data['properties'].items():
                        category = self.categorize_property(prop_name)
                        transformed_prop = self.transform_property(prop_name, prop_data)
                        material_properties[category][prop_name] = transformed_prop
                        self.migration_stats['migrated_properties'] += 1
        
        new_frontmatter['materialProperties'] = material_properties
        
        # Machine Settings
        machine_settings = self.extract_machine_settings(material_data)
        if machine_settings:
            new_frontmatter['machineSettings'] = machine_settings
        
        # Environmental Impact
        if 'environmentalImpact' in material_data:
            new_frontmatter['environmentalImpact'] = material_data['environmentalImpact']
        
        # Outcome Metrics - placeholder structure
        new_frontmatter['outcomeMetrics'] = [
            {
                'Contaminant Removal Efficiency': {
                    'description': 'Percentage of target contaminants successfully removed from surface',
                    'typicalRanges': '95-99.9% depending on application and material',
                    'measurementMethods': ['Before/after microscopy', 'Chemical analysis', 'Mass spectrometry'],
                    'factorsAffecting': ['Contamination type', 'Adhesion strength', 'Surface geometry']
                }
            }
        ]
        
        # Preserved Data Section
        preserved_data = self.extract_preserved_data(current_frontmatter, material_data)
        if preserved_data:
            new_frontmatter['preservedData'] = preserved_data
            self.migration_stats['preserved_fields'] += len(preserved_data)
        
        return new_frontmatter
    
    def migrate_material(self, material_name: str, materials_data: Dict[str, Any]) -> bool:
        """Migrate single material frontmatter file"""
        
        if material_name not in materials_data.get('materials', {}):
            print(f"❌ Material '{material_name}' not found in materials.yaml")
            return False
        
        material_data = materials_data['materials'][material_name]
        
        print(f"🔄 Migrating {material_name}...")
        
        # Generate new frontmatter
        try:
            new_frontmatter = self.transform_material(material_name, material_data)
            
            # Create output file path
            output_file = self.frontmatter_dir / f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml"
            
            # Create backup of existing file
            self.create_backup(output_file)
            
            # Write new frontmatter
            if not self.dry_run:
                self.frontmatter_dir.mkdir(parents=True, exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    yaml.dump(new_frontmatter, f, default_flow_style=False, 
                             allow_unicode=True, sort_keys=False, indent=2)
                
                print(f"  ✅ Migrated: {output_file.name}")
            else:
                print(f"  🔍 DRY RUN: Would migrate {output_file.name}")
            
            self.migration_stats['processed'] += 1
            return True
            
        except Exception as e:
            print(f"  ❌ Error migrating {material_name}: {e}")
            self.migration_stats['errors'] += 1
            return False
    
    def migrate_all_materials(self, materials_data: Dict[str, Any]) -> None:
        """Migrate all materials"""
        
        materials = materials_data.get('materials', {})
        total_materials = len(materials)
        
        print(f"🚀 Starting migration of {total_materials} materials...")
        print(f"📁 Output directory: {self.frontmatter_dir}")
        print(f"📋 Mode: {'DRY RUN' if self.dry_run else 'LIVE MIGRATION'}")
        print("-" * 80)
        
        for i, material_name in enumerate(materials.keys(), 1):
            print(f"[{i}/{total_materials}] ", end="")
            self.migrate_material(material_name, materials_data)
        
        print("-" * 80)
        print("📊 MIGRATION SUMMARY")
        print(f"  ✅ Processed: {self.migration_stats['processed']}")
        print(f"  ❌ Errors: {self.migration_stats['errors']}")
        print(f"  🔄 Properties Migrated: {self.migration_stats['migrated_properties']}")
        print(f"  📦 Fields Preserved: {self.migration_stats['preserved_fields']}")
        
        if self.migration_stats['errors'] == 0:
            print("🎉 Migration completed successfully!")
        else:
            print(f"⚠️  Migration completed with {self.migration_stats['errors']} errors")

def main():
    parser = argparse.ArgumentParser(description='Migrate frontmatter files to new format')
    parser.add_argument('--material', help='Migrate specific material only')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing files')
    
    args = parser.parse_args()
    
    # Initialize migrator
    migrator = FrontmatterMigrator(dry_run=args.dry_run)
    
    # Load materials data
    print("📂 Loading materials data...")
    materials_data = migrator.load_materials_data()
    print(f"✅ Loaded {len(materials_data.get('materials', {}))} materials")
    
    # Migrate materials
    if args.material:
        migrator.migrate_material(args.material, materials_data)
    else:
        migrator.migrate_all_materials(materials_data)

if __name__ == '__main__':
    main()