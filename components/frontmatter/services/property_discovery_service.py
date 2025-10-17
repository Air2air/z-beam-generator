#!/usr/bin/env python3
"""
Property Discovery Service

Determines which properties need to be researched for a material based on:
- Material category (determines applicable properties)
- Available YAML data (high-confidence existing values)
- Category-specific requirements (thermal properties, etc.)

Follows fail-fast principles:
- No default values or fallbacks
- Explicit error handling with PropertyDiscoveryError
- Validates all inputs immediately
"""

import logging
from typing import Dict, List, Set, Optional, Tuple
from validation.errors import PropertyDiscoveryError, ConfigurationError

logger = logging.getLogger(__name__)


class PropertyDiscoveryService:
    """
    Service for discovering which properties need research for a material.
    
    Responsibilities:
    - Determine required properties based on material category
    - Identify gaps in existing YAML data
    - Apply category-specific property requirements
    - Calculate property coverage statistics
    """
    
    # Essential properties that every material should have
    ESSENTIAL_PROPERTIES = {
        'thermalConductivity',
        'density',
        'hardness',
        'reflectivity'
    }
    
    # Category-specific essential properties
    CATEGORY_ESSENTIALS = {
        'metal': {'thermalDestructionPoint', 'thermalConductivity', 'density', 'hardness'},
        'ceramic': {'sinteringPoint', 'thermalConductivity', 'density', 'hardness'},
        'plastic': {'degradationPoint', 'thermalConductivity', 'density'},
        'composite': {'degradationPoint', 'thermalConductivity', 'density'},
        'wood': {'thermalDestructionPoint', 'density'},
        'stone': {'thermalDegradationPoint', 'density', 'hardness'},
        'glass': {'softeningPoint', 'thermalConductivity', 'density'},
        'semiconductor': {'thermalDestructionPoint', 'thermalConductivity', 'density'},
        'masonry': {'thermalDegradationPoint', 'density', 'hardness'}
    }
    
    # Minimum confidence threshold for YAML properties (85%)
    YAML_CONFIDENCE_THRESHOLD = 0.85
    
    def __init__(self, categories_data: Optional[Dict] = None):
        """
        Initialize property discovery service.
        
        Args:
            categories_data: Optional Categories.yaml data for enhanced discovery
            
        Raises:
            ConfigurationError: If required configuration is invalid
        """
        self.categories_data = categories_data or {}
        self.logger = logger
        
    def discover_properties_to_research(
        self, 
        material_name: str,
        material_category: str,
        yaml_properties: Dict
    ) -> Tuple[Set[str], Dict[str, str]]:
        """
        Determine which properties need AI research for a material.
        
        Args:
            material_name: Name of the material
            material_category: Category (metal, plastic, etc.)
            yaml_properties: Existing properties from Materials.yaml
            
        Returns:
            Tuple of (properties_to_research, skip_reasons)
            - properties_to_research: Set of property names needing research
            - skip_reasons: Dict mapping property names to reasons why skipped
            
        Raises:
            PropertyDiscoveryError: If discovery fails
        """
        if not material_name:
            raise PropertyDiscoveryError("Material name is required for property discovery")
            
        if not material_category:
            raise PropertyDiscoveryError(f"Material category is required for {material_name}")
            
        try:
            # Get essential properties for this category
            essential = self._get_essential_properties(material_category)
            self.logger.info(f"📋 Category '{material_category}' requires {len(essential)} essential properties")
            
            # Identify high-confidence YAML properties
            yaml_props = self._filter_high_confidence_yaml(yaml_properties)
            self.logger.info(f"✅ Found {len(yaml_props)} high-confidence YAML properties for {material_name}")
            
            # Determine what needs research
            to_research = essential - set(yaml_props.keys())
            
            # Track skip reasons for logging
            skip_reasons = {}
            for prop in essential:
                if prop in yaml_props:
                    skip_reasons[prop] = f"High-confidence YAML data (confidence: {yaml_props[prop].get('confidence', 0)})"
            
            self.logger.info(f"🔍 Need to research {len(to_research)} properties for {material_name}")
            
            return to_research, skip_reasons
            
        except Exception as e:
            raise PropertyDiscoveryError(f"Failed to discover properties for {material_name}: {e}")
    
    def _get_essential_properties(self, material_category: str) -> Set[str]:
        """
        Get essential properties for a material category.
        
        Args:
            material_category: Category name (metal, plastic, etc.)
            
        Returns:
            Set of essential property names
        """
        category_lower = material_category.lower()
        
        # Start with universal essentials
        essentials = self.ESSENTIAL_PROPERTIES.copy()
        
        # Add category-specific essentials
        if category_lower in self.CATEGORY_ESSENTIALS:
            essentials.update(self.CATEGORY_ESSENTIALS[category_lower])
        else:
            self.logger.warning(
                f"Unknown category '{material_category}' - using universal essentials only"
            )
        
        return essentials
    
    def _filter_high_confidence_yaml(self, yaml_properties: Dict) -> Dict:
        """
        Filter YAML properties to only include high-confidence values.
        
        Args:
            yaml_properties: Raw YAML properties
            
        Returns:
            Dict of high-confidence properties only
        """
        high_confidence = {}
        
        for prop_name, prop_data in yaml_properties.items():
            if not isinstance(prop_data, dict):
                continue
                
            confidence = prop_data.get('confidence', 0)
            
            # Handle both 0-1 and 0-100 confidence scales
            if confidence < 1:
                confidence = confidence  # Already 0-1 scale
            else:
                confidence = confidence / 100.0  # Convert from 0-100 to 0-1
            
            if confidence >= self.YAML_CONFIDENCE_THRESHOLD:
                high_confidence[prop_name] = prop_data
        
        return high_confidence
    
    def calculate_coverage(
        self,
        material_category: str,
        yaml_properties: Dict,
        researched_properties: Dict
    ) -> Dict[str, float]:
        """
        Calculate property coverage statistics.
        
        Args:
            material_category: Material category
            yaml_properties: Properties from YAML
            researched_properties: Properties from AI research
            
        Returns:
            Dict with coverage statistics:
            - yaml_count: Number of YAML properties
            - ai_count: Number of AI properties  
            - total: Total properties
            - yaml_percentage: Percentage from YAML
            - ai_percentage: Percentage from AI
            - essential_coverage: Percentage of essential properties covered
        """
        yaml_props = self._filter_high_confidence_yaml(yaml_properties)
        yaml_count = len(yaml_props)
        ai_count = len(researched_properties)
        total = yaml_count + ai_count
        
        # Calculate percentages
        yaml_pct = (yaml_count / total * 100) if total > 0 else 0
        ai_pct = (ai_count / total * 100) if total > 0 else 0
        
        # Calculate essential coverage
        essentials = self._get_essential_properties(material_category)
        all_props = set(yaml_props.keys()) | set(researched_properties.keys())
        covered_essentials = essentials & all_props
        essential_coverage = (len(covered_essentials) / len(essentials) * 100) if essentials else 100
        
        return {
            'yaml_count': yaml_count,
            'ai_count': ai_count,
            'total': total,
            'yaml_percentage': round(yaml_pct, 1),
            'ai_percentage': round(ai_pct, 1),
            'essential_coverage': round(essential_coverage, 1)
        }
    
    def validate_property_completeness(
        self,
        material_name: str,
        material_category: str,
        properties: Dict
    ) -> None:
        """
        Validate that all essential properties are present.
        
        Args:
            material_name: Material name
            material_category: Material category
            properties: All properties (YAML + researched)
            
        Raises:
            PropertyDiscoveryError: If essential properties are missing
        """
        essentials = self._get_essential_properties(material_category)
        missing = essentials - set(properties.keys())
        
        if missing:
            raise PropertyDiscoveryError(
                f"Missing essential properties for {material_name} ({material_category}): "
                f"{', '.join(sorted(missing))}"
            )
        
        self.logger.info(f"✅ All {len(essentials)} essential properties present for {material_name}")
