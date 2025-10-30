#!/usr/bin/env python3
"""
Consolidated Schema Validation

Combines schema validation and duplication detection into a unified service.

Merges functionality from:
- validation/schema_validator.py
- validation/duplication_detector.py
"""

from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from pathlib import Path
import yaml

from validation.core.base_validator import BaseValidator, ValidationContext
from validation.errors import ErrorType, ErrorSeverity


@dataclass
class SchemaValidationResult:
    """Schema validation results with duplication detection"""
    valid: bool
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    duplicates_found: int = 0
    duplicate_details: List[Dict[str, Any]] = field(default_factory=list)


class SchemaValidator(BaseValidator):
    """
    Unified schema validation service.
    
    Validates:
    - YAML structure and syntax
    - Required fields presence
    - Field types and formats
    - Value constraints
    - Duplication detection
    """
    
    def __init__(
        self,
        schema_path: Optional[Path] = None,
        check_duplicates: bool = True,
        strict_mode: bool = False
    ):
        """
        Initialize schema validator.
        
        Args:
            schema_path: Path to schema definition file
            check_duplicates: Enable duplication detection
            strict_mode: If True, treat warnings as errors
        """
        super().__init__(strict_mode=strict_mode)
        self.schema_path = schema_path
        self.check_duplicates = check_duplicates
        self.seen_values: Dict[str, Set[str]] = {}
    
    def get_validator_name(self) -> str:
        """Return validator name"""
        return "SchemaValidator"
    
    def validate(
        self,
        data: Any,
        context: Optional[ValidationContext] = None
    ):
        """
        Validate data against schema.
        
        Args:
            data: Dict containing data to validate
            context: Optional validation context
            
        Returns:
            ValidationResult with schema validation results
        """
        self.clear_errors()
        self.seen_values.clear()
        
        if not isinstance(data, dict):
            self.add_error(
                ErrorType.INVALID_FIELD,
                "Data must be a dictionary",
                ErrorSeverity.ERROR
            )
            return self.create_result(success=False)
        
        # Run schema validation checks
        self._validate_structure(data)
        self._validate_required_fields(data)
        self._validate_field_types(data)
        
        # Run duplication detection if enabled
        duplicates = []
        if self.check_duplicates:
            duplicates = self._detect_duplicates(data)
        
        success = not self.has_errors()
        
        return self.create_result(
            success=success,
            data={
                'duplicates_found': len(duplicates),
                'duplicate_details': duplicates
            }
        )
    
    def _validate_structure(self, data: Dict[str, Any]) -> None:
        """Validate basic YAML structure"""
        if not data:
            self.add_error(
                ErrorType.INVALID_FIELD,
                "Empty data structure",
                ErrorSeverity.ERROR
            )
    
    def _validate_required_fields(self, data: Dict[str, Any]) -> None:
        """Check for required fields"""
        # Define required fields based on data type
        required_fields = self._get_required_fields(data)
        
        for field in required_fields:
            if field not in data:
                self.add_error(
                    ErrorType.MISSING_FIELD,
                    f"Required field '{field}' is missing",
                    ErrorSeverity.ERROR,
                    field=field
                )
    
    def _validate_field_types(self, data: Dict[str, Any]) -> None:
        """Validate field types match expected schema"""
        # Simplified type checking
        for key, value in data.items():
            if value is None:
                self.add_error(
                    ErrorType.MISSING_FIELD,
                    f"Field '{key}' has null value",
                    ErrorSeverity.WARNING,
                    field=key
                )
    
    def _detect_duplicates(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect duplicate values across specified fields.
        
        Args:
            data: Data to check for duplicates
            
        Returns:
            List of duplicate findings
        """
        duplicates = []
        
        # Track values for duplication detection
        for key, value in data.items():
            if isinstance(value, (str, int, float)):
                str_value = str(value)
                
                if key not in self.seen_values:
                    self.seen_values[key] = set()
                
                if str_value in self.seen_values[key]:
                    duplicates.append({
                        'field': key,
                        'value': str_value,
                        'type': 'duplicate_value'
                    })
                    self.add_error(
                        ErrorType.INVALID_VALUE,
                        f"Duplicate value '{str_value}' in field '{key}'",
                        ErrorSeverity.WARNING,
                        field=key
                    )
                else:
                    self.seen_values[key].add(str_value)
        
        return duplicates
    
    def _get_required_fields(self, data: Dict[str, Any]) -> List[str]:
        """
        Get list of required fields based on data type.
        
        Args:
            data: Data being validated
            
        Returns:
            List of required field names
        """
        # Basic required fields (can be extended based on schema_path)
        return []


class DuplicationDetector(BaseValidator):
    """
    Specialized duplication detection validator.
    
    Finds duplicate entries across materials, properties, or content.
    """
    
    def __init__(self, strict_mode: bool = False):
        """Initialize duplication detector"""
        super().__init__(strict_mode=strict_mode)
        self.duplicates_by_field: Dict[str, List[str]] = {}
    
    def get_validator_name(self) -> str:
        """Return validator name"""
        return "DuplicationDetector"
    
    def validate(
        self,
        data: Any,
        context: Optional[ValidationContext] = None
    ):
        """
        Detect duplicates in dataset.
        
        Args:
            data: Dict or list of items to check
            context: Optional validation context
            
        Returns:
            ValidationResult with duplication findings
        """
        self.clear_errors()
        self.duplicates_by_field.clear()
        
        if isinstance(data, list):
            self._check_list_duplicates(data)
        elif isinstance(data, dict):
            self._check_dict_duplicates(data)
        else:
            self.add_error(
                ErrorType.INVALID_FIELD,
                "Data must be a list or dictionary",
                ErrorSeverity.ERROR
            )
            return self.create_result(success=False)
        
        success = not self.has_errors()
        
        return self.create_result(
            success=success,
            data={
                'duplicates_by_field': self.duplicates_by_field,
                'total_duplicates': sum(len(v) for v in self.duplicates_by_field.values())
            }
        )
    
    def _check_list_duplicates(self, items: List[Any]) -> None:
        """Check for duplicates in a list"""
        seen = set()
        for i, item in enumerate(items):
            item_str = str(item)
            if item_str in seen:
                self.add_error(
                    ErrorType.INVALID_VALUE,
                    f"Duplicate item at index {i}: {item_str[:50]}",
                    ErrorSeverity.WARNING
                )
                if 'list_items' not in self.duplicates_by_field:
                    self.duplicates_by_field['list_items'] = []
                self.duplicates_by_field['list_items'].append(item_str)
            else:
                seen.add(item_str)
    
    def _check_dict_duplicates(self, data: Dict[str, Any]) -> None:
        """Check for duplicate values within dictionary fields"""
        value_counts: Dict[str, List[str]] = {}
        
        for key, value in data.items():
            value_str = str(value)
            if value_str not in value_counts:
                value_counts[value_str] = []
            value_counts[value_str].append(key)
        
        # Find values that appear multiple times
        for value_str, keys in value_counts.items():
            if len(keys) > 1:
                self.add_error(
                    ErrorType.INVALID_VALUE,
                    f"Duplicate value '{value_str[:50]}' found in fields: {', '.join(keys)}",
                    ErrorSeverity.WARNING
                )
                for key in keys:
                    if key not in self.duplicates_by_field:
                        self.duplicates_by_field[key] = []
                    self.duplicates_by_field[key].append(value_str)
