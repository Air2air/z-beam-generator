#!/usr/bin/env python3
"""
Comprehensive Data Quality Validation Agent

This agent systematically validates all properties, categories, and materials
for accuracy, completeness, and physical constraint violations.

Architecture:
1. Property-level validation (physical laws, units, ranges)
2. Category-level validation (taxonomy, range definitions)
3. Material-level validation (property relationships, completeness)
4. Cross-validation (inter-property constraints)

Based on methodology from recent fixes:
- Laser optical properties: Conservation of energy (A + R + T = 100%)
- Thermal diffusivity: Formula validation (α = k / (ρ × Cp))
- Electrical conductivity: Unit standardization
- Young's Modulus: Physical plausibility (E/TS ratios)
"""

import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict
import math

# ============================================================================
# VALIDATION RULES DATABASE
# ============================================================================

@dataclass
class PropertyRule:
    """Validation rules for a specific property"""
    property_name: str
    unit: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_units: List[str] = field(default_factory=list)
    category_specific_ranges: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    formula_dependencies: List[str] = field(default_factory=list)
    validation_function: Optional[str] = None
    physical_constraints: List[str] = field(default_factory=list)
    typical_values: Dict[str, float] = field(default_factory=dict)
    measurement_method: Optional[str] = None
    confidence_threshold: int = 70

@dataclass
class RelationshipRule:
    """Rules for relationships between properties"""
    name: str
    properties: List[str]
    relationship_type: str  # 'formula', 'ratio', 'sum', 'inverse'
    formula: Optional[str] = None
    expected_ratio_range: Optional[Tuple[float, float]] = None
    tolerance_percent: float = 20.0
    applies_to_categories: List[str] = field(default_factory=list)

@dataclass
class CategoryRule:
    """Validation rules for material categories"""
    category_name: str
    required_properties: List[str]
    optional_properties: List[str]
    forbidden_properties: List[str]
    typical_property_ranges: Dict[str, Tuple[float, float]]

# ============================================================================
# PROPERTY VALIDATION RULES
# ============================================================================

