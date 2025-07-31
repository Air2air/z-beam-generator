"""
Tags generator for Z-Beam Generator.

MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: Extract keywords and categories from frontmatter
2. KEYWORD EXTRACTION: Parse keywords from frontmatter data
3. TAG GENERATION: Create relevant tags based on article content and type
4. ERROR HANDLING: Gracefully handle missing frontmatter data
5. CATEGORIZATION: Group tags by relevance and type
"""

import logging
import yaml
from typing import Dict, Any, List
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class TagsGenerator(BaseComponent):
    """Generator for article tags."""
    
    def generate(self) -> str:
        """Generate tags content with strict validation.
        
        Returns:
            str: The generated tags
            
        Raises:
            ValueError: If generation fails
        """
        # Strict validation - no fallbacks
        data = self._prepare_data()
        prompt = self._format_prompt(data)
        content = self._call_api(prompt)
        return self._post_process(content)
    
    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare data for tags generation.
        
        Returns:
            Dict[str, Any]: Data for prompt formatting
        """
        data = super()._prepare_data()
        
        # Get component-specific configuration
        component_config = self.get_component_config()
        
        # Add tags-specific configuration
        # Validate required configuration
        required_config = ["max_tags", "min_tags", "tag_categories"]
        for key in required_config:
            if key not in component_config:
                raise ValueError(f"Required config '{key}' missing for tags component")
        
        data.update({
            "max_tags": component_config["max_tags"],
            "min_tags": component_config["min_tags"],
            "tag_categories": component_config["tag_categories"]
        })
        
        # Get frontmatter data and extract keywords
        frontmatter = self.get_frontmatter_data()
        if frontmatter:
            # Extract keywords from frontmatter
            keywords = self._extract_keywords_from_frontmatter(frontmatter)
            data["extracted_keywords"] = keywords
            
            # Include relevant frontmatter fields for context
            relevant_fields = ["category", "applications", "materials", "regions", "industry"]
            for field in relevant_fields:
                if field in frontmatter and frontmatter[field]:
                    data[field] = frontmatter[field]
            
            # Provide complete frontmatter for comprehensive tag generation
            data["all_frontmatter"] = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
            
            logger.info(f"Extracted {len(keywords)} keywords from frontmatter for tag generation")
        else:
            data["extracted_keywords"] = []
            data["all_frontmatter"] = "No frontmatter data available"
            logger.warning("No frontmatter data available for tag generation")
        
        return data
    
    def _extract_keywords_from_frontmatter(self, frontmatter: Dict[str, Any]) -> List[str]:
        """Extract keywords from frontmatter data.
        
        Args:
            frontmatter: The frontmatter data
            
        Returns:
            List[str]: Extracted keywords
        """
        keywords = []
        
        # Fields that commonly contain keywords
        keyword_fields = [
            "keywords", "tags", "applications", "materials", 
            "industries", "processes", "technologies", "regions"
        ]
        
        for field in keyword_fields:
            if field in frontmatter:
                value = frontmatter[field]
                if isinstance(value, list):
                    keywords.extend([str(item).strip() for item in value if item])
                elif isinstance(value, str) and value.strip():
                    # Split on common delimiters
                    for delimiter in [',', ';', '|']:
                        if delimiter in value:
                            keywords.extend([item.strip() for item in value.split(delimiter) if item.strip()])
                            break
                    else:
                        keywords.append(value.strip())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower not in seen:
                seen.add(keyword_lower)
                unique_keywords.append(keyword)
        
        return unique_keywords
    
    def _post_process(self, tags: str) -> str:
        """Post-process the tags.
        
        Args:
            tags: The API response tags
            
        Returns:
            str: The processed tags
        """
        # Basic validation
        if not tags or not tags.strip():
            raise ValueError("API returned empty or invalid tags")
        
        # Ensure tags are in YAML array format
        if not tags.strip().startswith('-') and not tags.strip().startswith('['):
            # Convert to YAML array if not already
            lines = [line.strip() for line in tags.split('\n') if line.strip()]
            if lines:
                tags = '\n'.join([f"- {line}" for line in lines])
        
        return tags.strip()