#!/usr/bin/env python3
"""
Material Machine Settings Enhancement System

Specialized generator system for optimizing laser machine settings
based on material properties and category-specific processing requirements.

This system provides:
- Material-specific laser parameter optimization
- Category-aware processing parameter generation
- Machine setting validation and safety checks
- Processing efficiency optimization
- Quality prediction based on material characteristics
"""

import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """Laser processing modes"""
    CLEANING = "cleaning"
    CUTTING = "cutting"
    WELDING = "welding"
    MARKING = "marking"
    TEXTURING = "texturing"


class LaserType(Enum):
    """Laser types and wavelengths"""
    FIBER_1064 = ("fiber", 1064)      # Fiber laser, 1064nm
    FIBER_1030 = ("fiber", 1030)      # Ytterbium fiber, 1030nm
    CO2_10600 = ("co2", 10600)        # CO2 laser, 10.6μm
    EXCIMER_308 = ("excimer", 308)     # XeCl excimer, 308nm
    FEMTO_800 = ("femtosecond", 800)   # Ti:Sapphire, 800nm


@dataclass
class MachineSetting:
    """Individual machine setting with analysis"""
    name: str
    value: Union[float, str, int]
    unit: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    confidence: float = 0.0
    sources: List[str] = field(default_factory=list)
    category: str = "general"


@dataclass
class MachineSettingsResult:
    """Complete machine settings analysis result"""
    material_name: str
    material_category: MaterialCategory
    settings: Dict[str, MachineSetting]
    wavelength_analysis: Dict[str, Any]
    power_analysis: Dict[str, Any]
    validation_score: float
    confidence_score: float


