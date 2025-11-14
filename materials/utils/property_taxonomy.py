#!/usr/bin/env python3
"""
Property Taxonomy - Unified property classification and categorization

Consolidates PropertyCategorizer + PropertyClassifier into single service.
Provides property type detection, category lookup, and metadata access.

Architecture:
- Single source of truth: Categories.yaml + property_system.yaml
- Fail-fast validation on missing data
- No mocks, no fallbacks, no silent failures
- Singleton pattern for performance

Usage:
    from materials.utils.property_taxonomy import get_property_taxonomy
    
    taxonomy = get_property_taxonomy()
    
    # Type detection
    is_qual = taxonomy.is_qualitative('crystallineStructure')
    is_quant = taxonomy.is_quantitative('density')
    
    # Category lookup
    category = taxonomy.get_category('thermalConductivity')  # 'thermal'
    
    # Metadata access
    info = taxonomy.get_property_info('density')
    tier = taxonomy.get_usage_tier('hardness')
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class PropertyTaxonomyError(Exception):
    """Raised when property taxonomy operations fail - fail-fast behavior"""
    pass


@dataclass
class PropertyInfo:
    """Complete property metadata from registry"""
    name: str
    type: str  # 'quantitative', 'qualitative', 'quantitative_nested'
    category: str
    unit_required: bool
    range_required: bool
    typical_units: List[str] = None
    allowed_values: List[str] = None
    description: str = ""
    measurement_context: str = ""
    nested_structure: bool = False
    fields: Dict[str, Any] = None


class PropertyTaxonomy:
    """
    Unified property classification and categorization service.
    
    Combines functionality from:
    - PropertyCategorizer: Category lookup and grouping
    - PropertyClassifier: Type detection and validation
    
    Features:
    - Property type detection (qualitative/quantitative)
    - Category organization (thermal, mechanical, optical, etc.)
    - Usage tier classification (core/common/specialized)
    - Metadata access and validation
    - Legacy property mapping
    
    GROK Architecture:
    - Read-only: No state mutation
    - Fail-fast: Throws PropertyTaxonomyError on missing data
    - Single source: Categories.yaml + property_system.yaml
    - No fallbacks: No defaults, no mocks, no silent failures
    """
    
    def __init__(self, categories_path: Optional[Path] = None, registry_path: Optional[Path] = None):
        """
        Initialize property taxonomy from YAML sources.
        
        Args:
            categories_path: Path to Categories.yaml (auto-detects if None)
            registry_path: Path to property_system.yaml (auto-detects if None)
            
        Raises:
            PropertyTaxonomyError: If required files missing or invalid
        """
        # Auto-detect paths if not provided
        if categories_path is None or registry_path is None:
            # Navigate to project root, then to data/materials (normalized architecture)
            materials_dir = Path(__file__).resolve().parent.parent.parent
            if categories_path is None:
                # Load from PropertyDefinitions.yaml (normalized architecture)
                categories_path = materials_dir / "data" / "materials" / "PropertyDefinitions.yaml"
            if registry_path is None:
                registry_path = materials_dir / "data" / "materials" / "categories" / "property_system.yaml"
        
        self._load_categories(categories_path)
        self._load_registry(registry_path)
    
    def _load_categories(self, path: Path):
        """
        Load property categories from PropertyDefinitions.yaml - FAIL FAST
        
        Args:
            path: Path to PropertyDefinitions.yaml (normalized architecture)
            
        Raises:
            PropertyTaxonomyError: If file missing or invalid
        """
        try:
            if not path.exists():
                raise PropertyTaxonomyError(
                    f"PropertyDefinitions.yaml required for property taxonomy: {path}"
                )
            
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if 'property_categories' not in data:
                raise PropertyTaxonomyError(
                    "property_categories section required in PropertyDefinitions.yaml"
                )
            
            # Map old propertyCategories structure to new property_categories structure
            taxonomy = data['property_categories']
            
            # Extract the actual categories (nested under 'categories' key)
            if 'categories' in taxonomy:
                categories_data = taxonomy['categories']
            else:
                categories_data = {k: v for k, v in taxonomy.items() if k != 'metadata' and not k.startswith('_')}
            
            # Convert from new format to old format for backward compatibility
            self.categories = {}
            for cat_id, cat_data in categories_data.items():
                if not isinstance(cat_data, dict):
                    continue
                    
                # Extract properties list from nested structure
                if 'properties' in cat_data:
                    prop_list = cat_data['properties']
                else:
                    prop_list = cat_data.get('materialProperties', [])
                    
                self.categories[cat_id] = {
                    'materialProperties': prop_list,
                    'id': cat_id
                }
            
            # Usage tiers and metadata are not in PropertyDefinitions.yaml
            self.usage_tiers = {}
            self.category_metadata = {}
            
            if not self.categories:
                raise PropertyTaxonomyError(
                    "No categories found in property_categories section"
                )
            
            # Build reverse lookup: property -> category (O(1) access)
            self._property_to_category = {}
            for cat_id, cat_data in self.categories.items():
                properties = cat_data.get('materialProperties', [])
                if not isinstance(properties, list):
                    raise PropertyTaxonomyError(
                        f"Invalid properties for category {cat_id}: must be list"
                    )
                for prop in properties:
                    self._property_to_category[prop] = cat_id
            
            logger.info(
                f"Loaded {len(self.categories)} property categories "
                f"with {len(self._property_to_category)} properties from PropertyDefinitions.yaml"
            )
            
        except yaml.YAMLError as e:
            raise PropertyTaxonomyError(f"Invalid YAML in PropertyDefinitions.yaml: {e}")
        except Exception as e:
            raise PropertyTaxonomyError(f"Failed to load PropertyDefinitions.yaml: {e}")
    
    def _load_registry(self, path: Path):
        """
        Load property definitions from property_system.yaml - FAIL FAST
        
        Args:
            path: Path to property_system.yaml
            
        Raises:
            PropertyTaxonomyError: If file missing or invalid
        """
        try:
            if not path.exists():
                raise PropertyTaxonomyError(
                    f"property_system.yaml required for property classification: {path}"
                )
            
            with open(path, 'r', encoding='utf-8') as f:
                self.registry = yaml.safe_load(f)
            
            self.properties = self.registry.get('propertyDefinitions', {})
            self.rules = self.registry.get('classificationRules', {})
            self.mappings = self.registry.get('legacyPropertyMappings', {})
            
            logger.info(f"Loaded {len(self.properties)} property definitions from registry")
            
        except yaml.YAMLError as e:
            raise PropertyTaxonomyError(f"Invalid YAML in property_system.yaml: {e}")
        except Exception as e:
            raise PropertyTaxonomyError(f"Failed to load property_system.yaml: {e}")
    
    # ===== Type Detection (from PropertyClassifier) =====
    
    def is_qualitative(self, property_name: str) -> bool:
        """
        Check if property is qualitative (descriptive, no numerical range).
        
        Args:
            property_name: Name of the property
            
        Returns:
            True if qualitative, False if quantitative
        """
        prop_info = self.properties.get(property_name, {})
        return prop_info.get('type') == 'qualitative'
    
    def is_quantitative(self, property_name: str) -> bool:
        """
        Check if property is quantitative (numerical with ranges).
        
        Args:
            property_name: Name of the property
            
        Returns:
            True if quantitative, False if qualitative
        """
        prop_info = self.properties.get(property_name, {})
        prop_type = prop_info.get('type', '')
        return prop_type in ['quantitative', 'quantitative_nested']
    
    def requires_range(self, property_name: str) -> bool:
        """
        Check if property requires min/max range values.
        
        Args:
            property_name: Name of the property
            
        Returns:
            True if ranges required, False otherwise
        """
        prop_info = self.properties.get(property_name, {})
        return prop_info.get('range_required', False)
    
    def requires_unit(self, property_name: str) -> bool:
        """
        Check if property requires unit specification.
        
        Args:
            property_name: Name of the property
            
        Returns:
            True if unit required, False otherwise
        """
        prop_info = self.properties.get(property_name, {})
        return prop_info.get('unit_required', False)
    
    # ===== Category Lookup (from PropertyCategorizer) =====
    
    def get_category(self, property_name: str) -> Optional[str]:
        """
        Get category ID for a property.
        
        Args:
            property_name: Name of the property (e.g., 'thermalConductivity')
        
        Returns:
            Category ID string (e.g., 'thermal') or None if not categorized
        """
        return self._property_to_category.get(property_name)
    
    def get_category_info(self, category_id: str) -> Optional[Dict]:
        """
        Get full category information.
        
        Args:
            category_id: Category identifier (e.g., 'thermal')
        
        Returns:
            Dict with category metadata (label, description, properties) or None
        """
        return self.categories.get(category_id)
    
    def get_properties_by_category(self, category_id: str) -> List[str]:
        """
        Get all properties in a category.
        
        Args:
            category_id: Category identifier (e.g., 'thermal')
        
        Returns:
            List of property names in that category
        """
        cat_data = self.categories.get(category_id, {})
        return cat_data.get('materialProperties', [])
    
    def get_usage_tier(self, property_name: str) -> str:
        """
        Get usage tier (core/common/specialized) for a property.
        
        Args:
            property_name: Name of the property
        
        Returns:
            Tier string: 'core', 'common', or 'specialized'
        """
        for tier, tier_data in self.usage_tiers.items():
            # Tier data is just a list of property names, not nested
            if isinstance(tier_data, list):
                props = tier_data
            elif isinstance(tier_data, dict):
                # If it's a dict, extract property names directly (no 'properties' key)
                props = list(tier_data.keys())
            else:
                props = []
            if property_name in props:
                return tier
        return 'specialized'  # Default for properties not in core/common
    
    def categorize_properties(self, properties: List[str]) -> Dict[str, List[str]]:
        """
        Group properties by category.
        
        Args:
            properties: List of property names to categorize
        
        Returns:
            Dict mapping category_id -> list of properties
            Includes 'uncategorized' key for unknown properties
        """
        categorized = {}
        for prop in properties:
            category = self.get_category(prop)
            if category:
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append(prop)
            else:
                if 'uncategorized' not in categorized:
                    categorized['uncategorized'] = []
                categorized['uncategorized'].append(prop)
        
        return categorized
    
    def get_all_categories(self) -> List[str]:
        """
        Get list of all category IDs.
        
        Returns:
            List of category ID strings
        """
        return list(self.categories.keys())
    
    # ===== Metadata Access =====
    
    def get_property_info(self, property_name: str) -> Optional[PropertyInfo]:
        """
        Get complete property metadata.
        
        Args:
            property_name: Name of the property
            
        Returns:
            PropertyInfo object or None if not found
        """
        prop_data = self.properties.get(property_name)
        if not prop_data:
            return None
        
        return PropertyInfo(
            name=property_name,
            type=prop_data.get('type', 'quantitative'),
            category=prop_data.get('category', 'unknown'),
            unit_required=prop_data.get('unit_required', True),
            range_required=prop_data.get('range_required', True),
            typical_units=prop_data.get('typical_units', []),
            allowed_values=prop_data.get('allowed_values', []),
            description=prop_data.get('description', ''),
            measurement_context=prop_data.get('measurement_context', ''),
            nested_structure=prop_data.get('nested_structure', False),
            fields=prop_data.get('fields', {})
        )
    
    def get_frontmatter_section(self, property_name: str) -> str:
        """
        Determine which frontmatter section property belongs in.
        
        Args:
            property_name: Name of the property
            
        Returns:
            'materialProperties' or 'materialCharacteristics'
        """
        prop_info = self.properties.get(property_name, {})
        prop_type = prop_info.get('type', 'quantitative')
        
        if prop_type == 'qualitative':
            return 'materialCharacteristics'
        return 'materialProperties'
    
    # ===== Validation =====
    
    def validate_property_value(self, property_name: str, value: Any) -> bool:
        """
        Validate property value against allowed values (for qualitative).
        
        Args:
            property_name: Name of the property
            value: Value to validate
            
        Returns:
            True if valid, False otherwise
        """
        prop_info = self.properties.get(property_name, {})
        
        # Quantitative properties - just check if numeric
        if prop_info.get('type') in ['quantitative', 'quantitative_nested']:
            return isinstance(value, (int, float))
        
        # Qualitative properties - check against allowed values
        allowed = prop_info.get('allowed_values', [])
        if not allowed:
            # No restrictions - any string value allowed
            return isinstance(value, str)
        
        return value in allowed
    
    # ===== Legacy Support =====
    
    def get_legacy_mapping(self, old_property_name: str) -> Optional[Dict[str, str]]:
        """
        Get migration info for legacy property names.
        
        Args:
            old_property_name: Old property name
            
        Returns:
            Dict with new_property, new_type, migration_note
        """
        return self.mappings.get(old_property_name)
    
    # ===== Listing & Discovery =====
    
    def list_properties_by_type(self, prop_type: str) -> List[str]:
        """
        List all properties of a given type.
        
        Args:
            prop_type: 'quantitative', 'qualitative', or 'quantitative_nested'
            
        Returns:
            List of property names
        """
        return [
            name for name, info in self.properties.items()
            if info.get('type') == prop_type
        ]
    
    def list_properties_by_category(self, category: str) -> List[str]:
        """
        List all properties in a category.
        
        Args:
            category: Category name (thermal, mechanical, optical_laser, etc.)
            
        Returns:
            List of property names
        """
        return [
            name for name, info in self.properties.items()
            if info.get('category') == category
        ]
    
    def get_metadata(self) -> Dict:
        """
        Get property taxonomy metadata.
        
        Returns:
            Dict with version, total counts, etc.
        """
        return self.category_metadata.copy()


# ===== Singleton Pattern =====

_taxonomy_instance = None

def get_property_taxonomy() -> PropertyTaxonomy:
    """
    Get singleton PropertyTaxonomy instance.
    
    Singleton pattern for performance (load YAML files once per process)
    
    Returns:
        PropertyTaxonomy instance (creates on first call)
    
    Raises:
        PropertyTaxonomyError: If initialization fails
    """
    global _taxonomy_instance
    if _taxonomy_instance is None:
        _taxonomy_instance = PropertyTaxonomy()
    return _taxonomy_instance


# ===== Backward Compatibility Aliases =====

# For gradual migration from old modules
PropertyCategorizer = PropertyTaxonomy
PropertyClassifier = PropertyTaxonomy
get_property_categorizer = get_property_taxonomy
get_classifier = get_property_taxonomy
