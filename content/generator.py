import logging
import os
import sys
from typing import Dict, Any, List

# Add parent directory to Python path to allow importing sibling packages
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
    
from api_client import APIClient

# Import refactored components
from content.utils.config_loader import ConfigLoader
from content.utils.retry_handler import RetryHandler
from content.formatters.data_formatter import DataFormatter
from content.prompts.section_prompts import SectionPromptBuilder
from content.prompts.context_builder import ContextBuilder

logger = logging.getLogger(__name__)

class ContentGenerator:
    """Generates highly randomized content based on frontmatter data and configuration options."""

    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str):
        self.context = context
        self.schema = schema
        self.ai_provider = ai_provider
        self.options = {}
        self.frontmatter = {}
        
        # Load templates and prompts
        self.prompt_template = ConfigLoader.load_prompt_template()
        self.section_prompts = ConfigLoader.load_section_prompts()
        
        logger.info(f"ContentGenerator initialized for {context['article_type']}: {context['subject']}")

    def set_frontmatter(self, frontmatter: Dict[str, Any]) -> 'ContentGenerator':
        """Set frontmatter data for content generation."""
        self.frontmatter = frontmatter or {}
        return self

    def set_options(self, options: Dict[str, Any]) -> 'ContentGenerator':
        """Set component-specific options from component_config.content."""
        self.options = options or {}
        return self
    
    def generate(self) -> str:
        """Generate content with standard sections."""
        try:
            # Standard sections
            sections = [
                {"id": "overview", "title": "Overview"},
                {"id": "applications", "title": "Applications"},
                {"id": "technicalSpecifications", "title": "Technical Specifications"},
                {"id": "challenges", "title": "Challenges"},
                {"id": "benefits", "title": "Benefits"}
            ]
            
            # Get structured data for content generation
            subject = self.context.get('subject', '')
            article_type = self.context.get('article_type', '')
            
            # Format prompt with standard sections
            formatted_prompt = self._build_content_prompt(subject, article_type, sections)
            
            # Generate content using AI
            content = self._generate_content_with_ai(formatted_prompt)
            
            return content
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return None
    
    def _build_content_prompt(self, subject: str, article_type: str, sections: List[Dict[str, str]]) -> str:
        """Build the content prompt with standard sections."""
        sections_text = ""
        
        for section in sections:
            section_id = section["id"]
            section_title = section["title"]
            
            # Get data for this section
            if section_id in self.frontmatter:
                field_data = self.frontmatter[section_id]
                formatted_data = DataFormatter.format_section_data(section_id, field_data, False)
            else:
                # For sections without direct frontmatter data, use section prompt
                section_prompt = self.section_prompts.get(section_id, "")
                if not section_prompt:
                    logger.warning(f"No prompt found for section {section_id}")
                    continue
                    
                # Format with subject
                try:
                    formatted_data = section_prompt.format(subject=subject)
                except KeyError as e:
                    logger.warning(f"Missing format key for section '{section_id}': {e}")
                    formatted_data = section_prompt
            
            # Create prompt for this section
            prompt = SectionPromptBuilder.create_section_prompt(
                section, 
                subject, 
                formatted_data, 
                300,  # Fixed word count per section
                False  # No randomization
            )
            sections_text += prompt + "\n\n"
            
        # Format the main prompt
        formatted_prompt = self.prompt_template.format(
            article_type=article_type,
            subject=subject,
            min_words=300,
            max_words=1000,
            paragraphs=5,
            num_sections=len(sections),
            sections=", ".join([s["title"] for s in sections]),
            section_prompts=sections_text,
            frontmatter_context=""  # No frontmatter context used
        )
        
        return formatted_prompt
    
    def _generate_content_with_ai(self, formatted_prompt: str) -> str:
        """Generate content using AI provider."""
        client = APIClient(self.ai_provider)
        
        # Create a lambda function that will be passed to the retry handler
        generate_func = lambda prompt, tokens: client.generate(prompt, tokens)
        
        content = RetryHandler.generate_with_retry(
            generate_func,
            formatted_prompt,
            300,  # Fixed min_words
            1000,  # Fixed max_words
            3  # Fixed max_attempts
        )
        
        return content