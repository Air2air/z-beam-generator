"""
Enrichment Module

Generation-time data enrichment (complies with Core Principle 0.6)
"""

from generation.enrichment.generation_time_enricher import (
    enrich_for_generation,
    get_enricher,
    GenerationTimeEnricher
)

__all__ = [
    'enrich_for_generation',
    'get_enricher',
    'GenerationTimeEnricher'
]
