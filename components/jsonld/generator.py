"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODED SECTIONS: Section structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

import json
import logging
from typing import Dict, Any, List
from components.base import BaseComponent

logger = logging.getLogger(__name__)

class JsonLdGenerator(BaseComponent):
    """Generates JSON-LD structured data for articles."""
    
    def generate(self) -> str:
        """Generate JSON-LD structured data based on frontmatter."""
        try:
            # 1. Get frontmatter data using standard method
            frontmatter_data = self.get_frontmatter_data()
            
            if not frontmatter_data:
                logger.warning("No frontmatter data available for JSON-LD generation")
                return self._create_error_markdown("Missing frontmatter data")
                
            # 2. Prepare data (JSON-LD can be generated directly from frontmatter)
            jsonld_data = self._prepare_data(frontmatter_data)
            
            # 3. Post-process and format as JSON-LD (no API call needed)
            return self._post_process(jsonld_data)
            
        except Exception as e:
            logger.error(f"Error generating JSON-LD: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _prepare_data(self, frontmatter_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform frontmatter data into JSON-LD structure."""
        # Extract relevant data from frontmatter
        title = frontmatter_data.get("title", self.subject.capitalize())
        description = frontmatter_data.get("description", "")
        
        # Build basic JSON-LD data
        jsonld = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "description": description,
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": f"https://example.com/{self.subject.lower().replace(' ', '-')}"
            }
        }
        
        # Add author if available
        if "author" in frontmatter_data:
            author = frontmatter_data.get("author", {})
            jsonld["author"] = {
                "@type": "Person",
                "identifier": author.get("author_id"),
                "name": author.get("author_name"),
                "nationality": author.get("author_country"),
                "description": author.get("credentials"),
                "affiliation": author.get("name")
            }
        
        # Add dates if available
        if "datePublished" in frontmatter_data:
            jsonld["datePublished"] = frontmatter_data["datePublished"]
            
        if "dateModified" in frontmatter_data:
            jsonld["dateModified"] = frontmatter_data["dateModified"]
        
        # Add keywords if available
        if "keywords" in frontmatter_data:
            jsonld["keywords"] = frontmatter_data["keywords"]
        
        return jsonld
    
    def _format_prompt(self, data: Dict[str, Any]) -> str:
        """Format prompt template with data (not used in JsonLdGenerator)."""
        # JSON-LD doesn't require API calls, but included for standard conformance
        return ""
    
    def _call_api(self, prompt: str) -> str:
        """Call API with prompt (not used in JsonLdGenerator)."""
        # JSON-LD doesn't require API calls, but included for standard conformance
        return ""
    
    def _post_process(self, jsonld_data: Dict[str, Any]) -> str:
        """Format JSON-LD data as markdown code block."""
        if not jsonld_data:
            return ""
            
        # Format as pretty JSON
        try:
            jsonld_str = json.dumps(jsonld_data, indent=2)
            return f"```json\n{jsonld_str}\n```"
        except Exception as e:
            logger.error(f"Error formatting JSON-LD: {str(e)}")
            return self._create_error_markdown(f"Error formatting JSON-LD: {str(e)}")