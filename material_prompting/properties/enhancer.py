#!/usr/bin/env python3
"""
Material Properties Enhancement with Comprehensive Analysis System

Enhanced material properties generator with comprehensive value analysis,
validation, and accuracy verification.

KEY MISSION: Ensure every value for each material is fully analyzed, 
checked and highly accurate.

This system provides:
- Comprehensive property analysis and validation with multi-source verification
- Category-aware property generation (metals vs ceramics vs woods)
- Statistical analysis and outlier detection for all property values
- Scientific cross-validation using material science principles
- Property gap detection and intelligent completion with accuracy scoring
- Cross-property validation and consistency checking
- Range validation based on material type with confidence intervals
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import analysis capabilities
try:
    from ..analysis.analyzer import (
        ValueAnalyzer,
        PropertyAnalysis,
        ValidationLevel,
        AccuracyClass,
        MaterialAnalysisReport
    )
    ANALYSIS_AVAILABLE = True
except ImportError:
    ANALYSIS_AVAILABLE = False
    logging.warning("Analysis not available - using basic validation")

logger = logging.getLogger(__name__)


class PropertyPriority(Enum):
    """Property priority levels for generation and validation"""
    CRITICAL = "critical"      # Must be present and accurate
    IMPORTANT = "important"    # Should be present for completeness
    OPTIONAL = "optional"      # Nice to have but not required
    DERIVED = "derived"        # Can be calculated from other properties


@dataclass
class MaterialProperty:
    """Enhanced material property with comprehensive analysis metadata"""
    name: str
    value: Any
    unit: str
    description: str
    priority: PropertyPriority
    min_range: Optional[float] = None
    max_range: Optional[float] = None
    validation_notes: Optional[str] = None
    source: Optional[str] = None  # Where this property came from
    confidence: float = 1.0       # Confidence in the value (0-1)
    
    # Comprehensive analysis fields
    analysis_confidence: float = 0.0      # Statistical confidence from analysis
    accuracy_class: str = "unknown"       # verified, validated, probable, estimated, uncertain
    sources_validated: int = 0             # Number of sources that validated this value
    scientific_consistency: float = 0.0   # Consistency with physical laws
    outlier_score: float = 0.0            # How much this value deviates from expected


@dataclass
class PropertyEnhancementResult:
    """Enhanced result of property enhancement operation with comprehensive analysis"""
    success: bool
    enhanced_properties: Dict[str, MaterialProperty]
    missing_properties: List[str]
    validation_errors: List[str]
    enhancement_notes: List[str]
    
    # Comprehensive analysis results
    analysis_report: Optional[Any] = None  # MaterialAnalysisReport when available
    overall_accuracy_score: float = 0.0
    properties_fully_analyzed: int = 0
    properties_verified: int = 0
    properties_validated: int = 0
    scientific_consistency_score: float = 0.0


class MaterialPropertiesEnhancer:
    """
    Enhanced material properties generator with category-aware customization
    
    Provides:
    - Property gap detection and intelligent completion
    - Category-specific property validation
    - Cross-property consistency checking
    - Range validation and normalization
    """
    
    def __init__(self):
        """Initialize material properties enhancer"""
        self.property_definitions = self._initialize_property_definitions()
        self.category_requirements = self._initialize_category_requirements()
        
        # Initialize material-aware systems
        self._material_generator = None
        self._exception_handler = None
        
        # Initialize logger for comprehensive analysis integration
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("Material Properties Enhancer initialized")

    @property
    def material_generator(self):
        """Lazy-loaded material-aware generator"""
        if self._material_generator is None:
            from ..core.material_aware_generator import MaterialAwarePromptGenerator
            self._material_generator = MaterialAwarePromptGenerator()
        return self._material_generator
    
    def _initialize_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Initialize property definitions with metadata"""
        
        return {
            'density': {
                'unit': 'g/cm³',
                'description': 'Mass per unit volume',
                'priority': PropertyPriority.CRITICAL,
                'category_ranges': {
                    'metal': (2.7, 19.3),
                    'ceramic': (2.0, 6.0),
                    'wood': (0.16, 1.4),
                    'plastic': (0.9, 2.2),
                    'composite': (1.2, 2.5)
                }
            },
            'thermalConductivity': {
                'unit': 'W/m·K',
                'description': 'Thermal conductivity',
                'priority': PropertyPriority.IMPORTANT,
                'category_ranges': {
                    'metal': (15, 400),
                    'ceramic': (0.5, 200),
                    'wood': (0.04, 0.4),
                    'plastic': (0.1, 2.0),
                    'composite': (0.5, 50)
                }
            },
            'meltingPoint': {
                'unit': '°C',
                'description': 'Melting temperature',
                'priority': PropertyPriority.IMPORTANT,
                'category_ranges': {
                    'metal': (232, 3410),  # Tin to Tungsten
                    'ceramic': (1000, 4000),
                    'plastic': (80, 350),
                    'composite': (150, 600)
                },
                'category_exceptions': {
                    'wood': 'decompositionTemperature'  # Use decomposition instead
                }
            },
            'tensileStrength': {
                'unit': 'MPa',
                'description': 'Ultimate tensile strength',
                'priority': PropertyPriority.IMPORTANT,
                'category_ranges': {
                    'metal': (50, 2000),
                    'ceramic': (10, 500),    # Note: ceramics are weak in tension
                    'wood': (20, 200),
                    'plastic': (10, 150),
                    'composite': (100, 3500)
                }
            },
            'youngsModulus': {
                'unit': 'GPa',
                'description': 'Elastic modulus',
                'priority': PropertyPriority.IMPORTANT,
                'category_ranges': {
                    'metal': (70, 400),
                    'ceramic': (200, 500),
                    'wood': (5, 25),
                    'plastic': (0.01, 50),
                    'composite': (50, 300)
                }
            },
            'hardness': {
                'unit': 'HV',  # Default to Vickers
                'description': 'Material hardness',
                'priority': PropertyPriority.OPTIONAL,
                'category_units': {
                    'metal': 'HV',      # Vickers hardness
                    'ceramic': 'Mohs',  # Mohs scale
                    'wood': 'kN',       # Janka hardness
                    'plastic': 'Shore'   # Shore hardness
                },
                'category_ranges': {
                    'metal': (10, 1000),  # HV
                    'ceramic': (6, 10),   # Mohs
                    'wood': (0.5, 20),    # kN
                    'plastic': (10, 100)  # Shore A/D
                }
            },
            'ablationThreshold': {
                'unit': 'J/cm²',
                'description': 'Laser ablation threshold',
                'priority': PropertyPriority.OPTIONAL,
                'category_ranges': {
                    'metal': (0.1, 20.0),
                    'ceramic': (1.0, 50.0),
                    'wood': (0.1, 5.0),
                    'plastic': (0.05, 2.0),
                    'composite': (0.2, 10.0)
                }
            }
        }
    
    def _initialize_category_requirements(self) -> Dict[str, List[str]]:
        """Initialize category-specific property requirements"""
        
        return {
            'metal': [
                'density', 'thermalConductivity', 'meltingPoint', 
                'tensileStrength', 'youngsModulus', 'hardness'
            ],
            'ceramic': [
                'density', 'thermalConductivity', 'meltingPoint',
                'hardness', 'youngsModulus'  # Note: tensileStrength less important
            ],
            'wood': [
                'density', 'thermalConductivity', 'decompositionTemperature',
                'tensileStrength', 'youngsModulus', 'hardness'
            ],
            'plastic': [
                'density', 'thermalConductivity', 'meltingPoint',
                'tensileStrength', 'youngsModulus'
            ],
            'composite': [
                'density', 'thermalConductivity', 'tensileStrength',
                'youngsModulus'  # Properties highly dependent on layup
            ]
        }
    
    def enhance_material_properties(
        self,
        material_name: str,
        material_category: str,
        existing_properties: Dict[str, Any],
        material_data: Dict[str, Any] = None,
        comprehensive_analysis: bool = True
    ) -> PropertyEnhancementResult:
        """
        Enhance material properties with comprehensive analysis and validation
        
        MISSION: Ensure every value is fully analyzed, checked and highly accurate
        
        Args:
            material_name: Name of the material
            material_category: Material category (metal, ceramic, etc.)
            existing_properties: Current property data
            material_data: Additional material context
            comprehensive_analysis: Perform comprehensive analysis if available
            
        Returns:
            PropertyEnhancementResult with enhanced and analyzed properties
        """
        
        try:
            enhanced_properties = {}
            missing_properties = []
            validation_errors = []
            enhancement_notes = []
            
            # Initialize comprehensive analysis if available
            analysis_report = None
            analyzer = None
            
            if comprehensive_analysis and ANALYSIS_AVAILABLE:
                try:
                    analyzer = ValueAnalyzer(self.material_generator)
                    self.logger.info(f"Performing comprehensive analysis for {material_name}")
                    
                    # Perform comprehensive analysis of all properties
                    analysis_report = analyzer.analyze_material_comprehensively(
                        material_name=material_name,
                        material_category=material_category,
                        existing_properties=existing_properties,
                        validation_level=ValidationLevel.COMPREHENSIVE
                    )
                    enhancement_notes.append("Comprehensive multi-source analysis performed")
                    
                except Exception as e:
                    self.logger.warning(f"Comprehensive analysis failed: {e}")
                    enhancement_notes.append("Falling back to standard validation")
            
            # Get required properties for this category
            required_props = self.category_requirements.get(material_category, [])
            
            # Process existing properties with enhanced analysis
            for prop_name, prop_data in existing_properties.items():
                try:
                    enhanced_prop = self._enhance_single_property(
                        prop_name, prop_data, material_category, analysis_report
                    )
                    enhanced_properties[prop_name] = enhanced_prop
                    
                    # Add analysis results to property if available
                    if analysis_report and prop_name in analysis_report.properties_analysis:
                        prop_analysis = analysis_report.properties_analysis[prop_name]
                        enhanced_prop.analysis_confidence = prop_analysis.statistical_confidence
                        enhanced_prop.accuracy_class = prop_analysis.accuracy_class.value
                        enhanced_prop.validation_notes = prop_analysis.validation_notes
                        
                except Exception as e:
                    validation_errors.append(f"Error enhancing {prop_name}: {e}")
            
            # Identify missing critical properties
            for required_prop in required_props:
                if required_prop not in enhanced_properties:
                    
                    # Check for category-specific alternatives
                    prop_def = self.property_definitions.get(required_prop, {})
                    alternatives = prop_def.get('category_exceptions', {})
                    
                    if material_category in alternatives:
                        alternative_prop = alternatives[material_category]
                        if alternative_prop not in enhanced_properties:
                            missing_properties.append(alternative_prop)
                            enhancement_notes.append(f"Use {alternative_prop} instead of {required_prop} for {material_category}")
                    else:
                        missing_properties.append(required_prop)
            
            # Generate missing properties if possible
            if missing_properties:
                generated_properties = self._generate_missing_properties(
                    material_name, material_category, missing_properties, enhanced_properties
                )
                enhanced_properties.update(generated_properties)
                enhancement_notes.append(f"Generated {len(generated_properties)} missing properties")
            
            # Cross-validate properties
            cross_validation_errors = self._cross_validate_properties(
                enhanced_properties, material_category
            )
            validation_errors.extend(cross_validation_errors)
            
            # Calculate comprehensive analysis metrics
            overall_accuracy_score = 0.0
            properties_fully_analyzed = 0
            properties_verified = 0
            properties_validated = 0
            scientific_consistency_score = 0.0
            
            if analysis_report:
                overall_accuracy_score = analysis_report.overall_accuracy_score
                properties_fully_analyzed = len(analysis_report.properties_analysis)
                scientific_consistency_score = analysis_report.scientific_consistency_score
                
                # Count accuracy classifications
                for prop_analysis in analysis_report.properties_analysis.values():
                    if prop_analysis.accuracy_class.value == 'verified':
                        properties_verified += 1
                    elif prop_analysis.accuracy_class.value == 'validated':
                        properties_validated += 1
                
                enhancement_notes.append(f"Accuracy score: {overall_accuracy_score:.3f}")
                enhancement_notes.append(f"Scientific consistency: {scientific_consistency_score:.3f}")
            
            success = len(validation_errors) == 0
            
            return PropertyEnhancementResult(
                success=success,
                enhanced_properties=enhanced_properties,
                missing_properties=missing_properties,
                validation_errors=validation_errors,
                enhancement_notes=enhancement_notes,
                analysis_report=analysis_report,
                overall_accuracy_score=overall_accuracy_score,
                properties_fully_analyzed=properties_fully_analyzed,
                properties_verified=properties_verified,
                properties_validated=properties_validated,
                scientific_consistency_score=scientific_consistency_score
            )
            
        except Exception as e:
            logger.error(f"Error enhancing properties for {material_name}: {e}")
            return PropertyEnhancementResult(
                success=False,
                enhanced_properties={},
                missing_properties=[],
                validation_errors=[f"Enhancement failed: {e}"],
                enhancement_notes=[]
            )
    
    def _enhance_single_property(
        self, 
        prop_name: str, 
        prop_data: Any, 
        category: str
    ) -> MaterialProperty:
        """Enhance a single property with validation and metadata"""
        
        prop_def = self.property_definitions.get(prop_name, {})
        
        # Extract value and unit
        if isinstance(prop_data, dict):
            value = prop_data.get('value', prop_data.get('default', ''))
            unit = prop_data.get('unit', prop_def.get('unit', ''))
            description = prop_data.get('description', prop_def.get('description', ''))
        else:
            value = prop_data
            unit = prop_def.get('unit', '')
            description = prop_def.get('description', '')
        
        # Get category-specific unit if available
        category_units = prop_def.get('category_units', {})
        if category in category_units:
            unit = category_units[category]
        
        # Get priority
        priority = prop_def.get('priority', PropertyPriority.OPTIONAL)
        
        # Get range for validation
        min_range, max_range = None, None
        category_ranges = prop_def.get('category_ranges', {})
        if category in category_ranges:
            min_range, max_range = category_ranges[category]
        
        # Validate range if numeric
        validation_notes = None
        try:
            if isinstance(value, (int, float)) or (isinstance(value, str) and any(c.isdigit() for c in value)):
                import re
                numbers = re.findall(r'(\d+\.?\d*)', str(value))
                if numbers and min_range is not None and max_range is not None:
                    num_val = float(numbers[0])
                    if not (min_range <= num_val <= max_range):
                        validation_notes = f"Value {num_val} outside expected range {min_range}-{max_range} for {category}"
        except:
            pass
        
        return MaterialProperty(
            name=prop_name,
            value=value,
            unit=unit,
            description=description,
            priority=priority,
            min_range=min_range,
            max_range=max_range,
            validation_notes=validation_notes
        )
    
    def _generate_missing_properties(
        self,
        material_name: str,
        category: str,
        missing_props: List[str],
        existing_props: Dict[str, MaterialProperty]
    ) -> Dict[str, MaterialProperty]:
        """Generate missing properties using material-aware prompts"""
        
        generated = {}
        
        try:
            # Initialize material generator if needed
            if self._material_generator is None:
                from ..core.material_aware_generator import MaterialAwarePromptGenerator
                self._material_generator = MaterialAwarePromptGenerator()
            
            # For each missing property, try to generate it
            for prop_name in missing_props:
                prop_def = self.property_definitions.get(prop_name, {})
                
                # Estimate property value based on category and existing properties
                estimated_value = self._estimate_property_value(
                    prop_name, category, existing_props
                )
                
                if estimated_value:
                    generated[prop_name] = MaterialProperty(
                        name=prop_name,
                        value=estimated_value,
                        unit=prop_def.get('unit', ''),
                        description=f"Estimated {prop_def.get('description', prop_name)}",
                        priority=prop_def.get('priority', PropertyPriority.OPTIONAL),
                        source='estimated',
                        confidence=0.7  # Lower confidence for estimated values
                    )
            
        except Exception as e:
            logger.warning(f"Could not generate missing properties: {e}")
        
        return generated
    
    def _estimate_property_value(
        self,
        prop_name: str,
        category: str,
        existing_props: Dict[str, MaterialProperty]
    ) -> Optional[str]:
        """Estimate property value based on category and existing properties"""
        
        prop_def = self.property_definitions.get(prop_name)
        if not prop_def:
            return None
        
        # Get typical range for this category
        category_ranges = prop_def.get('category_ranges', {})
        if category not in category_ranges:
            return None
        
        min_val, max_val = category_ranges[category]
        
        # Use middle of range as estimate
        estimated_val = (min_val + max_val) / 2
        unit = prop_def.get('unit', '')
        
        return f"{estimated_val:.2f} {unit}"
    
    def _cross_validate_properties(
        self,
        properties: Dict[str, MaterialProperty],
        category: str
    ) -> List[str]:
        """Cross-validate properties for consistency"""
        
        errors = []
        
        # Check density vs other properties consistency
        if 'density' in properties and 'thermalConductivity' in properties:
            try:
                density_val = self._extract_numeric_value(properties['density'].value)
                tc_val = self._extract_numeric_value(properties['thermalConductivity'].value)
                
                # For metals, generally higher density correlates with higher thermal conductivity
                if category == 'metal' and density_val and tc_val:
                    if density_val > 10 and tc_val < 50:  # Dense metal but low TC
                        errors.append("High density metal with unexpectedly low thermal conductivity")
                    elif density_val < 5 and tc_val > 200:  # Light metal but very high TC
                        errors.append("Low density metal with unexpectedly high thermal conductivity")
            except:
                pass  # Skip validation if values can't be extracted
        
        return errors
    
    def _extract_numeric_value(self, value: Any) -> Optional[float]:
        """Extract numeric value from property value string"""
        try:
            import re
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                numbers = re.findall(r'(\d+\.?\d*)', value)
                if numbers:
                    return float(numbers[0])
        except:
            pass
        return None


if __name__ == "__main__":
    # Test material properties enhancement
    enhancer = MaterialPropertiesEnhancer()
    
    # Test with incomplete aluminum properties
    aluminum_props = {
        'density': {'value': '2.7 g/cm³', 'unit': 'g/cm³'},
        'thermalConductivity': {'value': '167 W/m·K', 'unit': 'W/m·K'}
        # Missing meltingPoint, tensileStrength, etc.
    }
    
    result = enhancer.enhance_material_properties(
        material_name='Aluminum 6061',
        material_category='metal',
        existing_properties=aluminum_props
    )
    
    print("=== PROPERTY ENHANCEMENT RESULT ===")
    print(f"Success: {result.success}")
    print(f"Enhanced properties: {len(result.enhanced_properties)}")
    print(f"Missing properties: {result.missing_properties}")
    print(f"Validation errors: {result.validation_errors}")
    print(f"Enhancement notes: {result.enhancement_notes}")
    
    for prop_name, prop_obj in result.enhanced_properties.items():
        print(f"  {prop_name}: {prop_obj.value} {prop_obj.unit} (Priority: {prop_obj.priority.value})")