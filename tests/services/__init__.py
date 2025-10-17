"""
Test suite for consolidated services.

This package contains comprehensive tests for the three consolidated services:
1. PreGenerationValidationService - Property validation, relationships, gap analysis
2. AIResearchEnrichmentService - AI research, verification, batch operations
3. PostGenerationQualityService - Schema validation, quality scoring, integration

Run all service tests:
    pytest tests/services/ -v

Run specific service tests:
    pytest tests/services/test_pre_generation_service.py -v
    pytest tests/services/test_ai_research_service.py -v
    pytest tests/services/test_post_generation_service.py -v

Run with coverage:
    pytest tests/services/ --cov=validation.services --cov=research.services --cov-report=html
"""

__all__ = [
    'test_pre_generation_service',
    'test_ai_research_service',
    'test_post_generation_service'
]
