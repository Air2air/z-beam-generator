#!/usr/bin/env python3
"""
Material Exception Handler - Organized Version

Defines material-specific field handling rules and prompt modifications for AI generation.
Provides structured exception handling for different material categories like wood, ceramic, metal, etc.

Migrated from ai_research/prompt_exceptions/material_exception_handler.py
"""

import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class MaterialCategory(Enum):
    """Material categories with specific handling requirements"""
    METAL = "metal"
    CERAMIC = "ceramic"
    WOOD = "wood"
    PLASTIC = "plastic"
    COMPOSITE = "composite"
    GLASS = "glass"
    SEMICONDUCTOR = "semiconductor"
    STONE = "stone"
    MASONRY = "masonry"


class PropertyBehavior(Enum):
    """How properties should be handled for specific materials"""
    REQUIRED = "required"          # Property must be present and valid
    OPTIONAL = "optional"          # Property may be present
    REPLACE = "replace"           # Replace with alternative property
    EXCLUDE = "exclude"           # Exclude property entirely
    MODIFY_UNITS = "modify_units" # Change units for this material
    RANGE_LIMIT = "range_limit"   # Apply specific range limits
    ALTERNATIVE = "alternative"   # Use alternative description/name


@dataclass
class PropertyException:
    """Exception rule for a specific property"""
    property_name: str
    behavior: PropertyBehavior
    replacement_property: Optional[str] = None
    alternative_units: Optional[str] = None
    custom_range: Optional[Tuple[float, float]] = None
    custom_description: Optional[str] = None
    priority_override: Optional[int] = None
    validation_notes: Optional[str] = None


@dataclass
class FieldModification:
    """Modification rule for AI prompt fields"""
    field_name: str
    action: str  # 'replace', 'append', 'prepend', 'modify', 'exclude'
    content: Optional[str] = None
    condition: Optional[str] = None


@dataclass
class MaterialExceptionRule:
    """Complete exception handling rule for a material category"""
    category: MaterialCategory
    description: str
    property_exceptions: List[PropertyException]
    field_modifications: List[FieldModification]
    prompt_additions: List[str]
    validation_overrides: Dict[str, Any]


