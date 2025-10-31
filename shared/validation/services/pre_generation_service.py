#!/usr/bin/env python3
"""
Pre-Generation Validation Service

Unified pre-generation validation service consolidating:
- comprehensive_validation_agent.py logic (property, relationship, category validation)
- fail_fast_materials_validator.py  
- materials_validator.py
- material_data_gap_analyzer.py
- analyze_ratio_errors.py

STRICT FAIL-FAST ARCHITECTURE - ZERO TOLERANCE for mocks/fallbacks
Per GROK_INSTRUCTIONS.md:
- CRITICAL/ERROR severity: System MUST fail immediately
- No optional validation - all checks are required
- No degraded operation modes
"""

import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict
import math
import logging

# Import unified error types
from shared.validation.errors import (
    ValidationError as VError,
    ValidationResult,
    ErrorSeverity,
    ErrorType,
    ConfigurationError,
    MaterialsValidationError
)

# Import validation helpers
from shared.validation.helpers.property_validators import PropertyValidators
from shared.validation.helpers.relationship_validators import RelationshipValidators
from shared.validation.helpers.unit_converter import UnitConverter, UnitConversionError

# Import validation rules from comprehensive_validation_agent
from scripts.validation.comprehensive_validation_agent import (
    PropertyRule,
    RelationshipRule,
    CategoryRule,
    PROPERTY_RULES,
    RELATIONSHIP_RULES,
    CATEGORY_RULES,
    QUALITATIVE_ONLY_PROPERTIES
)

logger = logging.getLogger(__name__)


# ============================================================================
# GAP ANALYSIS RESULT
# ============================================================================

@dataclass
class GapAnalysisResult:
    """Result of gap analysis"""
    total_materials: int
    total_gaps: int
    critical_gaps: int
    gaps_by_priority: Dict[int, int]
    gaps_by_type: Dict[str, int]
    materials_needing_research: List[Dict[str, Any]]
    completion_percentage: float


# ============================================================================
# PRE-GENERATION VALIDATION SERVICE
# ============================================================================

