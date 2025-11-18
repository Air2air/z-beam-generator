"""
Parameter module package.

Provides modular parameter system with preset prompts.

CONSOLIDATION (Nov 18, 2025):
- Individual parameter files consolidated into category modules
- ai_detection/, voice/, variation/, technical/ subdirectories → 4 consolidated files
- Imports preserved via this __init__.py for zero breaking changes
"""

from processing.parameters.base import (
    BaseParameter,
    Scale10Parameter,
    Scale3Parameter,
    ParameterCategory,
    ParameterTier
)
from processing.parameters.registry import get_registry, ParameterRegistry

# Import all parameter classes from consolidated modules
from processing.parameters.ai_detection import (
    HumannessIntensity,
    AIAvoidanceIntensity
)
from processing.parameters.voice import (
    JargonRemoval,
    ProfessionalVoice,
    PersonalityIntensity,
    EmotionalIntensity,
    AuthorVoiceIntensity,
    EngagementStyle
)
from processing.parameters.variation import (
    ImperfectionTolerance,
    LengthVariationRange,
    SentenceRhythmVariation,
    StructuralPredictability
)
from processing.parameters.technical import (
    TechnicalLanguageIntensity,
    ContextSpecificity
)

__all__ = [
    # Base classes
    'BaseParameter',
    'Scale10Parameter',
    'Scale3Parameter',
    'ParameterCategory',
    'ParameterTier',
    'get_registry',
    'ParameterRegistry',
    # AI Detection parameters
    'HumannessIntensity',
    'AIAvoidanceIntensity',
    # Voice parameters
    'JargonRemoval',
    'ProfessionalVoice',
    'PersonalityIntensity',
    'EmotionalIntensity',
    'AuthorVoiceIntensity',
    'EngagementStyle',
    # Variation parameters
    'ImperfectionTolerance',
    'LengthVariationRange',
    'SentenceRhythmVariation',
    'StructuralPredictability',
    # Technical parameters
    'TechnicalLanguageIntensity',
    'ContextSpecificity'
]
