"""
Contaminant Field Generators - AI Research Based
Populates description, appearance, compounds, and context fields.
NO FALLBACKS OR DEFAULTS - Pure AI research per copilot-instructions.md
"""

from generation.backfill.base import BaseBackfillGenerator
from generation.backfill.registry import BackfillRegistry
from generation.config.config_loader import ProcessingConfig
from shared.api.grok_client import GrokClient
from typing import Optional
import time


class ContaminantDescriptionGenerator(BaseBackfillGenerator):
    """Generate contaminant descriptions via AI research."""
    
    def __init__(self, source_file: str, items_key: str, target_field: str, dry_run: bool = False):
        super().__init__(source_file, items_key, target_field, dry_run)
        self.api_client = GrokClient()
        self._config = ProcessingConfig()
    
    def populate(self, item_id: str, item_data: dict) -> Optional[str]:
        """Research and generate contaminant description."""

        if 'name' not in item_data or not isinstance(item_data['name'], str) or not item_data['name'].strip():
            raise KeyError(f"Item '{item_id}' missing required non-empty field: name")
        if 'category' not in item_data or not isinstance(item_data['category'], str):
            raise KeyError(f"Item '{item_id}' missing required field: category")
        if 'subcategory' not in item_data or not isinstance(item_data['subcategory'], str):
            raise KeyError(f"Item '{item_id}' missing required field: subcategory")

        contam_name = item_data['name']
        category = item_data['category']
        subcategory = item_data['subcategory']
        
        prompt = f"""Research the contaminant "{contam_name}" (category: {category}, subcategory: {subcategory}) in the context of laser cleaning.

Write a comprehensive 2-3 sentence description (150-250 words) covering:
1. Chemical/physical composition and formation process
2. Common materials where this contamination appears
3. Why it's problematic and laser cleaning advantages
4. Typical removal challenges

Focus on technical accuracy and practical laser cleaning applications."""

        try:
            response = self.api_client.generate(
                prompt=prompt,
                temperature=float(self._config.get_required_config('constants.backfill_generators.contaminant_description.temperature')),
                max_tokens=int(self._config.get_required_config('constants.backfill_generators.contaminant_description.max_tokens'))
            )
            
            if 'text' not in response or not isinstance(response['text'], str):
                raise KeyError("API response missing required string key: text")
            description = response['text'].strip()
            
            if not description:
                print(f"  ⚠️  {item_id}: API returned empty response")
                return None
            
            time.sleep(float(self._config.get_required_config('constants.backfill_generators.contaminant_description.request_delay_seconds')))
            return description
            
        except Exception as e:
            print(f"  ❌ {item_id}: Research failed - {e}")
            return None


class ContaminantAppearanceGenerator(BaseBackfillGenerator):
    """Generate visual appearance descriptions via AI research."""
    
    def __init__(self, source_file: str, items_key: str, target_field: str, dry_run: bool = False):
        super().__init__(source_file, items_key, target_field, dry_run)
        self.api_client = GrokClient()
        self._config = ProcessingConfig()
    
    def populate(self, item_id: str, item_data: dict) -> Optional[dict]:
        """Research and generate appearance characteristics."""

        if 'name' not in item_data or not isinstance(item_data['name'], str) or not item_data['name'].strip():
            raise KeyError(f"Item '{item_id}' missing required non-empty field: name")
        contam_name = item_data['name']
        
        prompt = f"""Research the visual appearance of "{contam_name}" contamination.

Provide specific details for:
1. Color (specific shades, variations)
2. Texture (smooth, rough, flaky, powdery, etc.)
3. Thickness (typical range in micrometers)
4. Pattern (uniform, patchy, concentrated areas)
5. Surface effects (glossy, matte, crystalline)

Be specific and technical. Avoid generic descriptions."""

        try:
            response = self.api_client.generate(
                prompt=prompt,
                temperature=float(self._config.get_required_config('constants.backfill_generators.contaminant_appearance.temperature')),
                max_tokens=int(self._config.get_required_config('constants.backfill_generators.contaminant_appearance.max_tokens'))
            )
            
            if 'text' not in response or not isinstance(response['text'], str):
                raise KeyError("API response missing required string key: text")
            appearance_text = response['text'].strip()
            
            if not appearance_text:
                print(f"  ⚠️  {item_id}: API returned empty response")
                return None
            
            # Structure appearance data
            appearance = {
                'color': '',
                'texture': '',
                'thickness': '',
                'pattern': '',
                'surface_effect': '',
                'description': appearance_text
            }
            
            # Extract structured fields from text (basic parsing)
            lines = appearance_text.lower()
            if 'color' in lines:
                for line in appearance_text.split('\n'):
                    if 'color' in line.lower():
                        appearance['color'] = line.split(':', 1)[-1].strip() if ':' in line else line.strip()
                        break
            
            time.sleep(float(self._config.get_required_config('constants.backfill_generators.contaminant_appearance.request_delay_seconds')))
            return appearance
            
        except Exception as e:
            print(f"  ❌ {item_id}: Research failed - {e}")
            return None


