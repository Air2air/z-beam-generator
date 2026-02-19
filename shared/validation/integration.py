#!/usr/bin/env python3
"""
Content Validation Integration Module

Provides easy integration of ContentValidationService into component generators.
Simple API for FAQ, Caption, and Subtitle generators to validate their output.
"""

import logging
from typing import Any, Dict, Optional

from shared.validation.content_validator import (
    ContentValidationResult,
    ContentValidationService,
)

logger = logging.getLogger(__name__)


def validate_generated_content(
    content: Any,
    component_type: str,
    material_name: str,
    author_info: Dict[str, str],
    voice_profile: Optional[Dict[str, Any]] = None,
    log_report: bool = True
) -> ContentValidationResult:
    """
    Validate generated content with centralized validation service.
    
    Simple integration point for component generators.
    
    Args:
        content: Generated content (varies by component):
            - FAQ: dict with 'questions' list
            Validates:
            - Caption: dict with 'before' and 'after'
            - Subtitle: str or dict with 'subtitle'
        component_type: 'faq', 'micro', or 'subtitle'
        material_name: Material name
        author_info: Dict with 'name' and 'country' keys
        voice_profile: Optional voice profile from VoiceOrchestrator
        log_report: Whether to log validation report
        
    Returns:
        ContentValidationResult with all dimension scores
        
    Example:
        ```python
        # In FAQ generator
        result = validate_generated_content(
            content={'questions': faq_items},
            component_type='faq',
            material_name='Stainless Steel',
            author_info={'name': 'Todd Dunning', 'country': 'United States'},
            voice_profile=voice.profile
        )
        
        if not result.success:
            logger.warning(f"Validation issues: {result.critical_issues}")
        ```
    """
    validator = ContentValidationService()

    if not isinstance(author_info, dict):
        raise RuntimeError("CONFIGURATION ERROR: author_info must be a dictionary with required keys 'name' and 'country'")
    if 'name' not in author_info or 'country' not in author_info:
        raise RuntimeError("CONFIGURATION ERROR: author_info missing required keys 'name' and/or 'country'")
    if not isinstance(author_info['name'], str) or not author_info['name'].strip():
        raise RuntimeError("CONFIGURATION ERROR: author_info['name'] must be a non-empty string")
    if not isinstance(author_info['country'], str) or not author_info['country'].strip():
        raise RuntimeError("CONFIGURATION ERROR: author_info['country'] must be a non-empty string")
    
    # Normalize content format
    if isinstance(content, str):
        content_dict = {'subtitle': content}
    elif not isinstance(content, dict):
        logger.warning(f"Unexpected content type: {type(content)}")
        content_dict = {'raw': str(content)}
    else:
        content_dict = content
    
    # Validate
    result = validator.validate_content(
        content=content_dict,
        component_type=component_type,
        material_name=material_name,
        author_name=author_info['name'],
        author_country=author_info['country'],
        voice_profile=voice_profile
    )
    
    # Log report if requested
    if log_report:
        report = validator.generate_validation_report(result)
        logger.info(f"\n{report}")
    
    return result


def get_validation_summary(result: ContentValidationResult) -> str:
    """
    Get brief validation summary for logging.
    
    Args:
        result: ContentValidationResult from validation
        
    Returns:
        Brief summary string
        
    Example:
        "✅ PASSED (Score: 85.3/100, Grade: B)"
        "⚠️  FAILED (Score: 62.1/100, Grade: D) - 2 critical issues"
    """
    status = "✅ PASSED" if result.success else "⚠️  FAILED"
    summary = f"{status} (Score: {result.overall_score:.1f}/100, Grade: {result.grade})"
    
    if result.critical_issues:
        summary += f" - {len(result.critical_issues)} critical issue(s)"
    elif result.warnings:
        summary += f" - {len(result.warnings)} warning(s)"
    
    return summary


def get_dimension_scores_dict(result: ContentValidationResult) -> Dict[str, float]:
    """
    Extract dimension scores as dictionary.
    
    Args:
        result: ContentValidationResult from validation
        
    Returns:
        Dict mapping dimension names to scores
        
    Example:
        {
            'overall': 85.3,
            'author_voice': 88.2,
            'variation': 82.5,
            'human_characteristics': 84.0,
            'ai_avoidance': 86.1
        }
    """
    return {
        'overall': result.overall_score,
        'author_voice': result.author_voice.overall_score,
        'variation': result.variation.overall_score,
        'human_characteristics': result.human_characteristics.overall_score,
        'ai_avoidance': result.ai_avoidance.overall_score
    }


def should_regenerate(result: ContentValidationResult, strict_mode: bool = False) -> bool:
    """
    Determine if content should be regenerated based on validation results.
    
    Args:
        result: ContentValidationResult from validation
        strict_mode: If True, use stricter criteria (target scores instead of minimums)
        
    Returns:
        True if content should be regenerated, False otherwise
        
    Example:
        ```python
        if should_regenerate(result, strict_mode=True):
            logger.warning("Quality below target - regenerating...")
            # regenerate content
        ```
    """
    from shared.validation.content_validator import PERSONA_THRESHOLDS

    if result.author_country not in PERSONA_THRESHOLDS:
        raise RuntimeError(
            f"CONFIGURATION ERROR: Missing persona thresholds for author country '{result.author_country}'"
        )

    thresholds = PERSONA_THRESHOLDS[result.author_country]
    if 'target_score' not in thresholds or 'min_score' not in thresholds:
        raise RuntimeError(
            f"CONFIGURATION ERROR: Persona thresholds for '{result.author_country}' missing required keys 'target_score' and/or 'min_score'"
        )
    
    if strict_mode:
        target = thresholds['target_score']
        return result.overall_score < target
    else:
        minimum = thresholds['min_score']
        return result.overall_score < minimum or not result.success
