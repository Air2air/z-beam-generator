#!/usr/bin/env python3
"""
Property Manager - Unified Property Lifecycle Management

Consolidates property discovery, research, categorization, and validation into single service.
Replaces PropertyDiscoveryService and PropertyResearchService with unified interface.

Responsibilities:
- Property discovery (gap identification)
- AI research coordination
- Automatic categorization (quantitative/qualitative)
- Validation and normalization
- Machine settings research

Follows fail-fast principles:
- No mocks or default values in production
- Explicit error handling with PropertyDiscoveryError
- Validates all inputs immediately

Author: Refactoring - October 17, 2025
"""

import logging
from typing import Dict, List, Set, Optional, Tuple, Callable
from dataclasses import dataclass

from components.frontmatter.research.property_value_researcher import PropertyValueResearcher
from validation.errors import PropertyDiscoveryError, ConfigurationError

# Qualitative property definitions
from components.frontmatter.qualitative_properties import (
    QUALITATIVE_PROPERTIES,
    is_qualitative_property,
    get_property_definition,
    validate_qualitative_value,
    MATERIAL_CHARACTERISTICS_CATEGORIES
)

logger = logging.getLogger(__name__)


@dataclass
class PropertyResearchResult:
    """Result of complete property research pipeline."""
    quantitative_properties: Dict[str, Dict]
    qualitative_characteristics: Dict[str, Dict]
    machine_settings: Optional[Dict[str, Dict]] = None
    research_metadata: Optional[Dict] = None


