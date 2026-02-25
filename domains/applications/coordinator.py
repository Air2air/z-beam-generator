"""
Applications Domain Coordinator
Orchestrates content generation for applications profiles.

Created: February 17, 2026
Extends DomainCoordinator base class to provide unified generation architecture.
"""

import logging
from typing import Any, Dict, Optional

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

    def _load_applications_data(self) -> Dict:
        """Backwards-compatible wrapper — prefer _load_domain_data() directly."""
        return self._load_domain_data()

    def generate_application_content(
        self,
        application_id: str,
        component_type: str,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate content for a specific application and component type.
        Alias for generate_content() with applications-specific naming.
        """
        return self.generate_content(application_id, component_type, force_regenerate)

    def generate_all_components_for_application(
        self,
        application_id: str,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate all component types for an application.
        Delegates to base generate_all_components() using prompt-directory discovery.
        """
        return self.generate_all_components(application_id, force_regenerate)

    def get_application_data(self, application_id: str) -> Optional[Dict[str, Any]]:
        """Get application data for context."""
        try:
            return self._get_item_data(application_id)
        except ValueError:
            return None

    def list_applications(self) -> list:
        """Get list of all application IDs."""
        applications_data = self._load_domain_data()
        return list(applications_data['applications'].keys())
