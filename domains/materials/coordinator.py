#!/usr/bin/env python3
"""
Unified Materials Content Generator

TEXT CONTENT GENERATOR for all material content (micro, FAQ, description).
Used by shared/commands/generation.py for all generation commands.

ARCHITECTURE (Updated December 2025 - Production Only):
Single-pass generation with quality logging for learning.

- Fast single-pass generation (~5-7 seconds)
- No quality gates blocking content
- Direct API call via Generator
- Cost: ~$0.015 per description
- Quality scores logged for learning improvement

Usage:
    generator = UnifiedMaterialsGenerator(api_client)
    generator.generate('Bronze', 'micro')
"""

import logging
import random
from pathlib import Path
from typing import Dict, Optional

from generation.core.evaluated_generator import QualityEvaluatedGenerator
from postprocessing.evaluation.subjective_evaluator import SubjectiveEvaluator
from shared.research.faq_topic_researcher import FAQTopicResearcher

logger = logging.getLogger(__name__)

# Paths
MATERIALS_DATA_PATH = Path("data/materials/Materials.yaml")
PROMPTS_DIR = Path("prompts")


class UnifiedMaterialsGenerator:
    """
    Unified generator for all materials content types.
    
    Single-pass production generation with quality logging for learning.
    
    Responsibilities:
    - Generate content via Generator (single-pass)
    - Handle FAQ topic enhancement (optional)
    - Generate EEAT section (non-AI, random selection from regulatory_standards)
    - Save to Materials.yaml
    """
    
    def __init__(self, api_client):
        """
        Initialize unified generator with learning pipeline.
        
        Args:
            api_client: API client for content generation (required)
        """
        if not api_client:
            raise ValueError("API client required for content generation")
        
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)
        
        # Initialize SubjectiveEvaluator for quality learning
        self.subjective_evaluator = SubjectiveEvaluator(api_client)
        
        # Initialize Winston client (optional - graceful degradation if not configured)
        try:
            from postprocessing.detection.winston_client import WinstonClient
            self.winston_client = WinstonClient()
            self.logger.info("✅ Winston client initialized")
        except Exception as e:
            self.winston_client = None
            self.logger.warning(f"⚠️  Winston not configured (will continue without AI detection): {e}")
        
        # Initialize QualityEvaluatedGenerator with learning components
        self.generator = QualityEvaluatedGenerator(
            api_client=api_client,
            subjective_evaluator=self.subjective_evaluator,
            winston_client=self.winston_client
        )
        
        self.logger.info("🚀 UnifiedMaterialsGenerator initialized with learning pipeline")
    
    def _load_materials_data(self) -> Dict:
        """Load Materials.yaml using centralized loader"""
        from domains.materials.data_loader_v2 import load_materials_data
        return load_materials_data()
    
    def generate_eeat(self, material_name: str, material_data: Dict) -> Optional[Dict]:
        """
        Generate EEAT section from regulatory_standards (pure Python, no AI).
        
        EEAT (Experience, Expertise, Authoritativeness, Trustworthiness):
        - reviewedBy: Fixed string "Z-Beam Quality Assurance Team"
        - citations: 1-3 random regulatory_standards descriptions
        - isBasedOn: 1 random regulatoryStandard with name and url
        
        Args:
            material_name: Name of material
            material_data: Material data from Materials.yaml
            
        Returns:
            EEAT dict or None if no regulatory_standards available
        """
        import tempfile

        import yaml
        
        self.logger.info(f"📊 Generating EEAT section for {material_name}")
        
        # Get regulatory_standards
        regulatory_standards = material_data.get('regulatory_standards', [])
        
        # Filter to dict entries only (skip any legacy string entries)
        dict_standards = [
            std for std in regulatory_standards 
            if isinstance(std, dict) and 'description' in std and 'url' in std
        ]
        
        if not dict_standards:
            self.logger.warning(f"No valid regulatory_standards found for {material_name}")
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
        Generate content for material with learning pipeline.
        
        Single-pass generation via QualityEvaluatedGenerator:
        - Generate content
        - Save to Materials.yaml
        - Evaluate quality (Winston + Subjective + Structural)
        - Log to winston_feedback.db for learning
        
        Args:
            material_name: Name of material
            content_type: Type of content ('micro', 'faq', 'description', 'eeat')
            **kwargs: Additional parameters (e.g., faq_count=8)
            
        Returns:
            Generated content (string for micro/description, list for faq)
        """
        # Handle EEAT separately (pure Python, no AI)
        if content_type == 'eeat':
            materials_data = self._load_materials_data()
            if material_name not in materials_data['materials']:
                raise ValueError(f"Material '{material_name}' not found in Materials.yaml")
            return self.generate_eeat(material_name, materials_data['materials'][material_name])
        
        # All other types use QualityEvaluatedGenerator with learning pipeline
        result = self.generator.generate(material_name, content_type, **kwargs)
        
        # QualityEvaluatedGenerator returns dict with 'content' key
        return result
