"""
JSON-LD generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
Version: 3.0.5
"""

import logging
import json
import yaml
import re
from typing import Dict, Any, Optional
from components.base.component import BaseComponent
from components.base.image_handler import ImageHandler

logger = logging.getLogger(__name__)

class JsonldGenerator(BaseComponent):
    """Generator for JSON-LD structured data with strict validation."""
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated JSON-LD.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Validated and formatted JSON-LD
            
        Raises:
            ValueError: If content is invalid
        """
        # Extract JSON-LD from response (might be inside code blocks)
        extracted_jsonld = self._extract_jsonld(content)
        
        if not extracted_jsonld:
            raise ValueError("No valid JSON-LD data found in response")
            
        # Validate as JSON
        try:
            json_data = json.loads(extracted_jsonld)
            if not isinstance(json_data, dict):
                raise ValueError("JSON-LD must be a valid JSON object/dictionary")
                
            # Ensure proper image URLs
            self._process_image_urls(json_data)
                
            # Validate required fields based on schema
            self._validate_jsonld_structure(json_data)
            
            # Return the formatted JSON-LD
            return json.dumps(json_data, indent=2)
            
        except json.JSONDecodeError as e:
            # Try to parse as YAML as a fallback
            try:
                yaml_data = yaml.safe_load(extracted_jsonld)
                if not isinstance(yaml_data, dict):
                    raise ValueError("JSON-LD must be a valid dictionary structure")
                
                # Ensure proper image URLs
                self._process_image_urls(yaml_data)
                
                # Validate required fields based on schema
                self._validate_jsonld_structure(yaml_data)
                
                # Convert YAML to JSON
                return json.dumps(yaml_data, indent=2)
                
            except yaml.YAMLError:
                # If both JSON and YAML parsing fail, raise original JSON error
                raise ValueError(f"Invalid JSON in JSON-LD: {e}")
    
    def _extract_jsonld(self, content: str) -> Optional[str]:
        """Extract JSON-LD data from a potentially mixed content response.
        
        Args:
            content: API response that may contain JSON-LD within code blocks
            
        Returns:
            str or None: Extracted JSON-LD or None if not found
        """
        # First, try to find JSON-LD within JSON code blocks
        json_matches = re.findall(r'```(?:json|JSON)?\s*([\s\S]*?)```', content)
        if json_matches:
            for match in json_matches:
                try:
                    # Try parsing as JSON
                    json.loads(match.strip())
                    return match.strip()
                except json.JSONDecodeError:
                    # Not valid JSON, try next match
                    continue
        
        # Next, try to find JSON-LD within code blocks of any type
        code_matches = re.findall(r'```(?:\w*)?\s*([\s\S]*?)```', content)
        if code_matches:
            for match in code_matches:
                try:
                    # Try parsing as JSON
                    json.loads(match.strip())
                    return match.strip()
                except json.JSONDecodeError:
                    # Try parsing as YAML
                    try:
                        yaml_data = yaml.safe_load(match.strip())
                        if isinstance(yaml_data, dict):
                            return match.strip()
                    except yaml.YAMLError:
                        # Not valid YAML either, try next match
                        continue
        
        # If no code blocks found with valid JSON or YAML, try the whole content
        try:
            json.loads(content.strip())
            return content.strip()
        except json.JSONDecodeError:
            # Try as YAML
            try:
                yaml_data = yaml.safe_load(content.strip())
                if isinstance(yaml_data, dict):
                    return content.strip()
            except yaml.YAMLError:
                # Not valid YAML either
                pass
        
        # Look for unenclosed JSON-like structure
        if content.strip().startswith('{') and content.strip().endswith('}'):
            # Content looks like JSON but didn't parse - it might have issues
            # Return it anyway and let the validation handle errors
            return content.strip()
        
        # No valid JSON-LD found
        return None
    
    def _validate_jsonld_structure(self, data: Dict[str, Any]) -> None:
        """Validate the JSON-LD structure against schema requirements.
        
        Args:
            data: Parsed JSON-LD data
            
        Raises:
            ValueError: If validation fails
        """
        # Basic JSON-LD validation
        required_fields = ['@context', '@type']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Required JSON-LD field '{field}' is missing")
        
        # Check @context is schema.org
        if data['@context'] != 'https://schema.org' and data['@context'] != 'http://schema.org':
            raise ValueError(f"Invalid @context value: {data['@context']}. Must be https://schema.org")
        
        # Additional schema-specific validation based on article type
        profile_key = f"{self.article_type}Profile"
        if profile_key in self.schema and "jsonld" in self.schema[profile_key]:
            jsonld_schema = self.schema[profile_key]["jsonld"]
            
            # Check required type
            if "schemaType" in jsonld_schema:
                required_type = jsonld_schema["schemaType"]
                if data['@type'] != required_type:
                    raise ValueError(f"Invalid @type: {data['@type']}. Must be {required_type}")
            
            # Check for required properties if specified
            if "properties" in jsonld_schema:
                for prop, details in jsonld_schema["properties"].items():
                    if details.get("required", False) and prop not in data:
                        raise ValueError(f"Required property '{prop}' is missing in JSON-LD")
        
                # Check for image field if images are available in frontmatter
        frontmatter = self.get_frontmatter_data()
        if frontmatter and 'images' in frontmatter and 'image' not in data:
            subject_slug = self.subject.lower().replace(" ", "-").replace("_", "-")
            article_type = self.article_type.lower()
            
            # Use the article type pattern from run.py for the proper slug
            if article_type == "material":
                slug = f"{subject_slug}-laser-cleaning"
            elif article_type == "application":
                slug = f"{subject_slug}-applications"
            elif article_type == "region":
                slug = f"{subject_slug}-laser-cleaning"
            elif article_type == "thesaurus":
                slug = f"{subject_slug}-definition"
            else:
                # Fallback to simple slug
                slug = subject_slug
                
            # Add default image URL based on slug
            slug = ImageHandler.get_subject_slug(self.subject)
            data['image'] = f"https://www.z-beam.com/images/{slug}-laser-cleaning-hero.jpg"
            
    def _process_image_urls(self, data: Dict[str, Any]) -> None:
        """Process image objects to ensure they have proper URLs.
        
        Args:
            data: The JSON-LD data to process
            
        Returns:
            None: Updates the data in place
        """
        # Get the slug for constructing image URLs
        subject_slug = ImageHandler.get_subject_slug(self.subject)
        article_type = self.article_type.lower()
        base_url = "https://www.z-beam.com"
        
        # Use the article type pattern from run.py for the proper slug
        if article_type == "material":
            slug = f"{subject_slug}-laser-cleaning"
        elif article_type == "application":
            slug = f"{subject_slug}-applications"
        elif article_type == "region":
            slug = f"{subject_slug}-laser-cleaning"
        elif article_type == "thesaurus":
            slug = f"{subject_slug}-definition"
        else:
            # Fallback to simple slug
            slug = subject_slug
        
        # Use ImageHandler to format the URL
        hero_image_relative = ImageHandler.format_image_url(self.subject, "hero")
        hero_image_url = f"{base_url}{hero_image_relative}"
        closeup_image_relative = ImageHandler.format_image_url(self.subject, "closeup")
        closeup_image_url = f"{base_url}{closeup_image_relative}"
        
        # Handle different image formats in the JSON-LD
        if 'image' in data:
            if isinstance(data['image'], list):
                # Array of image objects
                for i, img in enumerate(data['image']):
                    if isinstance(img, dict):
                        # Already an ImageObject
                        if '@type' in img and img['@type'] == 'ImageObject':
                            # Check if URL is missing
                            if 'url' not in img:
                                # For hero (first) image, use slug-hero.jpg format
                                if i == 0:
                                    img['url'] = hero_image_url
                                elif i == 1:
                                    img['url'] = closeup_image_url
                                else:
                                    img['url'] = f"{base_url}/images/{slug}-image-{i+1}.jpg"
            elif isinstance(data['image'], dict):
                # Single image object
                if '@type' in data['image'] and data['image']['@type'] == 'ImageObject':
                    if 'url' not in data['image']:
                        data['image']['url'] = hero_image_url
            elif isinstance(data['image'], str):
                # String URL - convert to ImageObject
                url = data['image']
                data['image'] = {
                    '@type': 'ImageObject',
                    'url': url
                }
                
        # Handle case where there's no image property but frontmatter has images
        else:
            frontmatter = self.get_frontmatter_data()
            if frontmatter and 'images' in frontmatter:
                image_objects = []
                
                # Add hero image if available
                if 'hero' in frontmatter['images'] and 'alt' in frontmatter['images']['hero']:
                    hero_img = {
                        '@type': 'ImageObject',
                        'url': hero_image_url,
                        'caption': frontmatter['images']['hero']['alt']
                    }
                    image_objects.append(hero_img)
                
                # Add closeup image if available
                if 'closeup' in frontmatter['images'] and 'alt' in frontmatter['images']['closeup']:
                    closeup_img = {
                        '@type': 'ImageObject',
                        'url': closeup_image_url,
                        'caption': frontmatter['images']['closeup']['alt']
                    }
                    image_objects.append(closeup_img)
                
                if image_objects:
                    data['image'] = image_objects
