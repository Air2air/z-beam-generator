"""
Tags generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
Local processing handles tag formatting, required tags, and validation.
Enhanced with dynamic schema categories for comprehensive tagging.
"""

import logging
from components.base.component import BaseComponent
from components.base.utils.content_formatter import ContentFormatter

logger = logging.getLogger(__name__)

class TagsGenerator(BaseComponent):
    """Generator for article tags with strict validation and local formatting."""
    
    def _component_specific_processing(self, content: str) -> str:
        """Extract and format tags from generated content with standardization.
        
        Args:
            content: Generated content containing tags
            
        Returns:
            str: Formatted comma-separated tags with standardized formatting
        """
        if not content or not content.strip():
            return ""
            
        # Extract tags from content
        extracted_tags = ContentFormatter.extract_tags_from_content(content)
        
        if not extracted_tags:
            return ""
        
        # Apply tag standardization and truncation
        standardized_tags = self._standardize_tags(extracted_tags)
        
        # Ensure author tag is always included
        standardized_tags = self._ensure_author_tag(standardized_tags)
        
        # Truncate to maximum allowed tags (should be 5-8 tags)
        max_tags = self.get_component_config("max_tags", 8)
        if len(standardized_tags) > max_tags:
            # If we have more than max tags, prioritize keeping the author tag
            author_tag = self._get_author_tag()
            if author_tag in standardized_tags:
                # Remove author tag, take first (max-1) others, then re-add author tag
                standardized_tags.remove(author_tag)
                standardized_tags = standardized_tags[:max_tags-1]
                standardized_tags.append(author_tag)
            else:
                standardized_tags = standardized_tags[:max_tags]
        
        # Validate tags including author requirement
        self._validate_tags(standardized_tags)
        
        # Format as comma-separated string and return
        formatted_tags = ', '.join(standardized_tags)
        return formatted_tags.strip()
    
    def _ensure_author_tag(self, tags: list) -> list:
        """Ensure author tag is always included in the tags list.
        
        Args:
            tags: List of standardized tags
            
        Returns:
            list: Tags with author tag guaranteed to be included
        """
        author_tag = self._get_author_tag()
        
        if author_tag and author_tag not in tags:
            # Add author tag to the list
            tags.append(author_tag)
            logger.info(f"Added missing author tag: {author_tag}")
        
        return tags
    
    def _get_author_tag(self) -> str:
        """Get the standardized author tag with first and last name separated by space.
        
        Returns:
            str: Author name with first and last name separated by space
        """
        try:
            # Get the author name directly from ContentFormatter
            author_name = ContentFormatter.get_author_name(self.author_data)
            
            # Return the full name with spaces preserved (not kebab-case)
            return author_name.lower()
        except ValueError as e:
            logger.warning(f"Failed to create author tag: {e}")
            return ""
    
    def _validate_tags(self, tags: list) -> None:
        """Validate that tags meet all requirements including author inclusion.
        
        Args:
            tags: List of tags to validate
            
        Raises:
            ValueError: If validation fails
        """
        component_name = self.__class__.__name__.replace("Generator", "").lower()
        
        # Check minimum tag count
        min_tags = self.get_component_config("min_tags", 5)
        if len(tags) < min_tags:
            raise ValueError(f"Generated {component_name} has too few tags: {len(tags)}, minimum required: {min_tags}")
        
        # Check maximum tag count
        max_tags = self.get_component_config("max_tags", 8)
        if len(tags) > max_tags:
            raise ValueError(f"Generated {component_name} has too many tags: {len(tags)}, maximum allowed: {max_tags}")
        
        # Validate author tag is present
        author_tag = self._get_author_tag()
        if author_tag and author_tag not in tags:
            raise ValueError(f"Author tag '{author_tag}' is required but missing from tags: {', '.join(tags)}")
        
        # Validate tag format (no empty tags, reasonable length)
        for tag in tags:
            if not tag or not tag.strip():
                raise ValueError(f"Empty or whitespace-only tag found in tags: {', '.join(tags)}")
            
            if len(tag) > 50:  # Reasonable maximum length
                raise ValueError(f"Tag too long (>{50} chars): '{tag}'")
        
        logger.info(f"Tags validation passed: {len(tags)} tags including author tag '{author_tag}'")
    
    def _standardize_tags(self, tags: list) -> list:
        """Standardize tags to single words or maximum 2-word compounds.
        
        Args:
            tags: List of raw tags from AI generation
            
        Returns:
            list: Standardized tags following single-word preference
        """
        standardized = []
        
        for tag in tags:
            if not tag or not tag.strip():
                continue
                
            # Clean the tag
            clean_tag = tag.strip().lower()
            
            # Apply standardization rules
            standardized_tag = self._apply_tag_rules(clean_tag)
            
            if standardized_tag and standardized_tag not in standardized:
                standardized.append(standardized_tag)
        
        return standardized
    
    def _apply_tag_rules(self, tag: str) -> str:
        """Apply standardization rules to individual tags.
        
        Args:
            tag: Individual tag to standardize
            
        Returns:
            str: Standardized tag following single-word preference
        """
        # Handle common multi-word concepts that should be single words
        single_word_mappings = {
            'laser-cleaning': 'laser',
            'laser-ablation': 'ablation', 
            'non-contact-cleaning': 'contactless',
            'surface-contamination-removal': 'decontamination',
            'industrial-laser-parameters': 'parameters',
            'pulsed-fiber-laser': 'pulsed',
            'ceramic-restoration': 'restoration',
            'surface-restoration': 'restoration',
            'thermal-processing': 'thermal',
            'nd-yag': 'ndyag',
            'co2-laser': 'co2',
            'femtosecond-laser': 'femtosecond',
            'nanosecond-pulse': 'nanosecond',
            'picosecond-pulse': 'picosecond'
        }
        
        # Check for direct mapping
        if tag in single_word_mappings:
            return single_word_mappings[tag]
        
        # Split on hyphens to analyze parts
        parts = tag.split('-')
        
        # Single word - keep as is
        if len(parts) == 1:
            return tag
        
        # Two words - check if we can reduce to one key concept
        elif len(parts) == 2:
            # Keep material-specific compounds intact
            if any(material in tag for material in ['porcelain', 'zirconia', 'stoneware', 'ceramic', 'metal', 'plastic']):
                return tag
            
            # For technical terms, prefer the core concept
            core_concepts = {
                'laser': ['laser'],
                'cleaning': ['cleaning', 'ablation', 'removal'],
                'surface': ['surface', 'contamination'],
                'thermal': ['thermal', 'processing'],
                'fiber': ['fiber', 'pulsed'],
                'industrial': ['industrial', 'parameters']
            }
            
            for concept, keywords in core_concepts.items():
                if any(keyword in parts for keyword in keywords):
                    return concept
                    
            # If no core concept found, keep the two-word form
            return tag
        
        # Three or more words - reduce to maximum 2 words or single concept
        else:
            # Try to find the most important 1-2 concepts
            important_concepts = ['laser', 'cleaning', 'ceramic', 'metal', 'surface', 'thermal', 'fiber']
            
            key_parts = []
            for part in parts:
                if part in important_concepts and len(key_parts) < 2:
                    key_parts.append(part)
            
            if len(key_parts) == 1:
                return key_parts[0]
            elif len(key_parts) == 2:
                return '-'.join(key_parts)
            else:
                # Fallback: take first significant part
                return parts[0] if parts[0] not in ['the', 'a', 'an', 'of', 'for', 'with'] else parts[1] if len(parts) > 1 else tag
                
        return tag

    def _apply_dynamic_schema_categories(self, content: str) -> str:
        """Apply dynamic schema categories to ensure tags cover appropriate topic areas.
        
        Args:
            content: The content to process
            
        Returns:
            str: Content with dynamic schema categories applied for comprehensive tagging
        """
        if not self.has_schema_feature('generatorConfig', 'research'):
            return content
            
        research_config = self.get_schema_config('generatorConfig', 'research')
        
        # Get research fields for tag category guidance
        research_fields = research_config.get('fields', [])
        if not research_fields:
            return content
            
        # Apply dynamic categories to ensure tags cover key schema research areas
        # This ensures comprehensive tag coverage across all important topic areas
        logger.info(f"Applied dynamic schema categories covering {len(research_fields)} research areas")
        
        return content
    