class MaterialExceptionHandler:
    """Handles material-specific exceptions in AI prompt generation"""
    
    def __init__(self):
        self.exception_rules = self._initialize_exception_rules()
    
    def _initialize_exception_rules(self) -> Dict[MaterialCategory, MaterialExceptionRule]:
        """Initialize all material-specific exception rules"""
        return {
            MaterialCategory.WOOD: self._create_wood_exceptions(),
            MaterialCategory.CERAMIC: self._create_ceramic_exceptions(),
            MaterialCategory.METAL: self._create_metal_exceptions(),
            MaterialCategory.PLASTIC: self._create_plastic_exceptions(),
            MaterialCategory.COMPOSITE: self._create_composite_exceptions(),
        }
    
    def _create_wood_exceptions(self) -> MaterialExceptionRule:
        """Wood-specific exception handling"""
        return MaterialExceptionRule(
            category=MaterialCategory.WOOD,
            description="Wood materials require special handling for thermal properties and biological characteristics",
            property_exceptions=[
                PropertyException(
                    property_name="meltingPoint",
                    behavior=PropertyBehavior.REPLACE,
                    replacement_property="decompositionTemperature",
                    custom_description="Temperature at which wood begins to decompose (typically 200-500°C)",
                    validation_notes="Wood does not melt - it decomposes"
                ),
                PropertyException(
                    property_name="thermalConductivity",
                    behavior=PropertyBehavior.RANGE_LIMIT,
                    custom_range=(0.04, 0.4),
                    custom_description="Thermal conductivity of wood (perpendicular to grain)",
                    validation_notes="Wood thermal conductivity varies significantly with grain direction and moisture content"
                ),
                PropertyException(
                    property_name="density",
                    behavior=PropertyBehavior.RANGE_LIMIT,
                    custom_range=(0.16, 1.4),
                    custom_description="Wood density (dry basis)",
                    validation_notes="Density varies significantly between species and moisture content"
                ),
                PropertyException(
                    property_name="hardness",
                    behavior=PropertyBehavior.MODIFY_UNITS,
                    alternative_units="kN",
                    custom_description="Janka hardness test (force to embed 11.28mm steel ball)",
                    validation_notes="Wood hardness measured differently than metal hardness"
                ),
            ],
            field_modifications=[
                FieldModification(
                    field_name="material_characteristics",
                    action="append",
                    content="Wood is an anisotropic organic material with grain-dependent properties"
                ),
                FieldModification(
                    field_name="laser_considerations",
                    action="prepend",
                    content="CRITICAL: Wood moisture content significantly affects laser processing parameters"
                ),
            ],
            prompt_additions=[
                "Wood materials are anisotropic - properties vary with grain direction",
                "Moisture content significantly affects thermal and mechanical properties",
                "Wood decomposes rather than melts - use decomposition temperature instead of melting point",
                "Laser processing of wood requires special ventilation due to organic vapor production"
            ],
            validation_overrides={
                "allow_decomposition_temp": True,
                "require_grain_direction_notes": True,
                "moisture_content_consideration": True
            }
        )
    
    def _create_ceramic_exceptions(self) -> MaterialExceptionRule:
        """Ceramic-specific exception handling"""
        return MaterialExceptionRule(
            category=MaterialCategory.CERAMIC,
            description="Ceramic materials have high melting points and brittle behavior",
            property_exceptions=[
                PropertyException(
                    property_name="thermalConductivity",
                    behavior=PropertyBehavior.RANGE_LIMIT,
                    custom_range=(0.5, 200),
                    custom_description="Thermal conductivity (varies widely among ceramic types)",
                    validation_notes="Ceramic thermal conductivity ranges from insulators to highly conductive"
                ),
                PropertyException(
                    property_name="tensileStrength",
                    behavior=PropertyBehavior.ALTERNATIVE,
                    custom_description="Tensile strength (ceramics are much stronger in compression)",
                    validation_notes="Ceramics typically have low tensile but high compressive strength"
                ),
                PropertyException(
                    property_name="hardness",
                    behavior=PropertyBehavior.MODIFY_UNITS,
                    alternative_units="Mohs",
                    custom_description="Mohs hardness scale (more appropriate for ceramics)",
                    validation_notes="Mohs scale better represents ceramic hardness than metal scales"
                ),
            ],
            field_modifications=[
                FieldModification(
                    field_name="mechanical_properties",
                    action="append",
                    content="Ceramics are brittle materials with high compressive but low tensile strength"
                ),
            ],
            prompt_additions=[
                "Ceramics are brittle materials - emphasize compressive strength over tensile",
                "Thermal shock resistance is critical for ceramic laser processing",
                "Use Mohs hardness scale for ceramic materials when appropriate"
            ],
            validation_overrides={
                "allow_mohs_hardness": True,
                "emphasize_compressive_strength": True,
                "thermal_shock_consideration": True
            }
        )
    
    def _create_metal_exceptions(self) -> MaterialExceptionRule:
        """Metal-specific exception handling"""
        return MaterialExceptionRule(
            category=MaterialCategory.METAL,
            description="Metals have high thermal and electrical conductivity",
            property_exceptions=[
                PropertyException(
                    property_name="thermalConductivity",
                    behavior=PropertyBehavior.RANGE_LIMIT,
                    custom_range=(1, 500),
                    custom_description="Thermal conductivity (metals are generally good thermal conductors)",
                    validation_notes="Metal thermal conductivity typically much higher than non-metals"
                ),
                PropertyException(
                    property_name="reflectance",
                    behavior=PropertyBehavior.RANGE_LIMIT,
                    custom_range=(60, 98),
                    custom_description="Optical reflectance (metals are highly reflective at infrared wavelengths)",
                    validation_notes="Metal reflectance affects laser coupling efficiency"
                ),
            ],
            field_modifications=[
                FieldModification(
                    field_name="electrical_properties",
                    action="append",
                    content="Metals are excellent electrical conductors"
                ),
                FieldModification(
                    field_name="laser_considerations",
                    action="append",
                    content="High reflectance may require higher laser power for effective processing"
                )
            ],
            prompt_additions=[
                "Metals are excellent thermal and electrical conductors",
                "High reflectance at laser wavelengths affects processing efficiency",
                "Surface oxidation significantly impacts laser absorption"
            ],
            validation_overrides={
                "high_thermal_conductivity_expected": True,
                "high_reflectance_expected": True,
                "surface_condition_critical": True
            }
        )
    
    def _create_plastic_exceptions(self) -> MaterialExceptionRule:
        """Plastic-specific exception handling"""
        return MaterialExceptionRule(
            category=MaterialCategory.PLASTIC,
            description="Plastic materials have low melting points and may decompose",
            property_exceptions=[
                PropertyException(
                    property_name="meltingPoint",
                    behavior=PropertyBehavior.ALTERNATIVE,
                    custom_description="Glass transition or melting temperature (some plastics decompose before melting)",
                    validation_notes="Thermoset plastics decompose; thermoplastics melt"
                ),
                PropertyException(
                    property_name="thermalConductivity",
                    behavior=PropertyBehavior.RANGE_LIMIT,
                    custom_range=(0.1, 2.0),
                    custom_description="Thermal conductivity (plastics are generally thermal insulators)",
                    validation_notes="Most plastics have low thermal conductivity"
                ),
            ],
            field_modifications=[
                FieldModification(
                    field_name="thermal_behavior",
                    action="append",
                    content="Distinguish between thermoplastic (melts) and thermoset (decomposes) behavior"
                )
            ],
            prompt_additions=[
                "Distinguish between thermoplastic and thermoset behavior",
                "Plastic properties are highly temperature dependent",
                "Consider glass transition temperature for amorphous plastics"
            ],
            validation_overrides={
                "temperature_dependent_properties": True,
                "glass_transition_applicable": True
            }
        )
    
    def _create_composite_exceptions(self) -> MaterialExceptionRule:
        """Composite-specific exception handling"""
        return MaterialExceptionRule(
            category=MaterialCategory.COMPOSITE,
            description="Composite materials have direction-dependent properties",
            property_exceptions=[
                PropertyException(
                    property_name="thermalConductivity",
                    behavior=PropertyBehavior.ALTERNATIVE,
                    custom_description="Thermal conductivity (anisotropic - varies with fiber direction)",
                    validation_notes="Composite thermal properties depend on fiber orientation"
                ),
                PropertyException(
                    property_name="tensileStrength",
                    behavior=PropertyBehavior.ALTERNATIVE,
                    custom_description="Tensile strength parallel to fibers (much higher than perpendicular)",
                    validation_notes="Composite strength is highly directional"
                )
            ],
            field_modifications=[
                FieldModification(
                    field_name="anisotropy_note",
                    action="append",
                    content="Composite materials have direction-dependent properties"
                )
            ],
            prompt_additions=[
                "Composite properties are highly anisotropic and depend on fiber direction",
                "Consider both matrix and fiber contributions to overall properties"
            ],
            validation_overrides={
                "anisotropic_properties": True,
                "fiber_matrix_consideration": True
            }
        )


