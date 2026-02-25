"""
Contaminants Domain Coordinator
Orchestrates content generation for contamination pattern removal profiles.

Created: December 26, 2025
Extends DomainCoordinator base class to provide unified generation architecture.
"""

import logging

from shared.domain.base_coordinator import DomainCoordinator

logger = logging.getLogger(__name__)


class ContaminantCoordinator(DomainCoordinator):
    """
    Coordinates content generation for the contaminants domain.
    
    Extends DomainCoordinator to provide:
    - QualityEvaluatedGenerator initialization
    - Winston client integration
    - SubjectiveEvaluator setup
    - Domain config loading
    
    Domain-specific responsibilities:
    - Load contaminants data from Contaminants.yaml
    - Save generated content to Contaminants.yaml
    - Handle batch contaminant generation
    """
    
    @property
    def domain_name(self) -> str:
        """Return domain name for config loading"""
        return "contaminants"
