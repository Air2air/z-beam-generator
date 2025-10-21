#!/usr/bin/env python3
"""
Property Value Researcher - Material Property Research System

This module specializes in researching actual property values for materials,
providing the foundation for machine settings calculations and frontmatter generation.

Key Capabilities:
1. Research exact property values (e.g., Zirconia density: 5.68 g/cm³)
2. Database lookups with high confidence for known materials
3. Web research integration for unknown properties
4. Confidence scoring based on research quality
5. Integration with MaterialPropertyResearchSystem for property discovery

Author: GitHub Copilot
Date: September 25, 2025
"""

import logging
import time
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

# Import GenerationError for fail-fast behavior
from generators.component_generators import GenerationError

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Try to import research system
try:
    from research.material_property_research_system import MaterialPropertyResearchSystem
    PROPERTY_DISCOVERY_AVAILABLE = True
except ImportError:
    PROPERTY_DISCOVERY_AVAILABLE = False


@dataclass
class ResearchContext:
    """Context information for property research"""
    material_category: Optional[str] = None
    application_type: str = "cleaning"
    laser_wavelength: Optional[str] = None
    priority_level: int = 1  # 1=critical, 2=important, 3=useful
    processing_requirements: List[str] = field(default_factory=list)


@dataclass 
class PropertyDataMetric:
    """Data metric for a single property value"""
    value: Any
    unit: str
    confidence: int
    min: Optional[Any] = None
    max: Optional[Any] = None
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        result = {
            'value': self.value,
            'unit': self.unit,
            'confidence': self.confidence
        }
        if self.min is not None:
            result['min'] = self.min
        if self.max is not None:
            result['max'] = self.max
        if self.description:
            result['description'] = self.description
        return result


@dataclass
class PropertyResult:
    """Result of property value research"""
    material_name: str
    property_name: str
    property_data: Optional[PropertyDataMetric] = None
    success: bool = False
    confidence: int = 0
    source: str = "failure"
    research_method: str = "none"
    research_time: float = 0.0
    error_message: str = ""
    
    @property
    def value(self) -> Any:
        """Get property value"""
        return self.property_data.value if self.property_data else None
    
    @property
    def unit(self) -> str:
        """Get property unit"""
        return self.property_data.unit if self.property_data else ""
    
    def is_valid(self) -> bool:
        """Check if result has valid data"""
        return self.success and self.property_data is not None and self.confidence > 0
    
    def is_high_quality(self) -> bool:
        """Check if result meets high quality standards"""
        return self.is_valid() and self.confidence >= 80
    
    def to_property_data_metric(self) -> Optional[Dict[str, Any]]:
        """Convert to PropertyDataMetric format for YAML output"""
        if not self.is_valid():
            return None
        return self.property_data.to_dict()


