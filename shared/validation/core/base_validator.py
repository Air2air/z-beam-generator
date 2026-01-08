#!/usr/bin/env python3
"""
Base Validator Framework for Z-Beam Generator

Provides the foundational validation interface and utilities used by all
specialized validators (content, schema, quality).

Per GROK_INSTRUCTIONS.md:
- Fail-fast on configuration/dependency issues
- Return structured ValidationResult objects
- Use specific exception types from shared.validation.errors
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

# Import unified error types
from shared.exceptions import ConfigurationError, ValidationError
from shared.validation.errors import (
    ErrorSeverity,
    ErrorType,
    ValidationResult,
)


@dataclass
class ValidationContext:
    """Context information for validation operations"""
    material_name: Optional[str] = None
    component_type: Optional[str] = None
    validation_mode: str = "standard"
    strict_mode: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class BaseValidator(ABC):
    """
    Abstract base class for all validators.
    
    All validators must implement:
    - validate() - Main validation method
    - get_validator_name() - Identifier for logging
    
    Provides common utilities for:
    - Error collection and reporting
    - Validation result creation
    - Context management
    """
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize validator with optional strict mode.
        
        Args:
            strict_mode: If True, treat warnings as errors
        """
        self.strict_mode = strict_mode
        self.errors: List[ValidationError] = []
        
    @abstractmethod
    def validate(self, data: Any, context: Optional[ValidationContext] = None) -> ValidationResult:
        """
        Validate the provided data.
        
        Args:
            data: Data to validate (type varies by validator)
            context: Optional validation context
            
        Returns:
            ValidationResult with success status and any errors
            
        Raises:
            ConfigurationError: If validator not properly configured
            GenerationError: If validation cannot complete
        """
        pass
    
    @abstractmethod
    def get_validator_name(self) -> str:
        """Return the name of this validator for logging"""
        pass
    
    def add_error(
        self,
        error_type: ErrorType,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a validation error to the collection.
        
        Args:
            error_type: Category of error
            message: Human-readable error description
            severity: Error severity level
            field: Optional field name that caused error
            details: Optional additional error details
        """
        error = ValidationError(
            error_type=error_type,
            message=message,
            severity=severity,
            field=field,
            details=details or {}
        )
        self.errors.append(error)
    
    def create_result(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Create a ValidationResult from collected errors.
        
        Args:
            success: Whether validation passed
            data: Optional validated/processed data
            
        Returns:
            ValidationResult with errors and success status
        """
        # In strict mode, warnings become errors
        if self.strict_mode:
            has_warnings = any(e.severity == ErrorSeverity.WARNING for e in self.errors)
            if has_warnings:
                success = False
        
        return ValidationResult(
            valid=success,
            errors=self.errors.copy(),
            data=data or {},
            validator=self.get_validator_name()
        )
    
    def clear_errors(self) -> None:
        """Clear all collected errors (for reuse of validator instance)"""
        self.errors.clear()
    
    def has_critical_errors(self) -> bool:
        """Check if any critical errors have been collected"""
        return any(e.severity == ErrorSeverity.CRITICAL for e in self.errors)
    
    def has_errors(self) -> bool:
        """Check if any errors (not warnings) have been collected"""
        return any(
            e.severity in (ErrorSeverity.ERROR, ErrorSeverity.CRITICAL)
            for e in self.errors
        )
    
    def get_error_summary(self) -> Dict[str, int]:
        """Get count of errors by severity"""
        summary = {
            'critical': 0,
            'error': 0,
            'warning': 0,
            'info': 0
        }
        for error in self.errors:
            if error.severity == ErrorSeverity.CRITICAL:
                summary['critical'] += 1
            elif error.severity == ErrorSeverity.ERROR:
                summary['error'] += 1
            elif error.severity == ErrorSeverity.WARNING:
                summary['warning'] += 1
            elif error.severity == ErrorSeverity.INFO:
                summary['info'] += 1
        return summary


class CompositeValidator(BaseValidator):
    """
    Validator that combines multiple validators.
    
    Runs all sub-validators and aggregates their results.
    Useful for complex validation workflows.
    """
    
    def __init__(self, validators: List[BaseValidator], strict_mode: bool = False):
        """
        Initialize with a list of sub-validators.
        
        Args:
            validators: List of BaseValidator instances
            strict_mode: If True, treat warnings as errors
        """
        super().__init__(strict_mode=strict_mode)
        self.validators = validators
    
    def validate(self, data: Any, context: Optional[ValidationContext] = None) -> ValidationResult:
        """
        Run all sub-validators and aggregate results.
        
        Args:
            data: Data to validate
            context: Optional validation context
            
        Returns:
            ValidationResult combining all sub-validator results
        """
        self.clear_errors()
        all_success = True
        combined_data = {}
        
        for validator in self.validators:
            result = validator.validate(data, context)
            if not result.valid:
                all_success = False
            # Collect errors from sub-validator
            self.errors.extend(result.errors)
            # Merge data
            combined_data.update(result.data)
        
        return self.create_result(success=all_success, data=combined_data)
    
    def get_validator_name(self) -> str:
        """Return name identifying this as a composite validator"""
        sub_names = [v.get_validator_name() for v in self.validators]
        return f"CompositeValidator({', '.join(sub_names)})"
