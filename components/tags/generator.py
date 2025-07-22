"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODED SECTIONS: Section structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

# Your imports and code

import logging
from typing import Dict, Any, List
from components.base import BaseComponent

logger = logging.getLogger(__name__)

class TagsGenerator(BaseComponent):
    """Generates tags section for articles."""
    
    def generate(self) -> str:
        """Generate tags section based on frontmatter data."""
        try:
            # 1. Get frontmatter data using standard method
            frontmatter_data = self.get_frontmatter_data()
            
            if not frontmatter_data:
                logger.warning("No frontmatter data available for tags generation")
                return ""
                
            # 2. Prepare data (for tags, we extract directly from frontmatter)
            tags_data = self._prepare_data(frontmatter_data)
            
            if not tags_data:
                logger.info("No tags found in frontmatter")
                return ""
            
            # 3. Post-process and format tags (no API call needed)
            return self._post_process(tags_data)
            
        except Exception as e:
            logger.error(f"Error generating tags: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _prepare_data(self, frontmatter_data: Dict[str, Any]) -> List[str]:
        """Extract tags from frontmatter data."""
        # Extract tags from frontmatter
        tags = frontmatter_data.get("tags", [])
        
        # Add keywords as tags if present and not already in tags
        keywords = frontmatter_data.get("keywords", [])
        if keywords:
            for keyword in keywords:
                if keyword not in tags:
                    tags.append(keyword)
        
        return tags
    
    def _format_prompt(self, data: Dict[str, Any]) -> str:
        """Format prompt template with data (not used in TagsGenerator)."""
        # Tags don't require API calls, but included for standard conformance
        return ""
    
    def _call_api(self, prompt: str) -> str:
        """Call API with prompt (not used in TagsGenerator)."""
        # Tags don't require API calls, but included for standard conformance
        return ""
    
    def _post_process(self, tags: List[str]) -> str:
        """Format tags into markdown."""
        if not tags:
            return ""
            
        # Create tags section
        tags_section = ["## Tags", ""]
        
        # Format tags as badges
        tags_badges = []
        for tag in tags:
            tag_slug = tag.lower().replace(' ', '-')
            tags_badges.append(f'<span class="tag">{tag}</span>')
        
        tags_section.append(' '.join(tags_badges))
        
        return "\n".join(tags_section)