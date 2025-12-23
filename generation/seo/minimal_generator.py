"""Minimal SEO Generator - Direct to YAML"""

import yaml
import json
from pathlib import Path


class MinimalSEOGenerator:
    """Generate SEO and write directly to Materials.yaml."""
    
    def __init__(self, api_client):
        self.api_client = api_client
        self.data_path = Path('data/materials/Materials.yaml')
        
    def generate(self, material_id: str):
        """Generate both SEO fields for a material."""
        try:
            # Load
            with open(self.data_path, 'r') as f:
                data = yaml.safe_load(f)
            
            material = data['materials'][material_id]
            name = material.get('name', material_id.replace('-laser-cleaning', '').title())
            
            # Prompt
            prompt = f"""You are an SEO copywriter. Generate metadata for {name} laser cleaning.

CRITICAL CHARACTER LIMITS (count carefully):
1. page_title: 50-55 characters TOTAL (including spaces and punctuation)
2. meta_description: 155-160 characters TOTAL (including spaces and punctuation)

DO NOT exceed these limits. Count every character.

Example good title (50 chars): "Aluminum: High Reflectivity Laser Cleaning"
Example good description (155 chars): "High reflectivity (88%) requires 1064nm, 100-300W. Prevents heat damage, preserves finish. Aerospace-grade surface treatment for aluminum components."

Return ONLY JSON:
{{
  "page_title": "",
  "meta_description": ""
}}"""

            # Generate
            from shared.api.client import GenerationRequest
            req = GenerationRequest(prompt=prompt, temperature=0.7, max_tokens=300)
            resp = self.api_client.generate(req)
            
            # Parse
            content = resp.content.strip()
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]
            
            seo = json.loads(content.strip())
            
            # Write
            data['materials'][material_id]['page_title'] = seo['page_title']
            data['materials'][material_id]['meta_description'] = seo['meta_description']
            
            with open(self.data_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            print(f"   ✅ Title: {seo['page_title']} ({len(seo['page_title'])})")
            print(f"   ✅ Desc: {seo['meta_description']} ({len(seo['meta_description'])})")
            
            return True, True
            
        except Exception as e:
            print(f"   ❌ {e}")
            return False, False
