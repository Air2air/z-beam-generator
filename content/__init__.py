"""
Universal Content System

Extensible framework for researching and generating frontmatter for ANY content type.
Supports materials, products, services, technologies, and future content types.
"""

from content.schemas.base import (
    ContentSchema,
    FieldResearchSpec,
    ResearchResult,
    ComponentResult,
    ContentResult
)

__all__ = [
    'ContentSchema',
    'FieldResearchSpec', 
    'ResearchResult',
    'ComponentResult',
    'ContentResult'
]
