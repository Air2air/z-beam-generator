"""
Contamination Research Module

Provides AI-driven research for contamination patterns, compatibility analysis,
laser-specific properties, and detailed contamination data for dedicated pages.

Author: AI Assistant
Date: November 25, 2025
"""

from domains.contaminants.research.base import ContaminationResearcher
from domains.contaminants.research.pattern_researcher import PatternResearcher
from domains.contaminants.research.laser_properties_researcher import LaserPropertiesResearcher
from domains.contaminants.research.factory import ContaminationResearcherFactory

__all__ = [
    'ContaminationResearcher',
    'PatternResearcher',
    'LaserPropertiesResearcher',
    'ContaminationResearcherFactory'
]
