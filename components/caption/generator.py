"""
Caption generator for Z-Beam Generator.

MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODED SECTIONS: Caption structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

import logging
from typing import Dict, Any
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class CaptionGenerator(BaseComponent):
    """Generator for image caption content."""
    
    def generate(self) -> str:
        """Generate caption content.
        
        Returns:
            str: The generated caption
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
            logger.error(f"Error generating caption: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare data for caption generation.
        
        Returns:
            Dict[str, Any]: Data for prompt formatting
        """
        data = super()._prepare_data()
        
        # Get component-specific configuration
        component_config = self.get_component_config()
        
        # Add caption-specific configuration
        data.update({
            "caption_style": component_config.get("caption_style", "descriptive"),
            "max_length": component_config.get("max_length", 200)
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
            import yaml
            data["all_frontmatter"] = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
            
            logger.info(f"Using frontmatter data with {len(frontmatter)} fields for caption generation")
        else:
            data["all_frontmatter"] = "No frontmatter data available"
            logger.warning("No frontmatter data available for caption generation")
        
        return data
    
    def _post_process(self, content: str) -> str:
        """Post-process the caption content.
        
        Args:
            content: The API response content
            
        Returns:
            str: The processed caption
        """
        # Apply standard processing
        processed = super()._post_process(content)
        
        # Ensure caption is concise and well-formatted
        processed = processed.strip()
        
        # Remove any markdown formatting for clean caption
        import re
        processed = re.sub(r'[#*_`]', '', processed)
        
        # Limit length if needed
        max_length = self.get_component_config().get("max_length", 200)
        if len(processed) > max_length:
            processed = processed[:max_length].rsplit(' ', 1)[0] + "..."
        
        return processed
