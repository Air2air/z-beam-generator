"""
Settings Domain Coordinator
Orchestrates content generation for laser parameter settings profiles.

Created: December 26, 2025
Extends DomainCoordinator base class to provide unified generation architecture.
"""

import logging

from shared.domain.base_coordinator import DomainCoordinator

logger = logging.getLogger(__name__)


class SettingCoordinator(DomainCoordinator):
    """
    Coordinates content generation for the settings domain.
    
    Extends DomainCoordinator to provide:
    - QualityEvaluatedGenerator initialization
    - Winston client integration
    - SubjectiveEvaluator setup
    - Domain config loading
    
    Domain-specific responsibilities:
    - Load settings data from Settings.yaml
    - Save generated content to Settings.yaml
    - Handle batch setting generation
    """
    
    @property
    def domain_name(self) -> str:
        """Return domain name for config loading"""
        return "settings"
