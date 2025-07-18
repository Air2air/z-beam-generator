from typing import Dict, Any

class ContextBuilder:
    """Builds context from frontmatter for enhancing content generation."""
    
    @staticmethod
    def extract_frontmatter_context(frontmatter: Dict[str, Any], article_type: str) -> str:
        """
        Extract relevant data from frontmatter to enrich content.
        
        Args:
            frontmatter: The frontmatter dictionary
            article_type: The type of article being generated
            
        Returns:
            Formatted context string
        """
        if not frontmatter:
            return ""
            
        context_parts = []
        
        # Common fields across all types
        if "description" in frontmatter:
            context_parts.append(f"Description: {frontmatter['description']}")
            
        if "keywords" in frontmatter and isinstance(frontmatter["keywords"], list):
            context_parts.append(f"Keywords: {', '.join(frontmatter['keywords'])}")
        
        # Join all context parts
        return "\n".join(context_parts)