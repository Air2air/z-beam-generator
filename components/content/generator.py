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
import os
from typing import Dict, Any
import yaml
from components.base import BaseComponent

logger = logging.getLogger(__name__)

class ContentGenerator(BaseComponent):
    """Generates main article content based on frontmatter data."""
    
    def generate(self) -> str:
        """Generate main content for the article."""
        try:
            # 1. Get frontmatter data using standard method
            frontmatter_data = self.get_frontmatter_data()
            
            if not frontmatter_data:
                logger.warning("No frontmatter data available for content generation")
                return self._create_error_markdown("Missing frontmatter data")
                
            # 2. Prepare data for prompt
            prompt_data = self._prepare_data(frontmatter_data)
            
            # 3. Format prompt
            prompt = self._format_prompt(prompt_data)
            
            # 4. Call API
            content = self._call_api(prompt)
            
            # 5. Post-process content
            return self._post_process(content)
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _prepare_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for prompt formatting."""
        # Create base data with required fields
        prompt_data = {
            "subject": self.subject,
            "article_type": self.article_type,
            "intensity": 2,  # Default intensity level
            "country_specific_instructions": "",  # Will be populated from country files
            "frontmatter": ""  # Will be populated if frontmatter is available
        }
        
        # Add author information and country
        try:
            # Get author_id from context
            author_id = self.context.get("author_id", 1)
            
            # Load authors from JSON file
            with open("components/author/authors.json", "r") as f:
                authors = json.load(f)
                
            # Find the author by ID
            author = next((a for a in authors if a["id"] == author_id), None)
            if author:
                prompt_data["author_name"] = author["name"]
                prompt_data["author_title"] = author.get("title", "")
                prompt_data["country"] = author["country"]
                logger.info(f"Using country '{author['country']}' from author '{author['name']}'")
                
                # Load country-specific instructions
                country_file = f"components/content/prompts/{author['country'].lower().replace(' ', '_')}.yaml"
                try:
                    if os.path.exists(country_file):
                        with open(country_file, 'r') as f:
                            country_config = yaml.safe_load(f)
                            prompt_data["country_specific_instructions"] = country_config.get("instructions", "")
                            # Use intensity from country config or default to 2
                            prompt_data["intensity"] = country_config.get("intensity", 2)
                            logger.info(f"Loaded country-specific instructions for {author['country']} with intensity {prompt_data['intensity']}")
                    else:
                        logger.warning(f"No country-specific instructions found for {author['country']}")
                        prompt_data["intensity"] = 2
                        prompt_data["country_specific_instructions"] = f"Focus on global technical standards with minimal references to {author['country']}."
                except Exception as e:
                    logger.warning(f"Failed to load country-specific instructions: {str(e)}")
                    prompt_data["intensity"] = 2
                    prompt_data["country_specific_instructions"] = f"Focus on global technical standards with minimal references to {author['country']}."
                
            else:
                # Author not found - this should raise an error since no fallbacks are allowed
                logger.error(f"Author with ID {author_id} not found in authors.json")
                raise ValueError(f"Author with ID {author_id} not found in authors.json")
                
        except Exception as e:
            logger.error(f"Error loading author data: {str(e)}")
            raise ValueError(f"Failed to load required author data: {str(e)}")
        
        # Add frontmatter if available
        frontmatter_data = self.get_frontmatter_data()
        if frontmatter_data:
            # Convert frontmatter to YAML for prompt
            prompt_data["frontmatter"] = yaml.safe_dump(frontmatter_data, 
                                                      default_flow_style=False, 
                                                      sort_keys=False)
        
        # Add any other data passed in
        if data:
            prompt_data.update(data)
        
        return prompt_data
    
    def _format_prompt(self, data: Dict[str, Any]) -> str:
        """Format prompt template with data."""
        template = self.load_prompt_template()
        
        try:
            return template.format(**data)
        except KeyError as e:
            logger.error(f"Missing key in prompt data: {e}")
            # Fallback to a simple prompt if template formatting fails
            return f"Write a detailed article about {data.get('subject', 'the topic')}."
    
    def _call_api(self, prompt: str) -> str:
        """Call API with prompt."""
        return self.api_client.generate_content(prompt)
    
    def _post_process(self, content: str) -> str:
        """Post-process API response."""
        if not content:
            return ""
            
        # Ensure content starts with a header if not already
        if not content.strip().startswith("#"):
            frontmatter_data = self.get_frontmatter_data()
            title = frontmatter_data.get("title", self.subject.capitalize())
            content = f"# {title}\n\n{content}"
        
        return content
    
    def _get_country_prompt(self, country, min_words=None, max_words=None):
        try:
            with open(f"components/content/prompts/{country.lower()}.txt") as f:
                prompt = f.read().strip()
                if min_words or max_words:
                    prompt += "\n"
                    if min_words:
                        prompt += f"\nMinimum words: {min_words}."
                    if max_words:
                        prompt += f"\nMaximum words: {max_words}."
                return prompt
        except FileNotFoundError:
            return ""

    def generate(self) -> str:
        frontmatter = self.get_frontmatter_data()
        country = frontmatter.get("author", {}).get("author_country", "").lower()
        min_words = frontmatter.get("min_words")
        max_words = frontmatter.get("max_words")
        country_prompt = self._get_country_prompt(country, min_words, max_words)
        main_prompt = self._format_prompt(self._prepare_data(frontmatter))
        full_prompt = f"{country_prompt}\n\n{main_prompt}" if country_prompt else main_prompt

        logger.debug(f"Using country prompt for: '{country}'")
        logger.debug(f"Country prompt content:\n{country_prompt}")

        content = self._call_api(full_prompt)
        return self._post_process(content)