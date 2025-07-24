"""
Base class for tag generation with standardized two-stage approach.
"""

import logging
from typing import Dict, Any, List
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class BaseTagGenerator(BaseComponent):
    """Base class for tag generation with two-stage approach."""
    
    def generate(self) -> str:
        """Generate tags using a two-stage approach."""
        try:
            # Get frontmatter data
            frontmatter_data = self.get_frontmatter_data()
            
            if not frontmatter_data:
                logger.warning("No frontmatter data available")
                return self._create_error_markdown("Missing frontmatter data")
                
            # Stage 1: Generate candidate tags
            candidate_tags = self._generate_candidate_tags(frontmatter_data)
            
            # Stage 2: Filter and refine tags based on audience
            final_tags = self._refine_tags(candidate_tags, frontmatter_data)
            
            # Format tags as markdown
            return self._format_tags_as_markdown(final_tags)
            
        except Exception as e:
            logger.error(f"Error generating tags: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _generate_candidate_tags(self, frontmatter_data: Dict[str, Any]) -> List[str]:
        """Generate candidate tags based on frontmatter.
        
        Args:
            frontmatter_data: Frontmatter data dictionary
            
        Returns:
            List of candidate tags
        """
        # This method should be implemented by subclasses
        raise NotImplementedError("Subclasses must implement _generate_candidate_tags")
    
    def _refine_tags(self, candidate_tags: List[str], frontmatter_data: Dict[str, Any]) -> List[str]:
        """Refine tags based on audience and relevance.
        
        Args:
            candidate_tags: List of candidate tags
            frontmatter_data: Frontmatter data dictionary
            
        Returns:
            List of refined tags
        """
        # This method should be implemented by subclasses
        raise NotImplementedError("Subclasses must implement _refine_tags")
    
    def _format_tags_as_markdown(self, tags: List[str]) -> str:
        """Format tags as markdown.
        
        Args:
            tags: List of tags
            
        Returns:
            Markdown-formatted tag content
        """
        if not tags:
            return "<!-- No tags generated -->"
            
        # Format as markdown
        tags_section = "## Tags\n\n"
        tags_formatted = ", ".join([f"`{tag.strip()}`" for tag in tags])
        return tags_section + tags_formatted