"""
Material Data Enrichment

Fetches real-world facts about materials to ground AI generation in reality.
Reduces generic, AI-like descriptions by injecting specific, verifiable data.
"""

import logging
from typing import Dict, Optional
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)


class DataEnricher:
    """
    Enriches material context with real data from Materials.yaml.
    
    Uses existing material database instead of web search to ensure
    accuracy and avoid external API dependencies.
    """
    
    def __init__(self, materials_path: Optional[Path] = None):
        """
        Initialize enricher.
        
        Args:
            materials_path: Path to Materials.yaml (default: data/materials/Materials.yaml)
        """
        if materials_path is None:
            materials_path = Path(__file__).parent.parent.parent / "data" / "materials" / "Materials.yaml"
        
        self.materials_path = Path(materials_path)
        self._materials = None
    
    def _load_materials(self):
        """Lazy load materials database"""
        if self._materials is None:
            try:
                with open(self.materials_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    self._materials = data.get('materials', {})
                    logger.info(f"Loaded {len(self._materials)} materials")
            except Exception as e:
                logger.error(f"Failed to load materials: {e}")
                self._materials = {}
    
    def fetch_real_facts(self, material: str) -> Dict[str, any]:
        """
        Fetch real facts about material from database.
        
        Args:
            material: Material name
            
        Returns:
            Dict with properties, applications, machine settings, etc.
        """
        self._load_materials()
        
        material_data = self._materials.get(material, {})
        
        if not material_data:
            logger.warning(f"No data found for material: {material}")
            return {}
        
        # Extract key facts
        facts = {
            'category': material_data.get('category', ''),
            'subcategory': material_data.get('subcategory', ''),
            'properties': {},
            'applications': material_data.get('applications', ''),
            'machine_settings': {},
            'key_challenges': ''
        }
        
        # Extract property values from nested structure
        material_props = material_data.get('materialProperties', {})
        material_chars = material_props.get('material_characteristics', {})
        for prop_name, prop_data in material_chars.items():
            if isinstance(prop_data, dict) and 'value' in prop_data:
                value = prop_data.get('value')
                unit = prop_data.get('unit', '')
                if value is not None:
                    facts['properties'][prop_name] = f"{value} {unit}".strip()
        
        # Extract machine settings from nested structure
        settings_section = material_data.get('machineSettings', {})
        laser_settings = settings_section.get('laser_settings', {})
        settings = laser_settings if laser_settings else settings_section
        for setting_name, setting_data in settings.items():
            if isinstance(setting_data, dict):
                value = setting_data.get('value')
                unit = setting_data.get('unit', '')
                if value:
                    facts['machine_settings'][setting_name] = f"{value} {unit}".strip()
        
        logger.info(f"Enriched {material} with {len(facts['properties'])} properties, {len(facts['machine_settings'])} settings")
        
        return facts
    
    def format_facts_for_prompt(self, facts: Dict, enrichment_params: Optional[Dict] = None, technical_intensity: int = 50, voice_params: Optional[Dict] = None) -> str:
        """
        Format facts as prompt-friendly string with density and style controlled by enrichment_params.
        
        Args:
            facts: Facts dict from fetch_real_facts()
            enrichment_params: Dict from DynamicConfig.calculate_enrichment_params() with:
                - technical_intensity: 0-100 (spec density)
                - context_detail_level: 0-100 (description verbosity)
                - fact_formatting_style: 'formal'|'balanced'|'conversational'
                - engagement_level: 0-100 (informal language)
            technical_intensity: Backward compatibility (used if enrichment_params is None)
            voice_params: Dict from DynamicConfig.calculate_voice_parameters() with:
                - jargon_removal: 0.0-1.0 (high = remove jargon)
            
        Returns:
            Formatted string for injection into prompts
        """
        # Phase 3A: Extract params from enrichment_params or fall back to technical_intensity
        if enrichment_params:
            tech_intensity = enrichment_params.get('technical_intensity', 2)  # 1-3
            context_detail = enrichment_params.get('context_detail_level', 2)  # 1-3
            fact_style = enrichment_params.get('fact_formatting_style', 'balanced')
            engagement = enrichment_params.get('engagement_level', 2)  # 1-3
        else:
            # Backward compatibility
            tech_intensity = technical_intensity
            context_detail = 2  # 1-3 scale
            fact_style = 'balanced'
            engagement = 2  # 1-3 scale
        lines = []
        
        # Always include category with context detail
        if facts.get('category'):
            category_line = f"Category: {facts['category']}"
            # Add subcategory based on context_detail_level
            if context_detail >= 2 and facts.get('subcategory'):
                category_line += f" ({facts['subcategory']})"
            lines.append(category_line)
        
        # Check jargon_removal level - if high, exclude ALL technical specs
        jargon_removal = voice_params.get('jargon_removal', 0.5) if voice_params else 0.5
        if jargon_removal > 0.7:
            # High jargon removal: NO technical specs at all
            logger.info(f"High jargon removal ({jargon_removal:.3f}) - excluding all technical specs")
            max_props = 0
            max_settings = 0
            include_apps = True  # Applications are usually plain language
        else:
            # Calculate how many specs to include based on technical_intensity (1-3 scale)
            if tech_intensity == 1:
                # Level 1: Conceptual only, NO technical specs
                max_props = 0
                max_settings = 0
                include_apps = False
            elif tech_intensity == 2:
                # Level 2: Minimal specs - 1-2 key properties
                max_props = 2
                max_settings = 1
                include_apps = False
            else:  # tech_intensity == 3
                # Level 3: Full technical detail
                max_props = 5
                max_settings = 3
                include_apps = True
        
        if facts.get('properties') and max_props > 0:
            lines.append("Properties:")
            for prop, value in list(facts['properties'].items())[:max_props]:
                # Phase 3A: Format value based on fact_formatting_style
                formatted_value = self._format_fact_value(value, fact_style, engagement)
                lines.append(f"  - {prop}: {formatted_value}")
        
        if facts.get('machine_settings') and max_settings > 0:
            lines.append("Laser cleaning settings:")
            for setting, value in list(facts['machine_settings'].items())[:max_settings]:
                lines.append(f"  - {setting}: {value}")
        
        if include_apps and facts.get('applications'):
            # Truncate based on context_detail_level (1-3)
            if context_detail == 1:
                max_chars = 100  # Brief
            elif context_detail == 2:
                max_chars = 200  # Moderate
            else:  # context_detail == 3
                max_chars = 300  # Full
            lines.append(f"Applications: {facts['applications'][:max_chars]}")
        
        return "\n".join(lines)
    
    def _format_fact_value(self, value: str, style: str, engagement: int) -> str:
        """
        Format fact value based on style preference.
        
        Args:
            value: Original value (e.g., "2.7 g/cm³")
            style: 'formal', 'balanced', or 'conversational'
            engagement: 1-3 engagement level
            
        Returns:
            Formatted value string
        """
        if style == 'formal':
            return value
        elif style == 'balanced':
            # Add "roughly" or "approximately" for numeric values
            if any(char.isdigit() for char in value):
                return f"roughly {value}"
            return value
        else:  # conversational
            # Add "around" and contextual comment for high engagement
            if any(char.isdigit() for char in value):
                base = f"around {value}"
                # Add contextual comments for high engagement
                if engagement > 60:
                    # Add casual parenthetical based on property type
                    if 'g/cm³' in value or 'kg/m³' in value:
                        return f"{base} (pretty dense!)"
                    elif 'W/m' in value or 'thermal' in value.lower():
                        return f"{base} (good conductor)"
                    elif 'GPa' in value or 'MPa' in value:
                        return f"{base} (quite strong)"
                return base
            return value
