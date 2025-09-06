"""
AI Detection Configuration

This module contains all AI detection configuration settings that were previously
scattered throughout run.py. This provides a centralized location for managing
AI detection parameters and thresholds.

Configuration includes:
- Dynamic threshold calculations based on content type
- Service configuration for AI detection providers
- Winston.ai API settings and timeouts
- Iterative optimization parameters
- Content-type specific tuning
"""

import time as time_module
from typing import Any, Dict, Optional


def create_dynamic_ai_detection_config(
    content_type: str = "technical",
    author_country: str = None,
    content_length: int = None,
) -> dict:
    """
    Create dynamic AI detection configuration based on content characteristics and system performance.

    Args:
        content_type: Type of content ("technical", "marketing", "educational", "creative")
        author_country: Author country for style-specific tuning
        content_length: Expected content length for adaptive thresholds

    Returns:
        dict: Dynamic configuration optimized for the given parameters
    """

    # Base configuration with intelligent defaults
    config = {
        # Core AI Detection Thresholds - Adaptive based on content type
        "target_score": _calculate_optimal_target_score(content_type, author_country),
        "max_iterations": _calculate_optimal_iterations(content_type, content_length),
        "improvement_threshold": _calculate_improvement_threshold(content_type),
        "human_threshold": _calculate_human_threshold(content_type),
        # Content Length Thresholds - Adaptive based on content type
        "min_text_length_winston": _calculate_min_text_length(content_type),
        "short_content_threshold": _calculate_short_content_threshold(content_type),
        "min_content_length": _calculate_min_content_length(content_type),
        # Fallback Scores - Dynamic based on content characteristics
        "fallback_score_first_iteration": _calculate_fallback_score_first(content_type),
        "fallback_score_short_content": _calculate_fallback_score_short(content_type),
        "fallback_score_very_short": _calculate_fallback_score_very_short(content_type),
        "fallback_score_error": _calculate_fallback_score_error(content_type),
        # Status Update Configuration - Adaptive based on expected processing time
        "status_update_interval": _calculate_status_update_interval(content_length),
        "iteration_status_frequency": _calculate_iteration_status_frequency(
            content_type
        ),
        # Word Count Validation - Dynamic based on author and content type
        "word_count_tolerance": _calculate_word_count_tolerance(content_type),
        "word_count_limits": _calculate_word_count_limits(author_country),
        # API Timeouts and Limits - Adaptive based on content complexity
        "winston_timeout_cap": _calculate_winston_timeout(content_length),
        "max_tokens": _calculate_max_tokens(content_type, content_length),
        "retry_delay": _calculate_retry_delay(content_type),
        # Winston.ai Scoring Ranges - Content-type specific
        "winston_human_range": _calculate_winston_human_range(content_type),
        "winston_unclear_range": _calculate_winston_unclear_range(content_type),
        "winston_ai_range": _calculate_winston_ai_range(content_type),
        # Early Exit Conditions - Adaptive based on content type
        "min_iterations_before_exit": _calculate_min_iterations_before_exit(
            content_type
        ),
        "early_exit_score_threshold": _calculate_early_exit_threshold(content_type),
        # Configuration Optimization - Content-aware
        "deepseek_optimization_enabled": _should_enable_deepseek_optimization(
            content_type
        ),
        "config_backup_enabled": True,  # Always enable for safety
        # Service Configuration - Performance-optimized
        "service_cache_ttl_hours": _calculate_service_cache_ttl(content_type),
        "service_detection_threshold": _calculate_service_detection_threshold(
            content_type
        ),
        "service_confidence_threshold": _calculate_service_confidence_threshold(
            content_type
        ),
        "service_mock_score": _calculate_service_mock_score(content_type),
        "service_max_templates": _calculate_service_max_templates(content_type),
        "service_evolution_history_size": _calculate_service_evolution_history(
            content_type
        ),
        "service_max_history_size": _calculate_service_max_history(content_type),
        # Logging and Debugging - Adaptive based on content complexity
        "enable_detailed_logging": _should_enable_detailed_logging(content_type),
        "max_sentence_details": _calculate_max_sentence_details(content_type),
        # Metadata for tracking
        "config_metadata": {
            "content_type": content_type,
            "author_country": author_country,
            "content_length": content_length,
            "generated_at": time_module.time(),
            "logic_version": "2.0",
        },
    }

    return config


# ============================================================================
# DYNAMIC CALCULATION FUNCTIONS
# ============================================================================


