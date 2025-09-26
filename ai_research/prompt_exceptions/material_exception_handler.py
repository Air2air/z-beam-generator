#!/usr/bin/env python3
"""
AI Prompt Exception Handling System

Defines material-specific field handling rules and prompt modifications for AI generation.
Provides structured exception handling for different material categories like wood, ceramic, metal, etc.
"""

import yaml
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


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
    custom_range: Optional[tuple] = None
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


class AIPromptExceptionHandler:
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
            MaterialCategory.GLASS: self._create_glass_exceptions(),
            MaterialCategory.SEMICONDUCTOR: self._create_semiconductor_exceptions(),
            MaterialCategory.STONE: self._create_stone_exceptions(),
            MaterialCategory.MASONRY: self._create_masonry_exceptions()
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
                    property_name="youngsModulus",
                    behavior=PropertyBehavior.MODIFY_UNITS,
                    alternative_units="GPa",
                    custom_range=(5, 25),
                    custom_description="Elastic modulus parallel to grain",
                    validation_notes="Wood modulus varies dramatically with grain direction"
                ),
                PropertyException(
                    property_name="hardness",
                    behavior=PropertyBehavior.MODIFY_UNITS,
                    alternative_units="kN",
                    custom_description="Janka hardness test (force to embed 11.28mm steel ball)",
                    validation_notes="Wood hardness measured differently than metal hardness"
                ),
                PropertyException(
                    property_name="ablationThreshold",
                    behavior=PropertyBehavior.RANGE_LIMIT,
                    custom_range=(0.1, 5.0),
                    custom_description="Laser ablation threshold for wood (highly variable with species and moisture)",
                    validation_notes="Wood ablation depends heavily on moisture content and laser wavelength"
                )
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
                FieldModification(
                    field_name="safety_notes",
                    action="append",
                    content="Wood laser processing may produce smoke and organic vapors requiring ventilation"
                )
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
                PropertyException(
                    property_name="ablationThreshold",
                    behavior=PropertyBehavior.RANGE_LIMIT,
                    custom_range=(1.0, 50.0),
                    custom_description="Laser ablation threshold (ceramics typically require higher fluence)",
                    validation_notes="Ceramic ablation thresholds vary widely with composition"
                )
            ],
            field_modifications=[
                FieldModification(
                    field_name="mechanical_properties",
                    action="append",
                    content="Ceramics are brittle materials with high compressive but low tensile strength"
                ),
                FieldModification(
                    field_name="thermal_properties",
                    action="append",
                    content="Many ceramics are excellent thermal insulators with low thermal shock resistance"
                )
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
                PropertyException(
                    property_name="ablationThreshold",
                    behavior=PropertyBehavior.RANGE_LIMIT,
                    custom_range=(0.1, 20.0),
                    custom_description="Laser ablation threshold (varies with surface condition and alloy)",
                    validation_notes="Metal surface oxidation and roughness affect ablation threshold"
                )
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
                PropertyException(
                    property_name="youngsModulus",
                    behavior=PropertyBehavior.RANGE_LIMIT,
                    custom_range=(0.01, 50),
                    custom_description="Elastic modulus (highly temperature dependent)",
                    validation_notes="Plastic modulus varies significantly with temperature"
                )
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
                    content="Properties vary significantly with fiber orientation and loading direction"
                )
            ],
            prompt_additions=[
                "Composite materials are anisotropic - properties depend on fiber direction",
                "Matrix and fiber properties both contribute to overall behavior"
            ],
            validation_overrides={
                "anisotropic_properties": True,
                "fiber_direction_dependent": True
            }
        )
    
    def _create_glass_exceptions(self) -> MaterialExceptionRule:
        """Glass-specific exception handling"""
        return MaterialExceptionRule(
            category=MaterialCategory.GLASS,
            description="Glass materials are amorphous and have unique thermal properties",
            property_exceptions=[
                PropertyException(
                    property_name="meltingPoint",
                    behavior=PropertyBehavior.REPLACE,
                    replacement_property="softeningPoint",
                    custom_description="Glass softening point (glass doesn't have a sharp melting point)",
                    validation_notes="Glass transitions gradually from solid to liquid"
                )
            ],
            field_modifications=[],
            prompt_additions=[
                "Glass is an amorphous material without a sharp melting point",
                "Use softening point or glass transition temperature instead of melting point"
            ],
            validation_overrides={
                "allow_softening_point": True,
                "amorphous_material": True
            }
        )
    
    def _create_semiconductor_exceptions(self) -> MaterialExceptionRule:
        """Semiconductor-specific exception handling"""
        return MaterialExceptionRule(
            category=MaterialCategory.SEMICONDUCTOR,
            description="Semiconductor materials have temperature-dependent electrical properties",
            property_exceptions=[],
            field_modifications=[
                FieldModification(
                    field_name="electrical_properties",
                    action="append",
                    content="Electrical conductivity is highly temperature and purity dependent"
                )
            ],
            prompt_additions=[
                "Semiconductor properties are highly sensitive to temperature and impurities",
                "Electrical conductivity varies exponentially with temperature"
            ],
            validation_overrides={
                "temperature_sensitive": True
            }
        )
    
    def _create_stone_exceptions(self) -> MaterialExceptionRule:
        """Stone-specific exception handling"""
        return MaterialExceptionRule(
            category=MaterialCategory.STONE,
            description="Natural stone materials have variable composition",
            property_exceptions=[],
            field_modifications=[
                FieldModification(
                    field_name="composition_note",
                    action="append",
                    content="Natural stone composition varies with geological origin"
                )
            ],
            prompt_additions=[
                "Natural stone properties vary with geological origin and mineral composition"
            ],
            validation_overrides={
                "natural_variation_expected": True
            }
        )
    
    def _create_masonry_exceptions(self) -> MaterialExceptionRule:
        """Masonry-specific exception handling"""
        return MaterialExceptionRule(
            category=MaterialCategory.MASONRY,
            description="Masonry materials include fired clay products with porosity",
            property_exceptions=[
                PropertyException(
                    property_name="porosity",
                    behavior=PropertyBehavior.REQUIRED,
                    custom_description="Porosity significantly affects thermal and mechanical properties",
                    validation_notes="Masonry porosity is critical for laser processing"
                )
            ],
            field_modifications=[],
            prompt_additions=[
                "Masonry materials often have significant porosity affecting properties"
            ],
            validation_overrides={
                "porosity_consideration": True
            }
        )
    
    def apply_exceptions(self, material_category: str, base_prompt: str, material_data: Dict[str, Any]) -> str:
        """
        Apply material-specific exceptions to a base prompt
        
        Args:
            material_category: Category of material (metal, wood, ceramic, etc.)
            base_prompt: Original AI prompt
            material_data: Material property data
            
        Returns:
            Modified prompt with material-specific exceptions applied
        """
        try:
            category_enum = MaterialCategory(material_category.lower())
        except ValueError:
            # Unknown category - return base prompt unchanged
            return base_prompt
        
        if category_enum not in self.exception_rules:
            return base_prompt
        
        rule = self.exception_rules[category_enum]
        
        # Build exception-aware prompt
        modified_prompt = base_prompt
        
        # Add material-specific guidance
        if rule.prompt_additions:
            exception_guidance = "\n".join([
                "\n=== MATERIAL-SPECIFIC GUIDANCE ===",
                f"Material Category: {rule.category.value.upper()}",
                f"Special Considerations: {rule.description}",
                "",
                "IMPORTANT HANDLING RULES:"
            ] + [f"- {addition}" for addition in rule.prompt_additions])
            
            modified_prompt = exception_guidance + "\n\n" + modified_prompt
        
        # Add property-specific exceptions
        if rule.property_exceptions:
            property_guidance = self._generate_property_guidance(rule.property_exceptions)
            modified_prompt = modified_prompt + "\n\n" + property_guidance
        
        # Add validation overrides
        if rule.validation_overrides:
            validation_guidance = self._generate_validation_guidance(rule.validation_overrides)
            modified_prompt = modified_prompt + "\n\n" + validation_guidance
        
        return modified_prompt
    
    def _generate_property_guidance(self, exceptions: List[PropertyException]) -> str:
        """Generate property-specific guidance text"""
        guidance_lines = ["=== PROPERTY-SPECIFIC HANDLING ==="]
        
        for exception in exceptions:
            if exception.behavior == PropertyBehavior.REPLACE:
                guidance_lines.append(
                    f"- {exception.property_name}: REPLACE with '{exception.replacement_property}' "
                    f"({exception.custom_description})"
                )
            elif exception.behavior == PropertyBehavior.EXCLUDE:
                guidance_lines.append(
                    f"- {exception.property_name}: EXCLUDE from output "
                    f"({exception.validation_notes})"
                )
            elif exception.behavior == PropertyBehavior.MODIFY_UNITS:
                guidance_lines.append(
                    f"- {exception.property_name}: Use units '{exception.alternative_units}' "
                    f"({exception.custom_description})"
                )
            elif exception.behavior == PropertyBehavior.RANGE_LIMIT:
                guidance_lines.append(
                    f"- {exception.property_name}: Valid range {exception.custom_range} "
                    f"({exception.validation_notes})"
                )
            elif exception.behavior == PropertyBehavior.ALTERNATIVE:
                guidance_lines.append(
                    f"- {exception.property_name}: {exception.custom_description} "
                    f"({exception.validation_notes})"
                )
        
        return "\n".join(guidance_lines)
    
    def _generate_validation_guidance(self, overrides: Dict[str, Any]) -> str:
        """Generate validation override guidance"""
        guidance_lines = ["=== VALIDATION CONSIDERATIONS ==="]
        
        for key, value in overrides.items():
            if value:
                guidance_lines.append(f"- {key.replace('_', ' ').title()}: Required for this material type")
        
        return "\n".join(guidance_lines)
    
    def get_property_exceptions_for_material(self, material_category: str) -> List[PropertyException]:
        """Get property exceptions for a specific material category"""
        try:
            category_enum = MaterialCategory(material_category.lower())
            if category_enum in self.exception_rules:
                return self.exception_rules[category_enum].property_exceptions
        except ValueError:
            pass
        
        return []
    
    def validate_property_for_material(self, material_category: str, property_name: str, value: Any) -> tuple[bool, str]:
        """
        Validate a property value against material-specific rules
        
        Returns:
            (is_valid, validation_message)
        """
        exceptions = self.get_property_exceptions_for_material(material_category)
        
        for exception in exceptions:
            if exception.property_name == property_name:
                if exception.behavior == PropertyBehavior.EXCLUDE:
                    return False, f"Property '{property_name}' should be excluded for {material_category} materials"
                
                if exception.behavior == PropertyBehavior.RANGE_LIMIT and exception.custom_range:
                    try:
                        numeric_value = float(str(value).split()[0])  # Extract numeric part
                        min_val, max_val = exception.custom_range
                        if not (min_val <= numeric_value <= max_val):
                            return False, f"Value {numeric_value} outside valid range {exception.custom_range} for {material_category}"
                    except (ValueError, IndexError):
                        return False, f"Could not validate numeric range for {property_name}"
        
        return True, "Valid"


