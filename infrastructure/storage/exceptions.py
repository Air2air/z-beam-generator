"""
Exception classes for storage operations.
"""


class StorageException(Exception):
    """Base exception for storage operations."""

    pass


class FileOperationError(StorageException):
    """Exception raised when a file operation fails."""

    def __init__(self, message: str, path: str = None, operation: str = None):
        self.path = path
        self.operation = operation
        self.message = message
        super().__init__(
            f"{message} (Operation: {operation or 'unknown'}, Path: {path or 'unknown'})"
        )
