#!/usr/bin/env python3
"""
Content Validation Integration Module

Provides easy integration of ContentValidationService into component generators.
Simple API for FAQ, Caption, and Subtitle generators to validate their output.
"""

import logging
from typing import Dict, Any, Optional
from validation.content_validator import ContentValidationService, ContentValidationResult

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
            - Caption: dict with 'beforeText' and 'afterText'
            - Subtitle: str or dict with 'subtitle'
        component_type: 'faq', 'caption', or 'subtitle'
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
        author_name=author_info.get('name', 'Unknown'),
        author_country=author_info.get('country', 'Unknown'),
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
    from validation.content_validator import PERSONA_THRESHOLDS
    
    thresholds = PERSONA_THRESHOLDS.get(result.author_country, {})
    
    if strict_mode:
        target = thresholds.get('target_score', 80)
        return result.overall_score < target
    else:
        minimum = thresholds.get('min_score', 70)
        return result.overall_score < minimum or not result.success
