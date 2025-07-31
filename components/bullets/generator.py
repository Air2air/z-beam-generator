"""
Bullets generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
"""

import logging
from typing import Dict, Any
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class BulletsGenerator(BaseComponent):
    """Generator for bullet point content with strict validation."""
    
    def generate(self) -> str:
        """Generate bullet points content with strict validation.
        
        Returns:
            str: The generated bullet points
            
        Raises:
            ValueError: If generation fails
        """
        # Strict validation - no fallbacks
        data = self._prepare_data()
        prompt = self._format_prompt(data)
        content = self._call_api(prompt)
        return self._post_process(content)
    
    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare data for bullet points generation with strict validation.
        
        Returns:
            Dict[str, Any]: Validated data for generation
            
        Raises:
            ValueError: If required data is missing
        """
        data = super()._prepare_data()
        
        # Get component configuration
        component_config = self.get_component_config()
        
        # Validate required configuration
        if "count" not in component_config:
            raise ValueError("Required config 'count' missing for bullets component")
        
        data["count"] = component_config["count"]
        
        return data
    
    def _post_process(self, content: str) -> str:
        """Post-process the generated bullet points.
        
        Args:
            content: Raw API response
            
        Returns:
            str: Processed bullet points
            
        Raises:
            ValueError: If content is invalid
        """
        if not content or not content.strip():
            raise ValueError("API returned empty or invalid bullet points")
        
        # Validate bullet point format
        lines = content.strip().split('\n')
        bullet_lines = [line for line in lines if line.strip().startswith('-') or line.strip().startswith('•')]
        
        expected_count = self.get_component_config("count")
        if len(bullet_lines) < expected_count:
            raise ValueError(f"Generated {len(bullet_lines)} bullet points, expected {expected_count}")
        
        return content.strip()