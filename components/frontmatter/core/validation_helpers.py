#!/usr/bin/env python3
"""
Validation Helpers

Provides validation helper functionality for frontmatter content including
YAML extraction, automatic corrections, and validation report management.
Extracted from the monolithic generator for better separation of concerns.
"""

import logging
import os
import re
import yaml
from typing import Dict, Tuple, Any, Optional

logger = logging.getLogger(__name__)


class ValidationHelpers:
    """Helper methods for frontmatter validation and correction"""

    @staticmethod
    def validate_and_enhance_content(
        content: str, 
        material_name: str, 
        material_data: dict, 
        api_client
    ) -> Tuple[str, Optional[Any]]:
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
            from components.frontmatter.comprehensive_validator import ComprehensiveFrontmatterValidator
            
            # Parse YAML content for validation
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
            if validation_report.has_critical_issues():
                logger.warning(f"⚠️ Critical validation issues found for {material_name}")
                corrected_content = ValidationHelpers.apply_automatic_corrections(
                    content, frontmatter_data, validation_report
                )
            
            # Log validation results
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
    def extract_yaml_from_content(content: str) -> str:
        """
        Extract YAML content between --- delimiters
        
        Args:
            content: Content string that may contain YAML frontmatter
            
        Returns:
            str: Extracted YAML content
        """
        # Match YAML frontmatter between --- delimiters
        yaml_pattern = r'^---\s*\n(.*?)\n---'
        match = re.search(yaml_pattern, content, re.DOTALL | re.MULTILINE)
        
        if match:
            return match.group(1)
        else:
            # If no delimiters, assume entire content is YAML
            return content.strip()

    @staticmethod
    def apply_automatic_corrections(
        content: str, 
        frontmatter_data: dict, 
        validation_report
    ) -> str:
        """
        Apply automatic corrections based on validation recommendations.
        
        This method implements smart corrections for common validation issues:
        - Fix missing required fields with sensible defaults
        - Correct obvious data type issues
        - Standardize format inconsistencies
        
        Args:
            content: Original content
            frontmatter_data: Parsed frontmatter data
            validation_report: Validation report with issues
            
        Returns:
            str: Corrected content
        """
        try:
            corrected_data = frontmatter_data.copy()
            corrections_applied = []
            
            # Apply corrections based on validation issues
            for result in validation_report.validation_results:
                if result.stage == "schema_structure":
                    for issue in result.issues:
                        if "Missing required field:" in issue:
                            field_name = issue.split(": ")[1]
                            corrected_data = ValidationHelpers.add_missing_field(corrected_data, field_name)
                            corrections_applied.append(f"Added missing field: {field_name}")
                            
            # Regenerate YAML if corrections were applied
            if corrections_applied:
                corrected_yaml = yaml.dump(corrected_data, default_flow_style=False, sort_keys=False)
                corrected_content = f"---\n{corrected_yaml}---"
                
                logger.info(f"Applied automatic corrections: {', '.join(corrections_applied)}")
                return corrected_content
            
            return content
            
        except Exception as e:
            logger.error(f"Error applying automatic corrections: {e}")
            return content

    @staticmethod
    def add_missing_field(data: dict, field_name: str) -> dict:
        """
        Add missing required field with sensible default
        
        Args:
            data: Dictionary to add field to
            field_name: Name of field to add
            
        Returns:
            dict: Updated dictionary with added field
        """
        defaults = {
            "description": "Technical overview of laser cleaning applications",
            "keywords": ["laser cleaning", "surface treatment", "industrial processing"],
            "category": "unknown",
            "author": "Technical Expert",
            "title": f"Laser Cleaning {data.get('name', 'Material')}",
            "headline": f"Technical guide for laser cleaning {data.get('name', 'material')}"
        }
        
        if field_name in defaults:
            data[field_name] = defaults[field_name]
        
        return data

    @staticmethod
    def save_validation_report(material_name: str, validation_report) -> None:
        """
        Save validation report for review and debugging
        
        Args:
            material_name: Name of the material being validated
            validation_report: Validation report to save
        """
        try:
            # Create validation reports directory
            reports_dir = "logs/validation_reports"
            os.makedirs(reports_dir, exist_ok=True)
            
            # Generate comprehensive report
            from components.frontmatter.comprehensive_validator import ComprehensiveFrontmatterValidator
            validator = ComprehensiveFrontmatterValidator()
            report_text = validator.generate_comprehensive_report(validation_report)
            
            # Save report file
            report_file = f"{reports_dir}/{material_name}_validation_report.md"
            with open(report_file, "w") as f:
                f.write(report_text)
                
            logger.info(f"📄 Validation report saved: {report_file}")
            
        except Exception as e:
            logger.error(f"Failed to save validation report: {e}")

    @staticmethod
    def ensure_technical_specifications(frontmatter_data: Dict) -> None:
        """
        Ensure technical specifications section exists and has proper structure
        
        Args:
            frontmatter_data: Dictionary to ensure has technical specifications
        """
        if "technicalSpecifications" not in frontmatter_data:
            frontmatter_data["technicalSpecifications"] = {}
        
        tech_specs = frontmatter_data["technicalSpecifications"]
        
        # Ensure key technical sections exist
        required_sections = {
            "materialProperties": {},
            "laserParameters": {},
            "processingGuidelines": {}
        }
        
        for section, default_value in required_sections.items():
            if section not in tech_specs:
                tech_specs[section] = default_value
                
        logger.debug("Ensured technical specifications structure")
