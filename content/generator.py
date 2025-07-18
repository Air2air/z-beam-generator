import logging
import os
import re
import sys
from typing import Dict, Any, List
from datetime import datetime

# Add parent directory to Python path to allow importing sibling packages
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
    
from api_client import APIClient

# Only keep essential imports
from content.utils.retry_handler import RetryHandler

logger = logging.getLogger(__name__)

class ContentGenerator:
    """Generates content based solely on frontmatter data."""

    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str):
        self.context = context
        self.schema = schema
        self.ai_provider = ai_provider
        self.options = {}
        self.frontmatter = {}
        
        logger.info(f"ContentGenerator initialized for {context['article_type']}: {context['subject']}")

    def set_frontmatter(self, frontmatter: Dict[str, Any]) -> 'ContentGenerator':
        """Set frontmatter data for content generation."""
        self.frontmatter = frontmatter or {}
        return self

    def set_options(self, options: Dict[str, Any]) -> 'ContentGenerator':
        """Set component-specific options from component_config.content."""
        self.options = options or {}
        return self
    
    def generate(self):
        """Generate content with fully dynamic sections based on frontmatter."""
        try:
            frontmatter_dict = self.frontmatter
            if not frontmatter_dict:
                logger.error("No frontmatter data available for content generation")
                return None
                
            # Extract subject
            subject = frontmatter_dict.get('name', self.context.get('subject', ''))
            
            # Dynamically determine sections from frontmatter
            sections = self._get_frontmatter_driven_sections(frontmatter_dict)
            
            # Order sections intelligently
            sections = self._order_sections_intelligently(sections, frontmatter_dict)
            
            # Build prompt
            prompt = self._build_frontmatter_driven_prompt(subject, sections, frontmatter_dict)
            
            # Generate content
            content = self._generate_content_with_ai(prompt)
            
            return content
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return None
        
    def _get_frontmatter_driven_sections(self, frontmatter_dict):
        """Generate sections dynamically based on available frontmatter data without hardcoded mappings."""
        sections = []
        
        # Always include overview
        sections.append({"id": "overview", "title": "Overview"})
        
        # Non-section fields that should be excluded
        metadata_fields = ['name', 'description', 'author', 'website', 'url', 'keywords', 'tags']
        
        # Process all frontmatter fields as potential sections
        for key, value in frontmatter_dict.items():
            # Skip metadata fields
            if key in metadata_fields:
                continue
            
            # Format section title from the key itself
            title = self._format_section_title(key)
            
            # Add as a section if it contains substantial data
            if value:
                # For lists and dicts, always include
                if isinstance(value, list) or isinstance(value, dict):
                    sections.append({"id": key, "title": title})
                # For strings, include if they're substantial
                elif isinstance(value, str) and len(value) > 50:
                    sections.append({"id": key, "title": title})
    
        return sections
    
    def _format_section_title(self, key):
        """Convert camelCase or snake_case to Title Case."""
        # Replace camelCase with spaces
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', key)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
        # Replace underscores with spaces
        s3 = s2.replace('_', ' ')
        # Title case
        return s3.title()
    
    def _build_frontmatter_driven_prompt(self, subject, sections, frontmatter_dict):
        """Build content prompt based purely on frontmatter data."""
        prompt = f"# Create an article about {subject}\n\n"
        prompt += "Use ONLY the following data to create the content:\n\n"
        
        # Add ALL frontmatter data except excluded fields
        excluded_fields = ['name', 'author', 'website', 'url', 'keywords', 'tags']
        
        for key, value in frontmatter_dict.items():
            # Skip fields that should be excluded from content generation
            if key in excluded_fields:
                continue
                
            # Format the value based on its type
            if isinstance(value, list):
                formatted_value = "\n".join([f"- {self._format_item(item)}" for item in value])
            elif isinstance(value, dict):
                formatted_value = "\n".join([f"- {k}: {v}" for k, v in value.items()])
            else:
                formatted_value = str(value)
            
            prompt += f"## {key}:\n{formatted_value}\n\n"
        
        # Add instructions for each section
        prompt += "Generate the following sections:\n\n"
        for section in sections:
            prompt += f"## {section['title']}\n"
            prompt += f"Write content for this section using ONLY the relevant information provided above.\n\n"
        
        prompt += "Format the content as markdown with section headers (##) for each section.\n"
        
        return prompt
    
    def _format_item(self, item):
        """Format an item based on its type."""
        if isinstance(item, dict):
            # Format each key-value pair
            return ", ".join([f"{k}: {v}" for k, v in item.items()])
        else:
            return str(item)
    
    def _generate_content_with_ai(self, formatted_prompt: str) -> str:
        """Generate content using AI provider."""
        client = APIClient(self.ai_provider)
        
        # Get word count settings from options or use defaults
        min_words = self.options.get('min_words', 300)
        max_words = self.options.get('max_words', 1000)
        max_attempts = self.options.get('max_attempts', 3)
        
        # Create a lambda function that will be passed to the retry handler
        generate_func = lambda prompt, tokens: client.generate(prompt, tokens)
        
        content = RetryHandler.generate_with_retry(
            generate_func,
            formatted_prompt,
            min_words,
            max_words,
            max_attempts
        )
        
        return content
    
    def _order_sections_intelligently(self, sections, frontmatter_dict):
        """Order sections based on their content and importance."""
        # Always keep overview first
        overview_section = next((s for s in sections if s['id'] == 'overview'), None)
        ordered_sections = [overview_section] if overview_section else []
        remaining_sections = [s for s in sections if s['id'] != 'overview']
        
        # Common section priority patterns by article type
        article_type = self.context.get('article_type', '').lower()
        
        # Score sections based on importance heuristics
        scored_sections = []
        for section in remaining_sections:
            score = 0
            section_id = section['id'].lower()
            
            # Score based on common patterns
            if 'technical' in section_id or 'specifications' in section_id:
                score += 90  # Technical specs usually high priority
            elif 'application' in section_id or 'uses' in section_id:
                score += 85  # Applications usually important
            elif 'benefit' in section_id or 'advantage' in section_id:
                score += 80  # Benefits are important
            elif 'challenge' in section_id or 'limitation' in section_id:
                score += 75  # Challenges usually before solutions
            elif 'solution' in section_id or 'method' in section_id:
                score += 70  # Solutions after challenges
                
            # Score based on data richness
            data = frontmatter_dict.get(section['id'])
            if isinstance(data, list):
                score += min(len(data) * 2, 10)  # More list items = higher priority
            elif isinstance(data, dict):
                score += min(len(data) * 2, 10)  # More dict items = higher priority
                
            scored_sections.append((section, score))
        
        # Sort by score (descending)
        sorted_sections = [s[0] for s in sorted(scored_sections, key=lambda x: x[1], reverse=True)]
        
        # Combine with overview
        return ordered_sections + sorted_sections
    
    def _log_section_quality(self, sections, content_quality):
        """Log section performance for future optimization."""
        try:
            # Create a simple log entry that could be used for future improvements
            quality_log = {
                "article_type": self.context.get('article_type', ''),
                "sections": [s['id'] for s in sections],
                "quality_score": content_quality,
                "timestamp": datetime.now().isoformat()
            }
            
            # Log for future analysis
            logger.debug(f"Section quality data: {quality_log}")
            
            # In a more advanced version, you could store this in a database
            # for training a section ordering model
            
        except Exception as e:
            logger.error(f"Error logging section quality: {e}")