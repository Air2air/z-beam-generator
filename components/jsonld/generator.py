"""
JSON-LD generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
Version: 3.0.5
"""

import logging
import yaml
from typing import Dict, Any
from components.base.component import BaseComponent
from components.base.image_handler import ImageHandler
from components.base.utils.slug_utils import SlugUtils

logger = logging.getLogger(__name__)

class JsonldGenerator(BaseComponent):
    """Generator for JSON-LD structured data with strict validation."""
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated JSON-LD YAML.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: YAML content for JSON-LD (like all other components)
            
        Raises:
            ValueError: If content is invalid
        """
        # Extract YAML from response
        extracted_yaml = self._extract_jsonld(content)
        
        if not extracted_yaml:
            raise ValueError("No valid YAML data found in response")
            
        # Parse YAML to validate structure
        try:
            yaml_data = yaml.safe_load(extracted_yaml)
            if not isinstance(yaml_data, dict):
                raise ValueError("JSON-LD YAML must be a valid dictionary structure")
                
            # Apply centralized formatting (pass the YAML string, not dict)
            formatted_content = self.apply_centralized_formatting(extracted_yaml)
            
            # Add YAML frontmatter delimiters for consistency (following frontmatter pattern)
            if not formatted_content.startswith('---'):
                formatted_content = '---\n' + formatted_content
            if not formatted_content.endswith('---'):
                formatted_content = formatted_content.rstrip() + '\n---'
            
            return formatted_content
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in JSON-LD response: {e}")
    
    def _extract_jsonld(self, content: str) -> str:
        """Extract JSON-LD YAML content from the API response.
        
        Args:
            content: API response content
            
        Returns:
            str or None: Extracted YAML content or None if not found
        """
        # Use centralized base component method for YAML extraction
        return self.extract_yaml_content(content)
    
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
        if self.has_schema_feature('generatorConfig', 'jsonld'):
            jsonld_schema = self.get_schema_config('generatorConfig', 'jsonld')
            
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
            
    def _process_image_urls(self, data: Dict[str, Any]) -> None:
        """Process image objects to ensure they have proper URLs.
        
        Args:
            data: The JSON-LD data to process
            
        Returns:
            None: Updates the data in place
        """
        # Get the slug for constructing image URLs
        subject_slug = SlugUtils.create_subject_slug(self.subject)
        # Use centralized base component method for case normalization
        article_type = self.normalize_case(self.article_type, 'lower')
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
                
        # Handle case where there's no image property - use base component data
        else:
            # Use base component's formatted image data instead of frontmatter
            formatted_images = self.get_template_variable('formatted_images')
            if formatted_images:
                image_objects = []
                
                # Add hero image
                if 'hero' in formatted_images:
                    hero_img = {
                        '@type': 'ImageObject',
                        'url': hero_image_url,
                        'caption': formatted_images['hero']['alt']
                    }
                    image_objects.append(hero_img)
                
                # Add closeup image
                if 'closeup' in formatted_images:
                    closeup_img = {
                        '@type': 'ImageObject',
                        'url': closeup_image_url,
                        'caption': formatted_images['closeup']['alt']
                    }
                    image_objects.append(closeup_img)
                
                if image_objects:
                    data['image'] = image_objects
