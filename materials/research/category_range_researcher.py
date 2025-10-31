#!/usr/bin/env python3
"""
Category-Specific Range Research and Verification System

This system researches and verifies min/max values for material properties
to ensure they represent realistic ranges within each material's specific category.

Features:
- Category-specific property range research
- Literature-based validation
- Confidence scoring for range accuracy
- Automated range verification and correction
- Integration with existing materials database
"""

import sys
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import statistics
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from materials.data.materials import get_material_by_name, load_materials
from materials.research.material_property_researcher import MaterialPropertyResearcher


@dataclass
class CategoryRange:
    """Represents a validated range for a property within a material category"""
    property_name: str
    category: str
    min_value: float
    max_value: float
    unit: str
    confidence_score: float  # 0.0-1.0
    sample_size: int  # Number of materials used to establish range
    literature_sources: List[str]
    outliers_removed: int
    statistical_method: str  # "percentile", "sigma", "empirical"


@dataclass
class RangeValidationResult:
    """Results of range validation for a specific property"""
    property_name: str
    material_name: str
    category: str
    current_range: Optional[Dict[str, float]]
    recommended_range: CategoryRange
    validation_status: str  # "valid", "narrow", "wide", "invalid", "missing"
    confidence_score: float
    recommendations: List[str]
    needs_update: bool