def _calculate_optimal_target_score(
    content_type: str, author_country: str = None
) -> float:
    """Calculate optimal target score based on content type and author characteristics."""
    base_scores = {
        "technical": 50.0,  # Technical content is harder to make human-like
        "marketing": 45.0,  # Marketing content needs to be engaging
        "educational": 55.0,  # Educational content can be more structured
        "creative": 40.0,  # Creative content has more flexibility
    }

    score = base_scores.get(content_type, 50.0)

    # Adjust based on author country (cultural writing styles)
    if author_country:
        country_adjustments = {
            "italy": 2.0,  # Italian writing tends to be more expressive
            "taiwan": -1.0,  # Taiwanese technical writing is more formal
            "indonesia": 1.0,  # Indonesian writing can be more narrative
            "usa": 0.0,  # American writing is balanced
        }
        score += country_adjustments.get(author_country.lower(), 0.0)

    return max(30.0, min(70.0, score))  # Clamp between 30-70


def _calculate_optimal_iterations(content_type: str, content_length: int = None) -> int:
    """Calculate optimal number of iterations based on content complexity."""
    base_iterations = {
        "technical": 5,  # Technical content needs more iterations
        "marketing": 4,  # Marketing content needs refinement
        "educational": 3,  # Educational content is more straightforward
        "creative": 3,  # Creative content can be more flexible
    }

    iterations = base_iterations.get(content_type, 4)

    # Adjust based on content length
    if content_length:
        if content_length > 2000:
            iterations += 1  # Longer content needs more iterations
        elif content_length < 500:
            iterations = max(2, iterations - 1)  # Shorter content needs fewer

    return max(2, min(8, iterations))  # Clamp between 2-8


def _calculate_improvement_threshold(content_type: str) -> float:
    """Calculate improvement threshold based on content type."""
    thresholds = {
        "technical": 2.5,  # Technical content improvements are smaller
        "marketing": 3.0,  # Marketing content needs clear improvements
        "educational": 2.0,  # Educational content can have smaller increments
        "creative": 3.5,  # Creative content needs more significant changes
    }
    return thresholds.get(content_type, 3.0)


def _calculate_human_threshold(content_type: str) -> float:
    """Calculate human threshold based on content type."""
    thresholds = {
        "technical": 70.0,  # Technical content can be more structured
        "marketing": 75.0,  # Marketing content needs to be very human-like
        "educational": 72.0,  # Educational content balanced
        "creative": 68.0,  # Creative content more flexible
    }
    return thresholds.get(content_type, 75.0)


def _calculate_min_text_length(content_type: str) -> int:
    """Calculate minimum text length for Winston analysis."""
    lengths = {
        "technical": 250,  # Technical content needs more context
        "marketing": 200,  # Marketing content can be shorter
        "educational": 300,  # Educational content needs substantial text
        "creative": 150,  # Creative content can be more concise
    }
    return lengths.get(content_type, 250)


def _calculate_short_content_threshold(content_type: str) -> int:
    """Calculate threshold for short content handling."""
    thresholds = {
        "technical": 350,  # Technical content needs more words
        "marketing": 250,  # Marketing content can be punchier
        "educational": 400,  # Educational content needs explanation
        "creative": 200,  # Creative content can be brief
    }
    return thresholds.get(content_type, 350)


def _calculate_min_content_length(content_type: str) -> int:
    """Calculate minimum content length for validation."""
    lengths = {
        "technical": 120,  # Technical content minimum
        "marketing": 100,  # Marketing content minimum
        "educational": 150,  # Educational content minimum
        "creative": 80,  # Creative content minimum
    }
    return lengths.get(content_type, 120)


def _calculate_fallback_score_first(content_type: str) -> float:
    """Calculate fallback score for first iteration."""
    scores = {
        "technical": 55.0,  # Technical content starts lower
        "marketing": 50.0,  # Marketing content competitive
        "educational": 60.0,  # Educational content structured
        "creative": 45.0,  # Creative content flexible
    }
    return scores.get(content_type, 55.0)


def _calculate_fallback_score_short(content_type: str) -> float:
    """Calculate fallback score for short content."""
    scores = {
        "technical": 50.0,  # Technical short content
        "marketing": 45.0,  # Marketing short content
        "educational": 55.0,  # Educational short content
        "creative": 40.0,  # Creative short content
    }
    return scores.get(content_type, 50.0)


def _calculate_fallback_score_very_short(content_type: str) -> float:
    """Calculate fallback score for very short content."""
    scores = {
        "technical": 40.0,  # Technical very short
        "marketing": 35.0,  # Marketing very short
        "educational": 45.0,  # Educational very short
        "creative": 30.0,  # Creative very short
    }
    return scores.get(content_type, 40.0)


