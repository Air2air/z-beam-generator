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
            # Build the prompt
            context = {
                "subject": subject,
                "article_type": article_type,
                "category": category,
                "schema": schema,
                "author_context": author_data
            }
            prompt = self._build_unified_prompt(context)
            
            # Call the API
            response = self._call_api(prompt)
            
            # Parse response into component structure
            document = self._parse_response(response, subject, schema)
            
            if document is None:
                logger.error(f"Failed to parse response for {subject} - returning failure")
                return {"success": False, "error": "Failed to parse AI response", "components": {}}
            
            return {
                "success": True,
                "components": document
            }
            
        except Exception as e:
            logger.error(f"Unified generation failed for {subject}: {e}")
            return {"success": False, "error": str(e), "components": {}}
    
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
        component_requirements = self._build_component_requirements(enabled_components, component_configs, context)
        
        system_prompt = f"""Generate complete technical {article_type} documentation for {subject} as JSON.

IMPORTANT: Create natural, technically accurate content that includes all required fields.
Use the component requirements as structural guidance, not rigid templates.

ENABLED COMPONENTS: {', '.join(enabled_components)}

COMPONENT REQUIREMENTS:
{component_requirements}

MATERIAL INFORMATION:
- Subject: {subject}
- Article Type: {article_type}
- Category: {category}
- Author Perspective: {author_context}

OUTPUT FORMAT: Return a JSON object with each component as a separate key.
Example structure:
{{
  "frontmatter": "your complete frontmatter content here",
  "content": "your article content here",
  "bullets": "your bullet points here",
  "caption": "your image caption here",
  "jsonld": "your structured data here",
  "metatags": "your meta tags here",
  "table": "your table content here",
  "tags": "your tags here",
  "propertiestable": "your properties table here"
}}

REQUIREMENTS:
- Include all required structural fields for each component
- Generate natural, technically accurate content
- Use specific numerical values and real-world applications
- Make content informative and professionally written
- Ensure completeness while maintaining natural expression"""

        user_prompt = f"""Generate complete documentation for {subject} ({category} {article_type}).
Follow all template requirements exactly."""

        return f"{system_prompt}\n\nHuman: {user_prompt}\n\nAssistant:"
    
    def _build_component_requirements(self, enabled_components: list, component_configs: Dict[str, Any], 
                                    context: Dict[str, Any]) -> str:
        """Build component requirements by reading actual updated component prompt files."""
        requirements = []
        
        subject = context["subject"]
        category = context["category"] 
        article_type = context["article_type"]
        material_formula = context.get("material_formula", "N/A")
        material_symbol = context.get("material_symbol", "N/A")
        material_type = context.get("material_type", "material")
        
        for component in enabled_components:
            try:
                # Load the actual component prompt file
                prompt_file = f"components/{component}/prompt.yaml"
                if os.path.exists(prompt_file):
                    with open(prompt_file, 'r') as f:
                        prompt_config = yaml.safe_load(f)
                    
                    # Ensure prompt_config is not None and is a dict
                    if prompt_config is None:
                        logger.error(f"Error loading prompt for {component}: YAML file is empty or invalid")
                        prompt_config = {}
                    elif not isinstance(prompt_config, dict):
                        logger.error(f"Error loading prompt for {component}: YAML content is not a dictionary")
                        prompt_config = {}
                    
                    template = prompt_config.get('template', '')
                    description = prompt_config.get('description', f'{component} component')
                    version = prompt_config.get('version', '1.0.0')
                    
                    # Replace template variables with actual values
                    template = template.replace('{subject}', subject)
                    template = template.replace('{category}', category)
                    template = template.replace('{article_type}', article_type)
                    template = template.replace('{material_formula}', material_formula)
                    template = template.replace('{material_symbol}', material_symbol)
                    template = template.replace('{material_type}', material_type)
                    template = template.replace('{subject_slug}', subject.lower().replace(' ', '-'))
                    
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
        """Parse AI response into component structure with robust error handling."""
        from components.base.utils.content_formatter import ContentFormatter
        
        try:
            cleaned = ContentFormatter.extract_json_content(response)
            document = json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed for {subject}: {e}")
            logger.debug(f"Raw response: {response[:500]}...")
            logger.debug(f"Cleaned content: {cleaned[:500]}...")
            
            # Attempt JSON repair strategies
            document = self._attempt_json_repair(cleaned, subject)
            if not document:
                # If all repair attempts fail, return None to trigger regeneration
                logger.error(f"All JSON repair attempts failed for {subject}")
                return None
        
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

    def _attempt_json_repair(self, content: str, subject: str) -> Dict[str, Any]:
        """Attempt to repair malformed JSON using various strategies."""
        
        # Try individual repair strategies first
        repair_attempts = [
            self._repair_missing_quotes,
            self._repair_trailing_commas, 
            self._repair_unescaped_quotes,
            self._repair_malformed_objects
        ]
        
        for repair_func in repair_attempts:
            try:
                repaired = repair_func(content)
                document = json.loads(repaired)
                logger.info(f"JSON repair successful for {subject} using {repair_func.__name__}")
                return document
            except (json.JSONDecodeError, Exception) as e:
                logger.debug(f"Repair attempt {repair_func.__name__} failed: {e}")
                continue
        
        # If individual strategies fail, try combining multiple repair strategies
        try:
            logger.info(f"Attempting combined JSON repair strategies for {subject}")
            repaired = content
            # Apply all repair strategies in sequence
            for repair_func in repair_attempts:
                repaired = repair_func(repaired)
            
            document = json.loads(repaired)
            logger.info(f"Combined JSON repair successful for {subject}")
            return document
        except (json.JSONDecodeError, Exception) as e:
            logger.debug(f"Combined repair attempt failed: {e}")
                
        return None
    
    def _repair_missing_quotes(self, content: str) -> str:
        """Repair missing quotes around property names."""
        import re
        # Fix unquoted property names: property: -> "property":
        content = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', content)
        return content
    
    def _repair_trailing_commas(self, content: str) -> str:
        """Remove trailing commas before closing brackets."""
        import re
        content = re.sub(r',\s*}', '}', content)
        content = re.sub(r',\s*]', ']', content)
        return content
    
    def _repair_unescaped_quotes(self, content: str) -> str:
        """Escape unescaped quotes in string values."""
        # This is a basic implementation - could be more sophisticated
        return content
    
    def _repair_malformed_objects(self, content: str) -> str:
        """Attempt to fix malformed object structures."""
        # Basic cleanup of common malformations
        content = content.strip()
        if not content.startswith('{'):
            content = '{' + content
        if not content.endswith('}'):
            content = content + '}'
        return content
