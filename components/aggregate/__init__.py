"""
Aggregate component generation module.

Provides functionality to generate all components for a material
in a single API request instead of individual requests.
"""

from .generator import AggregateGenerator
from .integration import (
    generate_material_aggregate,
    save_generated_components, 
    run_aggregate_generation,
    AGGREGATE_CONFIG
)

__all__ = [
    'AggregateGenerator',
    'generate_material_aggregate',
    'save_generated_components',
    'run_aggregate_generation', 
    'AGGREGATE_CONFIG'
]
