#!/usr/bin/env python3
"""
Comprehensive Exception Handling for Frontmatter Generation

Ensures normalized fields are always generated, even when errors occur.
Implements fail-safe mechanisms, field validation, and recovery strategies.

Key principles:
- Never fail completely - always return valid frontmatter structure
- Provide fallback values for critical fields
- Log all exceptions for debugging while maintaining operation
- Validate field normalization at multiple stages
- Implement progressive fallback strategies
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class FieldValidationError(Exception):
    """Raised when field validation fails"""
    pass


class NormalizationError(Exception):
    """Raised when field normalization fails"""
    pass


class FallbackLevel(Enum):
    """Levels of fallback strategies"""
    PRIMARY = "primary"      # Use original data
    SECONDARY = "secondary"  # Use enhanced/processed data
    TERTIARY = "tertiary"   # Use category defaults
    EMERGENCY = "emergency"  # Use minimal valid structure


@dataclass
class FieldValidationResult:
    """Result of field validation"""
    is_valid: bool
    field_name: str
    value: Any
    error_message: Optional[str] = None
    fallback_used: Optional[str] = None


class FrontmatterExceptionHandler:
    """Comprehensive exception handling for frontmatter generation"""
    
    def __init__(self):
        self.fallback_cache = {}
        self.validation_errors = []
        self.normalization_stats = {
            'fields_processed': 0,
            'fields_normalized': 0,
            'fallbacks_used': 0,
            'errors_handled': 0
        }
    
    def generate_with_exception_handling(self, 
                                       material_name: str,
                                       generator_func: callable,
                                       **kwargs) -> Dict[str, Any]:
        """
        Generate frontmatter with comprehensive exception handling
        
        Args:
            material_name: Name of material
            generator_func: Original generation function
            **kwargs: Additional parameters
            
        Returns:
            Dict with normalized frontmatter, guaranteed to be valid
        """
        try:
            # Attempt primary generation
            logger.info(f"Attempting primary generation for {material_name}")
            frontmatter = generator_func(material_name, **kwargs)
            
            # Validate and normalize the result
            normalized_frontmatter = self._validate_and_normalize_structure(
                frontmatter, material_name, FallbackLevel.PRIMARY
            )
            
            logger.info(f"Primary generation successful for {material_name}")
            return normalized_frontmatter
            
        except Exception as primary_error:
            logger.warning(f"Primary generation failed for {material_name}: {primary_error}")
            self.normalization_stats['errors_handled'] += 1
            
            # Attempt progressive fallback strategies
            return self._execute_fallback_strategy(material_name, primary_error, **kwargs)
    
    def _execute_fallback_strategy(self, 
                                 material_name: str, 
                                 primary_error: Exception,
                                 **kwargs) -> Dict[str, Any]:
        """Execute progressive fallback strategies"""
        
        fallback_strategies = [
            (FallbackLevel.SECONDARY, self._generate_with_partial_data),
            (FallbackLevel.TERTIARY, self._generate_from_category_defaults),
            (FallbackLevel.EMERGENCY, self._generate_minimal_structure)
        ]
        
        for level, strategy_func in fallback_strategies:
            try:
                logger.info(f"Attempting {level.value} fallback for {material_name}")
                frontmatter = strategy_func(material_name, **kwargs)
                
                # Validate and normalize
                normalized_frontmatter = self._validate_and_normalize_structure(
                    frontmatter, material_name, level
                )
                
                logger.warning(f"{level.value} fallback successful for {material_name}")
                self.normalization_stats['fallbacks_used'] += 1
                return normalized_frontmatter
                
            except Exception as fallback_error:
                logger.error(f"{level.value} fallback failed for {material_name}: {fallback_error}")
                continue
        
        # If all strategies fail, create emergency structure
        logger.error(f"All fallback strategies failed for {material_name}, creating emergency structure")
        return self._create_emergency_structure(material_name, primary_error)
    
    def _validate_and_normalize_structure(self, 
                                        frontmatter: Dict[str, Any],
                                        material_name: str,
                                        fallback_level: FallbackLevel) -> Dict[str, Any]:
        """Validate and normalize frontmatter structure"""
        
        if not isinstance(frontmatter, dict):
            raise FieldValidationError(f"Frontmatter must be a dictionary, got {type(frontmatter)}")
        
        normalized = {}
        
        # Required fields with their validation and normalization
        required_fields = {
            'name': self._normalize_name,
            'category': self._normalize_category,
            'complexity': self._normalize_complexity,
            'difficulty_score': self._normalize_difficulty_score,
            'author_id': self._normalize_author_id,
            'title': self._normalize_title,
            'headline': self._normalize_headline,
            'description': self._normalize_description,
            'keywords': self._normalize_keywords,
            'properties': self._normalize_properties,
            'machineSettings': self._normalize_machine_settings,
            'applications': self._normalize_applications,
            'compatibility': self._normalize_compatibility,
            'author_object': self._normalize_author_object
        }
        
        # Process each required field
        for field_name, normalizer_func in required_fields.items():
            try:
                self.normalization_stats['fields_processed'] += 1
                
                # Get field value with fallback
                field_value = frontmatter.get(field_name)
                
                # Validate and normalize the field
                validation_result = self._validate_field(field_name, field_value, material_name)
                
                if validation_result.is_valid:
                    normalized[field_name] = normalizer_func(
                        validation_result.value, material_name, fallback_level
                    )
                    self.normalization_stats['fields_normalized'] += 1
                else:
                    # Use fallback value
                    fallback_value = self._get_field_fallback(field_name, material_name, fallback_level)
                    normalized[field_name] = normalizer_func(
                        fallback_value, material_name, fallback_level
                    )
                    logger.warning(f"Used fallback for {field_name} in {material_name}: {validation_result.error_message}")
                    self.normalization_stats['fallbacks_used'] += 1
                    
            except Exception as field_error:
                logger.error(f"Error processing field {field_name} for {material_name}: {field_error}")
                # Emergency fallback for this field
                normalized[field_name] = self._get_emergency_field_value(field_name, material_name)
                self.normalization_stats['errors_handled'] += 1
        
        # Handle optional fields
        optional_fields = ['chemicalProperties', 'subcategory']
        for field_name in optional_fields:
            if field_name in frontmatter:
                try:
                    normalized[field_name] = self._normalize_optional_field(
                        field_name, frontmatter[field_name], material_name
                    )
                except Exception as e:
                    logger.warning(f"Error processing optional field {field_name}: {e}")
                    # Optional fields can be omitted if they fail
        
        # Final structure validation
        self._validate_final_structure(normalized, material_name)
        
        return normalized
    
    def _validate_field(self, field_name: str, value: Any, material_name: str) -> FieldValidationResult:
        """Validate individual field"""
        
        if value is None:
            return FieldValidationResult(
                is_valid=False,
                field_name=field_name,
                value=None,
                error_message=f"Field {field_name} is None"
            )
        
        # Field-specific validation
        validation_rules = {
            'name': lambda v: isinstance(v, str) and len(v) > 0,
            'category': lambda v: isinstance(v, str) and v in [
                'metal', 'ceramic', 'composite', 'semiconductor', 
                'glass', 'stone', 'wood', 'plastic', 'masonry'
            ],
            'complexity': lambda v: isinstance(v, str) and v in ['low', 'medium', 'high'],
            'difficulty_score': lambda v: isinstance(v, int) and 1 <= v <= 5,
            'author_id': lambda v: isinstance(v, int) and v > 0,
            'title': lambda v: isinstance(v, str) and len(v) > 0,
            'headline': lambda v: isinstance(v, str) and len(v) > 0,
            'description': lambda v: isinstance(v, str) and len(v) > 0,
            'keywords': lambda v: isinstance(v, (list, str)) and len(v) > 0,
            'properties': lambda v: isinstance(v, dict) and len(v) > 0,
            'machineSettings': lambda v: isinstance(v, dict) and len(v) > 0,
            'applications': lambda v: isinstance(v, list) and len(v) > 0,
            'compatibility': lambda v: isinstance(v, dict),
            'author_object': lambda v: isinstance(v, dict) and 'id' in v
        }
        
        validator = validation_rules.get(field_name, lambda v: True)
        
        try:
            is_valid = validator(value)
            return FieldValidationResult(
                is_valid=is_valid,
                field_name=field_name,
                value=value,
                error_message=None if is_valid else f"Validation failed for {field_name}"
            )
        except Exception as e:
            return FieldValidationResult(
                is_valid=False,
                field_name=field_name,
                value=value,
                error_message=f"Validation error for {field_name}: {e}"
            )
    
    def _get_field_fallback(self, field_name: str, material_name: str, level: FallbackLevel) -> Any:
        """Get fallback value for a field"""
        
        # Category-based fallbacks
        category_fallbacks = {
            'name': material_name,
            'category': 'material',  # Generic fallback
            'complexity': 'medium',
            'difficulty_score': 3,
            'author_id': 1,
            'title': f"Laser Cleaning {material_name}",
            'headline': f"Professional laser cleaning for {material_name.lower()}",
            'description': f"Technical overview of {material_name} laser cleaning applications",
            'keywords': [material_name.lower(), 'laser cleaning', 'surface treatment'],
            'properties': {'density': 1.0, 'densityUnit': 'g/cm³'},
            'machineSettings': {
                'powerRange': 100.0, 'powerRangeUnit': 'W',
                'wavelength': 1064.0, 'wavelengthUnit': 'nm'
            },
            'applications': [f'General {material_name.lower()} surface cleaning'],
            'compatibility': {
                'laser_types': ['Fiber lasers', 'Nd:YAG lasers'],
                'surface_treatments': ['General surface cleaning']
            },
            'author_object': {
                'id': 1, 'name': 'Default Author', 'sex': 'm',
                'title': 'Engineer', 'country': 'International',
                'expertise': 'Laser Cleaning', 'image': '/images/author/default.jpg'
            }
        }
        
        return category_fallbacks.get(field_name, f"default_{field_name}")
    
    def _normalize_name(self, value: Any, material_name: str, level: FallbackLevel) -> str:
        """Normalize name field"""
        if isinstance(value, str) and value.strip():
            return value.strip()
        return material_name
    
    def _normalize_category(self, value: Any, material_name: str, level: FallbackLevel) -> str:
        """Normalize category field"""
        valid_categories = ['metal', 'ceramic', 'composite', 'semiconductor', 
                          'glass', 'stone', 'wood', 'plastic', 'masonry']
        
        if isinstance(value, str) and value.lower() in valid_categories:
            return value.lower()
        
        # Intelligent category detection based on material name
        name_lower = material_name.lower()
        if any(metal in name_lower for metal in ['aluminum', 'steel', 'iron', 'copper', 'brass']):
            return 'metal'
        elif any(wood in name_lower for wood in ['oak', 'pine', 'maple', 'wood']):
            return 'wood'
        elif any(stone in name_lower for stone in ['granite', 'marble', 'stone', 'rock']):
            return 'stone'
        elif any(glass in name_lower for glass in ['glass', 'silicate']):
            return 'glass'
        else:
            return 'material'  # Safe fallback
    
    def _normalize_properties(self, value: Any, material_name: str, level: FallbackLevel) -> Dict:
        """Normalize properties with unit separation"""
        if not isinstance(value, dict):
            return {'density': 1.0, 'densityUnit': 'g/cm³'}
        
        normalized_props = {}
        
        # Ensure unit separation for all numeric properties
        for prop_key, prop_value in value.items():
            if prop_key.endswith('Unit') or prop_key.endswith('Min') or prop_key.endswith('Max'):
                normalized_props[prop_key] = prop_value
                continue
            
            try:
                # Extract numeric value and ensure unit field exists
                numeric_value = self._extract_numeric_only(prop_value)
                if numeric_value is not None:
                    normalized_props[prop_key] = numeric_value
                    
                    # Ensure corresponding unit field exists
                    unit_key = f"{prop_key}Unit"
                    if unit_key not in value:
                        # Provide default unit based on property type
                        default_units = {
                            'density': 'g/cm³',
                            'thermalConductivity': 'W/m·K',
                            'tensileStrength': 'MPa',
                            'youngsModulus': 'GPa',
                            'hardness': 'HV'
                        }
                        normalized_props[unit_key] = default_units.get(prop_key, 'unit')
                    else:
                        normalized_props[unit_key] = value[unit_key]
                else:
                    # Keep original value if can't extract numeric
                    normalized_props[prop_key] = prop_value
            except Exception as e:
                logger.warning(f"Error normalizing property {prop_key}: {e}")
                normalized_props[prop_key] = prop_value
        
        return normalized_props if normalized_props else {'density': 1.0, 'densityUnit': 'g/cm³'}
    
    def _extract_numeric_only(self, value):
        """Extract numeric value from mixed string/number"""
        if isinstance(value, (int, float)):
            return value
        
        if isinstance(value, str):
            import re
            match = re.match(r'^(-?\d+(?:\.\d+)?)', value.strip())
            if match:
                numeric_str = match.group(1)
                try:
                    return float(numeric_str) if '.' in numeric_str else int(numeric_str)
                except ValueError:
                    pass
        
        return None
    
    # Additional normalizer methods for other fields...
    def _normalize_complexity(self, value: Any, material_name: str, level: FallbackLevel) -> str:
        valid_values = ['low', 'medium', 'high']
        return value if value in valid_values else 'medium'
    
    def _normalize_difficulty_score(self, value: Any, material_name: str, level: FallbackLevel) -> int:
        if isinstance(value, int) and 1 <= value <= 5:
            return value
        return 3
    
    def _normalize_author_id(self, value: Any, material_name: str, level: FallbackLevel) -> int:
        if isinstance(value, int) and value > 0:
            return value
        return 1
    
    def _normalize_title(self, value: Any, material_name: str, level: FallbackLevel) -> str:
        if isinstance(value, str) and value.strip():
            return value.strip()
        return f"Laser Cleaning {material_name}"
    
    def _normalize_headline(self, value: Any, material_name: str, level: FallbackLevel) -> str:
        if isinstance(value, str) and value.strip():
            return value.strip()
        return f"Professional laser cleaning for {material_name.lower()}"
    
    def _normalize_description(self, value: Any, material_name: str, level: FallbackLevel) -> str:
        if isinstance(value, str) and value.strip():
            return value.strip()
        return f"Technical overview of {material_name} laser cleaning applications and parameters"
    
    def _normalize_keywords(self, value: Any, material_name: str, level: FallbackLevel) -> List[str]:
        if isinstance(value, list):
            return [str(kw).strip() for kw in value if str(kw).strip()]
        elif isinstance(value, str):
            return [kw.strip() for kw in value.split(',') if kw.strip()]
        return [material_name.lower(), 'laser cleaning', 'surface treatment']
    
    def _normalize_machine_settings(self, value: Any, material_name: str, level: FallbackLevel) -> Dict:
        if not isinstance(value, dict):
            return {
                'powerRange': 100.0, 'powerRangeUnit': 'W',
                'wavelength': 1064.0, 'wavelengthUnit': 'nm'
            }
        
        # Apply same unit separation logic as properties
        return self._normalize_properties(value, material_name, level)
    
    def _normalize_applications(self, value: Any, material_name: str, level: FallbackLevel) -> List[str]:
        if isinstance(value, list):
            return [str(app).strip() for app in value if str(app).strip()]
        return [f'General {material_name.lower()} surface cleaning']
    
    def _normalize_compatibility(self, value: Any, material_name: str, level: FallbackLevel) -> Dict:
        if isinstance(value, dict):
            return value
        return {
            'laser_types': ['Fiber lasers', 'Nd:YAG lasers'],
            'surface_treatments': ['General surface cleaning']
        }
    
    def _normalize_author_object(self, value: Any, material_name: str, level: FallbackLevel) -> Dict:
        if isinstance(value, dict) and 'id' in value:
            return value
        
        return {
            'id': 1, 'name': 'Default Author', 'sex': 'm',
            'title': 'Engineer', 'country': 'International',
            'expertise': 'Laser Cleaning', 'image': '/images/author/default.jpg'
        }
    
    def _normalize_optional_field(self, field_name: str, value: Any, material_name: str) -> Any:
        """Normalize optional fields"""
        if field_name == 'chemicalProperties':
            if isinstance(value, dict) and ('formula' in value or 'symbol' in value):
                return value
            return None  # Omit if invalid
        
        return value
    
    def _create_emergency_structure(self, material_name: str, error: Exception) -> Dict[str, Any]:
        """Create minimal valid structure when all else fails"""
        logger.critical(f"Creating emergency structure for {material_name} due to: {error}")
        
        return {
            'name': material_name,
            'category': 'material',
            'complexity': 'medium',
            'difficulty_score': 3,
            'author_id': 1,
            'title': f"Laser Cleaning {material_name}",
            'headline': f"Laser cleaning guide for {material_name.lower()}",
            'description': f"Basic laser cleaning information for {material_name}",
            'keywords': [material_name.lower(), 'laser cleaning'],
            'properties': {
                'density': 1.0,
                'densityUnit': 'g/cm³'
            },
            'machineSettings': {
                'powerRange': 100.0,
                'powerRangeUnit': 'W',
                'wavelength': 1064.0,
                'wavelengthUnit': 'nm'
            },
            'applications': [f'Basic {material_name.lower()} cleaning'],
            'compatibility': {
                'laser_types': ['General laser systems'],
                'surface_treatments': ['Basic cleaning']
            },
            'author_object': {
                'id': 1,
                'name': 'System Generated',
                'sex': 'm',
                'title': 'Automated System',
                'country': 'System',
                'expertise': 'Emergency Generation',
                'image': '/images/author/system.jpg'
            }
        }
    
    def _generate_with_partial_data(self, material_name: str, **kwargs) -> Dict[str, Any]:
        """Generate using partial data (secondary fallback)"""
        # Implementation would use available partial data
        pass
    
    def _generate_from_category_defaults(self, material_name: str, **kwargs) -> Dict[str, Any]:
        """Generate using category defaults (tertiary fallback)"""
        # Implementation would use category-based templates
        pass
    
    def _generate_minimal_structure(self, material_name: str, **kwargs) -> Dict[str, Any]:
        """Generate minimal valid structure (emergency fallback)"""
        return self._create_emergency_structure(material_name, Exception("Minimal structure fallback"))
    
    def _validate_final_structure(self, frontmatter: Dict[str, Any], material_name: str):
        """Final validation of complete structure"""
        required_fields = [
            'name', 'category', 'complexity', 'difficulty_score', 'author_id',
            'title', 'headline', 'description', 'keywords', 'properties',
            'machineSettings', 'applications', 'compatibility', 'author_object'
        ]
        
        missing_fields = [field for field in required_fields if field not in frontmatter]
        
        if missing_fields:
            raise FieldValidationError(
                f"Final validation failed for {material_name}. Missing fields: {missing_fields}"
            )
    
    def _get_emergency_field_value(self, field_name: str, material_name: str) -> Any:
        """Get emergency value when all else fails"""
        return self._get_field_fallback(field_name, material_name, FallbackLevel.EMERGENCY)
    
    def get_normalization_stats(self) -> Dict[str, int]:
        """Get normalization statistics"""
        return self.normalization_stats.copy()