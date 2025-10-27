#!/usr/bin/env python3
"""
Migrate flat properties structure to hierarchical materialProperties.

BEFORE (old flat structure):
  properties:
    density: {...}
    thermalConductivity: {...}

AFTER (new hierarchical structure):
  materialProperties:
    material_characteristics:
      properties:
        density: {...}
    laser_material_interaction:
      properties:
        thermalConductivity: {...}

Also ensures generators write to correct structure.
"""

import yaml
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict

class PropertyMigrator:
    """Migrate properties from flat to hierarchical structure."""
    
    # Property categorization
    MATERIAL_CHARACTERISTICS = {
        'density', 'hardness', 'tensileStrength', 'compressiveStrength',
        'flexuralStrength', 'youngsModulus', 'poissonsRatio', 'fractureToughness',
        'porosity', 'grainSize', 'crystallineStructure', 'corrosionResistance',
        'oxidationResistance', 'wearResistance', 'fatigueStrength'
    }
    
    LASER_MATERIAL_INTERACTION = {
        'laserReflectivity', 'laserAbsorption', 'thermalConductivity',
        'thermalDiffusivity', 'thermalExpansion', 'specificHeat',
        'thermalDestruction', 'meltingPoint', 'boilingPoint', 'vaporization',
        'ablationThreshold', 'damageThreshold', 'penetrationDepth',
        'absorptionCoefficient', 'emissivity'
    }
    
    def __init__(self):
        self.materials_file = Path('data/Materials.yaml')
        self.backup_file = Path(f'data/Materials.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml')
        
    def categorize_property(self, prop_name: str) -> str:
        """Determine which section a property belongs to."""
        if prop_name in self.MATERIAL_CHARACTERISTICS:
            return 'material_characteristics'
        elif prop_name in self.LASER_MATERIAL_INTERACTION:
            return 'laser_material_interaction'
        else:
            # Default to other for unknown properties
            return 'other'
    
    def migrate_material(self, material_name: str, material_data: Dict) -> Dict:
        """Migrate a single material's properties to hierarchical structure."""
        if 'properties' not in material_data:
            return material_data, []
        
        old_properties = material_data['properties']
        migrated_count = []
        
        # Ensure materialProperties structure exists
        if 'materialProperties' not in material_data:
            material_data['materialProperties'] = {
                'material_characteristics': {
                    'label': 'Material Characteristics',
                    'description': 'Intrinsic physical, mechanical, chemical, and structural properties affecting cleaning outcomes and material integrity',
                    'properties': {}
                },
                'laser_material_interaction': {
                    'label': 'Laser-Material Interaction',
                    'description': 'Optical and thermal properties governing laser energy absorption, reflection, propagation, and ablation thresholds',
                    'properties': {}
                }
            }
        
        # Ensure properties dicts exist in each section
        for section in material_data['materialProperties'].values():
            if 'properties' not in section:
                section['properties'] = {}
        
        # Migrate each property to appropriate section
        for prop_name, prop_data in old_properties.items():
            section_name = self.categorize_property(prop_name)
            
            # Add 'other' section if needed
            if section_name == 'other' and section_name not in material_data['materialProperties']:
                material_data['materialProperties']['other'] = {
                    'label': 'Other Properties',
                    'description': 'Additional material-specific properties',
                    'properties': {}
                }
            
            # Check if property already exists in new structure (avoid duplicates)
            section = material_data['materialProperties'][section_name]
            if prop_name not in section['properties']:
                section['properties'][prop_name] = prop_data
                migrated_count.append(prop_name)
        
        # Remove old flat properties structure
        if migrated_count:
            del material_data['properties']
        
        return material_data, migrated_count
    
    def run(self):
        """Execute migration on all materials."""
        print("=" * 70)
        print("Migrating flat properties to hierarchical materialProperties")
        print("=" * 70)
        print()
        
        # Create backup
        print(f"💾 Creating backup: {self.backup_file.name}...")
        shutil.copy2(self.materials_file, self.backup_file)
        
        # Load Materials.yaml
        print(f"📖 Loading {self.materials_file}...")
        with open(self.materials_file, 'r') as f:
            materials_data = yaml.safe_load(f)
        
        # Migrate each material
        print(f"🔧 Processing {len(materials_data['materials'])} materials...")
        print()
        
        total_migrated = 0
        materials_updated = 0
        
        for material_name, material_data in materials_data['materials'].items():
            updated_data, migrated_props = self.migrate_material(material_name, material_data)
            
            if migrated_props:
                materials_updated += 1
                total_migrated += len(migrated_props)
                print(f"  ✅ {material_name}: Migrated {len(migrated_props)} properties")
                materials_data['materials'][material_name] = updated_data
        
        # Save updated data
        print()
        print(f"💾 Saving updated {self.materials_file}...")
        with open(self.materials_file, 'w') as f:
            yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, indent=2)
        
        # Summary
        print()
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"✅ Migrated {total_migrated} properties from {materials_updated} materials")
        print(f"📊 Total materials: {len(materials_data['materials'])}")
        print(f"💾 Backup: {self.backup_file.name}")
        print("=" * 70)
        print()
        print("✅ Migration complete! Old flat 'properties' removed, all data in hierarchical 'materialProperties'")

if __name__ == '__main__':
    migrator = PropertyMigrator()
    migrator.run()
