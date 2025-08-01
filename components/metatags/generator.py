"""
Metatags generator for Z-Beam Generator.

Generates Next.js compatible meta tags in YAML frontmatter format.
"""

import logging
import yaml
from components.base.enhanced_component import EnhancedBaseComponent

logger = logging.getLogger(__name__)

class MetatagsGenerator(EnhancedBaseComponent):
    """Generator for Next.js compatible meta tags in YAML frontmatter format with strict validation."""
    
    def _get_prompt_path(self) -> str:
        """Override to use the correct directory name.
        
        Returns:
            str: Path to prompt template
        """
        return "components/metatags/prompt.yaml"
    
    def _post_process(self, content: str) -> str:
        """Post-process the generated metatags, ensuring proper Next.js compatible YAML frontmatter format.
        
        Args:
            content: Raw API response
            
        Returns:
            str: Processed Next.js compatible YAML frontmatter metatags
            
        Raises:
            ValueError: If content is invalid
        """
        # Validate and clean input
        content = self._validate_non_empty(content, "API returned empty or invalid metatags")
        
        # Log the raw content for debugging
        logger.debug(f"Raw metatags content: {content}")
        with open("logs/metatags_raw.log", "a") as f:
            f.write(f"Subject: {self.subject}\n")
            f.write(f"Raw content:\n{content}\n")
            f.write("-" * 80 + "\n")
        
        # Strip any markdown code blocks if present
        content = self._strip_markdown_code_blocks(content)
        
        # Try to use the LLM-generated content first, falling back to our template if needed
        try:
            # If we have YAML content from the LLM, use it
            if '---' in content:
                # Return the properly formatted content
                return content
        except Exception as e:
            logger.warning(f"Error parsing LLM-generated metatags, falling back to template: {e}")
            # Continue with the fallback template below
        
        # FALLBACK: Create structured metatags if parsing the LLM output failed
        # Get template data including extracted keywords
        template_data = self.get_template_data()
        extracted_keywords = template_data.get('extracted_keywords', f"{self.subject}, laser cleaning")
        
        # Make sure we don't duplicate keywords
        if self.subject.lower() in extracted_keywords.lower():
            # Subject is already in the keywords, no need to add it again
            keywords_str = extracted_keywords
        else:
            # Add subject to the keywords if not already present
            keywords_str = f"{self.subject}, {extracted_keywords}"
        
        meta_data = {
            "title": f"{self.subject} Laser Cleaning | Technical Guide",
            "description": f"Technical guide to {self.subject} laser cleaning including specifications, applications, and environmental impact.",
            "keywords": keywords_str,
            "author": self.author_data["author_name"],
            "openGraph": {
                "title": f"{self.subject} Laser Cleaning: Technical Guide",
                "description": f"Comprehensive technical resource on {self.subject} laser cleaning applications, specifications, and best practices.",
                "url": f"https://www.z-beam.com/{self.subject.lower()}-laser-cleaning",
                "siteName": "Z-Beam",
                "images": [{
                    "url": f"https://www.z-beam.com/images/{self.subject.lower()}-laser-cleaning.jpg",
                    "width": 1200,
                    "height": 630,
                    "alt": f"{self.subject} Laser Cleaning"
                }],
                "locale": "en_US",
                "type": "article"
            },
            "twitter": {
                "card": "summary_large_image",
                "title": f"{self.subject} Laser Cleaning: Technical Guide",
                "description": f"Comprehensive technical resource on {self.subject} laser cleaning applications, specifications, and best practices.",
                "images": [f"https://www.z-beam.com/images/{self.subject.lower()}-laser-cleaning.jpg"]
            }
        }
        
        # Validate we have enough metadata fields
        min_tags = self.get_component_config("min_tags")
        flat_fields_count = self._count_metadata_fields(meta_data)
        if flat_fields_count < min_tags:
            raise ValueError(f"Generated only {flat_fields_count} meta properties, minimum required: {min_tags}")
        
        # Check maximum tags limit
        max_tags = self.get_component_config("max_tags")
        if flat_fields_count > max_tags:
            raise ValueError(f"Generated {flat_fields_count} meta properties, maximum allowed: {max_tags}")
        
        # Format as YAML frontmatter
        formatted_yaml = yaml.dump(meta_data, default_flow_style=False, sort_keys=False)
        return f"---\n{formatted_yaml}---\n"
    
    def _count_metadata_fields(self, meta_data: dict, prefix="") -> int:
        """Count the total number of metadata fields, including nested ones.
        
        Args:
            meta_data: The metadata dictionary
            prefix: Prefix for nested fields
            
        Returns:
            int: Total number of fields
        """
        count = 0
        for key, value in meta_data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                count += self._count_metadata_fields(value, full_key)
            elif isinstance(value, list):
                # Count each item in a list as one field (for arrays like images)
                count += 1
            else:
                count += 1
        return count
