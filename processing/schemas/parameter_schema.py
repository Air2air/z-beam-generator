"""
Canonical Parameter Schema for Z-Beam Generation System

Defines single source of truth for parameter structure across entire pipeline:
- Sweet spot discovery
- Parameter initialization
- Prompt construction
- API generation
- Result storage
- Evaluation linkage

POLICY: All parameter dictionaries MUST use this canonical structure.
No custom formats, no key variations, no hardcoded values.
"""

from dataclasses import dataclass, asdict, field
from typing import Dict, Any, Optional
import json


@dataclass
class MetadataParams:
    """Generation metadata for tracking and correlation."""
    material_name: str
    component_type: str
    attempt: int
    timestamp: str
    
    def __post_init__(self):
        """Auto-validate on creation."""
        self.validate()
    
    def validate(self) -> None:
        """Validate metadata parameters."""
        if not self.material_name:
            raise ValueError("material_name cannot be empty")
        if not self.component_type:
            raise ValueError("component_type cannot be empty")
        if self.attempt < 1:
            raise ValueError(f"attempt must be >= 1, got {self.attempt}")


@dataclass
class ApiParams:
    """API generation parameters sent to language model."""
    temperature: float
    max_tokens: int
    frequency_penalty: float
    presence_penalty: float
    
    def __post_init__(self):
        """Auto-validate on creation."""
        self.validate()
    
    def validate(self) -> None:
        """Validate API parameters."""
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError(f"temperature must be 0.0-2.0, got {self.temperature}")
        if self.max_tokens < 1:
            raise ValueError(f"max_tokens must be >= 1, got {self.max_tokens}")
        if not 0.0 <= self.frequency_penalty <= 2.0:
            raise ValueError(f"frequency_penalty must be 0.0-2.0, got {self.frequency_penalty}")
        if not 0.0 <= self.presence_penalty <= 2.0:
            raise ValueError(f"presence_penalty must be 0.0-2.0, got {self.presence_penalty}")


@dataclass
class RetryParams:
    """Retry behavior configuration."""
    max_attempts: int
    retry_temperature_increase: float
    
    def __post_init__(self):
        """Auto-validate on creation."""
        self.validate()
    
    def validate(self) -> None:
        """Validate retry parameters."""
        if self.max_attempts < 1:
            raise ValueError(f"max_attempts must be >= 1, got {self.max_attempts}")
        if not 0.0 <= self.retry_temperature_increase <= 0.5:
            raise ValueError(f"retry_temperature_increase must be 0.0-0.5, got {self.retry_temperature_increase}")


@dataclass
class VoiceParams:
    """Voice profile parameters for human-like writing style."""
    trait_frequency: float
    opinion_rate: float
    reader_address_rate: float
    colloquialism_frequency: float
    structural_predictability: float
    emotional_tone: float
    imperfection_tolerance: Optional[float] = None
    sentence_rhythm_variation: Optional[float] = None
    
    def __post_init__(self):
        """Auto-validate on creation."""
        self.validate()
    
    def validate(self) -> None:
        """Validate voice parameters (all 0.0-1.0 range)."""
        for name, value in [
            ('trait_frequency', self.trait_frequency),
            ('opinion_rate', self.opinion_rate),
            ('reader_address_rate', self.reader_address_rate),
            ('colloquialism_frequency', self.colloquialism_frequency),
            ('structural_predictability', self.structural_predictability),
            ('emotional_tone', self.emotional_tone)
        ]:
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be 0.0-1.0, got {value}")
        
        # Optional params
        if self.imperfection_tolerance is not None:
            if not 0.0 <= self.imperfection_tolerance <= 1.0:
                raise ValueError(f"imperfection_tolerance must be 0.0-1.0, got {self.imperfection_tolerance}")
        
        if self.sentence_rhythm_variation is not None:
            if not 0.0 <= self.sentence_rhythm_variation <= 1.0:
                raise ValueError(f"sentence_rhythm_variation must be 0.0-1.0, got {self.sentence_rhythm_variation}")


