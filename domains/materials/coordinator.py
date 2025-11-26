#!/usr/bin/env python3
"""
Unified Materials Content Generator

TEXT CONTENT GENERATOR for all material content (caption, FAQ, subtitle, description).
Used by shared/commands/generation.py for all generation commands.

ARCHITECTURE (Updated November 22, 2025):
TWO MODES with single generator:

1. PRODUCTION MODE (default, training_mode=False):
   - Fast single-pass generation (~5-7 seconds)
   - No quality gates, no evaluation, no retry
   - Direct API call via SimpleGenerator
   - Cost: ~$0.015 per description
   - Use for: Normal content generation

2. TRAINING MODE (training_mode=True):
   - Quality-gated generation with evaluation (~30-60 seconds)
   - Evaluates content BEFORE save using SubjectiveEvaluator
   - Retries up to 5 times with parameter adjustments if quality fails
   - Learns from feedback to improve future generations
   - Cost: ~$0.049 per description (includes evaluation API calls)
   - Use for: Building learning database, quality assurance

Quality Gates in Training Mode (ALL must pass):
- Subjective Realism: Learned threshold (typically 5.5-7.0/10)
- Voice Authenticity: Learned threshold
- Tonal Consistency: Learned threshold
- AI Tendencies: Configurable (require_zero_ai_tendencies setting)

Usage:
    # Production mode (default): Fast, no quality gates
    generator = UnifiedMaterialsGenerator(api_client)
    generator.generate('Bronze', 'caption')
    
    # Training mode: Quality gates, evaluation, retry with feedback learning
    generator = UnifiedMaterialsGenerator(api_client, training_mode=True)
    generator.generate('Bronze', 'caption')   # Evaluates before save, retries if needed
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
    Unified generator for all materials content types with dual-mode operation.
    
    PRODUCTION MODE (default): Fast single-pass generation without quality gates.
    TRAINING MODE (opt-in): Quality-gated generation with evaluation and retry.
    
    Responsibilities:
    - Route to SimpleGenerator (production) or QualityGatedGenerator (training)
    - Handle FAQ topic enhancement (optional)
    - Generate EEAT section (non-AI, random selection from regulatoryStandards)
    - Proper Materials.yaml save in both modes
    """
    
    def __init__(self, api_client, training_mode: bool = False):
        """
        Initialize unified generator.
        
        Args:
            api_client: API client for content generation (required)
            training_mode: If True, enable quality gates for learning (slower).
                          If False, production mode - fast single-pass generation.
        """
        if not api_client:
            raise ValueError("API client required for content generation")
        
        self.training_mode = training_mode
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)
        
        # Load config
        from generation.config.config_loader import get_config
        config = get_config()
        quality_gate_config = config.config.get('quality_gates', {})
        evaluation_config = config.config.get('evaluation', {})
        
        # PRODUCTION MODE: Skip quality gate initialization
        if not training_mode:
            self.logger.info("🚀 Production mode: Quality gates disabled (fast single-pass)")
            self.quality_gated_generator = None
            return
        
        # TRAINING MODE: Initialize quality gates for learning
        self.logger.info("🎓 Training mode: Quality gates enabled (learning from feedback)")
        
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
        
        # Get dynamic realism threshold from database learning
        from learning.threshold_manager import ThresholdManager
        threshold_manager = ThresholdManager(db_path='z-beam.db')
        realism_threshold = threshold_manager.get_realism_threshold(use_learned=True)
        self.logger.info(f"Using learned realism threshold: {realism_threshold:.1f}/10")
        
        # Fail-fast if quality gate config missing (other than threshold)
        if 'verbose' not in evaluation_config:
            raise ValueError("evaluation.verbose missing in config.yaml - fail-fast architecture")
        if 'temperature' not in evaluation_config:
            raise ValueError("evaluation.temperature missing in config.yaml - fail-fast architecture")
        if 'max_retry_attempts' not in quality_gate_config:
            raise ValueError("quality_gates.max_retry_attempts missing in config.yaml - fail-fast architecture")
        
        self.subjective_evaluator = SubjectiveEvaluator(
            api_client=evaluation_client,  # Use evaluation-specific client
            quality_threshold=realism_threshold,  # Use learned threshold
            verbose=evaluation_config['verbose'],
            evaluation_temperature=evaluation_config['temperature']
        )
        
        # Create Winston API client for AI detection (optional)
        winston_client = None
        try:
            from shared.api.client_factory import APIClientFactory
            winston_client = APIClientFactory.create_client(provider="winston")
            self.logger.info("Winston API client created for quality gate integration")
        except Exception as e:
            self.logger.warning(f"Winston API not configured: {e}")
            self.logger.info("Quality gate will skip Winston detection (Grok evaluation only)")
        
        # Initialize StructuralVariationChecker for diversity enforcement
        from generation.validation.structural_variation_checker import StructuralVariationChecker
        structural_checker = StructuralVariationChecker(
            db_path='data/winston_feedback.db',
            min_diversity_score=6.0
        )
        self.logger.info("StructuralVariationChecker initialized (enforces 6.0/10 diversity)")
        
        # Initialize QualityGatedGenerator (evaluate before save, retry on fail)
        self.generator = QualityGatedGenerator(
            api_client=api_client,
            subjective_evaluator=self.subjective_evaluator,
            winston_client=winston_client,  # Add Winston for quality gate
            structural_variation_checker=structural_checker,  # Add structural variation as 5th gate
            max_attempts=quality_gate_config['max_retry_attempts'],
            quality_threshold=realism_threshold  # Use learned threshold
        )
        
        self.logger.info("UnifiedMaterialsGenerator initialized (quality-gated generation with auto-retry)")
    
    def _load_materials_data(self) -> Dict:
        """Load Materials.yaml using centralized loader"""
        from domains.materials.data_loader import load_materials_data
        return load_materials_data()
    
    def generate_caption(self, material_name: str, material_data: Dict) -> Dict:
        """
        Generate before/after microscopy captions using QualityGatedGenerator.
        
        Option C: Saves ALL attempts, tries to improve quality.
        Always returns success=True after max attempts (content saved regardless).
        
        Returns:
            Dict with 'before' and 'after' keys (caption content)
        """
        self.logger.info(f"📸 Generating caption for {material_name}")
        
        # Use QualityGatedGenerator - Option C: saves all, tries to improve
        result = self.generator.generate(material_name, 'caption')
        
        # Option C: Trust success=True even if quality low
        # Content already saved to Materials.yaml during generation
        if not result.success:
            # Should never happen with Option C, but handle defensively
            self.logger.warning(f"⚠️  Unexpected failure from QualityGatedGenerator (Option C should always succeed)")
            self.logger.warning(f"   Attempts: {result.attempts}, Reasons: {'; '.join(result.rejection_reasons)}")
            # Don't raise exception - Option C means we accept whatever was saved
        
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
        
        # Use QualityGatedGenerator - Option C: saves all, tries to improve
        result = self.generator.generate(material_name, 'faq', faq_count=faq_count)
        
        # Option C: Trust success=True even if quality low
        # Content already saved to Materials.yaml during generation
        if not result.success:
            # Should never happen with Option C, but handle defensively
            self.logger.warning(f"⚠️  Unexpected failure from QualityGatedGenerator (Option C should always succeed)")
            self.logger.warning(f"   Attempts: {result.attempts}, Reasons: {'; '.join(result.rejection_reasons)}")
            # Don't raise exception - Option C means we accept whatever was saved
        
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
        
        Option C: Saves ALL attempts, tries to improve quality.
        Always returns success=True after max attempts (content saved regardless).
        
        Returns:
            String (subtitle content)
        """
        self.logger.info(f"📝 Generating subtitle for {material_name}")
        
        # Use QualityGatedGenerator - Option C: saves all, tries to improve
        result = self.generator.generate(material_name, 'subtitle')
        
        # Option C: Trust success=True even if quality low
        # Content already saved to Materials.yaml during generation
        if not result.success:
            # Should never happen with Option C, but handle defensively
            self.logger.warning(f"⚠️  Unexpected failure from QualityGatedGenerator (Option C should always succeed)")
            self.logger.warning(f"   Attempts: {result.attempts}, Reasons: {'; '.join(result.rejection_reasons)}")
            # Don't raise exception - Option C means we accept whatever was saved
        
        subtitle = result.content
        word_count = len(subtitle.split())
        self.logger.info(f"   ✅ Generated: {subtitle[:80]}... ({word_count} words)")
        
        # Return content string
        return subtitle
    
    def generate_description(self, material_name: str, material_data: Dict) -> str:
        """
        Generate description using QualityGatedGenerator.
        
        Option C: Saves ALL attempts, tries to improve quality.
        Always returns success=True after max attempts (content saved regardless).
        
        Returns:
            String (description content)
        """
        self.logger.info(f"📝 Generating description for {material_name}")
        
        # Use QualityGatedGenerator - Option C: saves all, tries to improve
        result = self.generator.generate(material_name, 'description')
        
        # Option C: Trust success=True even if quality low
        # Content already saved to Materials.yaml during generation
        if not result.success:
            # Should never happen with Option C, but handle defensively
            self.logger.warning(f"⚠️  Unexpected failure from QualityGatedGenerator (Option C should always succeed)")
            self.logger.warning(f"   Attempts: {result.attempts}, Reasons: {'; '.join(result.rejection_reasons)}")
            # Don't raise exception - Option C means we accept whatever was saved
        
        description = result.content
        word_count = len(description.split())
        self.logger.info(f"   ✅ Generated: {description[:80]}... ({word_count} words)")
        
        # Return content string
        return description
    
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
        
        TRAINING MODE: Uses QualityGatedGenerator with retries and evaluation.
        PRODUCTION MODE: Direct API call, single-pass, no quality gates.
        
        Args:
            material_name: Name of material
            content_type: Type of content ('caption', 'faq', 'subtitle', 'description')
            **kwargs: Additional parameters (e.g., faq_count=8)
            
        Returns:
            Generated content (string for caption/subtitle/description, list for faq)
        """
        # PRODUCTION MODE: Fast single-pass generation
        if not self.training_mode:
            return self._generate_production(material_name, content_type, **kwargs)
        
        # TRAINING MODE: Quality-gated generation with retry
        return self._generate_training(material_name, content_type, **kwargs)
    
    def _generate_production(self, material_name: str, content_type: str, **kwargs):
        """Production mode: Fast single-pass generation, no quality gates."""
        from generation.core.simple_generator import SimpleGenerator
        
        generator = SimpleGenerator(self.api_client)
        result = generator.generate(material_name, content_type, **kwargs)
        
        # SimpleGenerator returns content directly (not wrapped)
        return result
    
    def _generate_training(self, material_name: str, content_type: str, **kwargs):
        """Training mode: Quality-gated generation with evaluation and retry."""
        # Load material data
        materials_data = self._load_materials_data()
        
        if material_name not in materials_data['materials']:
            raise ValueError(f"Material '{material_name}' not found in Materials.yaml")
        
        material_data = materials_data['materials'][material_name]
        
        # Generate based on type using quality-gated approach
        if content_type == 'caption':
            return self.generate_caption(material_name, material_data)
        elif content_type == 'faq':
            return self.generate_faq(material_name, material_data, **kwargs)
        elif content_type == 'subtitle':
            return self.generate_subtitle(material_name, material_data)
        elif content_type == 'description':
            return self.generate_description(material_name, material_data)
        elif content_type == 'eeat':
            return self.generate_eeat(material_name, material_data)
        else:
            raise ValueError(f"Unknown content type: {content_type}")
