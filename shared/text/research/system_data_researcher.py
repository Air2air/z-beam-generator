"""
System Data Researcher

Provides research capabilities for text generation pipeline.
Enables looking up material properties, contaminants, settings during generation.

Purpose: Ground generation in actual system data when context requires it.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml

logger = logging.getLogger(__name__)


class SystemDataResearcher:
    """
    Research system data during text generation.
    
    Provides access to:
    - Materials.yaml: Material properties, categories, applications
    - Contaminants.yaml: Contamination patterns, compatibility
    - Categories.yaml: Category-level data and ranges
    - Settings.yaml: Laser settings and parameter ranges
    
    Usage:
        researcher = SystemDataResearcher()
        
        # Research material properties
        steel_data = researcher.get_material("Steel")
        
        # Find related materials in same category
        related = researcher.get_related_materials("Steel", limit=3)
        
        # Get common contaminants for material
        contaminants = researcher.get_material_contaminants("Steel")
    """
    
    def __init__(self):
        """Initialize researcher with data paths."""
        self.materials_path = Path("data/materials/Materials.yaml")
        self.categories_path = Path("data/materials/Categories.yaml")
        self.contaminants_path = Path("data/contaminants/Contaminants.yaml")
        self.settings_path = Path("data/settings/Settings.yaml")
        
        # Lazy-load caches
        self._materials_cache = None
        self._categories_cache = None
        self._contaminants_cache = None
        self._settings_cache = None
    
    def _load_materials(self) -> Dict:
        """Load Materials.yaml (cached)."""
        if self._materials_cache is None:
            if not self.materials_path.exists():
                raise FileNotFoundError(f"Materials.yaml not found: {self.materials_path}")
            with open(self.materials_path, 'r', encoding='utf-8') as f:
                self._materials_cache = yaml.safe_load(f)
        return self._materials_cache
    
    def _load_categories(self) -> Dict:
        """Load Categories.yaml (cached)."""
        if self._categories_cache is None:
            if not self.categories_path.exists():
                raise FileNotFoundError(f"Categories.yaml not found: {self.categories_path}")
            with open(self.categories_path, 'r', encoding='utf-8') as f:
                self._categories_cache = yaml.safe_load(f)
        return self._categories_cache
    
    def _load_contaminants(self) -> Dict:
        """Load Contaminants.yaml (cached)."""
        if self._contaminants_cache is None:
            if not self.contaminants_path.exists():
                raise FileNotFoundError(f"Contaminants.yaml not found: {self.contaminants_path}")
            with open(self.contaminants_path, 'r', encoding='utf-8') as f:
                self._contaminants_cache = yaml.safe_load(f)
        return self._contaminants_cache
    
    def _load_settings(self) -> Dict:
        """Load Settings.yaml (cached)."""
        if self._settings_cache is None:
            if not self.settings_path.exists():
                logger.warning(f"Settings.yaml not found: {self.settings_path}")
                return {}
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                self._settings_cache = yaml.safe_load(f)
        return self._settings_cache
    
    # =========================================================================
    # MATERIAL RESEARCH
    # =========================================================================
    
    def get_material(self, material_name: str) -> Optional[Dict[str, Any]]:
        """
        Get complete material data.
        
        Args:
            material_name: Material name (exact match)
            
        Returns:
            Material data dict or None if not found
        """
        materials = self._load_materials()
        return materials.get('materials', {}).get(material_name)
    
    def get_material_property(self, material_name: str, property_name: str) -> Optional[Any]:
        """
        Get specific material property.
        
        Args:
            material_name: Material name
            property_name: Property key (e.g., 'hardness', 'thermalConductivity')
            
        Returns:
            Property value or None
        """
        material = self.get_material(material_name)
        if not material:
            return None
        return material.get('properties', {}).get(property_name)
    
    def get_related_materials(self, material_name: str, limit: int = 5) -> List[str]:
        """
        Find related materials in same category.
        
        Args:
            material_name: Source material
            limit: Maximum number of related materials
            
        Returns:
            List of related material names
        """
        material = self.get_material(material_name)
        if not material:
            return []
        
        category = material.get('category')
        if not category:
            return []
        
        # Find other materials in same category
        materials = self._load_materials().get('materials', {})
        related = [
            name for name, data in materials.items()
            if data.get('category') == category and name != material_name
        ]
        
        return related[:limit]
    
    def get_category_info(self, category_name: str) -> Optional[Dict[str, Any]]:
        """
        Get category-level information.
        
        Args:
            category_name: Category name
            
        Returns:
            Category data or None
        """
        categories = self._load_categories()
        return categories.get('categories', {}).get(category_name)
    
    # =========================================================================
    # CONTAMINANT RESEARCH
    # =========================================================================
    
    def get_material_contaminants(self, material_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get common contaminants for a material.
        
        Args:
            material_name: Material name
            limit: Maximum contaminants to return
            
        Returns:
            List of contaminant data dicts with pattern info
        """
        contaminants_data = self._load_contaminants()
        patterns = contaminants_data.get('contamination_patterns', {})
        
        matching = []
        for pattern_id, pattern_data in patterns.items():
            valid_materials = pattern_data.get('valid_materials', [])
            
            # Check if material is in valid_materials or if "ALL" is present
            if 'ALL' in valid_materials or material_name in valid_materials:
                matching.append({
                    'pattern_id': pattern_id,
                    'name': pattern_data.get('name'),
                    'category': pattern_data.get('category'),
                    'commonality': pattern_data.get('commonality_score', 0)
                })
        
        # Sort by commonality (most common first)
        matching.sort(key=lambda x: x['commonality'], reverse=True)
        
        return matching[:limit]
    
    def get_contaminant_info(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete contaminant pattern info.
        
        Args:
            pattern_id: Contamination pattern ID
            
        Returns:
            Pattern data or None
        """
        contaminants_data = self._load_contaminants()
        return contaminants_data.get('contamination_patterns', {}).get(pattern_id)
    
    # =========================================================================
    # SETTINGS RESEARCH
    # =========================================================================
    
    def get_setting_info(self, setting_name: str) -> Optional[Dict[str, Any]]:
        """
        Get laser setting information.
        
        Args:
            setting_name: Setting name
            
        Returns:
            Setting data or None
        """
        settings = self._load_settings()
        return settings.get('settings', {}).get(setting_name)
    
    def get_setting_range(self, setting_name: str) -> Optional[Dict[str, float]]:
        """
        Get parameter range for a setting.
        
        Args:
            setting_name: Setting name
            
        Returns:
            Dict with 'min' and 'max' or None
        """
        setting = self.get_setting_info(setting_name)
        if not setting:
            return None
        
        return {
            'min': setting.get('min'),
            'max': setting.get('max'),
            'unit': setting.get('unit')
        }