PROPERTY_RULES = {
    # Laser-Material Interaction Properties
    'laserAbsorption': PropertyRule(
        property_name='laserAbsorption',
        unit='%',
        min_value=0.0,
        max_value=100.0,
        allowed_units=['%'],
        category_specific_ranges={
            'metal': (2.0, 65.0),
            'ceramic': (10.0, 95.0),
            'stone': (5.0, 90.0),
            'wood': (25.0, 95.0),
            'plastic': (4.0, 95.0),
            'glass': (0.5, 10.0),
            'composite': (0.5, 95.0),
            'semiconductor': (30.0, 70.0),
            'masonry': (5.0, 90.0)
        },
        physical_constraints=[
            'Must sum with laserReflectivity to ≤100% (opaque materials)',
            'Higher for dark/rough surfaces, lower for polished/reflective surfaces'
        ],
        confidence_threshold=85
    ),
    
    'laserReflectivity': PropertyRule(
        property_name='laserReflectivity',
        unit='%',
        min_value=0.0,
        max_value=100.0,
        allowed_units=['%'],
        category_specific_ranges={
            'metal': (35.0, 98.0),
            'ceramic': (5.0, 90.0),
            'stone': (10.0, 95.0),
            'wood': (5.0, 75.0),
            'plastic': (4.0, 95.0),
            'glass': (3.0, 10.0),
            'composite': (4.0, 99.0),
            'semiconductor': (30.0, 70.0),
            'masonry': (10.0, 95.0)
        },
        physical_constraints=[
            'Must sum with laserAbsorption to ≤100% (opaque materials)',
            'Highly polished metals: 90-98%',
            'Rough surfaces: lower reflectivity'
        ],
        confidence_threshold=85
    ),
    
    # Thermal Properties
    'thermalConductivity': PropertyRule(
        property_name='thermalConductivity',
        unit='W/(m·K)',
        min_value=0.01,
        max_value=450.0,
        allowed_units=['W/(m·K)', 'W/m/K', 'W/mK'],
        category_specific_ranges={
            'metal': (15.0, 430.0),
            'ceramic': (1.0, 100.0),
            'stone': (0.5, 7.0),
            'wood': (0.1, 0.5),
            'plastic': (0.1, 0.5),
            'glass': (0.8, 1.4),
            'composite': (0.1, 200.0),
            'semiconductor': (1.0, 150.0),
            'masonry': (0.4, 2.0)
        },
        formula_dependencies=['thermalDiffusivity', 'density', 'specificHeat'],
        physical_constraints=[
            'Metals >> Non-metals',
            'Pure metals > Alloys',
            'Crystalline > Amorphous'
        ],
        typical_values={
            'copper': 401, 'aluminum': 237, 'steel': 50,
            'glass': 1.0, 'wood': 0.15, 'plastic': 0.2
        }
    ),
    
    'thermalDiffusivity': PropertyRule(
        property_name='thermalDiffusivity',
        unit='mm²/s',
        min_value=0.001,
        max_value=200.0,
        allowed_units=['mm²/s', 'mm2/s', 'm²/s', 'm2/s'],
        category_specific_ranges={
            'metal': (0.2, 174.0),
            'ceramic': (0.01, 50.0),
            'stone': (0.3, 5.0),
            'wood': (0.1, 0.5),
            'plastic': (0.08, 0.6),
            'glass': (0.3, 1.5),
            'composite': (0.06, 90.0),
            'semiconductor': (0.5, 100.0),
            'masonry': (0.2, 1.5)
        },
        formula_dependencies=['thermalConductivity', 'density', 'specificHeat'],
        validation_function='validate_thermal_diffusivity',
        physical_constraints=[
            'α = k / (ρ × Cp)',
            'Must be consistent with conductivity, density, and specific heat'
        ]
    ),
    
    'specificHeat': PropertyRule(
        property_name='specificHeat',
        unit='J/(kg·K)',
        min_value=100.0,
        max_value=5000.0,
        allowed_units=['J/(kg·K)', 'J/kg/K', 'J/kgK', 'kJ/(kg·K)'],
        category_specific_ranges={
            'metal': (100.0, 900.0),
            'ceramic': (400.0, 1500.0),
            'stone': (700.0, 2000.0),
            'wood': (1200.0, 2500.0),
            'plastic': (900.0, 2500.0),
            'glass': (500.0, 1000.0),
            'composite': (800.0, 2000.0),
            'semiconductor': (300.0, 900.0),
            'masonry': (800.0, 1100.0)
        },
        formula_dependencies=['thermalDiffusivity', 'thermalConductivity', 'density'],
        physical_constraints=[
            'Water has highest: ~4186 J/(kg·K)',
            'Metals typically: 200-900 J/(kg·K)',
            'Polymers typically: 1000-2500 J/(kg·K)'
        ]
    ),
    
    'thermalExpansion': PropertyRule(
        property_name='thermalExpansion',
        unit='10⁻⁶/K',
        min_value=0.1,
        max_value=200.0,
        allowed_units=['10⁻⁶/K', '10^-6/K', 'μm/m/K', 'ppm/K'],
        category_specific_ranges={
            'metal': (0.5, 33.0),
            'ceramic': (0.5, 15.0),
            'stone': (3.0, 15.0),
            'wood': (3.0, 35.0),
            'plastic': (20.0, 200.0),
            'glass': (0.5, 9.0),
            'composite': (1.0, 80.0),
            'semiconductor': (2.0, 7.0),
            'masonry': (4.0, 14.0)
        },
        physical_constraints=[
            'Plastics > Metals > Ceramics',
            'Amorphous > Crystalline',
            'Low thermal expansion critical for dimensional stability'
        ]
    ),
    
    # Mechanical Properties
    'density': PropertyRule(
        property_name='density',
        unit='g/cm³',
        min_value=0.01,
        max_value=25.0,
        allowed_units=['g/cm³', 'g/cm3', 'kg/m³', 'kg/m3'],
        category_specific_ranges={
            'metal': (0.53, 22.6),
            'ceramic': (1.8, 10.0),
            'stone': (1.5, 3.5),
            'wood': (0.3, 1.2),
            'plastic': (0.8, 2.3),
            'glass': (2.2, 6.0),
            'composite': (0.5, 8.0),
            'semiconductor': (2.3, 6.0),
            'masonry': (1.6, 2.4)
        },
        formula_dependencies=['thermalDiffusivity', 'thermalConductivity', 'specificHeat'],
        physical_constraints=[
            'Osmium highest: 22.6 g/cm³',
            'Aerogels lowest: ~0.001 g/cm³',
            'Water reference: 1.0 g/cm³'
        ],
        typical_values={
            'steel': 7.85, 'aluminum': 2.70, 'copper': 8.96,
            'glass': 2.5, 'wood': 0.6, 'plastic': 1.2
        }
    ),
    
    'youngsModulus': PropertyRule(
        property_name='youngsModulus',
        unit='GPa',
        min_value=0.001,
        max_value=1200.0,
        allowed_units=['GPa', 'MPa', 'Pa'],
        category_specific_ranges={
            'metal': (10.0, 600.0),
            'ceramic': (50.0, 600.0),
            'stone': (5.0, 120.0),
            'wood': (3.0, 25.0),
            'plastic': (0.01, 10.0),
            'glass': (50.0, 90.0),
            'composite': (5.0, 500.0),
            'semiconductor': (100.0, 200.0),
            'masonry': (3.0, 45.0)
        },
        formula_dependencies=['tensileStrength'],
        validation_function='validate_youngs_modulus_ratio',
        physical_constraints=[
            'Diamond highest: ~1200 GPa',
            'Rubbers lowest: ~0.001 GPa',
            'E/TS ratio typically 100-300 for metals',
            'E/TS ratio typically 50-500 for other materials'
        ],
        typical_values={
            'steel': 200, 'aluminum': 69, 'copper': 110,
            'glass': 70, 'wood': 12, 'polycarbonate': 2.3
        }
    ),
    
    'tensileStrength': PropertyRule(
        property_name='tensileStrength',
        unit='MPa',
        min_value=0.1,
        max_value=8000.0,  # Increased for single-crystal silicon (up to 7 GPa)
        allowed_units=['MPa', 'GPa', 'Pa', 'psi'],
        category_specific_ranges={
            'metal': (3.0, 3000.0),
            'ceramic': (2.0, 1000.0),
            'stone': (1.0, 30.0),
            'wood': (20.0, 200.0),
            'plastic': (10.0, 250.0),
            'glass': (30.0, 2000.0),
            'composite': (50.0, 3500.0),
            'semiconductor': (100.0, 400.0),
            'masonry': (0.5, 20.0)
        },
        formula_dependencies=['youngsModulus'],
        physical_constraints=[
            'Carbon fiber highest: ~7000 MPa',
            'Foam lowest: ~0.1 MPa',
            'TS = E / (100 to 300) typical for metals'
        ]
    ),
    
    'hardness': PropertyRule(
        property_name='hardness',
        unit='varies',  # Multi-scale property
        min_value=0.1,
        max_value=10000.0,
        allowed_units=['Mohs', 'HV', 'HRC', 'HRB', 'HRA', 'GPa', 'MPa', 'Shore A', 'Shore D', 'HRM', 'Brinell'],
        category_specific_ranges={
            'metal': (20.0, 3500.0),  # HV or MPa
            'ceramic': (5.0, 10.0),  # Mohs or 1000+ HV
            'stone': (1.0, 8.0),  # Mohs
            'wood': (1.0, 6.0),  # Mohs or Shore D
            'plastic': (20.0, 100.0),  # Shore A/D
            'glass': (5.0, 7.0),  # Mohs
            'composite': (10.0, 1000.0),  # Various
            'semiconductor': (6.0, 9.5),  # Mohs
            'masonry': (2.0, 7.0)  # Mohs
        },
        physical_constraints=[
            'Multi-scale property: different scales for different materials',
            'Mohs scale: 1-10 (minerals)',
            'Vickers (HV): metals and hard materials',
            'Shore A/D: polymers and elastomers',
            'Documented in HARDNESS_MULTI_SCALE_DOCUMENTATION.md'
        ],
        measurement_method='material_dependent'
    ),
    
    # Electrical Properties
    'electricalConductivity': PropertyRule(
        property_name='electricalConductivity',
        unit='MS/m',
        min_value=0.000001,
        max_value=70.0,
        allowed_units=['MS/m', 'S/m', '×10⁷ S/m', '% IACS'],
        category_specific_ranges={
            'metal': (4.8, 63.0),  # MS/m
            'ceramic': (0.00001, 100.0),  # Varies widely
            'semiconductor': (0.001, 50.0),
            'plastic': (0.0, 0.001)  # Mostly insulators
        },
        physical_constraints=[
            'Silver highest: 63 MS/m',
            'σ × ρ = 1 (conductivity × resistivity)',
            '100% IACS = 58.1 MS/m (copper standard)'
        ],
        typical_values={
            'silver': 63.0, 'copper': 59.6, 'aluminum': 37.7,
            'steel': 10.0, 'stainless_steel': 1.4
        }
    ),
    
    'electricalResistivity': PropertyRule(
        property_name='electricalResistivity',
        unit='Ω·m',
        min_value=0.000000015,
        max_value=1e16,
        allowed_units=['Ω·m', 'ohm·m', 'Ω⋅m'],
        category_specific_ranges={
            'metal': (0.000000015, 0.00001),
            'semiconductor': (0.001, 1000.0),
            'ceramic': (1e-6, 1e14)
        },
        physical_constraints=[
            'σ × ρ = 1 (conductivity × resistivity)',
            'Inverse relationship with conductivity'
        ]
    ),
    
    # Environmental/Chemical Properties
    'oxidationResistance': PropertyRule(
        property_name='oxidationResistance',
        unit='°C',
        min_value=20.0,
        max_value=1600.0,
        allowed_units=['°C', 'C', 'K'],
        category_specific_ranges={
            'metal': (200.0, 1200.0),
            'ceramic': (1000.0, 1600.0),
            'composite': (200.0, 800.0)
        },
        physical_constraints=[
            'Steel: 200-400°C',
            'Stainless steel: 400-800°C',
            'Nickel alloys: 800-1200°C',
            'Ceramics: >1000°C'
        ],
        typical_values={
            'steel': 300, 'stainless_steel': 650, 'inconel': 1000,
            'alumina': 1400
        }
    ),
    
    'corrosionResistance': PropertyRule(
        property_name='corrosionResistance',
        unit='qualitative',
        allowed_units=['qualitative', 'rating'],
        min_value=None,  # No numeric validation for qualitative properties
        max_value=None,
        physical_constraints=[
            'Excellent > Good > Fair > Poor',
            'Material and environment specific'
        ]
    ),
}

