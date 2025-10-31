#!/usr/bin/env python3
"""
Research Services Module - Import Redirect

The canonical research service is now located at:
research/services/ai_research_service.py

This __init__.py provides backward compatibility.

Last Updated: October 24, 2025
"""

from materials.research.services.ai_research_service import AIResearchEnrichmentService

__all__ = [
    'AIResearchEnrichmentService',
]