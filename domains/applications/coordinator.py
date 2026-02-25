"""
Applications Domain Coordinator
Orchestrates content generation for applications profiles.

Created: February 17, 2026
Extends DomainCoordinator base class to provide unified generation architecture.
"""

import logging

from shared.domain.base_coordinator import DomainCoordinator

logger = logging.getLogger(__name__)


class ApplicationsCoordinator(DomainCoordinator):
    """
    Coordinates content generation for the applications domain.

    Extends DomainCoordinator to provide:
    - QualityEvaluatedGenerator initialization
    - Winston client integration
    - SubjectiveEvaluator setup
    - Domain config loading

    Domain-specific responsibilities:
    - Load applications data from Applications.yaml
    - Save generated content to Applications.yaml
    - Handle batch applications generation
    """

    @property
    def domain_name(self) -> str:
        """Return domain name for config loading"""
        return "applications"
