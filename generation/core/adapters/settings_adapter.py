"""
Settings Domain Adapter

Enables Generator to work with Settings.yaml following the same
patterns as Materials.yaml. Implements DataSourceAdapter interface.

Usage:
    from generation.core.adapters.settings_adapter import SettingsAdapter
    from generation.core.generator import Generator
    
    adapter = SettingsAdapter()
    generator = Generator(api_client, adapter=adapter)
    result = generator.generate("Copper", "component_summary")
"""

import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from generation.core.adapters.base import DataSourceAdapter

logger = logging.getLogger(__name__)


class SettingsAdapter(DataSourceAdapter):
    """
    Adapter for Settings.yaml data source.
    
    Enables unified generation pipeline to work with settings domain
    using same interface as materials domain.
    """
    
    def __init__(self):
        """Initialize settings adapter."""
        self._data_cache: Optional[Dict] = None
    
    def get_data_path(self) -> Path:
        """Get path to Settings.yaml."""
        return Path("data/settings/Settings.yaml")
    
    def load_all_data(self) -> Dict[str, Any]:
        """Load complete Settings.yaml structure."""
        if self._data_cache is not None:
            return self._data_cache
        
        path = self.get_data_path()
        if not path.exists():
            raise FileNotFoundError(f"Settings.yaml not found: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            self._data_cache = yaml.safe_load(f)
        
        return self._data_cache
    
    def invalidate_cache(self):
        """Clear cached data (call after writes)."""
        self._data_cache = None
    
    def get_item_data(self, identifier: str) -> Dict[str, Any]:
        """
        Load settings data for specific material.
        
        Args:
            identifier: Material name (e.g., "Copper")
            
        Returns:
            Dict with material settings data
            
        Raises:
            ValueError: If material not found in Settings.yaml
        """
        data = self.load_all_data()
        settings = data.get('settings', {})
        
        if identifier not in settings:
            raise ValueError(f"Material '{identifier}' not found in Settings.yaml")
        
        return settings[identifier]
    
    def build_context(self, item_data: Dict[str, Any]) -> str:
        """
        Build context string from settings data.
        
        For settings, we pull key configuration values that inform
        component summary generation.
        """
        context_parts = []
        
        # Add material name if available
        if 'name' in item_data:
            context_parts.append(f"Material: {item_data['name']}")
        
        # Add any machine settings ranges
        if 'machine_settings' in item_data:
            settings = item_data['machine_settings']
            context_parts.append("\nMachine Settings Ranges:")
            for param, values in settings.items():
                if isinstance(values, dict):
                    min_val = values.get('min', 'N/A')
                    max_val = values.get('max', 'N/A')
                    unit = values.get('unit', '')
                    context_parts.append(f"  - {param}: {min_val}-{max_val} {unit}".strip())
        
        return "\n".join(context_parts)
    
    def get_author_id(self, item_data: Dict[str, Any]) -> int:
        """
        Extract author ID from settings data.
        
        Settings inherit author from Materials.yaml, so we look it up there.
        """
        # First check if author is in settings data
        author = item_data.get('author', {})
        if isinstance(author, dict) and 'id' in author:
            return author['id']
        
        # Fall back to looking up in Materials.yaml
        material_name = item_data.get('name', '')
        if material_name:
            try:
                from domains.materials.data_loader import load_material
                material_data = load_material(material_name)
                if material_data:
                    material_author = material_data.get('author', {})
                    if isinstance(material_author, dict):
                        author_id = material_author.get('id')
                        if author_id:
                            return author_id
            except Exception as e:
                logger.debug(f"Could not load author from Materials.yaml: {e}")
        
        # Fail fast - no default author
        raise ValueError(
            "Author ID missing for settings. Check Materials.yaml for author assignment. "
            "See Author Assignment Immutability Policy."
        )
    
    def write_component(
        self,
        identifier: str,
        component_type: str,
        content_data: Any
    ) -> None:
        """
        Write generated component to Settings.yaml atomically.
        
        Args:
            identifier: Material name
            component_type: Component type (e.g., "component_summaries")
            content_data: Content to write
        """
        path = self.get_data_path()
        data = self.load_all_data()
        
        # Ensure settings structure exists
        if 'settings' not in data:
            data['settings'] = {}
        if identifier not in data['settings']:
            data['settings'][identifier] = {}
        
        # Write component data
        data['settings'][identifier][component_type] = content_data
        
        # Atomic write
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            dir=path.parent,
            delete=False,
            suffix='.yaml'
        ) as temp_f:
            yaml.dump(data, temp_f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            temp_path = temp_f.name
        
        Path(temp_path).replace(path)
        self.invalidate_cache()
        
        logger.info(f"💾 Wrote {component_type} to Settings.yaml for {identifier}")
    
    def extract_content(self, raw_response: str, component_type: str) -> Any:
        """
        Extract content from API response based on component type.
        
        For component_summary, returns cleaned text string.
        """
        # Clean up common formatting issues
        content = raw_response.strip()
        content = content.strip('`').strip('"').strip("'")
        
        # Remove any markdown formatting
        if content.startswith('```'):
            lines = content.split('\n')
            content = '\n'.join(lines[1:-1] if lines[-1] == '```' else lines[1:])
        
        return content.strip()


def get_settings_adapter() -> SettingsAdapter:
    """Get singleton settings adapter instance."""
    if not hasattr(get_settings_adapter, '_instance'):
        get_settings_adapter._instance = SettingsAdapter()
    return get_settings_adapter._instance
