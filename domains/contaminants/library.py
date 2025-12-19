#!/usr/bin/env python3
"""
Contamination Library Loader

Loads and manages the contamination patterns and material properties
from the schema.yaml file.

Author: AI Assistant
Date: November 25, 2025
"""

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from .models import (
    ContaminantCategory,
    ContaminantPattern,
    FormationConditions,
    MaterialProperties,
    VisualCharacteristics,
)

logger = logging.getLogger(__name__)


class ContaminationLibrary:
    """
    Library of contamination patterns and material properties.
    
    Loads from schema.yaml and provides lookup methods.
    """
    
    def __init__(self, schema_path: Optional[Path] = None):
        """
        Initialize library from schema file.
        
        Args:
            schema_path: Path to Contaminants.yaml (auto-detects if not provided)
        """
        if schema_path is None:
            # Default to data/contaminants/Contaminants.yaml (normalized with Materials.yaml)
            schema_path = Path(__file__).parent.parent.parent / 'data' / 'contaminants' / 'Contaminants.yaml'
        
        self.schema_path = Path(schema_path)
        
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Contaminants.yaml not found: {self.schema_path}")
        
        # Load schema
        with open(self.schema_path, 'r') as f:
            self.schema = yaml.safe_load(f)
        
        # Parse contamination patterns
        self._patterns: Dict[str, ContaminantPattern] = {}
        self._parse_patterns()
        
        # Parse material properties
        self._materials: Dict[str, MaterialProperties] = {}
        self._parse_materials()
        
        # Load error messages
        self._error_messages = self.schema.get('error_messages', {})
        
        logger.info(
            f"✅ Contamination library loaded: "
            f"{len(self._patterns)} patterns, {len(self._materials)} materials"
        )
    
    def _parse_patterns(self):
        """Parse contamination patterns from schema"""
        patterns_data = self.schema.get('contamination_patterns', {})
        
        for pattern_id, data in patterns_data.items():
            try:
                # Parse visual characteristics
                visual_data = data.get('visual_characteristics', {})
                visual = VisualCharacteristics(
                    color_range=visual_data.get('color_range', []),
                    texture=visual_data.get('texture', ''),
                    thickness=visual_data.get('thickness', '')
                )
                
                # Parse formation conditions
                formation_data = data.get('formation_conditions', [])
                if isinstance(formation_data, list):
                    formation = FormationConditions(required=formation_data)
                else:
                    formation = FormationConditions(
                        required=formation_data.get('required', []),
                        accelerating=formation_data.get('accelerating'),
                        protective=formation_data.get('protective')
                    )
                
                # Parse category
                category_str = data.get('category', 'contamination')
                try:
                    category = ContaminantCategory(category_str)
                except ValueError:
                    category = ContaminantCategory.CONTAMINATION
                
                # Create pattern object
                pattern = ContaminantPattern(
                    id=pattern_id,
                    name=data.get('name', pattern_id),
                    category=category,
                    description=data.get('description', ''),
                    required_elements=data.get('required_elements', []),
                    chemical_formula=data.get('chemical_formula'),
                    scientific_name=data.get('scientific_name'),
                    formation_conditions=formation,
                    visual_characteristics=visual,
                    valid_materials=data.get('valid_materials', []),
                    invalid_materials=data.get('invalid_materials', []),
                    valid_material_categories=data.get('valid_material_categories', []),
                    context_required=data.get('context_required', False),
                    valid_contexts=data.get('valid_contexts', []),
                    invalid_without_context=data.get('invalid_without_context', []),
                    realism_notes=data.get('realism_notes', '')
                )
                
                self._patterns[pattern_id] = pattern
                
            except Exception as e:
                logger.error(f"Failed to parse pattern {pattern_id}: {e}")
    
    def _parse_materials(self):
        """Parse material properties from schema"""
        materials_data = self.schema.get('material_properties', {})
        
        for material_name, data in materials_data.items():
            try:
                material = MaterialProperties(
                    name=material_name,
                    category=data.get('category', ''),
                    contains=data.get('contains', []),
                    can_rust=data.get('can_rust', False),
                    valid_contamination=data.get('valid_contamination', []),
                    prohibited_contamination=data.get('prohibited_contamination', []),
                    conditional_contamination=data.get('conditional_contamination', {})
                )
                
                self._materials[material_name] = material
                
            except Exception as e:
                logger.error(f"Failed to parse material {material_name}: {e}")
    
    def get_pattern(self, pattern_id: str) -> Optional[ContaminantPattern]:
        """
        Get contamination pattern by ID.
        
        Args:
            pattern_id: Pattern identifier (e.g., "rust_oxidation")
            
        Returns:
            ContaminantPattern object or None if not found
        """
        return self._patterns.get(pattern_id)
    
    def get_pattern_by_name(self, pattern_name: str) -> Optional[ContaminantPattern]:
        """
        Get contamination pattern by name (fuzzy match).
        
        Args:
            pattern_name: Pattern name to search for
            
        Returns:
            ContaminantPattern object or None if not found
        """
        pattern_name_lower = pattern_name.lower()
        
        # Exact name match
        for pattern in self._patterns.values():
            if pattern.name.lower() == pattern_name_lower:
                return pattern
        
        # Partial match
        for pattern in self._patterns.values():
            if pattern_name_lower in pattern.name.lower():
                return pattern
        
        return None
    
    def get_material(self, material_name: str) -> Optional[MaterialProperties]:
        """
        Get material properties by name.
        
        Args:
            material_name: Material name (e.g., "Steel")
            
        Returns:
            MaterialProperties object or None if not found
        """
        return self._materials.get(material_name)
    
    def list_patterns(self) -> List[ContaminantPattern]:
        """Get all contamination patterns"""
        return list(self._patterns.values())
    
    def list_materials(self) -> List[MaterialProperties]:
        """Get all material properties"""
        return list(self._materials.values())
    
    def get_patterns_for_material(
        self, 
        material_name: str,
        include_conditional: bool = False
    ) -> List[ContaminantPattern]:
        """
        Get all valid contamination patterns for a material.
        
        Args:
            material_name: Material name
            include_conditional: Include patterns requiring context
            
        Returns:
            List of valid ContaminantPattern objects
        """
        material = self.get_material(material_name)
        if not material:
            logger.warning(f"Material not found in library: {material_name}")
            return []
        
        valid_patterns = []
        
        for pattern_id in material.valid_contamination:
            pattern = self.get_pattern(pattern_id)
            if pattern:
                valid_patterns.append(pattern)
        
        if include_conditional:
            for pattern_id in material.conditional_contamination.keys():
                pattern = self.get_pattern(pattern_id)
                if pattern and pattern not in valid_patterns:
                    valid_patterns.append(pattern)
        
        return valid_patterns
    
    def get_prohibited_patterns_for_material(
        self, 
        material_name: str
    ) -> List[ContaminantPattern]:
        """
        Get all prohibited contamination patterns for a material.
        
        Args:
            material_name: Material name
            
        Returns:
            List of prohibited ContaminantPattern objects
        """
        material = self.get_material(material_name)
        if not material:
            return []
        
        prohibited_patterns = []
        
        for pattern_id in material.prohibited_contamination:
            pattern = self.get_pattern(pattern_id)
            if pattern:
                prohibited_patterns.append(pattern)
        
        return prohibited_patterns
    
    def get_error_message(
        self, 
        error_code: str, 
        **kwargs
    ) -> Dict[str, str]:
        """
        Get formatted error message with substitutions.
        
        Args:
            error_code: Error code (e.g., "INCOMPATIBLE_RUST")
            **kwargs: Values for template substitution
            
        Returns:
            Dict with 'message', 'explanation', 'suggestion'
        """
        error_template = self._error_messages.get(error_code, {})
        
        result = {}
        for key in ['code', 'message', 'explanation', 'suggestion']:
            template = error_template.get(key, '')
            if template:
                try:
                    result[key] = template.format(**kwargs)
                except KeyError as e:
                    result[key] = template  # Use unformatted if missing key
        
        return result
    
    def search_patterns(
        self,
        category: Optional[ContaminantCategory] = None,
        requires_element: Optional[str] = None,
        valid_for_material: Optional[str] = None
    ) -> List[ContaminantPattern]:
        """
        Search for patterns matching criteria.
        
        Args:
            category: Filter by contamination category
            requires_element: Filter by required element
            valid_for_material: Filter by material compatibility
            
        Returns:
            List of matching ContaminantPattern objects
        """
        results = list(self._patterns.values())
        
        if category:
            results = [p for p in results if p.category == category]
        
        if requires_element:
            results = [
                p for p in results 
                if requires_element.lower() in [e.lower() for e in p.required_elements]
            ]
        
        if valid_for_material:
            material = self.get_material(valid_for_material)
            if material:
                results = [
                    p for p in results
                    if p.id in material.valid_contamination or 
                       p.id in material.conditional_contamination
                ]
        
        return results
    
    def get_schema_version(self) -> str:
        """Get schema version"""
        return self.schema.get('metadata', {}).get('version', 'unknown')
    
    def reload(self):
        """Reload schema from file"""
        self.__init__(self.schema_path)


# Global library instance
_library_instance: Optional[ContaminationLibrary] = None


@lru_cache(maxsize=1)
def get_library() -> ContaminationLibrary:
    """
    Get or create global contamination library instance.
    
    Returns:
        ContaminationLibrary singleton
    """
    global _library_instance
    if _library_instance is None:
        _library_instance = ContaminationLibrary()
    return _library_instance


def reload_library():
    """Reload the global library from disk"""
    global _library_instance
    _library_instance = None
    get_library.cache_clear()
    return get_library()