@dataclass
class EnrichmentParams:
    """Content enrichment parameters for technical depth and engagement."""
    technical_intensity: int
    context_detail_level: int
    fact_formatting_style: str
    engagement_level: int
    
    def __post_init__(self):
        """Auto-validate on creation."""
        self.validate()
    
    def validate(self) -> None:
        """Validate enrichment parameters."""
        if not 1 <= self.technical_intensity <= 3:
            raise ValueError(f"technical_intensity must be 1-3, got {self.technical_intensity}")
        if not 1 <= self.context_detail_level <= 3:
            raise ValueError(f"context_detail_level must be 1-3, got {self.context_detail_level}")
        if self.fact_formatting_style not in ['minimal', 'balanced', 'detailed']:
            raise ValueError(f"fact_formatting_style must be minimal/balanced/detailed, got {self.fact_formatting_style}")
        if not 1 <= self.engagement_level <= 3:
            raise ValueError(f"engagement_level must be 1-3, got {self.engagement_level}")


@dataclass
class ValidationParams:
    """Quality validation thresholds for acceptance criteria."""
    detection_threshold: float
    readability_min: float
    readability_max: float
    grammar_strictness: float
    confidence_high: float
    confidence_medium: float
    
    def __post_init__(self):
        """Auto-validate on creation."""
        self.validate()
    
    def validate(self) -> None:
        """Validate validation parameters."""
        if not 0.0 <= self.detection_threshold <= 1.0:
            raise ValueError(f"detection_threshold must be 0.0-1.0, got {self.detection_threshold}")
        if not 0.0 <= self.readability_min <= 100.0:
            raise ValueError(f"readability_min must be 0.0-100.0, got {self.readability_min}")
        if not 0.0 <= self.readability_max <= 100.0:
            raise ValueError(f"readability_max must be 0.0-100.0, got {self.readability_max}")
        if self.readability_min > self.readability_max:
            raise ValueError(f"readability_min ({self.readability_min}) > readability_max ({self.readability_max})")
        if not 0.0 <= self.grammar_strictness <= 1.0:
            raise ValueError(f"grammar_strictness must be 0.0-1.0, got {self.grammar_strictness}")
        if not 0.0 <= self.confidence_high <= 1.0:
            raise ValueError(f"confidence_high must be 0.0-1.0, got {self.confidence_high}")
        if not 0.0 <= self.confidence_medium <= 1.0:
            raise ValueError(f"confidence_medium must be 0.0-1.0, got {self.confidence_medium}")


