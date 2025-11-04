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
from materials.data.materials import load_materials_cached

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
        """Initialize with output directory, load Categories.yaml for taxonomy and ranges."""
        self.output_dir = Path(__file__).resolve().parents[3] / "frontmatter" / "materials"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Load Categories.yaml for taxonomy, category ranges, and machine settings ranges
        categories_path = Path(__file__).resolve().parents[3] / "materials" / "data" / "Categories.yaml"
        with open(categories_path, 'r', encoding='utf-8') as f:
            self.categories_data = yaml.safe_load(f)
        
        # Extract machine settings ranges from Categories.yaml
        self.machine_settings_ranges = self.categories_data.get('machineSettingsRanges', {})
        
        # Load property taxonomy for categorization
        self._load_property_taxonomy()
        
        self.logger.info(f"✅ Loaded {len(self.categories_data.get('categories', {}))} material categories")
        self.logger.info(f"✅ Loaded {len(self.machine_settings_ranges)} machine settings ranges")
        self.logger.info(f"✅ Loaded property taxonomy with {len(self.property_taxonomy)} categories")
    
    def _load_property_taxonomy(self):
        """Load property taxonomy from Categories.yaml to categorize properties correctly."""
        # The taxonomy is nested under 'propertyTaxonomy' key in Categories.yaml
        # Search for it in the data structure
        taxonomy_data = None
        
        for key, value in self.categories_data.items():
            if isinstance(value, dict) and 'categories' in value:
                categories = value['categories']
                if 'material_characteristics' in categories and 'laser_material_interaction' in categories:
                    taxonomy_data = value
                    break
        
        # If not found in nested structure, check root level
        if not taxonomy_data:
            if 'propertyTaxonomy' in self.categories_data:
                taxonomy_data = self.categories_data['propertyTaxonomy']
            else:
                taxonomy_data = self.categories_data
        
        # Extract property categories (material_characteristics, laser_material_interaction)
        categories = taxonomy_data.get('categories', {})
        
        # Build taxonomy mapping: property_name -> category_id
        self.property_taxonomy = {}
        metadata_keys = {'label', 'description', 'percentage'}
        for cat_id in ['material_characteristics', 'laser_material_interaction']:
            if cat_id in categories:
                cat_data = categories[cat_id]
                # Properties are directly in category (flat structure, excluding metadata)
                if isinstance(cat_data, dict):
                    for prop in cat_data.keys():
                        if prop not in metadata_keys:
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
        
        # Define fields that should be exported to frontmatter (per frontmatter_template.yaml)
        EXPORTABLE_FIELDS = {
            'category', 'subcategory', 'title', 'subtitle',
            'author', 'images', 'caption', 'regulatoryStandards',
            'materialProperties', 'machineSettings', 'faq',
            'material_metadata', 'subtitle_metadata'
        }
        
        # Copy only exportable fields from Materials.yaml
        for key, value in material_data.items():
            if key not in EXPORTABLE_FIELDS:
                # Skip fields that shouldn't be in frontmatter (applications, materialCharacteristics, environmentalImpact, outcomeMetrics, etc.)
                continue
            
            if key == 'materialProperties':
                # Enrich material properties with min/max from category ranges
                enriched = self._enrich_material_properties(value, category_ranges)
                # Remove description fields except from regulatoryStandards
                frontmatter[key] = self._remove_descriptions(enriched, preserve_regulatory=False)
            elif key == 'machineSettings':
                # Enrich machine settings with min/max from machine settings ranges
                enriched = self._enrich_machine_settings(value, category_ranges)
                # Remove description fields
                frontmatter[key] = self._remove_descriptions(enriched, preserve_regulatory=False)
            elif key == 'regulatoryStandards':
                # Keep descriptions in regulatoryStandards
                frontmatter[key] = value
            else:
                # Copy as-is but remove description fields
                frontmatter[key] = self._remove_descriptions(value, preserve_regulatory=(key == 'regulatoryStandards'))
        
        # Write YAML file
        filename = f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml"
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(frontmatter, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
        
        self.logger.info(f"✅ Exported {material_name} → {filename}")
    
    def _get_category_ranges(self, category: str) -> Dict[str, Any]:
        """Get category-wide ranges from Categories.yaml."""
        if not category or 'categories' not in self.categories_data:
            return {}
        
        category_data = self.categories_data['categories'].get(category, {})
        return category_data.get('category_ranges', {})
    
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


def export_all_frontmatter() -> Dict[str, bool]:
    """
    Convenience function to export all frontmatter files.
    
    Usage:
        from components.frontmatter.core.trivial_exporter import export_all_frontmatter
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
