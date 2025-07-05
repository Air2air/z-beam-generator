"""
Enhanced exception handling with structured error context.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class ErrorContext:
    """Context information for errors."""

    operation: str
    module: str
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "operation": self.operation,
            "module": self.module,
            "details": self.details or {},
        }


class GeneratorException(Exception):
    """Base exception for the generator system."""

    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        super().__init__(message)
        self.context = context

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging."""
        return {
            "message": str(self),
            "type": self.__class__.__name__,
            "context": self.context.to_dict() if self.context else None,
        }


class ValidationError(GeneratorException):
    """Raised when validation fails."""

    pass


class ConfigurationError(GeneratorException):
    """Raised when there's a configuration-related error."""

    pass


class APIError(GeneratorException):
    """Raised when there's an API-related error."""

    def __init__(
        self,
        message: str,
        provider: str,
        status_code: Optional[int] = None,
        response_data: Optional[str] = None,
    ):
        context = ErrorContext(
            operation="api_call",
            module="api_client",
            details={
                "provider": provider,
                "status_code": status_code,
                "response_data": response_data,
            },
        )
        super().__init__(message, context)
        self.provider = provider
        self.status_code = status_code
        self.response_data = response_data


class PromptError(GeneratorException):
    """Raised when there's a prompt-related error."""

    def __init__(
        self,
        message: str,
        prompt_name: Optional[str] = None,
        category: Optional[str] = None,
    ):
        context = ErrorContext(
            operation="prompt_processing",
            module="prompt_manager",
            details={"prompt_name": prompt_name, "category": category},
        )
        super().__init__(message, context)


class ContentGenerationError(GeneratorException):
    """Raised when content generation fails."""

    def __init__(
        self,
        message: str,
        section: Optional[str] = None,
        iteration: Optional[int] = None,
    ):
        context = ErrorContext(
            operation="content_generation",
            module="content_generator",
            details={"section": section, "iteration": iteration},
        )
        super().__init__(message, context)


class DetectionError(GeneratorException):
    """Raised when AI/human detection fails."""

    def __init__(
        self,
        message: str,
        detection_type: Optional[str] = None,
        content_length: Optional[int] = None,
    ):
        context = ErrorContext(
            operation="detection",
            module="detection_service",
            details={
                "detection_type": detection_type,
                "content_length": content_length,
            },
        )
        super().__init__(message, context)


class FileOperationError(GeneratorException):
    """Raised when file operations fail."""

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        operation: Optional[str] = None,
    ):
        context = ErrorContext(
            operation=operation or "file_operation",
            module="file_handler",
            details={"file_path": file_path, "operation": operation},
        )
        super().__init__(message, context)


class CacheError(GeneratorException):
    """Raised when cache operations fail."""

    def __init__(self, message: str, cache_key: Optional[str] = None):
        context = ErrorContext(
            operation="cache_operation",
            module="cache_repository",
            details={"cache_key": cache_key},
        )
        super().__init__(message, context)


# Legacy exceptions for backward compatibility
class ArticleGenerationError(GeneratorException):
    """Legacy exception - use GeneratorException instead."""

    pass


class GenerationError(GeneratorException):
    """Legacy exception - use ContentGenerationError instead."""

    pass
