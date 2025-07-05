"""Domain layer for the Z-Beam content generation system."""

# Domain entities
from .entities import (
    ContentGenerationRequest,
    ContentGenerationResult,
    GenerationSession
)

# Value objects
from .value_objects import (
    SectionSpec,
    WordBudget,
    SectionType,
    GenerationSettings,
    TemperatureSettings,
    ThresholdSettings,
    APISettings,
    Provider,
    DetectionMode,
    DetectionResult,
    DetectionScore,
    AggregateDetectionResult,
    DetectionStatus,
    ContentQuality
)

__all__ = [
    # Entities
    'ContentGenerationRequest',
    'ContentGenerationResult', 
    'GenerationSession',
    # Value objects
    'SectionSpec',
    'WordBudget',
    'SectionType',
    'GenerationSettings',
    'TemperatureSettings',
    'ThresholdSettings',
    'APISettings',
    'Provider',
    'DetectionMode',
    'DetectionResult',
    'DetectionScore',
    'AggregateDetectionResult',
    'DetectionStatus',
    'ContentQuality',
]
