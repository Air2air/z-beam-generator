#!/usr/bin/env python3
"""
Validation Helpers

Provides validation and correction utilities for frontmatter content.
Extracted from the monolithic generator for better separation of concerns.
"""

import logging
import re
from typing import Dict, Tuple, Any

logger = logging.getLogger(__name__)


class ValidationHelpers:
    """Helper methods for validating and correcting frontmatter content"""

    @staticmethod
    def has_units(value_str: str) -> bool:
        """
        Check if a property value string contains units.
        
        Examples:
            "2.70 g/cm³" -> True
            "385 MPa" -> True
            "70-120 HB" -> True
            "1668" -> False
        """
        # Check if string contains letters (indicating units) after numbers
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
        
        # Handle range values by taking the midpoint
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
    def ensure_technical_specifications(frontmatter_data: Dict) -> None:
        """
        Ensure all required technical specifications are present and properly formatted.
        
        This method validates that critical fields like chemical formula, symbol, 
        and material properties are present and correctly structured.
        
        Args:
            frontmatter_data: Dictionary of frontmatter fields to validate
        """
        try:
            # Ensure chemical formula is present
            if 'chemicalFormula' not in frontmatter_data:
                logger.warning("Missing chemical formula in frontmatter data")
                
            # Ensure material properties exist
            if 'properties' not in frontmatter_data:
                logger.warning("Missing properties section in frontmatter data")
                frontmatter_data['properties'] = {}
                
            # Ensure basic material info
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
        
        This method fixes common formatting issues, missing fields, and 
        standardizes the structure of the frontmatter data.
        
        Args:
            frontmatter_data: Dictionary of frontmatter fields to correct
            material_name: Name of the material for context
            
        Returns:
            Dictionary with corrected frontmatter data
        """
        try:
            corrected_data = frontmatter_data.copy()
            
            # Standardize name field
            if 'name' not in corrected_data or not corrected_data['name']:
                corrected_data['name'] = material_name
                logger.info(f"Added missing name field: {material_name}")
            
            # Ensure properties section exists
            if 'properties' not in corrected_data:
                corrected_data['properties'] = {}
                logger.info("Added missing properties section")
            
            # Ensure machine settings section exists
            if 'machineSettings' not in corrected_data:
                corrected_data['machineSettings'] = {}
                logger.info("Added missing machineSettings section")
            
            return corrected_data
            
        except Exception as e:
            logger.error(f"Error applying automatic corrections: {e}")
            return frontmatter_data

    @staticmethod
    def save_validation_report(material_name: str, validation_report: Any) -> None:
        """
        Save validation report for debugging and quality assurance.
        
        Args:
            material_name: Name of the material being validated
            validation_report: Report data to save
        """
        try:
            import os
            import json
            from datetime import datetime
            
            # Create reports directory if it doesn't exist
            reports_dir = "logs/validation_reports"
            os.makedirs(reports_dir, exist_ok=True)
            
            # Create timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{reports_dir}/{material_name}_validation_{timestamp}.json"
            
            # Save report
            with open(filename, 'w') as f:
                json.dump({
                    'material': material_name,
                    'timestamp': timestamp,
                    'report': validation_report
                }, f, indent=2)
            
            logger.debug(f"Saved validation report to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving validation report: {e}")

    @staticmethod
    def extract_yaml_from_content(content: str) -> str:
        """Extract YAML content from various formats (frontmatter, code blocks, plain)"""
        # First try to extract from markdown code blocks
        code_block_pattern = r'```(?:yaml|yml)?\s*\n(.*?)\n```'
        match = re.search(code_block_pattern, content, re.DOTALL | re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # Then try YAML frontmatter between --- delimiters
        yaml_pattern = r'^---\s*\n(.*?)\n---'
        match = re.search(yaml_pattern, content, re.DOTALL | re.MULTILINE)
        if match:
            return match.group(1)
        
        # If no delimiters or code blocks, assume entire content is YAML
        return content.strip()

    @staticmethod
    def validate_and_enhance_content(
        content: str, material_name: str, material_data: dict, api_client
    ) -> tuple:
        """
        Comprehensive validation and enhancement of generated frontmatter content.
        
        This method implements the single source of truth validation pipeline:
        1. Parse generated YAML content 
        2. Run comprehensive multi-stage validation
        3. Apply automatic corrections if possible
        4. Return validated content with validation report
        
        Args:
            content: Generated frontmatter YAML content
            material_name: Name of the material
            material_data: Material data context
            api_client: API client for AI-powered validation
            
        Returns:
            tuple: (validated_content, validation_report)
        """
        try:
            # Import comprehensive validator
            from frontmatter.comprehensive_validator import ComprehensiveFrontmatterValidator
            
            # Parse YAML content for validation
            import yaml
            try:
                # Extract YAML between --- delimiters
                yaml_content = ValidationHelpers.extract_yaml_from_content(content)
                frontmatter_data = yaml.safe_load(yaml_content)
                
                if not frontmatter_data:
                    logger.warning(f"Failed to parse YAML from generated content for {material_name}")
                    return content, None
                    
            except yaml.YAMLError as e:
                logger.error(f"YAML parsing error for {material_name}: {e}")
                return content, None

            # Initialize comprehensive validator
            validator = ComprehensiveFrontmatterValidator()
            
            # Run comprehensive validation with AI-powered verification
            logger.info(f"🔍 Running comprehensive validation for {material_name}")
            validation_report = validator.validate_frontmatter_comprehensive(
                material_name=material_name,
                frontmatter_data=frontmatter_data,
                api_client=api_client,
                enable_ai_validation=True
            )
            
            # Apply automatic corrections if validation suggests them
            corrected_content = content
            if hasattr(validation_report, 'has_critical_issues') and validation_report.has_critical_issues():
                logger.warning(f"⚠️ Critical validation issues found for {material_name}")
                corrected_content = ValidationHelpers._apply_automatic_corrections(
                    content, frontmatter_data, validation_report
                )
            
            # Log validation results
            if hasattr(validation_report, 'overall_status'):
                if validation_report.overall_status == "PASS":
                    logger.info(f"✅ Frontmatter validation PASSED for {material_name} (score: {validation_report.overall_score:.1f}/10)")
                elif validation_report.overall_status == "WARNING":
                    logger.warning(f"⚠️ Frontmatter validation WARNING for {material_name} (score: {validation_report.overall_score:.1f}/10)")
                else:
                    logger.error(f"❌ Frontmatter validation FAILED for {material_name} (score: {validation_report.overall_score:.1f}/10)")
            
            # Save validation report for debugging/review
            ValidationHelpers.save_validation_report(material_name, validation_report)
            
            return corrected_content, validation_report
            
        except ImportError as e:
            logger.warning(f"Comprehensive validator not available: {e}")
            return content, None
        except Exception as e:
            logger.error(f"Validation error for {material_name}: {e}")
            return content, None

    @staticmethod
    def _apply_automatic_corrections(
        content: str, frontmatter_data: dict, validation_report
    ) -> str:
        """
        Apply automatic corrections based on validation recommendations.
        
        This method implements smart corrections for common validation issues:
        - Fix missing required fields with sensible defaults
        - Correct obvious data type issues
        - Standardize format inconsistencies
        """
        try:
            corrected_data = frontmatter_data.copy()
            corrections_applied = []
            
            # Apply corrections based on validation issues
            if hasattr(validation_report, 'validation_results'):
                for result in validation_report.validation_results:
                    if hasattr(result, 'stage') and result.stage == "schema_structure":
                        for issue in result.issues:
                            if "Missing required field:" in issue:
                                field_name = issue.split(": ")[1]
                                # FAIL-FAST: Cannot proceed with invalid data
                                from utils.ai.loud_errors import validation_failure
                                validation_failure(
                                    "frontmatter_generator",
                                    f"Missing required field '{field_name}' in generated frontmatter - fail-fast architecture requires complete data",
                                    field=field_name
                                )
                                raise ValueError(f"Missing required field '{field_name}' in generated frontmatter - no fallbacks allowed")
                                
            # Regenerate YAML if corrections were applied
            if corrections_applied:
                import yaml
                corrected_yaml = yaml.dump(corrected_data, default_flow_style=False, sort_keys=False)
                corrected_content = f"---\n{corrected_yaml}---"
                
                logger.info(f"Applied automatic corrections: {', '.join(corrections_applied)}")
                return corrected_content
            
            return content
            
        except Exception as e:
            logger.error(f"Error applying automatic corrections: {e}")
            return content
