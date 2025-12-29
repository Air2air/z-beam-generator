"""
Materials Description Generator - AI Research Based
Populates description field for materials using web research.
NO FALLBACKS OR DEFAULTS - Pure AI research per copilot-instructions.md
"""

from generation.backfill.base import BaseBackfillGenerator
from generation.backfill.registry import BackfillRegistry
from shared.api.grok_client import GrokClient
from typing import Dict, Any
import time


class MaterialDescriptionGenerator(BaseBackfillGenerator):
    """Generate comprehensive material descriptions via AI research."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_client = GrokClient()
    
    def populate(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Research and generate material description using AI."""
        
        # Skip if already populated
        if item_data.get('description'):
            return item_data
        
        # Extract material name
        item_id = item_data.get('id', '')
        material_name = item_data.get('name', item_id.replace('-laser-cleaning', '').replace('-', ' ').title())
        
        # Get category for context
        category = item_data.get('category', '')
        
        # Build research prompt
        prompt = f"""Research the material "{material_name}" in the context of laser cleaning applications.

Material Category: {category}

Write a comprehensive 2-3 sentence description (150-250 words) that covers:
1. Material composition and key physical properties
2. Common laser cleaning applications and industries
3. Unique challenges or advantages for laser cleaning

Focus on technical accuracy and practical applications. Do NOT use generic phrases like "presents a challenge" or "is essential for".

Write in a natural, professional tone."""

        try:
            # Call API for research
            response = self.api_client.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=500
            )
            
            description = response.get('text', '').strip()
            
            if description:
                item_data['description'] = description
                print(f"  🔧 {item_id}: Generated ({len(description)} chars)")
            else:
                print(f"  ⚠️  {item_id}: API returned empty response")
            
            # Rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ❌ {item_id}: Research failed - {e}")
        
        return item_data


# Register generator
BackfillRegistry.register('material_description', MaterialDescriptionGenerator)
