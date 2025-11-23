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
from data.materials.materials import load_materials_cached
from data.materials.loader import get_material_challenges

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
        
        # Load metadata from new architecture (MaterialProperties.yaml, MachineSettings.yaml, CategoryMetadata.yaml, Categories.yaml)
        from data.materials.loader import (
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
        
        self.logger.info(f"✅ Loaded {len(self.category_definitions)} material categories")
        self.logger.info(f"✅ Loaded {len(self.machine_settings_ranges)} machine settings ranges")
        self.logger.info(f"✅ Loaded property taxonomy with {len(self.property_taxonomy)} categories")
        
        # Load separated content files for orchestration
        self.captions = self._load_captions()
        self.faqs = self._load_faqs()
        self.regulatory_standards = self._load_regulatory_standards()
        
        self.logger.info(f"✅ Loaded {len(self.captions)} captions from content files")
        self.logger.info(f"✅ Loaded {len(self.faqs)} FAQ sets from content files")
        self.logger.info(f"✅ Loaded {len(self.regulatory_standards)} regulatory standards from content files")
    
    def _load_captions(self) -> Dict[str, Any]:
        """Load Captions.yaml and return captions dict."""
        captions_file = Path(__file__).resolve().parents[3] / "materials" / "data" / "content" / "Captions.yaml"
        if not captions_file.exists():
            self.logger.warning(f"Captions.yaml not found at {captions_file}")
            return {}
        
        with open(captions_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return data.get('captions', {})
    
    def _load_faqs(self) -> Dict[str, Any]:
        """Load FAQs.yaml and return faqs dict."""
        faqs_file = Path(__file__).resolve().parents[3] / "materials" / "data" / "content" / "FAQs.yaml"
        if not faqs_file.exists():
            self.logger.warning(f"FAQs.yaml not found at {faqs_file}")
            return {}
        
        with open(faqs_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return data.get('faqs', {})
    
    def _load_regulatory_standards(self) -> Dict[str, Any]:
        """Load RegulatoryStandards.yaml and return regulatory_standards dict."""
        regulatory_file = Path(__file__).resolve().parents[3] / "materials" / "data" / "content" / "RegulatoryStandards.yaml"
        if not regulatory_file.exists():
            self.logger.warning(f"RegulatoryStandards.yaml not found at {regulatory_file}")
            return {}
        
        with open(regulatory_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return data.get('regulatory_standards', {})
    
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
        filename = f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml"
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
        
        # Define fields that should be exported to frontmatter (per frontmatter_template.yaml)
        EXPORTABLE_FIELDS = {
            'breadcrumb',
            'category', 'subcategory', 'title', 'material_description',
            'datePublished', 'dateModified',  # Schema.org date fields from git history
            'images', 'caption', 'regulatoryStandards', 'eeat',
            'materialProperties', 'machineSettings', 'faq',
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
                # Enrich machine settings with min/max from machine settings ranges
                enriched = self._enrich_machine_settings(value, category_ranges)
                # Remove description fields
                cleaned = self._remove_descriptions(enriched, preserve_regulatory=False)
                # Strip generation metadata
                frontmatter[key] = self._strip_generation_metadata(cleaned)
            elif key in ['caption', 'faq', 'regulatoryStandards']:
                # These fields are orchestrated from separate content files - skip in this loop
                # Will be added after the loop from self.captions, self.faqs, self.regulatory_standards
                continue
            else:
                # Copy as-is but remove description fields and strip generation metadata
                cleaned = self._remove_descriptions(value, preserve_regulatory=False)
                frontmatter[key] = self._strip_generation_metadata(cleaned)
        
        # Orchestrate content from separated content files (Captions.yaml, FAQs.yaml, RegulatoryStandards.yaml)
        # These files were extracted from Materials.yaml for better organization while maintaining single-file output
        
        # Add caption from Captions.yaml
        if material_name in self.captions:
            caption_data = self.captions[material_name]
            cleaned = self._remove_descriptions(caption_data, preserve_regulatory=False)
            stripped = self._strip_generation_metadata(cleaned)
            # Ensure only before/after remain
            if isinstance(stripped, dict):
                frontmatter['caption'] = {
                    k: v for k, v in stripped.items()
                    if k in ['before', 'after']
                }
            else:
                frontmatter['caption'] = stripped
        
        # Add FAQ from FAQs.yaml
        if material_name in self.faqs:
            faq_data = self.faqs[material_name]
            cleaned = self._remove_descriptions(faq_data, preserve_regulatory=False)
            formatted_faq = self._format_faq_with_topics(cleaned)
            frontmatter['faq'] = self._strip_generation_metadata(formatted_faq)
        
        # Add regulatory standards from RegulatoryStandards.yaml
        if material_name in self.regulatory_standards:
            regulatory_data = self.regulatory_standards[material_name]
            normalized = self._normalize_regulatory_standards(regulatory_data)
            frontmatter['regulatoryStandards'] = self._strip_generation_metadata(normalized)
        
        # Add material_challenges from Categories.yaml (category-level diagnostic guidance)
        if category:
            material_challenges = get_material_challenges(category)
            if material_challenges:
                # Strip generation metadata and add to frontmatter
                frontmatter['material_challenges'] = self._strip_generation_metadata(material_challenges)
                self.logger.info(f"✅ Added material_challenges for {material_name} from {category} category")
            else:
                self.logger.debug(f"No material_challenges found for category: {category}")
        
        # Override with components if they exist (new generation system saves to components)
        if 'components' in material_data:
            components = material_data['components']
            # Priority order: components > direct fields
            if 'material_description' in components:
                frontmatter['material_description'] = components['material_description']
            if 'settings_description' in components:
                frontmatter['description'] = components['description']
            if 'caption' in components:
                caption = components['caption']
                cleaned = self._remove_descriptions(caption, preserve_regulatory=False)
                stripped = self._strip_generation_metadata(cleaned)
                if isinstance(stripped, dict):
                    frontmatter['caption'] = {
                        k: v for k, v in stripped.items()
                        if k in ['before', 'after']
                    }
                else:
                    frontmatter['caption'] = stripped
                self.logger.debug(f"Using caption from components")
            if 'faq' in components:
                faq = components['faq']
                cleaned = self._remove_descriptions(faq, preserve_regulatory=False)
                formatted_faq = self._format_faq_with_topics(cleaned)
                frontmatter['faq'] = self._strip_generation_metadata(formatted_faq)
                self.logger.debug(f"Using FAQ from components")
        
        # Export dual-file structure: materials page and settings page
        self._export_materials_page(material_name, frontmatter)
        self._export_settings_page(material_name, frontmatter)
    
    def _export_materials_page(self, material_name: str, full_frontmatter: Dict) -> None:
        """
        Export materials page frontmatter: /materials/{material}-laser-cleaning.yaml
        
        Includes: caption, FAQ, regulatory standards, material properties, images, author
        """
        materials_page = {}
        
        # Core metadata
        materials_page['name'] = full_frontmatter.get('name')
        materials_page['slug'] = material_name.lower().replace(' ', '-')
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
        materials_page['caption'] = full_frontmatter.get('caption')
        materials_page['faq'] = full_frontmatter.get('faq')
        materials_page['regulatoryStandards'] = full_frontmatter.get('regulatoryStandards')
        materials_page['materialProperties'] = full_frontmatter.get('materialProperties')
        materials_page['eeat'] = full_frontmatter.get('eeat')
        materials_page['material_metadata'] = full_frontmatter.get('material_metadata')
        
        # Write materials page YAML
        filename = f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml"
        output_path = self.materials_output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(materials_page, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
        
        # Verify what was written
        if material_name == 'Aluminum':
            with open(output_path, 'r') as f:
                content = f.read()
                for line in content.split('\n')[:10]:
                    if 'material_description:' in line:
                        print(f"✅ [VERIFY] Wrote to file: {line}")
                        break
        
        self.logger.info(f"✅ Exported materials page: {material_name} → {filename}")
    
    def _export_settings_page(self, material_name: str, full_frontmatter: Dict) -> None:
        """
        Export settings page frontmatter: /settings/{material}-settings.yaml
        
        Includes: machine settings, diagnostics (future), challenges (future)
        """
        settings_page = {}
        
        # Core metadata
        settings_page['name'] = full_frontmatter.get('name')
        settings_page['slug'] = material_name.lower().replace(' ', '-')
        settings_page['category'] = full_frontmatter.get('category')
        settings_page['subcategory'] = full_frontmatter.get('subcategory')
        settings_page['content_type'] = 'unified_settings'
        settings_page['schema_version'] = '4.0.0'
        
        # Dates
        settings_page['datePublished'] = full_frontmatter.get('datePublished')
        settings_page['dateModified'] = full_frontmatter.get('dateModified')
        
        # Author (settings pages use professional tone, but same author attribution)
        settings_page['author'] = full_frontmatter.get('author')
        
        # Settings page metadata
        settings_page['title'] = f"{full_frontmatter.get('name')} Laser Cleaning Settings"
        settings_page['subtitle'] = f"Advanced Parameter Configuration and Troubleshooting for {full_frontmatter.get('name')} Laser Cleaning Systems"
        settings_page['settings_description'] = full_frontmatter.get('settings_description', f"Detailed machine settings, parameter relationships, diagnostic procedures, and troubleshooting guides for optimizing {full_frontmatter.get('name').lower()} laser cleaning operations.")
        
        # Settings-specific breadcrumb
        category = full_frontmatter.get('category', '')
        subcategory = full_frontmatter.get('subcategory', '')
        breadcrumb = [
            {'label': 'Home', 'href': '/'},
            {'label': 'Settings', 'href': '/settings'}
        ]
        
        if category:
            breadcrumb.append({
                'label': category.replace('_', ' ').title(),
                'href': f'/settings/{category}'
            })
        
        if subcategory:
            breadcrumb.append({
                'label': subcategory.replace('_', ' ').replace('-', ' ').title(),
                'href': f'/settings/{category}/{subcategory}'
            })
        
        breadcrumb.append({
            'label': full_frontmatter.get('name'),
            'href': f'/settings/{settings_page["slug"]}'
        })
        
        settings_page['breadcrumb'] = breadcrumb
        
        # Images (shared between pages)
        settings_page['images'] = full_frontmatter.get('images')
        
        # Content (settings page specific)
        settings_page['machineSettings'] = full_frontmatter.get('machineSettings')
        
        # Add material_challenges (category-level diagnostic guidance)
        settings_page['material_challenges'] = full_frontmatter.get('material_challenges')
        
        # Write settings page YAML
        filename = f"{material_name.lower().replace(' ', '-')}-settings.yaml"
        output_path = self.settings_output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(settings_page, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
        
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
    
    def _add_min_max(self, prop_value: Any, prop_name: str, category_ranges: Dict) -> Any:
        """Add min/max fields to a property if available in category ranges."""
        if not isinstance(prop_value, dict):
            return prop_value
        
        # Already has min/max - don't override
        if 'min' in prop_value or 'max' in prop_value:
            return prop_value
        
        # Look up category range
        range_data = category_ranges.get(prop_name, {})
        if not range_data or not isinstance(range_data, dict):
            return prop_value
        
        # Create enriched property with min/max - use shallow copy to preserve structure
        enriched = prop_value.copy()
        if 'min' in range_data:
            enriched['min'] = range_data['min']
        if 'max' in range_data:
            enriched['max'] = range_data['max']
        
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
            'author', 'generation_method'  # Caption-specific metadata
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
    
    def _generate_breadcrumb(self, material_data: Dict, slug: str) -> list:
        """
        Generate breadcrumb navigation for materials.
        
        Hierarchy: Home → Materials → Category → Subcategory → Material
        
        Example for Aluminum (category: metal, subcategory: non-ferrous):
          - Home → /
          - Materials → /materials
          - Metal → /materials/metals
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
        
        # Add Category level (pluralized for listing page)
        if category:
            category_label = category.replace('-', ' ').replace('_', ' ').title()
            breadcrumb.append({
                "label": category_label,
                "href": f"/materials/{category.lower()}s"  # Pluralized: /materials/metals
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
            if subcategory:
                material_slug = name.lower().replace(' ', '-')
                final_href = f"/materials/{category.lower()}/{subcategory.lower()}/{material_slug}"
            else:
                material_slug = name.lower().replace(' ', '-')
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
