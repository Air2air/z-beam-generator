#!/usr/bin/env python3
"""
Qualitative Property Definitions

Defines all qualitative (categorical/non-numeric) properties,
their allowed values, categories, and validation rules.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class QualitativePropertyDefinition:
    """Definition of a qualitative property"""
    name: str
    category: str  # Subcategory within materialCharacteristics
    allowed_values: List[str]
    description: str
    unit: str
    default_value: Optional[str] = None


# Qualitative property definitions organized by category
QUALITATIVE_PROPERTIES: Dict[str, QualitativePropertyDefinition] = {
    
    # Thermal Behavior Properties
    'thermalDestructionType': QualitativePropertyDefinition(
        name='thermalDestructionType',
        category='thermal_behavior',
        allowed_values=['melting', 'decomposition', 'sublimation', 'vaporization', 'oxidation', 'charring', 'pyrolysis'],
        description='Primary mechanism by which material thermally degrades under laser energy',
        unit='type'
    ),
    'thermalStability': QualitativePropertyDefinition(
        name='thermalStability',
        category='thermal_behavior',
        allowed_values=['poor', 'fair', 'good', 'excellent'],
        description='Overall thermal stability classification',
        unit='rating'
    ),
    'heatTreatmentResponse': QualitativePropertyDefinition(
        name='heatTreatmentResponse',
        category='thermal_behavior',
        allowed_values=['hardenable', 'non-hardenable', 'age-hardenable', 'precipitation-hardenable'],
        description='Material response to heat treatment processes',
        unit='type'
    ),
    
    # Safety & Handling Properties
    'toxicity': QualitativePropertyDefinition(
        name='toxicity',
        category='safety_handling',
        allowed_values=['None', 'Low', 'Medium', 'High', 'Extreme'],
        description='Toxicity level for safety and handling considerations',
        unit='rating'
    ),
    'flammability': QualitativePropertyDefinition(
        name='flammability',
        category='safety_handling',
        allowed_values=['non-flammable', 'low', 'moderate', 'high', 'extremely-flammable'],
        description='Flammability classification',
        unit='rating'
    ),
    'reactivity': QualitativePropertyDefinition(
        name='reactivity',
        category='safety_handling',
        allowed_values=['stable', 'low', 'moderate', 'high', 'explosive'],
        description='Chemical reactivity classification',
        unit='rating'
    ),
    'corrosivityLevel': QualitativePropertyDefinition(
        name='corrosivityLevel',
        category='safety_handling',
        allowed_values=['non-corrosive', 'mildly-corrosive', 'corrosive', 'highly-corrosive'],
        description='Corrosivity level for handling and storage',
        unit='rating'
    ),
    
    # Physical Appearance Properties
    'color': QualitativePropertyDefinition(
        name='color',
        category='physical_appearance',
        allowed_values=['silver', 'gray', 'black', 'bronze', 'copper', 'gold', 'white', 'red', 'blue', 'green', 'yellow', 'brown', 'purple', 'orange'],
        description='Primary visual color of material in natural state',
        unit='color'
    ),
    'surfaceFinish': QualitativePropertyDefinition(
        name='surfaceFinish',
        category='physical_appearance',
        allowed_values=['polished', 'brushed', 'matte', 'rough', 'oxidized', 'textured', 'smooth'],
        description='Surface finish characteristic',
        unit='finish'
    ),
    'transparency': QualitativePropertyDefinition(
        name='transparency',
        category='physical_appearance',
        allowed_values=['opaque', 'translucent', 'transparent', 'semi-transparent'],
        description='Light transmission characteristic',
        unit='type'
    ),
    'luster': QualitativePropertyDefinition(
        name='luster',
        category='physical_appearance',
        allowed_values=['metallic', 'vitreous', 'resinous', 'pearly', 'silky', 'greasy', 'dull'],
        description='Surface luster or shine characteristic',
        unit='type'
    ),
    
    # Material Classification Properties
    'crystalStructure': QualitativePropertyDefinition(
        name='crystalStructure',
        category='material_classification',
        allowed_values=['FCC', 'BCC', 'HCP', 'amorphous', 'cubic', 'hexagonal', 'tetragonal', 'orthorhombic', 'monoclinic', 'triclinic'],
        description='Crystal lattice structure type',
        unit='structure'
    ),
    'microstructure': QualitativePropertyDefinition(
        name='microstructure',
        category='material_classification',
        allowed_values=['single-phase', 'multi-phase', 'composite', 'layered', 'cellular', 'porous'],
        description='Microscopic structural organization',
        unit='type'
    ),
    'processingMethod': QualitativePropertyDefinition(
        name='processingMethod',
        category='material_classification',
        allowed_values=['cast', 'forged', 'machined', 'sintered', 'additive', 'extruded', 'rolled', 'stamped', 'molded'],
        description='Primary manufacturing or processing method',
        unit='method'
    ),
    'grainSize': QualitativePropertyDefinition(
        name='grainSize',
        category='material_classification',
        allowed_values=['ultrafine', 'fine', 'medium', 'coarse', 'very-coarse'],
        description='Grain size classification',
        unit='classification'
    )
}


# Category definitions for materialCharacteristics
MATERIAL_CHARACTERISTICS_CATEGORIES = {
    'thermal_behavior': {
        'label': 'Thermal Behavior',
        'description': 'Qualitative thermal response and degradation characteristics'
    },
    'safety_handling': {
        'label': 'Safety & Handling',
        'description': 'Safety, toxicity, and handling characteristic ratings'
    },
    'physical_appearance': {
        'label': 'Physical Appearance',
        'description': 'Visual and surface appearance characteristics'
    },
    'material_classification': {
        'label': 'Material Classification',
        'description': 'Structural and processing classification attributes'
    }
}


def is_qualitative_property(property_name: str) -> bool:
    """Check if a property is qualitative (categorical)"""
    return property_name in QUALITATIVE_PROPERTIES


def get_property_definition(property_name: str) -> Optional[QualitativePropertyDefinition]:
    """Get the definition for a qualitative property"""
    return QUALITATIVE_PROPERTIES.get(property_name)


def validate_qualitative_value(property_name: str, value: str) -> bool:
    """Validate that a value is allowed for a qualitative property"""
    definition = get_property_definition(property_name)
    if not definition:
        return False
    return value in definition.allowed_values


def get_qualitative_properties_by_category(category: str) -> List[str]:
    """Get all qualitative property names for a given category"""
    return [
        name for name, defn in QUALITATIVE_PROPERTIES.items()
        if defn.category == category
    ]


def get_all_categories() -> List[str]:
    """Get all materialCharacteristics category names"""
    return list(MATERIAL_CHARACTERISTICS_CATEGORIES.keys())
