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
            materials_path: Path to Materials.yaml (default: materials/data/Materials.yaml)
        """
        if materials_path is None:
            materials_path = Path(__file__).parent.parent.parent / "materials" / "data" / "Materials.yaml"
        
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
        
        # Extract property values
        properties = material_data.get('properties', {})
        for prop_name, prop_data in properties.items():
            if isinstance(prop_data, dict):
                value = prop_data.get('value')
                unit = prop_data.get('unit', '')
                if value:
                    facts['properties'][prop_name] = f"{value} {unit}".strip()
        
        # Extract machine settings
        settings = material_data.get('machineSettings', {})
        for setting_name, setting_data in settings.items():
            if isinstance(setting_data, dict):
                value = setting_data.get('value')
                unit = setting_data.get('unit', '')
                if value:
                    facts['machine_settings'][setting_name] = f"{value} {unit}".strip()
        
        logger.info(f"Enriched {material} with {len(facts['properties'])} properties, {len(facts['machine_settings'])} settings")
        
        return facts
    
    def format_facts_for_prompt(self, facts: Dict) -> str:
        """
        Format facts as prompt-friendly string.
        
        Args:
            facts: Facts dict from fetch_real_facts()
            
        Returns:
            Formatted string for injection into prompts
        """
        lines = []
        
        if facts.get('category'):
            lines.append(f"Category: {facts['category']}")
        
        if facts.get('properties'):
            lines.append("Properties:")
            for prop, value in list(facts['properties'].items())[:5]:  # Top 5
                lines.append(f"  - {prop}: {value}")
        
        if facts.get('machine_settings'):
            lines.append("Laser cleaning settings:")
            for setting, value in list(facts['machine_settings'].items())[:3]:  # Top 3
                lines.append(f"  - {setting}: {value}")
        
        if facts.get('applications'):
            lines.append(f"Applications: {facts['applications'][:200]}")  # Truncate
        
        return "\n".join(lines)
