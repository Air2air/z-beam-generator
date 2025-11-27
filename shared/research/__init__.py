"""
Shared Research Infrastructure

Generic research base classes, factory, and utilities for AI-powered content discovery.
Reusable across all domains (materials, settings, contaminants, regions, etc.)

Author: AI Assistant  
Date: November 26, 2025 (Extracted from materials domain)
"""

from shared.research.base import ContentResearcher
from shared.research.factory import ResearcherFactory
from shared.research.faq_topic_researcher import FAQTopicResearcher

__all__ = [
    'ContentResearcher',
    'ResearcherFactory',
    'FAQTopicResearcher',
]
