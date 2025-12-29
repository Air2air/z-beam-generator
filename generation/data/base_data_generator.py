"""
Base Data Generator - Simple Research for Structured Fields

For non-text fields (numerical ranges, metadata, structured data):
- Simple API call for research
- Parse response to expected structure
- Validate format
- Save to data/*.yaml

NO quality evaluation, NO voice processing, NO humanness layer.
These are for factual data lookups, not creative text generation.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)


class BaseDataGenerator(ABC):
    """
    Base class for simple data field generators.
    
    Use this for:
    - Numerical ranges (power_intensity, wavelength, etc.)
    - Metadata (context: indoor/outdoor/industrial/marine)
    - Structured lookups (chemical formulas, property values)
    
    Do NOT use for:
    - Free-form text (descriptions, captions, FAQs)
    - Content requiring voice/tone (use QualityEvaluatedGenerator)
    """
    
    def __init__(self, api_client, domain: str, field: str):
        """
        Initialize data generator.
        
        Args:
            api_client: API client for research calls
            domain: Domain name (materials, contaminants, etc.)
            field: Field name (power_intensity, context, etc.)
        """
        self.api_client = api_client
        self.domain = domain
        self.field = field
        self.data_file = Path(f'data/{domain}/{domain.title()}.yaml')
        
        # Validate data file exists
        if not self.data_file.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_file}")
    
    @abstractmethod
    def research(self, item_name: str, item_data: Dict) -> Any:
        """
        Research the field value via API.
        
        Args:
            item_name: Item identifier (material name, contaminant ID, etc.)
            item_data: Existing item data from YAML
        
        Returns:
            Researched value (format depends on field type)
        """
        pass
    
    @abstractmethod
    def validate(self, value: Any) -> bool:
        """
        Validate the researched value meets requirements.
        
        Args:
            value: Value to validate
        
        Returns:
            True if valid, False otherwise
        """
        pass
    
    @abstractmethod
    def format_for_yaml(self, value: Any) -> Any:
        """
        Format value for YAML storage.
        
        Args:
            value: Raw researched value
        
        Returns:
            YAML-ready value (dict, list, string, number, etc.)
        """
        pass
    
    def generate(self, item_name: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Generate field value for an item.
        
        Args:
            item_name: Item identifier
            dry_run: If True, don't save to file
        
        Returns:
            Result dict with 'success', 'value', 'error' keys
        """
        logger.info(f"Generating {self.field} for {item_name} ({self.domain})")
        
        try:
            # Load item data
            with open(self.data_file, 'r') as f:
                data = yaml.safe_load(f)
            
            # Get domain key (materials, contamination_patterns, compounds, settings)
            domain_key = self._get_domain_key()
            items = data.get(domain_key, {})
            
            if item_name not in items:
                return {
                    'success': False,
                    'error': f"Item '{item_name}' not found in {self.data_file}"
                }
            
            item_data = items[item_name]
            
            # Check if field already populated
            existing = item_data.get(self.field)
            if existing and existing != 'null' and existing != '':
                logger.info(f"Field '{self.field}' already populated, skipping")
                return {
                    'success': True,
                    'value': existing,
                    'skipped': True
                }
            
            # Research value
            logger.info(f"Researching {self.field}...")
            raw_value = self.research(item_name, item_data)
            
            # Validate
            if not self.validate(raw_value):
                return {
                    'success': False,
                    'error': f"Validation failed for {self.field}: {raw_value}"
                }
            
            # Format for YAML
            yaml_value = self.format_for_yaml(raw_value)
            
            # Save if not dry run
            if not dry_run:
                items[item_name][self.field] = yaml_value
                
                with open(self.data_file, 'w') as f:
                    yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
                
                logger.info(f"✅ Saved {self.field} to {self.data_file}")
            else:
                logger.info(f"✅ Generated {self.field} (dry run - not saved)")
            
            return {
                'success': True,
                'value': yaml_value,
                'skipped': False
            }
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_domain_key(self) -> str:
        """Get the YAML key for this domain's data."""
        domain_keys = {
            'materials': 'materials',
            'contaminants': 'contamination_patterns',
            'compounds': 'compounds',
            'settings': 'settings'
        }
        return domain_keys.get(self.domain, self.domain)