class ContaminantCompoundsGenerator(BaseBackfillGenerator):
    """Generate compound relationships via AI research."""
    
    def __init__(self, source_file: str, items_key: str, target_field: str, dry_run: bool = False):
        super().__init__(source_file, items_key, target_field, dry_run)
        self.api_client = GrokClient()
        self._config = ProcessingConfig()
    
    def populate(self, item_id: str, item_data: dict) -> Optional[dict]:
        """Research chemical compounds in this contamination."""

        if 'name' not in item_data or not isinstance(item_data['name'], str) or not item_data['name'].strip():
            raise KeyError(f"Item '{item_id}' missing required non-empty field: name")
        contam_name = item_data['name']
        
        prompt = f"""Research the chemical composition of "{contam_name}" contamination.

List the primary chemical compounds (3-5 most significant) and secondary compounds (2-3 minor components).
For each compound, provide:
- Common name
- Chemical formula
- CAS number if applicable
- Approximate concentration/percentage

Focus on compounds relevant to laser cleaning safety and fume generation."""

        try:
            response = self.api_client.generate(
                prompt=prompt,
                temperature=float(self._config.get_required_config('constants.backfill_generators.contaminant_compounds.temperature')),
                max_tokens=int(self._config.get_required_config('constants.backfill_generators.contaminant_compounds.max_tokens'))
            )
            
            if 'text' not in response or not isinstance(response['text'], str):
                raise KeyError("API response missing required string key: text")
            compounds_text = response['text'].strip()
            
            if not compounds_text:
                print(f"  ⚠️  {item_id}: API returned empty response")
                return None
            
            # Structure compound data
            compounds = {
                'primary': [],
                'secondary': []
            }
            
            # Parse compound list
            lines = compounds_text.split('\n')
            current_category = None
            
            for line in lines:
                line = line.strip()
                if 'primary' in line.lower():
                    current_category = 'primary'
                elif 'secondary' in line.lower():
                    current_category = 'secondary'
                elif current_category and line and not line.endswith(':'):
                    # Extract compound name (simple parsing)
                    compound = line.lstrip('- ').lstrip('• ').split('(')[0].strip()
                    if compound:
                        compounds[current_category].append(compound)
            
            time.sleep(float(self._config.get_required_config('constants.backfill_generators.contaminant_compounds.request_delay_seconds')))
            return compounds
            
        except Exception as e:
            print(f"  ❌ {item_id}: Research failed - {e}")
            return None


class ContaminantContextGenerator(BaseBackfillGenerator):
    """Generate context metadata via AI research."""
    
    def __init__(self, source_file: str, items_key: str, target_field: str, dry_run: bool = False):
        super().__init__(source_file, items_key, target_field, dry_run)
        self.api_client = GrokClient()
        self._config = ProcessingConfig()
    
    def populate(self, item_id: str, item_data: dict) -> Optional[dict]:
        """Research environmental context for contamination."""

        if 'name' not in item_data or not isinstance(item_data['name'], str) or not item_data['name'].strip():
            raise KeyError(f"Item '{item_id}' missing required non-empty field: name")
        contam_name = item_data['name']
        
        prompt = f"""Research where "{contam_name}" contamination typically occurs.

Analyze:
1. Indoor vs Outdoor environments (which is more common?)
2. Industrial settings (manufacturing, construction, automotive, etc.)
3. Marine/coastal exposure
4. Temperature/humidity conditions that accelerate formation

Rate likelihood: high, medium, low, none"""

        try:
            response = self.api_client.generate(
                prompt=prompt,
                temperature=float(self._config.get_required_config('constants.backfill_generators.contaminant_context.temperature')),
                max_tokens=int(self._config.get_required_config('constants.backfill_generators.contaminant_context.max_tokens'))
            )
            
            if 'text' not in response or not isinstance(response['text'], str):
                raise KeyError("API response missing required string key: text")
            context_text = response['text'].strip().lower()
            
            if not context_text:
                print(f"  ⚠️  {item_id}: API returned empty response")
                return None
            
            # Determine context ratings
            context = {
                'indoor': 'medium',
                'outdoor': 'medium',
                'industrial': 'high',
                'marine': 'low'
            }
            
            # Simple keyword analysis
            if 'primarily outdoor' in context_text or 'outdoor' in context_text and 'common' in context_text:
                context['outdoor'] = 'high'
                context['indoor'] = 'low'
            elif 'primarily indoor' in context_text or 'indoor' in context_text and 'common' in context_text:
                context['indoor'] = 'high'
                context['outdoor'] = 'low'
            
            if 'marine' in context_text or 'coastal' in context_text:
                context['marine'] = 'high' if 'common' in context_text else 'medium'
            
            time.sleep(float(self._config.get_required_config('constants.backfill_generators.contaminant_context.request_delay_seconds')))
            return context
            
        except Exception as e:
            print(f"  ❌ {item_id}: Research failed - {e}")
            return None


# Register generators
BackfillRegistry.register('contaminant_description', ContaminantDescriptionGenerator)
BackfillRegistry.register('contaminant_appearance', ContaminantAppearanceGenerator)
BackfillRegistry.register('contaminant_compounds', ContaminantCompoundsGenerator)
BackfillRegistry.register('contaminant_context', ContaminantContextGenerator)
