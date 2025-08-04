"""
Bullets generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
"""

import logging
from components.base.component import BaseComponent
from components.base.utils.formatting import format_bullet_points

logger = logging.getLogger(__name__)

class BulletsGenerator(BaseComponent):
    """Generator for bullet point content with strict validation."""
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated bullet points.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Processed bullet points
            
        Raises:
            ValueError: If content is invalid
        """
        # Extract bullet points from content
        lines = content.strip().split('\n')
        bullet_items = []
        
        # Process lines to extract bullet content
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                # Extract the text after the bullet marker
                bullet_text = line[1:].strip()
                if bullet_text:
                    bullet_items.append(bullet_text)
        
        expected_count = self.get_component_config("count")
        
        # Validate count
        if len(bullet_items) < expected_count:
            raise ValueError(f"Generated only {len(bullet_items)} bullet points, expected {expected_count}")
        
        # Format bullet points using utility function
        return format_bullet_points(bullet_items)