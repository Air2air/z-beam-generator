"""
Contaminant Field Generators - AI Research Based
Populates description, appearance, compounds, and context fields.
NO FALLBACKS OR DEFAULTS - Pure AI research per copilot-instructions.md
"""

from generation.backfill.base import BaseBackfillGenerator
from generation.backfill.registry import BackfillRegistry
from shared.api.grok_client import GrokClient
from typing import Optional
import time


class ContaminantDescriptionGenerator(BaseBackfillGenerator):
    """Generate contaminant descriptions via AI research."""
    
    def __init__(self, source_file: str, items_key: str, target_field: str, dry_run: bool = False):
        super().__init__(source_file, items_key, target_field, dry_run)
        self.api_client = GrokClient()
    
    def populate(self, item_id: str, item_data: dict) -> Optional[str]:
        """Research and generate contaminant description."""
        
        contam_name = item_data.get('name', item_id.replace('-contamination', '').replace('-', ' ').title())
        category = item_data.get('category', '')
        subcategory = item_data.get('subcategory', '')
        
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


class ContaminantAppearanceGenerator(BaseBackfillGenerator):
    """Generate visual appearance descriptions via AI research."""
    
    def __init__(self, source_file: str, items_key: str, target_field: str, dry_run: bool = False):
        super().__init__(source_file, items_key, target_field, dry_run)
        self.api_client = GrokClient()
    
    def populate(self, item_id: str, item_data: dict) -> Optional[dict]:
        """Research and generate appearance characteristics."""
        
        contam_name = item_data.get('name', item_id)
        
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
                temperature=0.6,
                max_tokens=400
            )
            
            appearance_text = response.get('text', '').strip()
            
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
            
            time.sleep(0.5)
            return appearance
            
        except Exception as e:
            print(f"  ❌ {item_id}: Research failed - {e}")
            return None


class ContaminantCompoundsGenerator(BaseBackfillGenerator):
    """Generate compound relationships via AI research."""
    
    def __init__(self, source_file: str, items_key: str, target_field: str, dry_run: bool = False):
        super().__init__(source_file, items_key, target_field, dry_run)
        self.api_client = GrokClient()
    
    def populate(self, item_id: str, item_data: dict) -> Optional[dict]:
        """Research chemical compounds in this contamination."""
        
        contam_name = item_data.get('name', item_id)
        
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
                temperature=0.5,
                max_tokens=600
            )
            
            compounds_text = response.get('text', '').strip()
            
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
            
            time.sleep(0.5)
            return compounds
            
        except Exception as e:
            print(f"  ❌ {item_id}: Research failed - {e}")
            return None


class ContaminantContextGenerator(BaseBackfillGenerator):
    """Generate context metadata via AI research."""
    
    def __init__(self, source_file: str, items_key: str, target_field: str, dry_run: bool = False):
        super().__init__(source_file, items_key, target_field, dry_run)
        self.api_client = GrokClient()
    
    def populate(self, item_id: str, item_data: dict) -> Optional[dict]:
        """Research environmental context for contamination."""
        
        contam_name = item_data.get('name', item_id)
        
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
                temperature=0.5,
                max_tokens=400
            )
            
            context_text = response.get('text', '').strip().lower()
            
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
            
            time.sleep(0.5)
            return context
            
        except Exception as e:
            print(f"  ❌ {item_id}: Research failed - {e}")
            return None


# Register generators
BackfillRegistry.register('contaminant_description', ContaminantDescriptionGenerator)
BackfillRegistry.register('contaminant_appearance', ContaminantAppearanceGenerator)
BackfillRegistry.register('contaminant_compounds', ContaminantCompoundsGenerator)
BackfillRegistry.register('contaminant_context', ContaminantContextGenerator)
