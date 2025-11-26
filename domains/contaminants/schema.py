"""
Type-safe schema for contamination patterns with comprehensive validation.

This module provides Python dataclasses for structured contamination pattern data,
ensuring type safety and data validation throughout the Contaminants domain.

Architecture: Type-safe wrappers around Contaminants.yaml data
Policy Compliance: Fail-fast validation, zero hardcoded values, physics constraints
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum


class PropertyType(Enum):
    """Laser property classification."""
    OPTICAL = "optical"
    THERMAL = "thermal"
    REMOVAL = "removal"
    LAYER = "layer"
    PARAMETER = "parameter"
    SAFETY = "safety"
    SELECTIVITY = "selectivity"


class ResearchConfidence(Enum):
    """Confidence level for AI-researched values."""
    HIGH = "high"           # Multiple authoritative sources, consistent values
    MEDIUM = "medium"       # Single source or minor variations
    LOW = "low"            # Estimated or highly variable
    NEEDS_VERIFICATION = "needs_verification"  # Flagged for manual review


@dataclass
class LaserPropertyValue:
    """
    Generic container for laser property values with metadata.
    
    Supports ranges, uncertainties, wavelength-specific values, and research tracking.
    
    Examples:
        >>> # Single value
        >>> LaserPropertyValue(value=0.85, unit="dimensionless", wavelength="1064nm")
        
        >>> # Range
        >>> LaserPropertyValue(value=2.5, unit="J/cm²", min_value=0.5, max_value=5.0)
        
        >>> # With uncertainty
        >>> LaserPropertyValue(value=0.45, unit="dimensionless", uncertainty=0.05)
    """
    value: float
    unit: str
    wavelength: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    uncertainty: Optional[float] = None
    
    # Research metadata
    confidence: ResearchConfidence = ResearchConfidence.MEDIUM
    source: Optional[str] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Validate property value constraints."""
        if self.min_value is not None and self.max_value is not None:
            if self.min_value > self.max_value:
                raise ValueError(f"min_value ({self.min_value}) cannot exceed max_value ({self.max_value})")
            if not (self.min_value <= self.value <= self.max_value):
                raise ValueError(f"value ({self.value}) must be within range [{self.min_value}, {self.max_value}]")
        
        if self.uncertainty is not None:
            if self.uncertainty < 0:
                raise ValueError(f"uncertainty cannot be negative: {self.uncertainty}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        result = {
            'value': self.value,
            'unit': self.unit
        }
        
        if self.wavelength:
            result['wavelength'] = self.wavelength
        if self.min_value is not None:
            result['min_value'] = self.min_value
        if self.max_value is not None:
            result['max_value'] = self.max_value
        if self.uncertainty is not None:
            result['uncertainty'] = self.uncertainty
        if self.confidence != ResearchConfidence.MEDIUM:
            result['confidence'] = self.confidence.value
        if self.source:
            result['source'] = self.source
        if self.notes:
            result['notes'] = self.notes
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LaserPropertyValue':
        """Create from dictionary (YAML deserialization)."""
        confidence = data.get('confidence', 'medium')
        if isinstance(confidence, str):
            confidence = ResearchConfidence(confidence)
        
        return cls(
            value=data['value'],
            unit=data['unit'],
            wavelength=data.get('wavelength'),
            min_value=data.get('min_value'),
            max_value=data.get('max_value'),
            uncertainty=data.get('uncertainty'),
            confidence=confidence,
            source=data.get('source'),
            notes=data.get('notes')
        )


