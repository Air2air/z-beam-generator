"""
Materials Data Loader - NEW ARCHITECTURE (December 11, 2025)

This module provides BaseDataLoader-based loading for materials data.
Maintains backward compatibility with existing function-based API.

New Architecture:
- Inherits from shared.data.base_loader.BaseDataLoader
- Uses shared.cache.manager.CacheManager for caching
- Uses shared.utils.file_io for file operations
- Eliminates duplicate YAML loading code

Backward Compatibility:
- All existing functions remain available
- No breaking changes to existing code
- Gradual migration path

Usage (New):
    from domains.materials.data_loader_v2 import MaterialsDataLoader
    
    loader = MaterialsDataLoader()
    materials = loader.load_materials()
    properties = loader.load_properties()

Usage (Legacy - still works):
    from domains.materials.data_loader_v2 import load_materials_yaml
    
    materials = load_materials_yaml()
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from shared.cache.manager import cache_manager
from shared.data.base_loader import BaseDataLoader
from shared.utils.file_io import read_yaml_file

logger = logging.getLogger(__name__)


class MaterialsDataLoader(BaseDataLoader):
    """
    Data loader for materials domain.
    
    Loads data from:
    - Materials.yaml: Core material metadata
    - MaterialProperties.yaml: Material properties with ranges
    - IndustryApplications.yaml: Industry-specific guidance
    - CategoryTaxonomy.yaml: Category hierarchies
    - PropertyDefinitions.yaml: Property metadata
    - ParameterDefinitions.yaml: Parameter definitions
    - RegulatoryStandards.yaml: Regulatory frameworks
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize materials data loader"""
        super().__init__(project_root)
        self.data_dir = self.project_root / 'data' / 'materials'
        self.settings_dir = self.project_root / 'data' / 'settings'
        
        # File paths
        self.materials_file = self.data_dir / 'Materials.yaml'
        self.properties_file = self.data_dir / 'MaterialProperties.yaml'
        self.industry_file = self.data_dir / 'IndustryApplications.yaml'
        self.categories_file = self.data_dir / 'CategoryTaxonomy.yaml'
        self.property_defs_file = self.data_dir / 'PropertyDefinitions.yaml'
        self.parameter_defs_file = self.data_dir / 'ParameterDefinitions.yaml'
        self.regulatory_file = self.data_dir / 'RegulatoryStandards.yaml'
        self.settings_file = self.settings_dir / 'Settings.yaml'
    
    def _get_data_file_path(self) -> Path:
        """Return path to primary data file (Materials.yaml)"""
        return self.materials_file
    
    def _validate_loaded_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate Materials.yaml structure.
        
        Args:
            data: Loaded YAML data
        
        Returns:
            True if valid structure
        """
        # Materials.yaml should have 'materials' or 'categories' key
        return 'materials' in data or 'categories' in data

    def _get_cache_domain(self) -> str:
        """Return the cache_manager domain string for the materials loader."""
        return 'materials'

    def load_materials(self, include_machine_settings: bool = False) -> Dict[str, Any]:
        """
        Load Materials.yaml with optional machine settings merge.
        
        By default, machineSettings remain in the Settings domain as separate data.
        Materials contain only material properties and metadata.
        
        For dataset generation (Materials + Settings cross-domain dataset), use
        include_machine_settings=True to merge Settings.yaml data.
        
        Args:
            include_machine_settings: If True, merge machineSettings from Settings.yaml
        
        Returns:
            Dict with 'materials', 'category_metadata', 'material_index', etc.
        
        Raises:
            ConfigurationError: If file cannot be loaded
        """
        # Use different cache keys for merged vs non-merged
        cache_key = 'materials_yaml_with_settings' if include_machine_settings else 'materials_yaml'
        
        # Check cache first
        cached = cache_manager.get(self._get_cache_domain(), cache_key)
        if cached:
            return cached

        # Load materials data
        data = self._load_yaml_file(self.materials_file)

        # Optionally merge settings for dataset generation
        if include_machine_settings:
            settings_data = read_yaml_file(self.settings_file)
            data = self._merge_machine_settings(data, settings_data)

        # Cache and return (1 hour TTL)
        cache_manager.set(self._get_cache_domain(), cache_key, data, ttl=3600)

        return data
    
    def _merge_machine_settings(self, materials_data: Dict[str, Any], settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge machine_settings from Settings.yaml into Materials.yaml.
        
        Matches by base slug: 'aluminum-laser-cleaning' material gets 'aluminum-settings' settings.
        
        Args:
            materials_data: Materials.yaml data
            settings_data: Settings.yaml data
        
        Returns:
            Materials data with machine_settings merged
        """
        settings = settings_data.get('settings', {})
        materials = materials_data.get('materials', {})
        
        merged_count = 0
        for material_slug, material_data in materials.items():
            # Get base slug (remove -laser-cleaning suffix)
            base_slug = material_slug.replace('-laser-cleaning', '')
            settings_slug = f"{base_slug}-settings"
            
            # Find matching settings
            if settings_slug in settings:
                setting_data = settings[settings_slug]
                # Merge machineSettings into material as machine_settings (snake_case for dataset validator)
                material_data['machine_settings'] = setting_data.get('machineSettings', {})
                merged_count += 1
        
        logger.info(f"Merged machineSettings into {merged_count}/{len(materials)} materials")
        return materials_data
    
    def load_properties(self) -> Dict[str, Dict[str, Any]]:
        """
        Load MaterialProperties.yaml.
        
        Returns:
            Dict mapping material names to property data
        
        Raises:
            ConfigurationError: If file cannot be loaded
        """
        return self._load_with_cache('properties_yaml', self.properties_file,
                                      lambda d: d.get('properties', {}))
    
    def load_industry_applications(self) -> Dict[str, Any]:
        """
        Load IndustryApplications.yaml (optional).
        
        Returns:
            Dict with industry guidance, or empty dict if not found
        """
        if not self.industry_file.exists():
            return {}
        return self._load_with_cache('industry_yaml', self.industry_file)
    
    def load_categories(self) -> Dict[str, Any]:
        """
        Load CategoryTaxonomy.yaml.
        
        Returns:
            Dict with category hierarchies
        
        Raises:
            ConfigurationError: If file cannot be loaded
        """
        return self._load_with_cache('categories_yaml', self.categories_file)
    
    def load_property_definitions(self) -> Dict[str, Any]:
        """
        Load PropertyDefinitions.yaml.
        
        Returns:
            Dict with property metadata and definitions
        """
        if not self.property_defs_file.exists():
            return {}
        return self._load_with_cache('property_defs_yaml', self.property_defs_file)
    
    def load_parameter_definitions(self) -> Dict[str, Any]:
        """
        Load ParameterDefinitions.yaml.
        
        Returns:
            Dict with parameter definitions
        """
        if not self.parameter_defs_file.exists():
            return {}
        return self._load_with_cache('parameter_defs_yaml', self.parameter_defs_file)
    
    def load_regulatory_standards(self) -> Dict[str, Any]:
        """
        Load RegulatoryStandards.yaml.
        
        Returns:
            Dict with regulatory frameworks
        """
        if not self.regulatory_file.exists():
            return {}
        return self._load_with_cache('regulatory_yaml', self.regulatory_file)
    
    def load_micros(self) -> Dict[str, Any]:
        """
        Load Micros.yaml (material captions).
        
        Returns:
            Dict with 'micros' mapping material names to captions
        """
        content_dir = self.project_root / 'materials' / 'data' / 'content'
        micros_file = content_dir / 'Micros.yaml'
        
        if not micros_file.exists():
            logger.debug(f"Legacy Micros.yaml not found (expected - content in Materials.yaml)")
            return {}
        return self._load_with_cache('micros_yaml', micros_file,
                                      lambda d: d.get('micros', {}))
    
    def load_faqs(self) -> Dict[str, Any]:
        """
        Load FAQs.yaml (material FAQs).
        
        Returns:
            Dict with 'faqs' mapping material names to FAQ lists
        """
        content_dir = self.project_root / 'materials' / 'data' / 'content'
        faqs_file = content_dir / 'FAQs.yaml'
        
        if not faqs_file.exists():
            logger.debug(f"Legacy FAQs.yaml not found (expected - content in Materials.yaml)")
            return {}
        return self._load_with_cache('faqs_yaml', faqs_file,
                                      lambda d: d.get('faqs', {}))
    
    def load_regulatory_standards_content(self) -> Dict[str, Any]:
        """
        Load RegulatoryStandards.yaml (material-specific standards).
        
        Note: Different from load_regulatory_standards() which loads
        from data/materials/RegulatoryStandards.yaml. This loads from
        materials/data/content/RegulatoryStandards.yaml.
        
        Returns:
            Dict with 'regulatory_standards' mapping material names to standards
        """
        content_dir = self.project_root / 'materials' / 'data' / 'content'
        regulatory_file = content_dir / 'RegulatoryStandards.yaml'
        
        if not regulatory_file.exists():
            logger.debug(f"Legacy RegulatoryStandards.yaml not found (expected - content in Materials.yaml)")
            return {}
        return self._load_with_cache('regulatory_content_yaml', regulatory_file,
                                      lambda d: d.get('regulatoryStandards', {}))
    
    def get_material(self, material_name: str) -> Optional[Dict[str, Any]]:
        """
        Get specific material by name.
        
        Args:
            material_name: Name of material (e.g., "Aluminum")
        
        Returns:
            Material data dict or None if not found
        """
        materials_data = self.load_materials()
        materials = materials_data.get('materials', {})
        return materials.get(material_name)
    

# Singleton instance for convenience
_loader_instance = None

def get_loader() -> MaterialsDataLoader:
    """Get singleton MaterialsDataLoader instance"""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = MaterialsDataLoader()
    return _loader_instance


# ============================================================================
# BACKWARD COMPATIBILITY FUNCTIONS (for v1 imports)
# ============================================================================

def load_materials_data() -> Dict[str, Any]:
    """Load all materials from Materials.yaml (backward compat)."""
    return get_loader().load_materials()


def load_material(material_name: str) -> Optional[Dict[str, Any]]:
    """Load single material by name (backward compat)."""
    return get_loader().load_material(material_name)


def get_material_names() -> list:
    """Get list of all material names (backward compat)."""
    return list(load_materials_data().keys())


def load_materials_yaml() -> Dict[str, Any]:
    """Load Materials.yaml (backward compat)."""
    return get_loader().load_item_data()


def load_properties_yaml() -> Dict[str, Any]:
    """Load MaterialProperties.yaml (backward compat)."""
    return get_loader().load_properties()


def get_property_definitions() -> Dict[str, Any]:
    """Get property definitions (backward compat)."""
    return get_loader().load_properties()


def load_parameter_definitions_yaml() -> Dict[str, Any]:
    """Load parameter definitions (backward compat)."""
    return get_loader().load_properties()


def get_category_ranges(category: str) -> Optional[Dict[str, Any]]:
    """Get ranges for a category (backward compat)."""
    loader = get_loader()
    categories = loader.load_item_data().get('categories', {})
    return categories.get(category)


def clear_cache():
    """Clear all materials caches (backward compat)."""
    get_loader().clear_cache()
