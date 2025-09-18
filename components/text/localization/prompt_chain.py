#!/usr/bin/env python3
"""
Localization Prompt Chain System

This module provides essential prompt chaining functionality for all text generation.
Every text generation request MUST include localized persona and formatting prompts.

CRITICAL REQUIREMENT: All text generation (generator or optimizer) must use this system.
"""

import os
from typing import Dict, Any, Optional
from utils.config_loader import load_yaml_config


class LocalizationPromptChain:
    """
    Essential localization prompt chaining system.
    
    This class MUST be used for every text generation request to ensure
    proper cultural and linguistic authenticity.
    """
    
    def __init__(self):
        self.base_path = "optimizer/text_optimization/prompts"
        self.personas_path = f"{self.base_path}/personas"
        self.formatting_path = f"{self.base_path}/formatting"
        
        # Country code mapping for file lookup
        self.country_mapping = {
            'italy': 'italy',
            'indonesia': 'indonesia', 
            'taiwan': 'taiwan',
            'usa': 'usa',
            'united states': 'usa',
            'united states (california)': 'usa'
        }
    
    def get_localization_chain(self, author_info: Dict[str, Any]) -> str:
        """
        REQUIRED METHOD: Get complete localization prompt chain for author.
        
        This method MUST be called for every text generation request.
        
        Args:
            author_info: Author information dictionary with 'country' key
            
        Returns:
            Complete localization prompt chain string
            
        Raises:
            ValueError: If localization prompts cannot be loaded
        """
        country = author_info.get('country', 'USA').lower()
        normalized_country = self.country_mapping.get(country, 'usa')
        
        persona_prompt = self._load_persona_prompt(normalized_country)
        formatting_prompt = self._load_formatting_prompt(normalized_country)
        
        if not persona_prompt or not formatting_prompt:
            raise ValueError(
                f"CRITICAL ERROR: Localization prompts not found for country '{country}'. "
                f"Localization is mandatory for all text generation."
            )
        
        return self._build_localization_chain(persona_prompt, formatting_prompt)
    
    def _load_persona_prompt(self, country: str) -> Optional[str]:
        """Load persona prompt for country."""
        try:
            persona_file = f"{self.personas_path}/{country}_persona.yaml"
            if os.path.exists(persona_file):
                data = load_yaml_config(persona_file, f"persona_{country}")
                return self._extract_persona_content(data)
        except Exception as e:
            print(f"Warning: Could not load persona for {country}: {e}")
        return None
    
    def _load_formatting_prompt(self, country: str) -> Optional[str]:
        """Load formatting prompt for country."""
        try:
            formatting_file = f"{self.formatting_path}/{country}_formatting.yaml"
            if os.path.exists(formatting_file):
                data = load_yaml_config(formatting_file, f"formatting_{country}")
                return self._extract_formatting_content(data)
        except Exception as e:
            print(f"Warning: Could not load formatting for {country}: {e}")
        return None
    
    def _extract_persona_content(self, data: Dict[str, Any]) -> str:
        """Extract key persona characteristics into prompt format."""
        sections = []
        
        if 'persona' in data:
            persona = data['persona']
            sections.append(f"PERSONA: {persona.get('name', 'Unknown')}")
            sections.append(f"BACKGROUND: {persona.get('background', '')}")
            sections.append(f"PERSONALITY: {persona.get('personality', '')}")
            sections.append(f"TONE OBJECTIVE: {persona.get('tone_objective', '')}")
        
        if 'language_patterns' in data:
            patterns = data['language_patterns']
            sections.append("\nLANGUAGE PATTERNS:")
            for key, value in patterns.items():
                if isinstance(value, str):
                    sections.append(f"- {key}: {value}")
                elif isinstance(value, list):
                    sections.append(f"- {key}:")
                    for item in value:
                        sections.append(f"  * {item}")
        
        if 'writing_style' in data and 'guidelines' in data['writing_style']:
            sections.append("\nWRITING GUIDELINES:")
            for guideline in data['writing_style']['guidelines']:
                sections.append(f"- {guideline}")
        
        return '\n'.join(sections)
    
    def _extract_formatting_content(self, data: Dict[str, Any]) -> str:
        """Extract key formatting requirements into prompt format."""
        sections = []
        
        if 'content_constraints' in data:
            constraints = data['content_constraints']
            sections.append("CONTENT CONSTRAINTS:")
            if 'max_word_count' in constraints:
                sections.append(f"- Maximum word count: {constraints['max_word_count']}")
            if 'target_range' in constraints:
                sections.append(f"- Target word range: {constraints['target_range']}")
        
        if 'structural_preferences' in data:
            prefs = data['structural_preferences']
            sections.append("\nSTRUCTURAL PREFERENCES:")
            for key, value in prefs.items():
                sections.append(f"- {key}: {value}")
        
        if 'formatting_patterns' in data:
            patterns = data['formatting_patterns']
            sections.append("\nFORMATTING PATTERNS:")
            for key, value in patterns.items():
                sections.append(f"- {key}: {value}")
        
        return '\n'.join(sections)
    
    def _build_localization_chain(self, persona_prompt: str, formatting_prompt: str) -> str:
        """Build the complete localization prompt chain."""
        return f"""
=== LOCALIZATION REQUIREMENTS (MANDATORY) ===

{persona_prompt}

{formatting_prompt}

=== END LOCALIZATION REQUIREMENTS ===

CRITICAL: You MUST follow ALL localization requirements above. This includes:
1. Writing in the specified persona and tone
2. Following all language patterns and cultural characteristics  
3. Adhering to formatting preferences and structural guidelines
4. Respecting word count constraints
5. Maintaining cultural authenticity throughout

Failure to follow localization requirements will result in content rejection.
"""


# Global instance for use throughout the system
localization_chain = LocalizationPromptChain()


def get_required_localization_prompt(author_info: Dict[str, Any]) -> str:
    """
    REQUIRED FUNCTION: Get localization prompt for any text generation.
    
    This function MUST be called before every text generation request.
    
    Args:
        author_info: Author information dictionary
        
    Returns:
        Complete localization prompt chain
        
    Raises:
        ValueError: If localization cannot be determined
    """
    return localization_chain.get_localization_chain(author_info)


def validate_localization_support(country: str) -> bool:
    """
    Validate that localization support exists for a country.
    
    Args:
        country: Country name to validate
        
    Returns:
        True if localization files exist, False otherwise
    """
    normalized = localization_chain.country_mapping.get(country.lower(), country.lower())
    
    persona_file = f"{localization_chain.personas_path}/{normalized}_persona.yaml"
    formatting_file = f"{localization_chain.formatting_path}/{normalized}_formatting.yaml"
    
    return os.path.exists(persona_file) and os.path.exists(formatting_file)
