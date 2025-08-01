"""
Bullets generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
"""

import logging
from components.base.enhanced_component import EnhancedBaseComponent

logger = logging.getLogger(__name__)

class BulletsGenerator(EnhancedBaseComponent):
    """Generator for bullet point content with strict validation."""
    
    def _post_process(self, content: str) -> str:
        """Post-process the generated bullet points.
        
        Args:
            content: Raw API response
            
        Returns:
            str: Processed bullet points
            
        Raises:
            ValueError: If content is invalid
        """
        # Validate and clean input
        content = self._validate_non_empty(content, "API returned empty or invalid bullet points")
        
        # Validate bullet point format
        lines = content.strip().split('\n')
        bullet_lines = [line for line in lines if line.strip().startswith('-') or line.strip().startswith('•')]
        
        expected_count = self.get_component_config("count")
        
        # Validate count
        if len(bullet_lines) < expected_count:
            raise ValueError(f"Generated only {len(bullet_lines)} bullet points, expected {expected_count}")
        
        return '\n'.join(bullet_lines) + '\n'