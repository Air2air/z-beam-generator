#!/usr/bin/env python3
"""
Unified Materials Content Generator

TEXT CONTENT GENERATOR for caption, FAQ, and subtitle generation ONLY.
Used by shared/commands/generation.py (--caption, --subtitle, --faq commands).

ARCHITECTURE:
- Wraps /processing/generator.py (DynamicGenerator) for backward compatibility
- All generation uses single robust generator with learning-based parameter adaptation
- Starts from /prompts/*.txt templates
- Uses processing/config.yaml as parameter baseline
- Parameters learn from Winston feedback across sessions

Usage:
    generator = UnifiedMaterialsGenerator(api_client)
    
    # Generate with dynamic processing
    generator.generate('Bronze', 'caption')   # Uses DynamicGenerator
    generator.generate('Bronze', 'subtitle')  # Uses DynamicGenerator
    generator.generate('Bronze', 'faq')       # Uses DynamicGenerator
"""

import logging
import random
from pathlib import Path
from typing import Dict, Optional

from materials.research.faq_topic_researcher import FAQTopicResearcher
from processing.generator import DynamicGenerator

logger = logging.getLogger(__name__)

# Paths
MATERIALS_DATA_PATH = Path("data/materials/Materials.yaml")
PROMPTS_DIR = Path("prompts")