# Properties that should not be validated as numeric
QUALITATIVE_ONLY_PROPERTIES = {'corrosionResistance'}

# ============================================================================
# RELATIONSHIP VALIDATION RULES
# ============================================================================

RELATIONSHIP_RULES = [
    RelationshipRule(
        name='optical_energy_conservation',
        properties=['laserAbsorption', 'laserReflectivity'],
        relationship_type='sum',
        formula='A + R ≤ 100',
        expected_ratio_range=(80.0, 105.0),
        tolerance_percent=5.0,
        applies_to_categories=['metal', 'ceramic', 'stone', 'wood', 'composite', 'masonry']
    ),
    
    RelationshipRule(
        name='thermal_diffusivity_formula',
        properties=['thermalDiffusivity', 'thermalConductivity', 'density', 'specificHeat'],
        relationship_type='formula',
        formula='α = k / (ρ × Cp) × 10^6',
        tolerance_percent=20.0,
        applies_to_categories=['metal', 'ceramic', 'stone', 'wood', 'plastic', 'glass', 'composite', 'semiconductor', 'masonry']
    ),
    
    RelationshipRule(
        name='youngs_tensile_ratio',
        properties=['youngsModulus', 'tensileStrength'],
        relationship_type='ratio',
        formula='E/TS',
        expected_ratio_range=(50.0, 500.0),  # Default range
        tolerance_percent=30.0,
        applies_to_categories=['metal', 'ceramic', 'stone', 'wood', 'plastic', 'glass', 'composite', 'semiconductor', 'masonry']
    ),
    
    RelationshipRule(
        name='electrical_conductivity_resistivity',
        properties=['electricalConductivity', 'electricalResistivity'],
        relationship_type='inverse',
        formula='σ × ρ = 1',
        tolerance_percent=10.0,
        applies_to_categories=['metal', 'semiconductor']
    ),
]