# Global instance for use throughout the system
exception_handler = AIPromptExceptionHandler()


def apply_material_exceptions(material_category: str, base_prompt: str, material_data: Dict[str, Any]) -> str:
    """
    Global function to apply material-specific exceptions to any AI prompt
    
    Args:
        material_category: Material category (metal, wood, ceramic, etc.)
        base_prompt: Original prompt template
        material_data: Material property data
        
    Returns:
        Modified prompt with material-specific handling applied
    """
    return exception_handler.apply_exceptions(material_category, base_prompt, material_data)


def validate_property_for_material_type(material_category: str, property_name: str, value: Any) -> tuple[bool, str]:
    """
    Global function to validate property values against material-specific rules
    
    Args:
        material_category: Material category
        property_name: Name of property to validate
        value: Property value to validate
        
    Returns:
        (is_valid, validation_message)
    """
    return exception_handler.validate_property_for_material(material_category, property_name, value)


if __name__ == "__main__":
    # Test the exception handling system
    handler = AIPromptExceptionHandler()
    
    # Test wood exceptions
    base_prompt = """
    Generate material properties for {material_name}.
    Include: density, melting point, thermal conductivity, tensile strength.
    """
    
    wood_prompt = handler.apply_exceptions("wood", base_prompt, {"name": "Oak"})
    print("=== WOOD EXCEPTION HANDLING TEST ===")
    print(wood_prompt)
    
    # Test property validation
    is_valid, message = handler.validate_property_for_material("wood", "density", "2.5 g/cm³")
    print(f"\nWood density validation: {is_valid} - {message}")
    
    # Test ceramic exceptions
    ceramic_prompt = handler.apply_exceptions("ceramic", base_prompt, {"name": "Alumina"})
    print("\n=== CERAMIC EXCEPTION HANDLING TEST ===")
    print(ceramic_prompt[:500] + "...")