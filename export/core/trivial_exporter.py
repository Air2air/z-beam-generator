#!/usr/bin/env python3
"""
Trivial Frontmatter Exporter

PURPOSE: Export Materials.yaml data to frontmatter YAML files.
DESIGN: Simple YAML-to-YAML copy + Categories.yaml metadata - NO API, NO validation.

OPERATIONS:
1. Copy material-specific data from Materials.yaml (100% complete, validated)
2. Add category metadata from Categories.yaml (for reference only, NO FALLBACK RANGES)
3. Write to frontmatter YAML file

All complex operations (AI generation, validation, quality scoring, property research)
happen on Materials.yaml ONLY. This exporter just copies the complete data.

NO FALLBACK RANGES - Materials.yaml must have 100% complete data.

Performance: Should take SECONDS for all 132 materials, not minutes.
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any
from domains.materials.materials_cache import load_materials_cached
from domains.materials.data_loader import get_material_challenges
from shared.utils.core.slug_utils import create_material_slug
from export.utils.numeric_formatting import format_numeric_value

logger = logging.getLogger(__name__)

# Property categorization for hierarchical structure
MATERIAL_CHARACTERISTICS_PROPS = [
    'density', 'hardness', 'tensileStrength', 'compressiveStrength',
    'flexuralStrength', 'fractureToughness', 'youngsModulus',
    'specificHeat', 'thermalConductivity', 'thermalExpansion',
    'electricalConductivity', 'electricalResistivity', 'corrosionResistance',
    'oxidationResistance', 'porosity', 'surfaceRoughness'
]

LASER_INTERACTION_PROPS = [
    'laserAbsorption', 'laserReflectivity', 'absorptivity', 'reflectivity',
    'absorptionCoefficient', 'ablationThreshold', 'laserDamageThreshold',
    'thermalDestruction', 'thermalDestructionPoint', 'thermalDiffusivity',
    'thermalShockResistance', 'meltingPoint', 'boilingPoint', 'vaporPressure'
]

# Category defaults for thermal properties (used when material-specific data missing)
# Values in mm²/s for thermalDiffusivity, J/cm² for thresholds
THERMAL_CATEGORY_DEFAULTS = {
    ('metal', 'precious'): {
        'thermalDiffusivity': 150.0,
        'thermalConductivity': 350.0,
        'thermalDestructionPoint': 1337,
        'destructionType': 'melting',
        'laserDamageThreshold': 12.0,
        'ablationThreshold': 3.0,
    },
    ('metal', 'non-ferrous'): {
        'thermalDiffusivity': 70.0,
        'thermalConductivity': 200.0,
        'thermalDestructionPoint': 1000,
        'destructionType': 'melting',
        'laserDamageThreshold': 8.0,
        'ablationThreshold': 2.0,
    },
    ('metal', 'ferrous'): {
        'thermalDiffusivity': 8.0,
        'thermalConductivity': 50.0,
        'thermalDestructionPoint': 1800,
        'destructionType': 'melting',
        'laserDamageThreshold': 12.0,
        'ablationThreshold': 4.0,
    },
    ('wood', 'hardwood'): {
        'thermalDiffusivity': 0.12,
        'thermalConductivity': 0.17,
        'thermalDestructionPoint': 523,
        'destructionType': 'charring',
        'laserDamageThreshold': 3.5,
        'ablationThreshold': 1.0,
    },
    ('wood', 'softwood'): {
        'thermalDiffusivity': 0.10,
        'thermalConductivity': 0.12,
        'thermalDestructionPoint': 513,
        'destructionType': 'charring',
        'laserDamageThreshold': 2.5,
        'ablationThreshold': 0.8,
    },
    ('plastic', 'thermoplastic'): {
        'thermalDiffusivity': 0.12,
        'thermalConductivity': 0.20,
        'thermalDestructionPoint': 473,
        'destructionType': 'softening',
        'laserDamageThreshold': 2.0,
        'ablationThreshold': 0.8,
    },
    ('plastic', 'thermoset'): {
        'thermalDiffusivity': 0.15,
        'thermalConductivity': 0.30,
        'thermalDestructionPoint': 573,
        'destructionType': 'decomposition',
        'laserDamageThreshold': 4.0,
        'ablationThreshold': 1.5,
    },
    ('composite', 'carbon-fiber'): {
        'thermalDiffusivity': 15.0,
        'thermalConductivity': 50.0,
        'thermalDestructionPoint': 673,
        'destructionType': 'decomposition',
        'laserDamageThreshold': 5.0,
        'ablationThreshold': 2.0,
    },
    ('composite', 'fiberglass'): {
        'thermalDiffusivity': 0.22,
        'thermalConductivity': 0.40,
        'thermalDestructionPoint': 573,
        'destructionType': 'decomposition',
        'laserDamageThreshold': 3.5,
        'ablationThreshold': 1.5,
    },
    ('stone', 'natural'): {
        'thermalDiffusivity': 1.2,
        'thermalConductivity': 2.5,
        'thermalDestructionPoint': 1400,
        'destructionType': 'melting',
        'laserDamageThreshold': 15.0,
        'ablationThreshold': 5.0,
    },
    ('ceramic', 'traditional'): {
        'thermalDiffusivity': 1.0,
        'thermalConductivity': 2.0,
        'thermalDestructionPoint': 1500,
        'destructionType': 'melting',
        'laserDamageThreshold': 20.0,
        'ablationThreshold': 6.0,
    },
    ('ceramic', 'advanced'): {
        'thermalDiffusivity': 12.0,
        'thermalConductivity': 70.0,
        'thermalDestructionPoint': 2700,
        'destructionType': 'melting',
        'laserDamageThreshold': 35.0,
        'ablationThreshold': 12.0,
    },
    ('glass', 'standard'): {
        'thermalDiffusivity': 0.5,
        'thermalConductivity': 1.0,
        'thermalDestructionPoint': 1000,
        'destructionType': 'softening',
        'laserDamageThreshold': 8.0,
        'ablationThreshold': 3.0,
    },
    ('rubber', None): {
        'thermalDiffusivity': 0.12,
        'thermalConductivity': 0.16,
        'thermalDestructionPoint': 523,
        'destructionType': 'decomposition',
        'laserDamageThreshold': 2.5,
        'ablationThreshold': 1.0,
    },
    ('textile', 'natural'): {
        'thermalDiffusivity': 0.07,
        'thermalConductivity': 0.07,
        'thermalDestructionPoint': 503,
        'destructionType': 'charring',
        'laserDamageThreshold': 2.0,
        'ablationThreshold': 0.5,
    },
    ('textile', 'synthetic'): {
        'thermalDiffusivity': 0.10,
        'thermalConductivity': 0.15,
        'thermalDestructionPoint': 523,
        'destructionType': 'melting',
        'laserDamageThreshold': 3.0,
        'ablationThreshold': 1.0,
    },
}

# Service Offering configuration for SEO rich snippets
# Estimated hours based on material difficulty (from SERVICE_OFFERING_FRONTMATTER_SPEC.md)
SERVICE_OFFERING_HOURS = {
    # Easy materials: 2-3 hours typical
    'easy': {'min': 1, 'typical': 3},
    # Standard materials: 3-5 hours typical  
    'standard': {'min': 1, 'typical': 4},
    # Complex materials: 5-8 hours typical
    'complex': {'min': 2, 'typical': 6},
    # Delicate materials: 2-3 hours typical
    'delicate': {'min': 1, 'typical': 2},
    # Heavy materials: 4-8 hours typical
    'heavy': {'min': 2, 'typical': 6},
    # Precision materials: 2-4 hours typical
    'precision': {'min': 1, 'typical': 3},
    # Careful materials (wood): 2-4 hours typical
    'careful': {'min': 1, 'typical': 3},
}

# Material to difficulty mapping based on category/subcategory
# Actual subcategories from Materials.yaml:
# metal: non-ferrous(17), specialty(11), alloy(11), lanthanide(7), ferrous(4), elemental(4), scandium-group(1)
# stone: sedimentary(14), metamorphic(3), igneous(2)
# plastic: thermoplastic(11), general(5)
# composite: fiber-reinforced(11)
# ceramic: oxide(7), technical(4), carbide(1)
# glass: soda-lime(9), specialty-glass(2)
# wood: hardwood(18), softwood(3)
# concrete: concrete(2), structural(2)
# rare-earth: lanthanide, scandium-group, compound
MATERIAL_DIFFICULTY = {
    # Easy - Non-ferrous metals (aluminum, copper, brass)
    ('metal', 'non-ferrous'): 'easy',
    ('metal', 'precious'): 'easy',
    ('metal', 'elemental'): 'easy',  # Pure metals like copper, zinc
    # Standard - Ferrous metals and common alloys
    ('metal', 'ferrous'): 'standard',
    ('metal', 'alloy'): 'standard',
    # Complex - Specialty/high-performance metals (titanium, inconel, etc.)
    ('metal', 'specialty'): 'complex',
    ('metal', 'refractory'): 'complex',
    ('metal', 'superalloy'): 'complex',
    ('metal', 'lanthanide'): 'complex',
    ('metal', 'scandium-group'): 'complex',
    # Delicate - Plastics and composites
    ('plastic', 'thermoplastic'): 'delicate',
    ('plastic', 'thermoset'): 'delicate',
    ('plastic', 'general'): 'delicate',
    ('composite', 'fiber-reinforced'): 'delicate',
    ('composite', 'carbon-fiber'): 'delicate',
    ('composite', 'fiberglass'): 'delicate',
    ('composite', None): 'delicate',
    # Heavy - Stone and masonry
    ('stone', 'sedimentary'): 'heavy',
    ('stone', 'metamorphic'): 'heavy',
    ('stone', 'igneous'): 'heavy',
    ('stone', 'natural'): 'heavy',
    ('stone', 'engineered'): 'heavy',
    ('concrete', 'concrete'): 'heavy',
    ('concrete', 'structural'): 'heavy',
    ('concrete', None): 'heavy',
    ('masonry', None): 'heavy',
    # Precision - Glass and ceramics
    ('glass', 'soda-lime'): 'precision',
    ('glass', 'specialty-glass'): 'precision',
    ('glass', 'standard'): 'precision',
    ('glass', 'optical'): 'precision',
    ('ceramic', 'oxide'): 'precision',
    ('ceramic', 'technical'): 'precision',
    ('ceramic', 'carbide'): 'precision',
    ('ceramic', 'traditional'): 'precision',
    ('ceramic', 'advanced'): 'precision',
    # Careful - Wood
    ('wood', 'hardwood'): 'careful',
    ('wood', 'softwood'): 'careful',
    # Rubber and textiles
    ('rubber', 'natural'): 'delicate',
    ('rubber', 'coating'): 'delicate',
    ('rubber', None): 'delicate',
    ('textile', 'natural'): 'delicate',
    ('textile', 'synthetic'): 'delicate',
    # Rare earth elements
    ('rare-earth', 'lanthanide'): 'complex',
    ('rare-earth', 'scandium-group'): 'complex',
    ('rare-earth', 'compound'): 'complex',
}

# Target contaminants by category (from SERVICE_OFFERING_FRONTMATTER_SPEC.md)
# Extended to cover all actual subcategories in Materials.yaml
TARGET_CONTAMINANTS = {
    # Ferrous metals
    ('metal', 'ferrous'): [
        'Rust and corrosion',
        'Mill scale',
        'Paint and coatings',
        'Weld discoloration',
        'Heat treatment scale'
    ],
    # Non-ferrous metals (aluminum, copper, etc.)
    ('metal', 'non-ferrous'): [
        'Oxide layer',
        'Paint and coatings',
        'Grease and oils',
        'Anodizing removal',
        'Tarnish and patina'
    ],
    ('metal', 'precious'): [
        'Oxide layer',
        'Tarnish and patina',
        'Surface contamination',
        'Polishing residue'
    ],
    ('metal', 'elemental'): [
        'Oxide layer',
        'Tarnish and patina',
        'Surface contamination',
        'Grease and oils'
    ],
    # Specialty metals (titanium, inconel, etc.)
    ('metal', 'specialty'): [
        'Oxide scale',
        'Heat discoloration',
        'Alpha case layer',
        'Thermal barrier coatings'
    ],
    ('metal', 'refractory'): [
        'Oxide scale',
        'Heat discoloration',
        'Alpha case layer',
        'Thermal barrier coatings'
    ],
    ('metal', 'superalloy'): [
        'Oxide scale',
        'Heat discoloration',
        'Thermal barrier coatings',
        'Surface contamination'
    ],
    ('metal', 'alloy'): [
        'Oxide layer',
        'Paint and coatings',
        'Mill scale',
        'Surface contamination'
    ],
    ('metal', 'lanthanide'): [
        'Oxide layer',
        'Surface contamination',
        'Atmospheric deposits',
        'Processing residue'
    ],
    ('metal', 'scandium-group'): [
        'Oxide layer',
        'Surface contamination',
        'Atmospheric deposits',
        'Processing residue'
    ],
    # Plastics and composites
    ('plastic', 'thermoplastic'): [
        'Surface contamination',
        'Mold release agents',
        'Adhesive residue',
        'Paint overspray'
    ],
    ('plastic', 'thermoset'): [
        'Surface contamination',
        'Mold release agents',
        'Adhesive residue',
        'Paint overspray'
    ],
    ('plastic', 'general'): [
        'Surface contamination',
        'Mold release agents',
        'Adhesive residue',
        'Paint overspray'
    ],
    ('composite', 'fiber-reinforced'): [
        'Surface contamination',
        'Mold release agents',
        'Adhesive residue',
        'Matrix surface prep'
    ],
    ('composite', 'carbon-fiber'): [
        'Surface contamination',
        'Mold release agents',
        'Adhesive residue',
        'Matrix surface prep'
    ],
    ('composite', 'fiberglass'): [
        'Surface contamination',
        'Gelcoat oxidation',
        'Paint and coatings',
        'Adhesive residue'
    ],
    # Stone and masonry
    ('stone', 'sedimentary'): [
        'Efflorescence',
        'Paint and graffiti',
        'Biological growth',
        'Weathering deposits'
    ],
    ('stone', 'metamorphic'): [
        'Efflorescence',
        'Paint and graffiti',
        'Biological growth',
        'Soot and smoke damage'
    ],
    ('stone', 'igneous'): [
        'Surface contamination',
        'Paint and coatings',
        'Biological growth',
        'Weathering deposits'
    ],
    ('stone', 'natural'): [
        'Efflorescence',
        'Paint and graffiti',
        'Biological growth',
        'Soot and smoke damage'
    ],
    ('stone', 'engineered'): [
        'Surface contamination',
        'Paint and coatings',
        'Adhesive residue',
        'Staining'
    ],
    ('concrete', 'concrete'): [
        'Efflorescence',
        'Paint and coatings',
        'Oil stains',
        'Biological growth'
    ],
    ('concrete', 'structural'): [
        'Efflorescence',
        'Paint and coatings',
        'Oil stains',
        'Surface contamination'
    ],
    ('concrete', None): [
        'Efflorescence',
        'Paint and coatings',
        'Oil stains',
        'Biological growth'
    ],
    # Wood
    ('wood', 'hardwood'): [
        'Char and weathering',
        'Paint and finish',
        'Stain removal',
        'Surface contamination'
    ],
    ('wood', 'softwood'): [
        'Char and weathering',
        'Paint and finish',
        'Stain removal',
        'Surface contamination'
    ],
    # Glass and ceramics
    ('glass', 'soda-lime'): [
        'Organic deposits',
        'Paint overspray',
        'Adhesive residue',
        'Surface contamination'
    ],
    ('glass', 'specialty-glass'): [
        'Organic deposits',
        'Coatings and films',
        'Adhesive residue',
        'Surface contamination'
    ],
    ('glass', 'standard'): [
        'Organic deposits',
        'Paint overspray',
        'Adhesive residue',
        'Surface contamination'
    ],
    ('glass', 'optical'): [
        'Organic deposits',
        'Coatings and films',
        'Adhesive residue',
        'Fingerprints and oils'
    ],
    ('ceramic', 'oxide'): [
        'Surface contamination',
        'Oxide scale',
        'Processing residue',
        'Adhesive residue'
    ],
    ('ceramic', 'technical'): [
        'Surface contamination',
        'Oxide scale',
        'Thermal spray coatings',
        'Adhesive residue'
    ],
    ('ceramic', 'carbide'): [
        'Surface contamination',
        'Oxide layer',
        'Processing residue',
        'Adhesive residue'
    ],
    ('ceramic', 'traditional'): [
        'Surface contamination',
        'Glaze defects',
        'Organic deposits',
        'Adhesive residue'
    ],
    ('ceramic', 'advanced'): [
        'Surface contamination',
        'Oxide layer',
        'Thermal spray coatings',
        'Adhesive residue'
    ],
    # Rubber and textiles
    ('rubber', 'natural'): [
        'Mold release agents',
        'Surface contamination',
        'Adhesive residue',
        'Oxidation'
    ],
    ('rubber', 'coating'): [
        'Surface contamination',
        'Adhesive residue',
        'Oxidation',
        'Paint overspray'
    ],
    ('rubber', None): [
        'Mold release agents',
        'Surface contamination',
        'Adhesive residue',
        'Oxidation'
    ],
    ('textile', 'natural'): [
        'Surface contamination',
        'Staining',
        'Biological growth',
        'Adhesive residue'
    ],
    ('textile', 'synthetic'): [
        'Surface contamination',
        'Adhesive residue',
        'Paint overspray',
        'Mold release agents'
    ],
}

# Service offering notes by material characteristics
SERVICE_NOTES = {
    # High reflectivity materials
    ('metal', 'non-ferrous'): 'Lower power settings recommended due to high reflectivity',
    ('metal', 'precious'): 'Precision settings required for delicate surfaces',
    ('metal', 'elemental'): 'Lower power settings recommended due to high reflectivity',
    # Oxidation-sensitive materials
    ('metal', 'specialty'): 'Controlled atmosphere may be required to prevent re-oxidation',
    ('metal', 'refractory'): 'Controlled atmosphere may be required to prevent re-oxidation',
    ('metal', 'superalloy'): 'Controlled environment recommended for aerospace-grade cleaning',
    ('metal', 'lanthanide'): 'Controlled environment required - highly reactive materials',
    ('metal', 'scandium-group'): 'Controlled environment required - highly reactive materials',
    # Heat-sensitive materials  
    ('plastic', 'thermoplastic'): 'Low fluence required to prevent melting or warping',
    ('plastic', 'thermoset'): 'Moderate power to avoid thermal decomposition',
    ('plastic', 'general'): 'Low fluence required to prevent surface damage',
    ('composite', 'fiber-reinforced'): 'Careful parameter control to avoid matrix damage',
    ('composite', 'carbon-fiber'): 'Careful parameter control to avoid matrix damage',
    # Porous materials
    ('stone', 'sedimentary'): 'Multiple passes may be required for porous surfaces',
    ('stone', 'natural'): 'Multiple passes may be required for porous surfaces',
    ('concrete', 'concrete'): 'Higher power settings tolerated - porous surface requires multiple passes',
    ('concrete', 'structural'): 'Higher power settings tolerated - structural cleaning applications',
    ('concrete', None): 'Higher power settings tolerated - porous surface requires multiple passes',
    # Combustible materials
    ('wood', 'hardwood'): 'Careful power control to avoid charring',
    ('wood', 'softwood'): 'Low power settings to prevent ignition',
}


class TrivialFrontmatterExporter:
    """
    Trivial exporter: Copy Materials.yaml → Frontmatter YAML files.
    
    Also adds Categories.yaml metadata for reference (NO FALLBACK RANGES).
    
    NO API CLIENT REQUIRED.
    NO VALIDATION REQUIRED (already validated in Materials.yaml).
    NO COMPLETENESS CHECKS REQUIRED (already 100% complete in Materials.yaml).
    NO QUALITY SCORING REQUIRED (already scored in Materials.yaml).
    NO FALLBACK RANGES - Materials.yaml must have all property values.
    
    Just simple field mapping, category metadata addition, and YAML writing.
    """
    
    def __init__(self):
        """Initialize with output directories for dual-file architecture."""
        # Output directories for materials and settings pages
        self.materials_output_dir = Path(__file__).resolve().parents[2] / "frontmatter" / "materials"
        self.settings_output_dir = Path(__file__).resolve().parents[2] / "frontmatter" / "settings"
        
        self.materials_output_dir.mkdir(parents=True, exist_ok=True)
        self.settings_output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # Load metadata from new architecture (MaterialProperties.yaml, Settings.yaml, CategoryMetadata.yaml, Categories.yaml)
        from domains.materials.data_loader import (
            get_parameter_ranges,
            get_property_categories,
            get_category_ranges,
            get_category_definitions
        )
        
        # Get machine settings ranges
        self.machine_settings_ranges = get_parameter_ranges()
        
        # Get property categories for taxonomy
        property_cats = get_property_categories()
        self.property_categories_metadata = property_cats
        
        # Get category definitions and ranges
        self.category_definitions = get_category_definitions()
        self.category_ranges = get_category_ranges()
        
        # Load property taxonomy for categorization
        self._load_property_taxonomy()
        
        # Load Settings.yaml for machine settings and material challenges
        self.settings_data = self._load_settings()
        
        self.logger.info(f"✅ Loaded {len(self.category_definitions)} material categories")
        self.logger.info(f"✅ Loaded {len(self.machine_settings_ranges)} machine settings ranges")
        self.logger.info(f"✅ Loaded property taxonomy with {len(self.property_taxonomy)} categories")
        self.logger.info(f"✅ Loaded {len(self.settings_data.get('settings', {}))} materials from Settings.yaml")
        
        # Load separated content files for orchestration using unified_loader
        from shared.data.unified_loader import (
            load_material_micros,
            load_material_faqs,
            load_regulatory_standards
        )
        
        self.micros = load_material_micros()
        self.faqs = load_material_faqs()
        self.regulatory_standards = load_regulatory_standards()
        
        self.logger.info(f"✅ Loaded {len(self.micros)} micros from content files")
        self.logger.info(f"✅ Loaded {len(self.faqs)} FAQ sets from content files")
        self.logger.info(f"✅ Loaded {len(self.regulatory_standards)} regulatory standards from content files")
    
    # Content loading methods removed - now using unified_loader
    # See load_material_micros(), load_material_faqs(), load_regulatory_standards()
    # in shared/data/unified_loader.py
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load Settings.yaml for machine settings and material challenges."""
        from shared.data.unified_loader import get_settings_loader
        
        try:
            loader = get_settings_loader()
            # Load raw structure (includes 'settings' key and '_metadata')
            data = loader.load_settings(extract_machine_settings=False)
            return data
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to load Settings.yaml: {e}")
            return {'settings': {}}
    
    def _load_property_taxonomy(self):
        """Load property taxonomy from MaterialProperties.yaml to categorize properties correctly."""
        # Extract property categories from the new schema
        categories = self.property_categories_metadata.get('categories', {})
        
        # Build taxonomy mapping: property_name -> category_id
        self.property_taxonomy = {}
        
        for cat_id in ['material_characteristics', 'laser_material_interaction']:
            if cat_id in categories:
                cat_data = categories[cat_id]
                # Properties are in 'properties' list
                properties_list = cat_data.get('properties', [])
                for prop in properties_list:
                    self.property_taxonomy[prop] = cat_id
                    
        self.logger.info(f"   Taxonomy maps {len(self.property_taxonomy)} properties to categories")
    
    def export_all(self) -> Dict[str, bool]:
        """
        Export all materials from Materials.yaml to frontmatter files.
        
        Returns:
            Dict mapping material names to success status
        """
        self.logger.info("🚀 Starting trivial frontmatter export (no API, no validation)")
        
        # Load source of truth (already validated, complete)
        materials_data = load_materials_cached()
        materials = materials_data.get('materials', {})
        
        results = {}
        for material_name in materials:
            try:
                self.export_single(material_name, materials[material_name])
                results[material_name] = True
            except Exception as e:
                self.logger.error(f"❌ Export failed for {material_name}: {e}")
                results[material_name] = False
        
        success_count = sum(1 for v in results.values() if v)
        self.logger.info(f"✅ Exported {success_count}/{len(results)} materials")
        
        return results
    
    def export_single(self, material_name: str, material_data: Dict) -> None:
        """
        Export single material to frontmatter YAML file.
        
        Copies data from Materials.yaml and enriches properties and machine settings
        with min/max ranges from Categories.yaml.
        
        Args:
            material_name: Name of the material
            material_data: Material data from Materials.yaml (100% complete, validated)
        """
        # Start with material name
        frontmatter = {'name': material_name}
        
        # Get category for range lookups
        category = material_data.get('category', '')
        category_ranges = self._get_category_ranges(category)
        
        # Generate breadcrumb navigation (before field copying)
        # POLICY: Strip parentheses from all filenames for clean URLs and consistency
        material_slug = create_material_slug(material_name)
        filename = f"{material_slug}-laser-cleaning.yaml"
        slug = filename.replace('.yaml', '')
        breadcrumb = self._generate_breadcrumb(material_data, slug)
        frontmatter['breadcrumb'] = breadcrumb
        
        # Enrich author data from registry (Materials.yaml only has author.id)
        author_field = material_data.get('author', {})
        author_id = author_field.get('id') if isinstance(author_field, dict) else author_field
        
        # Get full author data from registry
        from data.authors.registry import get_author
        try:
            author_data = get_author(author_id)
        except KeyError:
            self.logger.error(f"❌ Invalid author ID {author_id} in material {material_data.get('name', 'Unknown')}")
            raise
        
        # Add _metadata for voice tracking
        frontmatter['_metadata'] = {
            'voice': {
                'author_name': author_data.get('name', 'Unknown'),
                'author_country': author_data.get('country', 'Unknown'),
                'voice_applied': True,
                'content_type': 'material'
            }
        }
        
        # Add enriched author data to frontmatter (from registry, not Materials.yaml)
        frontmatter['author'] = author_data.copy()
        
        # Load settings from Settings.yaml (machineSettings + material_challenges)
        settings_entry = self.settings_data.get('settings', {}).get(material_name, {})
        
        # Define fields that should be exported to frontmatter (per frontmatter_template.yaml)
        EXPORTABLE_FIELDS = {
            'breadcrumb',
            'category', 'subcategory', 'title', 'material_description',
            'datePublished', 'dateModified',  # Schema.org date fields from git history
            'images', 'micro', 'regulatoryStandards', 'eeat',
            'materialProperties', 'machineSettings', 'material_challenges', 'settings_description', 'faq',
            '_metadata', 'material_metadata'
        }
        
        # Copy only exportable fields from Materials.yaml (exclude 'author' - it's enriched from registry above)
        for key, value in material_data.items():
            if key not in EXPORTABLE_FIELDS:
                # Skip fields that shouldn't be in frontmatter (author, applications, materialCharacteristics, environmentalImpact, outcomeMetrics, etc.)
                continue
            
            if key == 'materialProperties':
                # Enrich material properties with min/max from category ranges
                enriched = self._enrich_material_properties(value, category_ranges)
                # Remove description fields except from regulatoryStandards
                cleaned = self._remove_descriptions(enriched, preserve_regulatory=False)
                # Strip generation metadata
                frontmatter[key] = self._strip_generation_metadata(cleaned)
            elif key == 'machineSettings':
                # Load from Settings.yaml instead of Materials.yaml
                settings_value = settings_entry.get('machineSettings', {})
                if settings_value:
                    # Enrich machine settings with min/max from machine settings ranges
                    enriched = self._enrich_machine_settings(settings_value, category_ranges)
                    # Remove description fields
                    cleaned = self._remove_descriptions(enriched, preserve_regulatory=False)
                    # Strip generation metadata
                    frontmatter[key] = self._strip_generation_metadata(cleaned)
            elif key == 'micro':
                # Micro is orchestrated from separate Micros.yaml file - skip in this loop
                # Will be added after the loop from self.micros
                continue
            elif key == 'faq':
                # FAQ may exist in Materials.yaml OR in external FAQs.yaml
                # Priority: Materials.yaml data first, then FAQs.yaml
                if value:  # If FAQ exists in Materials.yaml, use it
                    cleaned = self._remove_descriptions(value, preserve_regulatory=False)
                    formatted_faq = self._format_faq_with_topics(cleaned)
                    frontmatter['faq'] = self._strip_generation_metadata(formatted_faq)
                # If no FAQ in Materials.yaml, will try external FAQs.yaml after loop
                continue
            elif key == 'regulatoryStandards':
                # Copy regulatoryStandards from Materials.yaml
                # Keep description field for regulatory standards (user-facing)
                if value:  # If exists in Materials.yaml, use it
                    frontmatter['regulatoryStandards'] = self._strip_generation_metadata(value)
                # If no regulatoryStandards in Materials.yaml, will try external RegulatoryStandards.yaml after loop
                continue
            else:
                # Copy as-is but remove description fields and strip generation metadata
                cleaned = self._remove_descriptions(value, preserve_regulatory=False)
                frontmatter[key] = self._strip_generation_metadata(cleaned)
        
        # Orchestrate content from separated content files (Micros.yaml, FAQs.yaml, RegulatoryStandards.yaml)
        # These files were extracted from Materials.yaml for better organization while maintaining single-file output
        
        # Add caption from Micros.yaml (if not already present)
        if 'micro' not in frontmatter and material_name in self.micros:
            micro_data = self.micros[material_name]
            cleaned = self._remove_descriptions(micro_data, preserve_regulatory=False)
            stripped = self._strip_generation_metadata(cleaned)
            # Ensure only before/after remain
            if isinstance(stripped, dict):
                frontmatter['micro'] = {
                    k: v for k, v in stripped.items()
                    if k in ['before', 'after']
                }
            else:
                frontmatter['micro'] = stripped
        
        # Add FAQ from FAQs.yaml (if not already present from Materials.yaml)
        if 'faq' not in frontmatter and material_name in self.faqs:
            faq_data = self.faqs[material_name]
            cleaned = self._remove_descriptions(faq_data, preserve_regulatory=False)
            formatted_faq = self._format_faq_with_topics(cleaned)
            frontmatter['faq'] = self._strip_generation_metadata(formatted_faq)
        
        # Add regulatory standards from RegulatoryStandards.yaml (if not already present from Materials.yaml)
        if 'regulatoryStandards' not in frontmatter and material_name in self.regulatory_standards:
            regulatory_data = self.regulatory_standards[material_name]
            normalized = self._normalize_regulatory_standards(regulatory_data)
            frontmatter['regulatoryStandards'] = self._strip_generation_metadata(normalized)
        
        # Add material_challenges from Settings.yaml (material-specific challenges)
        if settings_entry and 'material_challenges' in settings_entry:
            challenges = settings_entry['material_challenges']
            if challenges:
                frontmatter['material_challenges'] = self._strip_generation_metadata(challenges)
                self.logger.info(f"✅ Added material_challenges for {material_name} from Settings.yaml")
        elif category:
            # Fallback to category-level challenges if material-specific not available
            material_challenges = get_material_challenges(category)
            if material_challenges:
                frontmatter['material_challenges'] = self._strip_generation_metadata(material_challenges)
                self.logger.info(f"✅ Added material_challenges for {material_name} from {category} category")
            else:
                self.logger.debug(f"No material_challenges found for category: {category}")
        
        # Add settings_description from Settings.yaml
        if settings_entry and 'settings_description' in settings_entry:
            settings_desc = settings_entry['settings_description']
            if settings_desc:
                frontmatter['settings_description'] = self._strip_generation_metadata(settings_desc)
                self.logger.info(f"✅ Added settings_description for {material_name} from Settings.yaml")
        
        # Override with components if they exist (new generation system saves to components)
        if 'components' in material_data:
            components = material_data['components']
            # Priority order: components > direct fields
            if 'material_description' in components:
                frontmatter['material_description'] = components['material_description']
            if 'settings_description' in components:
                frontmatter['settings_description'] = components['settings_description']
            if 'micro' in components:
                caption = components['micro']
                cleaned = self._remove_descriptions(caption, preserve_regulatory=False)
                stripped = self._strip_generation_metadata(cleaned)
                if isinstance(stripped, dict):
                    frontmatter['micro'] = {
                        k: v for k, v in stripped.items()
                        if k in ['before', 'after']
                    }
                else:
                    frontmatter['micro'] = stripped
                self.logger.debug(f"Using caption from components")
            if 'faq' in components:
                faq = components['faq']
                cleaned = self._remove_descriptions(faq, preserve_regulatory=False)
                formatted_faq = self._format_faq_with_topics(cleaned)
                frontmatter['faq'] = self._strip_generation_metadata(formatted_faq)
                self.logger.debug(f"Using FAQ from components")
        
        # Export dual-file structure: materials page and settings page
        self._export_materials_page(material_name, frontmatter)
        self._export_settings_page(material_name, frontmatter, material_data)
    
    def _export_materials_page(self, material_name: str, full_frontmatter: Dict) -> None:
        """
        Export materials page frontmatter: /materials/{material}-laser-cleaning.yaml
        
        Includes: micro, FAQ, regulatory standards, material properties, images, author
        """
        materials_page = {}
        
        # Core metadata
        materials_page['name'] = full_frontmatter.get('name')
        # POLICY: Strip parentheses from slugs
        materials_page['slug'] = create_material_slug(material_name)
        materials_page['category'] = full_frontmatter.get('category')
        materials_page['subcategory'] = full_frontmatter.get('subcategory')
        materials_page['content_type'] = 'unified_material'
        materials_page['schema_version'] = '4.0.0'
        
        # Dates
        materials_page['datePublished'] = full_frontmatter.get('datePublished')
        materials_page['dateModified'] = full_frontmatter.get('dateModified')
        
        # Author and metadata
        materials_page['author'] = full_frontmatter.get('author')
        materials_page['_metadata'] = full_frontmatter.get('_metadata')
        
        # Page-specific metadata
        materials_page['title'] = full_frontmatter.get('title')
        materials_page['material_description'] = full_frontmatter.get('material_description')
        materials_page['breadcrumb'] = full_frontmatter.get('breadcrumb')
        
        # Images
        materials_page['images'] = full_frontmatter.get('images')
        
        # Content (materials page specific)
        materials_page['micro'] = full_frontmatter.get('micro')
        materials_page['faq'] = full_frontmatter.get('faq')
        materials_page['regulatoryStandards'] = full_frontmatter.get('regulatoryStandards')
        materials_page['materialProperties'] = full_frontmatter.get('materialProperties')
        materials_page['eeat'] = full_frontmatter.get('eeat')
        materials_page['material_metadata'] = full_frontmatter.get('material_metadata')
        
        # Generate serviceOffering for SEO rich snippets (Service/Product JSON-LD schema)
        # Uses category/subcategory to determine difficulty, hours, and target contaminants
        category = full_frontmatter.get('category', '')
        subcategory = full_frontmatter.get('subcategory', '')
        machine_settings = full_frontmatter.get('machineSettings')
        material_properties = full_frontmatter.get('materialProperties')
        
        materials_page['serviceOffering'] = self._generate_service_offering(
            material_name=material_name,
            category=category,
            subcategory=subcategory,
            machine_settings=machine_settings,
            material_properties=material_properties
        )
        
        # Add preservedData with generation timestamp for metadata sync validation
        from datetime import datetime
        materials_page['preservedData'] = {
            'generationMetadata': {
                'generated_date': datetime.now().isoformat()
            }
        }
        
        # NORMALIZATION: Wrap all fields in metadata property to match settings/contaminants structure
        output_data = {'metadata': materials_page}
        
        # Write materials page YAML
        # POLICY: Strip parentheses from filenames
        material_slug = create_material_slug(material_name)
        filename = f"{material_slug}-laser-cleaning.yaml"
        output_path = self.materials_output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(output_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
        
        # Verify what was written
        if material_name == 'Aluminum':
            with open(output_path, 'r') as f:
                content = f.read()
                for line in content.split('\n')[:10]:
                    if 'material_description:' in line:
                        print(f"✅ [VERIFY] Wrote to file: {line}")
                        break
        
        self.logger.info(f"✅ Exported materials page: {material_name} → {filename}")
    
    def _export_settings_page(self, material_name: str, full_frontmatter: Dict, material_data: Dict = None) -> None:
        """
        Export settings page frontmatter: /settings/{material}-settings.yaml
        
        Includes: machine settings, thermal properties, laser interaction, diagnostics (future), challenges (future)
        
        Args:
            material_name: Name of the material
            full_frontmatter: Frontmatter dict with common fields
            material_data: Raw material data from Materials.yaml for extracting thermal/laser properties
        """
        settings_page = {}
        
        # Core metadata
        settings_page['name'] = full_frontmatter.get('name')
        settings_page['slug'] = material_name.lower().replace(' ', '-')
        settings_page['category'] = full_frontmatter.get('category')
        settings_page['subcategory'] = full_frontmatter.get('subcategory')
        settings_page['content_type'] = 'unified_settings'
        settings_page['schema_version'] = '4.0.0'
        settings_page['active'] = True
        
        # Dates
        settings_page['datePublished'] = full_frontmatter.get('datePublished')
        settings_page['dateModified'] = full_frontmatter.get('dateModified')
        
        # Author (settings pages use professional tone, but same author attribution)
        settings_page['author'] = full_frontmatter.get('author')
        
        # Settings page metadata
        settings_page['title'] = f"{full_frontmatter.get('name')} Laser Cleaning Settings"
        settings_page['settings_description'] = full_frontmatter.get('settings_description', f"Detailed machine settings, parameter relationships, diagnostic procedures, and troubleshooting guides for optimizing {full_frontmatter.get('name').lower()} laser cleaning operations.")
        
        # Settings-specific breadcrumb (uses /materials paths)
        category = full_frontmatter.get('category', '')
        subcategory = full_frontmatter.get('subcategory', '')
        breadcrumb = [
            {'label': 'Home', 'href': '/'},
            {'label': 'Materials', 'href': '/materials'}
        ]
        
        if category:
            breadcrumb.append({
                'label': category.replace('_', ' ').title(),
                'href': f'/materials/{category}'
            })
        
        if subcategory:
            breadcrumb.append({
                'label': subcategory.replace('_', ' ').replace('-', ' ').title(),
                'href': f'/materials/{category}/{subcategory}'
            })
        
        breadcrumb.append({
            'label': full_frontmatter.get('name'),
            'href': f'/materials/{settings_page["slug"]}'
        })
        
        settings_page['breadcrumb'] = breadcrumb
        
        # Images (shared between pages)
        settings_page['images'] = full_frontmatter.get('images')
        
        # Content (settings page specific)
        settings_page['machineSettings'] = full_frontmatter.get('machineSettings')
        
        # Extract and add thermalProperties block for interactive components
        # Source: materialProperties.laser_material_interaction in Materials.yaml
        if material_data:
            thermal_props = self._extract_thermal_properties(material_data)
            if thermal_props:
                settings_page['thermalProperties'] = thermal_props
                self.logger.debug(f"✅ Added thermalProperties for {material_name}")
            else:
                # Use category defaults
                category = full_frontmatter.get('category', '')
                subcategory = full_frontmatter.get('subcategory', '')
                defaults = self._get_thermal_defaults(category, subcategory)
                if defaults:
                    settings_page['thermalProperties'] = {
                        'thermalDiffusivity': {
                            'value': defaults.get('thermalDiffusivity'),
                            'unit': 'mm²/s'
                        },
                        'thermalConductivity': {
                            'value': defaults.get('thermalConductivity'),
                            'unit': 'W/(m·K)'
                        },
                        'thermalDestructionPoint': {
                            'value': defaults.get('thermalDestructionPoint'),
                            'unit': 'K',
                            'type': defaults.get('destructionType', 'melting')
                        }
                    }
                    self.logger.debug(f"✅ Added thermalProperties (category defaults) for {material_name}")
            
            # Extract and add laserMaterialInteraction block for heatmap components
            laser_props = self._extract_laser_interaction(material_data)
            if laser_props:
                settings_page['laserMaterialInteraction'] = laser_props
                self.logger.debug(f"✅ Added laserMaterialInteraction for {material_name}")
            else:
                # Use category defaults
                category = full_frontmatter.get('category', '')
                subcategory = full_frontmatter.get('subcategory', '')
                defaults = self._get_thermal_defaults(category, subcategory)
                if defaults:
                    damage = defaults.get('laserDamageThreshold')
                    ablation = defaults.get('ablationThreshold')
                    settings_page['laserMaterialInteraction'] = {
                        'laserDamageThreshold': {
                            'value': damage,
                            'unit': 'J/cm²'
                        },
                        'ablationThreshold': {
                            'value': ablation,
                            'unit': 'J/cm²'
                        }
                    }
                    # Calculate optimal range
                    if damage and ablation:
                        min_opt = round(ablation * 1.2, 3)
                        max_opt = round(damage * 0.8, 3)
                        if min_opt < max_opt:
                            settings_page['laserMaterialInteraction']['optimalFluenceRange'] = {
                                'min': min_opt,
                                'max': max_opt,
                                'unit': 'J/cm²'
                            }
                    self.logger.debug(f"✅ Added laserMaterialInteraction (category defaults) for {material_name}")
        
        # Add material_challenges (category-level diagnostic guidance)
        settings_page['material_challenges'] = full_frontmatter.get('material_challenges')
        
        # Add preservedData with generation timestamp for metadata sync validation
        from datetime import datetime
        settings_page['preservedData'] = {
            'generationMetadata': {
                'generated_date': datetime.now().isoformat()
            }
        }
        
        # NORMALIZATION: Wrap all fields in metadata property to match materials structure
        output_data = {'metadata': settings_page}
        
        # Write settings page YAML
        # POLICY: Strip parentheses from all filenames for clean URLs and consistency
        material_slug = create_material_slug(material_name)
        filename = f"{material_slug}-settings.yaml"
        output_path = self.settings_output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(output_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
        
        self.logger.info(f"✅ Exported settings page: {material_name} → {filename}")
    
    def _get_category_ranges(self, category: str) -> Dict[str, Any]:
        """Get category-wide ranges from MaterialProperties.yaml."""
        if not category or not self.category_ranges:
            return {}
        
        # Use new category_ranges structure
        category_data = self.category_ranges.get(category, {})
        return category_data.get('ranges', {})
    
    def _enrich_material_properties(self, properties: Dict, category_ranges: Dict) -> Dict:
        """
        Enrich material properties with min/max ranges from Categories.yaml.
        
        Input from Materials.yaml: Already categorized structure
        Output for frontmatter: Same structure with added min/max from category ranges
        """
        if not properties or not isinstance(properties, dict):
            return properties
        
        # Check if already normalized (has category groups)
        has_categories = ('material_characteristics' in properties or 
                         'laser_material_interaction' in properties)
        
        if has_categories:
            # Already normalized - just enrich with ranges and flatten nested values
            enriched = {}
            for category_name, category_data in properties.items():
                if category_name not in ['material_characteristics', 'laser_material_interaction']:
                    continue
                    
                if not isinstance(category_data, dict):
                    enriched[category_name] = category_data
                    continue
                
                enriched_category = {}
                for key, value in category_data.items():
                    # Keep metadata fields
                    if key in ['label', 'description', 'percentage']:
                        enriched_category[key] = value
                    # Process properties
                    else:
                        flattened_value = self._flatten_property_value(value)
                        enriched_value = self._add_min_max(flattened_value, key, category_ranges)
                        enriched_category[key] = enriched_value
                
                enriched[category_name] = enriched_category
            
            return enriched
        
        # Legacy flat structure - categorize using taxonomy
        else:
            enriched = {
                'material_characteristics': {
                    'label': 'Material Characteristics'
                },
                'laser_material_interaction': {
                    'label': 'Laser-Material Interaction'
                }
            }
            
            for prop_name, prop_value in properties.items():
                if prop_name in ['label', 'description', 'percentage']:
                    continue
                
                category_id = self.property_taxonomy.get(prop_name)
                if not category_id:
                    self.logger.warning(f"⚠️  Property '{prop_name}' not in taxonomy - skipping")
                    continue
                
                flattened_value = self._flatten_property_value(prop_value)
                enriched_value = self._add_min_max(flattened_value, prop_name, category_ranges)
                enriched[category_id][prop_name] = enriched_value
            
            return enriched
    
    def _flatten_property_value(self, prop_value: Any) -> Dict:
        """
        Flatten double-nested property structure from Materials.yaml.
        
        Input:  {'value': {'value': 420.0, 'unit': '', 'confidence': 1.0}, 
                 'unit': 'kg/m³', 'confidence': {'value': 95, ...}, 'source': 'ai_research'}
        Output: {'value': 420.0, 'unit': 'kg/m³', 'confidence': 95, 'source': 'ai_research'}
        """
        if not isinstance(prop_value, dict):
            return prop_value
        
        flattened = {}
        
        for key, value in prop_value.items():
            if key == 'value' and isinstance(value, dict) and 'value' in value:
                # Extract nested value
                flattened['value'] = value['value']
            elif key == 'confidence' and isinstance(value, dict) and 'value' in value:
                # Extract nested confidence
                flattened['confidence'] = value['value']
            elif key not in flattened:
                # Copy other fields directly
                flattened[key] = value
        
        # Remove confidence from export (per frontmatter_template - not in example)
        if 'confidence' in flattened:
            del flattened['confidence']
        
        return flattened
    
    def _enrich_machine_settings(self, settings: Dict, category_ranges: Dict) -> Dict:
        """Add min/max from machine settings ranges to machine settings."""
        if not settings or not isinstance(settings, dict):
            return settings
        
        enriched = {}
        for setting_name, setting_value in settings.items():
            # Use machine settings ranges instead of category ranges
            enriched[setting_name] = self._add_min_max(setting_value, setting_name, self.machine_settings_ranges)
        
        return enriched
    
    def _normalize_thermal_diffusivity(self, value: float, unit: str) -> float:
        """
        Normalize thermalDiffusivity to mm²/s for frontend components.
        
        Input formats from Materials.yaml:
        - value=9.7, unit='×10^{-5} m²/s' → 97.0 mm²/s
        - value=1.25e-07, unit='m²/s' → 0.125 mm²/s  
        - value=6.2e-07, unit='m^2/s' → 0.62 mm²/s
        - value=0.12, unit='mm²/s' → 0.12 mm²/s (already correct)
        
        Returns:
            Thermal diffusivity in mm²/s
        """
        if value is None:
            return None
        
        # Already in mm²/s - check this FIRST before m²/s
        if 'mm²/s' in unit or 'mm^2/s' in unit:
            return value
        
        # Handle multiplier format: ×10^{-5} m²/s
        if '×10^{-5}' in unit or '10^{-5}' in unit:
            # value is in 10^-5 m²/s, convert to mm²/s
            # 10^-5 m²/s = 10 mm²/s
            return value * 10
        
        # Handle standard m²/s or m^2/s
        if 'm²/s' in unit or 'm^2/s' in unit:
            # Scientific notation: 1.25e-07 m²/s = 0.125 mm²/s
            return value * 1_000_000
        
        # Unknown format - assume m²/s and convert
        self.logger.warning(f"Unknown thermal diffusivity unit: {unit}, assuming m²/s")
        return value * 1_000_000
    
    def _extract_thermal_properties(self, material_data: Dict) -> Dict:
        """
        Extract thermalProperties block from material data for settings page.
        
        Source: materialProperties.laser_material_interaction
        
        Returns:
            Dict with thermalDiffusivity, thermalConductivity, thermalDestructionPoint
            formatted for frontend interactive components
        """
        thermal_props = {}
        
        # Get laser_material_interaction data
        mat_props = material_data.get('materialProperties', {})
        lmi = mat_props.get('laser_material_interaction', {})
        
        if not lmi:
            return thermal_props
        
        # Extract thermalDiffusivity (convert to mm²/s)
        td = lmi.get('thermalDiffusivity', {})
        if isinstance(td, dict) and td.get('value') is not None:
            unit = td.get('unit', 'm²/s')
            value_mm2_s = self._normalize_thermal_diffusivity(td['value'], unit)
            if value_mm2_s is not None:
                thermal_props['thermalDiffusivity'] = {
                    'value': round(value_mm2_s, 4),
                    'unit': 'mm²/s'
                }
        
        # Extract thermalConductivity (already in W/(m·K))
        tc = lmi.get('thermalConductivity', {})
        if isinstance(tc, dict) and tc.get('value') is not None:
            thermal_props['thermalConductivity'] = {
                'value': tc['value'],
                'unit': 'W/(m·K)'
            }
        
        # Extract thermalDestructionPoint
        tdp = lmi.get('thermalDestructionPoint', {})
        if isinstance(tdp, dict) and tdp.get('value') is not None:
            unit = tdp.get('unit', 'K')
            value = tdp['value']
            
            # Convert to K if in °C
            if unit == '°C':
                value = value + 273.15
                unit = 'K'
            
            # Determine destruction type based on category
            category = material_data.get('category', '')
            subcategory = material_data.get('subcategory', '')
            destruction_type = self._get_destruction_type(category, subcategory)
            
            thermal_props['thermalDestructionPoint'] = {
                'value': round(value, 2),
                'unit': 'K',
                'type': destruction_type
            }
        
        return thermal_props
    
    def _extract_laser_interaction(self, material_data: Dict) -> Dict:
        """
        Extract laserMaterialInteraction block from material data for settings page.
        
        Source: materialProperties.laser_material_interaction
        
        Returns:
            Dict with laserDamageThreshold, ablationThreshold, optimalFluenceRange
            formatted for frontend interactive components
        """
        laser_props = {}
        
        # Get laser_material_interaction data
        mat_props = material_data.get('materialProperties', {})
        lmi = mat_props.get('laser_material_interaction', {})
        
        if not lmi:
            return laser_props
        
        # Extract laserDamageThreshold
        ldt = lmi.get('laserDamageThreshold', {})
        if isinstance(ldt, dict) and ldt.get('value') is not None:
            unit = ldt.get('unit', 'J/cm²')
            value = ldt['value']
            
            # Convert J/m² to J/cm² if needed
            if unit == 'J/m²':
                value = value / 10000  # 1 J/m² = 0.0001 J/cm²
                unit = 'J/cm²'
            
            laser_props['laserDamageThreshold'] = {
                'value': round(value, 3),
                'unit': 'J/cm²'
            }
        
        # Extract ablationThreshold
        abt = lmi.get('ablationThreshold', {})
        if isinstance(abt, dict) and abt.get('value') is not None:
            unit = abt.get('unit', 'J/cm²')
            value = abt['value']
            
            # Convert J/m² to J/cm² if needed
            if unit == 'J/m²':
                value = value / 10000
                unit = 'J/cm²'
            
            laser_props['ablationThreshold'] = {
                'value': round(value, 3),
                'unit': 'J/cm²'
            }
        
        # Calculate optimalFluenceRange if both thresholds available
        if 'laserDamageThreshold' in laser_props and 'ablationThreshold' in laser_props:
            ablation = laser_props['ablationThreshold']['value']
            damage = laser_props['laserDamageThreshold']['value']
            
            # Optimal starts 20% above ablation, ends 20% below damage
            min_optimal = round(ablation * 1.2, 3)
            max_optimal = round(damage * 0.8, 3)
            
            # Ensure min < max
            if min_optimal < max_optimal:
                laser_props['optimalFluenceRange'] = {
                    'min': min_optimal,
                    'max': max_optimal,
                    'unit': 'J/cm²'
                }
        
        # Extract thermalShockResistance if available
        tsr = lmi.get('thermalShockResistance', {})
        if isinstance(tsr, dict) and tsr.get('value') is not None:
            laser_props['thermalShockResistance'] = {
                'value': tsr['value'],
                'unit': 'K'
            }
        
        # Extract reflectivity if available
        refl = lmi.get('laserReflectivity', {}) or lmi.get('reflectivity', {})
        if isinstance(refl, dict) and refl.get('value') is not None:
            laser_props['reflectivity'] = {
                'value': refl['value'],
                'wavelength': 1064  # Default to common laser wavelength
            }
        
        return laser_props
    
    def _get_destruction_type(self, category: str, subcategory: str) -> str:
        """
        Determine thermal destruction type based on material category.
        
        Returns: 'melting', 'charring', 'decomposition', or 'softening'
        """
        # Check specific subcategory first
        key = (category, subcategory)
        if key in THERMAL_CATEGORY_DEFAULTS:
            return THERMAL_CATEGORY_DEFAULTS[key].get('destructionType', 'melting')
        
        # Fall back to category only
        key_cat = (category, None)
        if key_cat in THERMAL_CATEGORY_DEFAULTS:
            return THERMAL_CATEGORY_DEFAULTS[key_cat].get('destructionType', 'melting')
        
        # Category-based defaults
        destruction_types = {
            'metal': 'melting',
            'wood': 'charring',
            'plastic': 'softening',
            'rubber': 'decomposition',
            'textile': 'charring',
            'composite': 'decomposition',
            'ceramic': 'melting',
            'glass': 'softening',
            'stone': 'melting',
        }
        
        return destruction_types.get(category, 'melting')
    
    def _get_thermal_defaults(self, category: str, subcategory: str) -> Dict:
        """
        Get category-level thermal defaults when material-specific data is missing.
        
        Returns dict with thermalDiffusivity, thermalConductivity, etc.
        """
        # Try specific subcategory first
        key = (category, subcategory)
        if key in THERMAL_CATEGORY_DEFAULTS:
            return THERMAL_CATEGORY_DEFAULTS[key].copy()
        
        # Fall back to category only
        key_cat = (category, None)
        if key_cat in THERMAL_CATEGORY_DEFAULTS:
            return THERMAL_CATEGORY_DEFAULTS[key_cat].copy()
        
        # Default to non-ferrous metal if nothing matches
        return THERMAL_CATEGORY_DEFAULTS.get(('metal', 'non-ferrous'), {}).copy()
    
    def _add_min_max(self, prop_value: Any, prop_name: str, category_ranges: Dict) -> Any:
        """Add min/max fields to a property if available in category ranges.
        
        Also applies numeric formatting for readability (see NUMERIC_FORMATTING_POLICY.md).
        """
        if not isinstance(prop_value, dict):
            return prop_value
        
        # Create enriched property - use shallow copy to preserve structure
        enriched = prop_value.copy()
        
        # Format existing numeric values for readability
        for field in ['value', 'min', 'max']:
            if field in enriched and isinstance(enriched[field], (int, float)):
                enriched[field] = format_numeric_value(enriched[field])
        
        # Already has min/max - don't override (but still format)
        if 'min' in prop_value or 'max' in prop_value:
            return enriched
        
        # Look up category range
        range_data = category_ranges.get(prop_name, {})
        if not range_data or not isinstance(range_data, dict):
            return enriched
        
        # Add and format min/max from category ranges
        if 'min' in range_data:
            enriched['min'] = format_numeric_value(range_data['min'])
        if 'max' in range_data:
            enriched['max'] = format_numeric_value(range_data['max'])
        
        return enriched
    
    def _remove_descriptions(self, data: Any, preserve_regulatory: bool = False) -> Any:
        """
        Recursively remove 'description' fields from data structures.
        
        Args:
            data: Data to process (dict, list, or other)
            preserve_regulatory: If True, preserve descriptions (for regulatoryStandards only)
        
        Returns:
            Data with description fields removed (except when preserve_regulatory=True)
        """
        if preserve_regulatory:
            # Don't remove descriptions from regulatoryStandards
            return data
        
        if isinstance(data, dict):
            # Remove 'description' key and recurse into nested structures
            return {
                k: self._remove_descriptions(v, preserve_regulatory=False)
                for k, v in data.items()
                if k != 'description'
            }
        elif isinstance(data, list):
            # Recurse into list items
            return [self._remove_descriptions(item, preserve_regulatory=False) for item in data]
        else:
            # Return primitives as-is
            return data
    
    def _strip_generation_metadata(self, data: Any) -> Any:
        """
        Remove generation metadata fields that should not persist in frontmatter.
        
        Strips:
        - generated (timestamp)
        - word_count, word_count_before, word_count_after, total_words
        - question_count, character_count
        - author (in caption - redundant with top-level author)
        - generation_method (tracking field)
        
        These fields are useful during generation for quality tracking but should
        not be exported to production frontmatter files.
        
        Args:
            data: Data to process (dict, list, or other)
        
        Returns:
            Data with generation metadata removed
        """
        # Fields to remove from all structures
        METADATA_FIELDS = {
            'generated', 'word_count', 'word_count_before', 'word_count_after',
            'total_words', 'question_count', 'character_count',
            'author', 'generation_method'  # Micro-specific metadata
        }
        
        if isinstance(data, dict):
            return {
                k: self._strip_generation_metadata(v)
                for k, v in data.items()
                if k not in METADATA_FIELDS
            }
        elif isinstance(data, list):
            return [self._strip_generation_metadata(item) for item in data]
        else:
            return data
    
    def _normalize_regulatory_standards(self, standards: Any) -> list:
        """
        Normalize regulatoryStandards to template format.
        
        Per frontmatter_template.yaml, regulatory standards should be:
        - List of dicts only (no strings)
        - Each dict has: name, description, url, image
        - No longName field
        - No duplicate entries
        - Enriched organization metadata for SEMI and ASTM standards
        
        Args:
            standards: Raw regulatoryStandards from Materials.yaml
            
        Returns:
            Normalized list of regulatory standards dicts
        """
        if not isinstance(standards, list):
            return []
        
        normalized = []
        seen_descriptions = set()
        
        for item in standards:
            # Skip string entries (legacy universal standards)
            if isinstance(item, str):
                continue
            
            # Keep only dict entries
            if isinstance(item, dict):
                description = item.get('description', '')
                
                # Skip duplicates based on description
                if description in seen_descriptions:
                    continue
                
                seen_descriptions.add(description)
                
                # Keep only template fields: name, description, url, image
                normalized_item = {
                    'name': item.get('name', ''),
                    'description': description,
                    'url': item.get('url', ''),
                    'image': item.get('image', '')
                }
                
                # Enrich organization metadata for SEMI and ASTM standards
                normalized_item = self._enrich_organization_metadata(normalized_item)
                
                # Remove longName (not in template)
                # Already excluded by only including template fields
                
                normalized.append(normalized_item)
        
        return normalized
    
    def _enrich_organization_metadata(self, standard: Dict[str, str]) -> Dict[str, str]:
        """
        Enrich regulatory standard metadata for known organizations.
        
        Detects SEMI and ASTM patterns in description and populates:
        - Proper organization name
        - Organization-specific URL pattern
        - Organization-specific logo
        
        Args:
            standard: Standard dict with name, description, url, image
            
        Returns:
            Enriched standard dict
        """
        description = standard.get('description', '')
        current_name = standard.get('name', '')
        
        # Only enrich if current metadata is incomplete (Unknown or empty)
        if current_name not in ['Unknown', '', 'unknown']:
            return standard
        
        # SEMI standards detection and enrichment
        if 'SEMI' in description or description.startswith('SEMI '):
            standard['name'] = 'SEMI'
            standard['image'] = '/images/logo/logo-org-semi.png'
            
            # Extract SEMI standard ID for URL generation (e.g., "SEMI M1")
            # Pattern: "SEMI M1", "SEMI E10", etc.
            import re
            semi_match = re.search(r'SEMI\s+([A-Z]\d+)', description)
            if semi_match:
                semi_id = semi_match.group(1).lower()  # e.g., "m1"
                # Generate SEMI store URL
                # Format: https://store-us.semi.org/products/m00100-semi-m1-specification-for-...
                # Use simplified format since we don't have full product codes
                standard['url'] = f'https://store-us.semi.org/products/semi-{semi_id}'
            else:
                # Fallback to SEMI store homepage if pattern not matched
                standard['url'] = 'https://store-us.semi.org/'
        
        # ASTM standards detection and enrichment
        elif 'ASTM' in description or description.startswith('ASTM '):
            standard['name'] = 'ASTM'
            standard['image'] = '/images/logo/logo-org-astm.png'
            
            # Extract ASTM standard ID for URL generation (e.g., "ASTM F1188", "ASTM C848")
            # Pattern: "ASTM C848", "ASTM F1188-00", etc.
            import re
            astm_match = re.search(r'ASTM\s+([A-Z]\d+)', description)
            if astm_match:
                astm_id = astm_match.group(1).lower()  # e.g., "c848", "f1188"
                # Generate ASTM store URL
                # Format: https://store.astm.org/f1188-00.html (simplified - using base ID)
                standard['url'] = f'https://store.astm.org/{astm_id}.html'
            else:
                # Fallback to ASTM store homepage if pattern not matched
                standard['url'] = 'https://www.astm.org/standards'
        
        # EPA standards detection and enrichment
        elif 'EPA' in description or description.startswith('EPA '):
            standard['name'] = 'EPA'
            standard['image'] = '/images/logo/logo-org-epa.png'
            
            # EPA standards typically reference acts/regulations
            # Common patterns: "EPA Clean Air Act", "EPA 40 CFR", etc.
            if 'Clean Air Act' in description:
                standard['url'] = 'https://www.epa.gov/clean-air-act-overview'
            elif 'Clean Water Act' in description:
                standard['url'] = 'https://www.epa.gov/laws-regulations/summary-clean-water-act'
            elif '40 CFR' in description:
                # Extract CFR part number if available
                import re
                cfr_match = re.search(r'40\s*CFR\s*(?:Part\s*)?(\d+)', description)
                if cfr_match:
                    part = cfr_match.group(1)
                    standard['url'] = f'https://www.ecfr.gov/current/title-40/part-{part}'
                else:
                    standard['url'] = 'https://www.epa.gov/laws-regulations'
            else:
                # Fallback to EPA laws and regulations homepage
                standard['url'] = 'https://www.epa.gov/laws-regulations'
        
        # USDA standards detection and enrichment
        elif 'USDA' in description or description.startswith('USDA '):
            standard['name'] = 'USDA'
            standard['image'] = '/images/logo/logo-org-usda.png'
            
            # USDA standards typically reference food safety
            if 'Food Safety' in description:
                standard['url'] = 'https://www.usda.gov/topics/food-and-nutrition/food-safety'
            else:
                standard['url'] = 'https://www.usda.gov/'
        
        # FSC standards detection and enrichment
        elif 'FSC' in description or description.startswith('FSC '):
            standard['name'] = 'FSC'
            standard['image'] = '/images/logo/logo-org-fsc.png'
            
            # FSC (Forest Stewardship Council) standards
            if 'Sustainable Forestry' in description or 'Forestry' in description:
                standard['url'] = 'https://fsc.org/en/forest-management-certification'
            else:
                standard['url'] = 'https://fsc.org/'
        
        # UNESCO standards detection and enrichment
        elif 'UNESCO' in description or description.startswith('UNESCO '):
            standard['name'] = 'UNESCO'
            standard['image'] = '/images/logo/logo-org-unesco.png'
            
            # UNESCO (United Nations Educational, Scientific and Cultural Organization)
            if 'Cultural Heritage' in description or 'Heritage Conservation' in description:
                standard['url'] = 'https://whc.unesco.org/en/conservation/'
            else:
                standard['url'] = 'https://www.unesco.org/'
        
        # CITES standards detection and enrichment
        elif 'CITES' in description or description.startswith('CITES '):
            standard['name'] = 'CITES'
            standard['image'] = '/images/logo/logo-org-cites.png'
            
            # CITES (Convention on International Trade in Endangered Species)
            standard['url'] = 'https://cites.org/'
        
        return standard
    
    def _format_faq_with_topics(self, faq_list: list) -> list:
        """
        Format FAQ entries with Markdown topic highlighting.
        
        Reads topic_keyword and topic_statement from Materials.yaml FAQ entries.
        Applies **bold** Markdown syntax at export time:
        - Wraps topic_keyword in question with **keyword**
        - Prepends **topic_statement**. to answer
        
        Only exports question and answer fields (strips topic metadata).
        
        Args:
            faq_list: List of FAQ dicts from Materials.yaml (may have topic_keyword, topic_statement)
            
        Returns:
            List of FAQ dicts with only question and answer (Markdown formatted)
        """
        if not faq_list:
            return []
        
        formatted_faqs = []
        
        for faq_item in faq_list:
            if not isinstance(faq_item, dict):
                formatted_faqs.append(faq_item)
                continue
            
            question = faq_item.get('question', '')
            answer = faq_item.get('answer', '')
            topic_keyword = faq_item.get('topic_keyword', '')
            topic_statement = faq_item.get('topic_statement', '')
            
            # Format question with **keyword** Markdown bold syntax
            if topic_keyword and question:
                # Case-insensitive replacement (preserve original case)
                import re
                pattern = re.escape(topic_keyword)
                question_formatted = re.sub(
                    f'({pattern})',
                    r'**\1**',
                    question,
                    count=1,
                    flags=re.IGNORECASE
                )
            else:
                question_formatted = question
            
            # Format answer with prepended **topic_statement**.
            if topic_statement and answer:
                answer_formatted = f"**{topic_statement}**. {answer}"
            else:
                answer_formatted = answer
            
            # Export only question and answer (strip topic metadata)
            formatted_faqs.append({
                'question': question_formatted,
                'answer': answer_formatted
            })
        
        return formatted_faqs
    
    def _generate_service_offering(self, material_name: str, category: str, subcategory: str, 
                                   machine_settings: Dict = None, material_properties: Dict = None) -> Dict:
        """
        Generate serviceOffering data for SEO rich snippets.
        
        Uses material category/subcategory to determine:
        - Difficulty level → estimated hours
        - Target contaminants (from mapping or machineSettings.contaminantType)
        - Material-specific notes
        
        Args:
            material_name: Name of the material
            category: Material category (e.g., 'metal', 'plastic')
            subcategory: Material subcategory (e.g., 'ferrous', 'non-ferrous')
            machine_settings: Optional machineSettings dict to extract contaminantType
            material_properties: Optional materialProperties for notes generation
            
        Returns:
            serviceOffering dict per SERVICE_OFFERING_FRONTMATTER_SPEC.md
        """
        # Determine difficulty level based on category/subcategory
        category_key = (category.lower() if category else '', subcategory.lower() if subcategory else None)
        category_key_no_sub = (category.lower() if category else '', None)
        
        # Try with subcategory first, then without
        difficulty = MATERIAL_DIFFICULTY.get(category_key)
        if not difficulty:
            difficulty = MATERIAL_DIFFICULTY.get(category_key_no_sub, 'standard')  # Default to standard
        
        # Get estimated hours for this difficulty level
        hours = SERVICE_OFFERING_HOURS.get(difficulty, SERVICE_OFFERING_HOURS['standard'])
        
        # Get target contaminants - priority: machineSettings.contaminantType > mapping
        target_contaminants = []
        
        # Try to get from machineSettings first
        if machine_settings and isinstance(machine_settings, dict):
            contaminant_type = machine_settings.get('contaminantType')
            if contaminant_type:
                if isinstance(contaminant_type, list):
                    target_contaminants = contaminant_type
                elif isinstance(contaminant_type, str):
                    target_contaminants = [contaminant_type]
        
        # Fall back to category-based mapping if no machineSettings contaminants
        if not target_contaminants:
            target_contaminants = TARGET_CONTAMINANTS.get(category_key)
            if not target_contaminants:
                target_contaminants = TARGET_CONTAMINANTS.get(category_key_no_sub, [
                    'Surface contamination',
                    'Paint and coatings',
                    'Oxide layer',
                    'Adhesive residue'
                ])
        
        # Get material-specific notes
        notes = SERVICE_NOTES.get(category_key)
        if not notes:
            notes = SERVICE_NOTES.get(category_key_no_sub)
        
        # Build serviceOffering structure per spec
        service_offering = {
            'enabled': True,
            'type': 'professionalCleaning',
            'materialSpecific': {
                'estimatedHoursMin': hours['min'],
                'estimatedHoursTypical': hours['typical'],
                'targetContaminants': target_contaminants
            }
        }
        
        # Only add notes if we have them
        if notes:
            service_offering['materialSpecific']['notes'] = notes
        
        self.logger.debug(f"✅ Generated serviceOffering for {material_name}: {difficulty} difficulty, {hours['typical']} typical hours")
        
        return service_offering
    
    def _generate_breadcrumb(self, material_data: Dict, slug: str) -> list:
        """
        Generate breadcrumb navigation for materials.
        
        Hierarchy: Home → Materials → Category → Subcategory → Material
        
        Example for Aluminum (category: metal, subcategory: non-ferrous):
          - Home → /
          - Materials → /materials
          - Metal → /materials/metal
          - Non Ferrous → /materials/metal/non-ferrous
          - Aluminum → /materials/metal/non-ferrous/aluminum
        
        Args:
            material_data: Material data from Materials.yaml
            slug: URL slug for the material (e.g., "aluminum-laser-cleaning")
            
        Returns:
            List of breadcrumb dicts with label and href
        """
        breadcrumb = [{"label": "Home", "href": "/"}]
        
        # Add Materials level
        breadcrumb.append({"label": "Materials", "href": "/materials"})
        
        # Get category and subcategory
        category = material_data.get('category', '')  # e.g., "metal"
        subcategory = material_data.get('subcategory', '')  # e.g., "non-ferrous"
        
        # Add Category level (singular for consistency)
        if category:
            category_label = category.replace('-', ' ').replace('_', ' ').title()
            breadcrumb.append({
                "label": category_label,
                "href": f"/materials/{category.lower()}"  # Singular: /materials/metal
            })
        
        # Add Subcategory level (if present)
        if subcategory:
            subcategory_label = subcategory.replace('-', ' ').replace('_', ' ').title()
            breadcrumb.append({
                "label": subcategory_label,
                "href": f"/materials/{category.lower()}/{subcategory.lower()}"
            })
        
        # Add current material (use material name from slug without "laser-cleaning")
        name = material_data.get('name', '')
        if name:
            # Build final href based on whether there's a subcategory
            # POLICY: Strip parentheses from all URLs for clean routing
            material_slug = create_material_slug(name)
            if subcategory:
                final_href = f"/materials/{category.lower()}/{subcategory.lower()}/{material_slug}"
            else:
                final_href = f"/materials/{category.lower()}/{material_slug}"
            
            breadcrumb.append({
                "label": name,
                "href": final_href
            })
        
        return breadcrumb


def export_all_frontmatter() -> Dict[str, bool]:
    """
    Convenience function to export all frontmatter files.
    
    Usage:
        from export.core.trivial_exporter import export_all_frontmatter
        results = export_all_frontmatter()
        print(f"Exported {sum(results.values())}/{len(results)} materials")
    
    Returns:
        Dict mapping material names to success status
    """
    exporter = TrivialFrontmatterExporter()
    return exporter.export_all()


if __name__ == "__main__":
    # CLI usage: python3 -m components.frontmatter.core.trivial_exporter
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    print("=" * 80)
    print("TRIVIAL FRONTMATTER EXPORTER")
    print("=" * 80)
    print()
    print("Purpose: Copy Materials.yaml → Frontmatter YAML files")
    print("         Add Categories.yaml metadata (NO fallback ranges)")
    print("Design: Simple export, no API calls, no validation")
    print("Performance: Seconds for all 132 materials")
    print()
    
    results = export_all_frontmatter()
    
    print()
    print("=" * 80)
    success_count = sum(1 for v in results.values() if v)
    print(f"✅ SUCCESS: Exported {success_count}/{len(results)} materials")
    print("=" * 80)
