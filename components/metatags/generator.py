"""
Metatags generator for Z-Beam Generator.

Generates Next.js compatible meta tags in YAML frontmatter format.
Enhanced with local formatting and validation.
"""

import logging
import yaml
import re
from components.base.component import BaseComponent
from components.metatags.validation import validate_article_specific_fields
from components.base.utils.formatting import format_yaml_object

logger = logging.getLogger(__name__)

class MetatagsGenerator(BaseComponent):
    """Generator for Next.js compatible meta tags in YAML frontmatter format with enhanced local processing."""
    
    def _get_prompt_path(self) -> str:
        """Override to use the correct directory name.
        
        Returns:
            str: Path to prompt template
        """
        return "components/metatags/prompt.yaml"
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated metatags, ensuring proper Next.js compatible YAML frontmatter format.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Processed Next.js compatible YAML frontmatter metatags
            
        Raises:
            ValueError: If content is invalid
        """
        # Log the raw content for debugging
        logger.debug(f"Raw metatags content: {content}")
        with open("logs/metatags_raw.log", "a") as f:
            f.write(f"Subject: {self.subject}\n")
            f.write(f"Raw content:\n{content}\n")
            f.write("-" * 80 + "\n")
        
        # Try to parse the YAML to validate and normalize
        try:
            # Extract content between --- markers if present
            if '---' in content:
                yaml_content = content.split('---')[1].strip()
            else:
                yaml_content = content.strip()
                
            # Parse the YAML content
            parsed = yaml.safe_load(yaml_content)
            if not isinstance(parsed, dict):
                raise ValueError("Metatags must be a valid YAML dictionary")
            
            # Apply local formatting and validation rules
            parsed = self._apply_formatting_rules(parsed)
            
            # Add missing required fields
            parsed = self._ensure_required_fields(parsed)
            
            # Ensure proper URL formatting
            parsed = self._format_urls(parsed)
            
            # Validate fields based on article type
            validate_article_specific_fields(self.article_type, getattr(self, 'category', None), parsed)
            
            # Convert back to YAML and format with --- delimiters
            # YAML formatting is now handled by the base component and format_yaml_object
            formatted_yaml = format_yaml_object(parsed)
            with open("logs/metatags_yaml.log", "a") as f:
                f.write(f"Subject: {self.subject}\n")
                f.write(f"Formatted content:\n{formatted_yaml}\n")
                f.write("-" * 80 + "\n")
                
            return f"---\n{formatted_yaml}---"
            
        except Exception as e:
            # Log the error
            logger.error(f"Error processing metatags: {e}")
            with open("logs/metatags_error.log", "a") as f:
                f.write(f"Subject: {self.subject}\n")
                f.write(f"Error: {e}\n")
                f.write(f"Content causing error:\n{content}\n")
                f.write("-" * 80 + "\n")
            raise ValueError(f"Metatags generation failed: {e}")
    
    def _apply_formatting_rules(self, parsed: dict) -> dict:
        """Apply formatting rules to metatags.
        
        Args:
            parsed: Parsed YAML content
            
        Returns:
            dict: Formatted metatags
        """
        # Ensure title field follows proper format
        if "title" in parsed:
            if not parsed["title"].startswith(f"{self.subject} "):
                parsed["title"] = f"{self.subject} Laser Cleaning | Technical Guide"
        else:
            parsed["title"] = f"{self.subject} Laser Cleaning | Technical Guide"
        
        # Ensure description follows proper format
        if "description" in parsed:
            # If description is too short, replace with standard format
            if len(parsed["description"]) < 50:
                parsed["description"] = f"Technical guide to {self.subject} laser cleaning including specifications, applications, and environmental impact."
        else:
            parsed["description"] = f"Technical guide to {self.subject} laser cleaning including specifications, applications, and environmental impact."
        
        # Ensure author is present
        if "author" not in parsed:
            parsed["author"] = self.author_data.get("author_name", "Z-Beam Technology")
        
        # Process frontmatter data
        template_data = self.get_template_data()
        frontmatter = template_data.get('frontmatter_data', {})
        
        # Create or enhance keywords field
        if "keywords" not in parsed or not parsed["keywords"]:
            # Use frontmatter keywords if available
            if frontmatter and "keywords" in frontmatter:
                if isinstance(frontmatter["keywords"], list):
                    parsed["keywords"] = ", ".join(frontmatter["keywords"])
                else:
                    parsed["keywords"] = frontmatter["keywords"]
            else:
                # Create basic keywords
                parsed["keywords"] = f"{self.subject}, laser cleaning, surface treatment"
        
        return parsed
    
    def _ensure_required_fields(self, parsed: dict) -> dict:
        """Ensure all required fields are present.
        
        Args:
            parsed: Parsed YAML content
            
        Returns:
            dict: Enhanced metatags with required fields
        """
        # Create openGraph if missing
        if "openGraph" not in parsed:
            parsed["openGraph"] = {
                "title": f"{self.subject} Laser Cleaning: Technical Guide",
                "description": parsed.get("description", f"Comprehensive technical resource on {self.subject} laser cleaning applications"),
                "url": f"https://www.z-beam.com/{self._format_slug(self.subject)}-laser-cleaning",
                "siteName": "Z-Beam",
                "images": [
                    {
                        "url": f"https://www.z-beam.com/images/{self._format_slug(self.subject)}-laser-cleaning-hero.jpg",
                        "width": 1200,
                        "height": 630,
                        "alt": f"{self.subject} Laser Cleaning"
                    }
                ],
                "locale": "en_US",
                "type": "article"
            }
        else:
            # Ensure openGraph has required fields
            og = parsed["openGraph"]
            if "title" not in og:
                og["title"] = f"{self.subject} Laser Cleaning: Technical Guide"
            if "description" not in og:
                og["description"] = parsed.get("description", f"Comprehensive technical resource on {self.subject} laser cleaning applications")
            if "url" not in og:
                og["url"] = f"https://www.z-beam.com/{self._format_slug(self.subject)}-laser-cleaning"
            if "siteName" not in og:
                og["siteName"] = "Z-Beam"
            if "images" not in og or not og["images"]:
                og["images"] = [
                    {
                        "url": f"https://www.z-beam.com/images/{self._format_slug(self.subject)}-laser-cleaning-hero.jpg",
                        "width": 1200,
                        "height": 630,
                        "alt": f"{self.subject} Laser Cleaning"
                    }
                ]
            if "locale" not in og:
                og["locale"] = "en_US"
            if "type" not in og:
                og["type"] = "article"
        
        # Create twitter if missing
        if "twitter" not in parsed:
            parsed["twitter"] = {
                "card": "summary_large_image",
                "title": parsed["openGraph"].get("title", f"{self.subject} Laser Cleaning: Technical Guide"),
                "description": parsed["openGraph"].get("description", parsed.get("description", "")),
                "images": [parsed["openGraph"]["images"][0]["url"]] if parsed["openGraph"].get("images") else []
            }
        
        # For material article types, include application information
        if self.article_type == 'material' and ('application' not in parsed or not isinstance(parsed['application'], dict)):
            parsed['application'] = {
                "name": f"{self.subject} Laser Cleaning",
                "description": f"Removal of contaminants, oxides, and coatings from {self.subject} surfaces using high-precision laser technology."
            }
        
        return parsed
    
    def _format_urls(self, parsed: dict) -> dict:
        """Format URLs to ensure they follow the correct pattern.
        
        Args:
            parsed: Parsed YAML content
            
        Returns:
            dict: Metatags with properly formatted URLs
        """
        # Format slug
        slug = self._format_slug(self.subject)
        
        # Update openGraph URL
        if "openGraph" in parsed and "url" in parsed["openGraph"]:
            url = parsed["openGraph"]["url"]
            if self.subject.lower() not in url.lower():
                parsed["openGraph"]["url"] = f"https://www.z-beam.com/{slug}-laser-cleaning"
            else:
                # Ensure URL is properly formatted
                parsed["openGraph"]["url"] = re.sub(
                    r'(https?://www\.z-beam\.com/).*?(-laser-cleaning)',
                    f'\\1{slug}\\2',
                    parsed["openGraph"]["url"]
                )
        
        # Update image URLs
        if "openGraph" in parsed and "images" in parsed["openGraph"]:
            for i, image in enumerate(parsed["openGraph"]["images"]):
                if "url" in image:
                    # Ensure URL is lowercase and follows pattern
                    image_type = "hero"
                    if "closeup" in image["url"].lower():
                        image_type = "closeup"
                    
                    image["url"] = f"https://www.z-beam.com/images/{slug}-laser-cleaning-{image_type}.jpg"
        
        # Update twitter images
        if "twitter" in parsed and "images" in parsed["twitter"]:
            for i, image_item in enumerate(parsed["twitter"]["images"]):
                # Handle both string URLs and image objects
                if isinstance(image_item, dict) and "url" in image_item:
                    # It's an image object with a URL property
                    image_url = image_item["url"]
                    image_type = "hero"
                    if "closeup" in image_url.lower():
                        image_type = "closeup"
                    
                    image_item["url"] = f"https://www.z-beam.com/images/{slug}-laser-cleaning-{image_type}.jpg"
                    parsed["twitter"]["images"][i] = image_item
                else:
                    # It's a string URL
                    image_url = image_item
                    image_type = "hero"
                    if isinstance(image_url, str) and "closeup" in image_url.lower():
                        image_type = "closeup"
                    
                    parsed["twitter"]["images"][i] = f"https://www.z-beam.com/images/{slug}-laser-cleaning-{image_type}.jpg"
        
        return parsed
    
    def _format_slug(self, text: str) -> str:
        """Format text as a URL slug.
        
        Args:
            text: Text to format
            
        Returns:
            str: Formatted slug
        """
        return text.lower().replace(" ", "-").replace("_", "-")
    
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
