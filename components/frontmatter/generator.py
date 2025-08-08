"""
Frontmatter generator for Z-Beam Generator.

Enhanced implementation with robust error handling and auto-recovery.
"""

import logging
import re

from components.base.component import BaseComponent
from components.base.utils.validation import validate_category_consistency
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
        if not self.has_schema_feature('generatorConfig'):
            logger.warning(f"No generatorConfig found for article type: {self.article_type}")
            return parsed
            
        config = self.get_schema_config('generatorConfig')
        
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
        """Process frontmatter with centralized structured content processing."""
        return self._process_structured_content(content, output_format="yaml")
    
    def _extract_content_from_text(self, content: str) -> dict:
        """Extract structured data from any text format.
        
        This method can handle raw text, markdown, partial YAML, or any other format
        and extract the technical information needed for frontmatter.
        
        Args:
            content: Raw text content from AI
            
        Returns:
            dict: Structured data extracted from text
        """
        import re
        
        result = {
            'name': self.subject,  # Use the subject as the base name
        }
        
        # Extract properties (look for numeric values with units)
        properties = {}
        
        # Common property patterns
        property_patterns = [
            (r'density[:\s]*([0-9.,–\-\s]+g/cm³)', 'density'),
            (r'melting\s*point[:\s]*([0-9.,–\-\s]+°?C)', 'meltingPoint'),
            (r'thermal\s*conductivity[:\s]*([0-9.,–\-\s]+W/m[·•]K)', 'thermalConductivity'),
            (r'hardness[:\s]*([0-9.,–\-\s]+Mohs)', 'hardness'),
            (r'flexural\s*strength[:\s]*([0-9.,–\-\s]+MPa)', 'flexuralStrength'),
            (r'tensile\s*strength[:\s]*([0-9.,–\-\s]+MPa)', 'tensileStrength'),
            (r'compressive\s*strength[:\s]*([0-9.,–\-\s]+MPa)', 'compressiveStrength'),
        ]
        
        for pattern, key in property_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                properties[key] = match.group(1).strip()
        
        if properties:
            result['properties'] = properties
        
        # Extract applications (look for industry contexts)
        applications = []
        
        # Look for application patterns
        app_patterns = [
            r'\*\*([^*]+)\*\*:\s*([^*\n]+)',  # **Industry**: Description
            r'([A-Z][a-z]+\s*[A-Z]*[a-z]*):\s*([^:\n]+)',  # Industry: Description
        ]
        
        for pattern in app_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) == 2:
                    industry, description = match
                    if any(word in industry.lower() for word in ['restoration', 'heritage', 'medical', 'aerospace', 'automotive', 'electronics']):
                        applications.append({
                            'industry': industry.strip(),
                            'useCase': description.strip(),
                            'detail': 'Specific laser cleaning application'
                        })
        
        if applications:
            result['applications'] = applications
        
        # Extract composition information
        composition = []
        
        # Look for composition patterns (percentages and formulas)
        comp_matches = re.findall(r'([A-Z][a-z]*(?:\s+[A-Z][a-z]*)*)\s*[:\-]?\s*([0-9]+[–\-][0-9]+%|[0-9]+%)\s*(?:[,\s]*([A-Z][a-z]*[₀-₉]*[A-Z]*[a-z]*[₀-₉]*))?', content)
        
        for match in comp_matches:
            component_name, percentage, formula = match
            comp_item = {
                'component': component_name.strip(),
                'percentage': percentage.strip(),
                'type': 'compound'
            }
            if formula:
                comp_item['formula'] = formula.strip()
            composition.append(comp_item)
        
        if composition:
            result['composition'] = composition
        
        # Extract technical specifications (look for laser parameters)
        tech_specs = {}
        
        tech_patterns = [
            (r'([0-9]+[–\-][0-9]+W|[0-9]+W)', 'powerRange'),
            (r'([0-9]+[–\-][0-9]+nm|[0-9]+nm)', 'wavelength'),
            (r'([0-9]+[–\-][0-9]+ns|[0-9]+ns)', 'pulseDuration'),
            (r'([0-9.,]+[–\-][0-9.,]+\s*J/cm²)', 'fluenceRange'),
        ]
        
        for pattern, key in tech_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                tech_specs[key] = match.group(1)
        
        if tech_specs:
            result['technicalSpecifications'] = tech_specs
        
        # Extract environmental impact information
        env_impact = {}
        
        env_patterns = [
            (r'([0-9]+%).*reduction', 'wasteReduction'),
            (r'([0-9]+[–\-][0-9]+%).*energy', 'energyEfficiency'),
        ]
        
        for pattern, key in env_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                env_impact[key] = match.group(1)
        
        if env_impact:
            result['environmentalImpact'] = env_impact
        
        return result
    
    def _extract_yaml_content(self, content: str) -> str:
        """Extract clean YAML content from various AI response formats.
        
        Args:
            content: Raw AI response content
            
        Returns:
            str: Clean YAML content
        """
        # First try to extract content between frontmatter markers
        yaml_content = ContentFormatter.extract_content_between_markers(content, '---')
        
        # If no markers found, use the general YAML extraction method
        if yaml_content == content:
            yaml_content = self.extract_yaml_content(content)
        
        # Make sure we don't have trailing --- markers that would create multiple YAML documents
        yaml_content = yaml_content.strip()
        if yaml_content.endswith('---'):
            yaml_content = yaml_content[:-3].strip()
        
        return yaml_content

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
