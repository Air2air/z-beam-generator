#!/usr/bin/env python3
"""
Content Generator - Generates text sections only (metadata moved to MetadataGenerator)
"""
import json
import logging
from pathlib import Path
from metadata.metadata_generator import MetadataGenerator

logger = logging.getLogger(__name__)

class ContentGenerator:
    """Generates text sections and metadata"""
    
    def __init__(self, config, api_client):
        self.config = config
        self.api_client = api_client
        self.metadata_generator = MetadataGenerator(config, api_client)
        
        # Extract word limits from config - NO HARDCODED DEFAULTS
        self.max_section_words = config["max_section_words"]
        self.target_section_words = config["target_section_words"]
        self.max_total_words = config["max_total_words"]
    
    def generate_text_sections(self, material, article_type):
        """Generate text sections from config"""
        logger.info("📚 Loading sections configuration...")
        sections_config = self._load_sections_config()
        logger.info(f"📚 Found {len(sections_config)} sections to generate")
        
        generated_sections = []
        
        for i, section in enumerate(sections_config, 1):
            logger.info(f"📄 [{i}/{len(sections_config)}] GENERATING SECTION: {section['name']}")
            
            # Load section prompt from JSON and add word limit
            prompt = self._load_section_prompt(section, material)
            
            # Add word limit instruction to prompt
            word_limit_instruction = f"\n\nCRITICAL: This section must be EXACTLY {self.max_section_words} words or less. Count every word carefully. Be direct and technical."
            full_prompt = prompt + word_limit_instruction
            
            # Generate via API
            content = self.api_client.call(full_prompt, f"section-{section['name']}")
            
            generated_sections.append({
                'name': section['name'],
                'title': section['title'],
                'content': content
            })
            
            logger.info(f"✅ Section '{section['name']}' generated - {len(content)} chars")
        
        return generated_sections
    
    def generate_metadata(self, material, author_id, article_type):
        """Generate metadata using new modular MetadataGenerator"""
        logger.info("📊 GENERATING METADATA")
        return self.metadata_generator.generate_metadata(material, author_id, article_type)
    
    def load_author_data(self, author_id):
        """Load author data - FAIL FAST if missing"""
        authors_file = Path(self.config["authors_file"])
        logger.info(f"👤 Loading author data from: {authors_file}")
        
        if not authors_file.exists():
            raise FileNotFoundError(f"Authors file not found: {authors_file}")
        
        with open(authors_file, 'r') as f:
            authors = json.load(f)
        
        author = next((a for a in authors if a["id"] == author_id), None)
        if not author:
            raise ValueError(f"Author ID {author_id} not found")
        
        logger.info(f"✅ Author loaded: {author.get('name', 'Unknown')}")
        return author
    
    def _load_sections_config(self):
        """Load sections config - FAIL FAST if missing"""
        sections_file = Path(self.config["sections_file"])
        
        if not sections_file.exists():
            raise FileNotFoundError(f"Sections file not found: {sections_file}")
        
        with open(sections_file, 'r') as f:
            data = json.load(f)
        
        # Handle the "sections" wrapper
        return data.get("sections", data)
    
    def _load_section_prompt(self, section, material):
        """Load section prompt from JSON config"""
        if "prompt" not in section:
            raise ValueError(f"Section '{section['name']}' missing prompt field")
        
        # Format the prompt template with the material
        return section["prompt"].format(material=material)