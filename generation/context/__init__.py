"""
Generation Context Module

Generation-time context providers and metadata (complies with Core Principle 0.6)
"""

from generation.context.generation_metadata import (
    enrich_for_generation,
    get_metadata_provider,
    GenerationMetadata
)
from generation.context.data_provider import DataProvider
from generation.context.seo_formatter import SEOContextFormatter

__all__ = [
    'enrich_for_generation',
    'get_metadata_provider',
    'GenerationMetadata',
    'DataProvider',
    'SEOContextFormatter'
]
