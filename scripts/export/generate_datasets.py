#!/usr/bin/env python3
"""
Dataset Generation Script

Generates Schema.org datasets in JSON/CSV/TXT formats for both:
1. Materials (with machine settings merged) 
2. Contaminants (with compounds merged)

Architecture:
- Loads directly from source YAML files (independent of frontmatter pipeline)
- Uses domain data loaders for clean data access
- Implements ADR 005 consolidation architecture
- Atomic writes with temp files

Usage:
    # Generate all datasets
    python3 scripts/export/generate_datasets.py
    
    # Generate materials only
    python3 scripts/export/generate_datasets.py --domain materials
    
    # Generate contaminants only
    python3 scripts/export/generate_datasets.py --domain contaminants
    
    # Dry run (no file writes)
    python3 scripts/export/generate_datasets.py --dry-run

Output:
    ../z-beam/public/datasets/materials/*.{json,csv,txt}
    ../z-beam/public/datasets/contaminants/*.{json,csv,txt}
"""

import argparse
import json
import csv
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from domains.materials.data_loader_v2 import MaterialsDataLoader
from domains.contaminants.data_loader_v2 import ContaminantsDataLoader
from domains.compounds.data_loader_v2 import CompoundsDataLoader

logger = logging.getLogger(__name__)


