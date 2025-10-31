#!/usr/bin/env python3
"""
Machine Settings Researcher - Laser Parameter Research System

This module specializes in researching optimal laser machine settings based on 
material properties. Unlike PropertyValueResearcher (which finds material properties),
this system calculates and researches machine parameters like powerRange, wavelength,
pulseDuration based on material characteristics.

Key Capabilities:
1. Research optimal laser parameters for specific materials
2. Calculate power ranges based on material absorption and thermal properties  
3. Determine wavelength effectiveness for different material types
4. Suggest pulse parameters based on material thickness and thermal conductivity
5. Integration with PropertyValueResearcher for material-based calculations

Author: GitHub Copilot
Date: September 25, 2025
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time

# Import PropertyValueResearcher for material property lookup
from .property_value_researcher import PropertyValueResearcher, ResearchContext, PropertyResult


class MachineSettingType(Enum):
    """Types of machine settings for laser processing"""
    POWER = "power"
    WAVELENGTH = "wavelength" 
    PULSE_DURATION = "pulse_duration"
    SPOT_SIZE = "spot_size"
    REPETITION_RATE = "repetition_rate"
    FLUENCE = "fluence"
    PROCESSING_SPEED = "processing_speed"
    THRESHOLD = "threshold"


@dataclass
class MachineSettingResult:
    """Result of machine setting research"""
    setting_name: str
    value: Optional[Any] = None
    unit: Optional[str] = None
    min_range: Optional[float] = None
    max_range: Optional[float] = None
    confidence: int = 0
    source: str = "failure"
    research_method: str = "none"
    material_dependencies: List[str] = field(default_factory=list)
    calculation_notes: str = ""
    
    def is_valid(self) -> bool:
        """Check if result has valid data"""
        return self.value is not None and self.confidence > 0
    
    def is_high_quality(self) -> bool:
        """Check if result meets high quality standards"""
        return self.is_valid() and self.confidence >= 80
    
    def to_machine_setting_format(self) -> Dict[str, Any]:
        """Convert to machine settings YAML format (like your Zirconia file)"""
        if not self.is_valid():
            return None
            
        result = {
            'value': self.value,
            'confidence': self.confidence
        }
        
        if self.unit:
            result['unit'] = self.unit
        if self.min_range is not None:
            result['min'] = self.min_range
        if self.max_range is not None:
            result['max'] = self.max_range
            
        return result


@dataclass
class LaserProcessingContext:
    """Context for laser processing research"""
    application_type: str = "cleaning"  # cleaning, cutting, welding, marking
    laser_type: Optional[str] = None  # fiber, nd_yag, co2, diode
    target_wavelength: Optional[str] = None
    processing_requirements: List[str] = field(default_factory=list)
    safety_constraints: List[str] = field(default_factory=list)
    precision_level: str = "standard"  # rough, standard, precision, ultra_precision


class MachineSettingsResearcher:
    """
    Specialized researcher for laser machine settings and parameters.
    
    Works in conjunction with PropertyValueResearcher to determine optimal
    laser parameters based on material properties and processing requirements.
    
    Core Research Strategies:
    1. Material-Based Calculation: Use material properties to calculate optimal settings
    2. Application-Specific Lookup: Database of settings for specific applications
    3. Physics-Based Modeling: Calculate parameters using laser-material interaction models
    4. Literature Research: Search for published laser processing parameters
    5. Empirical Estimation: Fallback estimates based on material category
    """
    
    def __init__(self, 
                 material_researcher: Optional[PropertyValueResearcher] = None,
                 confidence_threshold: int = 50,
                 debug_mode: bool = False):
        """
        Initialize Machine Settings Researcher.
        
        Args:
            material_researcher: PropertyValueResearcher instance for material data
            confidence_threshold: Minimum confidence for valid results
            debug_mode: Enable debug logging
        """
        self.material_researcher = material_researcher or PropertyValueResearcher()
        self.confidence_threshold = confidence_threshold
        self.debug_mode = debug_mode
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        if debug_mode:
            self.logger.setLevel(logging.DEBUG)
            
        # Research statistics
        self.research_stats = {
            'total_requests': 0,
            'successful_research': 0,
            'material_calc_success': 0,
            'database_lookup_success': 0,
            'physics_model_success': 0,
            'literature_success': 0,
            'estimation_success': 0,
            'failures': 0,
            'avg_response_time': 0.0,
            'cache_hits': 0
        }
        
        # Material-specific laser parameters database
        self.material_laser_params = self._load_material_laser_database()
    
    def research_machine_setting(self, 
                                material_name: str, 
                                setting_name: str,
                                context: Optional[LaserProcessingContext] = None) -> MachineSettingResult:
        """
        Research optimal machine setting for material - THE CORE OPERATION.
        
        This is the fundamental operation that researches one machine setting
        based on material properties and processing context.
        
        Args:
            material_name: Name of material (e.g., "Zirconia") 
            setting_name: Machine setting to research (e.g., "powerRange")
            context: Processing context and requirements
            
        Returns:
            MachineSettingResult with setting value and metadata
            
        Example:
            researcher = MachineSettingsResearcher()
            result = researcher.research_machine_setting("Zirconia", "powerRange")
            print(f"Power: {result.value} {result.unit} (confidence: {result.confidence}%)")
        """
        start_time = time.time()
        self.research_stats['total_requests'] += 1
        
        if context is None:
            context = LaserProcessingContext()
            
        if self.debug_mode:
            self.logger.info(f"🔍 Researching {setting_name} for {material_name} laser processing")
            
        # Execute research strategies in order of reliability
        result = self._execute_machine_setting_strategies(material_name, setting_name, context)
        
        # Record timing
        response_time = time.time() - start_time
        self._update_response_time(response_time)
        
        # Update statistics
        if result.is_valid():
            self.research_stats['successful_research'] += 1
            status = "✅"
        else:
            self.research_stats['failures'] += 1
            status = "❌"
            
        if self.debug_mode:
            self.logger.info(f"{status} Machine setting research complete for {setting_name}: {result.value} {result.unit or ''} (confidence: {result.confidence}%)")
            
        return result
    
    def batch_research_machine_settings(self, 
                                      material_name: str, 
                                      setting_names: List[str],
                                      context: Optional[LaserProcessingContext] = None) -> Dict[str, MachineSettingResult]:
        """
        Research multiple machine settings efficiently.
        
        Args:
            material_name: Material to research settings for
            setting_names: List of setting names to research
            context: Processing context
            
        Returns:
            Dict mapping setting names to MachineSettingResult objects
        """
        if self.debug_mode:
            self.logger.info(f"🔬 Batch researching {len(setting_names)} settings for {material_name}")
            
        results = {}
        for setting_name in setting_names:
            results[setting_name] = self.research_machine_setting(material_name, setting_name, context)
            
        return results
    
    def _execute_machine_setting_strategies(self, 
                                          material_name: str, 
                                          setting_name: str,
                                          context: LaserProcessingContext) -> MachineSettingResult:
        """Execute machine setting research strategies in priority order"""
        
        strategies = [
            ('material_based_calculation', self._material_based_calculation),
            ('application_database_lookup', self._application_database_lookup), 
            ('physics_based_modeling', self._physics_based_modeling),
            ('literature_research', self._literature_research),
            ('empirical_estimation', self._empirical_estimation)
        ]
        
        for strategy_name, strategy_func in strategies:
            if self.debug_mode:
                self.logger.info(f"🔬 Trying {strategy_name} for {setting_name}")
                
            try:
                result = strategy_func(material_name, setting_name, context)
                
                if result and result.confidence >= self.confidence_threshold:
                    result.research_method = strategy_name
                    self.research_stats[f"{strategy_name.split('_')[0]}_success"] = self.research_stats.get(f"{strategy_name.split('_')[0]}_success", 0) + 1
                    return result
                elif self.debug_mode:
                    confidence = result.confidence if result else 0
                    self.logger.info(f"⚠️ {strategy_name} result below threshold (confidence: {confidence}%)")
                    
            except Exception as e:
                if self.debug_mode:
                    self.logger.info(f"❌ {strategy_name} failed: {str(e)}")
                    
        # All strategies failed
        return MachineSettingResult(
            setting_name=setting_name,
            source="failure", 
            research_method="all_strategies_failed"
        )
    
    def _material_based_calculation(self, 
                                  material_name: str, 
                                  setting_name: str,
                                  context: LaserProcessingContext) -> Optional[MachineSettingResult]:
        """
        Calculate machine settings based on material properties.
        
        This is the most reliable method - uses actual material properties
        to calculate optimal laser parameters.
        """
        # Get material properties needed for calculations
        material_context = ResearchContext(
            material_category=self._infer_material_category(material_name),
            application_type=context.application_type,
            priority_level=1
        )
        
        # Research key material properties
        density = self.material_researcher.research_property_value(material_name, 'density', material_context)
        melting_point = self.material_researcher.research_property_value(material_name, 'meltingPoint', material_context)
        thermal_conductivity = self.material_researcher.research_property_value(material_name, 'thermalConductivity', material_context)
        
        # Calculate based on setting type and material properties
        if setting_name.lower() in ['powerrange', 'power']:
            return self._calculate_power_range(material_name, density, melting_point, thermal_conductivity, context)
        elif setting_name.lower() == 'wavelength':
            return self._calculate_optimal_wavelength(material_name, context)
        elif setting_name.lower() in ['pulseduration', 'pulse_duration']:
            return self._calculate_pulse_duration(material_name, thermal_conductivity, context)
        elif setting_name.lower() in ['fluencerange', 'fluence']:
            return self._calculate_fluence_range(material_name, density, context)
        else:
            return None
    
    def _calculate_power_range(self, 
                             material_name: str,
                             density: PropertyResult,
                             melting_point: PropertyResult, 
                             thermal_conductivity: PropertyResult,
                             context: LaserProcessingContext) -> Optional[MachineSettingResult]:
        """Calculate optimal power range based on material properties"""
        
        # Base power calculation factors
        base_power = 100  # W baseline
        
        # Material category adjustments
        material_category = self._infer_material_category(material_name)
        if material_category == 'ceramic':
            category_factor = 1.2  # Ceramics need higher power
        elif material_category == 'metal':
            category_factor = 1.0   # Metals are baseline
        elif material_category == 'polymer':
            category_factor = 0.6   # Polymers need lower power
        else:
            category_factor = 1.0
            
        # Density adjustment (higher density = higher power needed)
        density_factor = 1.0
        if density.is_valid():
            density_val = float(density.value)
            if density_val > 5.0:  # High density materials
                density_factor = 1.3
            elif density_val > 2.0:  # Medium density 
                density_factor = 1.1
            else:  # Low density
                density_factor = 0.9
                
        # Melting point adjustment (higher melting point = higher power)
        melting_factor = 1.0
        if melting_point.is_valid():
            mp_val = float(melting_point.value)
            if mp_val > 2000:  # Very high melting point
                melting_factor = 1.4
            elif mp_val > 1000:  # High melting point
                melting_factor = 1.2
            elif mp_val > 500:   # Medium melting point
                melting_factor = 1.0
            else:  # Low melting point
                melting_factor = 0.8
                
        # Application adjustment
        app_factor = 1.0
        if context.application_type == 'cleaning':
            app_factor = 1.0   # Baseline for cleaning
        elif context.application_type == 'cutting':
            app_factor = 2.0   # Cutting needs much higher power
        elif context.application_type == 'marking':
            app_factor = 0.7   # Marking needs lower power
        elif context.application_type == 'welding':
            app_factor = 3.0   # Welding needs highest power
            
        # Calculate optimal power
        optimal_power = base_power * category_factor * density_factor * melting_factor * app_factor
        
        # Calculate range (±40% of optimal)
        min_power = optimal_power * 0.6
        max_power = optimal_power * 1.4
        
        # Round to practical values
        optimal_power = round(optimal_power)
        min_power = round(min_power)
        max_power = round(max_power)
        
        # Confidence based on available data
        confidence = 60  # Base confidence for calculation
        if density.is_valid():
            confidence += 10
        if melting_point.is_valid():
            confidence += 15
        if thermal_conductivity.is_valid():
            confidence += 10
            
        confidence = min(confidence, 95)  # Cap at 95%
        
        dependencies = []
        if density.is_valid():
            dependencies.append(f"density: {density.value} {density.unit}")
        if melting_point.is_valid():
            dependencies.append(f"meltingPoint: {melting_point.value} {melting_point.unit}")
            
        return MachineSettingResult(
            setting_name='powerRange',
            value=optimal_power,
            unit='W',
            min_range=min_power,
            max_range=max_power,
            confidence=confidence,
            source='material_calculation',
            material_dependencies=dependencies,
            calculation_notes=f"Calculated for {material_category} material using density, melting point, and {context.application_type} application"
        )
    
    def _calculate_optimal_wavelength(self, 
                                    material_name: str,
                                    context: LaserProcessingContext) -> Optional[MachineSettingResult]:
        """Calculate optimal wavelength based on material type and application"""
        
        material_category = self._infer_material_category(material_name)
        
        # Wavelength recommendations by material and application
        wavelength_map = {
            'ceramic': {
                'cleaning': 1064,  # Nd:YAG excellent for ceramics
                'cutting': 1064,
                'marking': 532,    # Green laser for fine marking
                'welding': 1064
            },
            'metal': {
                'cleaning': 1064,  # Standard for metal cleaning
                'cutting': 1070,   # Fiber laser optimal
                'marking': 1064,
                'welding': 1070
            },
            'polymer': {
                'cleaning': 355,   # UV for gentle polymer processing
                'cutting': 355,
                'marking': 355,
                'welding': 1064
            }
        }
        
        optimal_wavelength = wavelength_map.get(material_category, {}).get(context.application_type, 1064)
        
        confidence = 85 if material_category in wavelength_map else 60
        
        return MachineSettingResult(
            setting_name='wavelength',
            value=optimal_wavelength,
            unit='nm', 
            confidence=confidence,
            source='material_wavelength_map',
            calculation_notes=f"Optimal wavelength for {material_category} {context.application_type}"
        )
    
    def _calculate_pulse_duration(self, 
                                material_name: str,
                                thermal_conductivity: PropertyResult,
                                context: LaserProcessingContext) -> Optional[MachineSettingResult]:
        """Calculate pulse duration based on thermal properties"""
        
        # Base pulse duration for different applications (nanoseconds)
        base_durations = {
            'cleaning': 50,   # Medium pulses for cleaning
            'cutting': 100,   # Longer pulses for cutting
            'marking': 20,    # Short pulses for precision
            'welding': 200    # Long pulses for welding
        }
        
        base_duration = base_durations.get(context.application_type, 50)
        
        # Adjust based on thermal conductivity
        if thermal_conductivity.is_valid():
            tc_val = float(thermal_conductivity.value)
            if tc_val > 100:     # High thermal conductivity - need shorter pulses
                tc_factor = 0.7
            elif tc_val > 50:    # Medium thermal conductivity
                tc_factor = 0.85
            else:                # Low thermal conductivity - can use longer pulses
                tc_factor = 1.2
        else:
            tc_factor = 1.0
            
        optimal_duration = base_duration * tc_factor
        min_duration = optimal_duration * 0.5
        max_duration = optimal_duration * 2.0
        
        confidence = 70 if thermal_conductivity.is_valid() else 60
        
        return MachineSettingResult(
            setting_name='pulseDuration',
            value=round(optimal_duration),
            unit='ns',
            min_range=round(min_duration),
            max_range=round(max_duration), 
            confidence=confidence,
            source='thermal_calculation',
            material_dependencies=[f"thermalConductivity: {thermal_conductivity.value} {thermal_conductivity.unit}"] if thermal_conductivity.is_valid() else [],
            calculation_notes=f"Calculated based on thermal conductivity for {context.application_type}"
        )
    
    def _calculate_fluence_range(self,
                               material_name: str,
                               density: PropertyResult,
                               context: LaserProcessingContext) -> Optional[MachineSettingResult]:
        """Calculate fluence range based on material density and application"""
        
        # Base fluence values (J/cm²)
        base_fluences = {
            'cleaning': 5.0,   # Moderate fluence for cleaning
            'cutting': 15.0,   # High fluence for cutting
            'marking': 3.0,    # Low fluence for marking
            'welding': 20.0    # Very high fluence for welding
        }
        
        base_fluence = base_fluences.get(context.application_type, 5.0)
        
        # Density adjustment
        if density.is_valid():
            density_val = float(density.value)
            if density_val > 5.0:    # High density - need higher fluence
                density_factor = 1.3
            elif density_val > 2.0:  # Medium density
                density_factor = 1.0
            else:                    # Low density - lower fluence
                density_factor = 0.7
        else:
            density_factor = 1.0
            
        optimal_fluence = base_fluence * density_factor
        min_fluence = optimal_fluence * 0.5
        max_fluence = optimal_fluence * 2.5
        
        confidence = 75 if density.is_valid() else 65
        
        return MachineSettingResult(
            setting_name='fluenceRange', 
            value=round(optimal_fluence, 1),
            unit='J/cm²',
            min_range=round(min_fluence, 1),
            max_range=round(max_fluence, 1),
            confidence=confidence,
            source='density_calculation',
            material_dependencies=[f"density: {density.value} {density.unit}"] if density.is_valid() else [],
            calculation_notes=f"Calculated based on material density for {context.application_type}"
        )
    
    def _application_database_lookup(self, 
                                   material_name: str,
                                   setting_name: str, 
                                   context: LaserProcessingContext) -> Optional[MachineSettingResult]:
        """Look up machine settings from application-specific database"""
        
        # This would query a database of known laser processing parameters
        # For now, implement with a basic lookup table
        
        material_key = material_name.lower()
        if material_key in self.material_laser_params:
            material_data = self.material_laser_params[material_key]
            app_data = material_data.get(context.application_type, {})
            
            if setting_name in app_data:
                setting_data = app_data[setting_name]
                return MachineSettingResult(
                    setting_name=setting_name,
                    value=setting_data.get('value'),
                    unit=setting_data.get('unit'),
                    min_range=setting_data.get('min'),
                    max_range=setting_data.get('max'),
                    confidence=setting_data.get('confidence', 70),
                    source='application_database'
                )
                
        return None
    
    def _physics_based_modeling(self, 
                              material_name: str,
                              setting_name: str,
                              context: LaserProcessingContext) -> Optional[MachineSettingResult]:
        """Use physics models to calculate optimal parameters"""
        # Placeholder for advanced physics-based calculations
        # Would implement laser-material interaction models, heat transfer equations, etc.
        return None
    
    def _literature_research(self, 
                           material_name: str,
                           setting_name: str,
                           context: LaserProcessingContext) -> Optional[MachineSettingResult]:
        """Research parameters from scientific literature"""
        # Placeholder for literature search and extraction
        # Would search research papers, technical publications, etc.
        return None
    
    def _empirical_estimation(self, 
                            material_name: str,
                            setting_name: str,
                            context: LaserProcessingContext) -> Optional[MachineSettingResult]:
        """Provide empirical estimates based on material category"""
        
        material_category = self._infer_material_category(material_name)
        
        # Basic empirical estimates by material category and setting
        estimates = {
            'ceramic': {
                'powerRange': {'value': 150, 'unit': 'W', 'min': 100, 'max': 300, 'confidence': 50},
                'wavelength': {'value': 1064, 'unit': 'nm', 'confidence': 60}, 
                'pulseDuration': {'value': 50, 'unit': 'ns', 'min': 20, 'max': 100, 'confidence': 40}
            },
            'metal': {
                'powerRange': {'value': 200, 'unit': 'W', 'min': 150, 'max': 400, 'confidence': 50},
                'wavelength': {'value': 1064, 'unit': 'nm', 'confidence': 60},
                'pulseDuration': {'value': 30, 'unit': 'ns', 'min': 10, 'max': 80, 'confidence': 40}
            },
            'polymer': {
                'powerRange': {'value': 50, 'unit': 'W', 'min': 20, 'max': 100, 'confidence': 45},
                'wavelength': {'value': 355, 'unit': 'nm', 'confidence': 55},
                'pulseDuration': {'value': 100, 'unit': 'ns', 'min': 50, 'max': 200, 'confidence': 35}
            }
        }
        
        category_data = estimates.get(material_category, {})
        setting_data = category_data.get(setting_name, {})
        
        if setting_data:
            return MachineSettingResult(
                setting_name=setting_name,
                value=setting_data.get('value'),
                unit=setting_data.get('unit'), 
                min_range=setting_data.get('min'),
                max_range=setting_data.get('max'),
                confidence=setting_data.get('confidence', 30),
                source='empirical_estimate',
                calculation_notes=f"Empirical estimate for {material_category} materials"
            )
            
        return None
    
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
    
    def _load_material_laser_database(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Load database of known material laser processing parameters"""
        
        # Basic database - in production this would come from external sources
        return {
            'zirconia': {
                'cleaning': {
                    'powerRange': {'value': 120, 'unit': 'W', 'min': 80, 'max': 200, 'confidence': 75},
                    'wavelength': {'value': 1064, 'unit': 'nm', 'confidence': 85},
                    'pulseDuration': {'value': 30, 'unit': 'ns', 'min': 20, 'max': 50, 'confidence': 70}
                }
            },
            'aluminum': {
                'cleaning': {
                    'powerRange': {'value': 100, 'unit': 'W', 'min': 70, 'max': 150, 'confidence': 80},
                    'wavelength': {'value': 1064, 'unit': 'nm', 'confidence': 90}
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


__all__ = ['MachineSettingsResearcher', 'MachineSettingResult', 'LaserProcessingContext', 'MachineSettingType']