# Global exception handler instance
exception_handler = MaterialExceptionHandler()


def apply_material_exceptions(
    material_category: str, 
    base_prompt: str, 
    material_data: Dict[str, Any] = None
) -> str:
    """
    Apply material-specific exceptions to base prompt
    
    Args:
        material_category: Material category string
        base_prompt: Base prompt to modify
        material_data: Additional material data
        
    Returns:
        Modified prompt with material-specific exceptions applied
    """
    try:
        # Convert string to enum
        category_enum = MaterialCategory(material_category.lower())
        
        # Get exception rule for this category
        if category_enum not in exception_handler.exception_rules:
            logger.warning(f"No exception rules found for category: {material_category}")
            return base_prompt
        
        rule = exception_handler.exception_rules[category_enum]
        
        # Apply prompt additions
        modified_prompt = base_prompt
        if rule.prompt_additions:
            additions = "\n".join([f"- {addition}" for addition in rule.prompt_additions])
            modified_prompt += f"\n\n=== MATERIAL-SPECIFIC CONSIDERATIONS ===\n{additions}"
        
        # Apply field modifications (basic implementation)
        for modification in rule.field_modifications:
            if modification.action == "append" and modification.content:
                modified_prompt += f"\n\n{modification.field_name.upper()}: {modification.content}"
            elif modification.action == "prepend" and modification.content:
                modified_prompt = f"{modification.content}\n\n{modified_prompt}"
        
        return modified_prompt
        
    except ValueError:
        logger.warning(f"Unknown material category: {material_category}")
        return base_prompt
    except Exception as e:
        logger.error(f"Error applying material exceptions: {e}")
        return base_prompt


