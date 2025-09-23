#!/usr/bin/env python3
"""
DeepSeek-specific API Client for Z-Beam Generator

Specialized implementation for DeepSeek API with optimized parameters
and DeepSeek-specific features.
"""

import logging

from .client import APIClient, APIResponse, GenerationRequest
from .config import get_default_config

logger = logging.getLogger(__name__)


class DeepSeekClient(APIClient):
    """DeepSeek-specific API client with optimized configuration"""

    def __init__(self, api_key=None, **kwargs):
        """Initialize DeepSeek client with optimized defaults"""

        # Load DeepSeek-specific configuration
        config = get_default_config()

        # If no API key provided, get it using standardized key manager
        if api_key is None:
            from api.key_manager import get_api_key
            api_key = get_api_key("deepseek")

        # Override with any provided parameters
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)

        # Set the API key in config
        if isinstance(config, dict):
            config["api_key"] = api_key
        else:
            config.api_key = api_key

        super().__init__(config=config)

        # DeepSeek-specific optimizations
        self.model_capabilities = {
            "max_context_length": 32000,
            "supports_function_calling": True,
            "supports_json_mode": True,
            "optimal_temperature": 0.1,  # Default only - use component configs
            "optimal_top_p": 0.95,
        }

    def generate_for_component(
        self, component_type: str, material: str, prompt_template: str, **kwargs
    ) -> APIResponse:
        """Generate content optimized for specific Z-Beam components"""

        # Component-specific optimizations
        optimizations = self._get_component_optimizations(component_type)

        # Build the request with optimizations
        request = GenerationRequest(
            prompt=prompt_template,
            max_tokens=optimizations.get("max_tokens", self.config.max_tokens),
            temperature=optimizations.get("temperature", self.config.temperature),
            top_p=optimizations.get("top_p", 1.0),
            frequency_penalty=optimizations.get("frequency_penalty", 0.0),
            presence_penalty=optimizations.get("presence_penalty", 0.0),
        )

        # Add system prompt for component type
        system_prompt = self._build_component_system_prompt(component_type, material)
        if system_prompt:
            request.system_prompt = system_prompt

        # Generate with retry logic
        response = self.generate(request)

        # Post-process for component-specific requirements
        if response.success:
            response.content = self._post_process_content(
                component_type, response.content
            )

        return response

    def _get_component_optimizations(self, component_type: str) -> dict:
        """Get component-specific optimizations, preferring prompt.yaml configs"""
        
        # First try to load from component's prompt.yaml
        try:
            import yaml
            from pathlib import Path
            
            component_prompt_path = Path(f"components/{component_type}/prompt.yaml")
            if component_prompt_path.exists():
                with open(component_prompt_path, 'r') as f:
                    prompt_config = yaml.safe_load(f)
                
                # Extract generation parameters from prompt.yaml
                if 'generation_parameters' in prompt_config:
                    params = prompt_config['generation_parameters']
                    logger.info(f"Using prompt.yaml config for {component_type}: {params}")
                    return {
                        "max_tokens": params.get("max_tokens", 4000),
                        "temperature": params.get("temperature", 0.1),
                        "top_p": params.get("top_p", 0.95),
                        "frequency_penalty": params.get("frequency_penalty", 0.0),
                        "presence_penalty": params.get("presence_penalty", 0.0),
                    }
                elif 'parameters' in prompt_config:
                    params = prompt_config['parameters']
                    logger.info(f"Using prompt.yaml parameters for {component_type}: {params}")
                    return {
                        "max_tokens": params.get("max_tokens", 4000),
                        "temperature": params.get("temperature", 0.1),
                        "top_p": params.get("top_p", 0.95),
                        "frequency_penalty": params.get("frequency_penalty", 0.0),
                        "presence_penalty": params.get("presence_penalty", 0.0),
                    }
        except Exception as e:
            logger.warning(f"Could not load prompt.yaml config for {component_type}: {e}")

        # Fallback to component-specific defaults only if prompt.yaml not found
        logger.info(f"Using fallback defaults for {component_type}")
        return {"max_tokens": 4000, "temperature": 0.1, "top_p": 0.95}

    def _build_component_system_prompt(self, component_type: str, material: str) -> str:
        """Build component-specific system prompts for DeepSeek"""

        base_prompt = f"""You are an expert technical writer specializing in laser cleaning applications for {material}.
Generate high-quality, accurate, and professional content that follows industry standards and best practices."""

        component_instructions = {
            "frontmatter": """
- Generate valid YAML frontmatter with proper formatting
- Include all required fields with appropriate data types
- Use specific technical values and measurements
- Ensure chemical formulas are scientifically accurate
- Follow the exact structure specified in the prompt""",
            "content": """
- Write comprehensive, technical articles suitable for industry professionals
- Include specific laser parameters, wavelengths, and power settings
- Provide detailed technical explanations and practical applications
- Use appropriate technical terminology and industry-standard measurements
- Structure content with clear headings and logical flow""",
            "jsonld": """
- Generate valid JSON-LD structured data following Schema.org standards
- Ensure proper syntax with correct escaping and formatting
- Include relevant properties for industrial materials and processes
- Use appropriate Schema.org types and vocabulary
- Validate that all JSON syntax is correct""",
            "table": """
- Generate well-formatted Markdown tables with proper alignment
- Include relevant technical specifications and measurements
- Use consistent units and formatting throughout
- Ensure data accuracy and logical organization
- Include appropriate headers and clear categorization""",
            "metatags": """
- Generate SEO-optimized meta tags and Open Graph properties
- Create compelling, accurate descriptions within character limits
- Include relevant keywords naturally and appropriately
- Follow SEO best practices for technical content
- Ensure meta descriptions are under 160 characters""",
            "tags": """
- Generate relevant, specific tags for categorization and SEO
- Include technical terms, industry keywords, and material properties
- Balance broad and specific tags for optimal discoverability
- Avoid overly generic tags, focus on technical accuracy
- Include both material-specific and process-specific tags""",
            "text": """
- Generate concise, informative bullet points
- Focus on key technical features and benefits
- Use parallel structure and consistent formatting
- Include specific measurements and technical details
- Prioritize most important information first""",
            "caption": """
- Generate descriptive, informative image captions
- Include technical context and relevant details
- Describe visual elements and technical processes
- Use appropriate technical terminology
- Keep descriptions concise but informative""",
            "propertiestable": """
- Generate well-formatted property tables with exact 2-column structure
- Extract data from frontmatter when available, otherwise research typical values
- Use intelligent 8-character value formatting with title case
- Apply scientific notation and unit abbreviations for readability
- Ensure all values are technically accurate and properly formatted""",
        }

        instruction = component_instructions.get(
            component_type, "Generate high-quality technical content."
        )

        return (
            f"{base_prompt}\n\nSpecific instructions for {component_type}:{instruction}"
        )

    def _post_process_content(self, component_type: str, content: str) -> str:
        """Post-process generated content for component-specific requirements"""

        # Remove common DeepSeek artifacts
        content = content.strip()

        # Component-specific post-processing
        if component_type == "frontmatter":
            # Ensure proper YAML formatting
            if not content.startswith("---"):
                content = "---\n" + content
            if not content.endswith("---"):
                content = content + "\n---"

        elif component_type == "jsonld":
            # Ensure proper JSON formatting
            content = content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()

        elif component_type == "table":
            # Ensure proper table formatting
            lines = content.split("\n")
            # Remove any leading/trailing empty lines
            while lines and not lines[0].strip():
                lines.pop(0)
            while lines and not lines[-1].strip():
                lines.pop()
            content = "\n".join(lines)

        return content

    def get_model_info(self) -> dict:
        """Get information about the DeepSeek model being used"""
        return {
            "model_name": self.config.model,
            "provider": "DeepSeek",
            "capabilities": self.model_capabilities,
            "api_version": "v1",
            "optimal_use_cases": [
                "Technical documentation",
                "Structured data generation",
                "Code generation",
                "Long-form content",
                "Complex reasoning tasks",
            ],
        }


# Factory function for easy instantiation
def create_deepseek_client(**kwargs) -> DeepSeekClient:
    """Create a properly configured DeepSeek client"""
    return DeepSeekClient(**kwargs)
