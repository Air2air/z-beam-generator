"""
Domain-Specific SEO Generators

⚠️  DEPRECATED: Use simple_seo_generator.py (SEOGenerator class) instead.
   This file contains legacy domain-specific generators that are no longer actively maintained.
   SEOGenerator provides a unified interface for all domains with better maintainability.

Each domain has unique user search intent and concerns.
These generators create SEO optimized for what users actually search for.

Research-based user intent:
- Materials: "can you laser clean X", "X laser cleaning parameters", "damage prevention"
- Contaminants: "how to remove X", "X removal from Y", "is X safe to laser clean"
- Settings: "optimal settings for X", "power for Y", "how many passes"
- Compounds: "X hazards", "safe removal of X", "X regulations"
"""

import yaml
import json
import logging
from typing import Dict, Any, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class MaterialSEOGenerator:
    """SEO for materials - focus on cleanability, parameters, damage prevention."""
    
    def __init__(self, api_client):
        self.api_client = api_client
        self.data_path = Path('data/materials/Materials.yaml')
    
    def generate(self, material_id: str) -> Tuple[bool, bool]:
        """Generate SEO for a material."""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        material = data['materials'][material_id]
        context = self._extract_context(material, material_id)
        
        prompt = f"""Create SEO for laser cleaning {context['name']}.

USER SEARCH INTENT: "can you laser clean {context['name']}", "{context['name']} laser cleaning", "how to clean {context['name']} with laser"

Key Properties Users Care About:
- Reflectivity: {context['reflectivity']}% (high = harder to clean)
- Wavelength needed: {context['wavelength']}nm (what laser type)
- Power range: {context['power']}W (operational parameters)
- Main challenge: {context['challenge']} (what makes this material difficult)
- Damage risk: {context['damage']} (what can go wrong)

Create:
1. page_title: "{context['name']}: [Solve Main Challenge] Laser Cleaning" (~55 chars, focus on PRIMARY user concern)
2. meta_description: Answer "can I laser clean this?" + key specs (%, nm, W) + damage prevention (~160 chars)

Format: JSON with page_title and meta_description"""

        return self._generate_and_save(prompt, material_id, data)
    
    def _extract_context(self, material: Dict, material_id: str) -> Dict:
        """Extract material properties."""
        name = material.get('name', material_id.replace('-laser-cleaning', '').title())
        
        props = material.get('properties', {})
        all_props = {}
        for cat_data in props.values():
            if isinstance(cat_data, dict):
                all_props.update({k: v for k, v in cat_data.items() if k not in ['label', 'description']})
        
        def safe_get(key, default='N/A'):
            val = all_props.get(key, {})
            return val.get('value', default) if isinstance(val, dict) else default
        
        return {
            'name': name,
            'reflectivity': safe_get('reflectivity'),
            'wavelength': safe_get('optimal_wavelength'),
            'power': f"{safe_get('power_min', 'N/A')}-{safe_get('power_max', 'N/A')}",
            'challenge': safe_get('primary_challenge', 'Material-specific challenges'),
            'damage': safe_get('damage_risk', 'Requires careful parameters')
        }
    
    def _generate_and_save(self, prompt: str, item_id: str, data: Dict) -> Tuple[bool, bool]:
        """Call API and save results."""
        from shared.api.client import GenerationRequest
        
        request = GenerationRequest(prompt=prompt, temperature=0.7, max_tokens=300)
        response = self.api_client.generate(request)
        
        content = response.content.strip()
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        
        seo = json.loads(content)
        
        data['materials'][item_id]['page_title'] = seo['page_title']
        data['materials'][item_id]['meta_description'] = seo['meta_description']
        
        with open(self.data_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        logger.info(f"✅ Title: {seo['page_title']} ({len(seo['page_title'])})")
        logger.info(f"✅ Desc: {seo['meta_description']} ({len(seo['meta_description'])})")
        return True, True


class ContaminantSEOGenerator:
    """SEO for contaminants - focus on removal effectiveness, safety, substrate compatibility."""
    
    def __init__(self, api_client):
        self.api_client = api_client
        self.data_path = Path('data/contaminants/Contaminants.yaml')
    
    def generate(self, contaminant_id: str) -> Tuple[bool, bool]:
        """Generate SEO for a contaminant."""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        contaminant = data['contaminants'][contaminant_id]
        context = self._extract_context(contaminant, contaminant_id)
        
        prompt = f"""Create SEO for laser removing {context['name']}.

USER SEARCH INTENT: "how to remove {context['name']}", "{context['name']} laser removal", "can laser remove {context['name']}"

Key Information Users Need:
- Removal difficulty: {context['difficulty']} (easy/hard to remove)
- Works on: {context['substrates']} (what materials it can be removed from)
- Removal method: {context['method']} (ablation/vaporization/etc)
- Safety concerns: {context['safety']} (hazards during removal)
- Common on: {context['common_on']} (where users encounter this)

Create:
1. page_title: "{context['name']} Laser Removal: [Key Benefit]" (~55 chars, focus on PRIMARY concern - effectiveness OR safety)
2. meta_description: Answer "can laser remove this?" + substrates + safety note + method (~160 chars)

Format: JSON with page_title and meta_description"""

        return self._generate_and_save(prompt, contaminant_id, data)
    
    def _extract_context(self, contaminant: Dict, contaminant_id: str) -> Dict:
        """Extract contaminant info."""
        name = contaminant.get('name', contaminant_id.replace('-', ' ').title())
        
        valid_materials = contaminant.get('valid_materials', [])
        common_on = ', '.join(valid_materials[:3]) if valid_materials else 'Various materials'
        
        return {
            'name': name,
            'difficulty': contaminant.get('removal_difficulty', 'Moderate'),
            'substrates': common_on,
            'method': contaminant.get('removal_method', 'Laser ablation'),
            'safety': contaminant.get('safety_concerns', 'Standard precautions'),
            'common_on': common_on
        }
    
    def _generate_and_save(self, prompt: str, item_id: str, data: Dict) -> Tuple[bool, bool]:
        """Call API and save results."""
        from shared.api.client import GenerationRequest
        
        request = GenerationRequest(prompt=prompt, temperature=0.7, max_tokens=300)
        response = self.api_client.generate(request)
        
        content = response.content.strip()
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        
        seo = json.loads(content)
        
        data['contaminants'][item_id]['page_title'] = seo['page_title']
        data['contaminants'][item_id]['meta_description'] = seo['meta_description']
        
        with open(self.data_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        logger.info(f"✅ Title: {seo['page_title']} ({len(seo['page_title'])})")
        logger.info(f"✅ Desc: {seo['meta_description']} ({len(seo['meta_description'])})")
        return True, True


class SettingSEOGenerator:
    """SEO for settings - focus on results achieved, when to use, parameter ranges."""
    
    def __init__(self, api_client):
        self.api_client = api_client
        self.data_path = Path('data/settings/Settings.yaml')
    
    def generate(self, setting_id: str) -> Tuple[bool, bool]:
        """Generate SEO for a setting."""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        setting = data['settings'][setting_id]
        context = self._extract_context(setting, setting_id)
        
        prompt = f"""Create SEO for laser cleaning setting: {context['name']}.

USER SEARCH INTENT: "best settings for {context['material']}", "{context['purpose']}", "power for {context['material']}"

Key Parameters Users Search For:
- Material: {context['material']} (what this setting is for)
- Power: {context['power']}W (most searched parameter)
- Speed: {context['speed']}mm/s (affects results)
- Passes: {context['passes']} (how many needed)
- Result: {context['result']} (what it achieves)
- When to use: {context['purpose']} (application)

Create:
1. page_title: "{context['material']}: [Result/Purpose] Settings" (~55 chars, focus on RESULT user wants)
2. meta_description: Power + speed + passes + result achieved + when to use (~160 chars with actual numbers)

Format: JSON with page_title and meta_description"""

        return self._generate_and_save(prompt, setting_id, data)
    
    def _extract_context(self, setting: Dict, setting_id: str) -> Dict:
        """Extract setting parameters."""
        material = setting.get('material', 'Unknown material')
        machine = setting.get('machine_settings', {})
        
        return {
            'name': setting.get('name', setting_id),
            'material': material,
            'power': machine.get('power', 'N/A'),
            'speed': machine.get('speed', 'N/A'),
            'passes': machine.get('passes', 'N/A'),
            'result': setting.get('expected_result', 'Effective cleaning'),
            'purpose': setting.get('purpose', f'Cleaning {material}')
        }
    
    def _generate_and_save(self, prompt: str, item_id: str, data: Dict) -> Tuple[bool, bool]:
        """Call API and save results."""
        from shared.api.client import GenerationRequest
        
        request = GenerationRequest(prompt=prompt, temperature=0.7, max_tokens=300)
        response = self.api_client.generate(request)
        
        content = response.content.strip()
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        
        seo = json.loads(content)
        
        data['settings'][item_id]['page_title'] = seo['page_title']
        data['settings'][item_id]['meta_description'] = seo['meta_description']
        
        with open(self.data_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        logger.info(f"✅ Title: {seo['page_title']} ({len(seo['page_title'])})")
        logger.info(f"✅ Desc: {seo['meta_description']} ({len(seo['meta_description'])})")
        return True, True


class CompoundSEOGenerator:
    """SEO for compounds - focus on safety, hazards, regulations, proper removal."""
    
    def __init__(self, api_client):
        self.api_client = api_client
        self.data_path = Path('data/compounds/Compounds.yaml')
    
    def generate(self, compound_id: str) -> Tuple[bool, bool]:
        """Generate SEO for a compound."""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        compound = data['compounds'][compound_id]
        context = self._extract_context(compound, compound_id)
        
        prompt = f"""Create SEO for hazardous compound: {context['name']}.

USER SEARCH INTENT: "{context['name']} hazards", "safe removal of {context['name']}", "{context['name']} laser cleaning safety"

Critical Safety Information:
- Hazard level: {context['hazard_level']} (severity)
- Primary hazards: {context['hazards']} (what can go wrong)
- Safety requirements: {context['safety']} (PPE, ventilation, etc)
- Regulations: {context['regulations']} (compliance needed)
- Safe removal: {context['removal']} (proper method)

Create:
1. page_title: "{context['name']}: Safe Laser Removal [Key Hazard]" (~55 chars, MUST mention safety/hazard)
2. meta_description: Hazard level + primary risks + required safety measures + compliance (~160 chars, safety-first)

Format: JSON with page_title and meta_description"""

        return self._generate_and_save(prompt, compound_id, data)
    
    def _extract_context(self, compound: Dict, compound_id: str) -> Dict:
        """Extract compound safety info."""
        name = compound.get('name', compound_id.replace('-', ' ').title())
        
        return {
            'name': name,
            'hazard_level': compound.get('hazard_level', 'Moderate'),
            'hazards': compound.get('primary_hazards', 'Chemical hazards'),
            'safety': compound.get('safety_requirements', 'PPE and ventilation required'),
            'regulations': compound.get('regulations', 'Standard safety regulations'),
            'removal': compound.get('removal_method', 'Controlled laser ablation with extraction')
        }
    
    def _generate_and_save(self, prompt: str, item_id: str, data: Dict) -> Tuple[bool, bool]:
        """Call API and save results."""
        from shared.api.client import GenerationRequest
        
        request = GenerationRequest(prompt=prompt, temperature=0.7, max_tokens=300)
        response = self.api_client.generate(request)
        
        content = response.content.strip()
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        
        seo = json.loads(content)
        
        data['compounds'][item_id]['page_title'] = seo['page_title']
        data['compounds'][item_id]['meta_description'] = seo['meta_description']
        
        with open(self.data_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        logger.info(f"✅ Title: {seo['page_title']} ({len(seo['page_title'])})")
        logger.info(f"✅ Desc: {seo['meta_description']} ({len(seo['meta_description'])})")
        return True, True


def create_seo_generator(domain: str, api_client):
    """Factory: Create appropriate SEO generator for domain."""
    generators = {
        'materials': MaterialSEOGenerator,
        'contaminants': ContaminantSEOGenerator,
        'settings': SettingSEOGenerator,
        'compounds': CompoundSEOGenerator
    }
    
    if domain not in generators:
        raise ValueError(f"Unknown domain: {domain}. Supported: {list(generators.keys())}")
    
    return generators[domain](api_client)
