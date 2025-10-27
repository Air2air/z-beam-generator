#!/usr/bin/env python3
"""
Conform Materials.yaml to frontmatter-example.yaml structure.

Adds all missing fields required by the example format:
- name (extracted from key)
- subcategory
- title
- regulatoryStandards
- materialProperties (hierarchical structure)
- outcomeMetrics

NO data loss - retains all existing data.
"""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class MaterialsConformer:
    def __init__(self):
        self.timestamp = datetime.now().strftime('%Y-%m-%d')
        self.materials_file = Path('data/Materials.yaml')
        self.backup_file = Path(f'data/Materials.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml')
        
        # Load Categories.yaml for subcategory mapping
        categories_file = Path('data/Categories.yaml')
        with open(categories_file, 'r') as f:
            self.categories_data = yaml.safe_load(f)
    
    def get_subcategory_for_material(self, material_name: str, category: str) -> str:
        """Determine appropriate subcategory for a material."""
        # Category-specific subcategory mappings
        subcategory_map = {
            'metal': {
                'Steel': 'ferrous',
                'Cast Iron': 'ferrous',
                'Stainless Steel': 'ferrous',
                'Aluminum': 'non-ferrous',
                'Copper': 'non-ferrous',
                'Brass': 'alloy',
                'Bronze': 'alloy',
                'Titanium': 'aerospace',
                'Nickel': 'specialty',
                'default': 'alloy'
            },
            'ceramic': {
                'Alumina': 'oxide',
                'Zirconia': 'oxide',
                'Silicon Carbide': 'carbide',
                'default': 'oxide'
            },
            'stone': {
                'Alabaster': 'mineral',
                'Basalt': 'igneous',
                'Granite': 'igneous',
                'Marble': 'metamorphic',
                'Limestone': 'sedimentary',
                'default': 'natural'
            },
            'wood': {
                'Oak': 'hardwood',
                'Pine': 'softwood',
                'Bamboo': 'bamboo',
                'default': 'hardwood'
            },
            'glass': {
                'Borosilicate Glass': 'borosilicate',
                'default': 'specialty-glass'
            },
            'plastic': {
                'default': 'thermoplastic'
            },
            'composite': {
                'Carbon Fiber Reinforced Polymer': 'fiber-reinforced',
                'default': 'structural'
            },
            'masonry': {
                'Brick': 'fired',
                'Concrete': 'concrete',
                'default': 'concrete'
            },
            'semiconductor': {
                'Silicon': 'intrinsic',
                'Gallium Arsenide': 'compound',
                'default': 'intrinsic'
            },
            'rare-earth': {
                'Cerium': 'lanthanide',
                'default': 'lanthanide'
            }
        }
        
        cat_map = subcategory_map.get(category, {'default': 'specialty'})
        return cat_map.get(material_name, cat_map['default'])
    
    def add_missing_fields(self, material_name: str, material_data: Dict) -> Dict:
        """Add all missing fields required by frontmatter-example.yaml."""
        category = material_data.get('category', 'metal')
        
        # 1. Add name if missing (explicit field)
        if 'name' not in material_data:
            material_data['name'] = material_name
        
        # 2. Add subcategory if missing
        if 'subcategory' not in material_data:
            material_data['subcategory'] = self.get_subcategory_for_material(material_name, category)
        
        # 3. Add title if missing
        if 'title' not in material_data:
            material_data['title'] = f"{material_name} Laser Cleaning"
        
        # 4. Add regulatoryStandards if missing
        if 'regulatoryStandards' not in material_data:
            material_data['regulatoryStandards'] = self.get_default_regulatory_standards()
        
        # 5. Add materialProperties with hierarchical structure if missing
        if 'materialProperties' not in material_data:
            material_data['materialProperties'] = self.create_material_properties_structure(
                material_name, category
            )
        
        # 6. Add outcomeMetrics if missing
        if 'outcomeMetrics' not in material_data:
            material_data['outcomeMetrics'] = self.get_default_outcome_metrics(material_name)
        
        return material_data
    
    def get_default_regulatory_standards(self) -> List[Dict]:
        """Get default regulatory standards list."""
        return [
            {
                'name': 'ANSI',
                'longName': 'American National Standards Institute',
                'description': 'ANSI Z136.1 - Safe Use of Lasers',
                'url': 'https://webstore.ansi.org/standards/lia/ansiz1362022',
                'image': '/images/logo/logo-org-ansi.png'
            },
            {
                'name': 'IEC',
                'longName': 'International Electrotechnical Commission',
                'description': 'IEC 60825 - Safety of Laser Products',
                'url': 'https://webstore.iec.ch/en/publication/3587',
                'image': '/images/logo/logo-org-iec.png'
            },
            {
                'name': 'OSHA',
                'longName': 'Occupational Safety and Health Administration',
                'description': 'OSHA 29 CFR 1926.95 - Personal Protective Equipment',
                'url': 'https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.95',
                'image': '/images/logo/logo-org-osha.png'
            }
        ]
    
    def create_material_properties_structure(self, material_name: str, category: str) -> Dict:
        """Create hierarchical materialProperties structure."""
        return {
            'material_characteristics': {
                'label': 'Material Characteristics',
                'description': 'Intrinsic physical, mechanical, chemical, and structural properties affecting cleaning outcomes and material integrity',
                # Properties will be added by research
            },
            'laser_material_interaction': {
                'label': 'Laser-Material Interaction',
                'description': 'Optical and thermal properties governing laser energy absorption, reflection, propagation, and ablation thresholds',
                # Properties will be added by research
            }
        }
    
    def get_default_outcome_metrics(self, material_name: str) -> List[Dict]:
        """Get default outcome metrics list."""
        return [
            {
                'Contaminant Removal Efficiency': {
                    'description': f'Percentage of target contaminants successfully removed from {material_name} surface',
                    'typicalRanges': '95-99.9% depending on application and material',
                    'measurementMethods': [
                        'Before/after microscopy',
                        'Chemical analysis',
                        'Surface profilometry'
                    ],
                    'factorsAffecting': [
                        'Contamination type',
                        'Adhesion strength',
                        'Surface geometry',
                        'Laser parameters'
                    ]
                }
            }
        ]
    
    def process(self):
        """Main processing function."""
        print("=" * 70)
        print("Conforming Materials.yaml to frontmatter-example.yaml structure")
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
        fields_added = {
            'name': 0,
            'subcategory': 0,
            'title': 0,
            'regulatoryStandards': 0,
            'materialProperties': 0,
            'outcomeMetrics': 0
        }
        
        for mat_name, mat_data in materials.items():
            original_keys = set(mat_data.keys())
            data['materials'][mat_name] = self.add_missing_fields(mat_name, mat_data)
            new_keys = set(data['materials'][mat_name].keys())
            
            added_keys = new_keys - original_keys
            if added_keys:
                updated_count += 1
                print(f"  ✅ {mat_name}: Added {', '.join(added_keys)}")
                for key in added_keys:
                    if key in fields_added:
                        fields_added[key] += 1
        
        # Save updated data
        print(f"\n💾 Saving updated Materials.yaml...")
        with open(self.materials_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"✅ Updated: {updated_count}/{len(materials)} materials")
        print(f"\nFields added:")
        for field, count in fields_added.items():
            if count > 0:
                print(f"  • {field}: {count} materials")
        print(f"\n📊 Total materials: {len(materials)}")
        print(f"💾 Backup: {self.backup_file.name}")
        print("=" * 70)
        print("\n✅ Materials.yaml now conforms to frontmatter-example.yaml structure!")

if __name__ == '__main__':
    conformer = MaterialsConformer()
    conformer.process()
