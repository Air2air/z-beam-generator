"""Value objects for the Z-Beam domain layer."""

from .content_specs import SectionSpec, WordBudget, SectionType
from .generation_settings import (
    GenerationSettings,
    TemperatureSettings, 
    ThresholdSettings,
    APISettings,
    Provider,
    DetectionMode
)
from .detection_result import (
    DetectionResult,
    DetectionScore,
    AggregateDetectionResult,
    DetectionStatus,
    ContentQuality
)

__all__ = [
    # Content specs
    'SectionSpec',
    'WordBudget', 
    'SectionType',
    # Generation settings
    'GenerationSettings',
    'TemperatureSettings',
    'ThresholdSettings', 
    'APISettings',
    'Provider',
    'DetectionMode',
    # Detection results
    'DetectionResult',
    'DetectionScore',
    'AggregateDetectionResult',
    'DetectionStatus',
    'ContentQuality',
]
