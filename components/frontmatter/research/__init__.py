#!/usr/bin/env python3
"""
Frontmatter Research System

Complete research system for material properties and laser machine settings.
Provides intelligent property discovery and research capabilities for frontmatter generation.

Key Components:
- PropertyValueResearcher: Research exact property values with confidence scoring
- MachineSettingsResearcher: Calculate optimal laser parameters based on material properties
- UnifiedMaterialResearcher: Combined interface for complete material research
- MaterialPropertyResearchSystem: Property discovery and recommendation system

Author: GitHub Copilot
Date: September 25, 2025
"""

from .property_value_researcher import PropertyValueResearcher, PropertyResult, PropertyDataMetric, ResearchContext
from .machine_settings_researcher import MachineSettingsResearcher, MachineSettingResult, LaserProcessingContext
from .unified_research_interface import UnifiedMaterialResearcher, UnifiedResearchResult

__all__ = [
    'PropertyValueResearcher', 
    'PropertyResult', 
    'PropertyDataMetric', 
    'ResearchContext',
    'MachineSettingsResearcher', 
    'MachineSettingResult', 
    'LaserProcessingContext',
    'UnifiedMaterialResearcher', 
    'UnifiedResearchResult'
]