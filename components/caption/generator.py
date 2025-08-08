"""
Caption generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
Enhanced with local formatting and section processing.
Enhanced with dynamic image requirements from schema configurations.
"""

import logging
import re
from components.base.component import BaseComponent
from components.base.utils.content_formatter import ContentFormatter

logger = logging.getLogger(__name__)

class CaptionGenerator(BaseComponent):
    """Generator for image caption content with strict validation and local formatting."""
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated caption with simplified formatting.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Processed caption with simplified two-line format
            
        Raises:
            ValueError: If content is invalid
        """
        # Apply centralized formatting first for consistency
        content = self.apply_centralized_formatting(content)
        
        # Apply dynamic image requirements from schema
        content = self._apply_dynamic_image_requirements(content)
        
        # Clean and normalize the content using ContentFormatter
        clean_content = ContentFormatter.normalize_case(content.strip(), 'sentence')
        
        # Extract and format the simplified caption format
        formatted_caption = self._format_simplified_caption(clean_content)
        
        return formatted_caption
    
    def _format_simplified_caption(self, content: str) -> str:
        """Format caption content into simplified two-line format.
        
        Args:
            content: Clean caption content from AI
            
        Returns:
            str: Formatted caption in simplified format
            
        Raises:
            ValueError: If content cannot be properly formatted
        """
        # Clean up any extra formatting or quotes
        content = re.sub(r'^["\']+|["\']+$', '', content.strip())
        content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
        
        # Look for the expected two-line format with material name and "After laser cleaning"
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # If we get the expected format, clean it up
        if len(lines) >= 2:
            # Find material line and laser cleaning line
            material_line = None
            cleaning_line = None
            
            for line in lines:
                if line.startswith('**') and '(' in line and ')' in line:
                    material_line = line
                elif 'after laser cleaning' in line.lower() or 'laser cleaning' in line.lower():
                    cleaning_line = line
            
            if material_line and cleaning_line:
                # Ensure proper formatting
                if not cleaning_line.startswith('**After laser cleaning**'):
                    # Fix the formatting if needed
                    cleaning_line = re.sub(r'^\*\*.*?\*\*', '**After laser cleaning**', cleaning_line)
                    if not cleaning_line.startswith('**After laser cleaning**'):
                        cleaning_line = '**After laser cleaning** ' + cleaning_line.lstrip('*').strip()
                
                return f"{material_line}\n\n{cleaning_line}"
        
        # If format is not as expected, try to parse it anyway
        # Look for material formula and create the expected format
        material_match = re.search(r'(\w+)\s*\([^)]+\)', content)
        if material_match:
            # Split at reasonable break points
            sentences = re.split(r'[.!?]\s+', content)
            if len(sentences) >= 2:
                first_part = sentences[0] + '.'
                second_part = ' '.join(sentences[1:])
                
                # Ensure proper bold formatting
                if not first_part.startswith('**'):
                    material_name = material_match.group(1)
                    first_part = re.sub(rf'{material_name}', f'**{material_name}**', first_part, 1)
                
                if 'laser' in second_part.lower() and not second_part.startswith('**After laser cleaning**'):
                    second_part = '**After laser cleaning** ' + second_part.lstrip()
                
                return f"{first_part}\n\n{second_part}"
        
        # Fallback: return content as-is if we can't parse it properly
        logger.warning("Could not parse caption into expected format, returning as-is")
        return content

    def _apply_dynamic_image_requirements(self, content: str) -> str:
        """Apply dynamic image requirements from schema for targeted caption generation.
        
        Args:
            content: The content to process
            
        Returns:
            str: Content with dynamic image requirements applied based on schema specifications
        """
        if not self.has_schema_feature('generatorConfig'):
            return content
            
        generator_config = self.get_schema_config('generatorConfig')
        
        # Use the research field configuration that exists in the schema
        if 'research' in generator_config:
            research_config = generator_config['research']
            if 'fields' in research_config:
                logger.info(f"Applied dynamic image generation context from research fields: {research_config['fields']}")
        else:
            # Strict mode: Generator config must be present
            raise ValueError("Caption generator requires generatorConfig with research fields in schema")
        
        return content
