#!/usr/bin/env python3
"""
Settings Frontmatter Generator

Modular generator for settings frontmatter following materials architecture.
Uses specialized modules for metadata, machine settings, challenges, etc.

Data Source: data/settings/Settings.yaml
Output: frontmatter/settings/*.yaml

Architecture:
- Loads from Settings.yaml (single source of truth)
- Uses modular components (metadata, settings, challenges, description)
- Trivial YAML-to-YAML export (no generation, just extraction)
- Fail-fast on missing data
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import yaml

from export.core.base_generator import BaseFrontmatterGenerator, GenerationContext
from shared.validation.errors import GenerationError, ConfigurationError

logger = logging.getLogger(__name__)


class SettingsFrontmatterGenerator(BaseFrontmatterGenerator):
    """
    Settings frontmatter generator.
    
    Generates structured frontmatter for laser cleaning machine settings
    per material, including parameters, challenges, and descriptions.
    """
    
    def __init__(
        self,
        api_client: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize settings generator with modular components.
        
        Args:
            api_client: API client (not used - trivial export)
            config: Configuration dictionary (optional)
            **kwargs: Additional parameters
        """
        super().__init__(
            content_type='settings',
            api_client=api_client,
            config=config,
            **kwargs
        )
        
        # Initialize modules
        from .modules import (
            MetadataModule,
            SettingsModule,
            ChallengesModule,
            DescriptionModule,
            AuthorModule,
            EEATModule,
        )
        
        self.metadata_module = MetadataModule()
        self.settings_module = SettingsModule()
        self.challenges_module = ChallengesModule()
        self.description_module = DescriptionModule()
        self.author_module = AuthorModule()
        self.eeat_module = EEATModule()
        
        self.logger.info("SettingsFrontmatterGenerator initialized with 6 modules")
    
    def _load_type_data(self):
        """
        Load settings data from Settings.yaml
        
        Raises:
            ConfigurationError: If Settings.yaml not found or invalid
        """
        # Load from centralized data file
        data_file = Path('data/settings/Settings.yaml')
        
        if not data_file.exists():
            raise ConfigurationError(f"Settings.yaml not found: {data_file}")
        
        try:
            with open(data_file, 'r') as f:
                data = yaml.safe_load(f)
                self._settings = data.get('settings', {})
                
                if not self._settings:
                    raise ConfigurationError("settings not found in Settings.yaml")
                
                self.logger.info(f"Loaded {len(self._settings)} materials from {data_file}")
                
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in {data_file}: {e}")
    
    def _validate_identifier(self, identifier: str) -> bool:
        """
        Validate that material settings exist in Settings.yaml.
        
        Args:
            identifier: Material name
            
        Returns:
            True if material settings found
            
        Raises:
            GenerationError: If material not found
        """
        if identifier not in self._settings:
            available = ', '.join(sorted(self._settings.keys())[:10])  # Show first 10
            raise GenerationError(
                f"Settings for material '{identifier}' not found. "
                f"Available (sample): {available}..."
            )
        return True
    
    def _get_schema_name(self) -> str:
        """
        Get schema name for validation.
        
        Returns:
            Schema name for this content type
        """
        return 'settings_frontmatter'
    
    def _get_output_filename(self, identifier: str) -> str:
        """
        Get output filename for frontmatter file.
        
        Args:
            identifier: Material name
            
        Returns:
            Output filename (e.g., "aluminum.yaml")
        """
        # Normalize identifier: lowercase, replace spaces with hyphens
        normalized = identifier.lower().replace(' ', '-')
        return f"{normalized}.yaml"
    
    def _build_frontmatter_data(
        self,
        identifier: str,
        context: GenerationContext
    ) -> Dict[str, Any]:
        """
        Build complete settings frontmatter using modular components.
        
        This is a trivial YAML-to-YAML export - all data already exists
        in Settings.yaml (machine_settings, challenges, settings_description)
        
        Args:
            identifier: Material name
            context: Generation context with author data
            
        Returns:
            Complete frontmatter dictionary
            
        Raises:
            GenerationError: If frontmatter construction fails
        """
        try:
            self.logger.info(f"Building frontmatter for settings: {identifier}")
            
            # Get settings data for this material
            settings_data = self._settings[identifier]
            
            # Build frontmatter using modules
            frontmatter = {}
            
            # 1. Metadata (name, slug, title)
            metadata = self.metadata_module.generate(identifier)
            frontmatter.update(metadata)
            
            # 2. Machine Settings
            if 'machine_settings' in settings_data:
                # Note: SettingsModule expects material_data structure,
                # but Settings.yaml is already per-material
                machine_settings = self.settings_module.generate(identifier, settings_data)
                if machine_settings:
                    frontmatter['machine_settings'] = machine_settings
            
            # 3. Material Challenges
            challenges = self.challenges_module.generate(settings_data)
            if challenges:
                frontmatter['challenges'] = challenges
            
            # 4. Settings Description
            description = self.description_module.generate(settings_data)
            if description:
                frontmatter['settings_description'] = description
            
            # 5. EEAT (Experience, Expertise, Authoritativeness, Trust)
            eeat = self.eeat_module.generate(settings_data)
            if eeat:
                frontmatter['eeat'] = eeat
            
            # 6. Author data
            author = self.author_module.generate(settings_data)
            if author:
                frontmatter['author'] = author
            elif context.author_data:
                frontmatter['author'] = context.author_data
            
            # 7. Layout and metadata
            frontmatter['layout'] = 'settings'
            frontmatter['_metadata'] = {
                'generator': 'SettingsFrontmatterGenerator',
                'version': '2.0.0',
                'content_type': 'settings',
                'export_method': 'modular_trivial_export',
                'data_source': 'Settings.yaml'
            }
            
            # Add voice tracking if author data present
            if 'author' in frontmatter:
                if 'voice' not in frontmatter['_metadata']:
                    frontmatter['_metadata']['voice'] = {}
                frontmatter['_metadata']['voice'].update({
                    'author_name': frontmatter['author'].get('name', 'Unknown'),
                    'author_country': frontmatter['author'].get('country', 'Unknown'),
                    'voice_applied': True,
                    'content_type': 'setting'
                })
            
            self.logger.info(f"✅ Built complete frontmatter for: {identifier}")
            return frontmatter
            
        except KeyError as e:
            raise GenerationError(
                f"Missing required field in settings data for '{identifier}': {e}"
            )
        except Exception as e:
            raise GenerationError(
                f"Failed to build settings frontmatter for '{identifier}': {e}"
            )
