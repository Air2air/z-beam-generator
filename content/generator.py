import logging
import os
import sys
from typing import Dict, Any, List

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
        """Generate content based solely on frontmatter data."""
        try:
            # Get frontmatter data
            frontmatter_dict = self.frontmatter
            if not frontmatter_dict:
                logger.error("No frontmatter data available for content generation")
                return None
                
            # Extract subject from frontmatter
            subject = frontmatter_dict.get('name', self.context.get('subject', ''))
            
            # Determine sections based on frontmatter keys
            sections = self._get_frontmatter_driven_sections(frontmatter_dict)
            
            # Build prompt with sections and frontmatter data
            prompt = self._build_frontmatter_driven_prompt(subject, sections, frontmatter_dict)
            
            # Generate content using AI
            content = self._generate_content_with_ai(prompt)
            
            return content
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return None
        
    def _get_frontmatter_driven_sections(self, frontmatter_dict):
        """Generate sections based on available frontmatter data."""
        sections = []
        
        # Always include overview
        sections.append({"id": "overview", "title": "Overview"})
        
        # Add other sections based on frontmatter availability
        if 'applications' in frontmatter_dict:
            sections.append({"id": "applications", "title": "Applications"})
            
        if 'technicalSpecifications' in frontmatter_dict:
            sections.append({"id": "technicalSpecifications", "title": "Technical Specifications"})
            
        if 'challenges' in frontmatter_dict:
            sections.append({"id": "challenges", "title": "Challenges"})
            
        if 'benefits' in frontmatter_dict or 'outcomes' in frontmatter_dict:
            sections.append({"id": "benefits", "title": "Benefits"})
            
        return sections
    
    def _build_frontmatter_driven_prompt(self, subject, sections, frontmatter_dict):
        """Build content prompt based purely on frontmatter data."""
        prompt = f"# Create an article about {subject}\n\n"
        prompt += "Use ONLY the following data to create the content:\n\n"
        
        # Add frontmatter data as context
        for key, value in frontmatter_dict.items():
            if key in ['description', 'applications', 'technicalSpecifications', 
                      'challenges', 'outcomes', 'benefits', 'facilities', 
                      'regulatoryStandards', 'qualityStandards']:
                
                # Format the value based on its type
                if isinstance(value, list):
                    # Format list items
                    formatted_value = "\n".join([f"- {self._format_item(item)}" for item in value])
                elif isinstance(value, dict):
                    # Format dictionary items
                    formatted_value = "\n".join([f"- {k}: {v}" for k, v in value.items()])
                else:
                    formatted_value = str(value)
                
                prompt += f"## {key}:\n{formatted_value}\n\n"
        
        # Add instructions for each section
        prompt += "Generate the following sections:\n\n"
        for section in sections:
            prompt += f"## {section['title']}\n"
            prompt += f"Write content for this section using ONLY the relevant information provided above.\n\n"
        
        # Add specific formatting instruction
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