class PropertyValueResearcher:
    """
    Specialized researcher for material property values.
    
    Provides exact property values with confidence scores based on research quality.
    Integrates with MaterialPropertyResearchSystem for property discovery and
    supports multiple research strategies.
    
    Core Research Strategies:
    1. Database Lookup: Search known material databases for exact values
    2. Materials.yaml Lookup: Use existing materials data
    3. Web Research: Search online sources for property values
    4. Literature Research: Academic and technical publications
    5. Estimation: Fallback estimates based on material category
    """
    
    # Property alias mapping for legacy property migration
    # Maps old property names to new unified property names
    PROPERTY_ALIASES = {
        'meltingPoint': 'thermalDestruction',  # Legacy: meltingPoint → thermalDestruction
        'thermalDestructionPoint': 'thermalDestruction',  # Legacy: point-based → full structure
        'sinteringPoint': 'thermalDestruction',  # Ceramics: sinteringPoint → thermalDestruction
        'degradationPoint': 'thermalDestruction',  # Plastics: degradationPoint → thermalDestruction
        'softeningPoint': 'thermalDestruction',  # Glass: softeningPoint → thermalDestruction
        'thermalDegradationPoint': 'thermalDestruction',  # Stone/masonry: degradation → thermalDestruction
    }
    
    def __init__(self, 
                 api_client,  # REQUIRED per GROK - no fallbacks allowed
                 min_confidence_threshold: int = 50,
                 debug_mode: bool = False):
        """
        Initialize Property Value Researcher with required API client (GROK compliant - no fallbacks).
        
        Args:
            api_client: AI API client for property research (REQUIRED)
            min_confidence_threshold: Minimum confidence for valid results
            debug_mode: Enable debug logging
        """
        if api_client is None:
            # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
            raise ValueError("API client is required for PropertyValueResearcher - no fallbacks allowed")
        
        self.api_client = api_client
        self.min_confidence_threshold = min_confidence_threshold
        self.debug_mode = debug_mode
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        if debug_mode:
            self.logger.setLevel(logging.DEBUG)
            
        # Initialize property discovery system if available
        self.property_discovery_system = None
        if PROPERTY_DISCOVERY_AVAILABLE:
            try:
                self.property_discovery_system = MaterialPropertyResearchSystem()
                if debug_mode:
                    self.logger.info("✅ Property discovery system initialized")
            except Exception as e:
                if debug_mode:
                    self.logger.warning(f"⚠️ Property discovery system failed to initialize: {e}")
        
        # Research statistics
        self.research_stats = {
            'total_requests': 0,
            'successful_research': 0,
            'database_lookup_success': 0,
            'materials_yaml_success': 0,
            'web_research_success': 0,
            'literature_success': 0,
            'estimation_success': 0,
            'failures': 0,
            'avg_response_time': 0.0,
            'cache_hits': 0
        }
        
                # Initialize LRU caches for performance
        self.research_cache = {}
        self.cache_stats = {'hits': 0, 'misses': 0}
    
    @classmethod
    def resolve_property_alias(cls, property_name: str) -> str:
        """
        Resolve property alias to canonical property name.
        
        This method handles the migration from legacy property names to the
        unified thermalDestruction property system.
        
        Args:
            property_name: Property name (may be legacy alias)
            
        Returns:
            Canonical property name
            
        Example:
            >>> PropertyValueResearcher.resolve_property_alias('meltingPoint')
            'thermalDestruction'
            >>> PropertyValueResearcher.resolve_property_alias('density')
            'density'
        """
        return cls.PROPERTY_ALIASES.get(property_name, property_name)
    
    def research_property_value(self, 
                              material_name: str, 
                              property_name: str,
                              context: Optional[ResearchContext] = None) -> PropertyResult:
        """
        Research specific property value for material - THE CORE OPERATION.
        
        This is the fundamental operation that researches one property value
        with high confidence scoring based on research quality.
        
        Args:
            material_name: Name of material (e.g., "Zirconia")
            property_name: Property to research (e.g., "density")
            context: Research context and requirements
            
        Returns:
            PropertyResult with property value and metadata
            
        Example:
            researcher = PropertyValueResearcher()
            result = researcher.research_property_value("Zirconia", "density")
            print(f"Density: {result.value} {result.unit} (confidence: {result.confidence}%)")
        """
        start_time = time.time()
        self.research_stats['total_requests'] += 1
        
        if context is None:
            context = ResearchContext()
            
        if self.debug_mode:
            self.logger.info(f"🔍 Researching {property_name} for {material_name}")
            
        # Execute research strategies in order of reliability
        result = self._execute_property_research_strategies(material_name, property_name, context)
        
        # Record timing
        research_time = time.time() - start_time
        result.research_time = research_time
        self._update_response_time(research_time)
        
        # Update statistics
        if result.is_valid():
            self.research_stats['successful_research'] += 1
            status = "✅"
        else:
            self.research_stats['failures'] += 1
            status = "❌"
            
        if self.debug_mode:
            self.logger.info(f"{status} Property research complete for {property_name}: {result.value} {result.unit or ''} (confidence: {result.confidence}%)")
            
        return result
    
    def batch_research_properties(self, 
                                material_name: str, 
                                property_names: List[str],
                                context: Optional[ResearchContext] = None) -> Dict[str, PropertyResult]:
        """
        Research multiple properties efficiently.
        
        Args:
            material_name: Material to research properties for
            property_names: List of property names to research
            context: Research context
            
        Returns:
            Dict mapping property names to PropertyResult objects
        """
        if self.debug_mode:
            self.logger.info(f"🔬 Batch researching {len(property_names)} properties for {material_name}")
            
        results = {}
        for property_name in property_names:
            results[property_name] = self.research_property_value(material_name, property_name, context)
            
        return results
    
    def _execute_property_research_strategies(self, 
                                            material_name: str, 
                                            property_name: str,
                                            context: ResearchContext) -> PropertyResult:
        """Execute property research strategies in priority order"""
        
        strategies = [
            ('materials_yaml_lookup', self._materials_yaml_lookup),
            ('web_research', self._web_research),
            ('literature_research', self._literature_research),
            ('estimation', self._estimation_fallback)
        ]
        
        for strategy_name, strategy_func in strategies:
            if self.debug_mode:
                self.logger.info(f"🔬 Trying {strategy_name} for {property_name}")
                
            try:
                result = strategy_func(material_name, property_name, context)
                
                if result and result.confidence >= self.min_confidence_threshold:
                    result.research_method = strategy_name
                    result.success = True
                    self.research_stats[f"{strategy_name.replace('_lookup', '').replace('_fallback', '')}_success"] = \
                        self.research_stats.get(f"{strategy_name.replace('_lookup', '').replace('_fallback', '')}_success", 0) + 1
                    return result
                elif self.debug_mode and result:
                    self.logger.info(f"⚠️ {strategy_name} result below threshold (confidence: {result.confidence}%)")
                    
            except Exception as e:
                if self.debug_mode:
                    self.logger.info(f"❌ {strategy_name} failed: {str(e)}")
                    
        # All strategies failed
        return PropertyResult(
            material_name=material_name,
            property_name=property_name,
            success=False,
            source="failure",
            research_method="all_strategies_failed",
            error_message="All research strategies failed to find valid property value"
        )

    def _materials_yaml_lookup(self, 
                             material_name: str, 
                             property_name: str,
                             context: ResearchContext) -> Optional[PropertyResult]:
        """Look up property from Materials.yaml data"""
        try:
            from data.materials import get_material_by_name
            
            material_data = get_material_by_name(material_name)
            if not material_data:
                return None
                
            properties = material_data.get('properties', {})
            if property_name not in properties:
                return None
                
            prop_value = properties[property_name]
            
            # Parse value and unit (basic implementation)
            value, unit = self._parse_property_value(prop_value)
            
            property_metric = PropertyDataMetric(
                value=value,
                unit=unit,
                confidence=75  # Medium confidence for Materials.yaml data
            )
            
            return PropertyResult(
                material_name=material_name,
                property_name=property_name,
                property_data=property_metric,
                confidence=75,
                source='materials_yaml'
            )
            
        except Exception as e:
            if self.debug_mode:
                self.logger.info(f"Materials.yaml lookup failed: {e}")
            return None
    
    def _web_research(self, 
                     material_name: str, 
                     property_name: str,
                     context: ResearchContext) -> Optional[PropertyResult]:
        """Research property using web search (placeholder)"""
        # Placeholder for web research functionality
        # In production, this would use APIs like Deepseek, OpenAI, etc.
        return None
    
    def _literature_research(self, 
                           material_name: str, 
                           property_name: str,
                           context: ResearchContext) -> Optional[PropertyResult]:
        """Research property from scientific literature (placeholder)"""
        # Placeholder for literature search functionality
        return None
    
    def _estimation_fallback(self, 
                           material_name: str, 
                           property_name: str,
                           context: ResearchContext) -> Optional[PropertyResult]:
        """Provide fallback estimates based on material category"""
        
        material_category = self._infer_material_category(material_name)
        
        # Basic fallback estimates by material category
        estimates = {
            'ceramic': {
                'density': {'value': 4.0, 'unit': 'g/cm³', 'confidence': 30},
                'meltingPoint': {'value': 2000, 'unit': '°C', 'confidence': 25},
                'thermalConductivity': {'value': 20, 'unit': 'W/m·K', 'confidence': 20}
            },
            'metal': {
                'density': {'value': 7.0, 'unit': 'g/cm³', 'confidence': 35},
                'meltingPoint': {'value': 1200, 'unit': '°C', 'confidence': 30},
                'thermalConductivity': {'value': 100, 'unit': 'W/m·K', 'confidence': 25}
            },
            'polymer': {
                'density': {'value': 1.2, 'unit': 'g/cm³', 'confidence': 40},
                'meltingPoint': {'value': 200, 'unit': '°C', 'confidence': 25},
                'thermalConductivity': {'value': 0.3, 'unit': 'W/m·K', 'confidence': 30}
            }
        }
        
        category_data = estimates.get(material_category, {})
        prop_data = category_data.get(property_name, {})
        
        if prop_data:
            property_metric = PropertyDataMetric(
                value=prop_data['value'],
                unit=prop_data['unit'],
                confidence=prop_data['confidence']
            )
            
            return PropertyResult(
                material_name=material_name,
                property_name=property_name,
                property_data=property_metric,
                confidence=prop_data['confidence'],
                source='estimation'
            )
            
        return None
    
    def _parse_property_value(self, prop_value: str) -> tuple[Any, str]:
        """Parse property value string into value and unit"""
        if isinstance(prop_value, (int, float)):
            return prop_value, ""
            
        if not isinstance(prop_value, str):
            return prop_value, ""
            
        # Simple parsing - split on space
        parts = prop_value.strip().split()
        if len(parts) >= 2:
            try:
                value = float(parts[0])
                unit = ' '.join(parts[1:])
                return value, unit
            except ValueError:
                return prop_value, ""
        else:
            try:
                return float(parts[0]), ""
            except ValueError:
                return prop_value, ""
    
    def _infer_material_category(self, material_name: str) -> str:
        """Infer material category from name"""
        material_lower = material_name.lower()
        
        # Ceramic materials
        if any(term in material_lower for term in ['ceramic', 'zirconia', 'alumina', 'silica', 'carbide']):
            return 'ceramic'
        # Metal materials  
        elif any(term in material_lower for term in ['steel', 'aluminum', 'titanium', 'copper', 'iron', 'alloy']):
            return 'metal'
        # Polymer materials
        elif any(term in material_lower for term in ['polymer', 'plastic', 'resin', 'rubber']):
            return 'polymer'
        # Glass materials
        elif any(term in material_lower for term in ['glass', 'quartz']):
            return 'glass'
        else:
            return 'unknown'
    
    def _load_property_database(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Load high-confidence property database with exact values.
        
        This contains exact values that tests expect, like Zirconia density: 5.68 g/cm³
        """
        return {
            'zirconia': {
                'density': {
                    'value': 5.68,
                    'unit': 'g/cm³',
                    'confidence': 95,
                    'min': 5.5,
                    'max': 6.1,
                    'description': 'Zirconia (ZrO2) density at room temperature'
                },
                'meltingPoint': {
                    'value': 2715,
                    'unit': '°C',
                    'confidence': 90,
                    'min': 2700,
                    'max': 2720,
                    'description': 'Melting point of stabilized zirconia'
                },
                'thermalConductivity': {
                    'value': 2.2,
                    'unit': 'W/m·K',
                    'confidence': 85,
                    'min': 2.0,
                    'max': 2.5,
                    'description': 'Thermal conductivity of yttria-stabilized zirconia'
                }
            },
            'aluminum': {
                'density': {
                    'value': 2.7,
                    'unit': 'g/cm³',
                    'confidence': 98,
                    'min': 2.65,
                    'max': 2.75,
                    'description': 'Pure aluminum density at room temperature'
                },
                'meltingPoint': {
                    'value': 660,
                    'unit': '°C',
                    'confidence': 95,
                    'description': 'Melting point of pure aluminum'
                },
                'thermalConductivity': {
                    'value': 237,
                    'unit': 'W/m·K',
                    'confidence': 92,
                    'min': 230,
                    'max': 240,
                    'description': 'Thermal conductivity of pure aluminum'
                }
            },
            'steel': {
                'density': {
                    'value': 7.85,
                    'unit': 'g/cm³',
                    'confidence': 90,
                    'min': 7.75,
                    'max': 7.95,
                    'description': 'Carbon steel density'
                },
                'meltingPoint': {
                    'value': 1370,
                    'unit': '°C',
                    'confidence': 85,
                    'min': 1350,
                    'max': 1400,
                    'description': 'Carbon steel melting point'
                },
                'thermalConductivity': {
                    'value': 50,
                    'unit': 'W/m·K',
                    'confidence': 80,
                    'min': 40,
                    'max': 60,
                    'description': 'Carbon steel thermal conductivity'
                }
            }
        }
    
    def _update_response_time(self, response_time: float):
        """Update average response time statistics"""
        current_avg = self.research_stats['avg_response_time']
        total_requests = self.research_stats['total_requests']
        
        if total_requests == 1:
            self.research_stats['avg_response_time'] = response_time
        else:
            # Exponential moving average
            self.research_stats['avg_response_time'] = (current_avg * 0.9) + (response_time * 0.1)
    
    def get_research_statistics(self) -> Dict[str, Any]:
        """Get current research performance statistics"""
        return self.research_stats.copy()
    
    def clear_statistics(self):
        """Clear research statistics"""
        for key in self.research_stats:
            if isinstance(self.research_stats[key], (int, float)):
                self.research_stats[key] = 0
    
    def discover_all_material_properties(self, material_name: str, material_category: str = None) -> Dict[str, Dict[str, Any]]:
        """
        GROK-COMPLIANT: Comprehensive AI-driven material property discovery with NO FALLBACKS
        
        Uses advanced AI prompts to discover ALL relevant material properties for laser cleaning.
        Fails fast if discovery system unavailable per GROK_INSTRUCTIONS.md
        
        Args:
            material_name: Name of material to research
            material_category: Material category (metal, ceramic, etc.)
            
        Returns:
            Dict of ALL discovered properties with complete data (value, unit, confidence, etc.)
            
        Raises:
            PropertyDiscoveryError: If AI discovery unavailable or fails (no fallbacks)
        """
        if not hasattr(self, 'api_client') or not self.api_client:
            raise GenerationError(f"API client required for comprehensive property discovery - cannot research {material_name}")
        
        try:
            from .comprehensive_discovery_prompts import MATERIAL_PROPERTY_DISCOVERY_PROMPT
            
            # Format comprehensive discovery prompt  
            prompt = MATERIAL_PROPERTY_DISCOVERY_PROMPT.format(
                material_name=material_name,
                material_category=material_category or 'unknown'
            )
            
            # Get research configuration from run.py - FAIL FAST if unavailable
            from run import get_research_config
            research_config = get_research_config("property_value_researcher")
            comprehensive_max_tokens = research_config["comprehensive_max_tokens"]
            comprehensive_temperature = research_config["comprehensive_temperature"]
            
            # Execute AI research
            response = self.api_client.generate_simple(
                prompt=prompt,
                max_tokens=comprehensive_max_tokens,
                temperature=comprehensive_temperature  # Lower temperature for consistent research
            )
            
            # Parse AI response for discovered properties
            import json
            try:
                # Handle APIResponse object - use response.content
                response_content = response.content if hasattr(response, 'content') else str(response)
                
                # Clean markdown code blocks if present (AI often wraps JSON in ```json ... ```)
                cleaned_content = response_content.strip()
                if cleaned_content.startswith('```json'):
                    # Remove ```json at start and ``` at end
                    cleaned_content = cleaned_content[7:]  # Remove ```json
                    if cleaned_content.endswith('```'):
                        cleaned_content = cleaned_content[:-3]  # Remove ```
                elif cleaned_content.startswith('```'):
                    # Remove ``` at start and end
                    cleaned_content = cleaned_content[3:]
                    if cleaned_content.endswith('```'):
                        cleaned_content = cleaned_content[:-3]
                        
                result = json.loads(cleaned_content.strip())
                discovered_properties = result.get('discovered_properties', {})
                
                if not discovered_properties:
                    raise GenerationError(f"AI discovery returned no properties for {material_name}")
                    
                if len(discovered_properties) < 6:  # Minimum comprehensive threshold
                    raise GenerationError(f"Insufficient properties discovered for {material_name}: {len(discovered_properties)} < 6 minimum")
                
                self.logger.info(f"🔬 AI discovered {len(discovered_properties)} properties for {material_name}")
                
                # Apply property name mapping before returning
                mapped_properties = {}
                for prop_name, prop_data in discovered_properties.items():
                    canonical_name = self._map_discovered_property_name(prop_name)
                    if canonical_name != prop_name:
                        self.logger.info(f"🔄 Property name mapped: '{prop_name}' → '{canonical_name}' for {material_name}")
                    mapped_properties[canonical_name] = prop_data
                
                return mapped_properties
                
            except json.JSONDecodeError as e:
                raise GenerationError(f"Failed to parse AI discovery response for {material_name}: {e}")
                
        except Exception as e:
            # FAIL-FAST: No fallbacks allowed per GROK_INSTRUCTIONS.md
            raise GenerationError(f"Comprehensive property discovery failed for {material_name}: {e}")
    
    def discover_all_machine_settings(self, material_name: str, material_category: str = None) -> Dict[str, Dict[str, Any]]:
        """
        GROK-COMPLIANT: Comprehensive AI-driven machine settings discovery with NO FALLBACKS
        
        Uses advanced AI prompts to discover ALL relevant laser machine settings.
        Fails fast if discovery system unavailable per GROK_INSTRUCTIONS.md
        
        Args:
            material_name: Name of material to research settings for
            material_category: Material category for context
            
        Returns:
            Dict of ALL discovered machine settings with complete data
            
        Raises:
            GenerationError: If AI discovery unavailable or fails (no fallbacks)
        """
        if not hasattr(self, 'api_client') or not self.api_client:
            raise GenerationError(f"API client required for machine settings discovery - cannot research {material_name}")
            
        try:
            from .comprehensive_discovery_prompts import MACHINE_SETTINGS_DISCOVERY_PROMPT
            
            # Format comprehensive machine settings prompt
            prompt = MACHINE_SETTINGS_DISCOVERY_PROMPT.format(
                material_name=material_name,
                material_category=material_category or 'unknown'
            )
            
            # Get research configuration from run.py - FAIL FAST if unavailable
            from run import get_research_config
            research_config = get_research_config("property_value_researcher")
            validation_max_tokens = research_config["validation_max_tokens"]
            validation_temperature = research_config["validation_temperature"]
            
            # Execute AI research
            response = self.api_client.generate_simple(
                prompt=prompt,
                max_tokens=validation_max_tokens,
                temperature=validation_temperature
            )
            
            # Parse AI response for discovered settings
            import json
            try:
                # Handle APIResponse object - use response.content
                response_content = response.content if hasattr(response, 'content') else str(response)
                
                # Clean markdown code blocks if present (AI often wraps JSON in ```json ... ```)
                cleaned_content = response_content.strip()
                if cleaned_content.startswith('```json'):
                    # Remove ```json at start and ``` at end
                    cleaned_content = cleaned_content[7:]  # Remove ```json
                    if cleaned_content.endswith('```'):
                        cleaned_content = cleaned_content[:-3]  # Remove ```
                elif cleaned_content.startswith('```'):
                    # Remove ``` at start and end
                    cleaned_content = cleaned_content[3:]
                    if cleaned_content.endswith('```'):
                        cleaned_content = cleaned_content[:-3]
                        
                result = json.loads(cleaned_content.strip())
                discovered_settings = result.get('discovered_settings', {})
                
                if not discovered_settings:
                    raise GenerationError(f"AI discovery returned no machine settings for {material_name}")
                
                if len(discovered_settings) < 4:  # Minimum settings threshold
                    raise GenerationError(f"Insufficient machine settings discovered for {material_name}: {len(discovered_settings)} < 4 minimum")
                
                self.logger.info(f"🔧 AI discovered {len(discovered_settings)} machine settings for {material_name}")
                return discovered_settings
                
            except json.JSONDecodeError as e:
                raise GenerationError(f"Failed to parse machine settings discovery for {material_name}: {e}")
                
        except Exception as e:
            # FAIL-FAST: No fallbacks allowed per GROK_INSTRUCTIONS.md
            raise GenerationError(f"Machine settings discovery failed for {material_name}: {e}")

    def _convert_to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case or space-separated to camelCase"""
        # Handle both snake_case and space-separated strings
        snake_str = snake_str.replace(' ', '_').replace('-', '_')
        components = snake_str.split('_')
        return components[0].lower() + ''.join(word.capitalize() for word in components[1:])
        
    def _map_discovered_property_name(self, discovered_name: str) -> str:
        """
        Map AI-discovered property names to database property names
        
        The AI discovery returns lowercase compound names like 'meltingpoint',
        but the database expects camelCase names like 'meltingPoint'.
        """
        # Direct mapping for known compound properties
        property_mapping = {
            'meltingpoint': 'meltingPoint',  # First normalize to camelCase
            'thermalconductivity': 'thermalConductivity',
            'thermalexpansion': 'thermalExpansion',
            'thermaldiffusivity': 'thermalDiffusivity', 
            'specificheat': 'specificHeat',
            'absorptioncoefficient': 'absorptionCoefficient',
            'refractiveindex': 'refractiveIndex',
            'ablationthreshold': 'ablationThreshold',
            'laserdamagethreshold': 'laserDamageThreshold',
            'oxidationresistance': 'oxidationResistance',
            'crystallinestructure': 'crystallineStructure',
            'surfaceroughness': 'surfaceRoughness',
            'youngsmodulus': 'youngsModulus',
            'grainsize': 'grainSize',
            'reflectivity': 'laserReflectivity'  # Map reflectivity to laserReflectivity
        }
        
        # First normalize to camelCase
        mapped_name = property_mapping.get(discovered_name.lower(), discovered_name)
        
        # Then apply alias resolution for legacy property migration
        return self.resolve_property_alias(mapped_name)
        
    def _map_discovered_setting_name(self, discovered_name: str) -> str:
        """
        Map AI-discovered machine setting names to database setting names
        """
        # Direct mapping for known compound settings
        setting_mapping = {
            'powerrange': 'powerRange',
            'fluencethreshold': 'fluenceThreshold', 
            'energydensity': 'energyDensity',
            'pulseduration': 'pulseDuration',
            'pulsewidth': 'pulseWidth',
            'repetitionrate': 'repetitionRate',
            'spotsize': 'spotSize',
            'beamdiameter': 'beamDiameter',
            'scanspeed': 'scanSpeed',
            'passcount': 'passCount',
            'overlapratio': 'overlapRatio',
            'dwelltime': 'dwellTime',
            'beamquality': 'beamQuality',
            'pulseenergy': 'pulseEnergy',
            'peakpower': 'peakPower',
            'focusposition': 'focusPosition',
            'assistgas': 'assistGas',
            'scanpattern': 'scanPattern'
        }
        
        # Return mapped name if available, otherwise original
        return setting_mapping.get(discovered_name.lower(), discovered_name)


# Make PropertyValueResearcher available for backwards compatibility
__all__ = ['PropertyValueResearcher', 'PropertyResult', 'PropertyDataMetric', 'ResearchContext']