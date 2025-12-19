"""
Score Validation Decorator

Prevents score inversion bugs and ensures consistent score representation
across all generation workflows.

PROBLEM THIS SOLVES:
- Score inversions (displaying 0.5% when Winston returned 99.5% human)
- Inconsistent score ranges (0-1 vs 0-100)
- Missing validation that human_score + ai_score = 100%

USAGE:
    from shared.validation.score_validator import validate_scores
    
    @validate_scores
    def generate(self, identifier, component_type):
        ...
        return {
            'success': True,
            'human_score': 95.0,  # Will be validated as 0-100 range
            'ai_score': 0.05,     # Will be validated as 0-1 range
            ...
        }
"""

import functools
import logging
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)


class ScoreValidationError(ValueError):
    """Raised when score validation fails"""
    pass


def validate_scores(func: Callable) -> Callable:
    """
    Decorator ensuring score consistency across all return paths.
    
    Validates:
    - human_score: 0-100 range
    - ai_score: 0-1.0 range
    - Consistency: human_score + (ai_score * 100) ≈ 100
    - subjective_score: 0-10 range (if present)
    
    Raises:
        ScoreValidationError: If any validation fails
    
    Example:
        @validate_scores
        def generate(self, material, component):
            return {
                'success': True,
                'human_score': 95.0,
                'ai_score': 0.05
            }
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        # Only validate dict results with success field
        if not isinstance(result, dict):
            return result
        
        if 'success' not in result:
            return result
        
        # Validate human_score range (0-100)
        if 'human_score' in result:
            score = result['human_score']
            if not isinstance(score, (int, float)):
                raise ScoreValidationError(
                    f"human_score must be numeric, got {type(score).__name__} "
                    f"in {func.__name__}()"
                )
            
            if not (0 <= score <= 100):
                raise ScoreValidationError(
                    f"Invalid human_score: {score} (must be 0-100). "
                    f"Possible score inversion detected in {func.__name__}(). "
                    f"Check if you're returning ai_score instead of human_score."
                )
        
        # Validate ai_score range (0-1.0)
        if 'ai_score' in result:
            score = result['ai_score']
            if not isinstance(score, (int, float)):
                raise ScoreValidationError(
                    f"ai_score must be numeric, got {type(score).__name__} "
                    f"in {func.__name__}()"
                )
            
            if not (0 <= score <= 1.0):
                raise ScoreValidationError(
                    f"Invalid ai_score: {score} (must be 0-1.0). "
                    f"Check conversion logic in {func.__name__}()"
                )
        
        # Validate score consistency (inverse relationship)
        if 'human_score' in result and 'ai_score' in result:
            human = result['human_score']
            ai = result['ai_score']
            expected_ai = (100 - human) / 100.0
            
            # Allow 1% tolerance for rounding
            if abs(ai - expected_ai) > 0.01:
                raise ScoreValidationError(
                    f"Score mismatch in {func.__name__}(): "
                    f"human_score={human}% but ai_score={ai:.3f}. "
                    f"Expected ai_score={(100-human)/100:.3f}. "
                    f"These should be inverse: ai_score = (100 - human_score) / 100"
                )
        
        # Validate subjective_score range (0-10)
        if 'subjective_score' in result:
            score = result['subjective_score']
            if not isinstance(score, (int, float)):
                raise ScoreValidationError(
                    f"subjective_score must be numeric, got {type(score).__name__} "
                    f"in {func.__name__}()"
                )
            
            if not (0 <= score <= 10):
                raise ScoreValidationError(
                    f"Invalid subjective_score: {score} (must be 0-10). "
                    f"Check Grok evaluation parsing in {func.__name__}()"
                )
        
        # Validate overall_score (alias for subjective_score)
        if 'overall_score' in result:
            score = result['overall_score']
            if not isinstance(score, (int, float)):
                raise ScoreValidationError(
                    f"overall_score must be numeric, got {type(score).__name__} "
                    f"in {func.__name__}()"
                )
            
            if not (0 <= score <= 10):
                raise ScoreValidationError(
                    f"Invalid overall_score: {score} (must be 0-10). "
                    f"Check subjective evaluation logic in {func.__name__}()"
                )
        
        # Log validation success for debugging
        if logger.isEnabledFor(logging.DEBUG):
            scores_validated = []
            if 'human_score' in result:
                scores_validated.append(f"human={result['human_score']:.1f}%")
            if 'ai_score' in result:
                scores_validated.append(f"ai={result['ai_score']:.3f}")
            if 'subjective_score' in result:
                scores_validated.append(f"subjective={result['subjective_score']:.1f}/10")
            
            if scores_validated:
                logger.debug(
                    f"✅ Score validation passed in {func.__name__}(): "
                    f"{', '.join(scores_validated)}"
                )
        
        return result
    
    return wrapper


def validate_score_dict(scores: Dict[str, Any], context: str = "") -> None:
    """
    Validate a dictionary of scores without decorator.
    
    Useful for validating scores before returning from functions
    or when processing external data.
    
    Args:
        scores: Dictionary containing score fields
        context: Context string for error messages (e.g., "Winston API response")
    
    Raises:
        ScoreValidationError: If any validation fails
    
    Example:
        from shared.validation.score_validator import validate_score_dict
        
        winston_response = api.detect(text)
        validate_score_dict(winston_response, "Winston API response")
    """
    context_str = f" in {context}" if context else ""
    
    # Validate human_score
    if 'human_score' in scores:
        score = scores['human_score']
        if not isinstance(score, (int, float)):
            raise ScoreValidationError(
                f"human_score must be numeric{context_str}, "
                f"got {type(score).__name__}"
            )
        if not (0 <= score <= 100):
            raise ScoreValidationError(
                f"Invalid human_score: {score} (must be 0-100){context_str}"
            )
    
    # Validate ai_score
    if 'ai_score' in scores:
        score = scores['ai_score']
        if not isinstance(score, (int, float)):
            raise ScoreValidationError(
                f"ai_score must be numeric{context_str}, "
                f"got {type(score).__name__}"
            )
        if not (0 <= score <= 1.0):
            raise ScoreValidationError(
                f"Invalid ai_score: {score} (must be 0-1.0){context_str}"
            )
    
    # Validate consistency
    if 'human_score' in scores and 'ai_score' in scores:
        human = scores['human_score']
        ai = scores['ai_score']
        expected_ai = (100 - human) / 100.0
        
        if abs(ai - expected_ai) > 0.01:
            raise ScoreValidationError(
                f"Score mismatch{context_str}: "
                f"human_score={human}% but ai_score={ai:.3f}. "
                f"Expected ai_score={(100-human)/100:.3f}"
            )
    
    # Validate subjective scores
    for score_name in ['subjective_score', 'overall_score']:
        if score_name in scores:
            score = scores[score_name]
            if not isinstance(score, (int, float)):
                raise ScoreValidationError(
                    f"{score_name} must be numeric{context_str}, "
                    f"got {type(score).__name__}"
                )
            if not (0 <= score <= 10):
                raise ScoreValidationError(
                    f"Invalid {score_name}: {score} (must be 0-10){context_str}"
                )


def convert_ai_to_human_score(ai_score: float) -> float:
    """
    Convert AI score (0-1.0) to human score (0-100).
    
    Args:
        ai_score: AI detection score (0.0 = 100% human, 1.0 = 100% AI)
    
    Returns:
        Human score (0-100 scale)
    
    Raises:
        ValueError: If ai_score is out of range
    
    Example:
        human = convert_ai_to_human_score(0.05)  # Returns 95.0
    """
    if not (0 <= ai_score <= 1.0):
        raise ValueError(f"ai_score must be 0-1.0, got {ai_score}")
    
    return (1.0 - ai_score) * 100.0


def convert_human_to_ai_score(human_score: float) -> float:
    """
    Convert human score (0-100) to AI score (0-1.0).
    
    Args:
        human_score: Human detection score (0-100 scale)
    
    Returns:
        AI score (0.0-1.0 scale)
    
    Raises:
        ValueError: If human_score is out of range
    
    Example:
        ai = convert_human_to_ai_score(95.0)  # Returns 0.05
    """
    if not (0 <= human_score <= 100):
        raise ValueError(f"human_score must be 0-100, got {human_score}")
    
    return (100.0 - human_score) / 100.0
