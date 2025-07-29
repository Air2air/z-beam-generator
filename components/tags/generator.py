"""
Tags generator for Z-Beam Generator.

MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODED SECTIONS: Section structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

import logging
import re
from typing import Dict, Any, List
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class TagsGenerator(BaseComponent):
    """Generator for article tags."""
    
    def generate(self) -> str:
        """Generate tags content.
        
        Returns:
            str: The generated tags
        """
        try:
            # Check if frontmatter already has keywords
            frontmatter = self.get_frontmatter_data()
            if frontmatter and "keywords" in frontmatter:
                keywords = frontmatter["keywords"]
                if keywords:
                    if isinstance(keywords, list):
                        tags = keywords
                    elif isinstance(keywords, str):
                        tags = [k.strip() for k in keywords.split(",")]
                    else:
                        tags = [str(keywords)]
                        
                    if tags:
                        # Extract additional tags from specific frontmatter fields
                        additional_tags = self._extract_additional_tags(frontmatter)
                        all_tags = tags + additional_tags
                        return self._format_tags(all_tags)
            
            # No keywords in frontmatter, generate tags
            # 1. Prepare data for prompt
            data = self._prepare_data()
            
            # 2. Format prompt
            prompt = self._format_prompt(data)
            
            # 3. Call API
            content = self._call_api(prompt)
            
            # 4. Post-process content
            return self._post_process(content)
        except Exception as e:
            logger.error(f"Error generating tags: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare data for tags generation.
        
        Returns:
            Dict[str, Any]: Data for prompt formatting
        """
        data = super()._prepare_data()
        
        # Add tag constraints
        data["max_count"] = self.get_component_config("count", 10)  # Use 'count' from config, fallback to 10
        
        # Add subject-with-dashes for template
        data["subject-with-dashes"] = data["subject"].replace(" ", "-").replace("_", "-")
        
        # Get frontmatter data and include ALL available data dynamically
        frontmatter = self.get_frontmatter_data()
        if frontmatter:
            # Include all frontmatter data for comprehensive tag generation
            for key, value in frontmatter.items():
                if value:  # Only include non-empty values
                    data[key] = value
            
            # Store list of available keys for template iteration
            data["available_keys"] = [k for k, v in frontmatter.items() if v]
            
            # Also provide the complete frontmatter
            data["all_frontmatter"] = frontmatter
        
        return data
    
    def _post_process(self, content: str) -> str:
        """Post-process the tags content.
        
        Args:
            content: The API response content
            
        Returns:
            str: The processed tags
        """
        # Apply standard processing
        processed = super()._post_process(content)
        
        # Extract tags from content
        tags = self._extract_tags(processed)
        
        # Format the tags
        return self._format_tags(tags)
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from content.
        
        Args:
            content: Content with tags
            
        Returns:
            List[str]: List of tags
        """
        # Get max tag count
        max_count = self.get_component_config("count", 10)
        
        # Split by commas, new lines, or bullet points
        tags = []
        
        # Try comma-separated list first
        if "," in content:
            tag_list = content.split(",")
            tags = [t.strip() for t in tag_list if t.strip()]
        else:
            # Try line-by-line or bullet points
            lines = content.split("\n")
            for line in lines:
                # Remove bullet points, dashes, and other markers
                clean_line = re.sub(r'^[-*•#\s]+', '', line.strip())
                if clean_line:
                    tags.append(clean_line)
        
        # Normalize tags (lowercase, remove special characters)
        normalized_tags = []
        for tag in tags:
            # Convert to kebab case (lowercase with hyphens)
            kebab = tag.lower().strip()
            kebab = re.sub(r'[^a-z0-9\-]+', '-', kebab)  # Replace non-alphanumeric with hyphens
            kebab = re.sub(r'-+', '-', kebab)  # Replace multiple hyphens with single hyphen
            kebab = kebab.strip('-')  # Remove leading/trailing hyphens
            
            if kebab and kebab not in normalized_tags:
                normalized_tags.append(kebab)
        
        # Limit to max count
        return normalized_tags[:max_count]
    
    def _extract_additional_tags(self, frontmatter: Dict[str, Any]) -> List[str]:
        """Extract additional tags from specific frontmatter fields.
        
        Args:
            frontmatter: The frontmatter data
            
        Returns:
            List[str]: Additional tags extracted from frontmatter fields
        """
        additional_tags = []
        
        # Extract from name
        if "name" in frontmatter:
            name = frontmatter["name"].strip('"').strip("'").strip()
            words = name.split()
            if len(words) > 2:
                short_name = " ".join(words[:2])
            else:
                short_name = name
            additional_tags.append(short_name)
        
        # Extract from author.author_name
        if "author" in frontmatter and isinstance(frontmatter["author"], dict):
            if "author_name" in frontmatter["author"]:
                author_name = frontmatter["author"]["author_name"].strip('"').strip("'").strip()
                words = author_name.split()
                if len(words) > 2:
                    short_author = " ".join(words[:2])
                else:
                    short_author = author_name
                additional_tags.append(short_author)
        
        # Extract from applications.name
        if "applications" in frontmatter and isinstance(frontmatter["applications"], list):
            for app in frontmatter["applications"]:
                if isinstance(app, dict) and "name" in app:
                    # Apply intelligent shortening to application names
                    name = app["name"].strip('"').strip("'").strip()
                    words = name.split()
                    if len(words) > 2:
                        short_name = " ".join(words[:2])
                    else:
                        short_name = name
                    additional_tags.append(short_name)
        
        # Extract from environmentalImpact.benefit
        if "environmentalImpact" in frontmatter and isinstance(frontmatter["environmentalImpact"], list):
            for impact in frontmatter["environmentalImpact"]:
                if isinstance(impact, dict) and "benefit" in impact:
                    # Apply intelligent shortening to benefits
                    benefit = impact["benefit"].strip('"').strip("'").strip()
                    words = benefit.split()
                    if len(words) > 2:
                        short_benefit = " ".join(words[:2])
                    else:
                        short_benefit = benefit
                    additional_tags.append(short_benefit)
        
        # Extract from regulatoryStandards.code
        if "regulatoryStandards" in frontmatter and isinstance(frontmatter["regulatoryStandards"], list):
            for standard in frontmatter["regulatoryStandards"]:
                if isinstance(standard, dict) and "code" in standard:
                    code = standard["code"].strip('"').strip("'").strip()
                    additional_tags.append(code)
        
        # Extract from composition.type
        if "composition" in frontmatter and isinstance(frontmatter["composition"], list):
            for comp in frontmatter["composition"]:
                if isinstance(comp, dict) and "type" in comp:
                    comp_type = comp["type"].strip('"').strip("'").strip()
                    words = comp_type.split()
                    if len(words) > 2:
                        short_type = " ".join(words[:2])
                    else:
                        short_type = comp_type
                    additional_tags.append(short_type)
        
        # Extract from compatibility.material
        if "compatibility" in frontmatter and isinstance(frontmatter["compatibility"], list):
            for compat in frontmatter["compatibility"]:
                if isinstance(compat, dict) and "material" in compat:
                    material = compat["material"].strip('"').strip("'").strip()
                    words = material.split()
                    if len(words) > 2:
                        short_material = " ".join(words[:2])
                    else:
                        short_material = material
                    additional_tags.append(short_material)
        
        return additional_tags

    def _format_tags(self, tags: List[str]) -> str:
        """Format tags as clean data (no HTML markup) with maximum 2 words per tag.
        
        Args:
            tags: List of tags
            
        Returns:
            str: Formatted tags as clean text with max 2 words each
        """
        # Add heading
        result = "## Tags\n\n"
        
        # Process tags to limit to maximum 2 words each with consistent formatting
        if tags:
            processed_tags = []
            seen_tags = set()  # Prevent duplicates
            
            for tag in tags:
                # Remove quotes and clean the tag
                clean_tag = tag.strip('"').strip("'").strip()
                
                # Split into words and intelligently shorten to max 2 words
                words = clean_tag.split()
                if len(words) > 2:
                    # Apply intelligent shortening (no abbreviations, natural shortening)
                    short_tag = self._intelligent_shorten(words)
                else:
                    short_tag = clean_tag
                
                # Apply consistent title case formatting
                formatted_tag = self._apply_title_case(short_tag)
                
                # Avoid duplicates (case-insensitive check)
                if formatted_tag.lower() not in seen_tags:
                    processed_tags.append(formatted_tag)
                    seen_tags.add(formatted_tag.lower())
            
            result += ", ".join(processed_tags)
        else:
            result += "<!-- No tags available -->"
        
        return result
    
    def _intelligent_shorten(self, words: List[str]) -> str:
        """Intelligently shorten a multi-word tag to 2 words maximum.
        
        Args:
            words: List of words to shorten
            
        Returns:
            str: Shortened tag with natural language flow
        """
        if len(words) <= 2:
            return " ".join(words)
        
        # Apply intelligent rules for natural shortening
        if len(words) >= 3:
            second_word = words[1].lower()
            
            # If second word is "and", "or", "of", etc., skip to third word
            if second_word in ["and", "or", "of", "for", "in", "on", "at", "to", "with"]:
                return f"{words[0]} {words[2]}"
        
        # Default: take first 2 words
        return f"{words[0]} {words[1]}"
    
    def _apply_title_case(self, tag: str) -> str:
        """Apply consistent title case formatting to tags.
        
        Args:
            tag: The tag to format
            
        Returns:
            str: Tag with proper title case
        """
        # Handle special cases for common abbreviations and codes
        special_cases = {
            "astm": "ASTM",
            "nadcap": "NADCAP", 
            "voc": "VOC",
            "xrf": "XRF",
            "osha": "OSHA",
            "carb": "CARB",
            "haz": "HAZ"
        }
        
        words = tag.split()
        formatted_words = []
        
        for word in words:
            word_lower = word.lower()
            if word_lower in special_cases:
                formatted_words.append(special_cases[word_lower])
            else:
                # Regular title case (first letter capitalized)
                formatted_words.append(word.capitalize())
        
        return " ".join(formatted_words)