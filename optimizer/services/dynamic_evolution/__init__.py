"""
Dynamic Evolution Service

This service provides dynamic prompt/content evolution capabilities that can be used
by any component in the system. It handles the evolution of prompts and content
based on performance data, user feedback, and quality metrics.

Features:
- Template-based prompt evolution
- Gradual improvement application
- Evolution history tracking
- Performance analytics
- A/B testing capabilities
- Version control for prompts

Optimized: Implementation moved to service.py for proper code organization.
"""

# Import all classes from the service implementation
from .service import (
    DynamicEvolutionService,
    EvolutionStrategy,
    EvolutionTrigger,
    EvolutionTemplate,
    EvolutionResult,
    EvolutionHistory,
    ABTestVariant,
    ABTest,
    DynamicEvolutionError
)

# Export public API
__all__ = [
    "DynamicEvolutionService",
    "EvolutionStrategy",
    "EvolutionTrigger", 
    "EvolutionTemplate",
    "EvolutionResult",
    "EvolutionHistory",
    "ABTestVariant",
    "ABTest",
    "DynamicEvolutionError"
]
