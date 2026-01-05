"""
Settings Domain Coordinator
Orchestrates content generation for laser parameter settings profiles.

Created: December 26, 2025
Extends DomainCoordinator base class to provide unified generation architecture.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional
import yaml

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
    
    def _create_data_loader(self):
        """
        Create settings data loader.
        
        Note: Settings use load_settings_data() function, not class-based loader.
        Returns None since data loading is handled via _load_domain_data() (base class).
        """
        return None
    
    def _load_settings_data(self) -> Dict:
        """Load settings data - wrapper for _load_domain_data for backwards compatibility"""
        return self._load_domain_data()
    
    def _get_item_data(self, item_id: str) -> Dict:
        """Get setting data from Settings.yaml"""
        settings_data = self._load_domain_data()
        if item_id not in settings_data['settings']:
            raise ValueError(f"Setting '{item_id}' not found in Settings.yaml")
        return settings_data['settings'][item_id]
    
    def _save_content(self, item_id: str, component_type: str, content: str, author_id: Optional[int] = None) -> None:
        """Save content to Settings.yaml - handled by QualityEvaluatedGenerator"""
        # Note: QualityEvaluatedGenerator already saves to Settings.yaml
        # This method exists to satisfy abstract base class
        pass
    
    def generate_setting_content(
        self,
        setting_id: str,
        component_type: str,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate content for a specific setting and component type.
        
        Wrapper for universal generate_content method with settings-specific naming.
        
        Args:
            setting_id: Setting identifier (e.g., "power", "speed", "frequency")
            component_type: Type of content to generate (e.g., "description")
            force_regenerate: Whether to regenerate even if content exists
            
        Returns:
            Dict with generation results (see DomainCoordinator.generate_content)
        """
        return self.generate_content(setting_id, component_type, force_regenerate)
    
    def generate_all_components_for_setting(
        self,
        setting_id: str,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate all enabled component types for a setting.
        
        Args:
            setting_id: Setting identifier
            force_regenerate: Whether to regenerate existing content
            
        Returns:
            Dict with results for each component type
        """
        results = {}
        enabled_types = [
            comp_type for comp_type, config in self.domain_config['component_types'].items()
            if config.get('enabled', True)
        ]
        
        logger.info(
            f"Generating {len(enabled_types)} component types for {setting_id}: "
            f"{enabled_types}"
        )
        
        for component_type in enabled_types:
            try:
                result = self.generate_setting_content(
                    setting_id=setting_id,
                    component_type=component_type,
                    force_regenerate=force_regenerate
                )
                results[component_type] = result
            except Exception as e:
                logger.error(
                    f"Failed to generate {component_type} for {setting_id}: {e}"
                )
                results[component_type] = {
                    'success': False,
                    'error': str(e)
                }
        
        return results
    
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