class UnifiedMaterialsGenerator:
    """
    Unified generator for all materials content types.
    
    Wrapper around DynamicGenerator for backward compatibility.
    All generation uses single robust generator with parameter learning.
    
    Responsibilities:
    - Wrap DynamicGenerator for materials-specific workflow
    - Handle FAQ topic enhancement (optional)
    - Generate EEAT section (non-AI, random selection from regulatoryStandards)
    """
    
    def __init__(self, api_client):
        """
        Initialize unified generator.
        
        Args:
            api_client: API client for content generation (required)
        """
        if not api_client:
            raise ValueError("API client required for content generation")
        
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)
        
        # Initialize DynamicGenerator (single robust generator)
        self.generator = DynamicGenerator(api_client)
        
        self.logger.info("UnifiedMaterialsGenerator initialized (wraps DynamicGenerator)")
    
    def _load_materials_data(self) -> Dict:
        """Load Materials.yaml using centralized loader"""
        from data.materials import load_materials_data
        return load_materials_data()
    
    def generate_caption(self, material_name: str, material_data: Dict) -> Dict[str, str]:
        """Generate before/after microscopy captions using DynamicGenerator"""
        self.logger.info(f"📸 Generating caption for {material_name}")
        
        # Use DynamicGenerator
        result = self.generator.generate(material_name, 'caption')
        
        if not result['success']:
            raise ValueError(f"Caption generation failed: {result['reason']}")
        
        return result['content']
    
    def generate_faq(self, material_name: str, material_data: Dict, faq_count: int = None, enhance_topics: bool = True) -> list:
        """
        Generate FAQ questions and answers using DynamicGenerator.
        
        Args:
            material_name: Name of material
            material_data: Material data from Materials.yaml
            faq_count: Number of FAQ items to generate (2-8 if not specified)
            enhance_topics: Whether to enhance FAQ with topic keywords/statements
            
        Returns:
            List of FAQ dicts with question, answer, and optionally topic_keyword, topic_statement
        """
        if faq_count is None:
            faq_count = random.randint(2, 8)
        
        self.logger.info(f"❓ Generating {faq_count} FAQ items for {material_name}")
        
        # Use DynamicGenerator
        result = self.generator.generate(material_name, 'faq', faq_count=faq_count)
        
        if not result['success']:
            raise ValueError(f"FAQ generation failed: {result['reason']}")
        
        faq_list = result['content']
        
        # INLINE TOPIC ENHANCEMENT (before Materials.yaml write)
        if enhance_topics:
            try:
                self.logger.info("🔍 Enhancing FAQ topics inline...")
                topic_researcher = FAQTopicResearcher(self.api_client)
                faq_list = topic_researcher.enhance_faq_topics(material_name, faq_list)
                self.logger.info("   ✅ Topic enhancement complete")
            except Exception as e:
                self.logger.warning(f"   ⚠️  Topic enhancement failed: {e}")
                self.logger.warning("   Continuing with non-enhanced FAQ")
        
        return faq_list
    
    def generate_subtitle(self, material_name: str, material_data: Dict) -> str:
        """
        Generate subtitle using DynamicGenerator with parameter learning.
        """
        self.logger.info(f"📝 Generating subtitle for {material_name}")
        
        # Use DynamicGenerator
        result = self.generator.generate(material_name, 'subtitle')
        
        if not result['success']:
            raise ValueError(f"Subtitle generation failed: {result['reason']}")
        
        subtitle = result['content']
        word_count = len(subtitle.split())
        self.logger.info(f"   ✅ Generated: {subtitle[:80]}... ({word_count} words)")
        
        return subtitle
    
    def generate_eeat(self, material_name: str, material_data: Dict) -> Optional[Dict]:
        """
        Generate EEAT section from regulatoryStandards (pure Python, no AI).
        
        EEAT (Experience, Expertise, Authoritativeness, Trustworthiness):
        - reviewedBy: Fixed string "Z-Beam Quality Assurance Team"
        - citations: 1-3 random regulatoryStandards descriptions
        - isBasedOn: 1 random regulatoryStandard with name and url
        
        Args:
            material_name: Name of material
            material_data: Material data from Materials.yaml
            
        Returns:
            EEAT dict or None if no regulatoryStandards available
        """
        import tempfile
        import yaml
        
        self.logger.info(f"📊 Generating EEAT section for {material_name}")
        
        # Get regulatoryStandards
        regulatory_standards = material_data.get('regulatoryStandards', [])
        
        # Filter to dict entries only (skip any legacy string entries)
        dict_standards = [
            std for std in regulatory_standards 
            if isinstance(std, dict) and 'description' in std and 'url' in std
        ]
        
        if not dict_standards:
            self.logger.warning(f"No valid regulatoryStandards found for {material_name}")
            return None
        
        # Select 1-3 random standards for citations
        num_citations = random.randint(1, min(3, len(dict_standards)))
        citation_standards = random.sample(dict_standards, num_citations)
        
        # Convert to citation strings (just the description)
        citations = [std['description'] for std in citation_standards]
        
        # Select 1 random standard for isBasedOn
        based_on_standard = random.choice(dict_standards)
        is_based_on = {
            'name': based_on_standard['description'],
            'url': based_on_standard['url']
        }
        
        eeat_data = {
            'reviewedBy': 'Z-Beam Quality Assurance Team',
            'citations': citations,
            'isBasedOn': is_based_on
        }
        
        self.logger.info(f"   reviewedBy: {eeat_data['reviewedBy']}")
        self.logger.info(f"   citations: {num_citations} selected from {len(dict_standards)} standards")
        self.logger.info(f"   isBasedOn: {is_based_on['name'][:60]}...")
        
        # Write to Materials.yaml (EEAT doesn't use DynamicGenerator)
        materials_data = self._load_materials_data()
        materials_data['materials'][material_name]['eeat'] = eeat_data
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            dir=MATERIALS_DATA_PATH.parent,
            delete=False,
            suffix='.yaml'
        ) as temp_f:
            yaml.dump(materials_data, temp_f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            temp_path = temp_f.name
        
        Path(temp_path).replace(MATERIALS_DATA_PATH)
        self.logger.info(f"✅ eeat written to Materials.yaml → materials.{material_name}.eeat")
        
        return eeat_data
    
    def generate(self, material_name: str, content_type: str, **kwargs):
        """
        Generate content for material.
        
        Args:
            material_name: Name of material
            content_type: Type of content ('caption', 'faq', 'subtitle', 'eeat')
            **kwargs: Additional parameters (e.g., faq_count=8)
            
        Returns:
            Generated content (dict for caption/faq/eeat, str for subtitle)
        """
        # Load material data
        materials_data = self._load_materials_data()
        
        if material_name not in materials_data['materials']:
            raise ValueError(f"Material '{material_name}' not found in Materials.yaml")
        
        material_data = materials_data['materials'][material_name]
        
        # Generate based on type
        if content_type == 'caption':
            return self.generate_caption(material_name, material_data)
        elif content_type == 'faq':
            return self.generate_faq(material_name, material_data, **kwargs)
        elif content_type == 'subtitle':
            return self.generate_subtitle(material_name, material_data)
        elif content_type == 'eeat':
            return self.generate_eeat(material_name, material_data)
        else:
            raise ValueError(f"Unknown content type: {content_type}")
        
        # Note: DynamicGenerator already writes to Materials.yaml
        # No need for separate _write_to_materials_yaml call
