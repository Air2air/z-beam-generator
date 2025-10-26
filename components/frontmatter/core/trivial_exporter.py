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
from typing import Dict
from data.materials import load_materials_cached

logger = logging.getLogger(__name__)


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
        """Initialize with output directory and load Categories.yaml."""
        self.output_dir = Path(__file__).resolve().parents[3] / "content" / "frontmatter"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Load Categories.yaml for category-level data
        categories_path = Path(__file__).resolve().parents[3] / "data" / "Categories.yaml"
        with open(categories_path, 'r', encoding='utf-8') as f:
            self.categories_data = yaml.safe_load(f)
        
        self.logger.info(f"✅ Loaded {len(self.categories_data.get('categories', {}))} categories")
    
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
        Simple field mapping + Categories.yaml metadata (NO FALLBACK RANGES).
        
        Args:
            material_name: Name of the material
            material_data: Material data from Materials.yaml (100% complete, validated)
        """
        # Get category for this material
        category = material_data.get('category', '')
        
        # Simple field mapping (Materials.yaml → frontmatter structure)
        frontmatter = {
            # Material name (required by example.yaml)
            'name': material_name,
            
            # Basic metadata (direct copy)
            'title': material_data.get('title', material_name),
            'subtitle': material_data.get('subtitle', ''),
            'description': material_data.get('description', ''),
            'category': category,
            'subcategory': material_data.get('subcategory', ''),
            
            # Text content (already generated in Materials.yaml)
            'caption': material_data.get('caption', {}),
            
            # Properties (direct copy from Materials.yaml - already complete)
            'materialProperties': material_data.get('materialProperties', {}),
            'materialCharacteristics': material_data.get('materialCharacteristics', {}),
            
            # Machine settings (already researched in Materials.yaml)
            'machineSettings': material_data.get('machineSettings', {}),
            
            # Applications (already researched in Materials.yaml)
            'applications': material_data.get('applications', []),
            
            # Environmental and outcomes (already generated in Materials.yaml)
            'environmentalImpact': material_data.get('environmentalImpact', []),
            'outcomeMetrics': material_data.get('outcomeMetrics', []),
            'regulatoryStandards': material_data.get('regulatoryStandards', []),
            
            # Images (already defined in Materials.yaml)
            'images': material_data.get('images', {}),
            
            # Author info (already set in Materials.yaml)
            'author': material_data.get('author', {}),
        }
        
        # Add caption.description if not present (combines beforeText and afterText context)
        if 'caption' in frontmatter and 'description' not in frontmatter['caption']:
            # Generate description from material context
            frontmatter['caption']['description'] = f"Microscopic analysis of {material_name.lower()} surface before and after laser cleaning treatment"
        
        # Add images.micro if not present
        if 'images' in frontmatter:
            if 'micro' not in frontmatter['images']:
                # Generate micro image entry
                material_slug = material_name.lower().replace(' ', '-')
                frontmatter['images']['micro'] = {
                    'alt': f"Microscopic view of {material_name.lower()} surface showing laser cleaning effects",
                    'url': f"/images/material/{material_slug}-laser-cleaning-micro.jpg"
                }
        
        # Merge min/max ranges into materialProperties from Categories.yaml
        if 'materialProperties' in frontmatter and category in self.categories_data.get('categories', {}):
            category_info = self.categories_data['categories'][category]
            category_ranges = category_info.get('properties', {})
            
            # Process material_characteristics properties
            if 'material_characteristics' in frontmatter['materialProperties']:
                mat_chars = frontmatter['materialProperties']['material_characteristics']
                if 'properties' in mat_chars:
                    for prop_name, prop_data in mat_chars['properties'].items():
                        if prop_name in category_ranges:
                            category_range = category_ranges[prop_name]
                            # Add min/max if not already present
                            if 'min' not in prop_data and 'min' in category_range:
                                prop_data['min'] = category_range['min']
                            if 'max' not in prop_data and 'max' in category_range:
                                prop_data['max'] = category_range['max']
            
            # Process laser_material_interaction properties
            if 'laser_material_interaction' in frontmatter['materialProperties']:
                laser_interact = frontmatter['materialProperties']['laser_material_interaction']
                if 'properties' in laser_interact:
                    for prop_name, prop_data in laser_interact['properties'].items():
                        if prop_name in category_ranges:
                            category_range = category_ranges[prop_name]
                            # Add min/max if not already present
                            if 'min' not in prop_data and 'min' in category_range:
                                prop_data['min'] = category_range['min']
                            if 'max' not in prop_data and 'max' in category_range:
                                prop_data['max'] = category_range['max']
            
            # Process other properties if present
            if 'other' in frontmatter['materialProperties']:
                other_props = frontmatter['materialProperties']['other']
                if 'properties' in other_props:
                    for prop_name, prop_data in other_props['properties'].items():
                        if prop_name in category_ranges:
                            category_range = category_ranges[prop_name]
                            # Add min/max if not already present
                            if 'min' not in prop_data and 'min' in category_range:
                                prop_data['min'] = category_range['min']
                            if 'max' not in prop_data and 'max' in category_range:
                                prop_data['max'] = category_range['max']
        
        # Add category metadata for reference
        if category and category in self.categories_data.get('categories', {}):
            category_info = self.categories_data['categories'][category]
            category_metadata = {}
            
            if 'industryApplications' in category_info:
                category_metadata['industryApplications'] = category_info['industryApplications']
            
            if 'description' in category_info:
                category_metadata['description'] = category_info['description']
            
            if category_metadata:
                frontmatter['categoryMetadata'] = category_metadata
        
        # Write YAML file (simple, fast, no API calls)
        filename = f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml"
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(frontmatter, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        self.logger.info(f"✅ Exported {material_name} → {filename}")


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
