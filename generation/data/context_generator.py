"""
Context Metadata Generator

Generates environmental context metadata (indoor/outdoor/industrial/marine).
Simple research + parsing, no quality evaluation.
"""

import logging
import re
from typing import Any, Dict

from generation.data.base_data_generator import BaseDataGenerator

logger = logging.getLogger(__name__)


class ContextGenerator(BaseDataGenerator):
    """Generate context metadata for materials or contaminants."""
    
    def __init__(self, api_client, domain: str):
        super().__init__(api_client, domain, 'context')
    
    def research(self, item_name: str, item_data: Dict) -> Dict[str, str]:
        """
        Research environmental context via API.
        
        Returns:
            Dict with 'indoor', 'outdoor', 'industrial', 'marine' keys
        """
        if 'name' not in item_data:
            raise ValueError(f"Missing 'name' field for item {item_name}")
        display_name = item_data['name']
        
        # Build domain-specific prompt
        if self.domain == 'materials':
            prompt = f"""Research where {display_name} is typically used and cleaned with lasers.

Analyze:
1. Indoor vs outdoor usage patterns
2. Industrial settings and applications
3. Marine/coastal exposure likelihood

Provide ONLY a structured assessment in this format:
indoor: [high/medium/low]
outdoor: [high/medium/low]
industrial: [high/medium/low]
marine: [high/medium/low]

Respond with ONLY the four lines above, no additional text."""
        else:  # contaminants
            prompt = f"""Research where {display_name} typically forms and which environments it's most common in.

Analyze:
1. Indoor vs outdoor occurrence
2. Industrial settings prevalence
3. Marine/coastal exposure patterns

Provide ONLY a structured assessment:
indoor: [high/medium/low/none]
outdoor: [high/medium/low/none]
industrial: [high/medium/low/none]
marine: [high/medium/low/none]

Respond with ONLY the four lines above, no additional text."""
        
        # API call (low temp for factual research)
        from shared.api.client import GenerationRequest
        
        request = GenerationRequest(
            prompt=prompt,
            temperature=0.3,
            max_tokens=100
        )
        
        response = self.api_client.generate(request)
        
        if not response.success:
            raise ValueError(f"API call failed: {response.error}")
        
        content = response.content
        
        # Parse response
        result = {}
        for context_type in ['indoor', 'outdoor', 'industrial', 'marine']:
            match = re.search(
                rf'{context_type}:\s*(high|medium|low|none)',
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