# ============================================================================
# CATEGORY VALIDATION RULES
# ============================================================================

CATEGORY_RULES = {
    'metal': CategoryRule(
        category_name='metal',
        required_properties=[
            'laserAbsorption', 'laserReflectivity', 'thermalConductivity',
            'specificHeat', 'density', 'youngsModulus', 'tensileStrength', 'hardness',
            'thermalDiffusivity', 'thermalExpansion',  # Critical for laser processing
            'oxidationResistance', 'corrosionResistance'  # Critical for material behavior
        ],
        optional_properties=[
            'electricalConductivity', 'fractureToughness', 'surfaceRoughness',
            'porosity'  # Optional for solid metals
        ],
        forbidden_properties=[
            'waterSolubility', 'decompositionTemperature', 'glassTransition'
        ],
        typical_property_ranges={
            'laserAbsorption': (2.0, 65.0),
            'laserReflectivity': (35.0, 98.0),
            'thermalConductivity': (15.0, 430.0),
            'density': (0.53, 22.6),
            'youngsModulus': (10.0, 600.0)
        }
    ),
    
    'ceramic': CategoryRule(
        category_name='ceramic',
        required_properties=[
            'laserAbsorption', 'laserReflectivity', 'thermalConductivity',
            'specificHeat', 'density', 'hardness'
        ],
        optional_properties=[
            'thermalDiffusivity', 'thermalExpansion', 'youngsModulus',
            'tensileStrength', 'oxidationResistance'
        ],
        forbidden_properties=[
            'waterSolubility', 'decompositionTemperature', 'glassTransition',
            'electricalConductivity'
        ],
        typical_property_ranges={
            'laserAbsorption': (10.0, 95.0),
            'laserReflectivity': (5.0, 90.0),
            'thermalConductivity': (1.0, 100.0),
            'density': (1.8, 10.0),
            'hardness': (5.0, 10.0)  # Mohs
        }
    ),
    
    'wood': CategoryRule(
        category_name='wood',
        required_properties=[
            'laserAbsorption', 'laserReflectivity', 'thermalConductivity',
            'specificHeat', 'density'
        ],
        optional_properties=[
            'thermalDiffusivity', 'thermalExpansion', 'youngsModulus',
            'tensileStrength', 'hardness', 'moistureContent'
        ],
        forbidden_properties=[
            'electricalConductivity', 'electricalResistivity',
            'oxidationResistance', 'decompositionTemperature', 'glassTransition'
        ],
        typical_property_ranges={
            'laserAbsorption': (25.0, 95.0),
            'laserReflectivity': (5.0, 75.0),
            'thermalConductivity': (0.1, 0.5),
            'density': (0.3, 1.2),
            'youngsModulus': (3.0, 25.0)  # NOT 2500!
        }
    ),
    
    'plastic': CategoryRule(
        category_name='plastic',
        required_properties=[
            'laserAbsorption', 'laserReflectivity', 'thermalConductivity',
            'specificHeat', 'density'
        ],
        optional_properties=[
            'thermalDiffusivity', 'thermalExpansion', 'youngsModulus',
            'tensileStrength', 'hardness', 'glassTrans ition', 'decompositionTemperature'
        ],
        forbidden_properties=[
            'electricalConductivity', 'oxidationResistance'
        ],
        typical_property_ranges={
            'laserAbsorption': (4.0, 95.0),
            'laserReflectivity': (4.0, 95.0),
            'thermalConductivity': (0.1, 0.5),
            'density': (0.8, 2.3),
            'thermalExpansion': (20.0, 200.0)
        }
    ),
    
    'stone': CategoryRule(
        category_name='stone',
        required_properties=[
            'laserAbsorption', 'laserReflectivity', 'thermalConductivity',
            'specificHeat', 'density', 'hardness'
        ],
        optional_properties=[
            'thermalDiffusivity', 'thermalExpansion', 'youngsModulus',
            'tensileStrength', 'waterSolubility'
        ],
        forbidden_properties=[
            'electricalConductivity', 'oxidationResistance',
            'decompositionTemperature', 'glassTransition'
        ],
        typical_property_ranges={
            'laserAbsorption': (5.0, 90.0),
            'laserReflectivity': (10.0, 95.0),
            'thermalConductivity': (0.5, 7.0),
            'density': (1.5, 3.5),
            'hardness': (1.0, 8.0)  # Mohs
        }
    ),
}

