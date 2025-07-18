import logging
import os
import sys
import yaml
from typing import Dict, Any, List, Optional
from api_client import APIClient as ApiClient  # Aliasing to maintain compatibility

# Add parent directory to Python path to allow importing sibling packages
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
    


logger = logging.getLogger(__name__)

class ContentGenerator:
    """Generates schema-driven article content with customizable parameters."""

    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str):
        self.context = context
        self.schema = schema
        self.ai_provider = ai_provider
        self.options = {}
        self.frontmatter = {}
        
        # Load the main content prompt template
        self.prompt_template = self._load_prompt_template()
        
        # Load section prompts
        self.section_prompts = self._load_section_prompts()
        
        logger.info(f"ContentGenerator initialized for {context['article_type']}: {context['subject']}")

    def set_frontmatter(self, frontmatter: Dict[str, Any]) -> 'ContentGenerator':
        """Set frontmatter data for content enrichment."""
        self.frontmatter = frontmatter or {}
        return self

    def set_options(self, options: Dict[str, Any]) -> 'ContentGenerator':
        """Set component-specific options."""
        self.options = options or {}
        return self
    
    def _load_prompt_template(self) -> str:
        """Load the main content prompt template."""
        prompt_path = os.path.join(os.path.dirname(__file__), "prompt.yaml")
        try:
            with open(prompt_path, 'r') as file:
                prompt_data = yaml.safe_load(file)
                return prompt_data.get("template", "")
        except Exception as e:
            logger.error(f"Failed to load content prompt template: {e}")
            return ""
    
    def _load_section_prompts(self) -> Dict[str, str]:
        """Load section-specific prompts."""
        section_path = os.path.join(os.path.dirname(__file__), "sections.yaml")
        try:
            with open(section_path, 'r') as file:
                return yaml.safe_load(file) or {}
        except Exception as e:
            logger.error(f"Failed to load section prompts: {e}")
            return {}
        
    def generate(self) -> str:
        """Generate content based on schema and options."""
        article_type = self.context['article_type']
        subject = self.context['subject']
        
        # Get configuration
        min_words = self.options.get("min_words", 300)
        max_words = self.options.get("max_words", 1000)
        target_paragraphs = self.options.get("paragraphs", 5)
        
        # Determine which sections to include
        requested_sections = self.options.get("sections", [])
        available_sections = list(self.section_prompts.keys())
        
        sections_to_generate = []
        if not requested_sections:
            # If no specific sections requested, use all available sections
            sections_to_generate = available_sections
        else:
            # Use only requested sections that exist
            for section_name in requested_sections:
                if section_name in available_sections:
                    sections_to_generate.append(section_name)
                else:
                    logger.warning(f"Requested section '{section_name}' not found, skipping")
    
        if not sections_to_generate:
            logger.error("No valid sections to generate content for")
            return ""
            
        logger.info(f"Generating content for sections: {', '.join(sections_to_generate)}")
        
        # Build section prompts text
        section_prompts_text = ""
        for section_name in sections_to_generate:
            section_prompt = self.section_prompts.get(section_name, "")
            if section_prompt:
                # Get section-specific data (excluding 'subject' to avoid conflict)
                section_data = self._get_section_specific_data(section_name)
                
                # Format with subject and section data (but don't duplicate 'subject')
                try:
                    formatted_section = section_prompt.format(subject=subject, **section_data)
                    section_prompts_text += formatted_section + "\n\n"
                except KeyError as e:
                    logger.warning(f"Missing format key for section '{section_name}': {e}")
                    # Fallback - try with just subject
                    formatted_section = section_prompt.format(subject=subject)
                    section_prompts_text += formatted_section + "\n\n"
    
        # Format the main prompt
        frontmatter_context = self._extract_frontmatter_context()
        
        formatted_prompt = self.prompt_template.format(
            article_type=article_type,
            subject=subject,
            min_words=min_words,
            max_words=max_words,
            paragraphs=target_paragraphs,
            num_sections=len(sections_to_generate),
            sections=", ".join(sections_to_generate),
            section_prompts=section_prompts_text,
            frontmatter_context=frontmatter_context
        )
        
        # Generate content using AI provider
        client = ApiClient(self.ai_provider)
        
        # Set parameters - use a simple integer instead of a dictionary
        max_tokens = int(max_words * 1.5)  # Words to tokens approximation
        
        try:
            # Get content from AI
            content = client.generate(formatted_prompt, max_tokens)
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return ""
    
        if not content:
            logger.error("Failed to generate article content")
            return ""
            
        # Check if we meet minimum length requirements
        word_count = len(content.split())
        logger.info(f"Generated content with {word_count} words")
        
        if word_count < min_words:
            logger.warning(f"Generated content ({word_count} words) is below minimum ({min_words} words)")
            
        return content
    
    def _extract_frontmatter_context(self) -> str:
        """Extract relevant data from frontmatter to enrich content."""
        if not self.frontmatter:
            return ""
            
        context_parts = []
        
        # Extract key metadata based on article type
        article_type = self.context.get('article_type')
        
        # Common fields across all types
        if "description" in self.frontmatter:
            context_parts.append(f"Description: {self.frontmatter['description']}")
            
        if "keywords" in self.frontmatter and isinstance(self.frontmatter["keywords"], list):
            context_parts.append(f"Keywords: {', '.join(self.frontmatter['keywords'])}")
        
        # Type-specific fields
        if article_type == "material":
            # Extract material properties
            if "properties" in self.frontmatter:
                props = self.frontmatter["properties"]
                if isinstance(props, dict):
                    for key, value in props.items():
                        context_parts.append(f"{key}: {value}")
                        
            # Extract compatibility information
            if "compatibility" in self.frontmatter:
                compat = self.frontmatter["compatibility"]
                if isinstance(compat, list):
                    context_parts.append(f"Compatible with: {', '.join(compat)}")
                    
        elif article_type == "region":
            # Extract region-specific data
            if "location" in self.frontmatter:
                loc = self.frontmatter["location"]
                if isinstance(loc, dict):
                    city = loc.get("city", "")
                    state = loc.get("state", "")
                    country = loc.get("country", "")
                    context_parts.append(f"Location: {city}, {state}, {country}")
                    
            # Extract regional industries
            if "industries" in self.frontmatter and isinstance(self.frontmatter["industries"], list):
                context_parts.append(f"Key Industries: {', '.join(self.frontmatter['industries'])}")
        
        # Extract regulatory standards if available
        if "regulatoryStandards" in self.frontmatter and isinstance(self.frontmatter["regulatoryStandards"], list):
            standards = []
            for std in self.frontmatter["regulatoryStandards"]:
                if isinstance(std, dict) and "code" in std:
                    standards.append(std["code"])
            if standards:
                context_parts.append(f"Regulatory Standards: {', '.join(standards)}")
        
        # Join all context parts
        return "\n".join(context_parts)
    
    def _get_section_specific_data(self, section_name) -> Dict[str, str]:
        """Get section-specific data from frontmatter."""
        data = {}  # Don't include subject here to avoid duplication

        # Add general properties from frontmatter
        if hasattr(self, 'frontmatter') and self.frontmatter:
            if "description" in self.frontmatter:
                data["description"] = self.frontmatter["description"]

            # Add section-specific properties
            if section_name == "technicalSpecifications" and "properties" in self.frontmatter:
                if isinstance(self.frontmatter["properties"], dict):
                    props_text = "\n".join([f"- {k}: {v}" for k, v in self.frontmatter["properties"].items()])
                    data["properties"] = props_text

            elif section_name == "applications" and "applications" in self.frontmatter:
                # Handle applications which may be a list of strings or dictionaries
                if isinstance(self.frontmatter["applications"], list):
                    app_list = []
                    for app in self.frontmatter["applications"]:
                        if isinstance(app, str):
                            app_list.append(app)
                        elif isinstance(app, dict) and "name" in app:
                            app_list.append(app["name"])
                        elif isinstance(app, dict) and "application" in app:
                            app_list.append(app["application"])
                
                if app_list:
                    data["applications"] = ", ".join(app_list)
                else:
                    # If we couldn't extract any application names, use a generic message
                    data["applications"] = "various industrial applications"

            elif section_name == "challenges" and "challenges" in self.frontmatter:
                if isinstance(self.frontmatter["challenges"], list):
                    challenges = []
                    for challenge in self.frontmatter["challenges"]:
                        if isinstance(challenge, dict):
                            issue = challenge.get("issue", "")
                            solution = challenge.get("solution", "")
                            if issue:
                                challenges.append(f"{issue}: {solution}")
                        elif isinstance(challenge, str):
                            challenges.append(challenge)
                
                if challenges:
                    data["challenges"] = "\n".join(challenges)

        return data