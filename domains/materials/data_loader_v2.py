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
    from domains.materials.data_loader import load_materials_yaml
    
    materials = load_materials_yaml()
"""

from pathlib import Path
from typing import Dict, Any, Optional
import logging

from shared.data.base_loader import BaseDataLoader
from shared.cache.manager import cache_manager
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
        
        # File paths
        self.materials_file = self.data_dir / 'Materials.yaml'
        self.properties_file = self.data_dir / 'MaterialProperties.yaml'
        self.industry_file = self.data_dir / 'IndustryApplications.yaml'
        self.categories_file = self.data_dir / 'CategoryTaxonomy.yaml'
        self.property_defs_file = self.data_dir / 'PropertyDefinitions.yaml'
        self.parameter_defs_file = self.data_dir / 'ParameterDefinitions.yaml'
        self.regulatory_file = self.data_dir / 'RegulatoryStandards.yaml'
    
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
    
    def load_materials(self) -> Dict[str, Any]:
        """
        Load Materials.yaml (core metadata only).
        
        Returns:
            Dict with 'materials', 'category_metadata', 'material_index', etc.
        
        Raises:
            ConfigurationError: If file cannot be loaded
        """
        # Check cache first
        cached = cache_manager.get('materials', 'materials_yaml')
        if cached:
            return cached
        
        # Load using base class method
        data = self._load_yaml_file(self.materials_file)
        
        # Cache for 1 hour
        cache_manager.set('materials', 'materials_yaml', data, ttl=3600)
        
        return data
    
    def load_properties(self) -> Dict[str, Dict[str, Any]]:
        """
        Load MaterialProperties.yaml.
        
        Returns:
            Dict mapping material names to property data
        
        Raises:
            ConfigurationError: If file cannot be loaded
        """
        # Check cache
        cached = cache_manager.get('materials', 'properties_yaml')
        if cached:
            return cached
        
        # Load file
        data = read_yaml_file(self.properties_file)
        properties = data.get('properties', {})
        
        # Cache for 1 hour
        cache_manager.set('materials', 'properties_yaml', properties, ttl=3600)
        
        return properties
    
    def load_industry_applications(self) -> Dict[str, Any]:
        """
        Load IndustryApplications.yaml (optional).
        
        Returns:
            Dict with industry guidance, or empty dict if not found
        """
        if not self.industry_file.exists():
            return {}
        
        # Check cache
        cached = cache_manager.get('materials', 'industry_yaml')
        if cached:
            return cached
        
        # Load file
        data = read_yaml_file(self.industry_file)
        
        # Cache for 1 hour
        cache_manager.set('materials', 'industry_yaml', data, ttl=3600)
        
        return data
    
    def load_categories(self) -> Dict[str, Any]:
        """
        Load CategoryTaxonomy.yaml.
        
        Returns:
            Dict with category hierarchies
        
        Raises:
            ConfigurationError: If file cannot be loaded
        """
        # Check cache
        cached = cache_manager.get('materials', 'categories_yaml')
        if cached:
            return cached
        
        # Load file
        data = read_yaml_file(self.categories_file)
        
        # Cache for 1 hour
        cache_manager.set('materials', 'categories_yaml', data, ttl=3600)
        
        return data
    
    def load_property_definitions(self) -> Dict[str, Any]:
        """
        Load PropertyDefinitions.yaml.
        
        Returns:
            Dict with property metadata and definitions
        """
        if not self.property_defs_file.exists():
            return {}
        
        # Check cache
        cached = cache_manager.get('materials', 'property_defs_yaml')
        if cached:
            return cached
        
        # Load file
        data = read_yaml_file(self.property_defs_file)
        
        # Cache for 1 hour
        cache_manager.set('materials', 'property_defs_yaml', data, ttl=3600)
        
        return data
    
    def load_parameter_definitions(self) -> Dict[str, Any]:
        """
        Load ParameterDefinitions.yaml.
        
        Returns:
            Dict with parameter definitions
        """
        if not self.parameter_defs_file.exists():
            return {}
        
        # Check cache
        cached = cache_manager.get('materials', 'parameter_defs_yaml')
        if cached:
            return cached
        
        # Load file
        data = read_yaml_file(self.parameter_defs_file)
        
        # Cache for 1 hour
        cache_manager.set('materials', 'parameter_defs_yaml', data, ttl=3600)
        
        return data
    
    def load_regulatory_standards(self) -> Dict[str, Any]:
        """
        Load RegulatoryStandards.yaml.
        
        Returns:
            Dict with regulatory frameworks
        """
        if not self.regulatory_file.exists():
            return {}
        
        # Check cache
        cached = cache_manager.get('materials', 'regulatory_yaml')
        if cached:
            return cached
        
        # Load file
        data = read_yaml_file(self.regulatory_file)
        
        # Cache for 1 hour
        cache_manager.set('materials', 'regulatory_yaml', data, ttl=3600)
        
        return data
    
    def load_micros(self) -> Dict[str, Any]:
        """
        Load Micros.yaml (material captions/subtitles).
        
        Returns:
            Dict with 'micros' mapping material names to captions
        """
        content_dir = self.project_root / 'materials' / 'data' / 'content'
        micros_file = content_dir / 'Micros.yaml'
        
        if not micros_file.exists():
            logger.warning(f"Micros.yaml not found at {micros_file}")
            return {}
        
        # Check cache
        cached = cache_manager.get('materials', 'micros_yaml')
        if cached:
            return cached
        
        # Load file
        data = read_yaml_file(micros_file)
        micros = data.get('micros', {})
        
        # Cache for 1 hour
        cache_manager.set('materials', 'micros_yaml', micros, ttl=3600)
        
        return micros
    
    def load_faqs(self) -> Dict[str, Any]:
        """
        Load FAQs.yaml (material FAQs).
        
        Returns:
            Dict with 'faqs' mapping material names to FAQ lists
        """
        content_dir = self.project_root / 'materials' / 'data' / 'content'
        faqs_file = content_dir / 'FAQs.yaml'
        
        if not faqs_file.exists():
            logger.warning(f"FAQs.yaml not found at {faqs_file}")
            return {}
        
        # Check cache
        cached = cache_manager.get('materials', 'faqs_yaml')
        if cached:
            return cached
        
        # Load file
        data = read_yaml_file(faqs_file)
        faqs = data.get('faqs', {})
        
        # Cache for 1 hour
        cache_manager.set('materials', 'faqs_yaml', faqs, ttl=3600)
        
        return faqs
    
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
            logger.warning(f"RegulatoryStandards.yaml not found at {regulatory_file}")
            return {}
        
        # Check cache
        cached = cache_manager.get('materials', 'regulatory_content_yaml')
        if cached:
            return cached
        
        # Load file
        data = read_yaml_file(regulatory_file)
        standards = data.get('regulatory_standards', {})
        
        # Cache for 1 hour
        cache_manager.set('materials', 'regulatory_content_yaml', standards, ttl=3600)
        
        return standards
    
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
    
    def clear_cache(self):
        """Clear all materials cache"""
        cache_manager.invalidate('materials')
        logger.info("Cleared materials cache")


# Singleton instance for convenience
_loader_instance = None

def get_loader() -> MaterialsDataLoader:
    """Get singleton MaterialsDataLoader instance"""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = MaterialsDataLoader()
    return _loader_instance