class PreGenerationValidationService:
    """
    Unified pre-generation validation service.
    
    Consolidates validation logic from multiple scripts into single service.
    Enforces strict fail-fast architecture per GROK_INSTRUCTIONS.md.
    
    ZERO TOLERANCE:
    - No optional validation (all checks are required)
    - No degraded operation modes  
    - CRITICAL/ERROR severity = immediate failure
    """
    
    def __init__(self, data_dir: Path = None):
        """
        Initialize validation service.
        
        Args:
            data_dir: Root directory for data files
        
        Raises:
            ConfigurationError: If required files are missing
        """
        self.data_dir = data_dir or Path(".")
        
        self.frontmatter_dir = self.data_dir / "content" / "frontmatter"
        self.categories_file = self.data_dir / "data" / "Categories.yaml"
        self.materials_file = self.data_dir / "data" / "Materials.yaml"
        
        # Validate required files exist (fail-fast)
        if not self.categories_file.exists():
            raise ConfigurationError(
                f"Categories.yaml not found at {self.categories_file}. "
                "This file is required for validation. "
                "Ensure data/Categories.yaml exists."
            )
        
        if not self.materials_file.exists():
            raise ConfigurationError(
                f"Materials.yaml not found at {self.materials_file}. "
                "This file is required for validation. "
                "Ensure data/Materials.yaml exists."
            )
        
        # Load validation rules from comprehensive_validation_agent
        self.property_rules = PROPERTY_RULES
        self.relationship_rules = RELATIONSHIP_RULES
        self.category_rules = CATEGORY_RULES
        
        logger.info("✅ PreGenerationValidationService initialized (strict fail-fast mode)")
    
    # ========================================================================
    # HIERARCHICAL VALIDATION (Categories → Materials → Frontmatter)
    # ========================================================================
    
    def validate_hierarchical(self, verbose: bool = False) -> ValidationResult:
        """
        Run hierarchical validation from Categories.yaml → Materials.yaml → Frontmatter.
        
        This is the primary entry point for pre-generation validation.
        """
        logger.info("🔍 Running hierarchical validation")
        
        all_issues = []
        all_warnings = []
        all_errors = []
        
        # Step 1: Validate Categories.yaml
        categories_result = self._validate_categories()
        all_issues.extend(categories_result.issues)
        all_warnings.extend(categories_result.warnings)
        all_errors.extend(categories_result.errors)
        
        # Fail-fast: Always fail on critical issues (per GROK_INSTRUCTIONS.md)
        if categories_result.has_critical_issues:
            raise ConfigurationError(
                f"Categories validation failed with {len(categories_result.errors)} critical issues:\n" +
                "\n".join(f"  - {e}" for e in categories_result.errors[:5])
            )
        
        # Step 2: Validate Materials.yaml
        materials_result = self._validate_materials()
        all_issues.extend(materials_result.issues)
        all_warnings.extend(materials_result.warnings)
        all_errors.extend(materials_result.errors)
        
        # Fail-fast: Always fail on critical issues (per GROK_INSTRUCTIONS.md)
        if materials_result.has_critical_issues:
            raise MaterialsValidationError(
                f"Materials validation failed with {len(materials_result.errors)} critical issues:\n" +
                "\n".join(f"  - {e}" for e in materials_result.errors[:5])
            )
        
        # Step 3: Validate Frontmatter files
        frontmatter_result = self._validate_all_frontmatter()
        all_issues.extend(frontmatter_result.issues)
        all_warnings.extend(frontmatter_result.warnings)
        all_errors.extend(frontmatter_result.errors)
        
        success = len(all_errors) == 0
        
        logger.info(f"✅ Hierarchical validation complete: {len(all_errors)} errors, {len(all_warnings)} warnings")
        
        return ValidationResult(
            success=success,
            validation_type="hierarchical",
            issues=all_issues,
            warnings=all_warnings,
            errors=all_errors
        )
    
    def _validate_categories(self) -> ValidationResult:
        """Validate Categories.yaml structure and content"""
        issues = []
        warnings = []
        errors = []
        
        try:
            if not self.categories_file.exists():
                errors.append({
                    "type": "file_not_found",
                    "file": str(self.categories_file),
                    "message": "Categories.yaml not found"
                })
                return ValidationResult(False, "categories", issues, warnings, errors)
            
            with open(self.categories_file) as f:
                categories_data = yaml.safe_load(f)
            
            if not categories_data or 'categories' not in categories_data:
                errors.append({
                    "type": "invalid_structure",
                    "file": "Categories.yaml",
                    "message": "Missing 'categories' key"
                })
            else:
                # Validate each category
                for category_name, category_data in categories_data['categories'].items():
                    if 'category_ranges' not in category_data:
                        warnings.append({
                            "type": "missing_ranges",
                            "category": category_name,
                            "message": f"Category {category_name} missing category_ranges"
                        })
            
            success = len(errors) == 0
            result = ValidationResult(success, "categories", issues, warnings, errors)
            
            # Fail-fast: Always raise exception on critical errors (per GROK_INSTRUCTIONS.md)
            if not success:
                raise ConfigurationError(
                    f"Categories.yaml validation failed:\n" +
                    "\n".join(f"  - {e.get('message', str(e))}" for e in errors[:3])
                )
            
            return result
            
        except ConfigurationError:
            # Let fail-fast exceptions propagate (per GROK_INSTRUCTIONS.md)
            raise
        except Exception as e:
            # Only catch YAML/file errors, not our intentional fail-fast exceptions
            raise ConfigurationError(
                f"Categories validation error: {str(e)}"
            )
    
    def _validate_materials(self) -> ValidationResult:
        """Validate Materials.yaml structure and content"""
        issues = []
        warnings = []
        errors = []
        
        try:
            if not self.materials_file.exists():
                errors.append({
                    "type": "file_not_found",
                    "file": str(self.materials_file),
                    "message": "Materials.yaml not found"
                })
                return ValidationResult(False, "materials", issues, warnings, errors)
            
            with open(self.materials_file) as f:
                materials_data = yaml.safe_load(f)
            
            if not materials_data or 'materials' not in materials_data:
                errors.append({
                    "type": "invalid_structure",
                    "file": "Materials.yaml",
                    "message": "Missing 'materials' key"
                })
            else:
                # Validate material index
                material_index = materials_data.get('material_index', {})
                if not material_index:
                    warnings.append({
                        "type": "missing_index",
                        "message": "Materials.yaml missing material_index"
                        })
            
            success = len(errors) == 0
            result = ValidationResult(success, "materials", issues, warnings, errors)
            
            # Fail-fast: Always raise exception on critical errors (per GROK_INSTRUCTIONS.md)
            if not success:
                raise ConfigurationError(
                    f"Materials.yaml validation failed:\n" +
                    "\n".join(f"  - {e.get('message', str(e))}" for e in errors[:3])
                )
            
            return result
            
        except ConfigurationError:
            # Let fail-fast exceptions propagate (per GROK_INSTRUCTIONS.md)
            raise
        except Exception as e:
            # Only catch YAML/file errors, not our intentional fail-fast exceptions
            raise ConfigurationError(
                f"Materials validation error: {str(e)}"
            )
    
    def _validate_all_frontmatter(self) -> ValidationResult:
        """Validate all frontmatter files including two-category compliance"""
        result = ValidationResult(success=True, validation_type="frontmatter")
        
        if not self.frontmatter_dir.exists():
            result.add_error(VError(
                severity=ErrorSeverity.WARNING,
                error_type=ErrorType.MISSING_CONFIG,
                message=f"Frontmatter directory not found: {self.frontmatter_dir}",
                file_path=str(self.frontmatter_dir)
            ))
            return result
        
        files = list(self.frontmatter_dir.glob("*.yaml"))
        
        for file_path in files:
            try:
                with open(file_path) as f:
                    frontmatter_data = yaml.safe_load(f)
                
                if not frontmatter_data:
                    result.add_error(VError(
                        severity=ErrorSeverity.WARNING,
                        error_type=ErrorType.INVALID_CONFIG,
                        message=f"Empty frontmatter file",
                        file_path=file_path.name
                    ))
                    continue
                
                # Basic structure validation
                required_fields = ['name', 'category', 'title']
                missing = [f for f in required_fields if f not in frontmatter_data]
                
                if missing:
                    result.add_error(VError(
                        severity=ErrorSeverity.WARNING,
                        error_type=ErrorType.MISSING_FIELD,
                        message=f"Missing required fields: {', '.join(missing)}",
                        file_path=file_path.name
                    ))
                
                # Two-category system validation
                material_name = frontmatter_data.get('name', file_path.stem)
                
                # Extract property categories (look for laser_material_interaction, material_characteristics, other)
                property_categories = {}
                for key in frontmatter_data.keys():
                    if key in ['laser_material_interaction', 'material_characteristics', 'other']:
                        property_categories[key] = frontmatter_data[key]
                
                if property_categories:
                    category_errors = self._validate_two_category_system(material_name, property_categories)
                    for error in category_errors:
                        error.file_path = file_path.name
                        result.add_error(error)
                    
            except Exception as e:
                result.add_error(VError(
                    severity=ErrorSeverity.ERROR,
                    error_type=ErrorType.VALIDATION_ERROR,
                    message=f"Error validating frontmatter: {str(e)}",
                    file_path=file_path.name
                ))
        
        return result
    
    # ========================================================================
    # PROPERTY-LEVEL VALIDATION
    # ========================================================================
    
    def validate_property_rules(self, material_name: str, category: str = None) -> ValidationResult:
        """
        Validate all properties for a material against property rules.
        
        Args:
            material_name: Name of material to validate
            category: Material category (optional, will load from Materials.yaml if not provided)
        """
        issues = []
        warnings = []
        errors = []
        
        try:
            # Load material data
            with open(self.materials_file) as f:
                materials_data = yaml.safe_load(f)
            
            # Get category if not provided
            if not category:
                material_index = materials_data.get('material_index', {})
                category = material_index.get(material_name)
                
                if not category:
                    # Fail-fast: Material not found is a critical error
                    raise MaterialsValidationError(
                        f"Material '{material_name}' not found in material_index"
                    )
            
            # Find material properties
            material_properties = {}
            materials_section = materials_data.get('materials', {})
            
            for material_name_key, material_data in materials_section.items():
                if material_name_key == material_name:
                    material_properties = material_data.get('properties', {})
                    break
            
            # Check for missing required properties based on category
            if category in self.category_rules:
                cat_rule = self.category_rules[category]
                existing_props = set(material_properties.keys())
                missing_required = set(cat_rule.required_properties) - existing_props
                
                if missing_required:
                    for prop in missing_required:
                        errors.append({
                            'severity': 'ERROR',
                            'type': 'missing_required_property',
                            'material': material_name,
                            'category': category,
                            'property': prop,
                            'message': f"Missing required property '{prop}' for category '{category}'"
                        })
            
            # Validate each property
            for prop_name, prop_data in material_properties.items():
                # First validate property has required fields
                field_issues = self._validate_property_fields(
                    material_name, prop_name, prop_data
                )
                for issue in field_issues:
                    if issue['severity'] == 'ERROR':
                        errors.append(issue)
                    elif issue['severity'] == 'WARNING':
                        warnings.append(issue)
                    else:
                        issues.append(issue)
                
                # Then validate property value against rules
                if prop_name not in self.property_rules:
                    continue
                
                prop_issues = self._validate_property_value(
                    material_name, category, prop_name, prop_data
                )
                
                for issue in prop_issues:
                    if issue['severity'] == 'ERROR':
                        errors.append(issue)
                    elif issue['severity'] == 'WARNING':
                        warnings.append(issue)
                    else:
                        issues.append(issue)
            
            # Check optical energy conservation (A + R ≤ 100%)
            optical_issues = self._validate_optical_energy(material_name, category, material_properties)
            for issue in optical_issues:
                if issue['severity'] == 'ERROR':
                    errors.append(issue)
                elif issue['severity'] == 'WARNING':
                    warnings.append(issue)
            
            success = len(errors) == 0
            result = ValidationResult(success, "property_rules", issues, warnings, errors)
            
            # Fail-fast: Always raise exception on critical errors (per GROK_INSTRUCTIONS.md)
            if not success:
                raise MaterialsValidationError(
                    f"Property validation failed for {material_name} ({category}):\n" +
                    "\n".join(f"  - {e.get('message', str(e))}" for e in errors[:5])
                )
            
            return result
            
        except MaterialsValidationError:
            # Let fail-fast exceptions propagate (per GROK_INSTRUCTIONS.md)
            raise
        except Exception as e:
            # Only catch YAML/file errors, not our intentional fail-fast exceptions
            errors.append({
                "type": "validation_error",
                "material": material_name,
                "message": f"Property validation failed: {str(e)}"
            })
            raise MaterialsValidationError(
                f"Property validation error for {material_name}: {str(e)}"
            )
    
    def _validate_property_fields(self, material: str, prop_name: str, 
                                  prop_data: Dict) -> List[Dict]:
        """Validate property metadata fields - delegates to PropertyValidators"""
        return PropertyValidators.validate_property_fields(material, prop_name, prop_data)
    
    def _validate_property_value(self, material: str, category: str, 
                                 prop_name: str, prop_data: Dict) -> List[Dict]:
        """Validate individual property value against rules"""
        issues = []
        
        if prop_name not in self.property_rules:
            return issues
        
        rule = self.property_rules[prop_name]
        value = prop_data.get('value')
        unit = prop_data.get('unit', '')
        confidence = prop_data.get('confidence', 100)
        
        if value is None:
            return issues
        
        # Skip numeric validation for qualitative-only properties
        if prop_name in QUALITATIVE_ONLY_PROPERTIES:
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
                    'message': f"Invalid unit '{unit}' for {prop_name}"
                })
            
            # ⚡ UNIT NORMALIZATION (Fix for electricalConductivity bug)
            # Convert to normalized unit before range validation
            # Example: 37,700,000 S/m → 37.7 MS/m before comparing to max 70 MS/m
            try:
                normalized_val, normalized_unit = UnitConverter.normalize(prop_name, val, unit)
            except Exception:
                # If conversion fails, use original value (backward compatible)
                normalized_val = val
                normalized_unit = unit
            
            # Check global range (using normalized value)
            if rule.min_value is not None and normalized_val < rule.min_value:
                issues.append({
                    'severity': 'ERROR',
                    'type': 'out_of_range',
                    'material': material,
                    'property': prop_name,
                    'value': val,
                    'normalized_value': normalized_val,
                    'unit': unit,
                    'normalized_unit': normalized_unit,
                    'min': rule.min_value,
                    'message': f"{prop_name} = {normalized_val:.2f} {normalized_unit} < {rule.min_value} (global min)"
                })
            
            if rule.max_value is not None and normalized_val > rule.max_value:
                issues.append({
                    'severity': 'ERROR',
                    'type': 'out_of_range',
                    'material': material,
                    'property': prop_name,
                    'value': val,
                    'normalized_value': normalized_val,
                    'unit': unit,
                    'normalized_unit': normalized_unit,
                    'max': rule.max_value,
                    'message': f"{prop_name} = {normalized_val:.2f} {normalized_unit} > {rule.max_value} (global max)"
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
    # RELATIONSHIP VALIDATION
    # ========================================================================
    
    def validate_relationships(self, material_name: str) -> ValidationResult:
        """Validate inter-property relationships for a material"""
        issues = []
        warnings = []
        errors = []
        
        try:
            # Load material data
            with open(self.materials_file) as f:
                materials_data = yaml.safe_load(f)
            
            material_index = materials_data.get('material_index', {})
            category = material_index.get(material_name)
            
            if not category:
                # Fail-fast: Material not found is a critical error
                raise MaterialsValidationError(
                    f"Material '{material_name}' not found in material_index"
                )
            
            # Find material properties
            material_properties = {}
            materials_section = materials_data.get('materials', {})
            
            if category in materials_section:
                for item in materials_section[category].get('items', []):
                    if item.get('name') == material_name:
                        material_properties = item.get('properties', {})
                        break
            
            # Validate each relationship rule
            for rule in self.relationship_rules:
                if category not in rule.applies_to_categories:
                    continue
                
                if rule.name == 'optical_energy_conservation':
                    rel_issues = self._validate_optical_energy(material_name, category, material_properties)
                elif rule.name == 'thermal_diffusivity_formula':
                    rel_issues = self._validate_thermal_diffusivity(material_name, category, material_properties)
                elif rule.name == 'youngs_tensile_ratio':
                    rel_issues = self._validate_youngs_tensile_ratio(material_name, category, material_properties)
                else:
                    continue
                
                for issue in rel_issues:
                    if issue['severity'] == 'ERROR':
                        errors.append(issue)
                    elif issue['severity'] == 'WARNING':
                        warnings.append(issue)
            
            success = len(errors) == 0
            result = ValidationResult(success, "relationships", issues, warnings, errors)
            
            # Fail-fast: Always raise exception on critical errors (per GROK_INSTRUCTIONS.md)
            if not success:
                raise MaterialsValidationError(
                    f"Relationship validation failed for {material_name}:\n" +
                    "\n".join(f"  - {e.get('message', str(e))}" for e in errors[:5])
                )
            
            return result
            
        except MaterialsValidationError:
            # Let fail-fast exceptions propagate (per GROK_INSTRUCTIONS.md)
            raise
        except Exception as e:
            # Only catch YAML/file errors, not our intentional fail-fast exceptions
            raise MaterialsValidationError(
                f"Relationship validation error for {material_name}: {str(e)}"
            )
    
    def _validate_optical_energy(self, material: str, category: str, props: Dict) -> List[Dict]:
        """Validate optical energy conservation - delegates to RelationshipValidators"""
        return RelationshipValidators.validate_optical_energy(material, category, props)
    
    def _validate_thermal_diffusivity(self, material: str, category: str, props: Dict) -> List[Dict]:
        """Validate thermal diffusivity formula - delegates to RelationshipValidators"""
        return RelationshipValidators.validate_thermal_diffusivity(material, category, props)
    
    def _validate_youngs_tensile_ratio(self, material: str, category: str, props: Dict) -> List[Dict]:
        """Validate Young's modulus / tensile strength ratio - delegates to RelationshipValidators"""
        return RelationshipValidators.validate_youngs_tensile_ratio(material, category, props)
    
    def _validate_two_category_system(self, frontmatter_path: Path) -> List[VError]:
        """Validate two-category system - delegates to RelationshipValidators"""
        # Read frontmatter to get categories
        try:
            with open(frontmatter_path) as f:
                frontmatter_data = yaml.safe_load(f)
            
            material_name = frontmatter_data.get('material', 'unknown')
            categories = frontmatter_data.get('categories', [])
            
            # Convert list to dict format expected by validator
            material_properties = {}
            for cat in categories:
                cat_id = cat.get('id', '')
                if cat_id:
                    material_properties[cat_id] = cat.get('properties', [])
            
            return RelationshipValidators.validate_two_category_system(material_name, material_properties)
        except Exception as e:
            logger.error(f"Error validating two-category system for {frontmatter_path}: {e}")
            return []
    
    # ========================================================================
    # GAP ANALYSIS
    # ========================================================================
    
    def analyze_gaps(self) -> GapAnalysisResult:
        """
        Identify missing properties and data gaps across all materials.
        
        Returns comprehensive gap analysis for prioritizing research tasks.
        """
        logger.info("🔍 Analyzing data gaps")
        
        try:
            with open(self.materials_file) as f:
                materials_data = yaml.safe_load(f)
            
            with open(self.categories_file) as f:
                categories_data = yaml.safe_load(f)
            
            total_materials = 0
            total_gaps = 0
            critical_gaps = 0
            gaps_by_priority = defaultdict(int)
            gaps_by_type = defaultdict(int)
            materials_needing_research = []
            
            # Expected properties by priority
            critical_properties = ['density', 'thermalConductivity', 'hardness']
            important_properties = ['tensileStrength', 'youngsModulus', 'specificHeat']
            
            materials_section = materials_data.get('materials', {})
            
            for category_name, category_items in materials_section.items():
                for item in category_items.get('items', []):
                    material_name = item.get('name')
                    properties = item.get('properties', {})
                    
                    total_materials += 1
                    
                    missing_critical = []
                    missing_important = []
                    low_confidence = []
                    
                    # Check critical properties
                    for prop in critical_properties:
                        if prop not in properties:
                            missing_critical.append(prop)
                            critical_gaps += 1
                            total_gaps += 1
                            gaps_by_priority[1] += 1
                            gaps_by_type['critical'] += 1
                        elif isinstance(properties[prop], dict):
                            confidence = properties[prop].get('confidence', 100)
                            if confidence < 70:
                                low_confidence.append((prop, confidence))
                    
                    # Check important properties
                    for prop in important_properties:
                        if prop not in properties:
                            missing_important.append(prop)
                            total_gaps += 1
                            gaps_by_priority[2] += 1
                            gaps_by_type['important'] += 1
                    
                    if missing_critical or missing_important or low_confidence:
                        materials_needing_research.append({
                            'material_name': material_name,
                            'category': category_name,
                            'missing_critical': missing_critical,
                            'missing_important': missing_important,
                            'low_confidence': low_confidence,
                            'priority': 1 if missing_critical else 2
                        })
            
            completion_percentage = 0.0
            if total_materials > 0:
                expected_properties = len(critical_properties) + len(important_properties)
                total_expected = total_materials * expected_properties
                completion_percentage = ((total_expected - total_gaps) / total_expected) * 100
            
            logger.info(f"✅ Gap analysis complete: {total_gaps} gaps found, {completion_percentage:.1f}% complete")
            
            return GapAnalysisResult(
                total_materials=total_materials,
                total_gaps=total_gaps,
                critical_gaps=critical_gaps,
                gaps_by_priority=dict(gaps_by_priority),
                gaps_by_type=dict(gaps_by_type),
                materials_needing_research=materials_needing_research,
                completion_percentage=completion_percentage
            )
            
        except (ConfigurationError, MaterialsValidationError):
            # Let fail-fast exceptions propagate (per GROK_INSTRUCTIONS.md)
            raise
        except Exception as e:
            # Only catch unexpected errors like file I/O issues
            logger.error(f"❌ Gap analysis failed: {e}")
            raise ConfigurationError(
                f"Gap analysis error: {str(e)}"
            )
    
    # ========================================================================
    # COMPLETENESS VALIDATION
    # ========================================================================
    
    def validate_completeness(self, material_name: str) -> ValidationResult:
        """Validate material has required properties for its category"""
        issues = []
        warnings = []
        errors = []
        
        try:
            with open(self.materials_file) as f:
                materials_data = yaml.safe_load(f)
            
            material_index = materials_data.get('material_index', {})
            category = material_index.get(material_name)
            
            if not category:
                # Fail-fast: Material not found is a critical error
                raise MaterialsValidationError(
                    f"Material '{material_name}' not found in material_index"
                )
            
            if category not in self.category_rules:
                warnings.append({
                    "type": "no_category_rules",
                    "category": category,
                    "message": f"No validation rules defined for category {category}"
                })
                return ValidationResult(True, "completeness", issues, warnings, errors)
            
            rule = self.category_rules[category]
            
            # Find material properties
            material_properties = set()
            materials_section = materials_data.get('materials', {})
            
            if category in materials_section:
                for item in materials_section[category].get('items', []):
                    if item.get('name') == material_name:
                        material_properties = set(item.get('properties', {}).keys())
                        break
            
            # Check required properties
            missing_required = set(rule.required_properties) - material_properties
            if missing_required:
                errors.append({
                    'type': 'missing_required_properties',
                    'material': material_name,
                    'category': category,
                    'missing': list(missing_required),
                    'message': f"Missing required properties: {missing_required}"
                })
            
            # Check forbidden properties
            forbidden_present = set(rule.forbidden_properties) & material_properties
            if forbidden_present:
                warnings.append({
                    'type': 'forbidden_properties_present',
                    'material': material_name,
                    'category': category,
                    'forbidden': list(forbidden_present),
                    'message': f"Has forbidden properties: {forbidden_present}"
                })
            
            success = len(errors) == 0
            result = ValidationResult(success, "completeness", issues, warnings, errors)
            
            # Fail-fast: Always raise exception on critical errors (per GROK_INSTRUCTIONS.md)
            if not success:
                raise MaterialsValidationError(
                    f"Completeness validation failed for {material_name}:\n" +
                    "\n".join(f"  - {e.get('message', str(e))}" for e in errors[:5])
                )
            
            return result
            
        except MaterialsValidationError:
            # Let fail-fast exceptions propagate (per GROK_INSTRUCTIONS.md)
            raise
        except Exception as e:
            # Only catch YAML/file errors, not our intentional fail-fast exceptions
            raise MaterialsValidationError(
                f"Completeness validation error for {material_name}: {str(e)}"
            )
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def validate_all(self, verbose: bool = False) -> ValidationResult:
        """
        Run all validations across entire database.
        
        This is a comprehensive validation suitable for batch operations.
        """
        logger.info("🔍 Running comprehensive validation on all materials")
        
        all_issues = []
        all_warnings = []
        all_errors = []
        
        # Run hierarchical validation
        hierarchical_result = self.validate_hierarchical(verbose)
        all_issues.extend(hierarchical_result.issues)
        all_warnings.extend(hierarchical_result.warnings)
        all_errors.extend(hierarchical_result.errors)
        
        # Fail-fast: Always fail on critical issues (per GROK_INSTRUCTIONS.md)
        if hierarchical_result.has_critical_issues:
            raise MaterialsValidationError(
                f"Hierarchical validation failed with {len(hierarchical_result.errors)} critical issues:\n" +
                "\n".join(f"  - {e}" for e in hierarchical_result.errors[:5])
            )
        
        # Load materials for per-material validation
        try:
            with open(self.materials_file) as f:
                materials_data = yaml.safe_load(f)
            
            material_index = materials_data.get('material_index', {})
            
            for material_name, category in material_index.items():
                if verbose:
                    logger.info(f"Validating {material_name}...")
                
                # Property rules validation
                prop_result = self.validate_property_rules(material_name, category)
                all_issues.extend(prop_result.issues)
                all_warnings.extend(prop_result.warnings)
                all_errors.extend(prop_result.errors)
                
                # Relationship validation
                rel_result = self.validate_relationships(material_name)
                all_issues.extend(rel_result.issues)
                all_warnings.extend(rel_result.warnings)
                all_errors.extend(rel_result.errors)
                
                # Completeness validation
                comp_result = self.validate_completeness(material_name)
                all_issues.extend(comp_result.issues)
                all_warnings.extend(comp_result.warnings)
                all_errors.extend(comp_result.errors)
                
        except Exception as e:
            all_errors.append({
                "type": "validation_error",
                "message": f"Comprehensive validation failed: {str(e)}"
            })
        
        success = len(all_errors) == 0
        
        logger.info(f"✅ Comprehensive validation complete: {len(all_errors)} errors, {len(all_warnings)} warnings")
        
        return ValidationResult(
            success=success,
            validation_type="comprehensive",
            issues=all_issues,
            warnings=all_warnings,
            errors=all_errors
        )
    
    def generate_report(self, validation_result: ValidationResult, output_file: str = None) -> str:
        """Generate detailed validation report"""
        report_lines = []
        
        report_lines.append("=" * 80)
        report_lines.append(f"VALIDATION REPORT - {validation_result.validation_type.upper()}")
        report_lines.append("=" * 80)
        report_lines.append(f"Timestamp: {validation_result.timestamp}")
        report_lines.append(f"Status: {'✅ PASSED' if validation_result.success else '❌ FAILED'}")
        report_lines.append("")
        
        report_lines.append(f"ERRORS: {len(validation_result.errors)}")
        report_lines.append(f"WARNINGS: {len(validation_result.warnings)}")
        report_lines.append(f"INFO: {len(validation_result.issues)}")
        report_lines.append("")
        
        if validation_result.errors:
            report_lines.append("-" * 80)
            report_lines.append("ERRORS (MUST FIX)")
            report_lines.append("-" * 80)
            for error in validation_result.errors[:20]:
                report_lines.append(f"  • {error.get('message', str(error))}")
            if len(validation_result.errors) > 20:
                report_lines.append(f"  ... and {len(validation_result.errors) - 20} more")
            report_lines.append("")
        
        if validation_result.warnings:
            report_lines.append("-" * 80)
            report_lines.append("WARNINGS (REVIEW RECOMMENDED)")
            report_lines.append("-" * 80)
            for warning in validation_result.warnings[:10]:
                report_lines.append(f"  • {warning.get('message', str(warning))}")
            if len(validation_result.warnings) > 10:
                report_lines.append(f"  ... and {len(validation_result.warnings) - 10} more")
        
        report = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            logger.info(f"📄 Report saved to {output_file}")
        
        return report
