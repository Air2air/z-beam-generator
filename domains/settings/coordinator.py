"""
Settings Domain Coordinator
Orchestrates content generation for laser parameter settings profiles.

Created: December 26, 2025
Extends DomainCoordinator base class to provide unified generation architecture.
"""

import logging
from typing import Any, Dict, Optional

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

    def list_settings(self) -> list:
        """Get list of all setting IDs."""
        return list(self._load_domain_data().get('settings', {}).keys())

    def get_setting_data(self, setting_id: str) -> Optional[Dict[str, Any]]:
        """Get setting data for context."""
        try:
            return self._get_item_data(setting_id)
        except ValueError:
            return None

    def generate_setting_content(
        self,
        setting_id: str,
        component_type: str,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """Legacy wrapper around generate_content()."""
        return self.generate_content(setting_id, component_type, force_regenerate)
