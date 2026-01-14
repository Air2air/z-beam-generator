"""
Material Data Enrichment

Fetches real-world facts about materials to ground AI generation in reality.
Reduces generic, AI-like descriptions by injecting specific, verifiable data.
"""

import logging
import random
from pathlib import Path
from typing import Dict, Optional

from shared.utils.file_io import read_yaml_file

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
        self._schema_cache = None  # Cache for section_display_schema.yaml
    
    def _load_materials(self):
        """Lazy load materials database"""
        if self._materials is None:
            try:
                data = read_yaml_file(self.materials_path)
                self._materials = data.get('materials', {})
                logger.info(f"Loaded {len(self._materials)} materials")
            except Exception as e:
                logger.error(f"Failed to load materials: {e}")
                self._materials = {}
    
    def _load_schema(self):
        """Lazy load section display schema"""
        if self._schema_cache is None:
            try:
                schema_path = Path(__file__).parent.parent.parent / "data" / "schemas" / "section_display_schema.yaml"
                self._schema_cache = read_yaml_file(schema_path)
                logger.debug(f"Loaded section display schema")
            except Exception as e:
                logger.error(f"Failed to load schema: {e}")
                self._schema_cache = {}
    
    def get_structural_pattern(self, component_type: str) -> Optional[str]:
        """
        Select a random structural pattern for the given component type.
        
        Provides variety in opening structures to prevent repetitive "Property X, Y, and Z..." patterns.
        Uses weighted random selection based on pattern weights in schema.
        
        Args:
            component_type: Component type (e.g., 'materialCharacteristics_description')
            
        Returns:
            Structural pattern instruction string, or None if no patterns defined
        """
        self._load_schema()
        
        # Get property pool for this component type
        property_pools = self._schema_cache.get('property_pools', {})
        pool_config = property_pools.get(component_type, {})
        patterns = pool_config.get('structural_patterns', [])
        
        if not patterns:
            logger.debug(f"No structural patterns defined for {component_type}")
            return None
        
        # Weighted random selection
        weights = [p.get('weight', 10) for p in patterns]
        selected = random.choices(patterns, weights=weights, k=1)[0]
        
        logger.info(f"Selected structural pattern '{selected['id']}' for {component_type}")
        return selected['instruction']
    
    def fetch_real_facts(self, material: str, component_type: str = None) -> Dict[str, any]:
        """
        Fetch real facts about material from database.
        
        READS pre-populated distinctive properties from source data.
        DOES NOT calculate them on-the-fly (Core Principle 0.6 compliance).
        
        Args:
            material: Material name
            component_type: Component type for section-specific property reading (optional)
            
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
            'distinctive_properties': [],  # Read from source data, not calculated
            'applications': material_data.get('applications', ''),
            'machine_settings': {},
            'key_challenges': '',
            'structural_pattern': None  # Structural variety instruction
        }
        
        # Select structural pattern for variety (if component_type provided)
        if component_type:
            facts['structural_pattern'] = self.get_structural_pattern(component_type)
        
        # Extract property values from nested structure
        material_props = material_data.get('properties', {})
        material_chars = material_props.get('materialCharacteristics', {})
        for prop_name, prop_data in material_chars.items():
            if isinstance(prop_data, dict) and 'value' in prop_data:
                value = prop_data.get('value')
                unit = prop_data.get('unit', '')
                if value is not None:
                    facts['properties'][prop_name] = f"{value} {unit}".strip()
        
        # READ pre-populated distinctive properties from source data (if available)
        # These should be written by backfill/research scripts, NOT calculated here
        if component_type:
            # Check for section-specific distinctive properties in source data
            section_key = f"_distinctive_{component_type}"
            if section_key in material_data:
                facts['distinctive_properties'] = material_data[section_key]
                logger.info(f"Read {len(facts['distinctive_properties'])} pre-populated distinctive properties for {material}.{component_type}")
            else:
                logger.debug(f"No pre-populated distinctive properties found for {material}.{component_type} (run backfill to populate)")
        
        # Extract machine settings from nested structure
        settings_section = material_data.get('machine_settings', {})
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
            tech_intensity = enrichment_params.get('technical_intensity', 0.22)  # 0.0-1.0 normalized
            context_detail = enrichment_params.get('context_detail_level', 0.22)  # 0.0-1.0 normalized
            fact_style = enrichment_params.get('fact_formatting_style', 'balanced')
            engagement = enrichment_params.get('engagement_level', 0.22)  # 0.0-1.0 normalized
        else:
            # Backward compatibility
            tech_intensity = technical_intensity
            context_detail = 0.22  # 0.0-1.0 normalized (slider 3 on 1-10 scale)
            fact_style = 'balanced'
            engagement = 0.22  # 0.0-1.0 normalized (slider 3 on 1-10 scale)
        lines = []
        
        # NEW: Include structural pattern instruction first (drives opening variety)
        if facts.get('structural_pattern'):
            lines.append("STRUCTURAL APPROACH:")
            lines.append(f"  {facts['structural_pattern']}")
            lines.append("")  # Blank line for separation
        
        # Always include category with context detail
        if facts.get('category'):
            category_line = f"Category: {facts['category']}"
            # Add subcategory based on context_detail_level
            if context_detail >= 2 and facts.get('subcategory'):
                category_line += f" ({facts['subcategory']})"
            lines.append(category_line)
        
        # NEW: Include distinctive properties first (most important for variation)
        if facts.get('distinctive_properties'):
            lines.append("\nDISTINCTIVE PROPERTIES (most unique to this material):")
            for prop in facts['distinctive_properties']:
                name_display = prop['name'].replace('_', ' ').title()
                value_str = f"{prop['value']} {prop['unit']}".strip()
                
                # Add comparison if highly distinctive (z-score > 1.5)
                if prop.get('distinctiveness_score', 0) > 1.5:
                    comparison = 'significantly higher' if float(prop['value']) > prop.get('category_mean', 0) else 'significantly lower'
                    lines.append(f"  • {name_display}: {value_str} ({comparison} than category average)")
                else:
                    lines.append(f"  • {name_display}: {value_str}")
        
        # Check jargon_removal level - if high, exclude ALL technical specs
        jargon_removal = voice_params.get('jargon_removal', 0.5) if voice_params else 0.5
        if jargon_removal > 0.7:
            # High jargon removal: NO technical specs at all
            logger.info(f"High jargon removal ({jargon_removal:.3f}) - excluding all technical specs")
            max_props = 0
            max_settings = 0
            include_apps = True  # Applications are usually plain language
        else:
            # Calculate how many specs to include based on technical_intensity (0.0-1.0 normalized)
            # Linear mapping: 0.0 (slider 1) → 0 specs, 0.5 (slider 5-6) → 2-3 specs, 1.0 (slider 10) → 5 specs
            if tech_intensity < 0.15:  # Very low (slider 1-2)
                # Conceptual only, NO technical specs
                max_props = 0
                max_settings = 0
                include_apps = False
            elif tech_intensity < 0.50:  # Low to moderate (slider 3-5)
                # Minimal specs - 1-2 key properties
                max_props = 2
                max_settings = 1
                include_apps = False
            else:  # tech_intensity >= 0.50 (slider 6-10)
                # Full technical detail
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
            # Truncate based on context_detail_level (0.0-1.0 normalized)
            # Linear mapping: 0.0 → 100 chars, 0.5 → 200 chars, 1.0 → 300 chars
            if context_detail < 0.30:  # Low (slider 1-3)
                max_chars = 100  # Brief
            elif context_detail < 0.70:  # Moderate (slider 4-7)
                max_chars = 200  # Moderate
            else:  # context_detail >= 0.70 (slider 8-10)
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
