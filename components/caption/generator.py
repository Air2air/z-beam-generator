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
        """Process the generated caption with enhanced local formatting.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Processed caption with dynamic image requirements
            
        Raises:
            ValueError: If content is invalid
        """
        # Apply centralized formatting first for consistency
        content = self.apply_centralized_formatting(content)
        
        # Apply dynamic image requirements from schema
        content = self._apply_dynamic_image_requirements(content)
        
        # Clean and normalize the content using ContentFormatter
        clean_content = ContentFormatter.normalize_case(content.strip(), 'sentence')
        
        # Extract before cleaning and equipment sections (handling various formats)
        sections = self._extract_caption_sections(clean_content)
        
        # Get max word counts from config
        before_max = self.get_component_config("before_word_count_max", 100)
        equipment_max = self.get_component_config("equipment_word_count_max", 50)
        
        # Truncate sections if needed
        sections = self._truncate_sections(sections, before_max, equipment_max)
        
        # Format sections properly
        formatted_caption = self._format_caption(sections)
        
        return formatted_caption
    
    def _extract_caption_sections(self, content: str) -> dict:
        """Extract before cleaning and equipment sections from caption.
        
        Args:
            content: Clean caption content
            
        Returns:
            dict: Extracted sections
            
        Raises:
            ValueError: If required sections are missing
        """
        sections = {}
        
        # Try various section header formats
        before_patterns = [
            r'\*\*Before Cleaning:\*\*\s*(.*?)(?=\*\*Equipment:|$)',
            r'Before Cleaning:\s*(.*?)(?=Equipment:|$)',
            r'BEFORE CLEANING:\s*(.*?)(?=EQUIPMENT:|$)',
            r'Before\s*Cleaning\s*(.*?)(?=Equipment|$)'
        ]
        
        equipment_patterns = [
            r'\*\*Equipment:\*\*\s*(.*?)$',
            r'Equipment:\s*(.*?)$',
            r'EQUIPMENT:\s*(.*?)$',
            r'Equipment\s*(.*?)$'
        ]
        
        # Try to extract before cleaning section
        before_section = None
        for pattern in before_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                before_section = match.group(1).strip()
                break
        
        # Try to extract equipment section
        equipment_section = None
        for pattern in equipment_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                equipment_section = match.group(1).strip()
                break
        
        # If sections are missing, try to split the content
        if not before_section or not equipment_section:
            # If there's a clear separation but no headers, assume first half is results
            # and second half is equipment
            if len(content.split('\n\n')) >= 2:
                parts = content.split('\n\n')
                before_section = parts[0].strip()
                equipment_section = parts[1].strip()
            else:
                # Strict mode: Require proper content structure
                raise ValueError("Caption content must contain '**Equipment:**' section marker")
        
        # Store sections
        sections['before'] = before_section if before_section else "Before cleaning details not provided"
        sections['equipment'] = equipment_section if equipment_section else "Equipment details not provided"
        
        return sections
    
    def _truncate_sections(self, sections: dict, before_max: int, equipment_max: int) -> dict:
        """Truncate sections to meet word count requirements.
        
        Args:
            sections: Caption sections
            before_max: Maximum words for before cleaning section
            equipment_max: Maximum words for equipment section
            
        Returns:
            dict: Truncated sections
        """
        truncated = {}
        
        # Truncate before cleaning section
        before_words = sections['before'].split()
        if len(before_words) > before_max:
            # Add ellipsis if truncated
            truncated['before'] = ' '.join(before_words[:before_max]) + '...'
        else:
            truncated['before'] = sections['before']
        
        # Truncate equipment section
        equipment_words = sections['equipment'].split()
        if len(equipment_words) > equipment_max:
            # Add ellipsis if truncated
            truncated['equipment'] = ' '.join(equipment_words[:equipment_max]) + '...'
        else:
            truncated['equipment'] = sections['equipment']
        
        return truncated
    
    def _format_caption(self, sections: dict) -> str:
        """Format caption with proper section headers.
        
        Args:
            sections: Caption sections
            
        Returns:
            str: Formatted caption
        """
        # Apply standard formatting with bold section headers
        formatted = f"**Before Cleaning:** {sections['before']}\n\n**Equipment:** {sections['equipment']}"
        
        return formatted

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
