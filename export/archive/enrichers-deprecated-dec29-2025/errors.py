"""
Standardized Error Classes for Enrichers

Consolidates error handling across all enricher types.
Part of Export System Consolidation Phase 3.
"""


class ExportError(Exception):
    """Base exception for export system errors."""
    pass


class EnrichmentError(ExportError):
    """Base exception for enrichment errors."""
    pass


class LibraryNotFoundError(EnrichmentError):
    """Raised when library file is not found."""
    pass


class EntryNotFoundError(EnrichmentError):
    """Raised when library entry is not found."""
    pass


class InvalidRelationshipError(EnrichmentError):
    """Raised when relationship data is invalid."""
    pass


class ConfigurationError(EnrichmentError):
    """Raised when enricher configuration is invalid."""
    pass
