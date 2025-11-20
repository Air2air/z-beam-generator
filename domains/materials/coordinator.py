#!/usr/bin/env python3
"""
Unified Materials Content Generator

TEXT CONTENT GENERATOR for caption, FAQ, and subtitle generation ONLY.
Used by shared/commands/generation.py (--caption, --subtitle, --faq commands).

ARCHITECTURE (Updated November 20, 2025):
- Wraps /generation/core/quality_gated_generator.py for quality-enforced generation
- Evaluates content BEFORE save using SubjectiveEvaluator
- Retries up to 5 times with parameter adjustments if quality fails
- Only saves content meeting 7.0/10 realism threshold
- Starts from /prompts/*.txt templates
- Uses generation/config.yaml for target lengths and global variation

Quality Gates (ALL must pass):
- Subjective Realism: 7.0/10 minimum
- Voice Authenticity: 7.0/10 minimum  
- Tonal Consistency: 7.0/10 minimum
- AI Tendencies: Zero detected patterns

Usage:
    generator = UnifiedMaterialsGenerator(api_client)
    
    # Generate with quality-gated approach (auto-retry until quality passes)
    generator.generate('Bronze', 'caption')   # Uses QualityGatedGenerator
    generator.generate('Bronze', 'subtitle')  # Uses QualityGatedGenerator
    generator.generate('Bronze', 'faq')       # Uses QualityGatedGenerator
"""

import logging
import random
from pathlib import Path
from typing import Dict, Optional

from domains.materials.research.faq_topic_researcher import FAQTopicResearcher
from generation.core.quality_gated_generator import QualityGatedGenerator

logger = logging.getLogger(__name__)

# Paths
MATERIALS_DATA_PATH = Path("data/materials/Materials.yaml")
PROMPTS_DIR = Path("prompts")


