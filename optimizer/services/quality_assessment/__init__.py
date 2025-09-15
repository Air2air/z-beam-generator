"""
Quality Assessment Service

This service provides comprehensive quality assessment and scoring capabilities
that can be used by any component in the system. It evaluates content quality
across multiple dimensions and provides detailed scoring and feedback.

Features:
- Multi-dimensional quality scoring
- Readability analysis
- Content structure analysis
- Technical accuracy assessment
- Consistency checking
- Quality trend analysis
- Benchmarking against standards

Optimized: Implementation moved to service.py for proper code organization.
"""

# Import all classes from the service implementation
from .service import (
    QualityAssessmentService,
    QualityDimension,
    QualityScore,
    QualityAssessment,
    QualityBenchmark,
    QualityTrend
)

# Export public API
__all__ = [
    "QualityAssessmentService",
    "QualityDimension",
    "QualityScore",
    "QualityAssessment", 
    "QualityBenchmark",
    "QualityTrend"
]