# ============================================================================
# VALIDATION AGENT CLASS
# ============================================================================

class DataQualityValidationAgent:
    """
    Comprehensive validation agent for material properties database.
    
    Validates at three levels:
    1. Property level: Individual property constraints
    2. Relationship level: Inter-property formulas and ratios
    3. Category level: Material taxonomy and completeness
    """
    
    def __init__(self, data_dir: Path = Path(".")):
        self.data_dir = data_dir
        self.frontmatter_dir = data_dir / "content" / "components" / "frontmatter"
        self.categories_file = data_dir / "data" / "Categories.yaml"
        
        self.violations = defaultdict(list)
        self.warnings = defaultdict(list)
        self.info = defaultdict(list)
        
    def load_categories(self) -> Dict:
        """Load Categories.yaml"""
        with open(self.categories_file) as f:
            return yaml.safe_load(f)
    
    def load_material(self, file_path: Path) -> Dict:
        """Load individual material frontmatter file"""
        with open(file_path) as f:
            return yaml.safe_load(f)
    
    # ========================================================================
    # LEVEL 1: PROPERTY VALIDATION
    # ========================================================================
    
    def validate_property_value(self, material: str, category: str, 
                               prop_name: str, prop_data: Dict) -> List[Dict]:
        """Validate individual property value against rules"""
        issues = []
        
        if prop_name not in PROPERTY_RULES:
            return issues  # No rules defined for this property
        
        rule = PROPERTY_RULES[prop_name]
        value = prop_data.get('value')
        unit = prop_data.get('unit', '')
        confidence = prop_data.get('confidence', 100)
        
        if value is None:
            return issues
        
        # Skip numeric validation for qualitative-only properties
        if prop_name in QUALITATIVE_ONLY_PROPERTIES:
            if unit not in rule.allowed_units:
                issues.append({
                    'severity': 'WARNING',
                    'type': 'invalid_unit',
                    'material': material,
                    'property': prop_name,
                    'unit': unit,
                    'expected_units': rule.allowed_units,
                    'message': f"Unit should be qualitative for {prop_name}"
                })
            return issues
        
        try:
            val = float(value)
            
            # Check unit
            if rule.allowed_units and unit not in rule.allowed_units:
                issues.append({
                    'severity': 'ERROR',
                    'type': 'invalid_unit',
                    'material': material,
                    'property': prop_name,
                    'value': value,
                    'unit': unit,
                    'expected_units': rule.allowed_units,
                    'message': f"Invalid unit '{unit}' for {prop_name}. Expected: {rule.allowed_units}"
                })
            
            # Check global range
            if rule.min_value is not None and val < rule.min_value:
                issues.append({
                    'severity': 'ERROR',
                    'type': 'out_of_range',
                    'material': material,
                    'property': prop_name,
                    'value': val,
                    'min': rule.min_value,
                    'message': f"{prop_name} = {val} < {rule.min_value} (global min)"
                })
            
            if rule.max_value is not None and val > rule.max_value:
                issues.append({
                    'severity': 'ERROR',
                    'type': 'out_of_range',
                    'material': material,
                    'property': prop_name,
                    'value': val,
                    'max': rule.max_value,
                    'message': f"{prop_name} = {val} > {rule.max_value} (global max)"
                })
            
            # Check category-specific range
            if category in rule.category_specific_ranges:
                cat_min, cat_max = rule.category_specific_ranges[category]
                if val < cat_min or val > cat_max:
                    issues.append({
                        'severity': 'WARNING',
                        'type': 'category_range_violation',
                        'material': material,
                        'category': category,
                        'property': prop_name,
                        'value': val,
                        'expected_range': (cat_min, cat_max),
                        'message': f"{prop_name} = {val} outside typical {category} range [{cat_min}, {cat_max}]"
                    })
            
            # Check confidence
            if confidence < rule.confidence_threshold:
                issues.append({
                    'severity': 'INFO',
                    'type': 'low_confidence',
                    'material': material,
                    'property': prop_name,
                    'confidence': confidence,
                    'threshold': rule.confidence_threshold,
                    'message': f"{prop_name} confidence {confidence}% < {rule.confidence_threshold}%"
                })
            
        except (ValueError, TypeError) as e:
            issues.append({
                'severity': 'ERROR',
                'type': 'invalid_value',
                'material': material,
                'property': prop_name,
                'value': value,
                'message': f"Cannot convert {prop_name} value to float: {value}"
            })
        
        return issues
    
    # ========================================================================
    # LEVEL 2: RELATIONSHIP VALIDATION
    # ========================================================================
    
    def validate_optical_energy_conservation(self, material: str, category: str, 
                                            props: Dict) -> List[Dict]:
        """Validate A + R ≤ 100% (conservation of energy)"""
        issues = []
        
        absorption = props.get('laserAbsorption', {}).get('value')
        reflectivity = props.get('laserReflectivity', {}).get('value')
        
        if absorption is None or reflectivity is None:
            return issues
        
        A = float(absorption)
        R = float(reflectivity)
        total = A + R
        
        # For opaque materials (most categories), should sum to ~100%
        if category in ['metal', 'ceramic', 'stone', 'wood', 'composite', 'masonry']:
            if total < 80:
                issues.append({
                    'severity': 'WARNING',
                    'type': 'optical_sum_low',
                    'material': material,
                    'category': category,
                    'absorption': A,
                    'reflectivity': R,
                    'sum': total,
                    'message': f"A + R = {total:.1f}% < 80% (may have transmittance)"
                })
            elif total > 105:
                issues.append({
                    'severity': 'ERROR',
                    'type': 'optical_sum_high',
                    'material': material,
                    'category': category,
                    'absorption': A,
                    'reflectivity': R,
                    'sum': total,
                    'message': f"A + R = {total:.1f}% > 105% (violates conservation of energy!)"
                })
        
        return issues
    
    def validate_thermal_diffusivity_formula(self, material: str, category: str,
                                            laser_props: Dict, char_props: Dict) -> List[Dict]:
        """Validate α = k / (ρ × Cp)"""
        issues = []
        
        alpha = laser_props.get('thermalDiffusivity', {}).get('value')
        k = laser_props.get('thermalConductivity', {}).get('value')
        cp = laser_props.get('specificHeat', {}).get('value')
        rho = char_props.get('density', {}).get('value')
        
        if any(v is None for v in [alpha, k, cp, rho]):
            return issues
        
        alpha_measured = float(alpha)
        k_val = float(k)
        cp_val = float(cp)
        rho_val = float(rho) * 1000  # g/cm³ to kg/m³
        
        # Calculate expected: α = k / (ρ × Cp) × 10^6 (mm²/s)
        alpha_calculated = (k_val / (rho_val * cp_val)) * 1e6
        
        error_percent = abs(alpha_calculated - alpha_measured) / alpha_calculated * 100
        
        if error_percent > 20:
            issues.append({
                'severity': 'ERROR',
                'type': 'formula_violation',
                'material': material,
                'category': category,
                'property': 'thermalDiffusivity',
                'measured': alpha_measured,
                'calculated': alpha_calculated,
                'error_percent': error_percent,
                'formula': 'α = k / (ρ × Cp)',
                'k': k_val,
                'rho': rho_val,
                'cp': cp_val,
                'message': f"α measured {alpha_measured:.2f} vs calculated {alpha_calculated:.2f} mm²/s ({error_percent:.1f}% error)"
            })
        
        return issues
    
    def validate_youngs_tensile_ratio(self, material: str, category: str,
                                      props: Dict) -> List[Dict]:
        """Validate E/TS ratio is physically reasonable with category-specific thresholds"""
        issues = []
        
        E = props.get('youngsModulus', {}).get('value')
        TS = props.get('tensileStrength', {}).get('value')
        
        if E is None or TS is None:
            return issues
        
        E_val = float(E)  # GPa
        TS_val = float(TS)  # MPa
        
        E_MPa = E_val * 1000
        ratio = E_MPa / TS_val if TS_val > 0 else float('inf')
        
        # Category-specific expected ranges based on materials science
        # Brittle materials (ceramics, stone, glass) have much higher ratios
        category_ranges = {
            'metal': (100, 500),
            'ceramic': (500, 2000),
            'stone': (500, 15000),
            'glass': (500, 3000),
            'wood': (50, 300),
            'plastic': (30, 200),
            'composite': (30, 500),
            'semiconductor': (100, 1000),
            'masonry': (500, 10000)
        }
        
        expected_range = category_ranges.get(category, (50, 500))
        min_ratio, max_ratio = expected_range
        
        if ratio < min_ratio:
            issues.append({
                'severity': 'WARNING',
                'type': 'ratio_too_low',
                'material': material,
                'category': category,
                'E_GPa': E_val,
                'TS_MPa': TS_val,
                'ratio': ratio,
                'expected_range': expected_range,
                'message': f"E/TS ratio {ratio:.1f} < {min_ratio} (unusually low for {category})"
            })
        elif ratio > max_ratio:
            issues.append({
                'severity': 'ERROR',
                'type': 'ratio_too_high',
                'material': material,
                'category': category,
                'E_GPa': E_val,
                'TS_MPa': TS_val,
                'ratio': ratio,
                'expected_range': expected_range,
                'message': f"E/TS ratio {ratio:.1f} > {max_ratio} (exceeds {category} range)"
            })
        
        return issues
    
    # ========================================================================
    # LEVEL 3: CATEGORY VALIDATION
    # ========================================================================
    
    def validate_material_completeness(self, material: str, category: str,
                                       material_data: Dict) -> List[Dict]:
        """Validate material has required properties for its category"""
        issues = []
        
        if category not in CATEGORY_RULES:
            return issues
        
        rule = CATEGORY_RULES[category]
        
        # Get all properties in material
        all_props = set()
        if 'materialProperties' in material_data:
            for group_name, group_data in material_data['materialProperties'].items():
                if 'properties' in group_data:
                    all_props.update(group_data['properties'].keys())
        
        # Check required properties
        missing_required = set(rule.required_properties) - all_props
        if missing_required:
            issues.append({
                'severity': 'ERROR',
                'type': 'missing_required_properties',
                'material': material,
                'category': category,
                'missing': list(missing_required),
                'message': f"Missing required properties for {category}: {missing_required}"
            })
        
        # Check forbidden properties
        forbidden_present = set(rule.forbidden_properties) & all_props
        if forbidden_present:
            issues.append({
                'severity': 'WARNING',
                'type': 'forbidden_properties_present',
                'material': material,
                'category': category,
                'forbidden': list(forbidden_present),
                'message': f"Has forbidden properties for {category}: {forbidden_present}"
            })
        
        return issues
    
    # ========================================================================
    # MAIN VALIDATION ORCHESTRATION
    # ========================================================================
    
    def validate_all(self, verbose: bool = False) -> Dict:
        """Run comprehensive validation on all materials"""
        print("=" * 80)
        print("DATA QUALITY VALIDATION AGENT")
        print("=" * 80)
        print()
        
        all_issues = {
            'ERROR': [],
            'WARNING': [],
            'INFO': []
        }
        
        files = list(self.frontmatter_dir.glob("*.yaml"))
        print(f"Validating {len(files)} materials...")
        print()
        
        for file_path in sorted(files):
            material = file_path.stem.replace('-laser-cleaning', '')
            
            try:
                data = self.load_material(file_path)
                category = data.get('category', 'unknown')
                
                if verbose:
                    print(f"Validating {material} ({category})...")
                
                # Level 1: Property validation
                if 'materialProperties' in data:
                    for group_name, group_data in data['materialProperties'].items():
                        if 'properties' not in group_data:
                            continue
                        
                        for prop_name, prop_data in group_data['properties'].items():
                            issues = self.validate_property_value(
                                material, category, prop_name, prop_data
                            )
                            for issue in issues:
                                all_issues[issue['severity']].append(issue)
                    
                    # Level 2: Relationship validation
                    laser_props = data['materialProperties'].get('laser_material_interaction', {}).get('properties', {})
                    char_props = data['materialProperties'].get('material_characteristics', {}).get('properties', {})
                    
                    # Optical energy conservation
                    issues = self.validate_optical_energy_conservation(material, category, laser_props)
                    for issue in issues:
                        all_issues[issue['severity']].append(issue)
                    
                    # Thermal diffusivity formula
                    issues = self.validate_thermal_diffusivity_formula(material, category, laser_props, char_props)
                    for issue in issues:
                        all_issues[issue['severity']].append(issue)
                    
                    # Young's modulus / tensile strength ratio
                    issues = self.validate_youngs_tensile_ratio(material, category, char_props)
                    for issue in issues:
                        all_issues[issue['severity']].append(issue)
                
                # Level 3: Category validation
                issues = self.validate_material_completeness(material, category, data)
                for issue in issues:
                    all_issues[issue['severity']].append(issue)
                    
            except Exception as e:
                all_issues['ERROR'].append({
                    'severity': 'ERROR',
                    'type': 'processing_error',
                    'material': material,
                    'message': f"Error processing file: {str(e)}"
                })
        
        return all_issues
    
    def generate_report(self, issues: Dict, output_file: str = None):
        """Generate comprehensive validation report"""
        print("\n" + "=" * 80)
        print("VALIDATION REPORT")
        print("=" * 80)
        
        # Summary
        print(f"\nERRORS: {len(issues['ERROR'])}")
        print(f"WARNINGS: {len(issues['WARNING'])}")
        print(f"INFO: {len(issues['INFO'])}")
        
        # Group by type
        errors_by_type = defaultdict(list)
        for issue in issues['ERROR']:
            errors_by_type[issue['type']].append(issue)
        
        warnings_by_type = defaultdict(list)
        for issue in issues['WARNING']:
            warnings_by_type[issue['type']].append(issue)
        
        # Print errors
        if issues['ERROR']:
            print("\n" + "-" * 80)
            print("ERRORS (MUST FIX)")
            print("-" * 80)
            for issue_type, items in sorted(errors_by_type.items()):
                print(f"\n{issue_type}: {len(items)} instances")
                for item in items[:10]:  # Show first 10
                    print(f"  - {item['material']}: {item['message']}")
                if len(items) > 10:
                    print(f"  ... and {len(items) - 10} more")
        
        # Print warnings
        if issues['WARNING']:
            print("\n" + "-" * 80)
            print("WARNINGS (REVIEW RECOMMENDED)")
            print("-" * 80)
            for issue_type, items in sorted(warnings_by_type.items()):
                print(f"\n{issue_type}: {len(items)} instances")
                for item in items[:5]:  # Show first 5
                    print(f"  - {item['material']}: {item['message']}")
                if len(items) > 5:
                    print(f"  ... and {len(items) - 5} more")
        
        # Save detailed report
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(issues, f, indent=2)
            print(f"\n✅ Detailed report saved to: {output_file}")

def main():
    """Main entry point"""
    import sys
    
    verbose = '--verbose' in sys.argv
    output_file = 'validation_report.json'
    
    agent = DataQualityValidationAgent()
    issues = agent.validate_all(verbose=verbose)
    agent.generate_report(issues, output_file=output_file)
    
    # Exit code based on errors
    sys.exit(1 if issues['ERROR'] else 0)

if __name__ == '__main__':
    main()