@dataclass
class CanonicalParameters:
    """
    Canonical parameter structure for entire Z-Beam pipeline.
    
    This is the SINGLE SOURCE OF TRUTH for parameter format.
    All parameter dictionaries must conform to this structure.
    
    Usage:
        # Creation
        params = CanonicalParameters(
            metadata=MetadataParams(...),
            api=ApiParams(...),
            retry=RetryParams(...),
            voice=VoiceParams(...),
            enrichment=EnrichmentParams(...),
            validation=ValidationParams(...)
        )
        
        # Validation
        params.validate()
        
        # Conversion to dict
        params_dict = params.to_dict()
        
        # Conversion from dict
        params = CanonicalParameters.from_dict(params_dict)
        
        # Storage format
        db.log_generation_parameters(detection_id, params.to_storage_format())
    """
    metadata: MetadataParams
    api: ApiParams
    retry: RetryParams
    voice: VoiceParams
    enrichment: EnrichmentParams
    validation: ValidationParams
    
    def validate(self) -> None:
        """Validate all parameter sections."""
        self.metadata.validate()
        self.api.validate()
        self.retry.validate()
        self.voice.validate()
        self.enrichment.validate()
        self.validation.validate()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dict with nested structure matching dataclass hierarchy
        """
        return {
            'metadata': asdict(self.metadata),
            'api': asdict(self.api),
            'retry': asdict(self.retry),
            'voice': asdict(self.voice),
            'enrichment': asdict(self.enrichment),
            'validation': asdict(self.validation)
        }
    
    def to_storage_format(self) -> Dict[str, Any]:
        """
        Convert to format expected by winston_feedback_db.log_generation_parameters().
        
        This is the canonical storage format that will be saved to the database.
        IMPORTANT: This should be the ONLY conversion needed for storage.
        
        Returns:
            Dict with structure:
            {
                'material_name': str,
                'component_type': str,
                'attempt': int,
                'api': {...},
                'voice': {...},
                'enrichment': {...},
                'validation': {...},
                'retry': {...}
            }
        """
        return {
            'material_name': self.metadata.material_name,
            'component_type': self.metadata.component_type,
            'attempt': self.metadata.attempt,
            'api': asdict(self.api),
            'retry': asdict(self.retry),
            'voice': asdict(self.voice),
            'enrichment': asdict(self.enrichment),
            'validation': asdict(self.validation)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CanonicalParameters':
        """
        Create from dictionary representation.
        
        Args:
            data: Dict with structure matching to_dict() output
            
        Returns:
            CanonicalParameters instance
        """
        return cls(
            metadata=MetadataParams(**data['metadata']),
            api=ApiParams(**data['api']),
            retry=RetryParams(**data['retry']),
            voice=VoiceParams(**data['voice']),
            enrichment=EnrichmentParams(**data['enrichment']),
            validation=ValidationParams(**data['validation'])
        )
    
    @classmethod
    def from_storage_format(cls, data: Dict[str, Any], timestamp: str) -> 'CanonicalParameters':
        """
        Create from database storage format.
        
        Handles conversion from winston_feedback_db.log_generation_parameters() format.
        
        Args:
            data: Dict with structure from to_storage_format()
            timestamp: ISO format timestamp string
            
        Returns:
            CanonicalParameters instance
        """
        return cls(
            metadata=MetadataParams(
                material_name=data['material_name'],
                component_type=data['component_type'],
                attempt=data['attempt'],
                timestamp=timestamp
            ),
            api=ApiParams(**data['api']),
            retry=RetryParams(**data['retry']),
            voice=VoiceParams(**data['voice']),
            enrichment=EnrichmentParams(**data['enrichment']),
            validation=ValidationParams(**data['validation'])
        )
    
    def to_json(self) -> str:
        """Convert to JSON string for logging or debugging."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'CanonicalParameters':
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))


# ============================================================================
# NORMALIZATION UTILITIES
# ============================================================================

