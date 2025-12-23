"""
Simple SEO Generator

Generates page_title and meta_description for ANY domain.
Writes directly to domain data files (Materials.yaml, Contaminants.yaml, etc).

Uses domain-specific prompts from domain_prompts.py that follow
PAGE_TITLE_META_DESCRIPTION_SPEC.md requirements:
- Titles: 50-55 chars with unique differentiators
- Descriptions: 155-160 chars with challenge → method → outcome
- Technical specs (reflectivity%, wavelength, power)
- Damage prevention signals
- Quality metrics
"""

import yaml
import json
import logging
from typing import Dict, Any, Tuple
from pathlib import Path
from generation.seo.domain_prompts import get_prompt_for_domain

logger = logging.getLogger(__name__)


class SimpleSEOGenerator:
    """Generate SEO metadata and write directly to data files."""
    
    def __init__(self, api_client, domain: str = 'materials'):
        """
        Initialize SEO generator.
        
        Args:
            api_client: Grok API client for generation
            domain: Domain name (materials, contaminants, settings, compounds)
        """
        self.api_client = api_client
        self.domain = domain
        
        # Map domain to data file
        domain_files = {
            'materials': 'data/materials/Materials.yaml',
            'contaminants': 'data/contaminants/Contaminants.yaml',
            'settings': 'data/settings/Settings.yaml',
            'compounds': 'data/compounds/Compounds.yaml'
        }
        self.data_path = Path(domain_files.get(domain, f'data/{domain}/{domain.capitalize()}.yaml'))
        
        # Map domain to root key
        self.root_key = domain
        
    def generate_for_item(self, item_id: str) -> Tuple[bool, bool]:
        """
        Generate both page_title and meta_description for any domain item.
        
        Args:
            item_id: Item identifier (e.g., "aluminum-laser-cleaning", "rust", "speed")
            
        Returns:
            Tuple of (title_success, description_success)
        """
        # Load data
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if item_id not in data[self.root_key]:
            logger.error(f"Item not found: {item_id}")
            return False, False
        
        item = data[self.root_key][item_id]
        
        # Extract data for prompt
        context = self._extract_context(item, item_id)
        
        # Generate SEO content
        try:
            seo_content = self._call_api(context)
            
            # Write to data file
            data[self.root_key][item_id]['page_title'] = seo_content['page_title']
            data[self.root_key][item_id]['meta_description'] = seo_content['meta_description']
            
            with open(self.data_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            logger.info(f"✅ Saved SEO for {item_id}")
            logger.info(f"   Title: {seo_content['page_title']} ({len(seo_content['page_title'])} chars)")
            logger.info(f"   Desc: {seo_content['meta_description']} ({len(seo_content['meta_description'])} chars)")
            
            return True, True
            
        except Exception as e:
            logger.error(f"❌ SEO generation failed: {e}")
            return False, False
    
    def _extract_context(self, material: Dict[str, Any], material_id: str) -> Dict[str, str]:
        """Extract relevant data from material for SEO generation."""
        material_name = material.get('name', material_id.replace('-laser-cleaning', '').title())
        category = material.get('category', 'Unknown')
        
        # Flatten properties from nested structure
        properties = material.get('properties', {})
        all_props = {}
        
        # Debug: Check structure
        logger.info(f"Properties keys: {list(properties.keys())}")
        
        for cat_name, cat_data in properties.items():
            if isinstance(cat_data, dict):
                for prop_name, prop_val in cat_data.items():
                    if prop_name not in ['label', 'description']:
                        all_props[prop_name] = prop_val
        
        logger.info(f"Flattened {len(all_props)} properties")
        
        # Extract key properties with safety checks
        reflectivity = all_props.get('reflectivity', {})
        if isinstance(reflectivity, dict):
            reflectivity = reflectivity.get('value', 'N/A')
        
        absorption = all_props.get('absorption', {})
        if isinstance(absorption, dict):
            absorption = absorption.get('value', 'N/A')
        
        wavelength = all_props.get('optimal_wavelength', {})
        if isinstance(wavelength, dict):
            wavelength = wavelength.get('value', 'N/A')
        
        # Extract power range with safety checks
        power_min = 'N/A'
        power_max = 'N/A'
        if 'power_range' in all_props:
            pr = all_props['power_range']
            if isinstance(pr, dict):
                power_min = pr.get('min', 'N/A')
                power_max = pr.get('max', 'N/A')
        
        primary_challenge = all_props.get('primary_challenge', 'Material-specific challenges')
        if isinstance(primary_challenge, dict):
            primary_challenge = primary_challenge.get('value', 'Material-specific challenges')
        
        return {
            'material_name': material_name,
            'category': category,
            'reflectivity': str(reflectivity),
            'absorption': str(absorption),
            'wavelength': str(wavelength),
            'power_min': str(power_min),
            'power_max': str(power_max),
            'primary_challenge': str(primary_challenge)
        }
    
    def _call_api(self, context: Dict[str, str]) -> Dict[str, str]:
        """
        Call Grok API to generate SEO content using domain-specific prompts.
        
        Prompts follow PAGE_TITLE_META_DESCRIPTION_SPEC.md:
        - Titles: Under 60 chars (50-55 optimal, +9 for " | Z-Beam")
        - Descriptions: 155-160 chars with specific metrics
        - Format: [Challenge] → [Method with specs] → [Outcome/Benefit]
        """
        # Get domain-specific prompt from spec-compliant templates
        prompt = get_prompt_for_domain(self.domain, context)

        from shared.api.client import GenerationRequest
        
        request = GenerationRequest(
            prompt=prompt,
            temperature=0.7,
            max_tokens=300
        )
        
        response = self.api_client.generate(request)
        
        # Parse JSON response
        content = response.content.strip()
        
        # Extract JSON if wrapped in markdown code blocks
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        
        seo_data = json.loads(content)
        
        return {
            'page_title': seo_data['page_title'],
            'meta_description': seo_data['meta_description']
        }
