#!/usr/bin/env python3
"""
Migrate Contaminants.yaml to relationships structure.

This script migrates legacy linkage fields to the new standardized format:
- valid_materials → relationships.related_materials (with id/title/url/image)
- eeat.citations → relationships.regulatory_compliance (with id/title/url/image)
- fumes_generated → relationships.related_compounds (with id/title/url/image)
- ppe_requirements → relationships.ppe_requirements (with id/title/url/image)

Author: GitHub Copilot
Date: December 15, 2025
"""

import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import re


class DomainLinkagesMigrator:
    """Migrates contaminants to use relationships structure."""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.contaminants_path = Path('data/contaminants/Contaminants.yaml')
        self.materials_path = Path('data/materials/Materials.yaml')
        self.standards_path = Path('data/shared/RegulatoryStandards.yaml')
        self.ppe_path = Path('data/shared/PPE.yaml')
        
        # Load reference data
        self.materials = self._load_yaml(self.materials_path)
        self.standards = self._load_yaml(self.standards_path)
        self.ppe = self._load_yaml(self.ppe_path)
        
        # Create material name to ID mapping
        self.material_name_to_id = self._build_material_mapping()
        
        # Stats
        self.stats = {
            'contaminants_processed': 0,
            'materials_migrated': 0,
            'compounds_migrated': 0,
            'standards_migrated': 0,
            'ppe_migrated': 0,
            'exposure_limits_removed': 0
        }
    
    def _load_yaml(self, path: Path) -> Dict:
        """Load YAML file."""
        if not path.exists():
            print(f"⚠️  Warning: {path} not found")
            return {}
        
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def _save_yaml(self, path: Path, data: Dict):
        """Save YAML file with proper formatting."""
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, 
                     allow_unicode=True, width=120)
    
    def _build_material_mapping(self) -> Dict[str, str]:
        """Build mapping from material names to IDs."""
        mapping = {}
        
        if 'materials' not in self.materials:
            return mapping
        
        for material_id, material_data in self.materials['materials'].items():
            # Add primary name
            if 'name' in material_data:
                mapping[material_data['name']] = material_id
            
            # Add alternate names
            if 'alternate_names' in material_data:
                for alt_name in material_data['alternate_names']:
                    mapping[alt_name] = material_id
        
        # Add special cases for common variations
        special_cases = {
            'Stainless Steel 316': 'Stainless Steel 316',
            'Stainless Steel 304': 'Stainless Steel 304',
            'Carbon Steel': 'Steel',  # Map to generic Steel if Carbon Steel doesn't exist
            'Mild Steel': 'Steel',
            'Cast Iron': 'Cast Iron',
            'Aluminum Alloy': 'Aluminum',
            'Copper Alloy': 'Copper',
            'Titanium Alloy': 'Titanium',
            'Brass': 'Brass',
            'Bronze': 'Bronze',
            'ABS': 'Acrylic (PMMA)',  # Map ABS to closest plastic
            'PVC': 'Acrylic (PMMA)',  # Map PVC to closest plastic
            'PTFE': 'Acrylic (PMMA)'  # Map PTFE to closest plastic
        }
        mapping.update(special_cases)
        
        return mapping
    
    def _standardize_material_name(self, name: str) -> Optional[str]:
        """Convert material name to standard Material ID."""
        # Try exact match first
        if name in self.material_name_to_id:
            return self.material_name_to_id[name]
        
        # Try case-insensitive match
        name_lower = name.lower()
        for material_name, material_id in self.material_name_to_id.items():
            if material_name.lower() == name_lower:
                return material_id
        
        # No fallback - if not in mapping, return None
        # This prevents creating material IDs that don't exist
        return None
    
    def _get_material_url(self, material_id: str) -> str:
        """Generate URL for material based on category and frontmatter slug."""
        if 'materials' not in self.materials or material_id not in self.materials['materials']:
            return f"/materials/{material_id}"
        
        material = self.materials['materials'][material_id]
        category = material.get('category', 'other')
        subcategory = material.get('subcategory', category)
        
        # Generate slug from material_id (matches frontmatter filename pattern)
        # e.g., "Aluminum" → "aluminum-laser-cleaning"
        slug = material_id.lower().replace(' ', '-').replace('(', '').replace(')', '') + '-laser-cleaning'
        
        return f"/materials/{category}/{subcategory}/{slug}"
    
    def _migrate_material_linkage(self, material_name: str) -> Optional[Dict]:
        """Migrate a single material linkage to new format."""
        material_id = self._standardize_material_name(material_name)
        if not material_id:
            return None
        
        url = self._get_material_url(material_id)
        
        # Use hero image path for material cards
        image_path = url.replace('/materials/', '/images/materials/') + '.jpg'
        
        return {
            'id': material_id,
            'title': material_name,
            'url': url,
            'image': image_path,
            'frequency': 'common',
            'severity': 'moderate',
            'typical_context': 'general'
        }
    
    def _migrate_compound_linkage(self, compound_data: Dict) -> Optional[Dict]:
        """Migrate a single compound linkage to new format."""
        # Extract compound name or ID
        compound_name = compound_data.get('compound', compound_data.get('name', ''))
        if not compound_name:
            return None
        
        # Convert to kebab-case ID
        compound_id = compound_name.lower().replace(' ', '-').replace('(', '').replace(')', '')
        
        # Extract concentration range
        concentration = compound_data.get('concentration_range_mg_m3', 
                                         compound_data.get('typical_concentration', ''))
        
        linkage = {
            'id': compound_id,
            'title': compound_name,
            'url': f"/compounds/{compound_id}",
            'image': f"/images/compounds/{compound_id}.jpg",
            'source': compound_data.get('source', 'thermal_decomposition'),
        }
        
        if concentration:
            linkage['concentration_range_mg_m3'] = str(concentration)
        
        return linkage
    
    def _migrate_standard_linkage(self, citation: str) -> Optional[Dict]:
        """Migrate a regulatory standard citation to new format."""
        # Try to match against known standards
        for standard_id, standard_data in self.standards.get('standards', {}).items():
            standard_name = standard_data.get('name', '')
            if standard_name in citation or citation.startswith(standard_name):
                return {
                    'id': standard_id,
                    'title': standard_name,
                    'url': standard_data.get('url', ''),
                    'image': f"/images/standards/{standard_data.get('organization', 'generic').lower()}-logo.svg",
                    'applicability': 'laser_operation',
                    'requirement': citation
                }
        
        # If not found, create generic entry
        match = re.match(r'^([A-Z]+\s*[\d\-\.]+)', citation)
        if match:
            standard_name = match.group(1).strip()
            standard_id = standard_name.lower().replace(' ', '-')
            
            return {
                'id': standard_id,
                'title': standard_name,
                'url': '',
                'image': '/images/standards/generic-logo.svg',
                'applicability': 'laser_operation',
                'requirement': citation
            }
        
        return None
    
    def _migrate_ppe_linkage(self, ppe_key: str, ppe_value: str) -> Optional[Dict]:
        """Migrate a PPE requirement to new format."""
        # Map legacy keys to new PPE IDs
        ppe_mapping = {
            'eye_protection': {
                'goggles': 'ppe-eye-goggles',
                'face_shield': 'ppe-eye-face-shield',
                'laser_od4': 'ppe-eye-laser-od4',
                'safety_glasses': 'ppe-eye-goggles'
            },
            'eye': {
                'goggles': 'ppe-eye-goggles',
                'face_shield': 'ppe-eye-face-shield',
                'laser_od4': 'ppe-eye-laser-od4'
            },
            'respiratory_protection': {
                'half_face': 'ppe-respiratory-half-face',
                'full_face': 'ppe-respiratory-full-face',
                'papr': 'ppe-respiratory-papr',
                'n95': 'ppe-respiratory-half-face'
            },
            'respiratory': {
                'half_face': 'ppe-respiratory-half-face',
                'full_face': 'ppe-respiratory-full-face',
                'papr': 'ppe-respiratory-papr'
            },
            'skin_protection': {
                'nitrile_gloves': 'ppe-skin-nitrile-gloves',
                'butyl_gloves': 'ppe-skin-butyl-gloves',
                'leather_gloves': 'ppe-skin-leather-gloves',
                'gloves': 'ppe-skin-nitrile-gloves'
            },
            'body_protection': {
                'lab_coat': 'ppe-body-lab-coat',
                'tyvek_suit': 'ppe-body-tyvek-suit',
                'coveralls': 'ppe-body-tyvek-suit'
            }
        }
        
        # Get PPE ID from mapping
        ppe_id = None
        if ppe_key in ppe_mapping:
            category_mapping = ppe_mapping[ppe_key]
            ppe_value_normalized = ppe_value.lower().replace(' ', '_').replace('-', '_')
            ppe_id = category_mapping.get(ppe_value_normalized)
        
        if not ppe_id:
            ppe_id = f"ppe-{ppe_key.replace('_protection', '').replace('_', '-')}-{ppe_value.lower().replace(' ', '-')}"
        
        # Get PPE details from shared data
        ppe_data = self.ppe.get('ppe', {}).get(ppe_id, {})
        ppe_title = ppe_data.get('name', ppe_value.replace('_', ' ').title())
        
        # Determine reason based on PPE type
        reason_mapping = {
            'eye': 'laser_exposure',
            'respiratory': 'toxic_fumes',
            'skin': 'chemical_contact',
            'body': 'chemical_contact'
        }
        
        ppe_category = ppe_key.replace('_protection', '')
        reason = reason_mapping.get(ppe_category, 'particulate_generation')
        
        return {
            'id': ppe_id,
            'title': ppe_title,
            'url': f"/ppe/{ppe_id}",
            'image': f"/images/ppe/{ppe_id}.jpg",
            'reason': reason,
            'required': True,
            'context': 'all_operations'
        }
    
    def migrate_contaminant(self, contaminant_id: str, contaminant_data: Dict) -> Dict:
        """Migrate a single contaminant to relationships format."""
        relationships = {
            'related_materials': [],
            'related_compounds': [],
            'regulatory_compliance': [],
            'ppe_requirements': []
        }
        
        # Migrate valid_materials
        if 'valid_materials' in contaminant_data:
            for material_name in contaminant_data['valid_materials']:
                linkage = self._migrate_material_linkage(material_name)
                if linkage:
                    relationships['related_materials'].append(linkage)
                    self.stats['materials_migrated'] += 1
        
        # Migrate fumes_generated to related_compounds
        if 'fumes_generated' in contaminant_data:
            for compound_data in contaminant_data['fumes_generated']:
                linkage = self._migrate_compound_linkage(compound_data)
                if linkage:
                    relationships['related_compounds'].append(linkage)
                    self.stats['compounds_migrated'] += 1
                    
                    # Count removed exposure limits
                    if 'exposure_limit_mg_m3' in compound_data:
                        self.stats['exposure_limits_removed'] += 1
        
        # Migrate eeat.citations to regulatory_compliance
        if 'eeat' in contaminant_data and 'citations' in contaminant_data['eeat']:
            for citation in contaminant_data['eeat']['citations']:
                linkage = self._migrate_standard_linkage(citation)
                if linkage:
                    relationships['regulatory_compliance'].append(linkage)
                    self.stats['standards_migrated'] += 1
        
        # Migrate ppe_requirements
        if 'ppe_requirements' in contaminant_data:
            for ppe_key, ppe_value in contaminant_data['ppe_requirements'].items():
                linkage = self._migrate_ppe_linkage(ppe_key, ppe_value)
                if linkage:
                    relationships['ppe_requirements'].append(linkage)
                    self.stats['ppe_migrated'] += 1
        
        # Add relationships to contaminant data
        migrated_data = contaminant_data.copy()
        migrated_data['relationships'] = relationships
        
        self.stats['contaminants_processed'] += 1
        
        return migrated_data
    
    def run(self):
        """Run the migration."""
        print("=" * 80)
        print("Domain Linkages Migration")
        print("=" * 80)
        
        if self.dry_run:
            print("🔍 DRY RUN MODE - No files will be modified")
        else:
            print("⚠️  LIVE MODE - Files will be modified")
        
        print()
        
        # Load contaminants
        contaminants_data = self._load_yaml(self.contaminants_path)
        
        if 'contamination_patterns' not in contaminants_data:
            print("❌ Error: No contamination_patterns found in data file")
            return
        
        # Migrate each contaminant
        migrated_contaminants = {}
        
        for contaminant_id, contaminant_data in contaminants_data['contamination_patterns'].items():
            print(f"Processing: {contaminant_id}...", end=' ')
            
            try:
                migrated_data = self.migrate_contaminant(contaminant_id, contaminant_data)
                migrated_contaminants[contaminant_id] = migrated_data
                print("✅")
            except Exception as e:
                print(f"❌ Error: {e}")
                migrated_contaminants[contaminant_id] = contaminant_data
        
        # Update contaminants data
        contaminants_data['contamination_patterns'] = migrated_contaminants
        
        # Save if not dry run
        if not self.dry_run:
            print("\n💾 Saving changes to Contaminants.yaml...")
            self._save_yaml(self.contaminants_path, contaminants_data)
            print("✅ Done")
        
        # Print statistics
        print("\n" + "=" * 80)
        print("Migration Statistics")
        print("=" * 80)
        print(f"Contaminants processed:    {self.stats['contaminants_processed']}")
        print(f"Material linkages:         {self.stats['materials_migrated']}")
        print(f"Compound linkages:         {self.stats['compounds_migrated']}")
        print(f"Standard linkages:         {self.stats['standards_migrated']}")
        print(f"PPE linkages:              {self.stats['ppe_migrated']}")
        print(f"Exposure limits removed:   {self.stats['exposure_limits_removed']}")
        print("=" * 80)
        
        # Show example
        if migrated_contaminants:
            print("\n📝 Example Migrated Contaminant:")
            print("-" * 80)
            
            # Find a good example with multiple linkage types
            example_id = None
            for cid, cdata in migrated_contaminants.items():
                if 'relationships' in cdata:
                    dl = cdata['relationships']
                    if (len(dl.get('related_materials', [])) > 0 and
                        len(dl.get('related_compounds', [])) > 0 and
                        len(dl.get('regulatory_compliance', [])) > 0 and
                        len(dl.get('ppe_requirements', [])) > 0):
                        example_id = cid
                        break
            
            if not example_id:
                example_id = list(migrated_contaminants.keys())[0]
            
            example = migrated_contaminants[example_id]
            print(f"ID: {example_id}")
            print(yaml.dump({'relationships': example.get('relationships', {})}, 
                          default_flow_style=False, sort_keys=False))


def main():
    parser = argparse.ArgumentParser(description='Migrate Contaminants.yaml to relationships format')
    parser.add_argument('--apply', action='store_true', help='Apply changes (default is dry-run)')
    args = parser.parse_args()
    
    migrator = DomainLinkagesMigrator(dry_run=not args.apply)
    migrator.run()


if __name__ == '__main__':
    main()