class UnifiedMaterialsGenerator:
    """
    Unified generator for all materials content types.
    
    Wrapper around QualityGatedGenerator for quality-enforced generation.
    Evaluates content BEFORE save, retries with parameter adjustments if needed.
    Only saves content that passes quality thresholds.
    
    Responsibilities:
    - Wrap QualityGatedGenerator for materials-specific workflow
    - Handle FAQ topic enhancement (optional)
    - Generate EEAT section (non-AI, random selection from regulatoryStandards)
    - Ensure only high-quality content persists in Materials.yaml
    """
    
    def __init__(self, api_client):
        """
        Initialize unified generator with quality gate enforcement.
        
        Args:
            api_client: API client for content generation (required)
        """
        if not api_client:
            raise ValueError("API client required for content generation")
        
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)
        
        # Load config for quality gate settings
        from generation.config.config_loader import get_config
        config = get_config()
        quality_gate_config = config.config.get('quality_gates', {})
        evaluation_config = config.config.get('evaluation', {})
        
        # Get evaluation API client based on config (respects evaluation.model setting)
        from shared.api.client_factory import create_api_client
        
        # Fail-fast if evaluation config missing
        if 'model' not in evaluation_config:
            raise ValueError("evaluation.model missing in config.yaml - fail-fast architecture")
        
        evaluation_model = evaluation_config['model']
        # Extract provider from model name (e.g., "grok-beta" -> "grok")
        evaluation_provider = evaluation_model.split('-')[0]
        evaluation_client = create_api_client(evaluation_provider)
        self.logger.info(f"Using {evaluation_provider} API for subjective evaluation")
        
        # Initialize SubjectiveEvaluator for quality gate
        from postprocessing.evaluation.subjective_evaluator import SubjectiveEvaluator
        
        # Fail-fast if quality gate config missing
        if 'realism_threshold' not in quality_gate_config:
            raise ValueError("quality_gates.realism_threshold missing in config.yaml - fail-fast architecture")
        if 'verbose' not in evaluation_config:
            raise ValueError("evaluation.verbose missing in config.yaml - fail-fast architecture")
        if 'temperature' not in evaluation_config:
            raise ValueError("evaluation.temperature missing in config.yaml - fail-fast architecture")
        if 'max_retry_attempts' not in quality_gate_config:
            raise ValueError("quality_gates.max_retry_attempts missing in config.yaml - fail-fast architecture")
        
        self.subjective_evaluator = SubjectiveEvaluator(
            api_client=evaluation_client,  # Use evaluation-specific client
            quality_threshold=quality_gate_config['realism_threshold'],
            verbose=evaluation_config['verbose'],
            evaluation_temperature=evaluation_config['temperature']
        )
        
        # Initialize QualityGatedGenerator (evaluate before save, retry on fail)
        self.generator = QualityGatedGenerator(
            api_client=api_client,
            subjective_evaluator=self.subjective_evaluator,
            max_attempts=quality_gate_config['max_retry_attempts'],
            quality_threshold=quality_gate_config['realism_threshold']
        )
        
        self.logger.info("UnifiedMaterialsGenerator initialized (quality-gated generation with auto-retry)")
    
    def _load_materials_data(self) -> Dict:
        """Load Materials.yaml using centralized loader"""
        from data.materials import load_materials_data
        return load_materials_data()
    
    def generate_caption(self, material_name: str, material_data: Dict) -> Dict:
        """
        Generate before/after microscopy captions using QualityGatedGenerator.
        
        Quality-gated: Evaluates BEFORE save, retries if < 7.0/10 realism.
        
        Returns:
            Dict with 'before' and 'after' keys (caption content)
        """
        self.logger.info(f"📸 Generating caption for {material_name}")
        
        # Use QualityGatedGenerator - evaluates before save, retries on fail
        result = self.generator.generate(material_name, 'caption')
        
        if not result.success:
            raise ValueError(
                f"Caption generation failed after {result.attempts} attempts. "
                f"Final score: {result.final_score or 'N/A'}/10. "
                f"Reasons: {'; '.join(result.rejection_reasons)}"
            )
        
        # Return content (already in before/after format)
        return result.content
    
    def generate_faq(self, material_name: str, material_data: Dict, faq_count: int = None, enhance_topics: bool = True) -> list:
        """
        Generate FAQ questions and answers using QualityGatedGenerator.
        
        Quality-gated: Evaluates BEFORE save, retries if < 7.0/10 realism.
        
        Args:
            material_name: Name of material
            material_data: Material data from Materials.yaml
            faq_count: Number of FAQ items to generate (2-8 if not specified)
            enhance_topics: Whether to enhance FAQ with topic keywords/statements
            
        Returns:
            List of FAQ dicts with 'question' and 'answer' keys
        """
        if faq_count is None:
            faq_count = random.randint(2, 8)
        
        self.logger.info(f"❓ Generating {faq_count} FAQ items for {material_name}")
        
        # Use QualityGatedGenerator - evaluates before save, retries on fail
        result = self.generator.generate(material_name, 'faq', faq_count=faq_count)
        
        if not result.success:
            raise ValueError(
                f"FAQ generation failed after {result.attempts} attempts. "
                f"Final score: {result.final_score or 'N/A'}/10. "
                f"Reasons: {'; '.join(result.rejection_reasons)}"
            )
        
        faq_list = result.content
        
        # INLINE TOPIC ENHANCEMENT (after generation, before return)
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
        Generate subtitle using QualityGatedGenerator.
        
        Quality-gated: Evaluates BEFORE save, retries if < 7.0/10 realism.
        
        Returns:
            String (subtitle content)
        """
        self.logger.info(f"📝 Generating subtitle for {material_name}")
        
        # Use QualityGatedGenerator - evaluates before save, retries on fail
        result = self.generator.generate(material_name, 'subtitle')
        
        if not result.success:
            raise ValueError(
                f"Subtitle generation failed after {result.attempts} attempts. "
                f"Final score: {result.final_score or 'N/A'}/10. "
                f"Reasons: {'; '.join(result.rejection_reasons)}"
            )
        
        subtitle = result.content
        word_count = len(subtitle.split())
        self.logger.info(f"   ✅ Generated: {subtitle[:80]}... ({word_count} words)")
        
        # Return content string
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
        Generate content for material using single-pass approach.
        
        Args:
            material_name: Name of material
            content_type: Type of content ('caption', 'faq', 'subtitle', 'eeat')
            **kwargs: Additional parameters (e.g., faq_count=8)
            
        Returns:
            Generated content (string for caption/subtitle, list for faq, dict for eeat)
        """
        # Load material data
        materials_data = self._load_materials_data()
        
        if material_name not in materials_data['materials']:
            raise ValueError(f"Material '{material_name}' not found in Materials.yaml")
        
        material_data = materials_data['materials'][material_name]
        
        # Generate based on type
        # SimpleGenerator returns content directly (no result wrapper)
        if content_type == 'caption':
            return self.generate_caption(material_name, material_data)
        elif content_type == 'faq':
            return self.generate_faq(material_name, material_data, **kwargs)
        elif content_type == 'subtitle':
            return self.generate_subtitle(material_name, material_data)
        elif content_type == 'eeat':
            # EEAT is non-AI, returns dict directly
            return self.generate_eeat(material_name, material_data)
        else:
            raise ValueError(f"Unknown content type: {content_type}")
        
        # Note: SimpleGenerator already writes to Materials.yaml
        # No need for separate _write_to_materials_yaml call
