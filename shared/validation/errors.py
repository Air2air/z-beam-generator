#!/usr/bin/env python3
"""
Unified validation error types for Z-Beam Generator

Provides structured error types with severity levels for consistent
fail-fast behavior across all validation services.

Per GROK_INSTRUCTIONS.md:
- CRITICAL/ERROR severity: System MUST fail immediately
- WARNING severity: Log and continue
- INFO severity: Log for debugging
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime


class ErrorSeverity(Enum):
    """Validation error severity levels"""
    CRITICAL = "CRITICAL"  # System cannot continue - fail immediately
    ERROR = "ERROR"        # Validation failed - fail immediately
    WARNING = "WARNING"    # Issue detected - log and continue
    INFO = "INFO"          # Informational - log for debugging


class ErrorType(Enum):
    """Categories of validation errors"""
    # Configuration errors
    MISSING_CONFIG = "missing_config"
    INVALID_CONFIG = "invalid_config"
    MISSING_DEPENDENCY = "missing_dependency"
    
    # Data structure errors
    MISSING_FIELD = "missing_field"
    INVALID_FIELD = "invalid_field"
    MISSING_PROPERTY = "missing_property"
    INVALID_PROPERTY = "invalid_property"
    
    # Value validation errors
    OUT_OF_RANGE = "out_of_range"
    INVALID_UNIT = "invalid_unit"
    INVALID_VALUE = "invalid_value"
    LOW_CONFIDENCE = "low_confidence"
    
    # Relationship validation errors
    FORMULA_VIOLATION = "formula_violation"
    RATIO_VIOLATION = "ratio_violation"
    ENERGY_CONSERVATION = "energy_conservation"
    
    # Category validation errors
    FORBIDDEN_CATEGORY = "forbidden_category"
    INCORRECT_CATEGORIZATION = "incorrect_categorization"
    MISSING_CATEGORY = "missing_category"
    
    # Completeness errors
    INCOMPLETE_DATA = "incomplete_data"
    MISSING_METADATA = "missing_metadata"
    
    # System errors
    VALIDATION_ERROR = "validation_error"
    GENERATION_ERROR = "generation_error"


@dataclass
class ValidationError:
    """Structured validation error with severity and context"""
    
    severity: ErrorSeverity
    error_type: ErrorType
    message: str
    
    # Context fields
    material: Optional[str] = None
    property_name: Optional[str] = None
    category: Optional[str] = None
    file_path: Optional[str] = None
    
    # Details
    expected_value: Optional[Any] = None
    actual_value: Optional[Any] = None
    suggestion: Optional[str] = None
    
    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'severity': self.severity.value,
            'type': self.error_type.value,
            'message': self.message,
            'material': self.material,
            'property': self.property_name,
            'category': self.category,
            'file': self.file_path,
            'expected': self.expected_value,
            'actual': self.actual_value,
            'suggestion': self.suggestion,
            'timestamp': self.timestamp
        }
    
    def is_critical(self) -> bool:
        """Check if error is critical (must fail immediately)"""
        return self.severity in (ErrorSeverity.CRITICAL, ErrorSeverity.ERROR)
    
    def is_warning(self) -> bool:
        """Check if error is a warning (log and continue)"""
        return self.severity == ErrorSeverity.WARNING
    
    def is_info(self) -> bool:
        """Check if error is informational (log for debugging)"""
        return self.severity == ErrorSeverity.INFO
    
    def __str__(self) -> str:
        """Human-readable error message"""
        parts = [f"[{self.severity.value}]"]
        
        if self.material:
            parts.append(f"Material: {self.material}")
        if self.property_name:
            parts.append(f"Property: {self.property_name}")
        if self.category:
            parts.append(f"Category: {self.category}")
            
        parts.append(self.message)
        
        if self.suggestion:
            parts.append(f"Suggestion: {self.suggestion}")
            
        return " | ".join(parts)


# Specific exception classes for fail-fast behavior
class ConfigurationError(Exception):
    """
    Missing or invalid configuration that prevents system startup.
    Per GROK_INSTRUCTIONS.md: ZERO TOLERANCE - must fail immediately.
    """
    pass


class MaterialsValidationError(Exception):
    """
    Invalid material data that cannot be processed.
    Per GROK_INSTRUCTIONS.md: ZERO TOLERANCE - must fail immediately.
    """
    pass


class GenerationError(Exception):
    """
    Content generation failure that should stop processing.
    Per GROK_INSTRUCTIONS.md: ZERO TOLERANCE - must fail immediately.
    """
    pass


class PropertyDiscoveryError(Exception):
    """
    Property discovery failure - no fallbacks allowed.
    Per GROK_INSTRUCTIONS.md: ZERO TOLERANCE - must fail immediately.
    """
    pass


class MaterialDataError(Exception):
    """
    Required material data is missing.
    Per GROK_INSTRUCTIONS.md: ZERO TOLERANCE - must fail immediately.
    """
    pass


@dataclass
class ValidationResult:
    """
    Result of validation operation with structured errors.
    Supports both new VError format and legacy dict format for backwards compatibility.
    """
    
    def __init__(self, success: bool, validation_type: str, 
                 issues: Optional[List[Dict]] = None,
                 warnings: Optional[List[Dict]] = None,
                 errors: Optional[List] = None,  # Can be VError or dict
                 timestamp: Optional[str] = None):
        """
        Initialize ValidationResult with backwards compatibility.
        
        Args:
            success: Whether validation passed
            validation_type: Type of validation performed
            issues: Legacy dict-based issues (INFO level) - optional
            warnings: Legacy dict-based warnings (WARNING level) - optional
            errors: Can be list of VError objects or legacy dict-based errors (ERROR level) - optional
            timestamp: ISO timestamp - optional
        """
        self.success = success
        self.validation_type = validation_type
        self.timestamp = timestamp or datetime.now().isoformat()
        
        # Handle legacy dict-based format
        self.issues = issues or []
        self.warnings = warnings or []
        
        if errors and len(errors) > 0 and isinstance(errors[0], dict):
            # Legacy dict format - store separately
            self._errors_dicts = errors or []
            self.errors = []
        else:
            # New VError format
            self.errors = errors or []
            self._errors_dicts = []
    
    @property
    def has_critical_issues(self) -> bool:
        """Check if has critical issues (for backwards compatibility with old code)"""
        return not self.success or len(self._errors_dicts) > 0 or self.has_critical_errors_new
    
    @property
    def has_critical_errors_new(self) -> bool:
        """Check if any critical VError objects exist"""
        return any(error.is_critical() for error in self.errors)
    
    @property
    def critical_errors(self) -> List[ValidationError]:
        """Get all critical VError objects"""
        return [e for e in self.errors if e.is_critical()]
    
    @property
    def warning_errors(self) -> List[ValidationError]:
        """Get all warning VError objects (different from self.warnings dict list)"""
        return [e for e in self.errors if e.is_warning()]
    
    @property
    def info_messages(self) -> List[ValidationError]:
        """Get all info VError objects"""
        return [e for e in self.errors if e.is_info()]
    
    def add_error(self, error: ValidationError) -> None:
        """Add a validation error"""
        self.errors.append(error)
        # Update success status if critical error added
        if error.is_critical():
            self.success = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'success': self.success,
            'validation_type': self.validation_type,
            'timestamp': self.timestamp,
            'critical_errors': len(self.critical_errors),
            'warnings': len(self.warnings),
            'info': len(self.info_messages),
            'errors': [error.to_dict() for error in self.errors]
        }
    
    def get_summary(self) -> str:
        """Get human-readable summary"""
        status = "✅ PASSED" if self.success else "❌ FAILED"
        return (
            f"Validation: {self.validation_type.upper()} - {status}\n"
            f"Critical Errors: {len(self.critical_errors)}\n"
            f"Warnings: {len(self.warnings)}\n"
            f"Info: {len(self.info_messages)}"
        )
