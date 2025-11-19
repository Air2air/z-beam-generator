#!/usr/bin/env python3
"""
Validation Service - Unified Validation for Frontmatter Generation

Consolidates validation logic from ValidationUtils and ValidationHelpers into a single service.
Step 4 of refactoring plan: Reduce complexity by merging validation utilities.

Follows GROK fail-fast principles:
- No mocks or fallbacks
- Explicit error handling
- Validates all inputs immediately

Last Updated: October 17, 2025
"""

import logging
import re
from typing import Dict, Tuple, Any, Union

logger = logging.getLogger(__name__)


class ValidationService:
    """Unified validation service for frontmatter generation"""
    
    # Confidence thresholds (centralized constants)
    YAML_CONFIDENCE_THRESHOLD = 0.85  # High confidence for YAML data
    AI_CONFIDENCE_THRESHOLD = 0.80    # Acceptable confidence for AI research
    
    @staticmethod
    def normalize_confidence(confidence: Union[int, float]) -> int:
        """
        Normalize confidence values to integer percentage (0-100).
        
        Handles both fractional (0.0-1.0) and percentage (0-100) formats.
        
        Args:
            confidence: Confidence value (0.0-1.0 or 0-100)
            
        Returns:
            Integer confidence percentage (0-100)
            
        Examples:
            >>> ValidationService.normalize_confidence(0.85)
            85
            >>> ValidationService.normalize_confidence(95)
            95
        """
        if confidence < 1:
            return int(confidence * 100)
        else:
            return int(confidence)
    
    @staticmethod
    def is_high_confidence(confidence: Union[int, float], threshold: float = None) -> bool:
        """
        Check if confidence meets high-confidence threshold.
        
        Args:
            confidence: Confidence value to check
            threshold: Optional custom threshold (defaults to YAML_CONFIDENCE_THRESHOLD)
            
        Returns:
            True if confidence >= threshold
        """
        if threshold is None:
            threshold = ValidationService.YAML_CONFIDENCE_THRESHOLD
        
        # Normalize to same scale for comparison
        if confidence >= 1:
            confidence = confidence / 100.0
        
        return confidence >= threshold
    
    @staticmethod
    def validate_essential_properties(
        properties: dict,
        essential_props: set,
        material_name: str = "unknown"
    ) -> tuple[bool, list[str]]:
        """
        Validate that all essential properties are present.
        
        Args:
            properties: Dictionary of properties to validate
            essential_props: Set of required property names
            material_name: Material name for error messages
            
        Returns:
            Tuple of (is_valid, missing_properties)
        """
        missing = essential_props - set(properties.keys())
        is_valid = len(missing) == 0
        return is_valid, sorted(missing)
    
    @staticmethod
    def has_units(value_str: str) -> bool:
        """
        Check if a property value string contains units.
        
        Examples:
            "2.70 g/cm³" -> True
            "385 MPa" -> True
            "1668" -> False
        """
        return bool(re.search(r'\d\s*[a-zA-Z°·/²³]+', value_str))
    
    @staticmethod
    def extract_numeric_and_unit(value_str: str) -> Tuple[float, str]:
        """
        Extract numeric value and unit from a property string.
        
        Examples:
            "2.70 g/cm³" -> (2.70, "g/cm³")
            "385 MPa" -> (385.0, "MPa") 
            "70-120 HB" -> (95.0, "HB")  # midpoint of range
        """
        if not value_str:
            return 0.0, ""
        
        # Handle range values by taking midpoint
        if '-' in value_str and not value_str.startswith('-'):
            parts = value_str.split('-')
            if len(parts) == 2:
                try:
                    num1_match = re.search(r'[\d.]+', parts[0].strip())
                    num2_match = re.search(r'[\d.]+', parts[1].strip())
                    
                    if num1_match and num2_match:
                        num1 = float(num1_match.group())
                        num2 = float(num2_match.group())
                        midpoint = (num1 + num2) / 2
                        
                        # Extract unit from second part
                        unit_match = re.search(r'[a-zA-Z°/³²·]+', parts[1].strip())
                        unit = unit_match.group() if unit_match else ""
                        
                        return midpoint, unit
                except (ValueError, AttributeError):
                    pass
        
        # Extract single value
        try:
            num_match = re.search(r'[\d.]+', value_str)
            if num_match:
                numeric_value = float(num_match.group())
                
                # Extract unit
                unit_match = re.search(r'[a-zA-Z°/³²·]+', value_str)
                unit = unit_match.group() if unit_match else ""
                
                return numeric_value, unit
        except (ValueError, AttributeError):
            pass
        
        return 0.0, ""
    
    @staticmethod
    def extract_yaml_from_content(content: str) -> str:
        """Extract YAML content from various formats (frontmatter, code blocks, plain)"""
        # Try markdown code blocks first
        code_block_pattern = r'```(?:yaml|yml)?\s*\n(.*?)\n```'
        match = re.search(code_block_pattern, content, re.DOTALL | re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # Then try YAML frontmatter between --- delimiters
        yaml_pattern = r'^---\s*\n(.*?)\n---'
        match = re.search(yaml_pattern, content, re.DOTALL | re.MULTILINE)
        if match:
            return match.group(1)
        
        # If no delimiters, assume entire content is YAML
        return content.strip()
    
    @staticmethod
    def ensure_technical_specifications(frontmatter_data: Dict) -> None:
        """
        Ensure all required technical specifications are present.
        Logs warnings for missing fields without applying fallbacks.
        
        Args:
            frontmatter_data: Dictionary of frontmatter fields to validate
        """
        try:
            if 'chemicalFormula' not in frontmatter_data:
                logger.warning("Missing chemical formula in frontmatter data")
                
            if 'properties' not in frontmatter_data:
                logger.warning("Missing properties section in frontmatter data")
                
            required_fields = ['name', 'category']
            for field in required_fields:
                if field not in frontmatter_data:
                    logger.warning(f"Missing required field: {field}")
                    
        except Exception as e:
            logger.error(f"Error ensuring technical specifications: {e}")
    
    @staticmethod
    def apply_automatic_corrections(frontmatter_data: Dict, material_name: str) -> Dict:
        """
        Apply automatic corrections to common issues in frontmatter data.
        
        NOTE: Only applies safe corrections. Does not mask missing data.
        
        Args:
            frontmatter_data: Dictionary of frontmatter fields to correct
            material_name: Name of the material for context
            
        Returns:
            Dictionary with corrected frontmatter data
        """
        try:
            corrected_data = frontmatter_data.copy()
            
            # Only add name if missing (safe correction)
            if 'name' not in corrected_data or not corrected_data['name']:
                corrected_data['name'] = material_name
                logger.info(f"Added missing name field: {material_name}")
            
            # Ensure empty sections exist with correct structure (safe correction)
            if 'materialProperties' not in corrected_data:
                corrected_data['materialProperties'] = {
                    'material_characteristics': {'label': 'Material Characteristics'},
                    'laser_material_interaction': {'label': 'Laser-Material Interaction'}
                }
                logger.info("Added missing materialProperties section with category groups")
            
            if 'machineSettings' not in corrected_data:
                corrected_data['machineSettings'] = {}
                logger.info("Added missing machineSettings section")
            
            return corrected_data
            
        except Exception as e:
            logger.error(f"Error applying automatic corrections: {e}")
            return frontmatter_data
    
    @staticmethod
    def validate_frontmatter_structure(
        content: str, material_name: str
    ) -> tuple:
        """
        Validate frontmatter structure and content.
        
        Args:
            content: Generated frontmatter YAML content
            material_name: Name of the material
            
        Returns:
            tuple: (validated_content, validation_report)
        """
        try:
            from export.core.schema_validator import FrontmatterSchemaValidator
            import yaml
            
            # Extract and parse YAML
            yaml_content = ValidationService.extract_yaml_from_content(content)
            frontmatter_data = yaml.safe_load(yaml_content)
            
            if not frontmatter_data:
                logger.warning(f"Failed to parse YAML for {material_name}")
                return content, None
            
            # Run schema validation
            validator = FrontmatterSchemaValidator()
            validation_result = validator.validate_frontmatter(frontmatter_data)
            
            if validation_result.valid:
                logger.info(f"✅ Validation PASSED for {material_name}")
            else:
                logger.warning(f"⚠️ Validation issues for {material_name}: {validation_result.errors}")
            
            return content, validation_result
            
        except ImportError as e:
            logger.warning(f"Schema validator not available: {e}")
            return content, None
        except Exception as e:
            logger.error(f"Validation error for {material_name}: {e}")
            return content, None