def _calculate_fallback_score_error(content_type: str) -> float:
    """Calculate fallback score when AI detection fails."""
    scores = {
        "technical": 45.0,  # Technical error fallback
        "marketing": 40.0,  # Marketing error fallback
        "educational": 50.0,  # Educational error fallback
        "creative": 35.0,  # Creative error fallback
    }
    return scores.get(content_type, 45.0)


def _calculate_status_update_interval(content_length: int = None) -> int:
    """Calculate status update interval based on expected processing time."""
    if content_length and content_length > 1500:
        return 15  # Longer content, less frequent updates
    elif content_length and content_length < 500:
        return 5  # Shorter content, more frequent updates
    else:
        return 10  # Default interval


def _calculate_iteration_status_frequency(content_type: str) -> int:
    """Calculate iteration status frequency."""
    frequencies = {
        "technical": 3,  # Technical content needs more status updates
        "marketing": 4,  # Marketing content moderate updates
        "educational": 5,  # Educational content fewer updates
        "creative": 4,  # Creative content moderate updates
    }
    return frequencies.get(content_type, 4)


def _calculate_word_count_tolerance(content_type: str) -> float:
    """Calculate word count tolerance."""
    tolerances = {
        "technical": 1.3,  # Technical content more flexible
        "marketing": 1.2,  # Marketing content moderate flexibility
        "educational": 1.4,  # Educational content needs structure
        "creative": 1.5,  # Creative content most flexible
    }
    return tolerances.get(content_type, 1.3)


def _calculate_word_count_limits(author_country: str = None) -> dict:
    """Calculate word count limits based on author country."""
    base_limits = {
        "taiwan": {"max": 380, "target_range": "340-380"},
        "italy": {"max": 450, "target_range": "400-450"},
        "indonesia": {"max": 400, "target_range": "350-400"},
        "usa": {"max": 320, "target_range": "280-320"},
    }

    if author_country and author_country.lower() in base_limits:
        return base_limits[author_country.lower()]

    # Default limits if country not specified
    return {"max": 350, "target_range": "300-350"}


def _calculate_winston_timeout(content_length: int = None) -> int:
    """Calculate Winston timeout based on content length."""
    if content_length and content_length > 1000:
        return 20  # Longer content needs more time
    else:
        return 15  # Default timeout


def _calculate_max_tokens(content_type: str, content_length: int = None) -> int:
    """Calculate max tokens based on content type and length."""
    base_tokens = {
        "technical": 2500,  # Technical content needs more tokens
        "marketing": 2000,  # Marketing content moderate tokens
        "educational": 3000,  # Educational content needs explanation
        "creative": 2000,  # Creative content flexible
    }

    tokens = base_tokens.get(content_type, 2500)

    # Adjust based on content length
    if content_length and content_length > 1500:
        tokens = int(tokens * 1.2)  # Increase for longer content

    return min(tokens, 4000)  # Cap at 4000


def _calculate_retry_delay(content_type: str) -> float:
    """Calculate retry delay based on content type."""
    delays = {
        "technical": 0.5,  # Technical content standard delay
        "marketing": 0.3,  # Marketing content faster retry
        "educational": 0.7,  # Educational content more conservative
        "creative": 0.4,  # Creative content moderate delay
    }
    return delays.get(content_type, 0.5)


def _calculate_winston_human_range(content_type: str) -> tuple:
    """Calculate Winston human range based on content type."""
    ranges = {
        "technical": (65, 100),  # Technical content harder to make human-like
        "marketing": (60, 100),  # Marketing content more flexible
        "educational": (70, 100),  # Educational content structured
        "creative": (55, 100),  # Creative content most flexible
    }
    return ranges.get(content_type, (65, 100))


def _calculate_winston_unclear_range(content_type: str) -> tuple:
    """Calculate Winston unclear range based on content type."""
    ranges = {
        "technical": (35, 65),  # Technical content wider unclear range
        "marketing": (30, 60),  # Marketing content competitive
        "educational": (40, 70),  # Educational content structured
        "creative": (25, 55),  # Creative content flexible
    }
    return ranges.get(content_type, (30, 65))


def _calculate_winston_ai_range(content_type: str) -> tuple:
    """Calculate Winston AI range based on content type."""
    ranges = {
        "technical": (0, 35),  # Technical content wider AI range
        "marketing": (0, 30),  # Marketing content competitive
        "educational": (0, 40),  # Educational content structured
        "creative": (0, 25),  # Creative content flexible
    }
    return ranges.get(content_type, (0, 35))