@dataclass
class OpticalProperties:
    """
    Optical properties at specific wavelengths.
    
    Physics constraint: absorption + reflection + transmission ≈ 1.0
    """
    wavelength: str  # e.g., "1064nm", "532nm", "355nm"
    absorption_coefficient: Optional[LaserPropertyValue] = None
    reflectivity: Optional[LaserPropertyValue] = None
    transmittance: Optional[LaserPropertyValue] = None
    refractive_index: Optional[LaserPropertyValue] = None
    scattering_coefficient: Optional[LaserPropertyValue] = None
    
    def validate_physics(self, tolerance: float = 0.05) -> Tuple[bool, Optional[str]]:
        """
        Validate physics constraint: absorption + reflection + transmission ≈ 1.0
        
        Args:
            tolerance: Acceptable deviation from 1.0 (default 5%)
        
        Returns:
            (is_valid, error_message) tuple
        """
        if not all([self.absorption_coefficient, self.reflectivity, self.transmittance]):
            return (True, None)  # Can't validate if values missing
        
        total = (self.absorption_coefficient.value + 
                 self.reflectivity.value + 
                 self.transmittance.value)
        
        deviation = abs(total - 1.0)
        if deviation > tolerance:
            return (False, f"Optical properties sum to {total:.3f}, expected ≈1.0 (deviation: {deviation:.3f})")
        
        return (True, None)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        result = {'wavelength': self.wavelength}
        
        if self.absorption_coefficient:
            result['absorption_coefficient'] = self.absorption_coefficient.to_dict()
        if self.reflectivity:
            result['reflectivity'] = self.reflectivity.to_dict()
        if self.transmittance:
            result['transmittance'] = self.transmittance.to_dict()
        if self.refractive_index:
            result['refractive_index'] = self.refractive_index.to_dict()
        if self.scattering_coefficient:
            result['scattering_coefficient'] = self.scattering_coefficient.to_dict()
        
        return result


@dataclass
class ThermalProperties:
    """Thermal behavior under laser irradiation."""
    ablation_threshold: Optional[LaserPropertyValue] = None
    vaporization_temperature: Optional[LaserPropertyValue] = None
    thermal_conductivity: Optional[LaserPropertyValue] = None
    heat_capacity: Optional[LaserPropertyValue] = None
    thermal_diffusivity: Optional[LaserPropertyValue] = None
    melting_point: Optional[LaserPropertyValue] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        result = {}
        
        if self.ablation_threshold:
            result['ablation_threshold'] = self.ablation_threshold.to_dict()
        if self.vaporization_temperature:
            result['vaporization_temperature'] = self.vaporization_temperature.to_dict()
        if self.thermal_conductivity:
            result['thermal_conductivity'] = self.thermal_conductivity.to_dict()
        if self.heat_capacity:
            result['heat_capacity'] = self.heat_capacity.to_dict()
        if self.thermal_diffusivity:
            result['thermal_diffusivity'] = self.thermal_diffusivity.to_dict()
        if self.melting_point:
            result['melting_point'] = self.melting_point.to_dict()
        
        return result


@dataclass
class RemovalCharacteristics:
    """Removal behavior and efficiency metrics."""
    removal_efficiency: Optional[LaserPropertyValue] = None
    removal_rate: Optional[LaserPropertyValue] = None
    damage_threshold_substrate: Optional[LaserPropertyValue] = None
    optimal_fluence_range: Optional[Tuple[float, float, str]] = None  # (min, max, unit)
    optimal_pulse_duration: Optional[LaserPropertyValue] = None
    surface_quality_post_removal: Optional[str] = None  # Description
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        result = {}
        
        if self.removal_efficiency:
            result['removal_efficiency'] = self.removal_efficiency.to_dict()
        if self.removal_rate:
            result['removal_rate'] = self.removal_rate.to_dict()
        if self.damage_threshold_substrate:
            result['damage_threshold_substrate'] = self.damage_threshold_substrate.to_dict()
        if self.optimal_fluence_range:
            result['optimal_fluence_range'] = {
                'min': self.optimal_fluence_range[0],
                'max': self.optimal_fluence_range[1],
                'unit': self.optimal_fluence_range[2]
            }
        if self.optimal_pulse_duration:
            result['optimal_pulse_duration'] = self.optimal_pulse_duration.to_dict()
        if self.surface_quality_post_removal:
            result['surface_quality_post_removal'] = self.surface_quality_post_removal
        
        return result


