"""
Power Intensity Data Generator

Generates min/max laser power intensity ranges for materials.
Simple research + parsing, no quality evaluation.
"""

import logging
import re
from typing import Any, Dict

from generation.config.config_loader import ProcessingConfig
from generation.data.base_data_generator import BaseDataGenerator

logger = logging.getLogger(__name__)


class PowerIntensityGenerator(BaseDataGenerator):
    """Generate power_intensity ranges for materials."""
    
    def __init__(self, api_client, domain: str = 'materials'):
        super().__init__(api_client, domain, 'power_intensity')
    
    def research(self, item_name: str, item_data: Dict) -> Dict[str, float]:
        """
        Research power intensity range via API.
        
        Returns:
            Dict with 'min_intensity' and 'max_intensity' keys (W/cm²)
        """
        # Build research prompt
        if 'name' not in item_data:
            raise ValueError(f"Missing 'name' field for item {item_name}")
        display_name = item_data['name']
        
        prompt = f"""Research the optimal laser power intensity range for cleaning {display_name}.

Consider:
1. Material thermal properties and damage threshold
2. Typical contamination bonding strength
3. Industry standards and safety margins

Provide ONLY the numerical range in this exact format:
min_intensity: [number] W/cm²
max_intensity: [number] W/cm²

Example:
min_intensity: 500 W/cm²
max_intensity: 2000 W/cm²

Respond with ONLY the two lines above, no additional text."""
        
        # API call (no quality evaluation needed for data lookup)
        from shared.api.client import GenerationRequest
        config = ProcessingConfig()
        
        request = GenerationRequest(
            prompt=prompt,
            temperature=float(config.get_required_config('constants.data_generators.power_intensity.temperature')),
            max_tokens=int(config.get_required_config('constants.data_generators.power_intensity.max_tokens'))
        )
        
        response = self.api_client.generate(request)
        
        if not response.success:
            raise ValueError(f"API call failed: {response.error}")
        
        # Parse response
        content = response.content
        
        # Extract values using regex
        min_match = re.search(r'min_intensity:\s*(\d+(?:\.\d+)?)\s*W/cm²?', content, re.IGNORECASE)
        max_match = re.search(r'max_intensity:\s*(\d+(?:\.\d+)?)\s*W/cm²?', content, re.IGNORECASE)
        
        if not min_match or not max_match:
            raise ValueError(f"Could not parse intensity values from response: {content}")
        
        min_val = float(min_match.group(1))
        max_val = float(max_match.group(1))
        
        return {
            'min_intensity': min_val,
            'max_intensity': max_val
        }
    
    def validate(self, value: Dict[str, float]) -> bool:
        """
        Validate intensity range.
        
        Checks:
        - Both min and max present
        - Values are positive
        - Max > min
        - Range is reasonable (min >= 100, max <= 10000)
        """
        if not isinstance(value, dict):
            return False
        
        if 'min_intensity' not in value or 'max_intensity' not in value:
            return False
        
        min_val = value['min_intensity']
        max_val = value['max_intensity']
        
        if min_val <= 0 or max_val <= 0:
            logger.error(f"Intensity values must be positive: {value}")
            return False
        
        if max_val <= min_val:
            logger.error(f"Max intensity must be greater than min: {value}")
            return False
        
        if min_val < 100 or max_val > 10000:
            logger.warning(f"Intensity range unusual (expected 100-10000 W/cm²): {value}")
            # Allow but warn
        
        return True
    
    def format_for_yaml(self, value: Dict[str, float]) -> Dict[str, float]:
        """Format intensity range for YAML storage."""
        return {
            'min_intensity': value['min_intensity'],
            'max_intensity': value['max_intensity']
        }
