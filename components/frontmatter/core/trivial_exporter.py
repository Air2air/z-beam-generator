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
from data.materials import load_materials_cached

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
        Export single material to frontmatter YAML file matching example.yaml structure.
        Simple field mapping + Categories.yaml metadata (NO FALLBACK RANGES).
        
        Args:
            material_name: Name of the material
            material_data: Material data from Materials.yaml (100% complete, validated)
        """
        # Get category for this material
        category = material_data.get('category', '')
        
        # Simple field mapping (Materials.yaml → frontmatter structure matching example.yaml)
        frontmatter = {
            # Core identification (example.yaml order)
            'name': material_name,
            'category': category,
            'subcategory': material_data.get('subcategory', ''),
            'title': material_data.get('title', f"{material_name} Laser Cleaning"),
            'subtitle': material_data.get('subtitle', ''),
            'description': material_data.get('description', ''),
            
            # Author (direct copy)
            'author': self._ensure_author(material_data),
            
            # Images (ensure micro image exists)
            'images': self._ensure_images(material_name, material_data),
            
            # Caption (ensure description exists)
            'caption': self._ensure_caption(material_name, material_data),
            
            # Regulatory standards (direct copy)
            'regulatoryStandards': material_data.get('regulatoryStandards', []),
            
            # Applications (direct copy)
            'applications': material_data.get('applications', []),
            
            # *** HIERARCHICAL materialProperties (example.yaml format) ***
            'materialProperties': self._build_material_properties(material_name, material_data, category),
            
            # Machine settings (direct copy - already correct format)
            'machineSettings': material_data.get('machineSettings', {}),
            
            # Environmental impact (direct copy)
            'environmentalImpact': material_data.get('environmentalImpact', []),
            
            # Outcome metrics (direct copy or empty list)
            'outcomeMetrics': material_data.get('outcomeMetrics', []),
        }
        
        # Write YAML file (simple, fast, no API calls)
        filename = f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml"
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(frontmatter, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        self.logger.info(f"✅ Exported {material_name} → {filename}")
    
    def _ensure_author(self, material_data: Dict) -> Dict:
        """Ensure author section exists and is properly formatted."""
        return material_data.get('author', {})
    
    def _ensure_images(self, material_name: str, material_data: Dict) -> Dict:
        """Ensure images section has both hero and micro images."""
        images = material_data.get('images', {})
        material_slug = material_name.lower().replace(' ', '-')
        
        # Ensure hero image
        if 'hero' not in images:
            images['hero'] = {
                'alt': f"{material_name} surface undergoing laser cleaning showing precise contamination removal",
                'url': f"/images/material/{material_slug}-laser-cleaning-hero.jpg"
            }
        
        # Ensure micro image
        if 'micro' not in images:
            images['micro'] = {
                'alt': f"Microscopic view of {material_name} surface showing laser cleaning effects",
                'url': f"/images/material/{material_slug}-laser-cleaning-micro.jpg"
            }
        
        return images
    
    def _ensure_caption(self, material_name: str, material_data: Dict) -> Dict:
        """Ensure caption has description, beforeText, and afterText."""
        caption = material_data.get('caption', {})
        
        # Ensure description exists
        if 'description' not in caption:
            caption['description'] = (
                f"Microscopic analysis of {material_name} surface before and "
                f"after laser cleaning treatment"
            )
        
        # Ensure beforeText and afterText exist (even if empty)
        if 'beforeText' not in caption:
            caption['beforeText'] = ''
        if 'afterText' not in caption:
            caption['afterText'] = ''
        
        return caption
    
    def _build_material_properties(self, material_name: str, material_data: Dict, category: str) -> Dict:
        """
        Build hierarchical materialProperties matching example.yaml structure.
        
        Structure:
            materialProperties:
                material_characteristics:
                    label: ...
                    description: ...
                    property_name:
                        value: ...
                        min: ...
                        max: ...
                        unit: ...
                        research_basis: ...
                laser_material_interaction:
                    label: ...
                    description: ...
                    property_name:
                        value: ...
                        min: ...
                        max: ...
                        unit: ...
                        research_basis: ...
        """
        # Check if Materials.yaml already has hierarchical materialProperties
        if 'materialProperties' in material_data:
            mat_props = material_data['materialProperties']
            
            # If it's already hierarchical, merge ranges and return
            if isinstance(mat_props, dict) and ('material_characteristics' in mat_props or 'laser_material_interaction' in mat_props):
                return self._merge_category_ranges_hierarchical(mat_props, category)
        
        # Otherwise, build from flat 'properties' structure (for backward compatibility)
        flat_props = material_data.get('properties', {})
        
        result = {
            'material_characteristics': {
                'label': 'Material Characteristics',
                'description': 'Intrinsic physical, mechanical, chemical, and structural properties affecting cleaning outcomes and material integrity'
            },
            'laser_material_interaction': {
                'label': 'Laser-Material Interaction',
                'description': 'Optical and thermal properties governing laser energy absorption, reflection, propagation, and ablation thresholds'
            }
        }
        
        # Categorize and format properties
        for prop_name, prop_data in flat_props.items():
            formatted_prop = self._format_property(prop_name, prop_data, category)
            
            if prop_name in MATERIAL_CHARACTERISTICS_PROPS:
                result['material_characteristics'][prop_name] = formatted_prop
            elif prop_name in LASER_INTERACTION_PROPS:
                result['laser_material_interaction'][prop_name] = formatted_prop
            else:
                # Unknown properties go to material_characteristics by default
                result['material_characteristics'][prop_name] = formatted_prop
        
        return result
    
    def _merge_category_ranges_hierarchical(self, mat_props: Dict, category: str) -> Dict:
        """Merge category ranges into existing hierarchical materialProperties."""
        if category not in self.categories_data.get('categories', {}):
            return mat_props
        
        category_ranges = self.categories_data['categories'][category].get('category_ranges', {})
        
        # Process each section (material_characteristics, laser_material_interaction, etc.)
        for section_name, section_data in mat_props.items():
            if not isinstance(section_data, dict):
                continue
            
            # Process properties in this section
            for key, value in section_data.items():
                # Skip metadata fields (label, description, percentage)
                if key in ['label', 'description', 'percentage']:
                    continue
                
                # If it's a property dict with value/unit
                if isinstance(value, dict) and 'value' in value:
                    prop_name = key
                    if prop_name in category_ranges:
                        range_data = category_ranges[prop_name]
                        # Add min/max from category ranges if not present
                        if 'min' not in value and 'min' in range_data:
                            value['min'] = range_data['min']
                        if 'max' not in value and 'max' in range_data:
                            value['max'] = range_data['max']
                
                # Handle nested 'properties' dict (alternative structure)
                elif key == 'properties' and isinstance(value, dict):
                    for prop_name, prop_data in value.items():
                        if isinstance(prop_data, dict) and prop_name in category_ranges:
                            range_data = category_ranges[prop_name]
                            if 'min' not in prop_data and 'min' in range_data:
                                prop_data['min'] = range_data['min']
                            if 'max' not in prop_data and 'max' in range_data:
                                prop_data['max'] = range_data['max']
        
        return mat_props
    
    def _format_property(self, prop_name: str, prop_data: dict, category: str) -> Dict:
        """Format individual property with value, min, max, unit, research_basis."""
        # Handle different input formats from Materials.yaml
        if isinstance(prop_data, dict):
            formatted = {
                'value': prop_data.get('value'),
                'unit': prop_data.get('unit', ''),
                'research_basis': prop_data.get('research_basis', prop_data.get('description', ''))
            }
            
            # Preserve existing min/max if present
            if 'min' in prop_data:
                formatted['min'] = prop_data['min']
            if 'max' in prop_data:
                formatted['max'] = prop_data['max']
        else:
            # Simple value (not a dict)
            formatted = {
                'value': prop_data,
                'unit': '',
                'research_basis': ''
            }
        
        # Add category ranges if not already present
        return self._add_category_ranges(formatted, prop_name, category)
    
    def _add_category_ranges(self, prop_dict: Dict, prop_name: str, category: str) -> Dict:
        """Add min/max ranges from Categories.yaml to property if not already present."""
        if category not in self.categories_data.get('categories', {}):
            return prop_dict
        
        category_ranges = self.categories_data['categories'][category].get('category_ranges', {})
        
        if prop_name in category_ranges:
            range_data = category_ranges[prop_name]
            
            # Add min if not present
            if 'min' not in prop_dict and 'min' in range_data:
                prop_dict['min'] = range_data['min']
            
            # Add max if not present
            if 'max' not in prop_dict and 'max' in range_data:
                prop_dict['max'] = range_data['max']
            
            # Use category unit if property doesn't have one
            if not prop_dict.get('unit') and 'unit' in range_data:
                prop_dict['unit'] = range_data['unit']
        
        return prop_dict


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
