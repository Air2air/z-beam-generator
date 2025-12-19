"""
Unified Enrichers Module

Consolidated directory structure:
- base.py: Unified base classes (BaseEnricher, BaseLibraryEnricher)
- errors.py: Standard error classes
- linkage/: Domain relationship enrichers (slug, relationships, registry)
- metadata/: Metadata enrichers (breadcrumb)
- library/: Library data enrichers (12 enrichers + processor + registry)

Part of Export System Consolidation Phase 3.
"""

# Base classes
from .base import BaseEnricher, BaseLibraryEnricher

# Errors
from .errors import (
    ConfigurationError,
    EnrichmentError,
    EntryNotFoundError,
    ExportError,
    InvalidRelationshipError,
    LibraryNotFoundError,
)

# Library enrichers
from .library import LibraryEnrichmentProcessor
from .library.enricher_registry import EnricherRegistry as LibraryEnricherRegistry

# Linkage enrichers
from .linkage import DomainLinkagesEnricher, DomainLinkagesSlugEnricher
from .linkage.registry import create_enrichers

# Metadata enrichers
from .metadata import BreadcrumbEnricher

__all__ = [
    # Base classes
    'BaseEnricher',
    'BaseLibraryEnricher',
    
    # Errors
    'ExportError',
    'EnrichmentError',
    'LibraryNotFoundError',
    'EntryNotFoundError',
    'InvalidRelationshipError',
    'ConfigurationError',
    
    # Linkage
    'DomainLinkagesEnricher',
    'DomainLinkagesSlugEnricher',
    'create_enrichers',
    
    # Metadata
    'BreadcrumbEnricher',
    
    # Library
    'LibraryEnrichmentProcessor',
    'LibraryEnricherRegistry',
]
