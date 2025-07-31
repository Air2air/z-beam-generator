"""
Bullets generator for Z-Beam Generator.

MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODED SECTIONS: Section structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

import logging
import yaml
from typing import Dict, Any
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class BulletsGenerator(BaseComponent):
    """Generator for bullet point content."""
    
    def generate(self) -> str:
        """Generate bullet points content.
        
        Returns:
            str: The generated bullet points
        """
        try:
            # 1. Prepare data for prompt
            data = self._prepare_data()
            
            # 2. Format prompt
            prompt = self._format_prompt(data)
            
            # 3. Call API
            content = self._call_api(prompt)
            
            # 4. Post-process content
            return self._post_process(content)
        except Exception as e:
            logger.error(f"Error generating bullets: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare data for bullet points generation.
        
        Returns:
            Dict[str, Any]: Data for prompt formatting
        """
        data = super()._prepare_data()
        
        # Get component-specific configuration
        component_config = self.get_component_config()
        
        # Add bullets-specific configuration
        data.update({
            "bullet_count": component_config.get("bullet_count", 5),
            "bullet_style": component_config.get("bullet_style", "concise")
        })
        
        # Get frontmatter data and include ALL available structured data
        frontmatter = self.get_frontmatter_data()
        if frontmatter:
            # Include all frontmatter data dynamically
            for key, value in frontmatter.items():
                if value:  # Only include non-empty values
                    data[key] = value
            
            # Store list of available keys for template iteration
            data["available_keys"] = [k for k, v in frontmatter.items() if v]
            
            # Also provide the complete frontmatter as formatted YAML
            data["all_frontmatter"] = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
            
            logger.info(f"Using frontmatter data with {len(frontmatter)} fields for bullets generation")
        else:
            data["all_frontmatter"] = "No frontmatter data available"
            logger.warning("No frontmatter data available for bullets generation")
        
        return data
    
    def _post_process(self, content: str) -> str:
        """Post-process the bullets content.
        
        Args:
            content: The API response content
            
        Returns:
            str: The processed bullets
        """
        # Apply standard processing
        processed = super()._post_process(content)
        
        # Ensure content is in bullet format
        if not any(line.strip().startswith(('*', '-', '•')) for line in processed.split('\n')):
            # Convert to bullet points if not already
            lines = [line.strip() for line in processed.split('\n') if line.strip()]
            if lines:
                processed = '\n'.join([f"• {line}" for line in lines])
        
        return processed