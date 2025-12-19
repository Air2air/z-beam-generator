"""
Consolidated Validation Core

Provides unified validation interface through 4 core modules:
- base_validator: Abstract base class and validation framework
- content: Content quality, author voice, micro integration
- schema: Schema validation and duplication detection  
- quality: Quality scoring and thresholds

Usage:
    from shared.validation.core import ContentValidator, SchemaValidator
    
    validator = ContentValidator(quality_threshold=0.7)
    result = validator.validate({'content': 'text to validate'})
"""

from shared.validation.core.base_validator import (
    BaseValidator,
    CompositeValidator,
    ValidationContext,
)
from shared.validation.core.content import (
    ContentQualityScore,
    ContentValidator,
    MicroIntegrationValidator,
)
from shared.validation.core.schema import (
    DuplicationDetector,
    SchemaValidationResult,
    SchemaValidator,
)

# Export all public classes
__all__ = [
    # Base framework
    'BaseValidator',
    'CompositeValidator',
    'ValidationContext',
    
    # Content validation
    'ContentValidator',
    'MicroIntegrationValidator',
    'ContentQualityScore',
    
    # Schema validation
    'SchemaValidator',
    'DuplicationDetector',
    'SchemaValidationResult',
]
