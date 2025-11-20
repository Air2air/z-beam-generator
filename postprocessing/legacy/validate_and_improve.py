"""
Post-Processing Validation & Improvement

⚠️ DEPRECATED - November 19, 2025
This monolithic validation system has been replaced by the ultra-modular ValidationOrchestrator.

OLD SYSTEM (THIS FILE - 474 lines):
- Single 474-line class with 12 methods
- Mixed concerns (validation, learning, recording, regeneration)
- Difficult to test (requires full integration test)
- Difficult to debug (errors buried in monolith)
- Difficult to profile (no per-step timing)

NEW SYSTEM (postprocessing/orchestrator.py + postprocessing/steps/**):
- 19 discrete steps (30-60 lines each)
- Single responsibility per step
- Independently testable (19 focused unit tests)
- Clear debugging ("Step 2.3 failed" vs buried error)
- Automatic timing per step
- Easy step replacement without touching others

USE INSTEAD:
    from postprocessing.orchestrator import ValidationOrchestrator
    orchestrator = ValidationOrchestrator(api_client, winston_client, simple_generator)
    result = orchestrator.validate_and_improve(material, component_type)

This file is preserved for reference only and may be removed in future releases.
⚠️ DO NOT USE IN NEW CODE

---

Original Documentation:

This stage runs AFTER simple generation to:
1. Validate quality (Winston, Realism, Readability, Subjective)
2. Apply learning systems (temperature advisor, pattern learner, etc.)
3. Retry with adjusted parameters if quality fails
4. Update learning database with results

Architecture:
    Generation Phase: Generate → Save (simple_generator.py)
    Validation Phase: Load → Validate → Learn → Retry (THIS FILE)
    
Learning systems operate on complete datasets, enabling:
- Temperature optimization from historical success
- Pattern detection across materials
- Parameter sweet spot identification
- Composite quality scoring with adaptive thresholds
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml

logger = logging.getLogger(__name__)


class ValidationAndImprovementPipeline:
    """
    Post-processing validation with learning-based improvement.
    
    Loads generated content, validates quality, applies learning systems,
    and retries with adjusted parameters if needed.
    """
    
    def __init__(self, api_client, winston_client):
        """
        Initialize validation pipeline.
        
        Args:
            api_client: API client for regeneration
            winston_client: Winston API client for detection
        """
        if not api_client or not winston_client:
            raise ValueError("API clients required for validation pipeline")
        
        self.api_client = api_client
        self.winston_client = winston_client
        self.logger = logging.getLogger(__name__)
        
        # Initialize all learning systems (from existing generator.py)
        self._init_learning_systems()
        
        # Initialize validators
        self._init_validators()
        
        self.logger.info("ValidationAndImprovementPipeline initialized with learning systems")
    
    def _init_learning_systems(self):
        """Initialize all learning systems for parameter optimization"""
        from generation.config.config_loader import get_config
        from learning.pattern_learner import PatternLearner
        from learning.temperature_advisor import TemperatureAdvisor
        from learning.prompt_optimizer import PromptOptimizer
        from learning.success_predictor import SuccessPredictor
        from learning.weight_learner import WeightLearner
        from learning.realism_optimizer import RealismOptimizer
        from learning.sweet_spot_analyzer import SweetSpotAnalyzer
        
        config = get_config()
        self.config = config.config
        
        # Pattern learner - detects risky patterns
        self.pattern_learner = PatternLearner()
        self.logger.info("[PATTERN LEARNER] Initialized")
        
        # Temperature advisor - learns optimal temperatures
        self.temperature_advisor = TemperatureAdvisor()
        self.logger.info("[TEMPERATURE ADVISOR] Initialized")
        
        # Prompt optimizer - enhances prompts based on failures
        self.prompt_optimizer = PromptOptimizer()
        self.logger.info("[PROMPT OPTIMIZER] Initialized")
        
        # Success predictor - predicts success probability
        self.success_predictor = SuccessPredictor()
        self.logger.info("[SUCCESS PREDICTOR] Initialized")
        
        # Weight learner - optimizes composite scoring weights
        self.weight_learner = WeightLearner()
        self.logger.info("[WEIGHT LEARNER] Initialized")
        
        # Realism optimizer - parameter adjustment for realism
        self.realism_optimizer = RealismOptimizer()
        self.logger.info("[REALISM OPTIMIZER] Initialized")
        
        # Sweet spot analyzer - finds optimal parameter combinations
        self.sweet_spot_analyzer = SweetSpotAnalyzer()
        self.logger.info("[SWEET SPOT ANALYZER] Initialized")
        
        # Dynamic config for parameter baseline
        from generation.config.dynamic_config import DynamicConfig
        self.dynamic_config = DynamicConfig()
    
    def _init_validators(self):
        """Initialize quality validators"""
        # Winston AI detector
        from postprocessing.detection.ensemble import AIDetectorEnsemble
        self.detector = AIDetectorEnsemble(use_ml=False, winston_client=self.winston_client)
        
        # Readability validator
        from generation.validation.readability import ReadabilityValidator
        readability_thresholds = self.dynamic_config.calculate_readability_thresholds()
        self.readability_validator = ReadabilityValidator(min_score=readability_thresholds['min'])
        
        # Subjective evaluator
        from postprocessing.evaluation import SubjectiveEvaluator
        self.subjective_evaluator = SubjectiveEvaluator(api_client=self.api_client)
        
        # Realism evaluator
        from postprocessing.evaluation.realism_evaluator import RealismEvaluator
        self.realism_evaluator = RealismEvaluator(api_client=self.api_client)
        
        self.logger.info("Quality validators initialized")
    
    def validate_and_improve(
        self,
        material_name: str,
        component_type: str,
        max_attempts: int = 5
    ) -> Dict[str, Any]:
        """
        Validate generated content and improve if needed.
        
        Args:
            material_name: Name of material
            component_type: Type of component
            max_attempts: Maximum retry attempts
            
        Returns:
            Dict with validation results and final content
        """
        self.logger.info(f"\n🔍 VALIDATION PIPELINE: {component_type} for {material_name}")
        
        # Load generated content
        content = self._load_content(material_name, component_type)
        if not content:
            raise ValueError(f"No content found for {material_name}.{component_type}")
        
        self.logger.info(f"📄 Loaded content: {len(content)} chars")
        
        # Validation loop with learning
        attempt = 1
        best_content = content
        best_score = 0.0
        last_winston_result = None
        last_realism_result = None
        suggested_adjustments = None
        
        while attempt <= max_attempts:
            self.logger.info(f"\n🔄 Validation Attempt {attempt}/{max_attempts}")
            
            # Run all quality checks
            quality_results = self._run_quality_checks(content, component_type)
            
            # Calculate composite score
            composite_score = self._calculate_composite_score(quality_results)
            self.logger.info(f"📊 Composite Score: {composite_score:.1f}%")
            
            # Update best if improved
            if composite_score > best_score:
                best_score = composite_score
                best_content = content
                self.logger.info(f"✅ New best score: {composite_score:.1f}%")
            
            # Check if passes all gates
            if self._passes_quality_gates(quality_results):
                self.logger.info(f"🎉 PASSED all quality gates on attempt {attempt}")
                
                # Update pattern learner with success
                self._update_pattern_learner(
                    quality_results,
                    content,
                    material_name,
                    component_type,
                    accepted=True
                )
                
                # Log to learning database
                self._log_to_learning_database(
                    material_name,
                    component_type,
                    content,
                    quality_results,
                    success=True,
                    attempt=attempt
                )
                
                return {
                    'success': True,
                    'content': content,
                    'attempts': attempt,
                    'quality_results': quality_results,
                    'composite_score': composite_score
                }
            
            # Failed - apply learning systems for next attempt
            if attempt < max_attempts:
                self.logger.info(f"❌ Quality gate failed, applying learning for retry {attempt + 1}")
                
                # Update pattern learner with rejection
                self._update_pattern_learner(
                    quality_results,
                    content,
                    material_name,
                    component_type,
                    accepted=False
                )
                
                # Get parameter adjustments from learning systems
                suggested_adjustments = self._get_learning_adjustments(
                    material_name,
                    component_type,
                    quality_results,
                    attempt
                )
                
                # Regenerate with adjusted parameters
                content = self._regenerate_with_adjustments(
                    material_name,
                    component_type,
                    suggested_adjustments
                )
                
                # Log failed attempt to learning database
                self._log_to_learning_database(
                    material_name,
                    component_type,
                    content,
                    quality_results,
                    success=False,
                    attempt=attempt
                )
            
            attempt += 1
        
        # Max attempts reached - return best result
        self.logger.warning(f"⚠️  Max attempts reached. Using best result (score: {best_score:.1f}%)")
        
        return {
            'success': False,
            'content': best_content,
            'attempts': max_attempts,
            'quality_results': quality_results,
            'composite_score': best_score,
            'reason': 'max_attempts_reached'
        }
    
    def _load_content(self, material_name: str, component_type: str) -> Optional[str]:
        """Load generated content from Materials.yaml"""
        materials_path = Path("data/materials/Materials.yaml")
        
        with open(materials_path, 'r') as f:
            data = yaml.safe_load(f)
        
        material = data['materials'].get(material_name, {})
        components = material.get('components', {})
        return components.get(component_type)
    
    def _run_quality_checks(self, content: str, component_type: str) -> Dict[str, Any]:
        """Run all quality validators"""
        results = {}
        
        # Winston AI detection
        self.logger.info("🔍 Running Winston AI detection...")
        winston_result = self.detector.detect(content)
        results['winston'] = {
            'ai_score': winston_result.get('ai_score', 1.0),
            'human_score': (1.0 - winston_result.get('ai_score', 1.0)) * 100,
            'passes': winston_result.get('ai_score', 1.0) < 0.33
        }
        self.logger.info(f"   AI: {results['winston']['ai_score']:.3f}, Human: {results['winston']['human_score']:.1f}%")
        
        # Realism evaluation
        self.logger.info("🔍 Running Realism evaluation...")
        realism_result = self.realism_evaluator.evaluate(content, component_type)
        results['realism'] = {
            'score': realism_result.get('score', 0.0),
            'passes': realism_result.get('score', 0.0) >= 7.0
        }
        self.logger.info(f"   Score: {results['realism']['score']:.1f}/10")
        
        # Readability check
        self.logger.info("🔍 Running Readability check...")
        readability_result = self.readability_validator.validate(content)
        results['readability'] = {
            'passes': readability_result
        }
        self.logger.info(f"   {'✅ PASS' if readability_result else '❌ FAIL'}")
        
        # Subjective language check
        self.logger.info("🔍 Running Subjective language check...")
        subjective_result = self.subjective_evaluator.evaluate(content, component_type)
        results['subjective'] = {
            'violations': len(subjective_result.get('violations', [])),
            'passes': len(subjective_result.get('violations', [])) == 0,
            'full_result': subjective_result  # Store complete result for pattern learning
        }
        self.logger.info(f"   Violations: {results['subjective']['violations']}")
        
        return results
    
    def _calculate_composite_score(self, quality_results: Dict[str, Any]) -> float:
        """Calculate composite quality score (Winston 60% + Realism 40%)"""
        winston_score = quality_results['winston']['human_score']
        realism_score = quality_results['realism']['score'] * 10  # Convert to 0-100
        
        composite = (winston_score * 0.6) + (realism_score * 0.4)
        return composite
    
    def _passes_quality_gates(self, quality_results: Dict[str, Any]) -> bool:
        """Check if content passes all quality gates"""
        return all([
            quality_results['winston']['passes'],
            quality_results['realism']['passes'],
            quality_results['readability']['passes'],
            quality_results['subjective']['passes']
        ])
    
    def _get_learning_adjustments(
        self,
        material_name: str,
        component_type: str,
        quality_results: Dict[str, Any],
        attempt: int
    ) -> Dict[str, Any]:
        """Get parameter adjustments from learning systems"""
        adjustments = {}
        
        # Sweet spot analyzer - Apply optimal parameter ranges from historical data
        if self.sweet_spot_analyzer:
            try:
                sweet_spots = self.sweet_spot_analyzer.find_sweet_spots(top_n_percent=25)
                if sweet_spots:
                    self.logger.info(f"📊 Found {len(sweet_spots)} sweet spot parameters")
                    # Apply median values from high-confidence sweet spots
                    for param_name, sweet_spot in sweet_spots.items():
                        if sweet_spot.confidence in ['high', 'medium']:
                            adjustments[param_name] = sweet_spot.optimal_median
                            self.logger.debug(
                                f"   {param_name}: {sweet_spot.optimal_median} "
                                f"(confidence: {sweet_spot.confidence}, samples: {sweet_spot.sample_count})"
                            )
            except Exception as e:
                self.logger.warning(f"Sweet spot analysis failed: {e}")
        
        # Temperature adjustment from advisor (overrides sweet spot if more specific)
        if self.temperature_advisor:
            temp_adjustment = self.temperature_advisor.get_recommendation(
                material_name,
                component_type,
                quality_results['winston']['ai_score']
            )
            if temp_adjustment:
                adjustments['temperature'] = temp_adjustment
        
        # Realism-based parameter optimization (overrides for realism failures)
        if self.realism_optimizer and quality_results['realism']['score'] < 7.0:
            realism_adjustments = self.realism_optimizer.get_adjustments(
                quality_results['realism']['score']
            )
            adjustments.update(realism_adjustments)
        
        # Pattern-based adjustments (final overrides for known patterns)
        if self.pattern_learner:
            pattern_adjustments = self.pattern_learner.get_adjustments(component_type)
            adjustments.update(pattern_adjustments)
        
        self.logger.info(f"📊 Learning adjustments: {len(adjustments)} parameters")
        return adjustments
    
    def _update_pattern_learner(
        self,
        quality_results: Dict[str, Any],
        content: str,
        material_name: str,
        component_type: str,
        accepted: bool
    ):
        """
        Update subjective pattern learner with evaluation results.
        
        This maintains the continuous learning loop:
        - Updates learned_patterns.yaml with theatrical phrases and AI tendencies
        - Tracks success patterns using exponential moving average
        - Feeds back into next evaluation prompt
        """
        try:
            # Get full subjective evaluation result
            subjective_data = quality_results.get('subjective', {})
            full_result = subjective_data.get('full_result')
            
            if not full_result:
                self.logger.debug("No subjective evaluation result to learn from")
                return
            
            # Get pattern learner from subjective evaluator
            pattern_learner = self.subjective_evaluator._get_pattern_learner()
            
            # Convert SubjectiveEvaluationResult to dict if needed
            if hasattr(full_result, '__dict__'):
                evaluation_dict = full_result.__dict__
            else:
                evaluation_dict = full_result
            
            # Update learned patterns
            pattern_learner.update_from_evaluation(
                evaluation_result=evaluation_dict,
                content=content,
                accepted=accepted,
                component_type=component_type,
                material_name=material_name
            )
            
            self.logger.info(f"📚 Updated pattern learner (accepted={accepted})")
            
        except Exception as e:
            # Don't fail validation if pattern learning fails
            self.logger.warning(f"Pattern learner update failed: {e}")
    
    def _regenerate_with_adjustments(
        self,
        material_name: str,
        component_type: str,
        adjustments: Dict[str, Any]
    ) -> str:
        """Regenerate content with adjusted parameters"""
        # This would call simple_generator with adjusted params
        # For now, placeholder - implementation depends on integration approach
        self.logger.warning("⚠️  Regeneration not yet implemented - returning original content")
        return self._load_content(material_name, component_type) or ""
    
    def _log_to_learning_database(
        self,
        material_name: str,
        component_type: str,
        content: str,
        quality_results: Dict[str, Any],
        success: bool,
        attempt: int
    ):
        """Log results to learning database"""
        # Log to Winston feedback database
        try:
            from postprocessing.detection.winston_feedback_db import WinstonFeedbackDatabase
            
            db_path = self.config.get('winston_feedback_db_path', 'z-beam.db')
            feedback_db = WinstonFeedbackDatabase(db_path)
            
            feedback_db.log_detection(
                content=content,
                ai_score=quality_results['winston']['ai_score'],
                human_score=quality_results['winston']['human_score'],
                component_type=component_type,
                material_name=material_name,
                success=success,
                realism_score=quality_results['realism']['score']
            )
            
            self.logger.info(f"💾 Logged to learning database (attempt {attempt})")
        except Exception as e:
            self.logger.error(f"Failed to log to learning database: {e}")
