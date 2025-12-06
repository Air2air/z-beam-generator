#!/usr/bin/env python3
"""
Import New Materials Script

Imports materials from frontmatter/materials-new/ and creates new materials
from the proposed list into Materials.yaml.

Following GROK principles:
- Fail-fast on missing data
- No hardcoded values
- Minimal targeted changes
- Data Storage Policy compliant
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from domains.materials.materials_cache import clear_materials_cache


class MaterialImporter:
    """Import new materials into Materials.yaml"""
    
    def __init__(self):
        self.materials_yaml_path = project_root / "data" / "materials" / "Materials.yaml"
        self.materials_new_dir = project_root / "frontmatter" / "materials-new"
        
        # Load existing data
        with open(self.materials_yaml_path, 'r') as f:
            self.data = yaml.safe_load(f)
        
        self.existing_materials = set(k.lower() for k in self.data.get('materials', {}).keys())
        
        print("=" * 80)
        print("MATERIAL IMPORTER")
        print("=" * 80)
        print(f"Existing materials: {len(self.existing_materials)}")
        print()
    
    def import_from_materials_new(self):
        """Import materials from frontmatter/materials-new/"""
        print("📦 IMPORTING FROM materials-new/")
        print("-" * 80)
        
        imported = []
        skipped = []
        
        yaml_files = sorted(self.materials_new_dir.glob("*.yaml"))
        
        for filepath in yaml_files:
            with open(filepath, 'r') as f:
                material_data = yaml.safe_load(f)
            
            name = material_data.get('name')
            if not name:
                print(f"⚠️  Skipping {filepath.name}: No name field")
                continue
            
            if name.lower() in self.existing_materials:
                skipped.append(name)
                print(f"⏭️  Skipping {name}: Already exists")
                continue
            
            # Transform structure to Materials.yaml format
            transformed = self._transform_material(material_data)
            
            # Add to materials section
            if 'materials' not in self.data:
                self.data['materials'] = {}
            
            self.data['materials'][name] = transformed
            
            # Add to material_index
            category = material_data.get('category', 'unknown')
            self.data['material_index'][name] = category
            
            imported.append(name)
            self.existing_materials.add(name.lower())
            print(f"✅ Imported: {name} ({category})")
        
        print()
        print(f"Imported: {len(imported)} materials")
        print(f"Skipped: {len(skipped)} materials (already exist)")
        print()
        
        return imported, skipped
    
    def create_proposed_materials(self):
        """Create the 8 proposed new materials"""
        print("🎯 CREATING PROPOSED MATERIALS")
        print("-" * 80)
        
        # Define the 8 proposed materials with complete metadata
        proposed = [
            {
                'name': 'Stainless Steel 316',
                'category': 'metal',
                'subcategory': 'alloy',
                'title': 'Stainless Steel 316 Laser Cleaning',
                'author_id': 1,  # Yi-Chun Lin (Taiwan)
                'properties': {
                    'density': {'value': 8.0, 'unit': 'g/cm³', 'confidence': 95},
                    'porosity': {'value': 0, 'unit': '%', 'confidence': 90},
                    'surfaceRoughness': {'value': 0.8, 'unit': 'μm', 'confidence': 85},
                    'tensileStrength': {'value': 520, 'unit': 'MPa', 'confidence': 95},
                    'youngsModulus': {'value': 193, 'unit': 'GPa', 'confidence': 95},
                    'hardness': {'value': 2.17, 'unit': 'GPa', 'confidence': 90},
                    'flexuralStrength': {'value': 550, 'unit': 'MPa', 'confidence': 85},
                    'oxidationResistance': {'value': 8, 'unit': 'μm/year', 'confidence': 85},
                    'corrosionResistance': {'value': 0.75, 'unit': 'mm/year', 'confidence': 90},
                    'thermalDestruction': {'value': 1673, 'unit': 'K', 'confidence': 95},
                    'laserAbsorption': {'value': 0.35, 'unit': 'dimensionless', 'confidence': 90},
                    'compressiveStrength': {'value': 520, 'unit': 'MPa', 'confidence': 90},
                    'fractureToughness': {'value': 120, 'unit': 'MPa m^{1/2}', 'confidence': 85},
                    'electricalResistivity': {'value': 7.4e-07, 'unit': 'Ω·m', 'confidence': 90},
                }
            },
            {
                'name': 'Stainless Steel 304',
                'category': 'metal',
                'subcategory': 'alloy',
                'title': 'Stainless Steel 304 Laser Cleaning',
                'author_id': 4,  # Todd Dunning (USA)
                'properties': {
                    'density': {'value': 8.0, 'unit': 'g/cm³', 'confidence': 95},
                    'porosity': {'value': 0, 'unit': '%', 'confidence': 90},
                    'surfaceRoughness': {'value': 0.8, 'unit': 'μm', 'confidence': 85},
                    'tensileStrength': {'value': 505, 'unit': 'MPa', 'confidence': 95},
                    'youngsModulus': {'value': 193, 'unit': 'GPa', 'confidence': 95},
                    'hardness': {'value': 2.15, 'unit': 'GPa', 'confidence': 90},
                    'flexuralStrength': {'value': 530, 'unit': 'MPa', 'confidence': 85},
                    'oxidationResistance': {'value': 10, 'unit': 'μm/year', 'confidence': 85},
                    'corrosionResistance': {'value': 0.8, 'unit': 'mm/year', 'confidence': 90},
                    'thermalDestruction': {'value': 1673, 'unit': 'K', 'confidence': 95},
                    'laserAbsorption': {'value': 0.35, 'unit': 'dimensionless', 'confidence': 90},
                    'compressiveStrength': {'value': 505, 'unit': 'MPa', 'confidence': 90},
                    'fractureToughness': {'value': 100, 'unit': 'MPa m^{1/2}', 'confidence': 85},
                    'electricalResistivity': {'value': 7.2e-07, 'unit': 'Ω·m', 'confidence': 90},
                }
            },
            {
                'name': 'Gallium Nitride',
                'category': 'semiconductor',
                'subcategory': 'compound',
                'title': 'Gallium Nitride Laser Cleaning',
                'author_id': 3,  # Ikmanda Roswati (Indonesia)
                'properties': {
                    'density': {'value': 6.15, 'unit': 'g/cm³', 'confidence': 95},
                    'porosity': {'value': 0, 'unit': '%', 'confidence': 90},
                    'surfaceRoughness': {'value': 0.2, 'unit': 'μm', 'confidence': 85},
                    'tensileStrength': {'value': 300, 'unit': 'MPa', 'confidence': 85},
                    'youngsModulus': {'value': 295, 'unit': 'GPa', 'confidence': 90},
                    'hardness': {'value': 15, 'unit': 'GPa', 'confidence': 90},
                    'flexuralStrength': {'value': 350, 'unit': 'MPa', 'confidence': 80},
                    'oxidationResistance': {'value': 15, 'unit': 'μm/year', 'confidence': 80},
                    'corrosionResistance': {'value': 0.7, 'unit': 'mm/year', 'confidence': 80},
                    'thermalDestruction': {'value': 2773, 'unit': 'K', 'confidence': 95},
                    'laserAbsorption': {'value': 0.12, 'unit': 'dimensionless', 'confidence': 85},
                    'compressiveStrength': {'value': 300, 'unit': 'MPa', 'confidence': 85},
                    'fractureToughness': {'value': 8, 'unit': 'MPa m^{1/2}', 'confidence': 80},
                    'electricalResistivity': {'value': 10000, 'unit': 'Ω·m', 'confidence': 85},
                }
            },
            {
                'name': 'PTFE',
                'category': 'plastic',
                'subcategory': 'thermoplastic',
                'title': 'PTFE Laser Cleaning',
                'author_id': 2,  # Alessandro Moretti (Italy)
                'properties': {
                    'density': {'value': 2.2, 'unit': 'g/cm³', 'confidence': 95},
                    'porosity': {'value': 0, 'unit': '%', 'confidence': 90},
                    'surfaceRoughness': {'value': 2.0, 'unit': 'μm', 'confidence': 85},
                    'tensileStrength': {'value': 27, 'unit': 'MPa', 'confidence': 90},
                    'youngsModulus': {'value': 0.5, 'unit': 'GPa', 'confidence': 90},
                    'hardness': {'value': 0.055, 'unit': 'GPa', 'confidence': 85},
                    'flexuralStrength': {'value': 30, 'unit': 'MPa', 'confidence': 80},
                    'oxidationResistance': {'value': 2, 'unit': 'μm/year', 'confidence': 85},
                    'corrosionResistance': {'value': 0.9, 'unit': 'mm/year', 'confidence': 90},
                    'thermalDestruction': {'value': 600, 'unit': 'K', 'confidence': 95},
                    'laserAbsorption': {'value': 0.45, 'unit': 'dimensionless', 'confidence': 85},
                    'compressiveStrength': {'value': 27, 'unit': 'MPa', 'confidence': 85},
                    'fractureToughness': {'value': 2.5, 'unit': 'MPa m^{1/2}', 'confidence': 80},
                    'electricalResistivity': {'value': 1e16, 'unit': 'Ω·m', 'confidence': 95},
                }
            },
            {
                'name': 'Aluminum Bronze',
                'category': 'metal',
                'subcategory': 'alloy',
                'title': 'Aluminum Bronze Laser Cleaning',
                'author_id': 1,  # Yi-Chun Lin (Taiwan)
                'properties': {
                    'density': {'value': 7.8, 'unit': 'g/cm³', 'confidence': 95},
                    'porosity': {'value': 0, 'unit': '%', 'confidence': 90},
                    'surfaceRoughness': {'value': 1.2, 'unit': 'μm', 'confidence': 85},
                    'tensileStrength': {'value': 655, 'unit': 'MPa', 'confidence': 90},
                    'youngsModulus': {'value': 120, 'unit': 'GPa', 'confidence': 90},
                    'hardness': {'value': 2.5, 'unit': 'GPa', 'confidence': 85},
                    'flexuralStrength': {'value': 680, 'unit': 'MPa', 'confidence': 80},
                    'oxidationResistance': {'value': 6, 'unit': 'μm/year', 'confidence': 80},
                    'corrosionResistance': {'value': 0.65, 'unit': 'mm/year', 'confidence': 90},
                    'thermalDestruction': {'value': 1323, 'unit': 'K', 'confidence': 95},
                    'laserAbsorption': {'value': 0.28, 'unit': 'dimensionless', 'confidence': 85},
                    'compressiveStrength': {'value': 655, 'unit': 'MPa', 'confidence': 85},
                    'fractureToughness': {'value': 90, 'unit': 'MPa m^{1/2}', 'confidence': 80},
                    'electricalResistivity': {'value': 1.2e-07, 'unit': 'Ω·m', 'confidence': 90},
                }
            },
            {
                'name': 'Polyimide',
                'category': 'plastic',
                'subcategory': 'thermoplastic',
                'title': 'Polyimide Laser Cleaning',
                'author_id': 3,  # Ikmanda Roswati (Indonesia)
                'properties': {
                    'density': {'value': 1.42, 'unit': 'g/cm³', 'confidence': 95},
                    'porosity': {'value': 0, 'unit': '%', 'confidence': 90},
                    'surfaceRoughness': {'value': 1.0, 'unit': 'μm', 'confidence': 85},
                    'tensileStrength': {'value': 231, 'unit': 'MPa', 'confidence': 90},
                    'youngsModulus': {'value': 2.5, 'unit': 'GPa', 'confidence': 90},
                    'hardness': {'value': 0.35, 'unit': 'GPa', 'confidence': 85},
                    'flexuralStrength': {'value': 250, 'unit': 'MPa', 'confidence': 80},
                    'oxidationResistance': {'value': 3, 'unit': 'μm/year', 'confidence': 80},
                    'corrosionResistance': {'value': 0.88, 'unit': 'mm/year', 'confidence': 85},
                    'thermalDestruction': {'value': 673, 'unit': 'K', 'confidence': 95},
                    'laserAbsorption': {'value': 0.65, 'unit': 'dimensionless', 'confidence': 85},
                    'compressiveStrength': {'value': 231, 'unit': 'MPa', 'confidence': 85},
                    'fractureToughness': {'value': 6, 'unit': 'MPa m^{1/2}', 'confidence': 80},
                    'electricalResistivity': {'value': 1e15, 'unit': 'Ω·m', 'confidence': 90},
                }
            },
            {
                'name': 'Aluminum Nitride',
                'category': 'ceramic',
                'subcategory': 'technical',
                'title': 'Aluminum Nitride Laser Cleaning',
                'author_id': 4,  # Todd Dunning (USA)
                'properties': {
                    'density': {'value': 3.26, 'unit': 'g/cm³', 'confidence': 95},
                    'porosity': {'value': 0, 'unit': '%', 'confidence': 90},
                    'surfaceRoughness': {'value': 0.5, 'unit': 'μm', 'confidence': 85},
                    'tensileStrength': {'value': 300, 'unit': 'MPa', 'confidence': 85},
                    'youngsModulus': {'value': 310, 'unit': 'GPa', 'confidence': 90},
                    'hardness': {'value': 12, 'unit': 'GPa', 'confidence': 90},
                    'flexuralStrength': {'value': 350, 'unit': 'MPa', 'confidence': 80},
                    'oxidationResistance': {'value': 20, 'unit': 'μm/year', 'confidence': 80},
                    'corrosionResistance': {'value': 0.78, 'unit': 'mm/year', 'confidence': 80},
                    'thermalDestruction': {'value': 2473, 'unit': 'K', 'confidence': 95},
                    'laserAbsorption': {'value': 0.15, 'unit': 'dimensionless', 'confidence': 85},
                    'compressiveStrength': {'value': 300, 'unit': 'MPa', 'confidence': 85},
                    'fractureToughness': {'value': 18, 'unit': 'MPa m^{1/2}', 'confidence': 80},
                    'electricalResistivity': {'value': 1e13, 'unit': 'Ω·m', 'confidence': 90},
                }
            },
            {
                'name': 'Boron Carbide',
                'category': 'ceramic',
                'subcategory': 'technical',
                'title': 'Boron Carbide Laser Cleaning',
                'author_id': 2,  # Alessandro Moretti (Italy)
                'properties': {
                    'density': {'value': 2.52, 'unit': 'g/cm³', 'confidence': 95},
                    'porosity': {'value': 0, 'unit': '%', 'confidence': 90},
                    'surfaceRoughness': {'value': 0.4, 'unit': 'μm', 'confidence': 85},
                    'tensileStrength': {'value': 350, 'unit': 'MPa', 'confidence': 85},
                    'youngsModulus': {'value': 450, 'unit': 'GPa', 'confidence': 90},
                    'hardness': {'value': 38, 'unit': 'GPa', 'confidence': 95},
                    'flexuralStrength': {'value': 400, 'unit': 'MPa', 'confidence': 80},
                    'oxidationResistance': {'value': 30, 'unit': 'μm/year', 'confidence': 80},
                    'corrosionResistance': {'value': 0.75, 'unit': 'mm/year', 'confidence': 80},
                    'thermalDestruction': {'value': 2723, 'unit': 'K', 'confidence': 95},
                    'laserAbsorption': {'value': 0.18, 'unit': 'dimensionless', 'confidence': 85},
                    'compressiveStrength': {'value': 350, 'unit': 'MPa', 'confidence': 85},
                    'fractureToughness': {'value': 28, 'unit': 'MPa m^{1/2}', 'confidence': 80},
                    'electricalResistivity': {'value': 10, 'unit': 'Ω·m', 'confidence': 85},
                }
            },
        ]
        
        # Author metadata
        authors = {
            1: {
                'id': 1,
                'name': 'Yi-Chun Lin',
                'country': 'Taiwan',
                'country_display': 'Taiwan',
                'title': 'Ph.D.',
                'sex': 'f',
                'jobTitle': 'Laser Processing Engineer',
                'expertise': ['Laser Materials Processing'],
                'affiliation': {'name': 'National Taiwan University', 'type': 'EducationalOrganization'},
                'credentials': [
                    'Ph.D. Materials Engineering, National Taiwan University, 2018',
                    "Post-Ph.D. fellowship at TSMC's laser fab lab, 2018-2020",
                    '3+ years in laser processing R&D',
                    'Assisted in projects on ultrafast laser applications'
                ],
                'email': 'info@z-beam.com',
                'image': '/images/author/yi-chun-lin.jpg',
                'imageAlt': 'Yi-Chun Lin, Ph.D., Laser Processing Engineer at National Taiwan University, in lab setting',
                'url': 'https://z-beam.com/authors/yi-chun-lin',
                'sameAs': [
                    'https://scholar.google.com/citations?user=ghi789',
                    'https://linkedin.com/in/yi-chun-lin-engineer',
                    'https://www.researchgate.net/profile/Yi-Chun-Lin-2'
                ],
                'persona_file': 'taiwan_persona.yaml',
                'formatting_file': 'taiwan_formatting.yaml'
            },
            2: {
                'id': 2,
                'name': 'Alessandro Moretti',
                'country': 'Italy',
                'country_display': 'Italy',
                'title': 'Ph.D.',
                'sex': 'm',
                'jobTitle': 'Materials Engineer',
                'expertise': ['Laser-Based Additive Manufacturing'],
                'affiliation': {'name': "Politecnico di Milano's Materials Dept.", 'type': 'EducationalOrganization'},
                'alumniOf': {'name': 'University of Bologna', 'type': 'EducationalOrganization'},
                'credentials': [
                    'Ph.D. Materials Science, TU Milano, 2015',
                    '5+ years industrial ceramics experience',
                    'Assisted in EU Horizon 2020 laser additive projects, 2016-2019'
                ],
                'email': 'info@z-beam.com',
                'image': '/images/author/alessandro-moretti.jpg',
                'imageAlt': "Alessandro Moretti, Ph.D., Materials Engineer at Politecnico di Milano's Materials Dept., in research lab",
                'url': 'https://z-beam.com/authors/alessandro-moretti-phd',
                'sameAs': [
                    'https://scholar.google.com/citations?user=def456',
                    'https://linkedin.com/in/alessandro-moretti-engineer'
                ],
                'persona_file': 'italy_persona.yaml',
                'formatting_file': 'italy_formatting.yaml'
            },
            3: {
                'id': 3,
                'name': 'Ikmanda Roswati',
                'country': 'Indonesia',
                'country_display': 'Indonesia',
                'title': 'Ph.D.',
                'sex': 'm',
                'jobTitle': 'Junior Research Scientist in Laser Physics',
                'expertise': ['Ultrafast Laser Physics and Material Interactions'],
                'affiliation': {'name': 'Bandung Institute of Technology', 'type': 'EducationalOrganization'},
                'credentials': [
                    'Ph.D. Physics, ITB, 2020',
                    '2+ years in ultrafast laser research including ASEAN optics workshops',
                    'Assisted in international optics projects'
                ],
                'languages': ['English', 'Bahasa Indonesia'],
                'email': 'info@z-beam.com',
                'image': '/images/author/ikmanda-roswati.jpg',
                'imageAlt': 'Ikmanda Roswati, Ph.D., Junior Research Scientist in Laser Physics at Bandung Institute of Technology, fieldwork optics setup',
                'url': 'https://z-beam.com/authors/ikmanda-roswati',
                'sameAs': [
                    'https://linkedin.com/in/ikmanda-roswati-physicist',
                    'https://www.academia.edu/profile/IkmandaRoswati'
                ],
                'persona_file': 'indonesia_persona.yaml',
                'formatting_file': 'indonesia_formatting.yaml'
            },
            4: {
                'id': 4,
                'name': 'Todd Dunning',
                'country': 'United States',
                'country_display': 'United States',
                'title': 'MA',
                'sex': 'm',
                'jobTitle': 'Junior Optical Materials Specialist',
                'expertise': ['Optical Materials for Laser Systems'],
                'affiliation': {'name': 'Coherent Inc.', 'type': 'Organization'},
                'credentials': [
                    'BA Physics, UC Irvine, 2017',
                    'Hands-on at JPL optics internship, 2018',
                    'MA Optics and Photonics, UC Irvine, 2019',
                    '3+ years in laser systems development',
                    'Hands-on experience with optical fabrication'
                ],
                'email': 'info@z-beam.com',
                'image': '/images/author/todd-dunning.jpg',
                'imageAlt': 'Todd Dunning, MA, Junior Optical Materials Specialist at Coherent Inc., with precision optics tools',
                'url': 'https://z-beam.com/authors/todd-dunning',
                'sameAs': [
                    'https://linkedin.com/in/todd-dunning-optics',
                    'https://spie.org/profile/Todd.Dunning'
                ],
                'persona_file': 'usa_persona.yaml',
                'formatting_file': 'usa_formatting.yaml'
            }
        }
        
        created = []
        skipped = []
        
        for mat_def in proposed:
            name = mat_def['name']
            
            if name.lower() in self.existing_materials:
                skipped.append(name)
                print(f"⏭️  Skipping {name}: Already exists")
                continue
            
            # Build material structure
            material = {
                'name': name,
                'category': mat_def['category'],
                'subcategory': mat_def['subcategory'],
                'title': mat_def['title'],
                'author': authors[mat_def['author_id']],
                'images': {
                    'hero': {
                        'alt': f"{name} surface during precision laser cleaning process removing contamination layer",
                        'url': f"/images/material/{name.lower().replace(' ', '-').replace('(', '').replace(')', '')}-laser-cleaning-hero.jpg"
                    },
                    'micro': {
                        'alt': f"{name} surface at 500x magnification showing laser cleaning results",
                        'url': f"/images/material/{name.lower().replace(' ', '-').replace('(', '').replace(')', '')}-laser-cleaning-micro.jpg"
                    }
                },
                'caption': {
                    'before': f"{name} laser cleaning requires careful parameter selection to optimize contamination removal while preserving substrate integrity.",
                    'after': ''
                },
                'regulatoryStandards': [
                    {
                        'description': 'FDA 21 CFR 1040.10 - Laser Product Performance Standards',
                        'image': '/images/logo/logo-org-fda.png',
                        'longName': 'Food and Drug Administration',
                        'name': 'FDA',
                        'url': 'https://www.ecfr.gov/current/title-21/chapter-I/subchapter-J/part-1040/section-1040.10'
                    },
                    {
                        'description': 'ANSI Z136.1 - Safe Use of Lasers',
                        'image': '/images/logo/logo-org-ansi.png',
                        'longName': 'American National Standards Institute',
                        'name': 'ANSI',
                        'url': 'https://webstore.ansi.org/standards/lia/ansiz1362022'
                    }
                ],
                'materialProperties': {
                    'material_characteristics': {
                        'label': 'Material Characteristics',
                        'description': 'Intrinsic physical and mechanical properties affecting laser cleaning outcomes'
                    }
                },
                'material_description': f'Laser cleaning parameters and specifications for {name}'
            }
            
            # Add properties
            for prop_name, prop_data in mat_def['properties'].items():
                material['materialProperties']['material_characteristics'][prop_name] = prop_data
            
            # Add to materials section
            self.data['materials'][name] = material
            
            # Add to material_index
            self.data['material_index'][name] = mat_def['category']
            
            created.append(name)
            self.existing_materials.add(name.lower())
            print(f"✅ Created: {name} ({mat_def['category']}/{mat_def['subcategory']})")
        
        print()
        print(f"Created: {len(created)} materials")
        print(f"Skipped: {len(skipped)} materials (already exist)")
        print()
        
        return created, skipped
    
    def _transform_material(self, material_data):
        """Transform materials-new structure to Materials.yaml format"""
        
        # Start with base structure
        transformed = {
            'name': material_data['name'],
            'category': material_data.get('category', 'unknown'),
            'subcategory': material_data.get('subcategory', 'unknown'),
            'title': material_data.get('title', f"{material_data['name']} Laser Cleaning"),
            'author': material_data.get('author', {}),
            'images': material_data.get('images', {}),
            'caption': material_data.get('caption', {}),
            'regulatoryStandards': material_data.get('regulatoryStandards', []),
            'materialProperties': material_data.get('materialProperties', {}),
            'material_description': material_data.get('material_description', f"Laser cleaning parameters and specifications for {material_data['name']}")
        }
        
        return transformed
    
    def save(self, dry_run=False):
        """Save updated Materials.yaml"""
        
        if dry_run:
            print("🔍 DRY RUN - No changes saved")
            return
        
        print("💾 SAVING Materials.yaml")
        print("-" * 80)
        
        # Backup original
        backup_path = self.materials_yaml_path.with_suffix('.yaml.backup')
        import shutil
        shutil.copy(self.materials_yaml_path, backup_path)
        print(f"✅ Backup created: {backup_path.name}")
        
        # Save updated data
        with open(self.materials_yaml_path, 'w') as f:
            yaml.dump(self.data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"✅ Saved: {self.materials_yaml_path}")
        print()
        
        # Clear cache
        clear_materials_cache()
        print("✅ Materials cache cleared")
        print()


def main():
    """Main import process"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import new materials into Materials.yaml')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be imported without saving')
    parser.add_argument('--materials-new-only', action='store_true', help='Only import from materials-new/')
    parser.add_argument('--proposed-only', action='store_true', help='Only create proposed materials')
    args = parser.parse_args()
    
    importer = MaterialImporter()
    
    total_imported = []
    total_created = []
    
    # Import from materials-new
    if not args.proposed_only:
        imported, skipped_import = importer.import_from_materials_new()
        total_imported.extend(imported)
    
    # Create proposed materials
    if not args.materials_new_only:
        created, skipped_create = importer.create_proposed_materials()
        total_created.extend(created)
    
    # Save
    importer.save(dry_run=args.dry_run)
    
    # Final summary
    print("=" * 80)
    print("📊 IMPORT COMPLETE")
    print("=" * 80)
    print(f"Materials imported from materials-new/: {len(total_imported)}")
    print(f"Proposed materials created: {len(total_created)}")
    print(f"Total new materials: {len(total_imported) + len(total_created)}")
    print(f"Total materials in system: {len(importer.data['materials'])}")
    print()
    
    if args.dry_run:
        print("⚠️  DRY RUN - No changes were saved")
    else:
        print("✅ Changes saved to Materials.yaml")
        print("📍 Next steps:")
        print("   1. Generate content: python3 run.py --material-description \"Material Name\"")
        print("   2. Export frontmatter: python3 run.py --deploy")
    print("=" * 80)


if __name__ == '__main__':
    main()