def to_canonical(legacy_params: Dict[str, Any], material_name: str, component_type: str, 
                 attempt: int, timestamp: str) -> CanonicalParameters:
    """
    Normalize legacy parameter formats to canonical structure.
    
    Handles various input formats:
    - DynamicConfig.get_all_generation_params() output
    - Old _get_adaptive_parameters() output
    - Database retrieval formats
    
    Args:
        legacy_params: Parameters in any legacy format
        material_name: Material identifier
        component_type: Component type
        attempt: Attempt number
        timestamp: ISO format timestamp
        
    Returns:
        Normalized CanonicalParameters instance
        
    Raises:
        ValueError: If required parameters are missing
    """
    # Extract API params (handle multiple possible locations)
    if 'api_params' in legacy_params:
        api_section = legacy_params['api_params']
        penalties = api_section.get('penalties', legacy_params.get('api_penalties', {}))
    elif 'api' in legacy_params:
        api_section = legacy_params['api']
        penalties = api_section
    else:
        # Flat structure - params at root level
        api_section = legacy_params
        penalties = legacy_params
    
    api_params = ApiParams(
        temperature=api_section['temperature'],
        max_tokens=api_section['max_tokens'],
        frequency_penalty=penalties.get('frequency_penalty', 0.0),
        presence_penalty=penalties.get('presence_penalty', 0.0)
    )
    
    # Extract retry params
    if 'retry_behavior' in legacy_params:
        retry_section = legacy_params['retry_behavior']
    elif 'retry' in legacy_params:
        retry_section = legacy_params['retry']
    else:
        retry_section = api_section.get('retry_behavior', {})
    
    retry_params = RetryParams(
        max_attempts=retry_section.get('max_attempts', 3),
        retry_temperature_increase=retry_section.get('retry_temperature_increase', 0.05)
    )
    
    # Extract voice params
    voice_section = legacy_params.get('voice_params', legacy_params.get('voice', {}))
    voice_params = VoiceParams(**voice_section)
    
    # Extract enrichment params
    enrichment_section = legacy_params.get('enrichment_params', legacy_params.get('enrichment', {}))
    enrichment_params = EnrichmentParams(**enrichment_section)
    
    # Extract validation params
    if 'validation_params' in legacy_params:
        val_section = legacy_params['validation_params']
        thresholds = val_section.get('readability_thresholds', {})
        confidence = val_section.get('confidence_thresholds', {})
        validation_params = ValidationParams(
            detection_threshold=val_section['detection_threshold'],
            readability_min=thresholds.get('min', 0.0),
            readability_max=thresholds.get('max', 100.0),
            grammar_strictness=val_section['grammar_strictness'],
            confidence_high=confidence.get('high', 0.9),
            confidence_medium=confidence.get('medium', 0.7)
        )
    elif 'validation' in legacy_params:
        val_section = legacy_params['validation']
        validation_params = ValidationParams(**val_section)
    else:
        # Provide sensible defaults if validation section missing
        validation_params = ValidationParams(
            detection_threshold=0.3,
            readability_min=40.0,
            readability_max=70.0,
            grammar_strictness=0.8,
            confidence_high=0.9,
            confidence_medium=0.7
        )
    
    # Create metadata
    metadata = MetadataParams(
        material_name=material_name,
        component_type=component_type,
        attempt=attempt,
        timestamp=timestamp
    )
    
    # Construct canonical parameters
    canonical = CanonicalParameters(
        metadata=metadata,
        api=api_params,
        retry=retry_params,
        voice=voice_params,
        enrichment=enrichment_params,
        validation=validation_params
    )
    
    # Validate before returning
    canonical.validate()
    
    return canonical


def from_canonical(canonical: CanonicalParameters, target_format: str = 'storage') -> Dict[str, Any]:
    """
    Convert canonical parameters to specific target format.
    
    Args:
        canonical: CanonicalParameters instance
        target_format: Output format ('storage', 'dict', 'legacy')
        
    Returns:
        Parameters in requested format
        
    Raises:
        ValueError: If target_format is unknown
    """
    if target_format == 'storage':
        return canonical.to_storage_format()
    elif target_format == 'dict':
        return canonical.to_dict()
    elif target_format == 'legacy':
        # Convert back to old DynamicConfig format for compatibility
        return {
            'api_params': {
                'temperature': canonical.api.temperature,
                'max_tokens': canonical.api.max_tokens,
                'retry_behavior': asdict(canonical.retry),
                'penalties': {
                    'frequency_penalty': canonical.api.frequency_penalty,
                    'presence_penalty': canonical.api.presence_penalty
                }
            },
            'voice_params': asdict(canonical.voice),
            'enrichment_params': asdict(canonical.enrichment),
            'validation_params': {
                'readability_thresholds': {
                    'min': canonical.validation.readability_min,
                    'max': canonical.validation.readability_max
                },
                'grammar_strictness': canonical.validation.grammar_strictness,
                'detection_threshold': canonical.validation.detection_threshold,
                'confidence_thresholds': {
                    'high': canonical.validation.confidence_high,
                    'medium': canonical.validation.confidence_medium
                }
            }
        }
    else:
        raise ValueError(f"Unknown target_format: {target_format}")
