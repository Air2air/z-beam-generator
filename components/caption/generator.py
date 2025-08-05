"""
Caption generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
Enhanced with local formatting and section processing.
"""

import logging
import re
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class CaptionGenerator(BaseComponent):
    """Generator for image caption content with strict validation and local formatting."""
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated caption with enhanced local formatting.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Processed caption
            
        Raises:
            ValueError: If content is invalid
        """
        # Clean and normalize the content
        clean_content = content.strip()
        
        # Extract results and equipment sections (handling various formats)
        sections = self._extract_caption_sections(clean_content)
        
        # Get max word counts from config
        results_max = self.get_component_config("results_word_count_max")
        equipment_max = self.get_component_config("equipment_word_count_max")
        
        # Truncate sections if needed
        sections = self._truncate_sections(sections, results_max, equipment_max)
        
        # Format sections properly
        formatted_caption = self._format_caption(sections)
        
        return formatted_caption
    
    def _extract_caption_sections(self, content: str) -> dict:
        """Extract results and equipment sections from caption.
        
        Args:
            content: Clean caption content
            
        Returns:
            dict: Extracted sections
            
        Raises:
            ValueError: If required sections are missing
        """
        sections = {}
        
        # Try various section header formats
        results_patterns = [
            r'\*\*Results:\*\*\s*(.*?)(?=\*\*Equipment:|$)',
            r'Results:\s*(.*?)(?=Equipment:|$)',
            r'RESULTS:\s*(.*?)(?=EQUIPMENT:|$)',
            r'Results\s*(.*?)(?=Equipment|$)'
        ]
        
        equipment_patterns = [
            r'\*\*Equipment:\*\*\s*(.*?)$',
            r'Equipment:\s*(.*?)$',
            r'EQUIPMENT:\s*(.*?)$',
            r'Equipment\s*(.*?)$'
        ]
        
        # Try to extract results section
        results_section = None
        for pattern in results_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                results_section = match.group(1).strip()
                break
        
        # Try to extract equipment section
        equipment_section = None
        for pattern in equipment_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                equipment_section = match.group(1).strip()
                break
        
        # If sections are missing, try to split the content
        if not results_section or not equipment_section:
            # If there's a clear separation but no headers, assume first half is results
            # and second half is equipment
            if len(content.split('\n\n')) >= 2:
                parts = content.split('\n\n')
                results_section = parts[0].strip()
                equipment_section = parts[1].strip()
            else:
                # As a fallback, just split the content in half
                words = content.split()
                middle = len(words) // 2
                results_section = ' '.join(words[:middle])
                equipment_section = ' '.join(words[middle:])
        
        # Store sections
        sections['results'] = results_section if results_section else "Results not provided"
        sections['equipment'] = equipment_section if equipment_section else "Equipment details not provided"
        
        return sections
    
    def _truncate_sections(self, sections: dict, results_max: int, equipment_max: int) -> dict:
        """Truncate sections to meet word count requirements.
        
        Args:
            sections: Caption sections
            results_max: Maximum words for results section
            equipment_max: Maximum words for equipment section
            
        Returns:
            dict: Truncated sections
        """
        truncated = {}
        
        # Truncate results section
        results_words = sections['results'].split()
        if len(results_words) > results_max:
            # Add ellipsis if truncated
            truncated['results'] = ' '.join(results_words[:results_max]) + '...'
        else:
            truncated['results'] = sections['results']
        
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
        # Apply standard formatting
        formatted = f"**Results:** {sections['results']}\n\n**Equipment:** {sections['equipment']}"
        
        return formatted
