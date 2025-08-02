"""
Metatags generator for Z-Beam Generator.

Generates Next.js compatible meta tags in YAML frontmatter format.
"""

import logging
import yaml
from components.base.enhanced_component import EnhancedBaseComponent
from components.metatags.validation import validate_article_specific_fields
from components.base.formatting_utils import format_yaml_object

logger = logging.getLogger(__name__)

class MetatagsGenerator(EnhancedBaseComponent):
    """Generator for Next.js compatible meta tags in YAML frontmatter format with strict validation."""
    
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
            # Parse the YAML content
            if '---' in content:
                # Extract content between --- markers
                yaml_content = content.split('---')[1].strip()
                parsed = yaml.safe_load(yaml_content)
                
                # Validate required fields
                required_fields = ["title", "description", "keywords", "openGraph"]
                missing_fields = [field for field in required_fields if field not in parsed]
                if missing_fields:
                    raise ValueError(f"Missing required metatag fields: {missing_fields}")
                
                # Ensure title field follows proper format
                if "title" in parsed and not parsed["title"].startswith(f"{self.subject} "):
                    parsed["title"] = f"{self.subject} Laser Cleaning | Technical Guide"
                
                # Validate fields based on article type
                validate_article_specific_fields(self.article_type, getattr(self, 'category', None), parsed)
                
                # Ensure frontmatter data is included if available
                template_data = self.get_template_data()
                if 'all_frontmatter' in template_data and template_data['all_frontmatter']:
                    try:
                        frontmatter = template_data['frontmatter_data'] if 'frontmatter_data' in template_data else {}
                        
                        # Always create a valid application object for material article types
                        if self.article_type == 'material' and ('application' not in parsed or not isinstance(parsed['application'], dict)):
                            parsed['application'] = {
                                'name': f"{self.subject} Laser Cleaning",
                                'description': f"Removal of contaminants, oxides, and coatings from {self.subject} surfaces using high-precision laser technology."
                            }
                        
                        # Use applications from frontmatter if available
                        if 'applications' in frontmatter and isinstance(frontmatter['applications'], list) and frontmatter['applications']:
                            # Get the first application from the list
                            first_app = frontmatter['applications'][0]
                            
                            # If it's already a dict with name and description, use it directly
                            if isinstance(first_app, dict) and 'name' in first_app and 'description' in first_app:
                                parsed['application'] = first_app
                            # If it's just a string, create a proper object
                            elif isinstance(first_app, str):
                                parsed['application'] = {
                                    'name': first_app,
                                    'description': f"Application of laser cleaning technology for {first_app} in the {self.subject} industry."
                                }
                            # If it has only a name, add a description
                            elif isinstance(first_app, dict) and 'name' in first_app and 'description' not in first_app:
                                parsed['application'] = {
                                    'name': first_app['name'],
                                    'description': f"Application of laser cleaning technology for {first_app['name']} in the {self.subject} industry."
                                }
                        
                        # Copy other fields from frontmatter
                        for field in ['properties', 'chemicalProperties', 'environmentalImpact', 'regulatoryStandards']:
                            if field in frontmatter and field not in parsed:
                                parsed[field] = frontmatter[field]
                    except Exception as e:
                        logger.warning(f"Could not process frontmatter data: {e}")
                
                # Convert back to YAML and format with --- delimiters
                formatted_yaml = format_yaml_object(parsed)
                return f"---\n{formatted_yaml}---"
            else:
                raise ValueError("Missing YAML frontmatter delimiters (---)")
        except Exception as e:
            # Let the error propagate
            logger.error(f"Error processing metatags: {e}")
            raise ValueError(f"Metatags generation failed: {e}")
    
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
