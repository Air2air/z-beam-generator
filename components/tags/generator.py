"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODED SECTIONS: Section structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

import logging
from typing import Dict, Any, List
from components.base.tag_generator import BaseTagGenerator

logger = logging.getLogger(__name__)

class TagsGenerator(BaseTagGenerator):
    """Generates tags section for articles using the two-stage approach."""
    
    def _generate_candidate_tags(self, frontmatter_data: Dict[str, Any]) -> List[str]:
        """Generate candidate tags based on frontmatter."""
        # Extract tags from frontmatter
        tags = frontmatter_data.get("tags", [])
        
        # Add keywords as tags if present and not already in tags
        keywords = frontmatter_data.get("keywords", [])
        if keywords:
            for keyword in keywords:
                if keyword not in tags:
                    tags.append(keyword)
                    
        # If no tags or keywords were found, try to derive from other fields
        if not tags:
            logger.debug("No explicit tags/keywords found, generating from other frontmatter fields")
            
            # Try to derive tags from categories if present
            categories = frontmatter_data.get("categories", [])
            if categories:
                tags.extend(categories)
                
            # Try to derive tags from subject and article type
            subject = frontmatter_data.get("subject", self.subject)
            if subject and subject not in tags:
                tags.append(subject)
                
            article_type = frontmatter_data.get("article_type", self.article_type)
            if article_type and article_type not in tags:
                tags.append(article_type)
                
        return tags
    
    def _refine_tags(self, candidate_tags: List[str], frontmatter_data: Dict[str, Any]) -> List[str]:
        """Refine tags based on audience and relevance.
        
        Args:
            candidate_tags: List of candidate tags
            frontmatter_data: Frontmatter data dictionary
            
        Returns:
            List of refined tags
        """
        # If no tags were found, return empty list
        if not candidate_tags:
            return []
            
        # Get audience from frontmatter (default to general)
        audience = frontmatter_data.get("audience", "general")
        
        # Get max tag count from component config (default to 10)
        component_config = self.get_component_config()
        max_tags = component_config.get("max_count", 10)
        
        # Filter to maximum number of tags
        refined_tags = candidate_tags[:max_tags]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in refined_tags:
            if tag and tag.strip() and tag.lower() not in seen:
                unique_tags.append(tag)
                seen.add(tag.lower())
                
        return unique_tags
    
    def _format_tags_as_markdown(self, tags: List[str]) -> str:
        """Format tags as markdown with custom styling.
        
        Args:
            tags: List of tags
            
        Returns:
            Markdown-formatted tag content
        """
        if not tags:
            return "<!-- No tags generated -->"
            
        # Create tags section
        tags_section = ["## Tags", ""]
        
        # Format tags as badges
        tags_badges = []
        for tag in tags:
            tag_slug = tag.lower().replace(' ', '-')
            tags_badges.append(f'<span class="tag">{tag}</span>')
        
        tags_section.append(' '.join(tags_badges))
        
        return "\n".join(tags_section)