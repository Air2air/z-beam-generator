"""
Fix Strategy Definitions

Standardized fix strategies for different failure patterns.
Each strategy is trackable, measurable, and learnable.

Similar to detection patterns, but for parameter adjustments.
"""

from typing import Dict, Any, List


# Standardized fix strategies with discrete IDs
FIX_STRATEGIES = {
    # UNIFORM FAILURE: All sentences terrible (avg < 20%)
    'uniform_increase_randomness': {
        'id': 'uniform_increase_randomness',
        'name': 'Increase Randomness Aggressively',
        'failure_types': ['uniform'],
        'temperature_adjustment': +0.15,
        'voice_adjustments': {
            'imperfection_tolerance': +0.20,
            'colloquialism_frequency': +0.15,
            'sentence_rhythm_variation': +0.10
        },
        'enrichment_adjustments': {
            'fact_density': -0.15
        },
        'rationale': 'All sentences AI-like → Inject chaos and imperfection',
        'priority': 1,  # Try this first
        'min_attempt': 2  # Don't use on first attempt
    },
    
    'uniform_reduce_technical': {
        'id': 'uniform_reduce_technical',
        'name': 'Reduce Technical Language',
        'failure_types': ['uniform'],
        'temperature_adjustment': +0.10,
        'voice_adjustments': {
            'technical_language_intensity': -0.30,
            'jargon_removal': +0.15,
            'conversational_tone': +0.20,
            'personality_intensity': +0.15
        },
        'enrichment_adjustments': {
            'technical_detail_level': -0.20
        },
        'rationale': 'Try human-like conversational language instead of randomness',
        'priority': 2,  # Alternative strategy
        'min_attempt': 4  # Try after randomness approach fails
    },
    
    'uniform_increase_author_voice': {
        'id': 'uniform_increase_author_voice',
        'name': 'Increase Author Voice',
        'failure_types': ['uniform'],
        'temperature_adjustment': +0.12,
        'voice_adjustments': {
            'author_voice_intensity': +0.25,
            'personality_intensity': +0.20,
            'emotional_tone': +0.15,
            'reader_address_rate': +0.10
        },
        'rationale': 'Add strong personality and voice to break AI patterns',
        'priority': 3,  # Third alternative
        'min_attempt': 5  # Last resort
    },
    
    # BORDERLINE: Close to passing (avg 30-50%)
    'borderline_fine_tune': {
        'id': 'borderline_fine_tune',
        'name': 'Fine-Tune Parameters',
        'failure_types': ['borderline'],
        'temperature_adjustment': -0.03,
        'voice_adjustments': {
            'sentence_rhythm_variation': +0.10,
            'structural_predictability': +0.05
        },
        'enrichment_adjustments': {},
        'rationale': 'Close to passing → Small tweaks only',
        'priority': 1,
        'min_attempt': 2
    },
    
    # PARTIAL: Mixed quality (some good, some bad)
    'partial_moderate_boost': {
        'id': 'partial_moderate_boost',
        'name': 'Moderate Boost',
        'failure_types': ['partial'],
        'temperature_adjustment': +0.08,
        'voice_adjustments': {
            'reader_address_rate': +0.10,
            'imperfection_tolerance': +0.10
        },
        'enrichment_adjustments': {
            'context_depth': +0.10
        },
        'rationale': 'Some good sentences exist → Moderate changes to improve bad ones',
        'priority': 1,
        'min_attempt': 2
    },
    
    # POOR: Consistently poor (avg 20-30%)
    'poor_major_adjustment': {
        'id': 'poor_major_adjustment',
        'name': 'Major Adjustment',
        'failure_types': ['poor'],
        'temperature_adjustment': +0.12,
        'voice_adjustments': {
            'imperfection_tolerance': +0.15,
            'colloquialism_frequency': +0.12,
            'sentence_rhythm_variation': +0.10
        },
        'enrichment_adjustments': {
            'fact_density': -0.10
        },
        'rationale': 'Consistently poor quality → Need significant changes',
        'priority': 1,
        'min_attempt': 2
    }
}


def get_strategies_for_failure_type(failure_type: str, attempt: int) -> List[Dict[str, Any]]:
    """
    Get all applicable strategies for a failure type, ordered by priority.
    
    Args:
        failure_type: Type of failure (uniform, borderline, partial, poor)
        attempt: Current attempt number (1-based)
        
    Returns:
        List of strategies applicable to this failure, ordered by priority
    """
    applicable = []
    
    for strategy_id, strategy in FIX_STRATEGIES.items():
        if failure_type in strategy['failure_types']:
            if attempt >= strategy['min_attempt']:
                applicable.append(strategy)
    
    # Sort by priority (lower number = higher priority)
    applicable.sort(key=lambda s: s['priority'])
    
    return applicable


def get_strategy_by_id(strategy_id: str) -> Dict[str, Any]:
    """
    Get specific strategy by ID.
    
    Args:
        strategy_id: Strategy identifier
        
    Returns:
        Strategy dict or None if not found
    """
    return FIX_STRATEGIES.get(strategy_id)


def get_alternative_strategies(current_strategy_id: str, attempt: int) -> List[Dict[str, Any]]:
    """
    Get alternative strategies when current one keeps failing.
    
    Args:
        current_strategy_id: ID of strategy that's not working
        attempt: Current attempt number
        
    Returns:
        List of alternative strategies to try
    """
    current = FIX_STRATEGIES.get(current_strategy_id)
    if not current:
        return []
    
    failure_type = current['failure_types'][0]
    all_strategies = get_strategies_for_failure_type(failure_type, attempt)
    
    # Return strategies other than current one
    return [s for s in all_strategies if s['id'] != current_strategy_id]


# Default strategy selection order (can be overridden by learning)
DEFAULT_STRATEGY_ORDER = {
    'uniform': [
        'uniform_increase_randomness',
        'uniform_reduce_technical', 
        'uniform_increase_author_voice'
    ],
    'borderline': [
        'borderline_fine_tune'
    ],
    'partial': [
        'partial_moderate_boost'
    ],
    'poor': [
        'poor_major_adjustment'
    ]
}
