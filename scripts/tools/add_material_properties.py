#!/usr/bin/env python3
"""
Add materialProperties to all materials in Materials.yaml

This script adds the materialProperties structure that was mistakenly removed.
Each material will get category-appropriate properties with proper structure.
"""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class MaterialPropertiesAdder:
    def __init__(self):
        self.timestamp = datetime.now().strftime('%Y-%m-%d')
        self.materials_file = Path('data/Materials.yaml')
        self.backup_file = Path(f'data/Materials.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml')
        
    def get_category_properties(self, category: str) -> List[str]:
        """Get appropriate properties for each category"""
        category_props = {
            'metal': [
                'density', 'youngsModulus', 'hardness', 'tensileStrength',
                'thermalConductivity', 'thermalExpansion', 'specificHeat',
                'electricalResistivity', 'corrosionResistance',
                'laserAbsorption', 'ablationThreshold', 'thermalDestruction'
            ],
            'ceramic': [
                'density', 'youngsModulus', 'hardness', 'compressiveStrength',
                'flexuralStrength', 'thermalConductivity', 'thermalExpansion',
                'fractureToughness', 'porosity', 'laserAbsorption',
                'ablationThreshold', 'thermalDestruction'
            ],
            'composite': [
                'density', 'youngsModulus', 'tensileStrength', 'compressiveStrength',
                'flexuralStrength', 'thermalConductivity', 'thermalExpansion',
                'laserAbsorption', 'ablationThreshold', 'thermalDestruction'
            ],
            'stone': [
                'density', 'hardness', 'compressiveStrength', 'porosity',
                'thermalConductivity', 'laserAbsorption', 'ablationThreshold',
                'thermalDestruction'
            ],
            'wood': [
                'density', 'hardness', 'compressiveStrength', 'thermalConductivity',
                'laserAbsorption', 'ablationThreshold', 'thermalDestruction'
            ],
            'glass': [
                'density', 'youngsModulus', 'hardness', 'thermalConductivity',
                'thermalExpansion', 'laserAbsorption', 'ablationThreshold',
                'thermalDestruction'
            ],
            'plastic': [
                'density', 'youngsModulus', 'tensileStrength', 'thermalConductivity',
                'thermalExpansion', 'laserAbsorption', 'ablationThreshold',
                'thermalDestruction'
            ],
            'masonry': [
                'density', 'compressiveStrength', 'porosity', 'thermalConductivity',
                'laserAbsorption', 'ablationThreshold', 'thermalDestruction'
            ],
            'semiconductor': [
                'density', 'youngsModulus', 'hardness', 'thermalConductivity',
                'electricalResistivity', 'laserAbsorption', 'ablationThreshold',
                'thermalDestruction'
            ],
            'rare-earth': [
                'density', 'hardness', 'thermalConductivity', 'electricalResistivity',
                'oxidationResistance', 'laserAbsorption', 'ablationThreshold',
                'thermalDestruction'
            ]
        }
        return category_props.get(category, [
            'density', 'laserAbsorption', 'ablationThreshold', 'thermalDestruction'
        ])
    
    def create_property_template(self, material_name: str, property_name: str) -> Dict:
        """Create a property template with AI research metadata"""
        
        # Property defaults
        property_defaults = {
            'density': {'value': None, 'unit': 'g/cm³'},
            'youngsModulus': {'value': None, 'unit': 'GPa'},
            'hardness': {'value': None, 'unit': 'HV'},
            'tensileStrength': {'value': None, 'unit': 'MPa'},
            'compressiveStrength': {'value': None, 'unit': 'MPa'},
            'flexuralStrength': {'value': None, 'unit': 'MPa'},
            'thermalConductivity': {'value': None, 'unit': 'W/(m·K)'},
            'thermalExpansion': {'value': None, 'unit': '10^-6/K'},
            'specificHeat': {'value': None, 'unit': 'J/(kg·K)'},
            'thermalDiffusivity': {'value': None, 'unit': 'mm²/s'},
            'electricalResistivity': {'value': None, 'unit': 'Ω·m'},
            'corrosionResistance': {'value': None, 'unit': 'rating'},
            'oxidationResistance': {'value': None, 'unit': '°C'},
            'porosity': {'value': None, 'unit': 'fraction'},
            'laserAbsorption': {'value': None, 'unit': 'fraction'},
            'ablationThreshold': {'value': None, 'unit': 'J/cm²'},
            'fractureToughness': {'value': None, 'unit': 'MPa·√m'}
        }
        
        if property_name == 'thermalDestruction':
            return {
                'point': {
                    'value': None,
                    'unit': '°C',
                    'min': None,
                    'max': None,
                    'confidence': None,
                    'source': 'ai_research'
                },
                'type': None
            }
        
        prop_data = property_defaults.get(property_name, {'value': None, 'unit': 'units'})
        
        return {
            'value': prop_data['value'],
            'unit': prop_data['unit'],
            'min': None,
            'max': None,
            'confidence': None,
            'source': 'ai_research'
        }
    
    def add_properties_to_material(self, material_name: str, material_data: Dict) -> Dict:
        """Add materialProperties structure to a material"""
        category = material_data.get('category', 'metal')
        
        # Skip if materialProperties already exists
        if 'materialProperties' in material_data and material_data['materialProperties']:
            print(f"  ⏭️  {material_name}: Already has materialProperties")
            return material_data
        
        # Get appropriate properties for this category
        properties = self.get_category_properties(category)
        
        # Create materialProperties dict
        material_props = {}
        for prop_name in properties:
            material_props[prop_name] = self.create_property_template(material_name, prop_name)
        
        # Add to material data
        material_data['materialProperties'] = material_props
        
        print(f"  ✅ {material_name}: Added {len(material_props)} properties ({category})")
        return material_data
    
    def process(self):
        """Main processing function"""
        print("=" * 70)
        print("Adding materialProperties to Materials.yaml")
        print("=" * 70)
        
        # Load current data
        print(f"\n📖 Loading {self.materials_file}...")
        with open(self.materials_file, 'r') as f:
            data = yaml.safe_load(f)
        
        # Create backup
        print(f"💾 Creating backup: {self.backup_file.name}...")
        with open(self.backup_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        # Process materials
        materials = data.get('materials', {})
        print(f"\n🔧 Processing {len(materials)} materials...\n")
        
        updated_count = 0
        skipped_count = 0
        
        for mat_name, mat_data in materials.items():
            if 'materialProperties' in mat_data and mat_data['materialProperties']:
                skipped_count += 1
                continue
            
            data['materials'][mat_name] = self.add_properties_to_material(mat_name, mat_data)
            updated_count += 1
        
        # Save updated data
        print(f"\n💾 Saving updated Materials.yaml...")
        with open(self.materials_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"✅ Updated: {updated_count} materials")
        print(f"⏭️  Skipped: {skipped_count} materials (already had properties)")
        print(f"📊 Total:   {len(materials)} materials")
        print(f"💾 Backup:  {self.backup_file.name}")
        print("=" * 70)
        print("\n✅ materialProperties successfully added to all materials!")
        print("\nNext step: Run property research to fill in the null values:")
        print("  python3 run.py --research-missing-properties")

if __name__ == '__main__':
    adder = MaterialPropertiesAdder()
    adder.process()
