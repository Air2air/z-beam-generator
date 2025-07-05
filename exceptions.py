# generator/exceptions.py
"""
Custom exception classes for the article generation system.
"""


class ArticleGenerationError(Exception):
    """Base exception for article generation errors."""

    pass


class ConfigurationError(ArticleGenerationError):
    """Raised when there's a configuration-related error."""

    pass


class APIError(ArticleGenerationError):
    """Raised when there's an API-related error."""

    def __init__(self, message: str, provider: str = None, status_code: int = None):
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code


class PromptError(ArticleGenerationError):
    """Raised when there's a prompt-related error."""

    pass


class ContentGenerationError(ArticleGenerationError):
    """Raised when content generation fails."""

    pass


class FileOperationError(ArticleGenerationError):
    """Raised when file operations fail."""

    pass


class GenerationError(ArticleGenerationError):
    """General generation process error."""

    pass