class MaterialMachineSettingsEnhancer:
    """
    Material-aware laser machine settings optimization system
    
    Generates optimal laser processing parameters based on:
    - Material category and properties
    - Processing mode requirements
    - Safety considerations
    - Quality objectives
    """
    
    def __init__(self):
        """Initialize machine settings enhancer"""
        self.material_absorption = self._initialize_material_absorption()
        self.category_settings = self._initialize_category_settings()
        self.safety_guidelines = self._initialize_safety_guidelines()
        
        logger.info("Material Machine Settings Enhancer initialized")
    
    def _initialize_material_absorption(self) -> Dict[str, Dict[int, float]]:
        """Initialize material absorption coefficients by wavelength"""
        
        return {
            'metal': {
                1064: 0.05,   # Low absorption at 1064nm (high reflectance)
                10600: 0.8,   # Higher absorption at CO2 wavelength
                308: 0.95     # High absorption at UV
            },
            'ceramic': {
                1064: 0.3,    # Moderate absorption
                10600: 0.85,  # Good absorption at CO2
                308: 0.9      # High UV absorption
            },
            'wood': {
                1064: 0.7,    # Good absorption at IR
                10600: 0.95,  # Excellent absorption at CO2
                308: 0.85     # Good UV absorption
            },
            'plastic': {
                1064: 0.4,    # Variable by polymer type
                10600: 0.9,   # Very good at CO2
                308: 0.95     # Excellent UV absorption
            },
            'composite': {
                1064: 0.5,    # Depends on fiber/matrix
                10600: 0.8,   # Good absorption
                308: 0.9      # High UV absorption
            }
        }
    
    def _initialize_category_settings(self) -> Dict[str, Dict[str, Any]]:
        """Initialize category-specific baseline settings"""
        
        return {
            'metal': {
                'power_range': (50, 500),    # Higher power needed due to reflectance
                'pulse_duration': 'ns',      # Nanosecond pulses typical
                'repetition_rate': (10000, 100000),  # High rep rate
                'fluence_threshold': (0.5, 10.0),
                'spot_size': (20, 200),      # Larger spots for efficiency
                'processing_speed': (100, 2000),
                'primary_wavelength': 1064,
                'challenges': ['high_reflectance', 'heat_affected_zone', 'oxidation'],
                'optimization_focus': 'power_density'
            },
            'ceramic': {
                'power_range': (20, 200),    # Moderate power
                'pulse_duration': 'ns',
                'repetition_rate': (5000, 50000),
                'fluence_threshold': (1.0, 25.0),
                'spot_size': (10, 100),
                'processing_speed': (50, 1000),
                'primary_wavelength': 1064,
                'challenges': ['thermal_shock', 'cracking', 'debris'],
                'optimization_focus': 'thermal_management'
            },
            'wood': {
                'power_range': (10, 100),    # Lower power to avoid burning
                'pulse_duration': 'ms',      # Longer pulses for thermal processing
                'repetition_rate': (100, 5000),  # Lower rep rate
                'fluence_threshold': (0.1, 2.0),
                'spot_size': (50, 300),      # Larger spots for gentle processing
                'processing_speed': (200, 3000),
                'primary_wavelength': 10600,  # CO2 excellent for organics
                'challenges': ['burning', 'charring', 'moisture_effects'],
                'optimization_focus': 'thermal_control'
            },
            'plastic': {
                'power_range': (5, 80),      # Very low power
                'pulse_duration': 'ns',
                'repetition_rate': (1000, 20000),
                'fluence_threshold': (0.05, 1.0),
                'spot_size': (25, 150),
                'processing_speed': (300, 5000),
                'primary_wavelength': 10600,
                'challenges': ['melting', 'toxic_fumes', 'thermal_degradation'],
                'optimization_focus': 'minimal_heat'
            },
            'composite': {
                'power_range': (15, 150),
                'pulse_duration': 'ns',
                'repetition_rate': (2000, 30000),
                'fluence_threshold': (0.2, 5.0),
                'spot_size': (30, 200),
                'processing_speed': (100, 2000),
                'primary_wavelength': 1064,
                'challenges': ['delamination', 'fiber_damage', 'matrix_degradation'],
                'optimization_focus': 'selective_processing'
            }
        }
    
    def _initialize_safety_guidelines(self) -> Dict[str, List[str]]:
        """Initialize safety guidelines by material category"""
        
        return {
            'metal': [
                "Ensure adequate ventilation for metal vapor",
                "Use laser safety eyewear rated for wavelength",
                "Monitor for sparks and hot metal debris",
                "Consider reflective surface hazards"
            ],
            'ceramic': [
                "Provide dust extraction for ceramic particles",
                "Monitor for thermal shock cracking",
                "Use appropriate respiratory protection",
                "Control debris ejection"
            ],
            'wood': [
                "Install fire suppression system",
                "Provide excellent ventilation for organic vapors",
                "Monitor moisture content effects",
                "Prevent ignition and smoldering"
            ],
            'plastic': [
                "Mandatory fume extraction for toxic vapors",
                "Use chemical-resistant ventilation",
                "Monitor for polymer degradation products",
                "Prevent melting and dripping"
            ],
            'composite': [
                "Extract fiber particles and resin vapors",
                "Monitor for delamination stress",
                "Use specialized respiratory protection",
                "Control processing temperature"
            ]
        }
    
    def optimize_machine_settings(
        self,
        material_name: str,
        material_category: str,
        material_properties: Dict[str, Any],
        processing_mode: ProcessingMode = ProcessingMode.CLEANING,
        laser_type: Optional[LaserType] = None
    ) -> MachineSettingsResult:
        """
        Generate optimized machine settings for material processing
        
        Args:
            material_name: Name of the material
            material_category: Material category
            material_properties: Material property data
            processing_mode: Type of processing required
            laser_type: Specific laser type (optional)
            
        Returns:
            Optimized machine settings with validation
        """
        
        try:
            # Get baseline settings for category
            if material_category not in self.category_settings:
                return MachineSettingsResult(
                    success=False,
                    settings=None,
                    validation_warnings=[f"Unknown material category: {material_category}"],
                    optimization_notes=[],
                    safety_considerations=[]
                )
            
            baseline = self.category_settings[material_category]
            
            # Determine optimal wavelength
            optimal_wavelength = self._determine_optimal_wavelength(
                material_category, material_properties, laser_type
            )
            
            # Calculate power requirements
            power_range = self._calculate_power_requirements(
                material_category, material_properties, processing_mode, optimal_wavelength
            )
            
            # Optimize pulse parameters
            pulse_duration, rep_rate = self._optimize_pulse_parameters(
                material_category, material_properties, processing_mode
            )
            
            # Calculate fluence and spot size
            fluence_range, spot_size_range = self._calculate_fluence_and_spot(
                material_category, material_properties, power_range
            )
            
            # Determine processing speed
            speed_range = self._calculate_processing_speed(
                material_category, material_properties, power_range
            )
            
            # Generate quality prediction
            quality_prediction = self._predict_processing_quality(
                material_category, material_properties, power_range
            )
            
            # Compile optimization notes
            optimization_notes = self._generate_optimization_notes(
                material_category, material_properties, baseline
            )
            
            # Get safety considerations
            safety_considerations = self.safety_guidelines.get(material_category, [])
            
            settings = MachineSettings(
                power_range=power_range,
                wavelength=optimal_wavelength,
                pulse_duration=pulse_duration,
                repetition_rate=rep_rate,
                fluence_threshold=fluence_range,
                spot_size=spot_size_range,
                processing_speed=speed_range,
                safety_level=self._determine_safety_level(material_category),
                quality_prediction=quality_prediction,
                optimization_notes=optimization_notes
            )
            
            # Validate settings
            validation_warnings = self._validate_settings(settings, material_category)
            
            return MachineSettingsResult(
                success=True,
                settings=settings,
                validation_warnings=validation_warnings,
                optimization_notes=optimization_notes,
                safety_considerations=safety_considerations
            )
            
        except Exception as e:
            logger.error(f"Error optimizing settings for {material_name}: {e}")
            return MachineSettingsResult(
                success=False,
                settings=None,
                validation_warnings=[f"Optimization failed: {e}"],
                optimization_notes=[],
                safety_considerations=[]
            )
    
    def _determine_optimal_wavelength(
        self,
        category: str,
        properties: Dict[str, Any],
        laser_type: Optional[LaserType]
    ) -> int:
        """Determine optimal laser wavelength for material"""
        
        if laser_type:
            return laser_type.value[1]
        
        baseline = self.category_settings.get(category, {})
        return baseline.get('primary_wavelength', 1064)
    
    def _calculate_power_requirements(
        self,
        category: str,
        properties: Dict[str, Any],
        mode: ProcessingMode,
        wavelength: int
    ) -> tuple:
        """Calculate power requirements based on material and mode"""
        
        baseline = self.category_settings[category]
        base_power = baseline['power_range']
        
        # Adjust for absorption at wavelength
        absorption = self.material_absorption.get(category, {}).get(wavelength, 0.5)
        
        # Lower absorption requires higher power
        power_factor = 1.0 / max(absorption, 0.1)
        
        min_power = int(base_power[0] * power_factor * 0.8)
        max_power = int(base_power[1] * power_factor * 1.2)
        
        # Adjust for processing mode
        if mode == ProcessingMode.CUTTING:
            min_power = int(min_power * 1.5)
            max_power = int(max_power * 2.0)
        elif mode == ProcessingMode.CLEANING:
            min_power = int(min_power * 0.5)
            max_power = int(max_power * 0.8)
        
        return (min_power, max_power)
    
    def _optimize_pulse_parameters(
        self,
        category: str,
        properties: Dict[str, Any],
        mode: ProcessingMode
    ) -> tuple:
        """Optimize pulse duration and repetition rate"""
        
        baseline = self.category_settings[category]
        
        pulse_duration = baseline['pulse_duration']
        rep_rate = baseline['repetition_rate']
        
        # Adjust for thermal properties if available
        thermal_conductivity = self._extract_thermal_conductivity(properties)
        if thermal_conductivity:
            if thermal_conductivity > 100:  # High TC materials (metals)
                pulse_duration = 'ns'  # Short pulses to minimize heat diffusion
                rep_rate = (rep_rate[0] * 2, rep_rate[1] * 2)
            elif thermal_conductivity < 1:  # Low TC materials (organics)
                pulse_duration = 'ms'  # Longer pulses for thermal processing
                rep_rate = (rep_rate[0] // 2, rep_rate[1] // 2)
        
        return pulse_duration, rep_rate
    
    def _calculate_fluence_and_spot(
        self,
        category: str,
        properties: Dict[str, Any],
        power_range: tuple
    ) -> tuple:
        """Calculate fluence threshold and optimal spot size"""
        
        baseline = self.category_settings[category]
        
        fluence_base = baseline['fluence_threshold']
        spot_base = baseline['spot_size']
        
        # Adjust based on material hardness or density
        density = self._extract_density(properties)
        if density:
            if density > 5.0:  # Dense materials need higher fluence
                fluence_factor = 1.5
                spot_factor = 0.8  # Smaller spots for higher power density
            elif density < 1.0:  # Light materials need lower fluence
                fluence_factor = 0.6
                spot_factor = 1.2  # Larger spots for gentler processing
            else:
                fluence_factor = 1.0
                spot_factor = 1.0
        else:
            fluence_factor = 1.0
            spot_factor = 1.0
        
        fluence_range = (
            fluence_base[0] * fluence_factor,
            fluence_base[1] * fluence_factor
        )
        
        spot_range = (
            int(spot_base[0] * spot_factor),
            int(spot_base[1] * spot_factor)
        )
        
        return fluence_range, spot_range
    
    def _calculate_processing_speed(
        self,
        category: str,
        properties: Dict[str, Any],
        power_range: tuple
    ) -> tuple:
        """Calculate optimal processing speed range"""
        
        baseline = self.category_settings[category]
        speed_base = baseline['processing_speed']
        
        # Higher power allows faster processing
        power_avg = (power_range[0] + power_range[1]) / 2
        baseline_power = (baseline['power_range'][0] + baseline['power_range'][1]) / 2
        
        speed_factor = power_avg / baseline_power
        
        return (
            int(speed_base[0] * speed_factor),
            int(speed_base[1] * speed_factor)
        )
    
    def _predict_processing_quality(
        self,
        category: str,
        properties: Dict[str, Any],
        power_range: tuple
    ) -> str:
        """Predict processing quality based on parameters"""
        
        baseline = self.category_settings[category]
        challenges = baseline.get('challenges', [])
        
        if len(challenges) > 3:
            return "Challenging - requires careful parameter optimization"
        elif len(challenges) > 1:
            return "Moderate - standard processing with some considerations"
        else:
            return "Good - straightforward processing expected"
    
    def _generate_optimization_notes(
        self,
        category: str,
        properties: Dict[str, Any],
        baseline: Dict[str, Any]
    ) -> List[str]:
        """Generate optimization notes for the operator"""
        
        notes = []
        
        challenges = baseline.get('challenges', [])
        focus = baseline.get('optimization_focus', '')
        
        notes.append(f"Primary optimization focus: {focus.replace('_', ' ')}")
        
        if challenges:
            notes.append(f"Key challenges: {', '.join(challenges)}")
        
        # Add material-specific notes
        thermal_conductivity = self._extract_thermal_conductivity(properties)
        if thermal_conductivity:
            if thermal_conductivity > 100:
                notes.append("High thermal conductivity - use short pulses to minimize heat spread")
            elif thermal_conductivity < 1:
                notes.append("Low thermal conductivity - monitor for heat accumulation")
        
        return notes
    
    def _determine_safety_level(self, category: str) -> str:
        """Determine safety classification level"""
        
        safety_levels = {
            'metal': 'Class 4 - High power laser with reflective surfaces',
            'ceramic': 'Class 4 - High power laser with particulate hazards',
            'wood': 'Class 4 - High power laser with fire hazard',
            'plastic': 'Class 4 - High power laser with toxic vapor hazard',
            'composite': 'Class 4 - High power laser with mixed hazards'
        }
        
        return safety_levels.get(category, 'Class 4 - High power laser system')
    
    def _validate_settings(self, settings: MachineSettings, category: str) -> List[str]:
        """Validate generated settings for safety and feasibility"""
        
        warnings = []
        
        # Check power range sanity
        if settings.power_range[1] > 1000:
            warnings.append("Very high power - ensure adequate cooling and safety measures")
        
        # Check fluence levels
        if settings.fluence_threshold[1] > 50:
            warnings.append("High fluence levels - risk of material damage")
        
        # Category-specific validation
        if category == 'wood' and settings.power_range[0] > 50:
            warnings.append("Power may be too high for wood - risk of burning")
        
        if category == 'plastic' and settings.power_range[0] > 30:
            warnings.append("Power may be too high for plastic - risk of melting")
        
        return warnings
    
    def _extract_thermal_conductivity(self, properties: Dict[str, Any]) -> Optional[float]:
        """Extract thermal conductivity value from properties"""
        try:
            tc_data = properties.get('thermalConductivity', properties.get('thermal_conductivity'))
            if tc_data:
                if isinstance(tc_data, dict):
                    value_str = str(tc_data.get('value', tc_data.get('default', '')))
                else:
                    value_str = str(tc_data)
                
                import re
                numbers = re.findall(r'(\d+\.?\d*)', value_str)
                if numbers:
                    return float(numbers[0])
        except Exception:
            pass
        return None
    
    def _extract_density(self, properties: Dict[str, Any]) -> Optional[float]:
        """Extract density value from properties"""
        try:
            density_data = properties.get('density')
            if density_data:
                if isinstance(density_data, dict):
                    value_str = str(density_data.get('value', density_data.get('default', '')))
                else:
                    value_str = str(density_data)
                
                import re
                numbers = re.findall(r'(\d+\.?\d*)', value_str)
                if numbers:
                    return float(numbers[0])
        except Exception:
            pass
        return None


if __name__ == "__main__":
    # Test machine settings optimization
    enhancer = MaterialMachineSettingsEnhancer()
    
    # Test with aluminum properties
    aluminum_props = {
        'density': {'value': '2.7 g/cm³'},
        'thermalConductivity': {'value': '167 W/m·K'},
        'reflectance': {'value': '92 %'}
    }
    
    result = enhancer.optimize_machine_settings(
        material_name='Aluminum 6061',
        material_category='metal',
        material_properties=aluminum_props,
        processing_mode=ProcessingMode.CLEANING
    )
    
    print("=== MACHINE SETTINGS OPTIMIZATION ===")
    print(f"Success: {result.success}")
    if result.settings:
        print(f"Power range: {result.settings.power_range} W")
        print(f"Wavelength: {result.settings.wavelength} nm")
        print(f"Pulse duration: {result.settings.pulse_duration}")
        print(f"Rep rate: {result.settings.repetition_rate} Hz")
        print(f"Quality prediction: {result.settings.quality_prediction}")
        print(f"Safety level: {result.settings.safety_level}")
    
    print(f"\nValidation warnings: {result.validation_warnings}")
    print(f"Optimization notes: {result.optimization_notes}")
    print(f"Safety considerations: {result.safety_considerations[:2]}")  # Show first 2