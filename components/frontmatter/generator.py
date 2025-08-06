"""
Frontmatter generator for Z-Beam Generator.

Enhanced implementation with robust error handling and auto-recovery.
"""

import logging
import yaml
import re
from typing import Dict, Any, List, Optional, Tuple

from components.base.component import BaseComponent
from components.base.utils.validation import (
    validate_length, validate_required_fields, validate_category_consistency
)
from components.base.utils.formatting import format_frontmatter_with_comment
from components.base.utils.slug_utils import SlugUtils
from components.base.utils.content_formatter import ContentFormatter
from components.base.image_handler import ImageHandler

logger = logging.getLogger(__name__)

class FrontmatterGenerator(BaseComponent):
    """Generator for article frontmatter with robust validation and auto-recovery."""
    
    def _get_prompt_path(self) -> str:
        """Override to use the correct directory name.
        
        Returns:
            str: Path to prompt template
        """
        return "components/frontmatter/prompt.yaml"
    
    def _get_base_data(self) -> dict:
        """Get base data for the prompt template."""
        data = super()._get_base_data()
        
        # Add subject-name-with-hyphens to support the image URL formatting
        data['subject-name-with-hyphens'] = SlugUtils.create_subject_slug(self.subject)
        
        return data
    
    def _ensure_schema_structure(self, parsed: dict) -> dict:
        """Ensure the frontmatter follows the schema structure for the article type.
        
        Args:
            parsed: The parsed frontmatter data
            
        Returns:
            dict: The frontmatter with enforced schema structure
        """
        profile_key = f"{self.article_type}Profile"
        
        if profile_key not in self.schema:
            logger.warning(f"No schema found for article type: {self.article_type}")
            return parsed
            
        schema_structure = self.schema[profile_key]
        
        # Check for generatorConfig section which might contain structure information
        if "generatorConfig" in schema_structure:
            config = schema_structure["generatorConfig"]
            
            # Extract any field mapping or structure information
            if "fieldContentMapping" in config:
                field_mappings = config["fieldContentMapping"]
                
                # Ensure all mapped fields exist in the frontmatter
                for field_name in field_mappings.keys():
                    if field_name not in parsed:
                        logger.warning(f"Adding missing field from schema mapping: {field_name}")
                        parsed[field_name] = f"Information about {field_name} for {self.subject}"
            
            # Check for research structure if available
            if "research" in config and "dataStructure" in config["research"]:
                data_structure = config["research"]["dataStructure"]
                
                # Validate complex nested structures based on schema
                for field_name, field_structure in data_structure.items():
                    if field_name in parsed:
                        # Check if field should be an object but isn't
                        if field_structure.get("type") == "object" and not isinstance(parsed[field_name], dict):
                            logger.warning(f"Field {field_name} should be an object, converting")
                            parsed[field_name] = {}
                            
                        # Check if field should be an array but isn't
                        if field_structure.get("type") == "array" and not isinstance(parsed[field_name], list):
                            logger.warning(f"Field {field_name} should be an array, converting")
                            parsed[field_name] = []
        
        return parsed
        
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated frontmatter using centralized formatting.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Validated and formatted frontmatter
            
        Raises:
            ValueError: If content is invalid
        """
        # First, apply basic content normalization
        content = ContentFormatter.normalize_yaml_content(content)
        
        # Check if the content seems to be markdown with a code block instead of raw YAML
        if content.startswith('```yaml') or content.startswith('```'):
            # Extract the YAML content from the code block
            lines = content.split('\n')
            content_lines = []
            in_yaml_block = False
            for line in lines:
                if line.startswith('```yaml') or line.startswith('```'):
                    if in_yaml_block:
                        break  # End of YAML block
                    in_yaml_block = True
                    continue
                if in_yaml_block:
                    content_lines.append(line)
            
            if content_lines:
                content = '\n'.join(content_lines)
            else:
                logger.warning("Failed to extract YAML content from markdown code block")
        
        # Attempt to parse as YAML to validate structure
        try:
            parsed = yaml.safe_load(content)
            if not isinstance(parsed, dict):
                raise ValueError("Frontmatter must be a valid YAML dictionary")
        except yaml.YAMLError as e:
            # Additional debugging
            logger.error(f"YAML parsing error: {e}")
            logger.error(f"Content causing error: {content}")
            raise ValueError(f"Invalid YAML in frontmatter: {e}")
        
        # Handle materialProfile wrapper (sometimes the model wraps everything in this object)
        if len(parsed.keys()) == 1 and 'materialProfile' in parsed and isinstance(parsed['materialProfile'], dict):
            logger.warning("Found 'materialProfile' wrapper, extracting contents")
            profile_data = parsed.pop('materialProfile')
            # Merge the profile data into the main dictionary
            parsed.update(profile_data)
            logger.info(f"Extracted fields from materialProfile: {list(profile_data.keys())}")
        
        # Special handling for common error: using 'title' instead of 'name'
        if 'name' not in parsed and 'title' in parsed:
            # Auto-fix instead of error
            logger.warning("Found 'title' field but 'name' is required. Copying 'title' to 'name'.")
            parsed['name'] = parsed['title']
        
        # Ensure name field only contains the subject name
        if 'name' in parsed:
            if parsed['name'] != self.subject:
                logger.warning(f"Name field '{parsed['name']}' doesn't match subject '{self.subject}'. Setting to subject only.")
                parsed['name'] = self.subject
        
        # Apply centralized formatting from BaseComponent
        formatted_content = self.apply_centralized_formatting(content, parsed)
        
        # Re-parse the formatted content to validate it
        try:
            final_parsed = yaml.safe_load(formatted_content)
            if not isinstance(final_parsed, dict):
                raise ValueError("Formatted frontmatter must be a valid YAML dictionary")
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error after formatting: {e}")
            raise ValueError(f"Invalid YAML in formatted frontmatter: {e}")
        
        # Validate required fields are present based on the article type schema
        profile_key = f"{self.article_type}Profile"
        
        if profile_key not in self.schema:
            raise ValueError(f"Missing schema for article type: {self.article_type}. Schema should contain {profile_key}.")
            
        validation = self.schema[profile_key]["validation"]["frontmatter"]
        required_fields = validation["requiredFields"]
        
        # Log what we're checking for
        logger.info(f"Validating frontmatter for article type '{self.article_type}' with required fields: {required_fields}")
        
        # Check what fields we actually have
        logger.info(f"Frontmatter contains fields: {list(final_parsed.keys())}")
        
        # Validate length constraints after formatting
        if "title" in final_parsed:
            validate_length(final_parsed["title"], 0, 100, "Title", "chars")
        
        if "headline" in final_parsed:
            validate_length(final_parsed["headline"], 0, 150, "Headline", "chars")
        
        if "description" in final_parsed:
            validate_length(final_parsed["description"], 0, 250, "Description", "chars")
        
        # Keywords should be limited in number and length
        if "keywords" in final_parsed and isinstance(final_parsed["keywords"], list):
            if len(final_parsed["keywords"]) > 15:
                final_parsed["keywords"] = final_parsed["keywords"][:15]
                logger.warning("Truncated keywords list to 15 items")
            
            for keyword in final_parsed["keywords"]:
                validate_length(keyword, 0, 50, "Keyword", "chars")
        
        # Auto-fix missing fields with standardized values from ContentFormatter
        for field in required_fields:
            if field not in parsed:
                logger.warning(f"Auto-fixing missing required field: {field}")
                
                # Add appropriate placeholder based on field type
                if field == "name":
                    parsed[field] = self.subject
                elif field == "title":
                    parsed[field] = f"{self.subject} Laser Cleaning | Technical Guide"
                elif field == "headline":
                    parsed[field] = f"Technical guide to {self.subject} for laser cleaning applications"
                elif field == "description":
                    parsed[field] = f"A comprehensive technical overview of {self.subject} for laser cleaning applications, including properties, composition, and optimal processing parameters."
                # Website field removed as per request
                elif field == "author":
                    # Use author data from BATCH_CONFIG
                    if self.author_data and "author_name" in self.author_data:
                        parsed[field] = {
                            "name": self.author_data["author_name"],
                            "country": self.author_data["author_country"],
                            "credentials": self.author_data.get("author_title", "Laser Cleaning Expert") + 
                                          (", " + self.author_data.get("author_specialties", [""])[0] if self.author_data.get("author_specialties") else "")
                        }
                        # Add author ID if available
                        if "author_id" in self.author_data:
                            parsed[field]["id"] = self.author_data["author_id"]
                    else:
                        # Fallback if author data is not available
                        parsed[field] = {
                            "name": "Material Science Institute", 
                            "country": "United States",
                            "credentials": f"Expert in {self.subject} and Laser Cleaning Technology"
                        }
                elif field == "keywords":
                    keywords = [
                        f"{self.subject.lower()} laser cleaning",
                        f"{self.subject.lower()} surface treatment",
                        "laser ablation",
                        "non-contact cleaning",
                        "industrial laser applications",
                        "precision surface cleaning"
                    ]
                    
                    # Add category-based keywords
                    if hasattr(self, 'category') and self.category:
                        keywords.append(f"{self.category.lower()} laser cleaning")
                        keywords.append(f"{self.category.lower()} materials")
                        
                    # Add type-specific keywords
                    if self.article_type == "material":
                        keywords.extend([
                            "material properties",
                            "surface preparation",
                            "contaminant removal",
                            "high-temperature materials"
                        ])
                    
                    parsed[field] = keywords
                elif field == "category":
                    if hasattr(self, 'category') and self.category:
                        parsed[field] = self.category
                    else:
                        parsed[field] = "unknown"
                elif field == "chemicalProperties":
                    # Use material formula service if available
                    try:
                        from components.base.material_formula_service import get_material_formula, get_material_symbol
                        formula = get_material_formula(self.subject)
                        symbol = get_material_symbol(self.subject)
                        
                        if formula and symbol:
                            parsed[field] = {
                                "formula": formula,
                                "symbol": symbol,
                                "materialType": getattr(self, 'category', "unknown")
                            }
                        else:
                            parsed[field] = {"formula": "N/A", "symbol": "N/A", "materialType": getattr(self, 'category', "unknown")}
                    except (ImportError, Exception):
                        parsed[field] = {"formula": "N/A", "symbol": "N/A", "materialType": getattr(self, 'category', "unknown")}
                elif field == "properties":
                    parsed[field] = {
                        "density": "See technical datasheet",
                        "meltingPoint": "See technical datasheet",
                        "hardness": "See technical datasheet",
                        "thermalConductivity": "See technical datasheet",
                        "laserType": "Nd:YAG or fiber laser (1064nm)",
                        "wavelength": "1064 nm (IR range)",
                        "fluenceRange": "1-10 J/cm²"
                    }
                elif field == "applications":
                    parsed[field] = [
                        {"name": "Industrial Cleaning", "description": f"Surface preparation of {self.subject} components for manufacturing processes"},
                        {"name": "Precision Maintenance", "description": f"Removal of contaminants from {self.subject} surfaces without damage"},
                        {"name": "Surface Preparation", "description": f"Pre-treatment of {self.subject} for coating or bonding applications"}
                    ]
                elif field == "environmentalImpact":
                    parsed[field] = [
                        {"benefit": "Chemical Reduction", "description": "Eliminates need for hazardous chemical cleaners, reducing environmental impact"},
                        {"benefit": "Energy Efficiency", "description": "Consumes less energy than traditional cleaning methods, with precise energy application"}
                    ]
                elif field == "technicalSpecifications":
                    parsed[field] = {
                        "powerRange": "100-1000W (pulsed)",
                        "pulseDuration": "10-200ns",
                        "wavelength": "1064nm ±2nm",
                        "spotSize": "0.05-3mm",
                        "repetitionRate": "10-500kHz",
                        "fluenceRange": "0.5-20 J/cm²",
                        "safetyClass": "IV (enclosed system)"
                    }
                elif field == "outcomes":
                    parsed[field] = [
                        {"result": "High purity surface", "metric": "SEM contamination analysis"},
                        {"result": "Precise surface preparation", "metric": "Surface profilometry measurements"}
                    ]
                elif field == "composition":
                    parsed[field] = [{
                        "component": self.subject,
                        "percentage": "99-100%",
                        "type": "primary"
                    }]
                elif field == "compatibility":
                    parsed[field] = [
                        {"material": "Stainless Steel", "application": "Surface preparation"},
                        {"material": "Various metals", "application": "Contaminant removal"}
                    ]
                elif field == "regulatoryStandards":
                    parsed[field] = [
                        {"code": "ISO Standards", "description": "International standards for material quality and processing"},
                        {"code": "ASTM Standards", "description": "American standards for material testing and specification"}
                    ]
                elif field == "images":
                    parsed[field] = ImageHandler.add_missing_images({}, self.subject)
                else:
                    parsed[field] = f"Placeholder for {field}"
        
        # Add image URLs if they're missing and process existing ones
        parsed = ImageHandler.process_image_data(parsed, self.subject)
        parsed = ImageHandler.add_missing_images(parsed, self.subject)
        
        # Ensure schema structure is followed
        parsed = self._ensure_schema_structure(parsed)
        
        # Pre-process values that might contain line breaks in quoted strings
        for key, value in list(parsed.items()):
            if isinstance(value, str):
                # Remove problematic backslash escape sequences
                if '\\' in value:
                    # Handle line continuations with \\n
                    if "\\n" in value:
                        parsed[key] = value.replace("\\n", "\n")
                    
                    # Remove backslash+space sequences
                    parsed[key] = parsed[key].replace('\\ ', ' ')
                    
                    # Handle YAML's line continuation format with backslashes at line end
                    if parsed[key].endswith('\\'):
                        lines = parsed[key].split('\\')
                        if len(lines) > 1:
                            # Join with actual newlines and strip whitespace from each line
                            parsed[key] = '\n'.join(line.strip() for line in lines if line.strip())
            
            # Recursively process nested dictionaries
            elif isinstance(value, dict):
                for subkey, subvalue in list(value.items()):
                    if isinstance(subvalue, str) and '\\' in subvalue:
                        # Handle the same replacements for nested values
                        value[subkey] = subvalue.replace("\\n", "\n").replace('\\ ', ' ')
        
        # Clean content - use allow_unicode to preserve Unicode characters properly
        cleaned_content = yaml.dump(parsed, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        # Store parsed frontmatter for other components to access
        self._frontmatter_data = parsed
        
        # Get category from instance attribute
        category = getattr(self, 'category', '')
        
        # Format frontmatter with HTML comment (metadata comment first, then frontmatter)
        final_content = format_frontmatter_with_comment(
            cleaned_content, category, self.article_type, self.subject
        )
        
        # Run required fields validation to ensure we've fixed everything
        try:
            validate_required_fields(parsed, required_fields, "frontmatter")
            logger.info("All required fields are now present in frontmatter")
        except ValueError as e:
            logger.error(f"Auto-fixing failed, still missing fields: {e}")
            raise
        
        # Ensure image URLs follow the correct convention
        if parsed and isinstance(parsed, dict):
            if "images" in parsed and isinstance(parsed["images"], dict):
                subject_slug = SlugUtils.create_subject_slug(self.subject)
                
                # Loop through all image types (hero, closeup, etc.)
                for image_type, image_data in parsed["images"].items():
                    if isinstance(image_data, dict) and "url" in image_data:
                        # Create the standardized URL
                        old_url = image_data["url"]
                        
                        # Get extension (default to jpg)
                        extension = "jpg"
                        if "." in old_url:
                            extension = old_url.split(".")[-1]
                        
                        # Create new standardized URL
                        new_url = f"/images/{subject_slug}-laser-cleaning-{image_type}.{extension}"
                        
                        # Normalize the URL to ensure no double dashes
                        new_url = ImageHandler.normalize_url(new_url)
                        
                        # Update URL
                        image_data["url"] = new_url
        
        # Sanitize content to remove malformed parts and standardize image URLs
        final_content = self._sanitize_content(final_content)
        
        return final_content
    
    def _sanitize_content(self, content: str) -> str:
        """Remove malformed content and standardize image URLs."""
        # Remove standalone URL fragments
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip standalone lines with broken URL fragments
            if re.match(r'^-*>*-*laser-cleaning.*\.jpg$', line.strip()):
                logger.info(f"Removing broken URL line: {line.strip()}")
                continue
            cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
        
        # Fix URLs with arrow characters
        content = re.sub(r'-+>+-*', '-', content)
        content = re.sub(r'([^a-z])>+-*', r'\1', content)
        
        # Fix missing hyphens between subject and laser-cleaning
        content = re.sub(r'(/images/[a-z0-9-]+)laser-cleaning', r'\1-laser-cleaning', content)
        
        # Fix double dashes in image URLs - this is our additional safeguard
        content = re.sub(r'(/images/[^"]*?)--+([^"]*?\.jpg)', r'\1-\2', content)
        
        return content
    
    def validate_category_consistency(self, content: str) -> bool:
        """Validates category consistency in frontmatter.
        
        Args:
            content: Frontmatter content
            
        Returns:
            bool: True if consistent
        """
        category = getattr(self, 'category', None)
        if not category:
            return True
            
        return validate_category_consistency(content, category, self.article_type, self.subject)
    
    def _process_response(self, response_data):
        """Process the raw response data from the AI model."""
        # Let the base class process the response first
        data = super()._process_response(response_data)
        
        # Process image URLs in case they bypass component_specific_processing
        data = ImageHandler.process_image_data(data, self.subject)
        data = ImageHandler.add_missing_images(data, self.subject)
        
        return data
