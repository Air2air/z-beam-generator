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
    
    def _load_settings_data(self) -> Dict:
        """Backwards-compatible wrapper — prefer _load_domain_data() directly."""
        return self._load_domain_data()

    def generate_setting_content(
        self,
        setting_id: str,
        component_type: str,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate content for a specific setting and component type.
        Alias for generate_content() with settings-specific naming.
        """
        return self.generate_content(setting_id, component_type, force_regenerate)

    def generate_all_components_for_setting(
        self,
        setting_id: str,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate all component types for a setting.
        Delegates to base generate_all_components() using prompt-directory discovery.
        """
        return self.generate_all_components(setting_id, force_regenerate)
    
    def get_setting_data(self, setting_id: str) -> Optional[Dict[str, Any]]:
        """Get setting data for context."""
        try:
            return self._get_item_data(setting_id)
        except ValueError:
            return None
    
    def list_settings(self) -> list:
        """Get list of all setting IDs."""
        settings_data = self._load_domain_data()
        return list(settings_data['settings'].keys())
