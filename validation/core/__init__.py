"""
Consolidated Validation Core

Provides unified validation interface through 4 core modules:
- base_validator: Abstract base class and validation framework
- content: Content quality, author voice, caption integration
- schema: Schema validation and duplication detection  
- quality: Quality scoring and thresholds

Usage:
    from validation.core import ContentValidator, SchemaValidator
    
    validator = ContentValidator(quality_threshold=0.7)
    result = validator.validate({'content': 'text to validate'})
"""

from validation.core.base_validator import (
    BaseValidator,
    CompositeValidator,
    ValidationContext
)

from validation.core.content import (
    ContentValidator,
    CaptionIntegrationValidator,
    ContentQualityScore
)

from validation.core.schema import (
    SchemaValidator,
    DuplicationDetector,
    SchemaValidationResult
)

# Export all public classes
__all__ = [
    # Base framework
    'BaseValidator',
    'CompositeValidator',
    'ValidationContext',
    
    # Content validation
    'ContentValidator',
    'CaptionIntegrationValidator',
    'ContentQualityScore',
    
    # Schema validation
    'SchemaValidator',
    'DuplicationDetector',
    'SchemaValidationResult',
]
