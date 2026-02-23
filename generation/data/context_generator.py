"""
Context Metadata Generator

Generates environmental context metadata (indoor/outdoor/industrial/marine).
Simple research + parsing, no quality evaluation.
"""

import logging
import re
from typing import Any, Dict

from generation.config.config_loader import ProcessingConfig
from generation.data.base_data_generator import BaseDataGenerator

logger = logging.getLogger(__name__)


class ContextGenerator(BaseDataGenerator):
    """Generate context metadata for materials or contaminants."""
    
    def __init__(self, api_client, domain: str):
        super().__init__(api_client, domain, 'context')

        self.context_config = self._get_context_config()

    def _get_context_config(self) -> Dict[str, Any]:
        from generation.config.config_loader import get_config

        config = get_config().config
        data_generators = config.get('data_generators')
        if not isinstance(data_generators, dict):
            raise KeyError("Missing required config block: data_generators")

        context_cfg = data_generators.get('context')
        if not isinstance(context_cfg, dict):
            raise KeyError("Missing required config block: data_generators.context")

        prompt_templates = context_cfg.get('prompt_templates')
        allowed_values_map = context_cfg.get('allowed_values')
        if not isinstance(prompt_templates, dict):
            raise KeyError("Missing required config block: data_generators.context.prompt_templates")
        if not isinstance(allowed_values_map, dict):
            raise KeyError("Missing required config block: data_generators.context.allowed_values")

        if self.domain not in prompt_templates:
            raise KeyError(
                f"Missing context prompt template for domain '{self.domain}'"
            )
        if self.domain not in allowed_values_map:
            raise KeyError(
                f"Missing context allowed_values for domain '{self.domain}'"
            )

        prompt_template = prompt_templates[self.domain]
        if not isinstance(prompt_template, str) or not prompt_template.strip():
            raise ValueError(
                f"Context prompt template for domain '{self.domain}' must be a string"
            )

        allowed_values = allowed_values_map[self.domain]
        if not isinstance(allowed_values, list) or not allowed_values:
            raise ValueError(
                f"Context allowed_values for domain '{self.domain}' must be a list"
            )
        for value in allowed_values:
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"Context allowed_values for domain '{self.domain}' must be non-empty strings"
                )

        return {
            'prompt_template': prompt_template,
            'allowed_values': allowed_values
        }
    
    def research(self, item_name: str, item_data: Dict) -> Dict[str, str]:
        """
        Research environmental context via API.
        
        Returns:
            Dict with 'indoor', 'outdoor', 'industrial', 'marine' keys
        """
        if 'name' not in item_data:
            raise ValueError(f"Missing 'name' field for item {item_name}")
        display_name = item_data['name']
        
        prompt_template = self.context_config['prompt_template']
        prompt = prompt_template.format(display_name=display_name)
        
        # API call (low temp for factual research)
        from shared.api.client import GenerationRequest
        config = ProcessingConfig()
        
        request = GenerationRequest(
            prompt=prompt,
            temperature=float(config.get_required_config('constants.data_generators.context.temperature')),
            max_tokens=int(config.get_required_config('constants.data_generators.context.max_tokens'))
        )
        
        response = self.api_client.generate(request)
        
        if not response.success:
            raise ValueError(f"API call failed: {response.error}")
        
        content = response.content
        
        # Parse response
        result = {}
        allowed_values = self.context_config['allowed_values']
        allowed_pattern = '|'.join(re.escape(value) for value in allowed_values)
        for context_type in ['indoor', 'outdoor', 'industrial', 'marine']:
            match = re.search(
                rf'{context_type}:\s*({allowed_pattern})',
                content,
                re.IGNORECASE
            )
            if match:
                result[context_type] = match.group(1).lower()
            else:
                raise ValueError(f"Could not parse {context_type} from response: {content}")
        
        return result
    
    def validate(self, value: Dict[str, str]) -> bool:
        """
        Validate context metadata.
        
        Checks:
        - All four keys present
        - Values are valid levels
        """
        required_keys = ['indoor', 'outdoor', 'industrial', 'marine']
        valid_values = {'high', 'medium', 'low', 'none'}
        
        if not isinstance(value, dict):
            return False
        
        for key in required_keys:
            if key not in value:
                logger.error(f"Missing required key: {key}")
                return False
            
            if value[key] not in valid_values:
                logger.error(f"Invalid value for {key}: {value[key]} (must be high/medium/low/none)")
                return False
        
        return True
    
    def format_for_yaml(self, value: Dict[str, str]) -> Dict[str, str]:
        """Format context metadata for YAML storage."""
        return {
            'indoor': value['indoor'],
            'outdoor': value['outdoor'],
            'industrial': value['industrial'],
            'marine': value['marine']
        }
