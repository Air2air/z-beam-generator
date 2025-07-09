#!/usr/bin/env python3
"""
Content Generator - Generates text sections and metadata
"""
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ContentGenerator:
    """Generates text sections and metadata"""
    
    def __init__(self, config, api_client):
        self.config = config
        self.api_client = api_client
        
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
        """Generate metadata"""
        logger.info("📊 GENERATING METADATA")
        
        # Load metadata prompt
        metadata_prompt = self._load_metadata_prompt(material, author_id, article_type)
        
        # Generate via API
        response = self.api_client.call(metadata_prompt, "metadata")
        
        # Parse JSON response - FAIL FAST if invalid
        try:
            # Handle xaiArtifact wrapper
            if '<xaiArtifact' in response:
                start = response.find('>')
                end = response.rfind('</xaiArtifact>')
                if start != -1 and end != -1:
                    response = response[start+1:end].strip()
                    logger.info("📊 Extracted JSON from xaiArtifact wrapper")
            
            # Handle code blocks
            if response.startswith('```json'):
                response = response[7:-3]
            elif response.startswith('```'):
                response = response[3:-3]
            
            metadata = json.loads(response)
            logger.info(f"✅ Metadata parsed - Keys: {list(metadata.keys())}")
            return metadata
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse metadata JSON: {e}")
            logger.error(f"❌ Raw response: {response}")
            raise ValueError(f"Failed to parse metadata JSON: {e}")
    
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
    
    def _load_metadata_prompt(self, material, author_id, article_type):
        """Load metadata prompt - FAIL FAST if missing"""
        prompt_file = Path(self.config["prompts_dir"]) / "metadata" / "metadata.md"
        
        if not prompt_file.exists():
            raise FileNotFoundError(f"Metadata prompt not found: {prompt_file}")
        
        template = prompt_file.read_text()
        
        # Replace template variables
        prompt = template.replace("{{materialType}}", material)
        prompt = prompt.replace("{{authorId}}", str(author_id))
        prompt = prompt.replace("{{articleType}}", article_type)
        
        return prompt