def _calculate_min_iterations_before_exit(content_type: str) -> int:
    """Calculate minimum iterations before allowing early exit."""
    iterations = {
        "technical": 4,  # Technical content needs more attempts
        "marketing": 3,  # Marketing content moderate
        "educational": 2,  # Educational content can exit earlier
        "creative": 3,  # Creative content moderate
    }
    return iterations.get(content_type, 3)


def _calculate_early_exit_threshold(content_type: str) -> int:
    """Calculate early exit threshold."""
    thresholds = {
        "technical": 12,  # Technical content needs higher threshold
        "marketing": 10,  # Marketing content moderate
        "educational": 8,  # Educational content can exit earlier
        "creative": 8,  # Creative content flexible
    }
    return thresholds.get(content_type, 10)


def _should_enable_deepseek_optimization(content_type: str) -> bool:
    """Determine if DeepSeek optimization should be enabled."""
    return content_type in [
        "technical",
        "educational",
    ]  # Most beneficial for these types


def _calculate_service_cache_ttl(content_type: str) -> int:
    """Calculate service cache TTL."""
    ttls = {
        "technical": 2,  # Technical content changes less frequently
        "marketing": 1,  # Marketing content changes more often
        "educational": 3,  # Educational content stable
        "creative": 1,  # Creative content dynamic
    }
    return ttls.get(content_type, 1)


def _calculate_service_detection_threshold(content_type: str) -> float:
    """Calculate service detection threshold."""
    thresholds = {
        "technical": 0.75,  # Technical content stricter
        "marketing": 0.65,  # Marketing content moderate
        "educational": 0.8,  # Educational content strictest
        "creative": 0.6,  # Creative content lenient
    }
    return thresholds.get(content_type, 0.7)


def _calculate_service_confidence_threshold(content_type: str) -> float:
    """Calculate service confidence threshold."""
    thresholds = {
        "technical": 0.85,  # Technical content needs high confidence
        "marketing": 0.75,  # Marketing content moderate
        "educational": 0.9,  # Educational content highest confidence
        "creative": 0.7,  # Creative content flexible
    }
    return thresholds.get(content_type, 0.8)


def _calculate_service_mock_score(content_type: str) -> float:
    """Calculate service mock score."""
    scores = {
        "technical": 0.25,  # Technical content lower mock score
        "marketing": 0.35,  # Marketing content higher
        "educational": 0.2,  # Educational content lowest
        "creative": 0.4,  # Creative content highest
    }
    return scores.get(content_type, 0.3)


def _calculate_service_max_templates(content_type: str) -> int:
    """Calculate service max templates."""
    templates = {
        "technical": 8,  # Technical content fewer templates
        "marketing": 12,  # Marketing content more templates
        "educational": 6,  # Educational content structured
        "creative": 15,  # Creative content most templates
    }
    return templates.get(content_type, 10)


def _calculate_service_evolution_history(content_type: str) -> int:
    """Calculate service evolution history size."""
    histories = {
        "technical": 40,  # Technical content moderate history
        "marketing": 60,  # Marketing content larger history
        "educational": 30,  # Educational content smaller history
        "creative": 70,  # Creative content largest history
    }
    return histories.get(content_type, 50)


def _calculate_service_max_history(content_type: str) -> int:
    """Calculate service max history size."""
    histories = {
        "technical": 15,  # Technical content moderate
        "marketing": 25,  # Marketing content larger
        "educational": 12,  # Educational content smaller
        "creative": 30,  # Creative content largest
    }
    return histories.get(content_type, 20)


def _should_enable_detailed_logging(content_type: str) -> bool:
    """Determine if detailed logging should be enabled."""
    return content_type in ["technical", "educational"]  # Most complex content types


def _calculate_max_sentence_details(content_type: str) -> int:
    """Calculate max sentence details."""
    details = {
        "technical": 6,  # Technical content more details
        "marketing": 4,  # Marketing content moderate
        "educational": 7,  # Educational content most details
        "creative": 3,  # Creative content fewer details
    }
    return details.get(content_type, 5)


# ============================================================================
# LEGACY STATIC CONFIG (for backward compatibility)
# ============================================================================


# Create default dynamic config for backward compatibility
def get_default_ai_detection_config() -> dict:
    """Get default AI detection configuration for backward compatibility."""
    return create_dynamic_ai_detection_config(
        content_type="technical", author_country="usa", content_length=1000
    )


# Global instance for backward compatibility
AI_DETECTION_CONFIG = get_default_ai_detection_config()