@dataclass
class LayerProperties:
    """Physical characteristics of contamination layer."""
    typical_thickness_range: Optional[Tuple[float, float, str]] = None  # (min, max, unit)
    layer_adhesion_strength: Optional[LaserPropertyValue] = None
    layer_porosity: Optional[LaserPropertyValue] = None
    layer_density: Optional[LaserPropertyValue] = None
    layer_uniformity: Optional[str] = None  # Description
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        result = {}
        
        if self.typical_thickness_range:
            result['typical_thickness_range'] = {
                'min': self.typical_thickness_range[0],
                'max': self.typical_thickness_range[1],
                'unit': self.typical_thickness_range[2]
            }
        if self.layer_adhesion_strength:
            result['layer_adhesion_strength'] = self.layer_adhesion_strength.to_dict()
        if self.layer_porosity:
            result['layer_porosity'] = self.layer_porosity.to_dict()
        if self.layer_density:
            result['layer_density'] = self.layer_density.to_dict()
        if self.layer_uniformity:
            result['layer_uniformity'] = self.layer_uniformity
        
        return result


@dataclass
class LaserParameters:
    """Recommended laser operating parameters."""
    wavelength_range: Optional[List[str]] = None  # e.g., ["1064nm", "532nm"]
    pulse_duration_range: Optional[Tuple[float, float, str]] = None  # (min, max, unit)
    repetition_rate_range: Optional[Tuple[float, float, str]] = None  # (min, max, unit)
    scan_speed_range: Optional[Tuple[float, float, str]] = None  # (min, max, unit)
    spot_size_recommendation: Optional[LaserPropertyValue] = None
    beam_profile: Optional[str] = None  # e.g., "Gaussian", "Top-hat"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        result = {}
        
        if self.wavelength_range:
            result['wavelength_range'] = self.wavelength_range
        if self.pulse_duration_range:
            result['pulse_duration_range'] = {
                'min': self.pulse_duration_range[0],
                'max': self.pulse_duration_range[1],
                'unit': self.pulse_duration_range[2]
            }
        if self.repetition_rate_range:
            result['repetition_rate_range'] = {
                'min': self.repetition_rate_range[0],
                'max': self.repetition_rate_range[1],
                'unit': self.repetition_rate_range[2]
            }
        if self.scan_speed_range:
            result['scan_speed_range'] = {
                'min': self.scan_speed_range[0],
                'max': self.scan_speed_range[1],
                'unit': self.scan_speed_range[2]
            }
        if self.spot_size_recommendation:
            result['spot_size_recommendation'] = self.spot_size_recommendation.to_dict()
        if self.beam_profile:
            result['beam_profile'] = self.beam_profile
        
        return result


@dataclass
class SafetyData:
    """Safety considerations and hazard information."""
    fume_composition: Optional[List[str]] = None
    toxicity_level: Optional[str] = None  # e.g., "Low", "Moderate", "High"
    required_ventilation: Optional[str] = None  # Description
    ppe_requirements: Optional[List[str]] = None
    environmental_impact: Optional[str] = None  # Description
    disposal_considerations: Optional[str] = None  # Description
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        result = {}
        
        if self.fume_composition:
            result['fume_composition'] = self.fume_composition
        if self.toxicity_level:
            result['toxicity_level'] = self.toxicity_level
        if self.required_ventilation:
            result['required_ventilation'] = self.required_ventilation
        if self.ppe_requirements:
            result['ppe_requirements'] = self.ppe_requirements
        if self.environmental_impact:
            result['environmental_impact'] = self.environmental_impact
        if self.disposal_considerations:
            result['disposal_considerations'] = self.disposal_considerations
        
        return result


@dataclass
class SelectivityRatios:
    """Selectivity between contamination and substrate materials."""
    contamination_substrate_absorption_ratio: Optional[LaserPropertyValue] = None
    contamination_substrate_ablation_threshold_ratio: Optional[LaserPropertyValue] = None
    selectivity_index: Optional[LaserPropertyValue] = None  # Higher = more selective
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        result = {}
        
        if self.contamination_substrate_absorption_ratio:
            result['contamination_substrate_absorption_ratio'] = self.contamination_substrate_absorption_ratio.to_dict()
        if self.contamination_substrate_ablation_threshold_ratio:
            result['contamination_substrate_ablation_threshold_ratio'] = self.contamination_substrate_ablation_threshold_ratio.to_dict()
        if self.selectivity_index:
            result['selectivity_index'] = self.selectivity_index.to_dict()
        
        return result


