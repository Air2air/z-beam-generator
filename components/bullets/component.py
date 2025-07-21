"""Bullet points component for Z-Beam articles."""

import logging
from typing import Dict, Any, List

from components.base import BaseComponent

logger = logging.getLogger(__name__)

class BulletsComponent(BaseComponent):
    """Component for generating bullet point sections in articles."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str = "deepseek"):
        """Initialize the bullets component."""
        super().__init__(context, schema, ai_provider)
        self.logger.info(f"BulletsComponent initialized for subject: {self.subject}")
    
    def generate(self) -> str:
        """Generate bullet points for the article.
        
        Returns:
            Markdown-formatted bullet points
        """
        try:
            # Get frontmatter data
            frontmatter_data = self.get_frontmatter_data()
            
            # Format the prompt
            prompt = self._format_prompt(frontmatter_data)
            
            # Generate bullet points
            bullets_markdown = self.api_client.generate_content(
                prompt, 
                provider=self.ai_provider
            )
            
            return bullets_markdown
        except Exception as e:
            logger.error(f"Error generating bullet points: {str(e)}")
            return f"""
## Key Benefits of Laser Cleaning for {self.subject.capitalize()}

- Non-contact cleaning preserves material integrity
- Environmentally friendly with no chemical waste
- Precision targeting for complex geometries
- Minimal thermal impact on base material

## Safety Considerations

- Standard laser safety protocols must be followed
- Proper ventilation is required to remove ablated particles
"""
    
    def _format_prompt(self, frontmatter: Dict[str, Any]) -> str:
        """Format the prompt for bullet point generation.
        
        Args:
            frontmatter: Frontmatter data dictionary
            
        Returns:
            Formatted prompt string
        """
        # Extract relevant data
        safety_considerations = frontmatter.get("safetyConsiderations", [])
        if isinstance(safety_considerations, str):
            safety_considerations = [safety_considerations]
        
        # Build the prompt
        prompt = f"""
Generate bullet point lists for a technical article about {self.subject} laser cleaning.

FORMAT:
- Use standard markdown bullet point syntax
- Group bullets into labeled sections
- Keep each bullet concise (1-2 lines)

CONTENT REQUIREMENTS:
1. Create a "Key Benefits" section with 4-5 bullet points about the benefits of using lasers for cleaning {self.subject}

2. Create a "Safety Considerations" section with these safety points:
{self._format_safety(safety_points=safety_considerations)}

Keep bullets informative, technical, and well-formatted.
"""
        return prompt
    
    def _format_safety(self, safety_points: List[str]) -> str:
        """Format safety considerations for the prompt.
        
        Args:
            safety_points: List of safety points
            
        Returns:
            Formatted safety points string
        """
        if not safety_points:
            return "- Standard laser safety protocols must be followed\n- Proper ventilation is essential"
        
        formatted_points = []
        for point in safety_points:
            if point and isinstance(point, str):
                formatted_points.append(f"- {point}")
        
        # If we have no valid points, add defaults
        if not formatted_points:
            formatted_points = ["- Standard laser safety protocols must be followed", 
                               "- Proper ventilation is essential"]
        
        return "\n".join(formatted_points)