#!/usr/bin/env python3
"""
Base Component Validator

Provides common validation patterns to reduce code duplication across component validators.
Following GROK_INSTRUCTIONS.md principles: fail-fast validation, no fallbacks.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from utils.validation import validate_placeholder_content


class BaseComponentValidator(ABC):
    """Base class for component validators to reduce duplication"""

    def __init__(self, component_type: str):
        self.component_type = component_type

    def validate_basic_content(self, content: str) -> List[str]:
        """
        Common content validation that all components need.
        
        Args:
            content: The content to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Basic empty content check
        if not content or not content.strip():
            errors.append(f"{self.component_type.title()} component cannot be empty")
            return errors  # Early return for empty content

        # Check for placeholder content using centralized utility
        errors.extend(validate_placeholder_content(content))

        return errors

    def validate_required_fields(
        self, data: Dict[str, Any], required_fields: List[str]
    ) -> List[str]:
        """
        Validate that required fields are present in data.
        
        Args:
            data: The data dictionary to validate
            required_fields: List of required field names
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        missing_fields = []

        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                missing_fields.append(field)

        if missing_fields:
            errors.append(
                f"Missing required fields for {self.component_type}: {', '.join(missing_fields)}"
            )

        return errors

    def validate_content_length(
        self, content: str, min_length: int = 1, max_length: int = None
    ) -> List[str]:
        """
        Validate content length requirements.
        
        Args:
            content: The content to validate
            min_length: Minimum character length
            max_length: Maximum character length (None for no limit)
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        content_length = len(content.strip())

        if content_length < min_length:
            errors.append(
                f"{self.component_type.title()} content too short "
                f"({content_length} chars, minimum {min_length})"
            )

        if max_length and content_length > max_length:
            errors.append(
                f"{self.component_type.title()} content too long "
                f"({content_length} chars, maximum {max_length})"
            )

        return errors

    @abstractmethod
    def validate_format(
        self, content: str, format_rules: Dict[str, Any] = None
    ) -> List[str]:
        """
        Component-specific format validation.
        Must be implemented by each component validator.
        
        Args:
            content: The content to validate
            format_rules: Optional format rules dictionary
            
        Returns:
            List of validation errors (empty if valid)
        """
        pass

    @abstractmethod
    def validate_content(self, content: str) -> List[str]:
        """
        Component-specific content validation.
        Must be implemented by each component validator.
        
        Args:
            content: The content to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        pass

    def validate_comprehensive(
        self, content: str, format_rules: Dict[str, Any] = None
    ) -> Dict[str, List[str]]:
        """
        Run all validation checks and return categorized results.
        
        Args:
            content: The content to validate
            format_rules: Optional format rules dictionary
            
        Returns:
            Dict with validation results categorized by type
        """
        results = {
            "basic_errors": [],
            "format_errors": [],
            "content_errors": [],
        }

        # Run basic validation first
        results["basic_errors"] = self.validate_basic_content(content)
        
        # Only run other validations if basic validation passes
        if not results["basic_errors"]:
            results["format_errors"] = self.validate_format(content, format_rules)
            results["content_errors"] = self.validate_content(content)

        return results

    def has_errors(self, validation_results: Dict[str, List[str]]) -> bool:
        """
        Check if validation results contain any errors.
        
        Args:
            validation_results: Results from validate_comprehensive()
            
        Returns:
            True if any errors found, False otherwise
        """
        return any(errors for errors in validation_results.values())

    def get_all_errors(self, validation_results: Dict[str, List[str]]) -> List[str]:
        """
        Flatten all errors from validation results into a single list.
        
        Args:
            validation_results: Results from validate_comprehensive()
            
        Returns:
            Flattened list of all errors
        """
        all_errors = []
        for error_list in validation_results.values():
            all_errors.extend(error_list)
        return all_errors