@dataclass
class ContaminationPattern:
    """
    Complete type-safe representation of a contamination pattern.
    
    Architecture:
    - Comprehensive validation on initialization
    - Physics constraint checking for optical properties
    - Research metadata tracking
    - YAML serialization/deserialization
    
    Usage:
        >>> pattern = ContaminationPattern(
        ...     pattern_id="rust_oxidation",
        ...     name="Rust / Iron Oxide Formation",
        ...     description="Iron oxide layers...",
        ...     composition=["Fe2O3", "Fe3O4"],
        ...     optical_properties_by_wavelength={
        ...         "1064nm": OpticalProperties(wavelength="1064nm", ...)
        ...     }
        ... )
        >>> is_valid, msg = pattern.validate()
        >>> if is_valid:
        ...     yaml_data = pattern.to_dict()
    """
    # Core identification
    pattern_id: str
    name: str
    description: str
    composition: List[str]
    
    # Material applicability
    valid_materials: List[str] = field(default_factory=list)
    prohibited_materials: List[str] = field(default_factory=list)
    
    # Laser properties (all optional - can be populated via research)
    optical_properties_by_wavelength: Dict[str, OpticalProperties] = field(default_factory=dict)
    thermal_properties: Optional[ThermalProperties] = None
    removal_characteristics: Optional[RemovalCharacteristics] = None
    layer_properties: Optional[LayerProperties] = None
    laser_parameters: Optional[LaserParameters] = None
    safety_data: Optional[SafetyData] = None
    selectivity_ratios: Optional[SelectivityRatios] = None
    
    # Research tracking
    research_timestamp: Optional[str] = None
    research_version: Optional[str] = None
    needs_verification: bool = False
    
    def __post_init__(self):
        """Validate pattern structure on initialization."""
        if not self.pattern_id:
            raise ValueError("pattern_id is required")
        if not self.name:
            raise ValueError("name is required")
        if not self.composition:
            raise ValueError("composition must contain at least one chemical formula")
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Comprehensive validation of pattern data.
        
        Returns:
            (is_valid, error_messages) tuple
        """
        errors = []
        
        # Validate optical properties physics constraints
        for wavelength, optical_props in self.optical_properties_by_wavelength.items():
            is_valid, error = optical_props.validate_physics()
            if not is_valid:
                errors.append(f"Optical properties at {wavelength}: {error}")
        
        # Check for research confidence flags
        if self.needs_verification:
            errors.append(f"Pattern {self.pattern_id} flagged for manual verification")
        
        # Validate ranges
        if self.layer_properties and self.layer_properties.typical_thickness_range:
            min_val, max_val, _ = self.layer_properties.typical_thickness_range
            if min_val > max_val:
                errors.append(f"Invalid thickness range: min ({min_val}) > max ({max_val})")
        
        return (len(errors) == 0, errors)
    
    def get_laser_property_coverage(self) -> Dict[str, bool]:
        """
        Report which laser property categories are populated.
        
        Returns:
            Dictionary mapping property type to presence boolean
        """
        return {
            'optical_properties': len(self.optical_properties_by_wavelength) > 0,
            'thermal_properties': self.thermal_properties is not None,
            'removal_characteristics': self.removal_characteristics is not None,
            'layer_properties': self.layer_properties is not None,
            'laser_parameters': self.laser_parameters is not None,
            'safety_data': self.safety_data is not None,
            'selectivity_ratios': self.selectivity_ratios is not None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for YAML serialization.
        
        Returns:
            Dictionary suitable for writing to Contaminants.yaml
        """
        result = {
            'name': self.name,
            'description': self.description,
            'composition': self.composition
        }
        
        if self.valid_materials:
            result['valid_materials'] = self.valid_materials
        if self.prohibited_materials:
            result['prohibited_materials'] = self.prohibited_materials
        
        # Laser properties
        if self.optical_properties_by_wavelength:
            result['optical_properties'] = {
                wavelength: props.to_dict()
                for wavelength, props in self.optical_properties_by_wavelength.items()
            }
        
        if self.thermal_properties:
            result['thermal_properties'] = self.thermal_properties.to_dict()
        
        if self.removal_characteristics:
            result['removal_characteristics'] = self.removal_characteristics.to_dict()
        
        if self.layer_properties:
            result['layer_properties'] = self.layer_properties.to_dict()
        
        if self.laser_parameters:
            result['laser_parameters'] = self.laser_parameters.to_dict()
        
        if self.safety_data:
            result['safety_data'] = self.safety_data.to_dict()
        
        if self.selectivity_ratios:
            result['selectivity_ratios'] = self.selectivity_ratios.to_dict()
        
        # Research metadata
        if self.research_timestamp:
            result['research_timestamp'] = self.research_timestamp
        if self.research_version:
            result['research_version'] = self.research_version
        if self.needs_verification:
            result['needs_verification'] = self.needs_verification
        
        return result
    
    @classmethod
    def from_dict(cls, pattern_id: str, data: Dict[str, Any]) -> 'ContaminationPattern':
        """
        Create ContaminationPattern from dictionary (YAML deserialization).
        
        Args:
            pattern_id: Pattern identifier (key in Contaminants.yaml)
            data: Pattern data dictionary
        
        Returns:
            ContaminationPattern instance
        """
        # Parse optical properties by wavelength
        optical_props = {}
        if 'optical_properties' in data:
            for wavelength, props_data in data['optical_properties'].items():
                optical_props[wavelength] = OpticalProperties(
                    wavelength=wavelength,
                    absorption_coefficient=LaserPropertyValue.from_dict(props_data['absorption_coefficient']) 
                        if 'absorption_coefficient' in props_data else None,
                    reflectivity=LaserPropertyValue.from_dict(props_data['reflectivity'])
                        if 'reflectivity' in props_data else None,
                    transmittance=LaserPropertyValue.from_dict(props_data['transmittance'])
                        if 'transmittance' in props_data else None,
                    refractive_index=LaserPropertyValue.from_dict(props_data['refractive_index'])
                        if 'refractive_index' in props_data else None,
                    scattering_coefficient=LaserPropertyValue.from_dict(props_data['scattering_coefficient'])
                        if 'scattering_coefficient' in props_data else None
                )
        
        # Parse thermal properties
        thermal = None
        if 'thermal_properties' in data:
            tp_data = data['thermal_properties']
            thermal = ThermalProperties(
                ablation_threshold=LaserPropertyValue.from_dict(tp_data['ablation_threshold'])
                    if 'ablation_threshold' in tp_data else None,
                vaporization_temperature=LaserPropertyValue.from_dict(tp_data['vaporization_temperature'])
                    if 'vaporization_temperature' in tp_data else None,
                thermal_conductivity=LaserPropertyValue.from_dict(tp_data['thermal_conductivity'])
                    if 'thermal_conductivity' in tp_data else None,
                heat_capacity=LaserPropertyValue.from_dict(tp_data['heat_capacity'])
                    if 'heat_capacity' in tp_data else None,
                thermal_diffusivity=LaserPropertyValue.from_dict(tp_data['thermal_diffusivity'])
                    if 'thermal_diffusivity' in tp_data else None,
                melting_point=LaserPropertyValue.from_dict(tp_data['melting_point'])
                    if 'melting_point' in tp_data else None
            )
        
        return cls(
            pattern_id=pattern_id,
            name=data['name'],
            description=data['description'],
            composition=data.get('composition', []),
            valid_materials=data.get('valid_materials', []),
            prohibited_materials=data.get('prohibited_materials', []),
            optical_properties_by_wavelength=optical_props,
            thermal_properties=thermal,
            # ... other properties can be added as needed
            research_timestamp=data.get('research_timestamp'),
            research_version=data.get('research_version'),
            needs_verification=data.get('needs_verification', False)
        )
