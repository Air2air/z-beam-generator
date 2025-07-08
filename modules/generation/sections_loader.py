#!/usr/bin/env python3
"""
Sections Loader - Handles loading section configurations
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class SectionsLoader:
    """Loads section configurations from sections.json"""
    
    def __init__(self, config):
        self.config = config
        self.prompts_directory = Path(config.get('prompts_directory', "prompts"))
    
    def load_sections(self):
        """Load section configurations from sections.json"""
        sections_file = self.prompts_directory / "sections.json"
        
        if not sections_file.exists():
            raise FileNotFoundError(f"Sections file not found: {sections_file}")
        
        with open(sections_file, 'r', encoding='utf-8') as f:
            sections_data = json.load(f)
        
        sections = sections_data.get('sections', [])
        logger.info(f"📋 Loaded {len(sections)} sections from {sections_file}")
        
        return sections
    
    def get_material_sections(self, sections, material):
        """Filter sections for specific material"""
        material_sections = [s for s in sections if material in s.get('materials', [material])]
        
        if not material_sections:
            logger.warning(f"⚠️ No sections found for material: {material}, using all sections")
            material_sections = sections
        
        logger.info(f"📋 Loaded {len(material_sections)} sections for material: {material}")
        return sorted(material_sections, key=lambda x: x.get('order', 999))