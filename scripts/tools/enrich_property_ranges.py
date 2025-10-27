#!/usr/bin/env python3
"""
Property Range Enrichment Tool

PURPOSE: Apply Categories.yaml ranges to Materials.yaml properties missing min/max.

PROBLEM: 2,438 properties (66%) have null min/max ranges after structure migration.
SOLUTION: Load category_ranges from Categories.yaml and apply to null properties.

POLICY: Zero Null Policy - All quantitative properties MUST have non-null min/max ranges.

OPERATION:
1. Load Categories.yaml category_ranges for all categories
2. Load Materials.yaml with hierarchical materialProperties
3. For each material, iterate through materialProperties sections
4. For each property with null min/max, lookup category range
5. Apply min/max values while preserving value/confidence/research_basis
6. Backup Materials.yaml before modifications
7. Save enriched Materials.yaml
8. Report statistics (properties enriched, missing ranges, etc.)

NO FALLBACKS - Only apply ranges that exist in Categories.yaml.
NO DEFAULTS - If category range missing, log warning but don't make up values.

Author: Range Enrichment - October 26, 2025
"""

import yaml
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class PropertyRangeEnricher:
    """Apply Categories.yaml ranges to Materials.yaml properties missing min/max."""
    
    # Property name aliases (unified property name → legacy names)
    PROPERTY_ALIASES = {
        'thermalDestruction': ['meltingPoint', 'degradationPoint', 'thermalDegradationPoint', 
                               'sinteringPoint', 'softeningPoint', 'carbonizationPoint']
    }
    
    def __init__(self):
        """Initialize with data file paths."""
        self.base_dir = Path(__file__).resolve().parents[2]
        self.materials_path = self.base_dir / "data" / "Materials.yaml"
        self.categories_path = self.base_dir / "data" / "Categories.yaml"
        
        # Validate files exist
        if not self.materials_path.exists():
            raise FileNotFoundError(f"Materials.yaml not found: {self.materials_path}")
        if not self.categories_path.exists():
            raise FileNotFoundError(f"Categories.yaml not found: {self.categories_path}")
        
        # Load data
        self.materials_data = self._load_yaml(self.materials_path)
        self.categories_data = self._load_yaml(self.categories_path)
        
        # Extract category ranges for quick lookup
        self.category_ranges = self._extract_category_ranges()
        
        # Statistics tracking
        self.stats = {
            'total_properties': 0,
            'null_ranges_found': 0,
            'ranges_applied': 0,
            'ranges_missing': 0,
            'materials_modified': 0,
            'missing_by_category': defaultdict(set),  # category -> set of property names
            'applied_by_category': defaultdict(int)   # category -> count
        }
    
    def _load_yaml(self, path: Path) -> Dict:
        """Load YAML file with error handling."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load {path}: {e}")
    
    def _save_yaml(self, path: Path, data: Dict) -> None:
        """Save YAML file with proper formatting."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to save {path}: {e}")
    
    def _extract_category_ranges(self) -> Dict[str, Dict[str, Dict]]:
        """
        Extract category_ranges from Categories.yaml.
        
        Returns:
            Dict mapping category -> property_name -> {min, max, unit}
        """
        ranges = {}
        categories = self.categories_data.get('categories', {})
        
        for category_name, category_data in categories.items():
            category_ranges = category_data.get('category_ranges', {})
            if category_ranges:
                ranges[category_name] = category_ranges
                logger.info(f"📊 Loaded {len(category_ranges)} ranges for '{category_name}'")
        
        return ranges
    
    def _get_category_range(self, category: str, property_name: str) -> Optional[Dict]:
        """
        Lookup category range for property with alias resolution.
        
        Args:
            category: Material category (metal, ceramic, stone, etc.)
            property_name: Property name (density, hardness, thermalDestruction, etc.)
        
        Returns:
            Dict with min/max/unit or None if not found
        """
        category_ranges = self.category_ranges.get(category, {})
        
        # Try direct lookup first
        range_data = category_ranges.get(property_name)
        
        # If not found and property has aliases, try them
        if not range_data:
            for unified_name, aliases in self.PROPERTY_ALIASES.items():
                if property_name in aliases:
                    # Property is an alias, lookup unified name
                    range_data = category_ranges.get(unified_name)
                    if range_data:
                        logger.debug(f"Resolved alias '{property_name}' → '{unified_name}'")
                        break
        
        # Handle nested structure for thermalDestruction
        if range_data and 'point' in range_data and isinstance(range_data['point'], dict):
            # Extract min/max/unit from nested 'point' structure
            point = range_data['point']
            return {
                'min': point.get('min'),
                'max': point.get('max'),
                'unit': point.get('unit')
            }
        
        return range_data
    
    def _backup_materials(self) -> Path:
        """Create timestamped backup of Materials.yaml."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.base_dir / "data" / f"Materials.backup_{timestamp}.yaml"
        
        self._save_yaml(backup_path, self.materials_data)
        logger.info(f"💾 Backup created: {backup_path.name}")
        
        return backup_path
    
    def _enrich_property(
        self,
        property_data: Dict,
        property_name: str,
        category: str
    ) -> bool:
        """
        Enrich single property with category range if missing.
        
        Args:
            property_data: Property dict with value/min/max/unit/etc.
            property_name: Name of the property
            category: Material category
        
        Returns:
            True if range was applied, False otherwise
        """
        self.stats['total_properties'] += 1
        
        # Check if min/max are null
        has_min = property_data.get('min') is not None
        has_max = property_data.get('max') is not None
        
        if has_min and has_max:
            return False  # Already has ranges
        
        self.stats['null_ranges_found'] += 1
        
        # Lookup category range
        category_range = self._get_category_range(category, property_name)
        
        if not category_range:
            # No category range available
            self.stats['ranges_missing'] += 1
            self.stats['missing_by_category'][category].add(property_name)
            logger.warning(
                f"⚠️  No category range for '{property_name}' in '{category}' category"
            )
            return False
        
        # Validate category range has required fields
        if 'min' not in category_range or 'max' not in category_range:
            self.stats['ranges_missing'] += 1
            self.stats['missing_by_category'][category].add(property_name)
            logger.warning(
                f"⚠️  Invalid category range for '{property_name}' in '{category}' (missing min/max)"
            )
            return False
        
        # Apply range
        property_data['min'] = category_range['min']
        property_data['max'] = category_range['max']
        
        # Ensure unit matches (use category unit if property unit is missing)
        if not property_data.get('unit') and category_range.get('unit'):
            property_data['unit'] = category_range['unit']
        
        self.stats['ranges_applied'] += 1
        self.stats['applied_by_category'][category] += 1
        
        logger.debug(
            f"✅ Applied range to '{property_name}': "
            f"min={category_range['min']}, max={category_range['max']}"
        )
        
        return True
    
    def _enrich_material_properties(
        self,
        material_name: str,
        material_data: Dict
    ) -> int:
        """
        Enrich all properties in a material.
        
        Args:
            material_name: Name of the material
            material_data: Material data dict
        
        Returns:
            Number of properties enriched
        """
        category = material_data.get('category')
        if not category:
            logger.warning(f"⚠️  Material '{material_name}' has no category")
            return 0
        
        material_properties = material_data.get('materialProperties', {})
        if not material_properties:
            return 0
        
        enriched_count = 0
        
        # Process material_characteristics
        mat_char = material_properties.get('material_characteristics', {})
        mat_char_props = mat_char.get('properties', {})
        
        for prop_name, prop_data in mat_char_props.items():
            if isinstance(prop_data, dict):
                if self._enrich_property(prop_data, prop_name, category):
                    enriched_count += 1
        
        # Process laser_material_interaction
        laser_int = material_properties.get('laser_material_interaction', {})
        laser_int_props = laser_int.get('properties', {})
        
        for prop_name, prop_data in laser_int_props.items():
            if isinstance(prop_data, dict):
                if self._enrich_property(prop_data, prop_name, category):
                    enriched_count += 1
        
        return enriched_count
    
    def enrich_all_materials(self) -> None:
        """Enrich all materials with category ranges."""
        logger.info("=" * 80)
        logger.info("PROPERTY RANGE ENRICHMENT")
        logger.info("=" * 80)
        logger.info("")
        
        # Backup before modifications
        self._backup_materials()
        
        # Process each material
        materials = self.materials_data.get('materials', {})
        total_materials = len(materials)
        
        logger.info(f"📦 Processing {total_materials} materials...")
        logger.info("")
        
        for material_name, material_data in materials.items():
            enriched_count = self._enrich_material_properties(material_name, material_data)
            if enriched_count > 0:
                self.stats['materials_modified'] += 1
                logger.info(f"✅ {material_name}: {enriched_count} properties enriched")
        
        # Save enriched data
        logger.info("")
        logger.info("💾 Saving enriched Materials.yaml...")
        self._save_yaml(self.materials_path, self.materials_data)
        
        # Print statistics
        self._print_statistics()
    
    def _print_statistics(self) -> None:
        """Print enrichment statistics."""
        logger.info("")
        logger.info("=" * 80)
        logger.info("ENRICHMENT STATISTICS")
        logger.info("=" * 80)
        logger.info("")
        
        logger.info(f"📊 Total properties processed: {self.stats['total_properties']}")
        logger.info(f"🔍 Properties with null ranges: {self.stats['null_ranges_found']}")
        logger.info(f"✅ Ranges applied: {self.stats['ranges_applied']}")
        logger.info(f"⚠️  Ranges missing: {self.stats['ranges_missing']}")
        logger.info(f"📦 Materials modified: {self.stats['materials_modified']}")
        logger.info("")
        
        # Percentage calculations
        if self.stats['null_ranges_found'] > 0:
            enrichment_rate = (self.stats['ranges_applied'] / self.stats['null_ranges_found']) * 100
            logger.info(f"📈 Enrichment rate: {enrichment_rate:.1f}%")
            logger.info("")
        
        # Ranges applied by category
        if self.stats['applied_by_category']:
            logger.info("📊 Ranges applied by category:")
            for category, count in sorted(self.stats['applied_by_category'].items()):
                logger.info(f"   {category}: {count} properties")
            logger.info("")
        
        # Missing ranges by category
        if self.stats['missing_by_category']:
            logger.info("⚠️  Missing category ranges:")
            for category, props in sorted(self.stats['missing_by_category'].items()):
                logger.info(f"   {category}: {', '.join(sorted(props))}")
            logger.info("")
        
        # Final status
        remaining_null = self.stats['null_ranges_found'] - self.stats['ranges_applied']
        if remaining_null == 0:
            logger.info("✅ SUCCESS: All properties now have ranges (Zero Null Policy compliant)")
        else:
            logger.info(f"⚠️  WARNING: {remaining_null} properties still have null ranges")
            logger.info("   These properties need category ranges added to Categories.yaml")
        
        logger.info("")
        logger.info("=" * 80)


def main():
    """Main entry point."""
    try:
        enricher = PropertyRangeEnricher()
        enricher.enrich_all_materials()
    except Exception as e:
        logger.error(f"❌ Enrichment failed: {e}")
        raise


if __name__ == "__main__":
    main()