class PropertyManager:
    """
    Unified property management service.
    
    Handles complete property lifecycle:
    Discovery → Research → Categorization → Validation → Normalization
    
    Replaces:
    - PropertyDiscoveryService (discovery logic)
    - PropertyResearchService (research coordination)
    - Scattered validation logic
    """
    
    # Essential properties by category
    ESSENTIAL_PROPERTIES = {
        'universal': {'thermalConductivity', 'density', 'hardness', 'reflectivity'},
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
    
    # Confidence thresholds
    YAML_CONFIDENCE_THRESHOLD = 0.85  # 85%
    
    def __init__(
        self,
        property_researcher: PropertyValueResearcher,
        get_category_ranges_func: Optional[Callable] = None,
        enhance_descriptions_func: Optional[Callable] = None,
        categories_data: Optional[Dict] = None
    ):
        """
        Initialize property manager.
        
        Args:
            property_researcher: PropertyValueResearcher instance for AI research
            get_category_ranges_func: Function to get category ranges for properties
            enhance_descriptions_func: Function to enhance with standardized descriptions
            categories_data: Optional Categories.yaml data for enhanced discovery
            
        Raises:
            PropertyDiscoveryError: If property_researcher is None
        """
        if not property_researcher:
            raise PropertyDiscoveryError(
                "PropertyValueResearcher required for property management. "
                "Cannot operate without AI research capability."
            )
        
        self.property_researcher = property_researcher
        self.get_category_ranges = get_category_ranges_func
        self.enhance_descriptions = enhance_descriptions_func
        self.categories_data = categories_data or {}
        self.logger = logger
    
    # ===== MAIN INTERFACE =====
    
    def discover_and_research_properties(
        self,
        material_name: str,
        material_category: str,
        existing_properties: Dict
    ) -> PropertyResearchResult:
        """
        Complete property discovery and research pipeline.
        
        Pipeline:
        1. Discover which properties need research (gap analysis)
        2. Research missing properties via AI
        3. Categorize properties (quantitative vs qualitative)
        4. Validate and normalize all properties
        5. Return organized result
        
        Args:
            material_name: Name of the material
            material_category: Category (metal, plastic, etc.)
            existing_properties: Properties already present (from YAML)
            
        Returns:
            PropertyResearchResult with categorized properties
            
        Raises:
            PropertyDiscoveryError: If pipeline fails
        """
        try:
            # Step 1: Discovery - identify gaps
            properties_to_research, skip_reasons = self._discover_gaps(
                material_name,
                material_category,
                existing_properties
            )
            
            # Step 2: Research - AI discovery for missing properties
            if properties_to_research:
                self.logger.info(f"🔍 Researching {len(properties_to_research)} missing properties")
                discovered = self.property_researcher.discover_all_material_properties(
                    material_name,
                    material_category
                )
            else:
                self.logger.info("✅ All essential properties present in YAML")
                discovered = {}
            
            # Step 3: Process discovered properties
            quantitative, qualitative = self._process_discovered_properties(
                material_name,
                material_category,
                discovered,
                existing_properties
            )
            
            # Step 4: Validation
            self._validate_essential_coverage(
                material_name,
                material_category,
                {**existing_properties, **quantitative},
                qualitative
            )
            
            # Step 5: Build result
            metadata = {
                'yaml_property_count': len(existing_properties),
                'researched_property_count': len(quantitative),
                'qualitative_count': len(qualitative),
                'skip_reasons': skip_reasons
            }
            
            return PropertyResearchResult(
                quantitative_properties=quantitative,
                qualitative_characteristics=qualitative,
                research_metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Property discovery and research failed for {material_name}: {e}")
            raise PropertyDiscoveryError(
                f"Failed to discover and research properties for {material_name}: {e}"
            )
    
    def research_machine_settings(
        self,
        material_name: str
    ) -> Dict[str, Dict]:
        """
        Research machine settings using AI discovery.
        
        Args:
            material_name: Name of the material
            
        Returns:
            Dict of researched machine settings with complete data structure
            
        Raises:
            PropertyDiscoveryError: If research fails or no settings found
        """
        try:
            # Use comprehensive AI discovery
            discovered_settings = self.property_researcher.discover_all_machine_settings(material_name)
            
            self.logger.info(f"AI discovered {len(discovered_settings)} machine settings for {material_name}")
            
            if not discovered_settings:
                raise PropertyDiscoveryError(
                    f"No machine settings discovered for {material_name}. "
                    "Comprehensive discovery required per fail-fast principles."
                )
            
            # Process and enhance discovered settings
            researched = {}
            for setting_name, setting_data in discovered_settings.items():
                # Build machine setting structure
                machine_setting_data = {
                    'value': setting_data['value'],
                    'unit': setting_data['unit'],
                    'confidence': setting_data['confidence'],
                    'description': setting_data['description'],
                    'min': setting_data.get('min'),
                    'max': setting_data.get('max')
                }
                
                # Enhance with standardized descriptions if available
                if self.enhance_descriptions:
                    machine_setting_data = self.enhance_descriptions(
                        machine_setting_data, setting_name, 'machineSettings'
                    )
                
                researched[setting_name] = machine_setting_data
                self.logger.info(
                    f"🤖 Researched {setting_name}: {setting_data['value']} {setting_data['unit']} "
                    f"(confidence: {setting_data['confidence']}%)"
                )
            
            return researched
            
        except PropertyDiscoveryError:
            raise
        except Exception as e:
            self.logger.error(f"Machine settings research failed for {material_name}: {e}")
            raise PropertyDiscoveryError(
                f"Failed to research machine settings for {material_name}: {e}"
            )
    
    # ===== DISCOVERY METHODS =====
    
    def _discover_gaps(
        self,
        material_name: str,
        material_category: str,
        yaml_properties: Dict
    ) -> Tuple[Set[str], Dict[str, str]]:
        """
        Identify which properties need research (gap analysis).
        
        Args:
            material_name: Material name
            material_category: Material category
            yaml_properties: Existing properties from YAML
            
        Returns:
            Tuple of (properties_to_research, skip_reasons)
        """
        if not material_name:
            raise PropertyDiscoveryError("Material name is required")
        if not material_category:
            raise PropertyDiscoveryError(f"Material category is required for {material_name}")
        
        # Get essential properties for category
        essential = self._get_essential_properties(material_category)
        self.logger.info(f"📋 Category '{material_category}' requires {len(essential)} essential properties")
        
        # Identify high-confidence YAML properties
        yaml_props = self._filter_high_confidence_yaml(yaml_properties)
        self.logger.info(f"✅ Found {len(yaml_props)} high-confidence YAML properties")
        
        # Calculate gaps
        to_research = essential - set(yaml_props.keys())
        
        # Track skip reasons
        skip_reasons = {}
        for prop in essential:
            if prop in yaml_props:
                confidence = yaml_props[prop].get('confidence', 0)
                skip_reasons[prop] = f"High-confidence YAML data (confidence: {confidence})"
        
        self.logger.info(f"🔍 Need to research {len(to_research)} properties")
        
        return to_research, skip_reasons
    
    def _get_essential_properties(self, material_category: str) -> Set[str]:
        """Get essential properties for a material category."""
        category_lower = material_category.lower()
        
        # Start with universal essentials
        essentials = self.ESSENTIAL_PROPERTIES['universal'].copy()
        
        # Add category-specific essentials
        if category_lower in self.ESSENTIAL_PROPERTIES:
            essentials.update(self.ESSENTIAL_PROPERTIES[category_lower])
        else:
            self.logger.warning(
                f"Unknown category '{material_category}' - using universal essentials only"
            )
        
        return essentials
    
    def _filter_high_confidence_yaml(self, yaml_properties: Dict) -> Dict:
        """Filter to only high-confidence YAML properties."""
        high_confidence = {}
        
        for prop_name, prop_data in yaml_properties.items():
            if not isinstance(prop_data, dict):
                continue
            
            confidence = prop_data.get('confidence', 0)
            
            # Normalize confidence to 0-1 scale
            if confidence > 1:
                confidence = confidence / 100.0
            
            if confidence >= self.YAML_CONFIDENCE_THRESHOLD:
                high_confidence[prop_name] = prop_data
        
        return high_confidence
    
    # ===== PROCESSING METHODS =====
    
    def _process_discovered_properties(
        self,
        material_name: str,
        material_category: str,
        discovered: Dict,
        existing_properties: Dict
    ) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
        """
        Process discovered properties into quantitative and qualitative.
        
        Returns:
            Tuple of (quantitative_properties, qualitative_characteristics)
        """
        quantitative = {}
        qualitative = {}
        
        for prop_name, prop_data in discovered.items():
            # Skip if already in YAML (YAML takes precedence)
            if prop_name in existing_properties:
                continue
            
            # Skip redundant thermalDestructionPoint
            if prop_name == 'thermalDestructionPoint' and 'thermalDestruction' in existing_properties:
                self.logger.debug("Skipping redundant thermalDestructionPoint")
                continue
            
            # Check if qualitative (defined in taxonomy)
            if is_qualitative_property(prop_name):
                self.logger.debug(f"Property '{prop_name}' is qualitative - routing to characteristics")
                qualitative[prop_name] = self._build_qualitative_property(prop_name, prop_data)
                continue
            
            # Check if value is qualitative (backup check)
            if self._is_qualitative_value(prop_data.get('value')):
                self.logger.warning(
                    f"Property '{prop_name}' has qualitative value '{prop_data['value']}' "
                    f"but not in QUALITATIVE_PROPERTIES. Consider adding to definitions."
                )
                continue
            
            # Process as quantitative
            quantitative[prop_name] = self._build_quantitative_property(
                prop_name,
                prop_data,
                material_category,
                material_name
            )
        
        return quantitative, qualitative
    
    def _build_quantitative_property(
        self,
        prop_name: str,
        prop_data: Dict,
        material_category: str,
        material_name: str
    ) -> Dict:
        """Build quantitative property structure with ranges."""
        property_data = {
            'value': prop_data['value'],
            'unit': prop_data['unit'],
            'confidence': prop_data['confidence'],
            'description': prop_data['description'],
            'min': None,
            'max': None
        }
        
        # Apply category ranges if available
        if self.get_category_ranges:
            category_ranges = self.get_category_ranges(material_category, prop_name)
            
            if category_ranges and category_ranges.get('min') is not None:
                property_data['min'] = category_ranges['min']
                property_data['max'] = category_ranges['max']
            else:
                self.logger.debug(f"No category range for '{prop_name}' - setting to None")
        
        # Enhance with standardized descriptions
        if self.enhance_descriptions:
            property_data = self.enhance_descriptions(
                property_data, prop_name, 'materialProperties'
            )
        
        self.logger.info(
            f"🤖 Quantitative: {prop_name} = {prop_data['value']} {prop_data['unit']} "
            f"(confidence: {prop_data['confidence']}%)"
        )
        
        return property_data
    
    def _build_qualitative_property(self, prop_name: str, prop_data: Dict) -> Dict:
        """Build qualitative property structure with allowedValues."""
        prop_def = get_property_definition(prop_name)
        
        property_data = {
            'value': prop_data['value'],
            'unit': prop_data.get('unit', prop_def.unit if prop_def else 'type'),
            'confidence': prop_data['confidence'],
            'description': prop_data['description'],
            'min': None,
            'max': None
        }
        
        # Add allowedValues if defined
        if prop_def:
            property_data['allowedValues'] = prop_def.allowed_values
            
            # Validate value against allowedValues
            if not validate_qualitative_value(prop_name, prop_data['value']):
                self.logger.warning(
                    f"Qualitative property '{prop_name}' value '{prop_data['value']}' "
                    f"not in allowedValues: {prop_def.allowed_values}"
                )
        
        self.logger.info(
            f"🎨 Qualitative: {prop_name} = {prop_data['value']} "
            f"(confidence: {prop_data['confidence']}%)"
        )
        
        return property_data
    
    # ===== VALIDATION METHODS =====
    
    def _validate_essential_coverage(
        self,
        material_name: str,
        material_category: str,
        quantitative_properties: Dict,
        qualitative_characteristics: Dict
    ) -> None:
        """
        Validate that all essential properties are present.
        
        Raises:
            PropertyDiscoveryError: If essential properties missing
        """
        essentials = self._get_essential_properties(material_category)
        all_props = set(quantitative_properties.keys()) | set(qualitative_characteristics.keys())
        missing = essentials - all_props
        
        if missing:
            raise PropertyDiscoveryError(
                f"Missing essential properties for {material_name} ({material_category}): "
                f"{', '.join(sorted(missing))}"
            )
        
        self.logger.info(f"✅ All {len(essentials)} essential properties present for {material_name}")
    
    # ===== UTILITY METHODS =====
    
    @staticmethod
    def _is_qualitative_value(value) -> bool:
        """Check if a value appears to be qualitative (non-numeric string)."""
        if not isinstance(value, str):
            return False
        
        # Try to convert to float - if it works, it's numeric
        try:
            float(value.replace(',', ''))
            return False
        except (ValueError, AttributeError):
            return True
    
    @staticmethod
    def _is_numeric_string(value: str) -> bool:
        """Check if string represents a number."""
        try:
            float(value.replace(',', ''))
            return True
        except (ValueError, AttributeError):
            return False
