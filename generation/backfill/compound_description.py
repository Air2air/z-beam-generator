"""
Compound Description Generator - AI Research Based
Populates description field for compounds using web research.
NO FALLBACKS OR DEFAULTS - Pure AI research per copilot-instructions.md
"""

from generation.backfill.base import BaseBackfillGenerator
from generation.backfill.registry import BackfillRegistry
from shared.api.grok_client import GrokClient
from typing import Optional
import time


class CompoundDescriptionGenerator(BaseBackfillGenerator):
    """Generate compound descriptions via AI research."""
    
    def __init__(self, source_file: str, items_key: str, target_field: str, dry_run: bool = False):
        super().__init__(source_file, items_key, target_field, dry_run)
        self.api_client = GrokClient()
    
    def populate(self, item_id: str, item_data: dict) -> Optional[str]:
        """Research and generate compound description using AI."""
        
        # Extract compound details
        compound_name = item_data.get('display_name', item_data.get('name', item_id))
        formula = item_data.get('chemical_formula', '')
        cas = item_data.get('cas_number', '')
        category = item_data.get('category', '')
        
        # Build research prompt
        prompt = f"""Research the chemical compound "{compound_name}" (formula: {formula}, CAS: {cas}) in the context of laser cleaning operations.

Category: {category}

Write a comprehensive 2-3 sentence description (150-250 words) covering:
1. Chemical properties and structure
2. How this compound is generated during laser cleaning
3. Health hazards and exposure risks
4. Monitoring and safety considerations

Focus on practical laser cleaning safety. Use natural professional language."""

        try:
            response = self.api_client.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=500
            )
            
            description = response.get('text', '').strip()
            
            if not description:
                print(f"  ⚠️  {item_id}: API returned empty response")
                return None
            
            time.sleep(0.5)
            return description
            
        except Exception as e:
            print(f"  ❌ {item_id}: Research failed - {e}")
            return None


# Register generator
BackfillRegistry.register('compound_description', CompoundDescriptionGenerator)
