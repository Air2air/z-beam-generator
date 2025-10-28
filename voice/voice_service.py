#!/usr/bin/env python3
"""
Centralized Voice Service for Component Generation

Provides normalized, single-point integration of Author Voice across all components.
Eliminates duplicated code and ensures consistent voice application.
"""

import json
import logging
from typing import Dict, Any
from voice.orchestrator import VoiceOrchestrator

logger = logging.getLogger(__name__)


class VoiceService:
    """
    Centralized service for Author Voice integration across all components.
    
    Responsibilities:
    - Single initialization point for VoiceOrchestrator
    - Standardized material context building
    - Component-specific configuration handling
    - Consistent prompt generation interface
    
    Benefits:
    - No duplicated voice initialization code
    - Consistent material context structure
    - Single source of truth for voice parameters
    - Easy to extend with new components
    """
    
    def __init__(self, author_data: Dict[str, Any]):
        """
        Initialize voice service with author data.
        
        Args:
            author_data: Author dictionary with keys: name, country, expertise
            
        Raises:
            ValueError: If author_data is missing required fields
        """
        if not author_data or not author_data.get('country'):
            raise ValueError("Author data with 'country' field is required for voice service")
        
        self.author_name = author_data.get('name', 'Unknown')
        self.author_country = author_data.get('country', 'Unknown')
        self.author_expertise = author_data.get('expertise', 'Laser cleaning technology')
        
        # Initialize VoiceOrchestrator once
        self.voice = VoiceOrchestrator(country=self.author_country)
        
        logger.debug(f"VoiceService initialized: {self.author_name} ({self.author_country})")
    
    def build_material_context(
        self,
        material_name: str,
        frontmatter_data: Dict[str, Any],
        include_machine_settings: bool = False
    ) -> Dict[str, Any]:
        """
        Build standardized material context dictionary.
        
        Args:
            material_name: Material name
            frontmatter_data: Frontmatter data containing properties, category, applications
            include_machine_settings: Whether to include machine settings in context
            
        Returns:
            Standardized material context dictionary
        """
        material_props = frontmatter_data.get('materialProperties', {})
        category = frontmatter_data.get('category', 'material')
        subcategory = frontmatter_data.get('subcategory', '')
        applications = frontmatter_data.get('applications', [])
        
        # Build properties summary (consistent JSON format)
        properties_json = json.dumps(
            {prop: data.get('value') for prop, data in material_props.items() 
             if isinstance(data, dict) and 'value' in data},
            indent=2
        ) if material_props else 'Standard material characteristics'
        
        applications_str = ', '.join(applications[:3]) if applications else 'General cleaning applications'
        
        # Build base context (consistent key naming)
        context = {
            'material_name': material_name,
            'category': category,
            'subcategory': subcategory,
            'properties': properties_json,
            'applications': applications_str
        }
        
        # Optionally include machine settings
        if include_machine_settings:
            machine_settings = frontmatter_data.get('machineSettings', {})
            settings_json = json.dumps(
                {setting: data.get('value') for setting, data in machine_settings.items()
                 if isinstance(data, dict) and 'value' in data},
                indent=2
            ) if machine_settings else 'Standard laser cleaning parameters'
            context['machine_settings'] = settings_json
        
        return context
    
    def get_author_dict(self) -> Dict[str, str]:
        """
        Get standardized author dictionary.
        
        Returns:
            Author dictionary with name, country, expertise
        """
        return {
            'name': self.author_name,
            'country': self.author_country,
            'expertise': self.author_expertise
        }
    
    def generate_prompt(
        self,
        component_type: str,
        material_context: Dict[str, Any],
        **kwargs
    ) -> str:
        """
        Generate component-specific prompt using unified voice system.
        
        Args:
            component_type: Component type (microscopy_description, subtitle, technical_faq_answer)
            material_context: Material context dictionary (from build_material_context)
            **kwargs: Component-specific parameters
            
        Returns:
            Complete prompt string with voice layering applied
            
        Raises:
            Exception: If prompt generation fails
        """
        try:
            prompt = self.voice.get_unified_prompt(
                component_type=component_type,
                material_context=material_context,
                author=self.get_author_dict(),
                **kwargs
            )
            
            logger.debug(f"Generated {component_type} prompt for {material_context.get('material_name')} ({self.author_country})")
            return prompt
            
        except Exception as e:
            logger.error(f"Failed to generate {component_type} prompt: {e}")
            raise
    
    def get_length_variation_range(self) -> tuple:
        """
        Get author-specific length variation range from voice profile.
        
        Returns:
            Tuple of (min_percent, max_percent) for variation range
        """
        try:
            ai_evasion = self.voice.profile.get('ai_evasion_parameters', {})
            char_variation = ai_evasion.get('character_variation', {})
            
            if char_variation and 'total_range' in char_variation:
                variation_range = char_variation['total_range']  # e.g., [30, 170]
                return tuple(variation_range)
            else:
                # Default variation if not specified
                return (80, 120)  # ±20% variation
        except Exception as e:
            logger.warning(f"Could not load author variation for {self.author_country}: {e}")
            return (80, 120)  # Default ±20% variation
    
    def get_component_config(self, component_type: str) -> Dict[str, Any]:
        """
        Get component-specific configuration (intensity, formality, word_count_range, etc.).
        
        Args:
            component_type: Component type name (faq, caption, subtitle, etc.)
            
        Returns:
            Component configuration dictionary with all settings
        """
        return self.voice.get_component_config(component_type)
    
    def get_word_count_range(self, component_type: str) -> tuple:
        """
        Get component-specific word count range from config.
        
        Args:
            component_type: Component type name
            
        Returns:
            Tuple of (min_words, max_words)
        """
        config = self.get_component_config(component_type)
        word_range = config.get('word_count_range', [20, 60])
        return tuple(word_range)
    
    def get_base_word_target(self, component_type: str) -> int:
        """
        Get component-specific base word target (before author variation).
        
        Args:
            component_type: Component type name
            
        Returns:
            Base word count target
        """
        config = self.get_component_config(component_type)
        # Try component-specific base_word_target, else use midpoint of range
        if 'base_word_target' in config:
            return config['base_word_target']
        else:
            word_range = config.get('word_count_range', [20, 60])
            return sum(word_range) // 2  # Midpoint
    
    @property
    def country(self) -> str:
        """Get author country"""
        return self.author_country
    
    @property
    def name(self) -> str:
        """Get author name"""
        return self.author_name
    
    @property
    def expertise(self) -> str:
        """Get author expertise"""
        return self.author_expertise