def validate_property_for_material_type(
    material_category: str, 
    property_name: str, 
    property_value: Any
) -> Tuple[bool, str]:
    """
    Validate a property value against material-specific rules
    
    Args:
        material_category: Material category string
        property_name: Name of the property
        property_value: Value to validate
        
    Returns:
        (is_valid, validation_message)
    """
    try:
        category_enum = MaterialCategory(material_category.lower())
        
        if category_enum not in exception_handler.exception_rules:
            return True, "No specific validation rules for this material category"
        
        rule = exception_handler.exception_rules[category_enum]
        
        # Find matching property exception
        for prop_exception in rule.property_exceptions:
            if prop_exception.property_name == property_name:
                
                if prop_exception.behavior == PropertyBehavior.EXCLUDE:
                    return False, f"Property {property_name} should not be used for {material_category}"
                
                if prop_exception.behavior == PropertyBehavior.REPLACE:
                    return False, f"Use {prop_exception.replacement_property} instead of {property_name} for {material_category}"
                
                if prop_exception.behavior == PropertyBehavior.RANGE_LIMIT and prop_exception.custom_range:
                    try:
                        # Extract numeric value from property_value
                        import re
                        value_str = str(property_value)
                        numeric_values = re.findall(r'(\d+\.?\d*)', value_str)
                        if numeric_values:
                            value = float(numeric_values[0])
                            min_val, max_val = prop_exception.custom_range
                            if not (min_val <= value <= max_val):
                                return False, f"{property_name} value {value} outside expected range {min_val}-{max_val} for {material_category}"
                    except (ValueError, TypeError):
                        return False, f"Could not validate {property_name} value for {material_category}"
        
        return True, "Property validation passed"
        
    except ValueError:
        return True, f"Unknown material category: {material_category}"
    except Exception as e:
        logger.error(f"Error validating property: {e}")
        return True, "Validation error - property accepted by default"


if __name__ == "__main__":
    # Test material exception handling
    
    # Test wood exceptions
    wood_prompt = "Generate properties for Oak."
    modified_wood_prompt = apply_material_exceptions("wood", wood_prompt)
    print("=== WOOD PROMPT MODIFICATIONS ===")
    print(modified_wood_prompt[:500] + "...")
    
    # Test property validation
    is_valid, message = validate_property_for_material_type("wood", "meltingPoint", "1500 °C")
    print(f"\nWood melting point validation: {is_valid} - {message}")
    
    is_valid, message = validate_property_for_material_type("wood", "density", "0.75 g/cm³")
    print(f"Wood density validation: {is_valid} - {message}")