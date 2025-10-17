#!/usr/bin/env python3
"""
Pipeline Integration - Validation and Quality Improvement

Provides real-time validation and improvement of generated content.
Integrates with Materials.yaml and Categories.yaml for data consistency.

UPDATED: Now uses consolidated service architecture.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Import consolidated services
from validation.services.pre_generation_service import PreGenerationValidationService
from research.services.ai_research_service import AIResearchEnrichmentService
from validation.services.post_generation_service import PostGenerationQualityService

logger = logging.getLogger(__name__)

# Initialize services globally (singleton pattern)
_pre_gen_service = None
_research_service = None
_quality_service = None


def get_pre_generation_service() -> PreGenerationValidationService:
    """Get or create pre-generation validation service"""
    global _pre_gen_service
    if _pre_gen_service is None:
        _pre_gen_service = PreGenerationValidationService()
    return _pre_gen_service


def get_research_service() -> AIResearchEnrichmentService:
    """Get or create AI research service"""
    global _research_service
    if _research_service is None:
        try:
            _research_service = AIResearchEnrichmentService(api_provider='deepseek')
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize research service: {e}")
            _research_service = None
    return _research_service


def get_quality_service() -> PostGenerationQualityService:
    """Get or create post-generation quality service"""
    global _quality_service
    if _quality_service is None:
        _quality_service = PostGenerationQualityService()
    return _quality_service


def validate_material_pre_generation(material_name: str) -> dict:
    """
    Validate material data before generation using consolidated service.
    
    Args:
        material_name: Name of material to validate
        
    Returns:
        dict with validation results
    """
    logger.info(f"🔍 Pre-generation validation for {material_name}")
    
    try:
        service = get_pre_generation_service()
        
        # Run property rules validation
        result = service.validate_property_rules(material_name)
        
        # Run relationship validation  
        rel_result = service.validate_relationships(material_name)
        
        # Run completeness validation
        comp_result = service.validate_completeness(material_name)
        
        # Combine results
        all_errors = result.errors + rel_result.errors + comp_result.errors
        all_warnings = result.warnings + rel_result.warnings + comp_result.warnings
        all_issues = result.issues + rel_result.issues + comp_result.issues
        
        validation_passed = len(all_errors) == 0
        
        return {
            "validation_passed": validation_passed,
            "material": material_name,
            "issues_detected": [issue.get('message', str(issue)) for issue in all_issues],
            "warnings": [warn.get('message', str(warn)) for warn in all_warnings],
            "errors": [err.get('message', str(err)) for err in all_errors]
        }
        
    except Exception as e:
        logger.error(f"❌ Pre-generation validation failed: {e}")
        return {
            "validation_passed": False,
            "material": material_name,
            "issues_detected": [],
            "warnings": [],
            "errors": [f"Validation error: {str(e)}"]
        }


def validate_and_improve_frontmatter(material_name: str, frontmatter_content: dict) -> dict:
    """
    Validate and improve generated frontmatter using consolidated service.
    
    Args:
        material_name: Name of material
        frontmatter_content: Generated frontmatter content as dict
        
    Returns:
        dict with validation/improvement results
    """
    logger.info(f"🔍 Post-generation validation for {material_name}")
    
    try:
        service = get_quality_service()
        
        # Validate schema
        schema_result = service.validate_schema(frontmatter_content, 'frontmatter', material_name)
        
        # Validate quality
        quality_result = service.validate_quality(frontmatter_content, 'frontmatter', material_name)
        
        # Check for improvements needed
        improvements_made = False
        improvements = []
        issues_detected = []
        
        if not schema_result.success:
            issues_detected.extend([err.get('message', str(err)) for err in schema_result.errors])
        
        if quality_result.quality_score and quality_result.quality_score.issues:
            issues_detected.extend(quality_result.quality_score.issues)
        
        # Check if tags field exists and has content
        if 'tags' in frontmatter_content:
            tags = frontmatter_content['tags']
            if isinstance(tags, list):
                if len(tags) < 4:
                    issues_detected.append(f"Insufficient tags ({len(tags)}, minimum 4)")
                elif len(tags) > 10:
                    issues_detected.append(f"Too many tags ({len(tags)}, maximum 10)")
        else:
            issues_detected.append("Missing tags field")
        
        validation_passed = len(issues_detected) == 0 and schema_result.success and quality_result.success
        
        return {
            "validation_passed": validation_passed,
            "validation_result": {
                "validation_passed": validation_passed,
                "issues_detected": issues_detected,
                "schema_valid": schema_result.success,
                "quality_score": quality_result.quality_score.overall_score if quality_result.quality_score else 0.0
            },
            "material": material_name,
            "improvements": improvements,
            "improvements_made": improvements_made,
            "improved_frontmatter": frontmatter_content
        }
        
    except Exception as e:
        return {
            "validation_passed": False,
            "validation_result": {  # Add this key for consistency
                "validation_passed": False,
                "issues_detected": issues_detected + [f"Validation error: {str(e)}"]
            },
            "material": material_name,
            "improvements": improvements,
            "improvements_made": False,
            "issues_detected": issues_detected,
            "errors": [f"Validation error: {str(e)}"]
        }


def validate_batch_generation(material_names: list) -> dict:
    """
    Validate a batch of materials before batch generation using consolidated service.
    
    Args:
        material_names: List of material names to validate
        
    Returns:
        dict with batch validation results
    """
    logger.info(f"🔍 Batch validation for {len(material_names)} materials")
    
    try:
        service = get_pre_generation_service()
        
        # Run gap analysis to identify materials needing research
        gap_result = service.analyze_gaps()
        
        errors = []
        warnings = []
        valid_materials = []
        invalid_materials = []
        
        for material_name in material_names:
            validation_result = validate_material_pre_generation(material_name)
            
            if validation_result["validation_passed"]:
                valid_materials.append(material_name)
            else:
                invalid_materials.append({
                    "material": material_name,
                    "errors": validation_result["errors"]
                })
                errors.extend(validation_result["errors"])
            
            if validation_result.get("warnings"):
                warnings.extend(validation_result["warnings"])
        
        logger.info(f"✅ Batch validation complete: {len(valid_materials)}/{len(material_names)} valid")
        
        return {
            "valid": len(invalid_materials) == 0,
            "total_materials": len(material_names),
            "valid_materials": len(valid_materials),
            "invalid_materials": len(invalid_materials),
            "data_completion": gap_result.completion_percentage,
            "critical_gaps": gap_result.critical_gaps,
            "errors": errors,
            "warnings": warnings,
            "materials": {
                "valid": valid_materials,
                "invalid": invalid_materials
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Batch validation failed: {e}")
        return {
            "valid": False,
            "total_materials": len(material_names),
            "valid_materials": 0,
            "invalid_materials": len(material_names),
            "errors": [f"Batch validation error: {str(e)}"],
            "warnings": []
        }
