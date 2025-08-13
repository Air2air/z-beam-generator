"""
Unified Document Generator - Clean Implementation

Single API call generates complete material documentation.
Uses updated component prompts for template-based generation.
"""

import logging
import json
import os
import sys
import yaml
from typing import Dict, Any

# Add project root to path to import BATCH_CONFIG
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)

class UnifiedDocumentGenerator:
    """Single API call generates complete material document using updated component prompts."""
    
    def __init__(self, ai_provider: str = "deepseek", options: Dict[str, Any] = None):
        self.ai_provider = ai_provider
        self.options = options or {"model": "deepseek-chat", "max_tokens": 8000}
        
        # Import BATCH_CONFIG for component settings
        from run import BATCH_CONFIG
        self.config = BATCH_CONFIG
    
    def generate_complete_document(self, subject: str, article_type: str, 
                                 category: str, author_data: Dict[str, Any],
                                 schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete document with single API call using updated component prompts."""
        
        try:
            # Build context with schema
            context = {
                "subject": subject,
                "article_type": article_type,
                "category": category,
                "author_context": author_data.get("author_name", "Expert") + " from " + author_data.get("author_country", "International"),
                "schema": schema
            }
            
            # Create unified prompt using updated component prompts
            prompt = self._build_unified_prompt(context)
            
            # Single API call
            response = self._call_api(prompt)
            
            # Parse response into component structure
            document = self._parse_response(response, subject, schema)
            
            return document
            
        except Exception as e:
            logger.error(f"Unified generation failed for {subject}: {e}")
            return None
    
    def _build_unified_prompt(self, context: Dict[str, Any]) -> str:
        """Build single comprehensive prompt using updated component prompts."""
        
        subject = context["subject"]
        category = context["category"]
        article_type = context["article_type"]
        schema = context.get("schema", {})
        author_context = context["author_context"]
        
        # Get enabled components from BATCH_CONFIG
        enabled_components = []
        component_configs = {}
        for name, config in self.config["components"].items():
            if config.get("enabled", False):
                enabled_components.append(name)
                component_configs[name] = config
        
        # Build component requirements using actual prompt files
        component_requirements = self._build_component_requirements(enabled_components, component_configs, subject, category, article_type)
        
        system_prompt = f"""Generate complete technical {article_type} documentation for {subject} as JSON.

CRITICAL: Follow the updated template-based component requirements exactly as specified.
Each component now includes explicit template structures that MUST be followed.

ENABLED COMPONENTS: {', '.join(enabled_components)}

UPDATED COMPONENT REQUIREMENTS:
{component_requirements}

ARTICLE TYPE: {article_type}
CATEGORY: {category}
AUTHOR PERSPECTIVE: {author_context}

OUTPUT FORMAT: Return a JSON object with each component as a separate key.
Example structure:
{{
  "frontmatter": "your frontmatter content here",
  "content": "your content here",
  "bullets": "your bullets here",
  "caption": "your caption here",
  "jsonld": "your jsonld content here",
  "metatags": "your metatags content here",
  "table": "your table content here",
  "tags": "your tags here",
  "propertiestable": "your properties table here"
}}

REQUIREMENTS:
- Follow template structures exactly as specified in each component
- Generate technically accurate content with specific values
- Use proper formatting as specified in each component template
- Include all required fields for each component"""

        user_prompt = f"""Generate complete documentation for {subject} ({category} {article_type}).
Follow all template requirements exactly."""

        return f"{system_prompt}\n\nHuman: {user_prompt}\n\nAssistant:"
    
    def _build_component_requirements(self, enabled_components: list, component_configs: Dict[str, Any], 
                                    subject: str, category: str, article_type: str) -> str:
        """Build component requirements by reading actual updated component prompt files."""
        requirements = []
        
        for component in enabled_components:
            try:
                # Load the actual component prompt file
                prompt_file = f"components/{component}/prompt.yaml"
                if os.path.exists(prompt_file):
                    with open(prompt_file, 'r') as f:
                        prompt_config = yaml.safe_load(f)
                    
                    template = prompt_config.get('template', '')
                    description = prompt_config.get('description', f'{component} component')
                    version = prompt_config.get('version', '1.0.0')
                    
                    # Replace template variables with actual values
                    template = template.replace('{subject}', subject)
                    template = template.replace('{category}', category)
                    template = template.replace('{article_type}', article_type)
                    
                    # Add component-specific config values
                    if component == "bullets":
                        count = component_configs.get(component, {}).get("count", 6)
                        template = template.replace('{count}', str(count))
                    elif component == "content":
                        min_words = component_configs.get(component, {}).get("min_words", 800)
                        max_words = component_configs.get(component, {}).get("max_words", 1200)
                        template = template.replace('{min_words}', str(min_words))
                        template = template.replace('{max_words}', str(max_words))
                    elif component == "tags":
                        min_tags = component_configs.get(component, {}).get("min_tags", 8)
                        max_tags = component_configs.get(component, {}).get("max_tags", 12)
                        template = template.replace('{min_tags}', str(min_tags))
                        template = template.replace('{max_tags}', str(max_tags))
                    
                    requirements.append(f"""COMPONENT: {component} ({description} v{version})
{template}""")
                    
                else:
                    # Fallback to basic requirements if prompt file not found
                    requirements.append(f"""COMPONENT: {component}
- Generate appropriate {component} content
- Follow technical accuracy standards
- Use proper formatting for component type""")
                    logger.warning(f"Prompt file not found for {component}, using basic requirements")
            
            except Exception as e:
                logger.error(f"Error loading prompt for {component}: {e}")
                # Add basic fallback
                requirements.append(f"""COMPONENT: {component} (fallback)
- Generate appropriate content for {component}""")
        
        return "\n\n".join(requirements)
    
    def _call_api(self, prompt: str) -> str:
        """Make API call to generate content."""
        from api.client import ApiClient
        
        # Build article context for API
        article_context = {
            "model": self.options.get("model", "deepseek-chat"),
            "max_tokens": self.options.get("max_tokens", 8000),
            "temperature": 0.7
        }
        
        client = ApiClient(provider=self.ai_provider, options=self.options, article_context=article_context)
        return client.complete(prompt)
    
    def _parse_response(self, response: str, subject: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into component structure."""
        from components.base.utils.content_formatter import ContentFormatter
        
        cleaned = ContentFormatter.extract_json_content(response)
        document = json.loads(cleaned)
        
        # Get enabled components for validation
        enabled_components = []
        if hasattr(self, 'config'):
            for name, config in self.config["components"].items():
                if config.get("enabled", False):
                    enabled_components.append(name)
        else:
            enabled_components = ["frontmatter", "content", "bullets", "caption", "jsonld", "metatags", "table", "tags"]
        
        # Ensure all enabled components are present
        for component in enabled_components:
            if component not in document:
                logger.warning(f"Missing component {component} in response for {subject}")
                document[component] = f"# {component.title()} for {subject}\n\nGenerated content placeholder."
        
        return document