class DatasetGenerator:
    """Generate datasets directly from source YAML data"""
    
    def __init__(self, z_beam_path: str, dry_run: bool = False):
        """
        Initialize dataset generator.
        
        Args:
            z_beam_path: Path to z-beam project root
            dry_run: If True, don't write files
        """
        self.z_beam_path = Path(z_beam_path)
        self.dry_run = dry_run
        
        # Validate paths
        if not self.z_beam_path.exists():
            raise FileNotFoundError(f"z-beam project not found: {z_beam_path}")
        
        # Output directories
        self.materials_dir = self.z_beam_path / "public" / "datasets" / "materials"
        self.contaminants_dir = self.z_beam_path / "public" / "datasets" / "contaminants"
        
        # Load site config
        self.site_config = self._load_site_config()
        
        # Initialize data loaders
        self.materials_loader = MaterialsDataLoader()
        self.contaminants_loader = ContaminantsDataLoader()
        self.compounds_loader = CompoundsDataLoader()
        
        # Statistics
        self.stats = {
            "materials": {"generated": 0, "skipped": 0, "errors": 0},
            "contaminants": {"generated": 0, "skipped": 0, "errors": 0},
            "total_files": 0
        }
        
        # Create output directories
        if not dry_run:
            self.materials_dir.mkdir(parents=True, exist_ok=True)
            self.contaminants_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_site_config(self) -> Dict[str, Any]:
        """Load site configuration from z-beam/site-config.json"""
        config_path = self.z_beam_path / "site-config.json"
        
        default_config = {
            "site": {
                "domain": "https://www.z-beam.com",
                "name": "Z-Beam Laser Cleaning Research Lab"
            }
        }
        
        if not config_path.exists():
            logger.info("Site config not found, using defaults")
            return default_config
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load site config: {e}, using defaults")
            return default_config
    
    def generate_all(self, domain: Optional[str] = None):
        """
        Generate all datasets.
        
        Args:
            domain: If specified, only generate for this domain
        """
        print("=" * 80)
        print("🚀 DATASET GENERATION (Direct from Source YAML)")
        print("=" * 80)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'WRITE'}")
        print(f"Output: {self.z_beam_path / 'public' / 'datasets'}")
        print()
        
        # Generate materials datasets
        if domain is None or domain == "materials":
            self._generate_materials()
        
        # Generate contaminants datasets (with compounds merged)
        if domain is None or domain == "contaminants":
            self._generate_contaminants()
        
        # Print summary
        self._print_summary()
    
    def _generate_materials(self):
        """Generate material datasets (with machine settings merged)"""
        print("📊 Generating Materials Datasets...")
        print("-" * 80)
        
        try:
            # Load materials data
            materials_data = self.materials_loader.load_materials()
            materials = materials_data.get('materials', {})
            
            print(f"Found {len(materials)} materials")
            
            # Generate dataset for each material
            for slug, material_data in materials.items():
                try:
                    # Extract base slug (remove -laser-cleaning suffix)
                    base_slug = slug.replace('-laser-cleaning', '')
                    
                    # Generate all formats
                    self._generate_material_json(base_slug, material_data)
                    self._generate_material_csv(base_slug, material_data)
                    self._generate_material_txt(base_slug, material_data)
                    
                    self.stats["materials"]["generated"] += 1
                    self.stats["total_files"] += 3
                    
                    if not self.dry_run:
                        logger.info(f"✅ Generated {base_slug}")
                    
                except Exception as e:
                    self.stats["materials"]["errors"] += 1
                    logger.error(f"❌ Error generating {slug}: {e}")
                    print(f"❌ Error: {slug}")
            
            print()
            
        except Exception as e:
            logger.error(f"Fatal error loading materials: {e}")
            print(f"❌ Fatal error loading materials: {e}")
    
    def _generate_contaminants(self):
        """Generate contaminant datasets (with compounds merged)"""
        print("🧪 Generating Contaminants Datasets...")
        print("-" * 80)
        
        try:
            # Load contaminants data
            contaminants_data = self.contaminants_loader.load_patterns()
            
            # Load compounds data for merging
            compounds_data = self.compounds_loader.load_compounds()
            compounds = compounds_data.get('compounds', {})
            
            print(f"Found {len(contaminants_data)} contaminants, {len(compounds)} compounds")
            
            # Generate dataset for each contaminant
            for pattern_id, pattern_data in contaminants_data.items():
                try:
                    # Merge compound data
                    enriched_data = self._merge_compounds_into_contaminant(
                        pattern_data, compounds
                    )
                    
                    # Generate all formats
                    self._generate_contaminant_json(pattern_id, enriched_data)
                    self._generate_contaminant_csv(pattern_id, enriched_data)
                    self._generate_contaminant_txt(pattern_id, enriched_data)
                    
                    self.stats["contaminants"]["generated"] += 1
                    self.stats["total_files"] += 3
                    
                    if not self.dry_run:
                        logger.info(f"✅ Generated {pattern_id}")
                    
                except Exception as e:
                    self.stats["contaminants"]["errors"] += 1
                    logger.error(f"❌ Error generating {pattern_id}: {e}")
                    print(f"❌ Error: {pattern_id}")
            
            print()
            
        except Exception as e:
            logger.error(f"Fatal error loading contaminants: {e}")
            print(f"❌ Fatal error loading contaminants: {e}")
    
    def _merge_compounds_into_contaminant(
        self,
        contaminant_data: Dict[str, Any],
        compounds: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge compound data into contaminant dataset.
        
        Per ADR 005: Contaminant datasets must include compounds array
        with chemical composition, safety metrics, PPE requirements.
        
        Args:
            contaminant_data: Contaminant pattern data
            compounds: All compounds data
        
        Returns:
            Enriched contaminant data with compounds merged
        """
        enriched = contaminant_data.copy()
        
        # Get related compounds (if specified in contaminant)
        related_compounds = contaminant_data.get('related_compounds', [])
        
        # Build compounds array
        compounds_array = []
        for compound_id in related_compounds:
            if compound_id in compounds:
                compound = compounds[compound_id]
                compounds_array.append({
                    "id": compound_id,
                    "name": compound.get('name', compound_id),
                    "formula": compound.get('chemical_formula', ''),
                    "cas_number": compound.get('cas_number', ''),
                    "composition": compound.get('composition', {}),
                    "safety": compound.get('safety', {}),
                    "ppe_requirements": compound.get('ppe_requirements', [])
                })
        
        enriched['compounds'] = compounds_array
        return enriched
    
    def _generate_material_json(self, slug: str, material_data: Dict[str, Any]):
        """Generate Schema.org Dataset JSON for material"""
        output_path = self.materials_dir / f"{slug}.json"
        
        if self.dry_run:
            print(f"  [DRY RUN] Would write: {output_path.name}")
            return
        
        dataset = self._build_material_dataset_json(slug, material_data)
        
        # Atomic write
        temp_path = output_path.with_suffix('.json.tmp')
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        temp_path.rename(output_path)
    
    def _build_material_dataset_json(
        self,
        slug: str,
        material_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build Schema.org Dataset structure for material"""
        site_domain = self.site_config['site']['domain']
        site_name = self.site_config['site']['name']
        
        name = material_data.get('name', slug.replace('-', ' ').title())
        description = material_data.get('description', f"Comprehensive laser cleaning dataset for {name}")
        
        # Build dataset
        return {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "@id": f"{site_domain}/materials/{slug}#dataset",
            "name": f"{name} Laser Cleaning Dataset",
            "description": description,
            "version": "1.0",
            "dateModified": datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            "datePublished": material_data.get('date_published', datetime.now(timezone.utc).strftime('%Y-%m-%d')),
            "license": {
                "@type": "CreativeWork",
                "name": "Creative Commons Attribution 4.0 International",
                "url": "https://creativecommons.org/licenses/by/4.0/"
            },
            "creator": {
                "@type": "Organization",
                "name": site_name,
                "url": site_domain
            },
            "publisher": {
                "@type": "Organization",
                "name": site_name,
                "url": site_domain
            },
            "keywords": self._extract_material_keywords(material_data, name),
            "variableMeasured": self._build_variable_measured_materials(material_data),
            "distribution": [
                {
                    "@type": "DataDownload",
                    "encodingFormat": "application/json",
                    "contentUrl": f"{site_domain}/datasets/materials/{slug}.json"
                },
                {
                    "@type": "DataDownload",
                    "encodingFormat": "text/csv",
                    "contentUrl": f"{site_domain}/datasets/materials/{slug}.csv"
                },
                {
                    "@type": "DataDownload",
                    "encodingFormat": "text/plain",
                    "contentUrl": f"{site_domain}/datasets/materials/{slug}.txt"
                }
            ]
        }
    
    def _build_variable_measured_materials(
        self,
        material_data: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Build variableMeasured array for materials (min 20 required)"""
        variables = []
        
        # Extract nested properties from category structure
        # Properties are organized: properties -> category -> property_name -> {value, unit, min, max}
        properties = material_data.get('properties', {})
        for category_name, category_data in properties.items():
            if isinstance(category_data, dict):
                # Iterate through properties within this category
                for prop_name, prop_value in category_data.items():
                    # Skip metadata fields
                    if prop_name in ['label', 'description', 'percentage']:
                        continue
                    # Check if this is a property with value/unit
                    if isinstance(prop_value, dict) and ('value' in prop_value or 'unit' in prop_value):
                        variables.append({
                            "@type": "PropertyValue",
                            "name": prop_name.replace('_', ' ').title(),
                            "description": f"{category_data.get('label', category_name)}: {prop_name.replace('_', ' ')}",
                            "value": str(prop_value.get('value', '')),
                            "unitText": prop_value.get('unit', ''),
                            "minValue": prop_value.get('min'),
                            "maxValue": prop_value.get('max')
                        })
        
        # Machine settings from Settings.yaml integration
        # Note: Machine settings may not be present in all materials
        machine_settings = material_data.get('machine_settings', {})
        if machine_settings:
            for param_name, param_value in machine_settings.items():
                if isinstance(param_value, dict):
                    variables.append({
                        "@type": "PropertyValue",
                        "name": param_name.replace('_', ' ').title(),
                        "description": f"Laser cleaning parameter: {param_name.replace('_', ' ')}",
                        "value": str(param_value.get('value', '')),
                        "unitText": param_value.get('unit', ''),
                        "minValue": param_value.get('min'),
                        "maxValue": param_value.get('max')
                    })
        
        return variables[:50]  # Cap at 50 to include all available data
    
    def _extract_material_keywords(
        self,
        material_data: Dict[str, Any],
        name: str
    ) -> List[str]:
        """Extract keywords for material dataset"""
        keywords = [
            name,
            "laser cleaning",
            "material properties",
            "industrial cleaning",
            "surface preparation"
        ]
        
        # Add category
        category = material_data.get('category', '')
        if category:
            keywords.append(category)
        
        # Add subcategory
        subcategory = material_data.get('subcategory', '')
        if subcategory:
            keywords.append(subcategory)
        
        return keywords
    
    def _generate_material_csv(self, slug: str, material_data: Dict[str, Any]):
        """Generate CSV dataset for material"""
        output_path = self.materials_dir / f"{slug}.csv"
        
        if self.dry_run:
            return
        
        # Build rows
        rows = []
        
        # Machine settings (appear FIRST per ADR 005)
        machine_settings = material_data.get('machine_settings', {})
        if machine_settings:
            for param_name, param_value in machine_settings.items():
                if isinstance(param_value, dict):
                    rows.append({
                        "Category": "Machine Setting",
                        "Property": param_name,
                        "Value": param_value.get('value', ''),
                        "Unit": param_value.get('unit', ''),
                        "Min": param_value.get('min', ''),
                        "Max": param_value.get('max', '')
                    })
        
        # Material properties (nested in categories)
        properties = material_data.get('properties', {})
        for category_name, category_data in properties.items():
            if isinstance(category_data, dict):
                category_label = category_data.get('label', category_name)
                for prop_name, prop_value in category_data.items():
                    # Skip metadata fields
                    if prop_name in ['label', 'description', 'percentage']:
                        continue
                    # Add property row
                    if isinstance(prop_value, dict) and ('value' in prop_value or 'unit' in prop_value):
                        rows.append({
                            "Category": category_label,
                            "Property": prop_name,
                            "Value": prop_value.get('value', ''),
                            "Unit": prop_value.get('unit', ''),
                            "Min": prop_value.get('min', ''),
                            "Max": prop_value.get('max', '')
                        })
        
        # Atomic write
        temp_path = output_path.with_suffix('.csv.tmp')
        with open(temp_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Category", "Property", "Value", "Unit", "Min", "Max"])
            writer.writeheader()
            writer.writerows(rows)
        temp_path.rename(output_path)
    
    def _generate_material_txt(self, slug: str, material_data: Dict[str, Any]):
        """Generate TXT dataset for material"""
        output_path = self.materials_dir / f"{slug}.txt"
        
        if self.dry_run:
            return
        
        name = material_data.get('name', slug.replace('-', ' ').title())
        description = material_data.get('description', '')
        
        lines = [
            f"DATASET: {name} Laser Cleaning Parameters",
            "=" * 80,
            "",
            "DESCRIPTION:",
            description,
            "",
            "MACHINE SETTINGS:",
            "-" * 80
        ]
        
        # Machine settings
        machine_settings = material_data.get('machine_settings', {})
        if machine_settings:
            for param_name, param_value in machine_settings.items():
                if isinstance(param_value, dict):
                    value = param_value.get('value', '')
                    unit = param_value.get('unit', '')
                    min_val = param_value.get('min', '')
                    max_val = param_value.get('max', '')
                    value_str = f"{value} {unit}".strip()
                    if min_val and max_val:
                        value_str += f" (range: {min_val}-{max_val} {unit})"
                    lines.append(f"  {param_name}: {value_str}")
        else:
            lines.append("  (No machine settings available)")
        
        lines.extend(["", "MATERIAL PROPERTIES:", "-" * 80])
        
        # Material properties (nested in categories)
        properties = material_data.get('properties', {})
        for category_name, category_data in properties.items():
            if isinstance(category_data, dict):
                category_label = category_data.get('label', category_name)
                lines.append(f"\n{category_label}:")
                for prop_name, prop_value in category_data.items():
                    # Skip metadata fields
                    if prop_name in ['label', 'description', 'percentage']:
                        continue
                    # Add property
                    if isinstance(prop_value, dict) and ('value' in prop_value or 'unit' in prop_value):
                        value = prop_value.get('value', '')
                        unit = prop_value.get('unit', '')
                        min_val = prop_value.get('min', '')
                        max_val = prop_value.get('max', '')
                        value_str = f"{value} {unit}".strip()
                        if min_val and max_val:
                            value_str += f" (range: {min_val}-{max_val} {unit})"
                        lines.append(f"  {prop_name}: {value_str}")
        
        # Atomic write
        temp_path = output_path.with_suffix('.txt.tmp')
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        temp_path.rename(output_path)
    
    def _generate_contaminant_json(self, pattern_id: str, pattern_data: Dict[str, Any]):
        """Generate Schema.org Dataset JSON for contaminant"""
        output_path = self.contaminants_dir / f"{pattern_id}.json"
        
        if self.dry_run:
            print(f"  [DRY RUN] Would write: {output_path.name}")
            return
        
        dataset = self._build_contaminant_dataset_json(pattern_id, pattern_data)
        
        # Atomic write
        temp_path = output_path.with_suffix('.json.tmp')
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        temp_path.rename(output_path)
    
    def _build_contaminant_dataset_json(
        self,
        pattern_id: str,
        pattern_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build Schema.org Dataset structure for contaminant"""
        site_domain = self.site_config['site']['domain']
        site_name = self.site_config['site']['name']
        
        name = pattern_data.get('name', pattern_id.replace('_', ' ').title())
        description = pattern_data.get('description', f"Comprehensive contamination removal dataset for {name}")
        
        # Build dataset
        return {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "@id": f"{site_domain}/contaminants/{pattern_id}#dataset",
            "name": f"{name} Contamination Dataset",
            "description": description,
            "version": "1.0",
            "dateModified": datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            "datePublished": pattern_data.get('date_published', datetime.now(timezone.utc).strftime('%Y-%m-%d')),
            "license": {
                "@type": "CreativeWork",
                "name": "Creative Commons Attribution 4.0 International",
                "url": "https://creativecommons.org/licenses/by/4.0/"
            },
            "creator": {
                "@type": "Organization",
                "name": site_name,
                "url": site_domain
            },
            "publisher": {
                "@type": "Organization",
                "name": site_name,
                "url": site_domain
            },
            "keywords": self._extract_contaminant_keywords(pattern_data, name),
            "variableMeasured": self._build_variable_measured_contaminants(pattern_data),
            "distribution": [
                {
                    "@type": "DataDownload",
                    "encodingFormat": "application/json",
                    "contentUrl": f"{site_domain}/datasets/contaminants/{pattern_id}.json"
                },
                {
                    "@type": "DataDownload",
                    "encodingFormat": "text/csv",
                    "contentUrl": f"{site_domain}/datasets/contaminants/{pattern_id}.csv"
                },
                {
                    "@type": "DataDownload",
                    "encodingFormat": "text/plain",
                    "contentUrl": f"{site_domain}/datasets/contaminants/{pattern_id}.txt"
                }
            ]
        }
    
    def _build_variable_measured_contaminants(
        self,
        pattern_data: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Build variableMeasured array for contaminants (min 20 required)"""
        variables = []
        
        # Contamination properties
        properties = pattern_data.get('properties', {})
        for prop_name in properties.keys():
            variables.append({
                "@type": "PropertyValue",
                "name": prop_name.replace('_', ' ').title(),
                "description": f"Contamination property: {prop_name}"
            })
        
        # Removal parameters
        removal = pattern_data.get('laser_removal', {})
        for param_name in removal.keys():
            variables.append({
                "@type": "PropertyValue",
                "name": param_name.replace('_', ' ').title(),
                "description": f"Removal parameter: {param_name}"
            })
        
        # Compounds
        compounds = pattern_data.get('compounds', [])
        for compound in compounds:
            compound_name = compound.get('name', 'Unknown')
            variables.append({
                "@type": "PropertyValue",
                "name": f"Compound: {compound_name}",
                "description": f"Chemical compound: {compound_name}"
            })
        
        # Add standard variables if needed
        standard_vars = [
            ("Adhesion Strength", "Bond strength to substrate"),
            ("Thickness", "Typical contamination layer thickness"),
            ("Removal Efficiency", "Cleaning effectiveness percentage"),
            ("Surface Damage Risk", "Risk of substrate damage"),
            ("PPE Requirements", "Personal protective equipment")
        ]
        
        for var_name, var_desc in standard_vars:
            if len(variables) < 20:
                variables.append({
                    "@type": "PropertyValue",
                    "name": var_name,
                    "description": var_desc
                })
        
        return variables[:30]  # Cap at 30
    
    def _extract_contaminant_keywords(
        self,
        pattern_data: Dict[str, Any],
        name: str
    ) -> List[str]:
        """Extract keywords for contaminant dataset"""
        keywords = [
            name,
            "contamination removal",
            "laser cleaning",
            "surface cleaning",
            "industrial decontamination"
        ]
        
        # Add category
        category = pattern_data.get('category', '')
        if category:
            keywords.append(category)
        
        return keywords
    
    def _generate_contaminant_csv(self, pattern_id: str, pattern_data: Dict[str, Any]):
        """Generate CSV dataset for contaminant"""
        output_path = self.contaminants_dir / f"{pattern_id}.csv"
        
        if self.dry_run:
            return
        
        rows = []
        
        # Contamination properties
        properties = pattern_data.get('properties', {})
        for prop_name, prop_value in properties.items():
            if isinstance(prop_value, dict):
                rows.append({
                    "Category": "Contamination Property",
                    "Property": prop_name,
                    "Value": prop_value.get('value', ''),
                    "Unit": prop_value.get('unit', ''),
                    "Notes": prop_value.get('notes', '')
                })
        
        # Removal parameters
        removal = pattern_data.get('laser_removal', {})
        for param_name, param_value in removal.items():
            if isinstance(param_value, dict):
                rows.append({
                    "Category": "Removal Parameter",
                    "Property": param_name,
                    "Value": param_value.get('value', ''),
                    "Unit": param_value.get('unit', ''),
                    "Notes": param_value.get('notes', '')
                })
        
        # Atomic write
        temp_path = output_path.with_suffix('.csv.tmp')
        with open(temp_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Category", "Property", "Value", "Unit", "Notes"])
            writer.writeheader()
            writer.writerows(rows)
        temp_path.rename(output_path)
    
    def _generate_contaminant_txt(self, pattern_id: str, pattern_data: Dict[str, Any]):
        """Generate TXT dataset for contaminant"""
        output_path = self.contaminants_dir / f"{pattern_id}.txt"
        
        if self.dry_run:
            return
        
        name = pattern_data.get('name', pattern_id.replace('_', ' ').title())
        description = pattern_data.get('description', '')
        
        lines = [
            f"DATASET: {name} Contamination Removal",
            "=" * 80,
            "",
            "DESCRIPTION:",
            description,
            "",
            "CONTAMINATION PROPERTIES:",
            "-" * 80
        ]
        
        # Properties
        properties = pattern_data.get('properties', {})
        for prop_name, prop_value in properties.items():
            if isinstance(prop_value, dict):
                value_str = f"{prop_value.get('value', '')} {prop_value.get('unit', '')}".strip()
                lines.append(f"  {prop_name}: {value_str}")
        
        lines.extend(["", "REMOVAL PARAMETERS:", "-" * 80])
        
        # Removal parameters
        removal = pattern_data.get('laser_removal', {})
        for param_name, param_value in removal.items():
            if isinstance(param_value, dict):
                value_str = f"{param_value.get('value', '')} {param_value.get('unit', '')}".strip()
                lines.append(f"  {param_name}: {value_str}")
        
        # Compounds
        compounds = pattern_data.get('compounds', [])
        if compounds:
            lines.extend(["", "CHEMICAL COMPOUNDS:", "-" * 80])
            for compound in compounds:
                compound_name = compound.get('name', 'Unknown')
                formula = compound.get('formula', '')
                lines.append(f"  {compound_name} ({formula})")
        
        # Atomic write
        temp_path = output_path.with_suffix('.txt.tmp')
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        temp_path.rename(output_path)
    
    def _print_summary(self):
        """Print generation summary"""
        print("=" * 80)
        print("📊 GENERATION SUMMARY")
        print("=" * 80)
        
        mat = self.stats["materials"]
        cont = self.stats["contaminants"]
        
        print(f"Materials:    {mat['generated']:3d} generated, {mat['errors']:3d} errors")
        print(f"Contaminants: {cont['generated']:3d} generated, {cont['errors']:3d} errors")
        print(f"Total Files:  {self.stats['total_files']:3d} ({self.stats['total_files']//3} datasets × 3 formats)")
        print()
        
        if self.dry_run:
            print("🔍 DRY RUN - No files were written")
        else:
            print(f"✅ Datasets written to:")
            print(f"   {self.materials_dir}")
            print(f"   {self.contaminants_dir}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate datasets directly from source YAML data"
    )
    parser.add_argument(
        '--domain',
        choices=['materials', 'contaminants'],
        help='Generate only for specific domain'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run (no file writes)'
    )
    parser.add_argument(
        '--z-beam-path',
        default='../z-beam',
        help='Path to z-beam project (default: ../z-beam)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s: %(message)s'
    )
    
    try:
        # Initialize generator
        generator = DatasetGenerator(
            z_beam_path=args.z_beam_path,
            dry_run=args.dry_run
        )
        
        # Generate datasets
        generator.generate_all(domain=args.domain)
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