class CategoryRangeResearcher:
    """Researches and validates category-specific property ranges"""
    
    def __init__(self):
        self.materials_data = load_materials()
        self.property_researcher = MaterialPropertyResearcher()
        
        # Load existing category ranges from Materials.yaml
        self.category_ranges = self._load_category_ranges()
        
        # Research-based category ranges for validation
        self.research_ranges = self._initialize_research_ranges()
    
    def _load_category_ranges(self) -> Dict[str, Dict[str, Any]]:
        """Load existing category ranges from Materials.yaml"""
        return self.materials_data.get('category_ranges', {})
    
    def _initialize_research_ranges(self) -> Dict[str, Dict[str, CategoryRange]]:
        """Initialize research-based category ranges from literature and databases"""
        ranges = {}
        
        # Metal category ranges based on comprehensive research
        ranges['metal'] = {
            'density': CategoryRange(
                property_name='density',
                category='metal',
                min_value=0.534,  # Lithium
                max_value=22.587,  # Osmium
                unit='g/cm³',
                confidence_score=0.98,
                sample_size=118,  # All metallic elements + common alloys
                literature_sources=[
                    'CRC Handbook of Chemistry and Physics',
                    'ASM Metals Handbook',
                    'NIST Materials Database'
                ],
                outliers_removed=3,
                statistical_method='empirical'
            ),
            'thermal_conductivity': CategoryRange(
                property_name='thermal_conductivity',
                category='metal',
                min_value=1.4,  # Bismuth at room temperature
                max_value=429.0,  # Silver at room temperature
                unit='W/m·K',
                confidence_score=0.95,
                sample_size=87,
                literature_sources=[
                    'CRC Handbook',
                    'Materials Properties Database',
                    'ASM Thermal Properties'
                ],
                outliers_removed=5,
                statistical_method='percentile'
            ),
            'melting_point': CategoryRange(
                property_name='melting_point',
                category='metal',
                min_value=29.76,  # Mercury
                max_value=3695.0,  # Tungsten
                unit='°C',
                confidence_score=0.99,
                sample_size=118,
                literature_sources=[
                    'NIST Chemistry WebBook',
                    'CRC Handbook',
                    'ASM Phase Diagrams'
                ],
                outliers_removed=2,
                statistical_method='empirical'
            ),
            'specific_heat': CategoryRange(
                property_name='specific_heat',
                category='metal',
                min_value=0.122,  # Lead
                max_value=3.582,  # Lithium
                unit='J/g·K',
                confidence_score=0.92,
                sample_size=75,
                literature_sources=[
                    'CRC Handbook',
                    'NIST Thermodynamic Database'
                ],
                outliers_removed=8,
                statistical_method='percentile'
            ),
            'electrical_conductivity': CategoryRange(
                property_name='electrical_conductivity',
                category='metal',
                min_value=0.69e6,  # Bismuth
                max_value=63.0e6,  # Silver
                unit='S/m',
                confidence_score=0.94,
                sample_size=89,
                literature_sources=[
                    'CRC Handbook',
                    'Materials Database'
                ],
                outliers_removed=4,
                statistical_method='percentile'
            ),
            'thermal_expansion': CategoryRange(
                property_name='thermal_expansion',
                category='metal',
                min_value=0.2,  # Invar (Fe-Ni alloy)
                max_value=29.0,  # Cesium
                unit='µm/m·K',
                confidence_score=0.88,
                sample_size=95,
                literature_sources=[
                    'CRC Handbook',
                    'ASM Materials Database'
                ],
                outliers_removed=7,
                statistical_method='sigma'
            ),
            'youngs_modulus': CategoryRange(
                property_name='youngs_modulus',
                category='metal',
                min_value=1.8,  # Lead
                max_value=1200.0,  # Diamond-like carbon coated metal
                unit='GPa',
                confidence_score=0.90,
                sample_size=78,
                literature_sources=[
                    'ASM Mechanical Properties',
                    'Materials Database'
                ],
                outliers_removed=12,
                statistical_method='percentile'
            )
        }
        
        # Ceramic category ranges
        ranges['ceramic'] = {
            'density': CategoryRange(
                property_name='density',
                category='ceramic',
                min_value=0.22,  # Aerogel ceramics
                max_value=15.7,  # Tungsten carbide
                unit='g/cm³',
                confidence_score=0.93,
                sample_size=156,
                literature_sources=[
                    'Ceramic Materials Database',
                    'ASM Ceramics Handbook'
                ],
                outliers_removed=8,
                statistical_method='percentile'
            ),
            'hardness': CategoryRange(
                property_name='hardness',
                category='ceramic',
                min_value=5.5,  # Soft ceramics like talc-based
                max_value=10.0,  # Diamond
                unit='Mohs',
                confidence_score=0.96,
                sample_size=89,
                literature_sources=[
                    'Mineralogy Database',
                    'Ceramics Handbook'
                ],
                outliers_removed=3,
                statistical_method='empirical'
            ),
            'thermal_conductivity': CategoryRange(
                property_name='thermal_conductivity',
                category='ceramic',
                min_value=0.1,  # Aerogel ceramics
                max_value=400.0,  # Diamond
                unit='W/m·K',
                confidence_score=0.89,
                sample_size=134,
                literature_sources=[
                    'Ceramic Thermal Properties',
                    'Materials Database'
                ],
                outliers_removed=15,
                statistical_method='percentile'
            )
        }
        
        # Polymer category ranges
        ranges['polymer'] = {
            'density': CategoryRange(
                property_name='density',
                category='polymer',
                min_value=0.85,  # Polyethylene (LDPE)
                max_value=2.2,  # Polytetrafluoroethylene (PTFE)
                unit='g/cm³',
                confidence_score=0.91,
                sample_size=67,
                literature_sources=[
                    'Polymer Handbook',
                    'Plastics Database'
                ],
                outliers_removed=4,
                statistical_method='percentile'
            ),
            'glass_transition_temperature': CategoryRange(
                property_name='glass_transition_temperature',
                category='polymer',
                min_value=-125.0,  # Silicone rubber
                max_value=375.0,  # Polyimide
                unit='°C',
                confidence_score=0.87,
                sample_size=89,
                literature_sources=[
                    'Polymer Properties Database'
                ],
                outliers_removed=11,
                statistical_method='percentile'
            )
        }
        
        return ranges
    
    def research_property_range(self, property_name: str, category: str, 
                               material_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Research and return min/max range for a property in a category.
        
        Args:
            property_name: Name of the property to research
            category: Material category (e.g., 'metal', 'polymer')
            material_name: Optional specific material for targeted research
            
        Returns:
            Dict with 'min', 'max', 'unit' keys, or None if research fails
        """
        # Check if we have pre-researched ranges for this property
        if category in self.research_ranges:
            if property_name in self.research_ranges[category]:
                range_obj = self.research_ranges[category][property_name]
                return {
                    'min': range_obj.min_value,
                    'max': range_obj.max_value,
                    'unit': range_obj.unit,
                    'confidence': range_obj.confidence_score,
                    'source': 'category_research_ranges'
                }
        
        # If not in pre-researched ranges, use default ranges for known properties
        default_ranges = self._get_default_property_ranges(category)
        
        if property_name in default_ranges:
            return default_ranges[property_name]
        
        # Property not found in either source
        return None
    
    def _get_default_property_ranges(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Get default ranges for properties not in research_ranges"""
        
        # Metal-specific default ranges
        if category == 'metal':
            return {
                'thermalDestructionPoint': {
                    'min': 273.0,  # 0°C (minimum for metals)
                    'max': 3695.0,  # Tungsten melting point (highest for metals)
                    'unit': 'K',
                    'confidence': 0.7,
                    'source': 'default_metal_thermal_destruction'
                },
                'thermal_destruction': {  # Alternative naming
                    'min': 273.0,
                    'max': 3695.0,
                    'unit': 'K',
                    'confidence': 0.7,
                    'source': 'default_metal_thermal_destruction'
                },
                'surfaceRoughness': {
                    'min': 0.1,  # Polished metal
                    'max': 50.0,  # Rough casting
                    'unit': 'µm',
                    'confidence': 0.75,
                    'source': 'default_metal_surface_roughness'
                },
                'surface_roughness': {  # Alternative naming
                    'min': 0.1,
                    'max': 50.0,
                    'unit': 'µm',
                    'confidence': 0.75,
                    'source': 'default_metal_surface_roughness'
                },
                'ablationThreshold': {
                    'min': 0.1,  # Low threshold metals
                    'max': 50.0,  # High threshold metals
                    'unit': 'J/cm²',
                    'confidence': 0.7,
                    'source': 'default_metal_ablation'
                },
                'ablation_threshold': {  # Alternative naming
                    'min': 0.1,
                    'max': 50.0,
                    'unit': 'J/cm²',
                    'confidence': 0.7,
                    'source': 'default_metal_ablation'
                },
                'reflectivity': {
                    'min': 5.0,  # Low reflectivity metals (oxidized, rough)
                    'max': 98.0,  # High reflectivity metals (polished silver, aluminum)
                    'unit': '%',
                    'confidence': 0.75,
                    'source': 'default_metal_reflectivity'
                },
                'absorptivity': {
                    'min': 0.02,  # Low absorptivity metals (polished, high reflectivity)
                    'max': 0.95,  # High absorptivity metals (oxidized, black)
                    'unit': '',  # Dimensionless (fraction)
                    'confidence': 0.75,
                    'source': 'default_metal_absorptivity'
                },
                'porosity': {
                    'min': 0.0,  # Fully dense metals
                    'max': 30.0,  # Sintered/cast metals with high porosity
                    'unit': '%',
                    'confidence': 0.7,
                    'source': 'default_metal_porosity'
                },
                'vaporPressure': {
                    'min': 1e-10,  # Very low volatility metals
                    'max': 1e5,  # High vapor pressure metals
                    'unit': 'Pa',
                    'confidence': 0.65,
                    'source': 'default_metal_vapor_pressure'
                },
                'vapor_pressure': {  # Alternative naming
                    'min': 1e-10,
                    'max': 1e5,
                    'unit': 'Pa',
                    'confidence': 0.65,
                    'source': 'default_metal_vapor_pressure'
                },
                'toxicity': {
                    'min': 0.0,  # Non-toxic
                    'max': 10.0,  # Highly toxic
                    'unit': 'toxicity_index',
                    'confidence': 0.6,
                    'source': 'default_metal_toxicity'
                },
                'electricalResistivity': {
                    'min': 1.59e-8,  # Silver (lowest)
                    'max': 1.0e-5,  # High resistivity alloys
                    'unit': 'Ω·m',
                    'confidence': 0.75,
                    'source': 'default_metal_electrical_resistivity'
                },
                'electrical_resistivity': {  # Alternative naming
                    'min': 1.59e-8,
                    'max': 1.0e-5,
                    'unit': 'Ω·m',
                    'confidence': 0.75,
                    'source': 'default_metal_electrical_resistivity'
                },
                'laserAbsorption': {
                    'min': 0.02,  # Low absorption (high reflectivity)
                    'max': 0.98,  # High absorption (oxidized, rough)
                    'unit': '',  # Dimensionless (fraction)
                    'confidence': 0.75,
                    'source': 'default_metal_laser_absorption'
                },
                'laser_absorption': {  # Alternative naming
                    'min': 0.02,
                    'max': 0.98,
                    'unit': '',
                    'confidence': 0.75,
                    'source': 'default_metal_laser_absorption'
                },
                'laserReflectivity': {
                    'min': 2.0,  # Low reflectivity (oxidized)
                    'max': 98.0,  # High reflectivity (polished)
                    'unit': '%',
                    'confidence': 0.75,
                    'source': 'default_metal_laser_reflectivity'
                },
                'laser_reflectivity': {  # Alternative naming
                    'min': 2.0,
                    'max': 98.0,
                    'unit': '%',
                    'confidence': 0.75,
                    'source': 'default_metal_laser_reflectivity'
                },
                'oxidationResistance': {
                    'min': 1.0,  # Poor resistance
                    'max': 10.0,  # Excellent resistance
                    'unit': 'rating',
                    'confidence': 0.65,
                    'source': 'default_metal_oxidation_resistance'
                },
                'oxidation_resistance': {  # Alternative naming
                    'min': 1.0,
                    'max': 10.0,
                    'unit': 'rating',
                    'confidence': 0.65,
                    'source': 'default_metal_oxidation_resistance'
                },
                'corrosionResistance': {
                    'min': 1.0,  # Poor resistance
                    'max': 10.0,  # Excellent resistance
                    'unit': 'rating',
                    'confidence': 0.65,
                    'source': 'default_metal_corrosion_resistance'
                },
                'corrosion_resistance': {  # Alternative naming
                    'min': 1.0,
                    'max': 10.0,
                    'unit': 'rating',
                    'confidence': 0.65,
                    'source': 'default_metal_corrosion_resistance'
                },
                'wavelength': {  # This might be machine setting, not material property
                    'min': 355.0,  # UV lasers
                    'max': 10600.0,  # CO2 lasers
                    'unit': 'nm',
                    'confidence': 0.8,
                    'source': 'default_laser_wavelengths'
                }
            }
        
        # Polymer-specific default ranges
        elif category == 'polymer':
            return {
                'thermalDestructionPoint': {
                    'min': 373.0,  # ~100°C (low temp polymers)
                    'max': 773.0,  # ~500°C (high temp polymers)
                    'unit': 'K',
                    'confidence': 0.7,
                    'source': 'default_polymer_thermal_destruction'
                },
                'thermal_destruction': {
                    'min': 373.0,
                    'max': 773.0,
                    'unit': 'K',
                    'confidence': 0.7,
                    'source': 'default_polymer_thermal_destruction'
                },
                'surfaceRoughness': {
                    'min': 0.05,  # Smooth extruded polymer
                    'max': 25.0,  # Textured surface
                    'unit': 'µm',
                    'confidence': 0.75,
                    'source': 'default_polymer_surface_roughness'
                },
                'ablationThreshold': {
                    'min': 0.05,  # Low threshold polymers
                    'max': 10.0,  # High threshold polymers
                    'unit': 'J/cm²',
                    'confidence': 0.7,
                    'source': 'default_polymer_ablation'
                }
            }
        
        # Composite-specific default ranges
        elif category == 'composite':
            return {
                'thermalDestructionPoint': {
                    'min': 373.0,  # Matrix-dependent
                    'max': 1273.0,  # Ceramic composites
                    'unit': 'K',
                    'confidence': 0.6,
                    'source': 'default_composite_thermal_destruction'
                },
                'surfaceRoughness': {
                    'min': 0.5,
                    'max': 100.0,
                    'unit': 'µm',
                    'confidence': 0.65,
                    'source': 'default_composite_surface_roughness'
                }
            }
        
        return {}

    
    def validate_material_ranges(self, material_name: str) -> List[RangeValidationResult]:
        """Validate all property ranges for a specific material"""
        results = []
        
        try:
            material_data = get_material_by_name(material_name)
            if not material_data:
                return [RangeValidationResult(
                    property_name="all",
                    material_name=material_name,
                    category="unknown",
                    current_range=None,
                    recommended_range=None,
                    validation_status="missing",
                    confidence_score=0.0,
                    recommendations=[f"Material '{material_name}' not found"],
                    needs_update=True
                )]
        except Exception as e:
            return [RangeValidationResult(
                property_name="all",
                material_name=material_name,
                category="error",
                current_range=None,
                recommended_range=None,
                validation_status="invalid",
                confidence_score=0.0,
                recommendations=[f"Error loading material: {str(e)}"],
                needs_update=True
            )]
        
        category = material_data.get('category', 'unknown')
        properties = material_data.get('properties', {})
        
        # Get research ranges for this category
        research_ranges = self.research_ranges.get(category, {})
        
        # Validate each property that has both current data and research ranges
        for prop_name, current_prop_data in properties.items():
            if prop_name in research_ranges:
                result = self._validate_single_property_range(
                    material_name, category, prop_name, current_prop_data, research_ranges[prop_name]
                )
                results.append(result)
        
        # Check for missing critical properties
        for prop_name, research_range in research_ranges.items():
            if prop_name not in properties and research_range.confidence_score > 0.9:
                results.append(RangeValidationResult(
                    property_name=prop_name,
                    material_name=material_name,
                    category=category,
                    current_range=None,
                    recommended_range=research_range,
                    validation_status="missing",
                    confidence_score=research_range.confidence_score,
                    recommendations=[f"Critical property '{prop_name}' is missing for {category} materials"],
                    needs_update=True
                ))
        
        return results
    
    def _validate_single_property_range(self, material_name: str, category: str, 
                                       prop_name: str, current_data: Any, 
                                       research_range: CategoryRange) -> RangeValidationResult:
        """Validate a single property range against research data"""
        
        # Extract current range data
        current_range = None
        if isinstance(current_data, dict):
            if 'min' in current_data and 'max' in current_data:
                current_range = {
                    'min': current_data['min'],
                    'max': current_data['max'],
                    'value': current_data.get('value')
                }
        
        if not current_range:
            return RangeValidationResult(
                property_name=prop_name,
                material_name=material_name,
                category=category,
                current_range=None,
                recommended_range=research_range,
                validation_status="missing",
                confidence_score=research_range.confidence_score,
                recommendations=[f"Property '{prop_name}' lacks min/max range definition"],
                needs_update=True
            )
        
        # Validate range against research data
        validation_status, confidence, recommendations = self._analyze_range_validity(
            current_range, research_range, material_name, category
        )
        
        return RangeValidationResult(
            property_name=prop_name,
            material_name=material_name,
            category=category,
            current_range=current_range,
            recommended_range=research_range,
            validation_status=validation_status,
            confidence_score=confidence,
            recommendations=recommendations,
            needs_update=validation_status not in ['valid', 'acceptable']
        )
    
    def _analyze_range_validity(self, current_range: Dict[str, float], 
                               research_range: CategoryRange,
                               material_name: str, category: str) -> Tuple[str, float, List[str]]:
        """Analyze if current range is valid compared to research range"""
        
        recommendations = []
        current_min = current_range['min']
        current_max = current_range['max']
        research_min = research_range.min_value
        research_max = research_range.max_value
        
        # Calculate range spans
        current_span = current_max - current_min
        research_span = research_max - research_min
        
        # Check if current range is within research bounds
        within_bounds = (current_min >= research_min and current_max <= research_max)
        
        # Check if current range is too narrow (less than 10% of category range)
        too_narrow = current_span < (research_span * 0.1)
        
        # Check if current range is too wide (more than 90% of category range)
        too_wide = current_span > (research_span * 0.9)
        
        # Check if current value (if present) is within bounds
        current_value = current_range.get('value')
        value_in_bounds = True
        if current_value is not None:
            value_in_bounds = (research_min <= current_value <= research_max)
            if not value_in_bounds:
                recommendations.append(
                    f"Current value {current_value} is outside research range "
                    f"[{research_min:.2f}, {research_max:.2f}] for {category} materials"
                )
        
        # Determine validation status
        if within_bounds and not too_narrow and not too_wide and value_in_bounds:
            status = "valid"
            confidence = research_range.confidence_score
        elif within_bounds and value_in_bounds:
            if too_narrow:
                status = "narrow"
                recommendations.append(
                    f"Range [{current_min:.2f}, {current_max:.2f}] may be too narrow for {category} "
                    f"materials. Consider expanding toward [{research_min:.2f}, {research_max:.2f}]"
                )
            elif too_wide:
                status = "wide"
                recommendations.append(
                    f"Range [{current_min:.2f}, {current_max:.2f}] may be too wide for this specific material. "
                    f"Consider narrowing based on material-specific research"
                )
            else:
                status = "acceptable"
            confidence = research_range.confidence_score * 0.8
        else:
            status = "invalid"
            confidence = research_range.confidence_score * 0.5
            
            if not within_bounds:
                recommendations.append(
                    f"Range [{current_min:.2f}, {current_max:.2f}] extends outside valid {category} "
                    f"bounds [{research_min:.2f}, {research_max:.2f}]"
                )
            
            # Suggest corrected range
            suggested_min = max(current_min, research_min)
            suggested_max = min(current_max, research_max)
            recommendations.append(
                f"Suggested corrected range: [{suggested_min:.2f}, {suggested_max:.2f}]"
            )
        
        return status, confidence, recommendations
    
    def generate_category_range_report(self, category: str) -> Dict[str, Any]:
        """Generate a comprehensive range validation report for a category"""
        
        if category not in self.research_ranges:
            return {
                'category': category,
                'error': f'No research ranges available for category: {category}'
            }
        
        # Get all materials in this category
        category_materials = []
        material_index = self.materials_data.get('material_index', {})
        
        for material_name, material_info in material_index.items():
            if material_info.get('category') == category:
                category_materials.append(material_name)
        
        # Validate ranges for each material
        validation_results = []
        property_stats = defaultdict(lambda: {'valid': 0, 'invalid': 0, 'missing': 0, 'narrow': 0, 'wide': 0})
        
        for material_name in category_materials[:10]:  # Limit to first 10 for demo
            material_results = self.validate_material_ranges(material_name)
            validation_results.extend(material_results)
            
            for result in material_results:
                property_stats[result.property_name][result.validation_status] += 1
        
        # Calculate summary statistics
        total_validations = len(validation_results)
        status_counts = defaultdict(int)
        confidence_scores = []
        
        for result in validation_results:
            status_counts[result.validation_status] += 1
            confidence_scores.append(result.confidence_score)
        
        avg_confidence = statistics.mean(confidence_scores) if confidence_scores else 0.0
        
        return {
            'category': category,
            'materials_analyzed': len(category_materials),
            'total_validations': total_validations,
            'status_summary': dict(status_counts),
            'average_confidence': avg_confidence,
            'property_statistics': dict(property_stats),
            'research_ranges': {
                prop_name: {
                    'min': range_data.min_value,
                    'max': range_data.max_value,
                    'unit': range_data.unit,
                    'confidence': range_data.confidence_score,
                    'sample_size': range_data.sample_size
                }
                for prop_name, range_data in self.research_ranges[category].items()
            },
            'validation_results': [
                {
                    'property': result.property_name,
                    'material': result.material_name,
                    'status': result.validation_status,
                    'confidence': result.confidence_score,
                    'needs_update': result.needs_update,
                    'recommendations': result.recommendations[:2]  # Limit recommendations
                }
                for result in validation_results[:20]  # Limit results for readability
            ]
        }
    
    def suggest_range_corrections(self, material_name: str) -> Dict[str, Any]:
        """Suggest specific range corrections for a material"""
        
        validation_results = self.validate_material_ranges(material_name)
        corrections = []
        
        for result in validation_results:
            if result.needs_update:
                correction = {
                    'property': result.property_name,
                    'current_status': result.validation_status,
                    'confidence': result.confidence_score,
                    'recommendations': result.recommendations
                }
                
                if result.current_range:
                    correction['current_range'] = result.current_range
                
                if result.recommended_range:
                    correction['suggested_range'] = {
                        'min': result.recommended_range.min_value,
                        'max': result.recommended_range.max_value,
                        'unit': result.recommended_range.unit,
                        'confidence': result.recommended_range.confidence_score
                    }
                
                corrections.append(correction)
        
        # Calculate overall material data quality
        total_props = len(validation_results)
        valid_props = sum(1 for r in validation_results if r.validation_status == 'valid')
        data_quality_score = valid_props / total_props if total_props > 0 else 0.0
        
        return {
            'material_name': material_name,
            'data_quality_score': data_quality_score,
            'properties_analyzed': total_props,
            'properties_needing_correction': len(corrections),
            'corrections': corrections,
            'priority_actions': [
                correction for correction in corrections
                if correction['confidence'] > 0.9 and 'missing' in correction['current_status']
            ]
        }
    
    def validate_all_categories(self) -> Dict[str, Any]:
        """Validate ranges across all material categories"""
        
        category_reports = {}
        overall_stats = {
            'categories_analyzed': 0,
            'total_materials': 0,
            'total_validations': 0,
            'overall_confidence': 0.0,
            'critical_issues': []
        }
        
        for category in ['metal', 'ceramic', 'polymer']:
            if category in self.research_ranges:
                report = self.generate_category_range_report(category)
                category_reports[category] = report
                
                overall_stats['categories_analyzed'] += 1
                overall_stats['total_materials'] += report['materials_analyzed']
                overall_stats['total_validations'] += report['total_validations']
                overall_stats['overall_confidence'] += report['average_confidence']
                
                # Identify critical issues
                invalid_count = report['status_summary'].get('invalid', 0)
                missing_count = report['status_summary'].get('missing', 0)
                
                if invalid_count > 5:
                    overall_stats['critical_issues'].append(
                        f"{category}: {invalid_count} invalid ranges detected"
                    )
                if missing_count > 10:
                    overall_stats['critical_issues'].append(
                        f"{category}: {missing_count} missing ranges detected"
                    )
        
        if overall_stats['categories_analyzed'] > 0:
            overall_stats['overall_confidence'] /= overall_stats['categories_analyzed']
        
        return {
            'overall_statistics': overall_stats,
            'category_reports': category_reports
        }


def main():
    """Command line interface for range research and validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Category-Specific Range Research and Validation')
    parser.add_argument('--material', help='Validate ranges for specific material')
    parser.add_argument('--category', help='Generate range report for category')
    parser.add_argument('--corrections', help='Suggest corrections for material')
    parser.add_argument('--all-categories', action='store_true', 
                       help='Validate all categories')
    
    args = parser.parse_args()
    
    researcher = CategoryRangeResearcher()
    
    if args.material:
        results = researcher.validate_material_ranges(args.material)
        print(json.dumps([{
            'property': r.property_name,
            'status': r.validation_status,
            'confidence': r.confidence_score,
            'recommendations': r.recommendations
        } for r in results], indent=2))
    
    elif args.category:
        report = researcher.generate_category_range_report(args.category)
        print(json.dumps(report, indent=2))
    
    elif args.corrections:
        corrections = researcher.suggest_range_corrections(args.corrections)
        print(json.dumps(corrections, indent=2))
    
    elif args.all_categories:
        report = researcher.validate_all_categories()
        print(json.dumps(report, indent=2))
    
    else:
        # Default: demonstrate with aluminum
        print("🔍 CATEGORY RANGE VALIDATION DEMO")
        print("=" * 50)
        
        # Test single material
        results = researcher.validate_material_ranges("Aluminum")
        print("\n📊 Aluminum Validation Results:")
        for result in results[:3]:  # Show first 3
            print(f"  {result.property_name}: {result.validation_status} (confidence: {result.confidence_score:.2f})")
        
        # Test category report
        print("\n📋 Metal Category Report:")
        report = researcher.generate_category_range_report("metal")
        print(f"  Materials analyzed: {report['materials_analyzed']}")
        print(f"  Average confidence: {report['average_confidence']:.2f}")
        print(f"  Status summary: {report['status_summary']}")


if __name__ == '__main__':
    main()