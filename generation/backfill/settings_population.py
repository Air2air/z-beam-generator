"""
Settings Description & Recommendations Generator - AI Research Based
Populates description and recommendations fields for settings.
NO FALLBACKS OR DEFAULTS - Pure AI research per copilot-instructions.md
"""

from generation.backfill.base import BaseBackfillGenerator
from generation.backfill.registry import BackfillRegistry
from generation.config.config_loader import ProcessingConfig
from shared.api.grok_client import GrokClient
from typing import Optional
import time


class SettingsDescriptionGenerator(BaseBackfillGenerator):
    """Generate settings descriptions via AI research."""
    
    def __init__(self, source_file: str, items_key: str, target_field: str, dry_run: bool = False):
        super().__init__(source_file, items_key, target_field, dry_run)
        self.api_client = GrokClient()
        self._config = ProcessingConfig()
    
    def populate(self, item_id: str, item_data: dict) -> Optional[str]:
        """Research and generate setting description using AI."""

        if 'material_name' not in item_data or not isinstance(item_data['material_name'], str) or not item_data['material_name'].strip():
            raise KeyError(f"Item '{item_id}' missing required non-empty field: material_name")
        material_name = item_data['material_name']
        
        prompt = f"""Research optimal laser cleaning settings for "{material_name}".

Write a comprehensive 2-3 sentence description (150-250 words) covering:
1. Why these specific laser parameters are optimal for this material
2. Key considerations (surface damage, cleaning efficiency, safety)
3. Industry best practices and typical applications

Focus on technical accuracy and practical guidance."""

        try:
            response = self.api_client.generate(
                prompt=prompt,
                temperature=float(self._config.get_required_config('constants.backfill_generators.settings_description.temperature')),
                max_tokens=int(self._config.get_required_config('constants.backfill_generators.settings_description.max_tokens'))
            )
            
            if 'text' not in response or not isinstance(response['text'], str):
                raise KeyError("API response missing required string key: text")
            description = response['text'].strip()
            
            if not description:
                print(f"  ⚠️  {item_id}: API returned empty response")
                return None
            
            time.sleep(float(self._config.get_required_config('constants.backfill_generators.settings_description.request_delay_seconds')))
            return description
            
        except Exception as e:
            print(f"  ❌ {item_id}: Research failed - {e}")
            return None


class SettingsRecommendationsGenerator(BaseBackfillGenerator):
    """Generate settings recommendations via AI research."""
    
    def __init__(self, source_file: str, items_key: str, target_field: str, dry_run: bool = False):
        super().__init__(source_file, items_key, target_field, dry_run)
        self.api_client = GrokClient()
        self._config = ProcessingConfig()
    
    def populate(self, item_id: str, item_data: dict) -> Optional[dict]:
        """Research and generate recommendations using AI."""

        if 'material_name' not in item_data or not isinstance(item_data['material_name'], str) or not item_data['material_name'].strip():
            raise KeyError(f"Item '{item_id}' missing required non-empty field: material_name")
        material_name = item_data['material_name']
        
        prompt = f"""Research laser cleaning recommendations for "{material_name}".

Provide specific recommendations in these categories:
1. Pre-cleaning preparation (surface inspection, cleaning)
2. Parameter optimization (power, frequency, speed adjustments)
3. Safety considerations (PPE, ventilation, hazards)
4. Quality control (inspection methods, success criteria)

Format as structured guidance with 2-3 specific recommendations per category."""

        try:
            response = self.api_client.generate(
                prompt=prompt,
                temperature=float(self._config.get_required_config('constants.backfill_generators.settings_recommendations.temperature')),
                max_tokens=int(self._config.get_required_config('constants.backfill_generators.settings_recommendations.max_tokens'))
            )
            
            if 'text' not in response or not isinstance(response['text'], str):
                raise KeyError("API response missing required string key: text")
            recommendations_text = response['text'].strip()
            
            if not recommendations_text:
                print(f"  ⚠️  {item_id}: API returned empty response")
                return None
            
            # Structure recommendations
            recommendations = {
                'preparation': [],
                'optimization': [],
                'safety': [],
                'quality_control': []
            }
            
            # Parse AI response into structured format
            # (Simple parsing - could be enhanced with better NLP)
            lines = [l.strip() for l in recommendations_text.split('\n') if l.strip()]
            current_category = None
            
            for line in lines:
                if 'preparation' in line.lower():
                    current_category = 'preparation'
                elif 'optimization' in line.lower() or 'parameter' in line.lower():
                    current_category = 'optimization'
                elif 'safety' in line.lower():
                    current_category = 'safety'
                elif 'quality' in line.lower():
                    current_category = 'quality_control'
                elif current_category and line and not line.endswith(':'):
                    recommendations[current_category].append(line.lstrip('- ').lstrip('• '))
            
            time.sleep(float(self._config.get_required_config('constants.backfill_generators.settings_recommendations.request_delay_seconds')))
            return recommendations
            
        except Exception as e:
            print(f"  ❌ {item_id}: Research failed - {e}")
            return None


# Register generators
BackfillRegistry.register('settings_description', SettingsDescriptionGenerator)
BackfillRegistry.register('settings_recommendations', SettingsRecommendationsGenerator)
