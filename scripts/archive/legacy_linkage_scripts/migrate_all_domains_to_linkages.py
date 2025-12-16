#!/usr/bin/env python3
"""
Migrate all domains (Materials, Settings, Compounds) to use domain_linkages structure.

This script adds bidirectional domain_linkages to all entities based on existing relationships.

Author: GitHub Copilot
Date: December 15, 2025
"""

import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional


class AllDomainsMigrator:
    """Migrates all domains to use domain_linkages structure."""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        
        # File paths
        self.materials_path = Path('data/materials/Materials.yaml')
        self.settings_path = Path('data/settings/Settings.yaml')
        self.compounds_path = Path('data/compounds/Compounds.yaml')
        self.contaminants_path = Path('data/contaminants/Contaminants.yaml')
        
        # Load all data
        self.materials_data = self._load_yaml(self.materials_path)
        self.settings_data = self._load_yaml(self.settings_path)
        self.compounds_data = self._load_yaml(self.compounds_path)
        self.contaminants_data = self._load_yaml(self.contaminants_path)
        
        # Stats
        self.stats = {
            'materials_processed': 0,
            'materials_contaminant_links': 0,
            'settings_processed': 0,
            'settings_material_links': 0,
            'settings_contaminant_links': 0,
            'compounds_processed': 0,
            'compounds_contaminant_links': 0
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
    
    def _get_contaminant_url(self, contaminant_id: str) -> str:
        """Generate URL for contaminant based on category."""
        if 'contamination_patterns' not in self.contaminants_data:
            return f"/contaminants/{contaminant_id}"
        
        contaminant = self.contaminants_data['contamination_patterns'].get(contaminant_id, {})
        category = contaminant.get('category', 'other')
        subcategory = contaminant.get('subcategory', category)
        
        return f"/contaminants/{category}/{subcategory}/{contaminant_id}"
    
    def _get_material_url(self, material_id: str) -> str:
        """Generate URL for material based on category."""
        if 'materials' not in self.materials_data:
            return f"/materials/{material_id}"
        
        material = self.materials_data['materials'].get(material_id, {})
        category = material.get('category', 'other')
        subcategory = material.get('subcategory', category)
        
        return f"/materials/{category}/{subcategory}/{material_id}"
    
    def _get_setting_url(self, setting_id: str) -> str:
        """Generate URL for setting based on category."""
        if 'settings' not in self.settings_data:
            return f"/settings/{setting_id}"
        
        setting = self.settings_data['settings'].get(setting_id, {})
        category = setting.get('category', 'other')
        
        return f"/settings/{category}/{setting_id}"
    
    def migrate_materials(self):
        """Add contaminant linkages to materials based on contaminant valid_materials."""
        print("\n" + "=" * 80)
        print("Migrating Materials")
        print("=" * 80)
        
        if 'materials' not in self.materials_data:
            print("⚠️  No materials found")
            return
        
        # Build reverse index: material_id -> list of contaminants
        material_to_contaminants = {}
        
        if 'contamination_patterns' in self.contaminants_data:
            for contaminant_id, contaminant in self.contaminants_data['contamination_patterns'].items():
                if 'domain_linkages' in contaminant:
                    for material_link in contaminant['domain_linkages'].get('related_materials', []):
                        material_id = material_link['id']
                        if material_id not in material_to_contaminants:
                            material_to_contaminants[material_id] = []
                        
                        # Create contaminant linkage
                        contaminant_linkage = {
                            'id': contaminant_id,
                            'title': contaminant.get('name', contaminant_id.replace('-', ' ').title()),
                            'url': self._get_contaminant_url(contaminant_id),
                            'image': self._get_contaminant_url(contaminant_id).replace('/contaminants/', '/images/contaminants/') + '.jpg',
                            'frequency': material_link.get('frequency', 'common'),
                            'severity': material_link.get('severity', 'moderate'),
                            'typical_context': material_link.get('typical_context', 'general')
                        }
                        material_to_contaminants[material_id].append(contaminant_linkage)
        
        # Add domain_linkages to each material
        for material_id, material in self.materials_data['materials'].items():
            print(f"Processing: {material_id}...", end=' ')
            
            if 'domain_linkages' not in material:
                material['domain_linkages'] = {}
            
            # Add related contaminants
            if material_id in material_to_contaminants:
                material['domain_linkages']['related_contaminants'] = material_to_contaminants[material_id]
                self.stats['materials_contaminant_links'] += len(material_to_contaminants[material_id])
            else:
                material['domain_linkages']['related_contaminants'] = []
            
            self.stats['materials_processed'] += 1
            print("✅")
        
        # Save if not dry run
        if not self.dry_run:
            print("\n💾 Saving changes to Materials.yaml...")
            self._save_yaml(self.materials_path, self.materials_data)
            print("✅ Done")
    
    def migrate_settings(self):
        """Add material and contaminant linkages to settings."""
        print("\n" + "=" * 80)
        print("Migrating Settings")
        print("=" * 80)
        
        if 'settings' not in self.settings_data:
            print("⚠️  No settings found")
            return
        
        # For each setting, aggregate materials and their contaminants
        for setting_id, setting in self.settings_data['settings'].items():
            print(f"Processing: {setting_id}...", end=' ')
            
            if 'domain_linkages' not in setting:
                setting['domain_linkages'] = {}
            
            # Get materials that use this setting (from applicable_materials or similar)
            related_materials = []
            related_contaminants = {}
            
            # Check if setting has applicable_materials list
            if 'applicable_materials' in setting:
                for material_name in setting['applicable_materials']:
                    # Find material ID
                    material_id = material_name.lower().replace(' ', '-')
                    
                    if material_id in self.materials_data.get('materials', {}):
                        material = self.materials_data['materials'][material_id]
                        
                        # Add material linkage
                        material_linkage = {
                            'id': material_id,
                            'title': material.get('name', material_name),
                            'url': self._get_material_url(material_id),
                            'image': self._get_material_url(material_id).replace('/materials/', '/images/materials/') + '.jpg',
                            'frequency': 'very_high',
                            'applicability': 'high'
                        }
                        related_materials.append(material_linkage)
                        self.stats['settings_material_links'] += 1
                        
                        # Get contaminants for this material
                        if 'domain_linkages' in material:
                            for contaminant in material['domain_linkages'].get('related_contaminants', []):
                                cont_id = contaminant['id']
                                if cont_id not in related_contaminants:
                                    related_contaminants[cont_id] = contaminant
            
            setting['domain_linkages']['related_materials'] = related_materials
            setting['domain_linkages']['related_contaminants'] = list(related_contaminants.values())
            
            self.stats['settings_processed'] += 1
            self.stats['settings_contaminant_links'] += len(related_contaminants)
            print("✅")
        
        # Save if not dry run
        if not self.dry_run:
            print("\n💾 Saving changes to Settings.yaml...")
            self._save_yaml(self.settings_path, self.settings_data)
            print("✅ Done")
    
    def migrate_compounds(self):
        """Add contaminant linkages to compounds based on contaminant related_compounds."""
        print("\n" + "=" * 80)
        print("Migrating Compounds")
        print("=" * 80)
        
        if 'compounds' not in self.compounds_data:
            print("⚠️  No compounds found")
            return
        
        # Build reverse index: compound_id -> list of contaminants
        compound_to_contaminants = {}
        
        if 'contamination_patterns' in self.contaminants_data:
            for contaminant_id, contaminant in self.contaminants_data['contamination_patterns'].items():
                if 'domain_linkages' in contaminant:
                    for compound_link in contaminant['domain_linkages'].get('related_compounds', []):
                        compound_id = compound_link['id']
                        if compound_id not in compound_to_contaminants:
                            compound_to_contaminants[compound_id] = []
                        
                        # Create contaminant linkage
                        contaminant_linkage = {
                            'id': contaminant_id,
                            'title': contaminant.get('name', contaminant_id.replace('-', ' ').title()),
                            'url': self._get_contaminant_url(contaminant_id),
                            'image': self._get_contaminant_url(contaminant_id).replace('/contaminants/', '/images/contaminants/') + '.jpg',
                            'source': compound_link.get('source', 'thermal_decomposition'),
                            'frequency': 'common'
                        }
                        compound_to_contaminants[compound_id].append(contaminant_linkage)
        
        # Add domain_linkages to each compound
        for compound_id, compound in self.compounds_data['compounds'].items():
            print(f"Processing: {compound_id}...", end=' ')
            
            if 'domain_linkages' not in compound:
                compound['domain_linkages'] = {}
            
            # Add produced_by_contaminants
            if compound_id in compound_to_contaminants:
                compound['domain_linkages']['produced_by_contaminants'] = compound_to_contaminants[compound_id]
                self.stats['compounds_contaminant_links'] += len(compound_to_contaminants[compound_id])
            else:
                compound['domain_linkages']['produced_by_contaminants'] = []
            
            self.stats['compounds_processed'] += 1
            print("✅")
        
        # Save if not dry run
        if not self.dry_run:
            print("\n💾 Saving changes to Compounds.yaml...")
            self._save_yaml(self.compounds_path, self.compounds_data)
            print("✅ Done")
    
    def run(self):
        """Run the migration."""
        print("=" * 80)
        print("All Domains Linkage Migration")
        print("=" * 80)
        
        if self.dry_run:
            print("🔍 DRY RUN MODE - No files will be modified")
        else:
            print("⚠️  LIVE MODE - Files will be modified")
        
        # Migrate each domain
        self.migrate_materials()
        self.migrate_settings()
        self.migrate_compounds()
        
        # Print statistics
        print("\n" + "=" * 80)
        print("Migration Statistics")
        print("=" * 80)
        print(f"Materials processed:           {self.stats['materials_processed']}")
        print(f"  → Contaminant links added:   {self.stats['materials_contaminant_links']}")
        print(f"Settings processed:            {self.stats['settings_processed']}")
        print(f"  → Material links added:      {self.stats['settings_material_links']}")
        print(f"  → Contaminant links added:   {self.stats['settings_contaminant_links']}")
        print(f"Compounds processed:           {self.stats['compounds_processed']}")
        print(f"  → Contaminant links added:   {self.stats['compounds_contaminant_links']}")
        print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description='Migrate all domains to domain_linkages format')
    parser.add_argument('--apply', action='store_true', help='Apply changes (default is dry-run)')
    args = parser.parse_args()
    
    migrator = AllDomainsMigrator(dry_run=not args.apply)
    migrator.run()


if __name__ == '__main__':
    main()
