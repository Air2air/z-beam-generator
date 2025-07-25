"""
API MODULE DIRECTIVES FOR AI ASSISTANTS:
1. ERROR HIERARCHY: All errors must inherit from ApiError
2. SPECIFIC ERRORS: Use the most specific error type possible
3. INFORMATIVE MESSAGES: Error messages must be clear and informative
4. NO NEW TYPES: Do not create new error types outside this file
"""

class ApiError(Exception):
    """Base class for all API errors."""
    pass

class ProviderNotFoundError(ApiError):
    """Error raised when a provider is not found or unavailable."""
    pass

class ModelNotAvailableError(ApiError):
    """Error raised when a model is not available."""
    pass

class OptionsValidationError(ApiError):
    """Error raised when options validation fails."""
    pass

class ApiRateLimitError(ApiError):
    """Error raised when an API rate limit is reached."""
    pass

class ApiTimeoutError(ApiError):
    """Error raised when an API request times out."""
    pass

class ApiAuthenticationError(ApiError):
    """Error raised when API authentication fails."""
    pass

class ContentGenerationError(ApiError):
    """Error raised when content generation fails."""
    pass